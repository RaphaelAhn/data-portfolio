"""Create a time-split customer repurchase prioritization analysis from UCI Online Retail."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


FEATURES = [
    "recency_days", "orders_90d", "items_90d", "revenue_90d", "aov_90d",
    "products_90d", "orders_prior_180d", "revenue_prior_180d",
]
TRAIN_CUTOFFS = pd.to_datetime(["2011-06-08", "2011-07-08", "2011-08-08"])
TEST_CUTOFF = pd.Timestamp("2011-09-08")
HORIZON_DAYS = 90


def clean_transactions(path):
    data = pd.read_excel(path, dtype={"InvoiceNo": str, "CustomerID": str, "StockCode": str})
    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"])
    data["CustomerID"] = data["CustomerID"].str.replace(r"\.0$", "", regex=True)
    valid = (
        ~data["InvoiceNo"].str.startswith("C", na=False)
        & data["CustomerID"].notna()
        & (data["Quantity"] > 0)
        & (data["UnitPrice"] > 0)
    )
    data = data.loc[valid].copy()
    data["revenue"] = data["Quantity"] * data["UnitPrice"]
    return data


def feature_frame(data, cutoff):
    history = data.loc[data["InvoiceDate"] < cutoff]
    recent_start = cutoff - pd.Timedelta(days=90)
    prior_start = cutoff - pd.Timedelta(days=270)
    customers = history.groupby("CustomerID")["InvoiceDate"].max().rename("last_purchase")
    recent = history.loc[history["InvoiceDate"] >= recent_start]
    prior = history.loc[(history["InvoiceDate"] >= prior_start) & (history["InvoiceDate"] < recent_start)]

    result = customers.to_frame()
    result["recency_days"] = (cutoff - result["last_purchase"]).dt.days
    recent_metrics = recent.groupby("CustomerID").agg(
        orders_90d=("InvoiceNo", "nunique"), items_90d=("Quantity", "sum"),
        revenue_90d=("revenue", "sum"), products_90d=("StockCode", "nunique"),
    )
    result = result.join(recent_metrics).fillna(0)
    result["aov_90d"] = np.where(result["orders_90d"] > 0, result["revenue_90d"] / result["orders_90d"], 0)
    prior_metrics = prior.groupby("CustomerID").agg(
        orders_prior_180d=("InvoiceNo", "nunique"), revenue_prior_180d=("revenue", "sum"),
    )
    result = result.join(prior_metrics).fillna(0)
    future = data.loc[(data["InvoiceDate"] >= cutoff) & (data["InvoiceDate"] < cutoff + pd.Timedelta(days=HORIZON_DAYS))]
    result["repurchased_90d"] = result.index.isin(future["CustomerID"].unique()).astype(int)
    return result.reset_index()


def fit_logistic(x, y, steps=1800, learning_rate=0.08, l2=0.02):
    mean, std = x.mean(axis=0), x.std(axis=0)
    std = np.where(std == 0, 1, std)
    z = (x - mean) / std
    design = np.c_[np.ones(len(z)), z]
    weights = np.zeros(design.shape[1])
    for _ in range(steps):
        prediction = 1 / (1 + np.exp(-np.clip(design @ weights, -30, 30)))
        gradient = (design.T @ (prediction - y)) / len(y)
        gradient[1:] += l2 * weights[1:]
        weights -= learning_rate * gradient
    return mean, std, weights


def probabilities(x, model):
    mean, std, weights = model
    design = np.c_[np.ones(len(x)), (x - mean) / std]
    return 1 / (1 + np.exp(-np.clip(design @ weights, -30, 30)))


def roc_auc(y, scores):
    positives, negatives = y.sum(), len(y) - y.sum()
    if positives == 0 or negatives == 0:
        return None
    ranks = pd.Series(scores).rank(method="average").to_numpy()
    return float((ranks[y == 1].sum() - positives * (positives + 1) / 2) / (positives * negatives))


def top_metrics(y, scores, share=0.10):
    k = max(1, int(np.ceil(len(y) * share)))
    selected = np.argsort(scores)[-k:]
    captured = int(y[selected].sum())
    return {"contacts": k, "precision": captured / k, "recall": captured / int(y.sum()), "captured": captured}


def evaluate(y, scores):
    return {"roc_auc": roc_auc(y, scores), "top_10pct": top_metrics(y, scores)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", default=Path(__file__).parents[1] / "outputs", type=Path)
    args = parser.parse_args()

    data = clean_transactions(args.input)
    train = pd.concat([feature_frame(data, cutoff) for cutoff in TRAIN_CUTOFFS], ignore_index=True)
    test = feature_frame(data, TEST_CUTOFF)
    model = fit_logistic(train[FEATURES].to_numpy(float), train["repurchased_90d"].to_numpy(float))
    model_scores = probabilities(test[FEATURES].to_numpy(float), model)
    baseline_scores = -test["recency_days"].to_numpy(float)
    summary = {
        "source": "UCI Online Retail (DOI: 10.24432/C5BW33)",
        "clean_transactions": int(len(data)), "unique_customers": int(data["CustomerID"].nunique()),
        "training_rows": int(len(train)), "test_customers": int(len(test)),
        "test_repurchase_rate": float(test["repurchased_90d"].mean()),
        "model": evaluate(test["repurchased_90d"].to_numpy(), model_scores),
        "recency_baseline": evaluate(test["repurchased_90d"].to_numpy(), baseline_scores),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    m, b = summary["model"], summary["recency_baseline"]
    text = f"""# Analysis Results

## Data and evaluation design

- Clean transaction lines: {summary['clean_transactions']:,}
- Unique customers: {summary['unique_customers']:,}
- Training rows across three time-based snapshots: {summary['training_rows']:,}
- Customers in the final evaluation: {summary['test_customers']:,}
- 90-day repurchase rate in the final evaluation: {summary['test_repurchase_rate']:.1%}

## Prioritization performance

| Method | ROC-AUC | Customers reviewed | Precision@Top 10% | Recall@Top 10% | Repeat purchasers captured |
| --- | ---: | ---: | ---: | ---: | ---: |
| Recency baseline | {b['roc_auc']:.3f} | {b['top_10pct']['contacts']:,} | {b['top_10pct']['precision']:.1%} | {b['top_10pct']['recall']:.1%} | {b['top_10pct']['captured']:,} |
| Logistic regression with RFM, product diversity, and prior history | {m['roc_auc']:.3f} | {m['top_10pct']['contacts']:,} | {m['top_10pct']['precision']:.1%} | {m['top_10pct']['recall']:.1%} | {m['top_10pct']['captured']:,} |

## Interpretation

The top-10% metric represents an offline review queue under limited CRM capacity. It does **not** show that a message or incentive caused additional purchases. A production test should use a randomized holdout group and evaluate incremental repurchase rate, contribution margin, and unsubscribe rate.
"""
    (args.output_dir / "portfolio-summary.md").write_text(text, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
