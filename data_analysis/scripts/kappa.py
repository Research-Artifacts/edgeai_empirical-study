"""
Inter-rater Reliability Analysis for ISO/IEC 30141 Capability Mappings
Author: Jander Pereira Santos Jr.
Purpose:
    - Compute Cohen’s Kappa between raters (Jander, Luana, Paulo)
    - Clean NaNs
    - Produce tables for replication package
"""

import pandas as pd
from sklearn.metrics import cohen_kappa_score

FILE = "/data_analysis/dataset/Capabilities.csv"

def clean_column(series):
    """Replace NaNs by a placeholder so sklearn can process."""
    return series.fillna("NONE")

def compute_kappa(df, col_base, col_rater1, col_rater2):
    """Compute Cohen's Kappa between two raters."""
    a = clean_column(df[col_rater1])
    b = clean_column(df[col_rater2])
    return cohen_kappa_score(a, b)

def run_analysis():
    df = pd.read_csv(FILE)

    results = []

    capability_groups = [
        ("capability_1", "iso_mapping_cap_1 - [Jander]", "iso_mapping_cap_1 - [Luana]", "iso_mapping_cap_1 - [Paulo]"),
        ("capability_2", "iso_mapping_cap_2 - [Jander]", "iso_mapping_cap_2 - [Luana]", "iso_mapping_cap_2 - [Paulo]"),
        ("capability_3", "iso_mapping_cap_3 - [Jander]", "iso_mapping_cap_3 - [Luana]", "iso_mapping_cap_3 - [Paulo]"),
    ]

    for cap, cj, cl, cp in capability_groups:
        results.append({
            "capability": cap,
            "Jander_vs_Luana": compute_kappa(df, cap, cj, cl),
            "Jander_vs_Paulo": compute_kappa(df, cap, cj, cp),
            "Luana_vs_Paulo": compute_kappa(df, cap, cl, cp),
        })

    results_df = pd.DataFrame(results)
    print("\n=== Cohen’s Kappa Results ===")
    print(results_df)

    results_df.to_csv("kappa_results.csv", index=False)
    print("\n[Saved] kappa_results.csv")

if __name__ == "__main__":
    run_analysis()
