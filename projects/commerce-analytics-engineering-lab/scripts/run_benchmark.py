"""Run dbt build at increasing seed scale and record real elapsed time.

Temporarily overwrites seeds/ with generated fixtures for one scale at a
time, runs `dbt build`, records the result, then restores the checked-in
seeds/ with `git checkout -- seeds/` before moving to the next scale (or
exiting). Never leaves the working tree with generated seeds in place.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_benchmark_seeds import generate  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SEEDS_DIR = ROOT / "seeds"
SCALES = (100_000, 500_000, 1_000_000)
SUMMARY_RE = re.compile(r"Done\. PASS=(\d+) WARN=(\d+) ERROR=(\d+) SKIP=(\d+) TOTAL=(\d+)")


def restore_seeds() -> None:
    subprocess.run(["git", "checkout", "--", "seeds"], cwd=ROOT, check=True)


DBT_INVOKE_CODE = (
    "import sys\n"
    "from dbt.cli.main import cli\n"
    "cli(['build', '--profiles-dir', sys.argv[1], '--full-refresh'])\n"
)


def run_one_scale(order_count: int) -> dict:
    generate(order_count, SEEDS_DIR)

    # dbt.exe's console-script shim is broken in this venv (fails silently,
    # exit 1, no output) -- invoking dbt's CLI entry point directly via
    # `python -c` works and was verified manually before this script existed.
    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "-c", DBT_INVOKE_CODE, str(ROOT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    elapsed = time.perf_counter() - start

    match = SUMMARY_RE.search(result.stdout)
    summary = (
        {
            "pass": int(match.group(1)),
            "warn": int(match.group(2)),
            "error": int(match.group(3)),
            "skip": int(match.group(4)),
            "total": int(match.group(5)),
        }
        if match
        else {"raw_tail": result.stdout[-2000:]}
    )

    return {
        "orders": order_count,
        "elapsed_seconds": round(elapsed, 2),
        "returncode": result.returncode,
        "summary": summary,
    }


def main() -> None:
    results = []
    try:
        for scale in SCALES:
            print(f"=== Running dbt build at {scale} orders ===", flush=True)
            outcome = run_one_scale(scale)
            print(json.dumps(outcome, indent=2), flush=True)
            results.append(outcome)
    finally:
        restore_seeds()
        print("Restored original seeds/ with git checkout.", flush=True)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
