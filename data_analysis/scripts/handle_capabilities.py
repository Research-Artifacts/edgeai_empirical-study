# -*- coding: utf-8 -*-
"""
Generate supplementary material (tables + figures) for the distribution of
capabilities across ISO/IEC/IEEE 30141 capability classes and layers
(Device/Edge/Fog/Cloud) from the study tables.

Input (example columns):
  - repo_id, repo_name,
  - capability_1, iso_mapping_cap_1,
  - capability_2, iso_mapping_cap_2,
  - capability_3, iso_mapping_cap_3,
  - layer_caps  (unified column with operating layers)

Outputs:
  - tables/normalized_capabilities_long.csv
  - tables/counts_iso.csv               (counts + percentage)
  - tables/counts_layers.csv            (counts + percentage)
  - tables/heatmap_iso_x_layer_counts.csv
  - tables/heatmap_iso_x_layer_percent.csv
  - tables/unmapped_iso.csv
  - tables/unmapped_layers.csv
  - figs/bar_iso.(png|pdf)
  - figs/bar_layers.(png|pdf)
  - figs/heatmap_iso_x_layer.(png|pdf)  (heatmap in percentage)

Notes:
  - Robust normalization for ISO capability classes (3 buckets) and layers
    (Device/Edge/Fog/Cloud/Cross-cutting).
  - Combined layers (e.g., "Edge/Fog", "Fog/Cloud ↔ Edge") are exploded
    into multiple rows with fractional weight (sum of weights per slot = 1).
  - Any column starting with 'iso' or 'iso_map' is interpreted as ISO mapping;
    'layer_caps' (or close variants) is interpreted as layer mapping.
  - Dependencies: pandas, matplotlib.
"""

from __future__ import annotations

from pathlib import Path
import re
import unicodedata

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# =========================
# Paths and configuration
# =========================

# Adjust the input path as needed for your replication package
INPUT = Path("../dataset/[Empirical_Study]-included_by_criteria.csv")

OUT_DIR_FIG = Path("../results/figs")
OUT_DIR_TAB = Path("../results/tables")
OUT_DIR_FIG.mkdir(parents=True, exist_ok=True)
OUT_DIR_TAB.mkdir(parents=True, exist_ok=True)

FIG_DPI = 220

# Canonical ISO capability buckets (3 classes)
ISO_CANON = [
    "Interface Capability",
    "Data Capabilities",
    "Supporting Capabilities",
]

# Color palette (reused across plots)
colors = ["#3b5b92", "#6c8ebf", "#8aa8d6", "#b7c7ea",
          "#777777", "#a0a0a0", "#c8c8c8", "#e0e0e0"]

# Canonical layer order
LAYER_CANON = ["Device", "Edge", "Fog", "Cloud", "Cross-cutting"]


# -------------------------
# Helper functions
# -------------------------
def norm_basic(s: str | float) -> str:
    """Basic string normalization: trim, collapse spaces, strip punctuation, remove accents."""
    if not isinstance(s, str):
        return ""
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.strip(",.;:|-_/")
    s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
    return s


def contains_any(s: str, words: list[str]) -> bool:
    """Check if any of the given words appears (case-insensitive) in the string."""
    s_low = s.lower()
    return any(w.lower() in s_low for w in words)


# -------------------------
# ISO normalization (3 buckets)
# -------------------------
def normalize_iso(raw: str) -> str | None:
    """
    Map raw ISO mapping column values into one of the 3 canonical classes:

        - "Interface Capability"
        - "Data Capabilities"
        - "Supporting Capabilities"

    This function is tailored to map tags such as:
        "Interface Capability", "Interface capability", "interface capabilities"
        "Data Capabilities", "Data capabilities"
        "Supporting Capabilities", "Supporting capability", "Supporting capabilities"
    and similar variations.
    """
    s = norm_basic(raw)
    if not s:
        return None

    s_low = s.lower()

    # Interface-related labels
    if "interface" in s_low:
        return "Interface Capability"

    # Data-related labels
    if "data" in s_low:
        return "Data Capabilities"

    # Supporting-related labels
    if "support" in s_low:
        return "Supporting Capabilities"

    # If it already matches one of the canonical labels (possibly different case)
    for canon in ISO_CANON:
        if s_low == canon.lower():
            return canon

    # No mapping found
    return None


