#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processing and visualization of project 'domains' (multi-value, comma-separated).

Input:
  - CSV file with a 'domain' column (e.g., "IIoT, Smart Environment")

Outputs:
  - tables/domains_normalized_long.csv
        One row per (repo_id, normalized_domain)
  - tables/domains_counts.csv
        Count and percentage of repositories per domain
        Columns: domain, count, proportion, percentage
  - figs/domains_distribution.png
  - figs/domains_distribution.pdf

Percentages are computed over the total number of repositories
(i.e., number of rows in the input CSV).

Usage:
  python make_domains_figs.py \
      --input ../dataset/[Empirical_Study]-work_file.csv \
      --col domain \
      --idcol repo_id \
      --topN 20
"""

from __future__ import annotations

from pathlib import Path
import argparse
import logging
import re
import unicodedata
from typing import Iterable, List, Dict, Tuple

import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Logging configuration
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s: %(message)s"
)
log = logging.getLogger("domains")

# =========================
# Color palette (fixed)
# =========================
PALETTE = ["#3b5b92", "#6c8ebf", "#8aa8d6", "#b7c7ea",
           "#777777", "#a0a0a0", "#c8c8c8", "#e0e0e0"]

# =========================
# Label normalization
# =========================
def _strip_accents(s: str) -> str:
    """Remove accents/diacritics from a string."""
    return ''.join(
        c for c in unicodedata.normalize('NFKD', s)
        if not unicodedata.combining(c)
    )


def _clean_token(tok: str) -> str:
    """
    Basic token cleaning:
      - trim whitespace
      - remove accents
      - normalize internal spaces
      - casefold (lowercase with unicode awareness)
    """
    t = tok.strip()
    t = _strip_accents(t)
    t = re.sub(r"\s+", " ", t)
    return t.casefold()


# Canonical map (keys must be casefolded / accent-free)
CANON_MAP: Dict[str, str] = {
    # IIoT and industry
    "iiot": "IIoT",
    "industrial iot": "IIoT",
    "industrial edge computing": "IIoT",
    "smart manufacturing": "IIoT",
    "industry 4.0": "Industry 4.0",

    # These entries are kept for completeness, but typical flow uses lowercase keys
    "IIoT": "IIoT",
    "Smart Environment": "Smart Environment",
    "Data streaming processing": "Data streaming processing",

    "smart environment": "Smart Environment",
    "smart environments": "Smart Environment",

    "computer vision": "Computer Vision",
    "vision": "Computer Vision",
    "speech": "Speech",
    "audio analisys": "Audio Analysis",
    "audio analysis": "Audio Analysis",
    "chatbot": "Chatbot",

    "orchestration": "Orchestration",

    "federated learning": "Federated Learning",

    "efficient ai": "Efficient AI",
    "efficiente ai": "Efficient AI",  # common typo
    "aiot": "IoT",
    "iot": "IoT",

    "autonomous systems": "Autonomous Systems",
    "autonomous system": "Autonomous Systems",
    "robotic": "Robotics",
    "robotics": "Robotics",

    # Healthcare
    "healthcare": "Healthcare",
    "medical iot": "Healthcare",

    # Mobile
    "mobile iot": "Mobile IoT",

    # Streaming / real-time (several variations)
    "real time data processing": "Data Streaming & Real-Time",
    "real-time data processing": "Data Streaming & Real-Time",
    "real-time data streaming": "Data Streaming & Real-Time",
    "real time data streaming": "Data Streaming & Real-Time",
    "data streaming processing": "Data Streaming & Real-Time",
    "data streaming": "Data Streaming & Real-Time",

    # Model-Driven
    "model-driven engineering (mde)": "MDE",

    # Others
    "others": "Others",
}

# Auxiliary regex rules to capture broader real-time / streaming patterns
_REGEX_RULES: List[Tuple[re.Pattern, str]] = [
    # Anything that mentions 'real-time', 'real time', or 'rt'
    (re.compile(r"\b(real[-\s]?time|rt)\b", re.I), "Data Streaming & Real-Time"),
    # Anything that mentions 'stream' or 'streaming'
    (re.compile(r"\bstream(ing)?\b", re.I), "Data Streaming & Real-Time"),
]


def normalize_domain_token(raw: str) -> str:
    """
    Normalize a single domain token to its canonical form.

    Steps:
      1) Clean token (strip, remove accents, normalize spaces, casefold).
      2) Apply regex rules for streaming/real-time.
      3) Apply canonical map for synonyms / typos.
      4) Apply small heuristics for autonomous / industrial.
      5) Fallback: Title Case of the original raw string.
    """
    base = _clean_token(raw)
    if not base:
        return ""

    # 1) Regex rules (broad match for streaming / real-time)
    for pat, label in _REGEX_RULES:
        if pat.search(base):
            return label

    # 2) Canonical map
    if base in CANON_MAP:
        return CANON_MAP[base]

    # 3) Simple heuristics
    if base in {"autonomous", "autonomous systems"}:
        return "Autonomous Systems"
    if base in {"industrial", "industrial edge", "industrial internet of things"}:
        return "IIoT"

    # 4) Fallback: Title Case on the original raw token
    return re.sub(r"\s+", " ", raw.strip()).title()


def split_domains(cell: str) -> List[str]:
    """
    Split a multi-valued domain cell by comma, preserving composite items.
    Returns a list of raw tokens.
    """
    if pd.isna(cell):
        return []
    parts = [p.strip() for p in str(cell).split(",")]
    # remove empty tokens
    return [p for p in parts if p]


def normalize_domains(tokens: Iterable[str]) -> List[str]:
    """
    Apply normalize_domain_token to a collection of raw tokens.
    """
    out: List[str] = []
    for c in tokens:
        label = normalize_domain_token(c)
        if label:
            out.append(label)
    return out


# =========================
# Plot
# =========================
def plot_bar_counts(
    counts_df: pd.DataFrame,
    out_png: Path,
    out_pdf: Path,
    title: str = "Domains Distribution (Projects)"
) -> None:
    """
    Generate a horizontal bar chart of domain counts.

    If a 'percentage' column is present, the bar labels will show
    both count and percentage (e.g., "12 (17.4%)").
    """
    df = counts_df.sort_values("count", ascending=False).copy()
    labels = df["domain"].tolist()
    values = df["count"].tolist()

    # Optional percentage values for label formatting
    if "percentage" in df.columns:
        pct_values = df["percentage"].tolist()
    else:
        pct_values = [None] * len(values)

    # Colors: cycle through palette to ensure one color per bar
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(values))]

    plt.figure(figsize=(12, max(4, 0.35 * len(labels))))  # adaptive height
    bars = plt.barh(labels, values, color=colors, edgecolor="black")
    plt.xlabel("Number of Projects")
    plt.title(title)
    plt.gca().invert_yaxis()  # most frequent on top

    # Value labels on each bar
    max_val = max(values) if values else 0
    offset = max_val * 0.01 if max_val > 0 else 0.1

    for bar, val, pct in zip(bars, values, pct_values):
        if pct is not None:
            label_text = f"{val} ({pct:.1f}%)"
        else:
            label_text = str(val)
        plt.text(
            val + offset,
            bar.get_y() + bar.get_height() / 2,
            label_text,
            va="center",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf)
    plt.close()


# =========================
# Main pipeline
# =========================
def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize and aggregate project domains from a CSV, "
            "producing long-format data, counts, and a distribution figure."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input CSV file (must contain the domain column).",
    )
    parser.add_argument(
        "--col",
        type=str,
        default="domain",
        help="Name of the column containing domains (default: 'domain').",
    )
    parser.add_argument(
        "--idcol",
        type=str,
        default=None,
        help="Name of the project/repository ID column (optional). "
             "If omitted, a sequential 'repo_id' will be created.",
    )
    parser.add_argument(
        "--out_fig_dir",
        type=Path,
        default=Path("../results/figs"),
        help="Output directory for figures (default: '../figs').",
    )
    parser.add_argument(
        "--out_tab_dir",
        type=Path,
        default=Path("../results/tables"),
        help="Output directory for tables (default: '../tables').",
    )
    parser.add_argument(
        "--topN",
        type=int,
        default=0,
        help=(
            "If > 0, plot only the top N domains in the figure "
            "(the CSV with counts is always complete)."
        ),
    )
    args = parser.parse_args()

    args.out_fig_dir.mkdir(parents=True, exist_ok=True)
    args.out_tab_dir.mkdir(parents=True, exist_ok=True)

    log.info(f"Reading input CSV: {args.input}")
    df = pd.read_csv(args.input)

    if args.col not in df.columns:
        raise SystemExit(f"Column '{args.col}' not found in the CSV.")

    # Determine project/repository ID
    if args.idcol and args.idcol in df.columns:
        id_series = df[args.idcol]
        id_col_name = args.idcol
    else:
        id_series = pd.Series(range(1, len(df) + 1), name="repo_id")
        id_col_name = "repo_id"

    total_repos = int(id_series.nunique())
    log.info("Total repositories (rows) in input: %d", total_repos)

    # --- Normalize to long format
    rows = []
    for repo_id, cell in zip(id_series, df[args.col]):
        raw_tokens = split_domains(cell)
        norm_tokens = normalize_domains(raw_tokens)
        # Remove duplicate domains per project
        norm_tokens = sorted(set(norm_tokens))
        for token in norm_tokens:
            rows.append({id_col_name: repo_id, "domain": token})

    long_df = pd.DataFrame(rows)
    long_path = args.out_tab_dir / "domains_normalized_long.csv"
    long_df.to_csv(long_path, index=False)
    log.info("Saved normalized long-format table: %s", long_path)

    if long_df.empty:
        log.warning("No domains were found after normalization. Exiting.")
        return

    # --- Counts and percentages
    counts = (
        long_df["domain"]
        .value_counts()
        .rename_axis("domain")
        .reset_index(name="count")
    )

    # Proportion and percentage over total repositories in the input CSV
    counts["proportion"] = counts["count"] / float(total_repos)
    counts["percentage"] = (counts["proportion"] * 100.0).round(2)

    counts_path = args.out_tab_dir / "domains_counts.csv"
    counts.to_csv(counts_path, index=False)
    log.info("Saved domain counts with percentages: %s", counts_path)

    # --- Figure (optional Top N)
    plot_df = counts.copy()
    if args.topN and args.topN > 0:
        plot_df = plot_df.head(args.topN)

    out_png = args.out_fig_dir / "domains_distribution.png"
    out_pdf = args.out_fig_dir / "domains_distribution.pdf"
    title = "Domains Distribution (Projects)"
    if args.topN and args.topN > 0:
        title += f" — Top {args.topN}"

    plot_bar_counts(plot_df, out_png, out_pdf, title=title)
    log.info("Saved figure: %s", out_png)
    log.info("Saved figure: %s", out_pdf)


if __name__ == "__main__":
    main()

# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Tratamento e visualização de 'domains' dos projetos (multi-valor, separados por vírgula).
#
# Entradas:
#   - CSV com a coluna 'domain' (ex.: "IIoT, Smart Environment")
#
# Saídas:
#   - tables/domains_normalized_long.csv         # (repo_id opcional) linha por domínio normalizado
#   - tables/domains_counts.csv                  # contagem por domínio
#   - figs/domains_distribution.png
#   - figs/domains_distribution.pdf
#
# Uso:
#   python make_domains_figs.py \
#       --input ../dataset/[Empirical_Study]-work_file.csv \
#       --col domain \
#       --topN 20
# """
#
# from __future__ import annotations
# from pathlib import Path
# import argparse
# import logging
# import re
# import unicodedata
# from collections import Counter, defaultdict
# from typing import Iterable, List, Dict, Tuple
#
# import pandas as pd
# import matplotlib.pyplot as plt
#
# # =========================
# # Configurações de logging
# # =========================
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(levelname)s:%(name)s: %(message)s"
# )
# log = logging.getLogger("domains")
#
# # =========================
# # Paleta de cores (forçada)
# # =========================
# PALETTE = ["#3b5b92", "#6c8ebf", "#8aa8d6", "#b7c7ea",
#            "#777777", "#a0a0a0", "#c8c8c8", "#e0e0e0"]
#
# # =========================
# # Normalização de rótulos
# # =========================
# def _strip_accents(s: str) -> str:
#     return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
#
# def _clean_token(tok: str) -> str:
#     # trim, remove acentos, normaliza espaços, casefold
#     t = tok.strip()
#     t = _strip_accents(t)
#     t = re.sub(r"\s+", " ", t)
#     return t.casefold()
#
# # Mapa canônico (chaves sempre em casefold / sem acento)
# CANON_MAP: Dict[str, str] = {
#     # IIoT e indústria
#     "iiot": "IIoT",
#     "industrial iot": "IIoT",
#     "industrial edge computing": "IIoT",
#     "smart manufacturing": "IIoT",
#     "industry 4.0": "Industry 4.0",
#
#     "IIoT":"IIoT",
#     "Smart Environment":"Smart Environment",
#     "Data streaming processing":"Data streaming processing",
#
#     "smart environment": "Smart Environment",
#     "smart environments": "Smart Environment",
#
#     "computer vision": "Computer Vision",
#     "vision": "Computer Vision",
#     "speech": "Speech",
#     "audio analisys": "Audio Analysis",
#     "audio analysis": "Audio Analysis",
#     "chatbot": "Chatbot",
#
#     "orchestration": "Orchestration",
#
#     "federated learning": "Federated Learning",
#
#     "efficient ai": "Efficient AI",
#     "efficiente ai": "Efficient AI",  # typo comum
#     "aiot": "IoT",
#     "iot": "IoT",
#
#     "autonomous systems": "Autonomous Systems",
#     "autonomous system": "Autonomous Systems",
#     "robotic": "Robotics",
#     "robotics": "Robotics",
#
#     # Saúde
#     "healthcare": "Healthcare",
#     "medical iot": "Healthcare",
#
#     # Mobile
#     "mobile iot": "Mobile IoT",
#
#     # Tempo real / streaming (várias variações)
#     "real time data processing": "Data Streaming & Real-Time",
#     "real-time data processing": "Data Streaming & Real-Time",
#     "real-time data streaming": "Data Streaming & Real-Time",
#     "real time data streaming": "Data Streaming & Real-Time",
#     "data streaming processing": "Data Streaming & Real-Time",
#     "data streaming": "Data Streaming & Real-Time",
#
#     # Model-Driven
#     "model-driven engineering (mde)": "MDE",
#
#     # Outros
#     "others": "Others",
# }
#
# # Regras auxiliares (regex) para capturar variações antes do mapa
# _REGEX_RULES: List[Tuple[re.Pattern, str]] = [
#     # Qualquer coisa que contenha 'data' e 'stream' ou 'real time'
#     (re.compile(r"\b(real[-\s]?time|rt)\b", re.I), "Data Streaming & Real-Time"),
#     (re.compile(r"\bstream(ing)?\b", re.I), "Data Streaming & Real-Time"),
# ]
#
# def normalize_domain_token(raw: str) -> str:
#     """Normaliza um único token de domínio para forma canônica."""
#     base = _clean_token(raw)
#     if not base:
#         return ""
#
#     # 1) regras regex (captura amplo para streaming/real-time)
#     for pat, label in _REGEX_RULES:
#         if pat.search(base):
#             return label
#
#     # 2) mapa canônico (sinônimos/typos)
#     if base in CANON_MAP:
#         return CANON_MAP[base]
#
#     # 3) heurísticas simples
#     if base in {"autonomous", "autonomous systems"}:
#         return "Autonomous Systems"
#     if base in {"industrial", "industrial edge", "industrial internet of things"}:
#         return "IIoT"
#
#     # 4) Title Case como fallback
#     return re.sub(r"\s+", " ", raw.strip()).title()
#
# def split_domains(cell: str) -> List[str]:
#     """Divide a célula de domínios por vírgula, preservando itens compostos."""
#     if pd.isna(cell):
#         return []
#     # divide por vírgulas
#     parts = [p.strip() for p in str(cell).split(",")]
#     # remove vazios
#     return [p for p in parts if p]
#
# def normalize_domains(cells: Iterable[str]) -> List[str]:
#     out: List[str] = []
#     for c in cells:
#         label = normalize_domain_token(c)
#         if label:
#             out.append(label)
#     return out
#
# # =========================
# # Plot
# # =========================
# def plot_bar_counts(counts_df: pd.DataFrame, out_png: Path, out_pdf: Path, title: str = "Domain Distribution (Projects)"):
#     """
#     Gera gráfico de barras (uma cor por barra, seguindo a paleta definida).
#     """
#     # Ordena por contagem desc
#     df = counts_df.sort_values("count", ascending=False).copy()
#     labels = df["domain"].tolist()
#     values = df["count"].tolist()
#
#     # Cores: cicla a paleta, garantindo uma cor por barra
#     colors = [PALETTE[i % len(PALETTE)] for i in range(len(values))]
#
#     plt.figure(figsize=(12, max(4, 0.35 * len(labels))))  # altura adaptativa
#     bars = plt.barh(labels, values, color=colors)
#     plt.xlabel("Count")
#     # plt.title(title)
#     plt.gca().invert_yaxis()  # maior no topo
#     # rótulos de valor na barra
#     for bar, val in zip(bars, values):
#         plt.text(val + max(values)*0.01, bar.get_y() + bar.get_height()/2, str(val), va="center", fontsize=9)
#     plt.tight_layout()
#     plt.savefig(out_png, dpi=300)
#     plt.savefig(out_pdf)
#     plt.close()
#
# # =========================
# # Pipeline principal
# # =========================
# def main():
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--input", type=Path, required=True, help="CSV de entrada (coluna 'domain')")
#     ap.add_argument("--col", type=str, default="domain", help="Nome da coluna de domínios (default: domain)")
#     ap.add_argument("--idcol", type=str, default=None, help="Coluna de ID do projeto/repo (opcional)")
#     ap.add_argument("--out_fig_dir", type=Path, default=Path("../figs"))
#     ap.add_argument("--out_tab_dir", type=Path, default=Path("../tables"))
#     ap.add_argument("--topN", type=int, default=0, help="Se >0, plota apenas os top N domínios")
#     args = ap.parse_args()
#
#     args.out_fig_dir.mkdir(parents=True, exist_ok=True)
#     args.out_tab_dir.mkdir(parents=True, exist_ok=True)
#
#     log.info(f"Lendo: {args.input}")
#     df = pd.read_csv(args.input)
#
#     if args.col not in df.columns:
#         raise SystemExit(f"Coluna '{args.col}' não encontrada no CSV.")
#
#     id_series = None
#     if args.idcol and args.idcol in df.columns:
#         id_series = df[args.idcol]
#     else:
#         # cria um ID sequencial caso não exista
#         id_series = pd.Series(range(1, len(df) + 1), name="repo_id")
#
#     # --- Normalização para formato "long"
#     rows = []
#     for repo_id, cell in zip(id_series, df[args.col]):
#         raw_tokens = split_domains(cell)
#         norm_tokens = normalize_domains(raw_tokens)
#         # remove duplicados por projeto (se repetir)
#         norm_tokens = sorted(set(norm_tokens))
#         for t in norm_tokens:
#             rows.append({"repo_id": repo_id, "domain": t})
#
#     long_df = pd.DataFrame(rows)
#     # Salva long
#     long_path = args.out_tab_dir / "domains_normalized_long.csv"
#     long_df.to_csv(long_path, index=False)
#     log.info(f"OK: {long_path}")
#
#     # --- Contagens
#     counts = long_df["domain"].value_counts().rename_axis("domain").reset_index(name="count")
#
#     # TopN opcional (para o gráfico)
#     plot_df = counts.copy()
#     if args.topN and args.topN > 0:
#         plot_df = plot_df.head(args.topN)
#
#     # Salva tabela de contagens completa
#     counts_path = args.out_tab_dir / "domains_counts.csv"
#     counts.to_csv(counts_path, index=False)
#     log.info(f"OK: {counts_path}")
#
#     # --- Figura
#     out_png = args.out_fig_dir / "domains_distribution.png"
#     out_pdf = args.out_fig_dir / "domains_distribution.pdf"
#     title = "Domains Distribution (Projects)"
#     if args.topN and args.topN > 0:
#         title += f" — Top {args.topN}"
#
#     plot_bar_counts(plot_df, out_png, out_pdf, title=title)
#     log.info(f"OK: {out_png}")
#     log.info(f"OK: {out_pdf}")
#
# if __name__ == "__main__":
#     main()
