#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Column coverage counter for EdgeAI empirical dataset.

Reads a CSV and, for a fixed set of columns, computes per-column:
- count of non-null/non-empty cells (default), OR
- count of "true-like" cells (when --true-like is passed),
and their percentages over total rows.

Outputs:
  - tables/column_coverage.csv

Usage:
  python column_coverage.py \
    --input path/to/file.csv
  # optional:
  # --true-like       -> counts only true-like values
  # --sep ";"         -> CSV separator (default ",")
  # --out tables/column_coverage.csv

Author: (your name / project)
License: MIT
"""

from __future__ import annotations
from pathlib import Path
import argparse
import logging
import sys
from typing import Iterable

import pandas as pd

COLUMNS = [
    "arch_overview", "diagrams", "adrs", "context",
    "deployment", "quality_attrs", "interface", "evaluation",
]

TRUE_LIKE_SET = {"true", "1", "yes", "y", "sim"}


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-8s %(message)s",
    )


def is_true_like(val) -> bool:
    if pd.isna(val):
        return False
    if isinstance(val, (int, float)):
        # treat non-zero as true (common in csv exports)
        return val != 0
    s = str(val).strip().lower()
    if s == "":
        return False
    return s in TRUE_LIKE_SET


def is_non_empty(val) -> bool:
    if pd.isna(val):
        return False
    if isinstance(val, str):
        return str(val).strip() != ""
    # any non-NaN is considered present
    return True


def compute_coverage(
        df: pd.DataFrame, columns: Iterable[str], true_like: bool = False
) -> pd.DataFrame:
    total = len(df)
    checker = is_true_like if true_like else is_non_empty

    rows = []
    for col in columns:
        if col not in df.columns:
            logging.warning("Column '%s' not found in input. Counting as zero.", col)
            count = 0
        else:
            count = df[col].apply(checker).sum()
        percentage = (count / total * 100.0) if total > 0 else 0.0
        rows.append(
            {
                "column": col,
                "count": int(count),
                "percentage": round(percentage, 2),
                "total_rows": total,
                "criterion": "true_like" if true_like else "non_null_non_empty",
            }
        )
    return pd.DataFrame(rows, columns=["column", "count", "percentage", "total_rows", "criterion"])


def main():
    parser = argparse.ArgumentParser(description="Compute per-column coverage (count & percent).")
    parser.add_argument("--input", required=True, help="Path to input CSV file.")
    parser.add_argument("--sep", default=",", help="CSV separator (default: ',').")
    parser.add_argument("--true-like", action="store_true",
                        help="Count only true-like values (true/yes/1/non-zero). Default: non-null/non-empty.")
    parser.add_argument("--out", default="tables/column_coverage.csv",
                        help="Output CSV path (default: tables/column_coverage.csv).")
    parser.add_argument("--log", default="INFO", help="Log level (default: INFO).")
    args = parser.parse_args()

    setup_logging(args.log)

    in_path = Path(args.input)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        logging.error("Input file not found: %s", in_path)
        sys.exit(1)

    logging.info("Loading CSV: %s", in_path)
    try:
        df = pd.read_csv(in_path, sep=args.sep, dtype=object, keep_default_na=True,
                         na_values=["", "NA", "NaN", "null", "None"])
    except Exception as e:
        logging.exception("Failed to read CSV: %s", e)
        sys.exit(1)

    logging.info("Rows loaded: %d | Columns: %d", len(df), len(df.columns))

    # Compute coverage
    coverage = compute_coverage(df, COLUMNS, true_like=args.true_like)

    # Save
    coverage.to_csv(out_path, index=False)
    logging.info("Saved: %s", out_path)

    # Pretty print summary
    print("\n=== Column Coverage Summary ===")
    print(coverage.to_string(index=False))


if __name__ == "__main__":
    main()