# -------------------------
# Layer normalization
# -------------------------
_LAYER_PATTERNS = {
    "Device": [
        r"\bdevice\b", r"\bdispositivo\b", r"\bendpoint\b", r"\bmcu\b",
        r"\bmicrontrol", r"\bdevice layer\b",
    ],
    "Edge": [
        r"\bedge\b", r"\bedge layer\b", r"\bborda\b", r"\blocal\b",
        r"\bedge/fog\b", r"\bfog/edge\b",
    ],
    "Fog": [
        r"\bfog\b", r"\bfog layer\b",
        r"\bfog/cloud\b", r"\bcloud/fog\b",
    ],
    "Cloud": [
        r"\bcloud\b", r"\bnuvem\b", r"\bdatacenter\b", r"\bhpc\b",
    ],
    "Cross-cutting": [
        r"\bcross[-\s]?cutting\b", r"\btransversal\b",
        r"\bend-to-end\b", r"\bfull stack\b", r"\bcontinuum\b",
    ],
}


def split_layers(raw: str) -> list[str] | None:
    """
    Normalize and split a raw 'layer' string into a list of canonical layers.

    Combined expressions such as "Edge/Fog", "Fog/Cloud ↔ Edge" are exploded
    into multiple layers (e.g., ["Edge", "Fog"]).
    """
    s = norm_basic(raw)
    if not s:
        return None

    s = s.replace("↔", "/").replace("\\", "/")
    s = re.sub(r"\bto\b", "/", s, flags=re.I)
    s = re.sub(r"[;,|]+", "/", s)
    s = re.sub(r"\s*/\s*", "/", s)
    s_low = s.lower()

    found: set[str] = set()

    # Common combinations
    combos = {
        "device/edge": ["Device", "Edge"],
        "edge/device": ["Device", "Edge"],
        "edge/fog": ["Edge", "Fog"],
        "fog/edge": ["Edge", "Fog"],
        "fog/cloud": ["Fog", "Cloud"],
        "cloud/fog": ["Fog", "Cloud"],
        "edge/fog/cloud": ["Edge", "Fog", "Cloud"],
        "device/edge/fog": ["Device", "Edge", "Fog"],
        "device/edge/fog/cloud": ["Device", "Edge", "Fog", "Cloud"],
        "device ↔ fog": ["Device", "Edge", "Fog"],
    }

    for k, layers in combos.items():
        if k in s_low:
            found.update(layers)

    # Individual patterns
    for layer, pats in _LAYER_PATTERNS.items():
        for pat in pats:
            if re.search(pat, s_low):
                found.add(layer)

    # Fallback: if we see "layer" but no specific match, assume "Edge"
    if not found and re.search(r"\blayer\b", s_low):
        found.add("Edge")

    if not found:
        return None

    ordered = [l for l in LAYER_CANON if l in found]
    return ordered or None


# -------------------------
# Data loading and melting
# -------------------------
def load_input(path: Path) -> pd.DataFrame:
    """Load input CSV and strip column names."""
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    return df


