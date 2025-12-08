#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_multilabel_kappa_iso25010.py

Supplementary script for computing Cohen's Kappa in a
multi-label coding setting based on ISO/IEC 25010 quality
attributes.

Input:
    A CSV file with, at least, the following columns:
        - R1: labels assigned by Coder 1
        - R2: labels assigned by Coder 2

    Each cell may contain one or more labels (multi-label
    coding), separated by commas and/or semicolons, e.g.:

        Functional Suitability, Performance Efficiency
        Reliability; Security

Output:
    - Prints per-attribute Cohen's Kappa and a macro-Kappa
      (average over all attributes).
    - Optionally writes a "cleaned" CSV with normalized,
      decomposed labels for transparency and reproducibility.

Usage example:
    python multilabel_kappa_iso25010.py \
        --input ../dataset/data_analysis/[Empirical_Study]-qual_req.csv \
        --output ../results/tables/codes_clean.csv

Dependencies:
    - pandas
    - scikit-learn
"""

import argparse
import re
from typing import List, Dict

import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import cohen_kappa_score


# -------------------------------------------------------------------
# 1. Label parsing and normalization
# -------------------------------------------------------------------

# Canonical mapping for the nine top-level ISO/IEC 25010
# product quality characteristics (normalized to Title Case).
CANON_MAP: Dict[str, str] = {
    "functional suitability": "Functional Suitability",
    "performance efficiency": "Performance Efficiency",
    "compatibility": "Compatibility",
    "interaction capability": "Interaction Capability",
    "reliability": "Reliability",
    "security": "Security",
    "maintainability": "Maintainability",
    "flexibility": "Flexibility",
    "safety": "Safety",
}


def parse_labels(cell: str) -> List[str]:
    """
    Parse a raw label cell into a list of individual labels.

    - Accepts multiple labels separated by commas (",")
      and/or semicolons (";").
    - Strips whitespace around labels.
    - Returns an empty list for empty/NaN cells.
    """
    if pd.isna(cell):
        return []

    # Split on comma or semicolon
    raw_parts = re.split(r"[;,]", str(cell))
    parts = [p.strip() for p in raw_parts if p.strip()]
    return parts


def normalize_labels(labels: List[str]) -> List[str]:
    """
    Normalize a list of labels:

    - Lowercases each label.
    - Maps common variants onto the nine canonical
      ISO/IEC 25010 quality characteristics (CANON_MAP).
    - If a label is not in CANON_MAP, it is kept as-is
      (can be inspected later).
    - Removes duplicates while preserving original order.
    """
    normalized: List[str] = []
    for lab in labels:
        key = lab.strip().lower()
        if key in CANON_MAP:
            normalized.append(CANON_MAP[key])
        else:
            normalized.append(lab.strip())

    # Remove duplicates while preserving order
    seen = set()
    dedup: List[str] = []
    for lab in normalized:
        if lab not in seen:
            seen.add(lab)
            dedup.append(lab)

    return dedup


# -------------------------------------------------------------------
# 2. Multi-label Cohen's Kappa computation
# -------------------------------------------------------------------

def compute_multilabel_kappa(
    df: pd.DataFrame,
    col_r1: str = "R1",
    col_r2: str = "R2",
) -> None:
    """
    Compute Cohen's Kappa for a multi-label coding setting.

    Each row corresponds to one fragment/document.
    Each coder may assign one or more labels from the
    ISO/IEC 25010 quality characteristics.

    Steps:
      1) Parse and normalize labels for R1 and R2.
      2) Build a multi-label binarized representation
         (one binary variable per attribute).
      3) Compute Cohen's Kappa per attribute.
      4) Compute macro-Kappa as the unweighted mean
         across attributes.
    """

    # Convert raw columns into normalized list-of-labels
    df["R1_list"] = (
        df[col_r1]
        .apply(parse_labels)
        .apply(normalize_labels)
    )
    df["R2_list"] = (
        df[col_r2]
        .apply(parse_labels)
        .apply(normalize_labels)
    )

    # Collect the set of all distinct labels present
    all_labels = sorted(
        list(
            set(
                sum(df["R1_list"].tolist() + df["R2_list"].tolist(), [])
            )
        )
    )

    print("Distinct normalized labels found:")
    for lab in all_labels:
        print(f"  - {lab}")
    print()

    # Multi-label binarization
    mlb = MultiLabelBinarizer(classes=all_labels)
    r1_bin = mlb.fit_transform(df["R1_list"])
    r2_bin = mlb.transform(df["R2_list"])

    # Per-label Cohen's Kappa
    kappas = {}
    for i, label in enumerate(all_labels):
        k = cohen_kappa_score(r1_bin[:, i], r2_bin[:, i])
        kappas[label] = k

    # Macro-Kappa = simple mean over all attributes
    macro_kappa = sum(kappas.values()) / len(kappas)

    print("Cohen's Kappa per attribute:")
    for label, k in kappas.items():
        print(f"  {label}: {k:.3f}")
    print()
    print(f"Macro-Kappa (mean over attributes): {macro_kappa:.3f}")


# -------------------------------------------------------------------
# 3. Command-line interface
# -------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Compute multi-label Cohen's Kappa for two coders "
            "classifying fragments according to ISO/IEC 25010 "
            "quality characteristics."
        )
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file (must contain columns R1 and R2).",
    )
    parser.add_argument(
        "--output",
        required=False,
        help=(
            "Optional: path to save a 'clean' CSV with normalized "
            "and decomposed labels (R1_list / R2_list)."
        ),
    )
    args = parser.parse_args()

    # Read original CSV
    df = pd.read_csv(args.input)

    # Compute and report Kappa
    compute_multilabel_kappa(df, col_r1="QR_R1", col_r2="QR_R2")

    # Optionally store normalized labels for transparency
    if args.output:
        df["R1_normalized"] = df["R1_list"].apply(lambda lst: ", ".join(lst))
        df["R2_normalized"] = df["R2_list"].apply(lambda lst: ", ".join(lst))

        df.to_csv(args.output, index=False)
        print(f"\nNormalized spreadsheet saved to: {args.output}")


if __name__ == "__main__":
    main()
