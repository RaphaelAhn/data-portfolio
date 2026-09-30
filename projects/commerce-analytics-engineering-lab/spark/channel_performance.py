"""PySpark port of mart_channel_daily_performance, built straight from the raw seeds.

Run after `dbt build`; exits non-zero if Spark and dbt disagree on any row:
    .venv\\Scripts\\python.exe spark\\channel_performance.py
"""

import os
import sys
from decimal import Decimal
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "seeds"
DATABASE = ROOT / "target" / "commerce_analytics.duckdb"
MONEY = "decimal(18,2)"


def read(spark: SparkSession, name: str) -> DataFrame:
    return spark.read.csv(str(SEEDS / f"{name}.csv"), header=True)


def latest(df: DataFrame, keys: list[str], *order_cols: str) -> DataFrame:
    w = Window.partitionBy(*keys).orderBy(*[F.col(c).desc() for c in order_cols])
    return df.withColumn("_rn", F.row_number().over(w)).filter("_rn = 1").drop("_rn")


def build(spark: SparkSession) -> DataFrame:
    # silver: typed, latest state per key (same rules as the dbt staging layer)
    orders = latest(
        read(spark, "raw_orders").select(
            "order_id",
            F.lower("order_status").alias("order_status"),
            F.to_timestamp("ordered_at").alias("ordered_at"),
            F.to_timestamp("updated_at").alias("updated_at"),
        ),
        ["order_id"], "updated_at",
    )
    order_ids = read(spark, "raw_order_items").select("order_id").distinct()
    payments = latest(
        read(spark, "raw_payments").select(
            "payment_id", "order_id",
            F.lower("payment_status").alias("payment_status"),
            F.col("paid_amount").cast(MONEY).alias("paid_amount"),
            F.to_timestamp("updated_at").alias("updated_at"),
        ),
        ["payment_id"], "updated_at",
    )
    refunds = latest(
        read(spark, "raw_refunds").select(
            "refund_id", "payment_id",
            F.lower("refund_status").alias("refund_status"),
            F.col("refund_amount").cast(MONEY).alias("refund_amount"),
            F.to_timestamp("updated_at").alias("updated_at"),
            F.to_timestamp("ingested_at").alias("ingested_at"),
        ),
        ["refund_id"], "updated_at", "ingested_at",
    )
    spend = latest(
        read(spark, "raw_ad_spend").select(
            "campaign_id",
            F.to_date("spend_date").alias("spend_date"),
            F.col("impressions").cast("long").alias("impressions"),
            F.col("clicks").cast("long").alias("clicks"),
            F.col("cost").cast(MONEY).alias("cost"),
            F.to_timestamp("reported_at").alias("reported_at"),
        ),
        ["campaign_id", "spend_date"], "reported_at",
    )
    campaigns = read(spark, "raw_campaigns").select("campaign_id", F.lower("platform").alias("channel"))
    clicks = read(spark, "raw_ad_clicks").select(
        "order_id", "campaign_id", F.to_timestamp("clicked_at").alias("clicked_at")
    )

    # fct_orders equivalent: net revenue = completed payments - completed refunds
    paid = (payments.filter("payment_status = 'completed'")
            .groupBy("order_id").agg(F.sum("paid_amount").alias("paid")))
    refunded = (refunds.filter("refund_status = 'completed'")
                .join(payments.select("payment_id", "order_id"), "payment_id")
                .groupBy("order_id").agg(F.sum("refund_amount").alias("refunded")))
    fct_orders = (
        orders.join(order_ids, "order_id")
        .join(paid, "order_id", "left").join(refunded, "order_id", "left")
        .withColumn("paid", F.coalesce("paid", F.lit(0).cast(MONEY)))
        .withColumn("refunded", F.coalesce("refunded", F.lit(0).cast(MONEY)))
        .select(
            "order_id", "ordered_at",
            F.to_date("ordered_at").alias("order_date"),
            ((F.col("order_status") == "completed") & (F.col("paid") > 0)).alias("is_recognized_order"),
            F.when(F.col("order_status") == "completed", F.col("paid") - F.col("refunded"))
             .otherwise(F.lit(0)).cast(MONEY).alias("net_revenue"),
        )
    )

    # last click at or before the order, within 7 days; otherwise organic
    last_click = latest(
        fct_orders.select("order_id", "ordered_at").join(clicks, "order_id")
        .filter((F.col("clicked_at") <= F.col("ordered_at"))
                & (F.col("clicked_at") >= F.col("ordered_at") - F.expr("INTERVAL 7 DAYS"))),
        ["order_id"], "clicked_at",
    ).select("order_id", "campaign_id")
    attributed = (
        fct_orders.join(last_click, "order_id", "left")
        .join(campaigns, "campaign_id", "left")
        .withColumn("channel", F.coalesce("channel", F.lit("organic")))
    )

    # gold: date x channel
    spend_daily = (spend.join(campaigns, "campaign_id")
                   .groupBy(F.col("spend_date").alias("metric_date"), "channel")
                   .agg(F.sum("impressions").alias("impressions"),
                        F.sum("clicks").alias("clicks"),
                        F.sum("cost").alias("cost")))
    orders_daily = (attributed.groupBy(F.col("order_date").alias("metric_date"), "channel")
                    .agg(F.countDistinct(F.when(F.col("is_recognized_order"), F.col("order_id"))).alias("attributed_orders"),
                         F.sum("net_revenue").alias("revenue")))

    s, o = spend_daily.alias("s"), orders_daily.alias("o")
    revenue = F.coalesce("o.revenue", F.lit(0))
    return (
        s.join(o, (F.col("s.metric_date") == F.col("o.metric_date")) & (F.col("s.channel") == F.col("o.channel")), "full")
        .select(
            F.coalesce("s.metric_date", "o.metric_date").alias("metric_date"),
            F.coalesce("s.channel", "o.channel").alias("channel"),
            F.coalesce("s.impressions", F.lit(0)).alias("impressions"),
            F.coalesce("s.clicks", F.lit(0)).alias("clicks"),
            F.coalesce("s.cost", F.lit(0)).cast(MONEY).alias("cost"),
            F.coalesce("o.attributed_orders", F.lit(0)).alias("attributed_orders"),
            revenue.cast(MONEY).alias("attributed_net_revenue"),
            (revenue / F.when(F.col("s.cost") != 0, F.col("s.cost"))).cast("decimal(18,4)").alias("roas"),
            (F.col("s.cost") / F.when(F.col("o.attributed_orders") != 0, F.col("o.attributed_orders"))).cast(MONEY).alias("cpa"),
            (F.col("s.clicks") / F.when(F.col("s.impressions") != 0, F.col("s.impressions"))).cast("decimal(18,4)").alias("ctr"),
        )
    )


def normalize(row) -> tuple:
    return tuple(str(v) if isinstance(v, Decimal) else v for v in row)


def main() -> int:
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    spark = (SparkSession.builder.master("local[2]").appName("channel_performance")
             .config("spark.sql.session.timeZone", "UTC")
             .config("spark.ui.enabled", "false").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    try:
        # ponytail: collect() is fine for fixtures; on Databricks write the result to a Delta table instead
        spark_rows = sorted(normalize(r) for r in build(spark).collect())
    finally:
        spark.stop()

    import duckdb
    with duckdb.connect(str(DATABASE), read_only=True) as con:
        dbt_rows = sorted(normalize(r) for r in con.sql("select * from mart_channel_daily_performance").fetchall())

    for r in sorted(set(spark_rows) - set(dbt_rows)):
        print("spark only:", r)
    for r in sorted(set(dbt_rows) - set(spark_rows)):
        print("dbt only:  ", r)
    if spark_rows != dbt_rows:
        print(f"Parity FAILED: spark={len(spark_rows)} rows, dbt={len(dbt_rows)} rows")
        return 1
    print(f"Parity passed: PySpark and dbt produced the same {len(spark_rows)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