def melt_and_normalize(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Transform the wide table into a long format, normalize ISO and layer values,
    and track unmapped entries.
    """

    def col_for(prefixes: list[str], n: int) -> str | None:
        for p in prefixes:
            cand = f"{p}_{n}"
            if cand in df.columns:
                return cand
        return None

    def get_layer_unified_colname() -> str | None:
        for name in ["layer_caps", "layers_cap", "layers_caps", "layer"]:
            if name in df.columns:
                return name
        return None

    layer_unified = get_layer_unified_colname()

    records: list[dict] = []
    unmapped_iso: list[dict] = []
    unmapped_layers: list[dict] = []

    for _, row in df.iterrows():
        rid = row.get("id") or row.get("repo_id") or row.get("uid")
        repo = row.get("repo_name") or row.get("repo") or row.get("name")
        layer_raw_base = row.get(layer_unified, "") if layer_unified else ""

        for n in (1, 2, 3):
            cap_col = col_for(["capability", "cap"], n)
            iso_col = col_for(["iso_mapping_cap", "iso_map", "iso_mapping", "iso", "iso_ns"], n)

            cap = row.get(cap_col, "") if cap_col else ""
            iso_raw = row.get(iso_col, "") if iso_col else ""
            layer_raw = layer_raw_base

            # Skip completely empty slots
            if not (str(cap).strip() or str(iso_raw).strip() or str(layer_raw).strip()):
                continue

            iso_norm = normalize_iso(iso_raw)
            if iso_norm is None and str(iso_raw).strip():
                unmapped_iso.append(
                    {"id": rid, "repo_name": repo, "slot": n, "iso_raw": iso_raw}
                )

            layers = split_layers(layer_raw)
            if layers is None and str(layer_raw).strip():
                unmapped_layers.append(
                    {"id": rid, "repo_name": repo, "slot": n, "layer_raw": layer_raw}
                )

            layers = layers or [None]
            weight = 1.0 / len(layers) if layers[0] is not None else 1.0

            for lyr in layers:
                records.append(
                    {
                        "id": rid,
                        "repo_name": repo,
                        "slot": n,
                        "cap_specific": str(cap).strip(),
                        "iso_raw": iso_raw,
                        "iso": iso_norm,
                        "layer_raw": layer_raw,
                        "layer": lyr,
                        "weight": weight,
                    }
                )

    long_df = pd.DataFrame.from_records(records)
    unm_iso_df = pd.DataFrame(unmapped_iso).drop_duplicates()
    unm_layer_df = pd.DataFrame(unmapped_layers).drop_duplicates()

    # Ordered categories
    long_df["iso"] = pd.Categorical(long_df["iso"], categories=ISO_CANON, ordered=True)
    long_df["layer"] = pd.Categorical(long_df["layer"], categories=LAYER_CANON, ordered=True)

    return long_df, unm_iso_df, unm_layer_df


# -------------------------
# Table generation (counts + percentages)
# -------------------------
def make_tables(long_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Build aggregated tables:

      - by_iso:    counts and percentages per ISO class
      - by_layer:  counts and percentages per layer
      - heat_counts:  ISO x layer matrix (counts)
      - heat_percent: ISO x layer matrix (percentages of total weight)
    """

    # ISO totals
    by_iso = (
        long_df.dropna(subset=["iso"])
        .groupby("iso", dropna=False, as_index=False)["weight"]
        .sum()
        .rename(columns={"weight": "count"})
        .sort_values(["iso"])
    )
    total_iso = by_iso["count"].sum()
    if total_iso > 0:
        by_iso["percent"] = (by_iso["count"] / total_iso) * 100.0
    else:
        by_iso["percent"] = 0.0

    # Layer totals
    by_layer = (
        long_df.dropna(subset=["layer"])
        .groupby("layer", dropna=False, as_index=False)["weight"]
        .sum()
        .rename(columns={"weight": "count"})
        .sort_values(["layer"])
    )
    total_layer = by_layer["count"].sum()
    if total_layer > 0:
        by_layer["percent"] = (by_layer["count"] / total_layer) * 100.0
    else:
        by_layer["percent"] = 0.0

    # ISO x Layer matrix (counts)
    mat = (
        long_df.dropna(subset=["iso", "layer"])
        .groupby(["iso", "layer"], as_index=False)["weight"]
        .sum()
        .rename(columns={"weight": "count"})
    )
    heat_counts = (
        mat.pivot(index="iso", columns="layer", values="count")
        .reindex(index=ISO_CANON, columns=LAYER_CANON)
        .fillna(0.0)
    )

    # ISO x Layer matrix (percent of total weight)
    total_all = heat_counts.values.sum()
    if total_all > 0:
        heat_percent = (heat_counts / total_all) * 100.0
    else:
        heat_percent = heat_counts.copy()

    return {
        "by_iso": by_iso,
        "by_layer": by_layer,
        "heat_counts": heat_counts,
        "heat_percent": heat_percent,
    }


# -------------------------
# Plotting helpers
# -------------------------
def plot_bar_iso(by_iso: pd.DataFrame, outfile_png: Path, outfile_pdf: Path) -> None:
    """Bar chart: ISO classes (counts) annotated with percentage."""
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(by_iso))
    ax.bar(x, by_iso["count"].values, color=colors, edgecolor="#222222", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(by_iso["iso"].astype(str), rotation=15, ha="right")
    ax.set_ylabel("Weighted count")
    ax.set_title("Distribution of Capabilities by ISO/IEC/IEEE 30141 Class")

    # Annotate bars with "count (xx.x%)"
    for idx, p in enumerate(ax.patches):
        h = p.get_height()
        if h <= 0:
            continue
        pct = by_iso.iloc[idx]["percent"]
        ax.annotate(
            f"{h:.1f} ({pct:.1f}%)",
            (p.get_x() + p.get_width() / 2, h),
            ha="center",
            va="bottom",
            fontsize=9,
            xytext=(0, 3),
            textcoords="offset points",
        )

    fig.tight_layout()
    fig.savefig(outfile_png, dpi=FIG_DPI)
    fig.savefig(outfile_pdf)
    plt.close(fig)


def plot_bar_layers(by_layer: pd.DataFrame, outfile_png: Path, outfile_pdf: Path) -> None:
    """Bar chart: layers (counts) annotated with percentage."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = range(len(by_layer))
    ax.bar(x, by_layer["count"].values, color=colors, edgecolor="#222222", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(by_layer["layer"].astype(str), rotation=0, ha="center")
    ax.set_ylabel("Weighted count")
    ax.set_title("Distribution of Capabilities by Layer")

    for idx, p in enumerate(ax.patches):
        h = p.get_height()
        if h <= 0:
            continue
        pct = by_layer.iloc[idx]["percent"]
        ax.annotate(
            f"{h:.1f} ({pct:.1f}%)",
            (p.get_x() + p.get_width() / 2, h),
            ha="center",
            va="bottom",
            fontsize=9,
            xytext=(0, 3),
            textcoords="offset points",
        )

    fig.tight_layout()
    fig.savefig(outfile_png, dpi=FIG_DPI)
    fig.savefig(outfile_pdf)
    plt.close(fig)


def plot_heatmap(heat_percent: pd.DataFrame, outfile_png: Path, outfile_pdf: Path) -> None:
    """
    Heatmap of ISO x Layer in percentage of total weight.

    The color scale and annotations are both in %.
    """
    colors_hm = ["#3b5b92", "#6c8ebf", "#8aa8d6", "#b7c7ea",
                 "#777777", "#a0a0a0", "#c8c8c8", "#e0e0e0"]
    cmap = LinearSegmentedColormap.from_list("custom_heatmap", colors_hm, N=256)

    fig, ax = plt.subplots(figsize=(9, 6))
    im = ax.imshow(heat_percent.values, aspect="auto", cmap=cmap)

    ax.set_yticks(range(len(heat_percent.index)))
    ax.set_yticklabels(heat_percent.index.astype(str))
    ax.set_xticks(range(len(heat_percent.columns)))
    ax.set_xticklabels(heat_percent.columns.astype(str), rotation=0)

    vmax = float(heat_percent.values.max()) if heat_percent.size else 0.0
    for i in range(heat_percent.shape[0]):
        for j in range(heat_percent.shape[1]):
            v = float(heat_percent.iat[i, j])
            label = f"{v:.1f}%"
            ax.text(
                j,
                i,
                label,
                ha="center",
                va="center",
                fontsize=15,
                fontweight="bold",
                color="black",
                # color="white" if vmax and v > vmax * 0.6 else "black",
            )

    ax.set_title("Capabilities by ISO Class and Layer (percentage of total)")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Percentage of total capability weight (%)")

    fig.tight_layout()
    fig.savefig(outfile_png, dpi=FIG_DPI)
    fig.savefig(outfile_pdf)
    plt.close(fig)


# -------------------------
# Main
# -------------------------
def main() -> None:
    df = load_input(INPUT)
    long_df, unm_iso_df, unm_layer_df = melt_and_normalize(df)

    # Long normalized table
    long_df.to_csv(OUT_DIR_TAB / "normalized_capabilities_long.csv", index=False)

    # Unmapped ISO / layers
    if not unm_iso_df.empty:
        unm_iso_df.to_csv(OUT_DIR_TAB / "unmapped_iso.csv", index=False)
    else:
        (OUT_DIR_TAB / "unmapped_iso.csv").write_text("")

    if not unm_layer_df.empty:
        unm_layer_df.to_csv(OUT_DIR_TAB / "unmapped_layers.csv", index=False)
    else:
        (OUT_DIR_TAB / "unmapped_layers.csv").write_text("")

    # Aggregated tables (counts + percentages)
    tables = make_tables(long_df)

    tables["by_iso"].to_csv(OUT_DIR_TAB / "counts_iso.csv", index=False)
    tables["by_layer"].to_csv(OUT_DIR_TAB / "counts_layers.csv", index=False)
    tables["heat_counts"].to_csv(OUT_DIR_TAB / "heatmap_iso_x_layer_counts.csv")
    tables["heat_percent"].to_csv(OUT_DIR_TAB / "heatmap_iso_x_layer_percent.csv")

    # Plots
    plot_bar_iso(
        tables["by_iso"],
        OUT_DIR_FIG / "bar_iso.png",
        OUT_DIR_FIG / "bar_iso.pdf",
    )
    plot_bar_layers(
        tables["by_layer"],
        OUT_DIR_FIG / "bar_layers.png",
        OUT_DIR_FIG / "bar_layers.pdf",
    )
    plot_heatmap(
        tables["heat_percent"],
        OUT_DIR_FIG / "heatmap_iso_x_layer.png",
       OUT_DIR_FIG / "heatmap_iso_x_layer.pdf",
    )

    total_slots = len(long_df)
    missing_iso = long_df["iso"].isna().sum()
    missing_layer = long_df["layer"].isna().sum()

    print(f"[OK] Records (exploded): {total_slots}")
    print(f"[OK] Unmapped ISO entries: {missing_iso} | Unmapped layers: {missing_layer}")
    print(f"[OK] Tables saved in: {OUT_DIR_TAB.resolve()}")
    print(f"[OK] Figures saved in: {OUT_DIR_FIG.resolve()}")


if __name__ == "__main__":
    main()
