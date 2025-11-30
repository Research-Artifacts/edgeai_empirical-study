# -*- coding: utf-8 -*-
"""
Likert Chart Generator for EdgeAI Survey (Google Forms CSV)
----------------------------------------------------------
- Detecta automaticamente colunas com respostas tipo Likert:
  • "Very not useful", "Not useful", "Neutral", "Useful", "Very useful"
  • "Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"
  • Mapeia também escalas numéricas 1–5, 0–4 e 1–7 para a escala de 5 pontos.
- Gera gráfico de barras horizontais empilhadas (um único plot, sem cores fixas).
- Exporta contagens e percentuais para CSV.
- Opções: encurtar rótulos (ex.: “[G01] …”), filtrar só perguntas de guidelines, etc.

Uso:
    python likert_generator.py \
        --input "/caminho/para/Survey - ... respostas.tables" \
        --out-figs "./figs" \
        --out-tables "./tables" \
        --scale useful agree \
        --shorten-labels \
        --only-guidelines

Requisitos:
    pip install pandas matplotlib numpy

Autor: você :) — com uma ajudinha do seu co-piloto
"""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------
# Logging
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s"
)
log = logging.getLogger("likert")


# ---------------------------
# Escalas e normalização
# ---------------------------

USEFULNESS_ORDER = ["Very not useful", "Not useful", "Neutral", "Useful", "Very useful"]
AGREE_ORDER = ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"]

USEFULNESS_SET = {s.lower() for s in USEFULNESS_ORDER}
AGREE_SET = {s.lower() for s in AGREE_ORDER}

TEXT_ALIASES = {
    # agree 5-pt (EN/PT)
    "strongly disagree": "Strongly disagree",
    "disagree": "Disagree",
    "neutral": "Neutral",
    "neither agree nor disagree": "Neutral",
    "agree": "Agree",
    "strongly agree": "Strongly agree",
    "discordo totalmente": "Strongly disagree",
    "discordo": "Disagree",
    "neutro": "Neutral",
    "nem concordo nem discordo": "Neutral",
    "concordo": "Agree",
    "concordo totalmente": "Strongly agree",

    # usefulness 5-pt (EN)
    "very not useful": "Very not useful",
    "not useful": "Not useful",
    "useful": "Useful",
    "very useful": "Very useful",
}

def _strip_score_suffix(s: str) -> str:
    # Remove sufixos do tipo " (4)" ao final
    return re.sub(r"\s*\(\d+\)\s*$", "", s)

def normalize_agree_text(x: object) -> Optional[str]:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    s = str(x).strip().lower()
    s = _strip_score_suffix(s)
    return TEXT_ALIASES.get(s, None)

def normalize_usefulness_text(x: object) -> Optional[str]:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    s = str(x).strip().lower()
    s = _strip_score_suffix(s)
    # Pequena tolerância
    if s == "verynotuseful":  # se vier sem espaço por algum motivo
        s = "very not useful"
    return TEXT_ALIASES.get(s, None)

def numeric_to_5pt(x: object) -> Optional[str]:
    """Mapeia 1..5, 0..4 ou 1..7 para a escala 'Strongly disagree'..'Strongly agree' (genérica 5-pt)."""
    try:
        v = float(str(x).strip())
    except Exception:
        return None
    if np.isnan(v):
        return None
    # 1..5 (clássica)
    if v in [1, 2, 3, 4, 5]:
        return {
            1: "Strongly disagree",
            2: "Disagree",
            3: "Neutral",
            4: "Agree",
            5: "Strongly agree",
        }[v]
    # 0..4
    if v in [0, 1, 2, 3, 4]:
        return {
            0: "Strongly disagree",
            1: "Disagree",
            2: "Neutral",
            3: "Agree",
            4: "Strongly agree",
        }[v]
    # 1..7 → colapsa bordas
    if v in [1, 2, 3, 4, 5, 6, 7]:
        if v <= 2:
            return "Strongly disagree"
        if v == 3:
            return "Disagree"
        if v == 4:
            return "Neutral"
        if v == 5:
            return "Agree"
        return "Strongly agree"
    return None


# ---------------------------
# Detecção de colunas Likert
# ---------------------------

def detect_likert_columns(
    df: pd.DataFrame,
    consider_scales: List[str]
) -> Dict[str, Dict]:
    """
    Retorna um dicionário col->perfil com as colunas que parecem Likert
    de acordo com as escalas indicadas em `consider_scales` (ex.: ["useful","agree"]).
    """
    profiles: Dict[str, Dict] = {}
    for col in df.columns:
        series = df[col]

        # Tenta usefulness
        mapped_use = series.map(normalize_usefulness_text) if "useful" in consider_scales else pd.Series([None]*len(series))
        # Tenta agree
        mapped_agree = series.map(normalize_agree_text) if "agree" in consider_scales else pd.Series([None]*len(series))
        # Tenta numérica → genérica agree 5-pt
        mapped_num = series.map(numeric_to_5pt) if "agree" in consider_scales else pd.Series([None]*len(series))

        # escolhe a melhor cobertura
        cand = max(
            [("useful", mapped_use), ("agree_txt", mapped_agree), ("agree_num", mapped_num)],
            key=lambda t: t[1].notna().sum()
        )
        key, mapped = cand
        non_null = mapped.dropna()

        if non_null.empty:
            continue

        coverage = non_null.size / max(1, series.notna().sum())
        # precisa de diversidade mínima de níveis (>=3)
        distinct = list(pd.Index(non_null.unique()))
        if coverage >= 0.50 and len(set(distinct)) >= 3:
            if key == "useful":
                order = USEFULNESS_ORDER
                scale = "useful"
            else:
                order = AGREE_ORDER
                scale = "agree"  # tanto txt quanto num viram agree
            profiles[col] = {
                "scale": scale,
                "order": order,
                "coverage": round(float(coverage), 3),
                "valid": int(non_null.size),
                "levels_observed": [lvl for lvl in order if lvl in set(non_null.unique())]
            }

    return profiles


# ---------------------------
# Plot e tabelas
# ---------------------------

def build_tables(
    df: pd.DataFrame,
    profiles: Dict[str, Dict],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rows_counts = []
    rows_pcts = []
    for col, meta in profiles.items():
        scale = meta["scale"]
        order = meta["order"]

        if scale == "useful":
            mapped = df[col].map(normalize_usefulness_text)
        else:
            # "agree": tenta numérico, se vazio cai no texto
            mapped = df[col].map(numeric_to_5pt)
            if mapped.dropna().empty:
                mapped = df[col].map(normalize_agree_text)

        counts = mapped.value_counts().reindex(order, fill_value=0)
        total = counts.sum()
        pcts = (counts / total * 100.0).round(1) if total else counts.astype(float)

        rows_counts.append({"question": col, **counts.to_dict()})
        rows_pcts.append({"question": col, **pcts.to_dict()})

    counts_df = (
        pd.DataFrame(rows_counts).set_index("question")
        if rows_counts else
        pd.DataFrame(columns=["question"]).set_index("question")
    )
    pcts_df = (
        pd.DataFrame(rows_pcts).set_index("question")
        if rows_pcts else
        pd.DataFrame(columns=["question"]).set_index("question")
    )
    return counts_df, pcts_df

def shorten_label(label: str) -> str:
    """
    Extrai apenas o ID da guideline no formato [Gxx] e descarta todo o texto.
    Exemplos:
        "[G15 - texto grande]" → "[G15]"
        "[ G 7 ] texto"        → "[G07]"
    """
    # Captura padrões [G15], [G 15], [G15 - ...], etc.
    m = re.search(r"\[\s*G\s*0*(\d+)", label, flags=re.IGNORECASE)
    if m:
        gid = m.group(1).zfill(2)
        return f"[G{gid}]"

    # fallback para casos sem guideline → corta se muito grande
    return (label[:80] + "…") if len(label) > 80 else label

#
# def shorten_label(label: str) -> str:
#     """
#     Reduz rótulos longos. Ex.: mantém prefixos de guideline "[G01]" se houver.
#     Se não houver padrão [Gxx], tenta pegar o início até ~80 chars.
#     """
#     m = re.search(r"\[G\s*0*(\d+)\]", label, flags=re.IGNORECASE)
#     if m:
#         gid = m.group(1).zfill(2)
#         return f"[G{gid}]"
#     # também há casos onde o label começa com ' [G10 - ...' (com espaço à esquerda)
#     m2 = re.search(r"\[\s*G\s*0*(\d+)\s*[-\]]", label, flags=re.IGNORECASE)
#     if m2:
#         gid = m2.group(1).zfill(2)
#         return f"[G{gid}]"
#
#     # fallback: corta
#     return (label[:80] + "…") if len(label) > 80 else label


def plot_stacked_likert(
    pcts_df: pd.DataFrame,
    profiles: Dict[str, Dict],
    out_png: Path,
    out_pdf: Path,
    shorten_labels_flag: bool,
    only_guidelines_flag: bool,
    title: str = "Likert overview (partial survey)",
    counts_df: Optional[pd.DataFrame] = None,
    figsize_base: float = 0.42,
) -> None:
    """
    Gera gráfico de barras horizontais empilhadas.
    Agora adiciona, em cada segmento colorido, o quantitativo (contagem) correspondente,
    se counts_df for fornecido.
    """
    if pcts_df.empty:
        log.warning("Nada a plotar: dataframe de percentuais vazio.")
        return

    # Reordena linhas: agrupa por escala e mantém ordem de colunas da respectiva escala
    # Também permite filtrar para apenas perguntas com “[G…]” se solicitado
    questions = list(pcts_df.index)
    if only_guidelines_flag:
        questions = [q for q in questions if re.search(r"\[\s*G\s*\d+", q, flags=re.IGNORECASE)]
        if not questions:
            log.warning("Flag --only-guidelines ativa, mas nenhuma pergunta com '[G..]' foi encontrada.")
            return
        pcts_df = pcts_df.loc[questions]
        if counts_df is not None:
            counts_df = counts_df.loc[questions]

    # Para plotar, garantimos que as colunas estejam em ordem consistente por linha (escala)
    agree_rows = [q for q in pcts_df.index if profiles[q]["scale"] == "agree"]
    usef_rows = [q for q in pcts_df.index if profiles[q]["scale"] == "useful"]

    parts = []
    if agree_rows:
        part_agree = pcts_df.loc[agree_rows, AGREE_ORDER]
        parts.append(part_agree)
    if usef_rows:
        part_usef = pcts_df.loc[usef_rows, USEFULNESS_ORDER]
        parts.append(part_usef)

    plot_df = pd.concat(parts, axis=0) if parts else pcts_df

    # Ajusta também counts_df para ter a mesma ordem de linhas
    if counts_df is not None:
        counts_df = counts_df.loc[plot_df.index]

    # Labels no eixo Y
    y_labels = [shorten_label(q) if shorten_labels_flag else q for q in plot_df.index]

    plt.figure(figsize=(10, max(3, figsize_base * len(plot_df))))
    y_pos = np.arange(len(plot_df))

    left = np.zeros(len(plot_df))
    for level in plot_df.columns:
        vals = plot_df[level].values

        # barra empilhada para esse nível
        bars = plt.barh(y_pos, vals, left=left, label=level)

        # recupera contagens para esse nível (mesma ordem das linhas)
        if counts_df is not None and level in counts_df.columns:
            counts_vals = counts_df[level].values
        else:
            counts_vals = [None] * len(vals)

        # adiciona texto no centro de cada segmento com o quantitativo
        for bar, val, cnt in zip(bars, vals, counts_vals):
            if val <= 0:
                continue
            if cnt is None or cnt == 0:
                continue
            x = bar.get_x() + bar.get_width() / 2.0
            y = bar.get_y() + bar.get_height() / 2.0
            plt.text(x, y, str(int(cnt)), ha="center", va="center", fontsize=8)

        left = left + vals

    plt.yticks(y_pos, y_labels)
    plt.xlabel("Percentage of responses (%)")
    plt.title(title)
    # Legenda fora, canto superior direito
    plt.legend(loc="lower right", bbox_to_anchor=(1.0, 1.02))
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.savefig(out_pdf, bbox_inches="tight")
    plt.close()


# ---------------------------
# CSV robust loader
# ---------------------------

def load_csv_robust(path: Path) -> pd.DataFrame:
    """
    Tenta carregar o CSV do Google Forms de forma robusta.
    """
    # engine='python' com sep=None tenta inferir delimitador
    try:
        df = pd.read_csv(path, engine="python", sep=None)
        return df
    except Exception as e:
        log.warning(f"Leitura com sep=None falhou ({e}), tentando UTF-8 padrão…")
    # fallback simples
    return pd.read_csv(path)


# ---------------------------
# CLI
# ---------------------------

def main():
    ap = argparse.ArgumentParser(description="Generate Likert overview chart from survey CSV.")
    ap.add_argument("--input", required=True, type=Path, help="Caminho do CSV exportado do Google Forms.")
    ap.add_argument("--out-figs", default=Path("./figs"), type=Path, help="Diretório de saída das figuras.")
    ap.add_argument("--out-tables", default=Path("./tables"), type=Path, help="Diretório de saída das tabelas.")
    ap.add_argument("--basename", default="likert_overview", help="Nome base dos arquivos de saída.")
    ap.add_argument("--scale", nargs="+", choices=["useful", "agree"], default=["useful", "agree"],
                    help="Quais escalas considerar na detecção.")
    ap.add_argument("--shorten-labels", action="store_true",
                    help="Encurta rótulos (ex.: '[G01]').")
    ap.add_argument("--only-guidelines", action="store_true",
                    help="Plota apenas perguntas com padrão '[G..]'.")
    ap.add_argument("--title", default="Likert overview (partial survey)", help="Título da figura.")
    args = ap.parse_args()

    df = load_csv_robust(args.input)
    log.info(f"CSV carregado: {df.shape[0]} linhas, {df.shape[1]} colunas.")

    profiles = detect_likert_columns(df, consider_scales=args.scale)
    if not profiles:
        log.error("Nenhuma coluna Likert detectada com as escalas selecionadas.")
        return

    log.info(f"Colunas detectadas ({len(profiles)}):")
    for c, meta in profiles.items():
        log.info(f" - {c[:80]}… | scale={meta['scale']} | coverage={meta['coverage']} | levels={meta['levels_observed']}")

    counts_df, pcts_df = build_tables(df, profiles)

    # Salvar tabelas
    args.out_tables.mkdir(parents=True, exist_ok=True)
    counts_path = args.out_tables / f"{args.basename}_counts.csv"
    pcts_path = args.out_tables / f"{args.basename}_percentages.csv"
    counts_df.to_csv(counts_path, encoding="utf-8")
    pcts_df.to_csv(pcts_path, encoding="utf-8")
    log.info(f"Tabelas salvas em:\n  - {counts_path}\n  - {pcts_path}")

    # Plot (agora com contagens para as legendas nas barras)
    args.out_figs.mkdir(parents=True, exist_ok=True)
    fig_png = args.out_figs / f"{args.basename}.png"
    fig_pdf = args.out_figs / f"{args.basename}.pdf"
    plot_stacked_likert(
        pcts_df=pcts_df,
        profiles=profiles,
        out_png=fig_png,
        out_pdf=fig_pdf,
        shorten_labels_flag=args.shorten_labels,
        only_guidelines_flag=args.only_guidelines,
        title=args.title,
        counts_df=counts_df,
    )
    log.info(f"Figuras salvas em:\n  - {fig_png}\n  - {fig_pdf}")

    # Opcional: exportar mapeamento ID curto → label completo, útil pro paper
    if args.shorten_labels:
        mapping = pd.DataFrame({
            "question": pcts_df.index,
            "alias": [shorten_label(q) for q in pcts_df.index]
        })
        map_path = args.out_tables / f"{args.basename}_label_map.csv"
        mapping.to_csv(map_path, index=False, encoding="utf-8")
        log.info(f"Mapa de rótulos salvo em: {map_path}")


if __name__ == "__main__":
    main()


# # -*- coding: utf-8 -*-
# """
# Likert Chart Generator for EdgeAI Survey (Google Forms CSV)
# ----------------------------------------------------------
# - Detecta automaticamente colunas com respostas tipo Likert:
#   • "Very not useful", "Not useful", "Neutral", "Useful", "Very useful"
#   • "Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"
#   • Mapeia também escalas numéricas 1–5, 0–4 e 1–7 para a escala de 5 pontos.
# - Gera gráfico de barras horizontais empilhadas (um único plot, sem cores fixas).
# - Exporta contagens e percentuais para CSV.
# - Opções: encurtar rótulos (ex.: “[G01] …”), filtrar só perguntas de guidelines, etc.
#
# Uso:
#     python likert_generator.py \
#         --input "/caminho/para/Survey - ... respostas.tables" \
#         --out-figs "./figs" \
#         --out-tables "./tables" \
#         --scale useful agree \
#         --shorten-labels \
#         --only-guidelines
#
# Requisitos:
#     pip install pandas matplotlib numpy
#
# Autor: você :) — com uma ajudinha do seu co-piloto
# """
#
# from __future__ import annotations
#
# import argparse
# import logging
# import re
# from pathlib import Path
# from typing import Dict, List, Optional, Tuple
#
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
#
#
# # ---------------------------
# # Logging
# # ---------------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(levelname)s | %(message)s"
# )
# log = logging.getLogger("likert")
#
#
# # ---------------------------
# # Escalas e normalização
# # ---------------------------
#
# USEFULNESS_ORDER = ["Very not useful", "Not useful", "Neutral", "Useful", "Very useful"]
# AGREE_ORDER = ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"]
#
# USEFULNESS_SET = {s.lower() for s in USEFULNESS_ORDER}
# AGREE_SET = {s.lower() for s in AGREE_ORDER}
#
# TEXT_ALIASES = {
#     # agree 5-pt (EN/PT)
#     "strongly disagree": "Strongly disagree",
#     "disagree": "Disagree",
#     "neutral": "Neutral",
#     "neither agree nor disagree": "Neutral",
#     "agree": "Agree",
#     "strongly agree": "Strongly agree",
#     "discordo totalmente": "Strongly disagree",
#     "discordo": "Disagree",
#     "neutro": "Neutral",
#     "nem concordo nem discordo": "Neutral",
#     "concordo": "Agree",
#     "concordo totalmente": "Strongly agree",
#
#     # usefulness 5-pt (EN)
#     "very not useful": "Very not useful",
#     "not useful": "Not useful",
#     "useful": "Useful",
#     "very useful": "Very useful",
# }
#
# def _strip_score_suffix(s: str) -> str:
#     # Remove sufixos do tipo " (4)" ao final
#     return re.sub(r"\s*\(\d+\)\s*$", "", s)
#
# def normalize_agree_text(x: object) -> Optional[str]:
#     if x is None or (isinstance(x, float) and np.isnan(x)):
#         return None
#     s = str(x).strip().lower()
#     s = _strip_score_suffix(s)
#     return TEXT_ALIASES.get(s, None)
#
# def normalize_usefulness_text(x: object) -> Optional[str]:
#     if x is None or (isinstance(x, float) and np.isnan(x)):
#         return None
#     s = str(x).strip().lower()
#     s = _strip_score_suffix(s)
#     # Pequena tolerância
#     if s == "verynotuseful":  # se vier sem espaço por algum motivo
#         s = "very not useful"
#     return TEXT_ALIASES.get(s, None)
#
# def numeric_to_5pt(x: object) -> Optional[str]:
#     """Mapeia 1..5, 0..4 ou 1..7 para a escala 'Strongly disagree'..'Strongly agree' (genérica 5-pt)."""
#     try:
#         v = float(str(x).strip())
#     except Exception:
#         return None
#     if np.isnan(v):
#         return None
#     # 1..5 (clássica)
#     if v in [1, 2, 3, 4, 5]:
#         return {
#             1: "Strongly disagree",
#             2: "Disagree",
#             3: "Neutral",
#             4: "Agree",
#             5: "Strongly agree",
#         }[v]
#     # 0..4
#     if v in [0, 1, 2, 3, 4]:
#         return {
#             0: "Strongly disagree",
#             1: "Disagree",
#             2: "Neutral",
#             3: "Agree",
#             4: "Strongly agree",
#         }[v]
#     # 1..7 → colapsa bordas
#     if v in [1, 2, 3, 4, 5, 6, 7]:
#         if v <= 2:
#             return "Strongly disagree"
#         if v == 3:
#             return "Disagree"
#         if v == 4:
#             return "Neutral"
#         if v == 5:
#             return "Agree"
#         return "Strongly agree"
#     return None
#
#
# # ---------------------------
# # Detecção de colunas Likert
# # ---------------------------
#
# def detect_likert_columns(
#     df: pd.DataFrame,
#     consider_scales: List[str]
# ) -> Dict[str, Dict]:
#     """
#     Retorna um dicionário col->perfil com as colunas que parecem Likert
#     de acordo com as escalas indicadas em `consider_scales` (ex.: ["useful","agree"]).
#     """
#     profiles: Dict[str, Dict] = {}
#     for col in df.columns:
#         series = df[col]
#
#         # Tenta usefulness
#         mapped_use = series.map(normalize_usefulness_text) if "useful" in consider_scales else pd.Series([None]*len(series))
#         # Tenta agree
#         mapped_agree = series.map(normalize_agree_text) if "agree" in consider_scales else pd.Series([None]*len(series))
#         # Tenta numérica → genérica agree 5-pt
#         mapped_num = series.map(numeric_to_5pt) if "agree" in consider_scales else pd.Series([None]*len(series))
#
#         # escolhe a melhor cobertura
#         cand = max(
#             [("useful", mapped_use), ("agree_txt", mapped_agree), ("agree_num", mapped_num)],
#             key=lambda t: t[1].notna().sum()
#         )
#         key, mapped = cand
#         non_null = mapped.dropna()
#
#         if non_null.empty:
#             continue
#
#         coverage = non_null.size / max(1, series.notna().sum())
#         # precisa de diversidade mínima de níveis (>=3)
#         distinct = list(pd.Index(non_null.unique()))
#         if coverage >= 0.50 and len(set(distinct)) >= 3:
#             if key == "useful":
#                 order = USEFULNESS_ORDER
#                 scale = "useful"
#             else:
#                 order = AGREE_ORDER
#                 scale = "agree"  # tanto txt quanto num viram agree
#             profiles[col] = {
#                 "scale": scale,
#                 "order": order,
#                 "coverage": round(float(coverage), 3),
#                 "valid": int(non_null.size),
#                 "levels_observed": [lvl for lvl in order if lvl in set(non_null.unique())]
#             }
#
#     return profiles
#
#
# # ---------------------------
# # Plot e tabelas
# # ---------------------------
#
# def build_tables(
#     df: pd.DataFrame,
#     profiles: Dict[str, Dict],
# ) -> Tuple[pd.DataFrame, pd.DataFrame]:
#     rows_counts = []
#     rows_pcts = []
#     for col, meta in profiles.items():
#         scale = meta["scale"]
#         order = meta["order"]
#
#         if scale == "useful":
#             mapped = df[col].map(normalize_usefulness_text)
#         else:
#             # "agree": tenta numérico, se vazio cai no texto
#             mapped = df[col].map(numeric_to_5pt)
#             if mapped.dropna().empty:
#                 mapped = df[col].map(normalize_agree_text)
#
#         counts = mapped.value_counts().reindex(order, fill_value=0)
#         total = counts.sum()
#         pcts = (counts / total * 100.0).round(1) if total else counts.astype(float)
#
#         rows_counts.append({"question": col, **counts.to_dict()})
#         rows_pcts.append({"question": col, **pcts.to_dict()})
#
#     counts_df = (
#         pd.DataFrame(rows_counts).set_index("question")
#         if rows_counts else
#         pd.DataFrame(columns=["question"]).set_index("question")
#     )
#     pcts_df = (
#         pd.DataFrame(rows_pcts).set_index("question")
#         if rows_pcts else
#         pd.DataFrame(columns=["question"]).set_index("question")
#     )
#     return counts_df, pcts_df
#
#
# def shorten_label(label: str) -> str:
#     """
#     Reduz rótulos longos. Ex.: mantém prefixos de guideline "[G01]" se houver.
#     Se não houver padrão [Gxx], tenta pegar o início até ~80 chars.
#     """
#     m = re.search(r"\[G\s*0*(\d+)\]", label, flags=re.IGNORECASE)
#     if m:
#         gid = m.group(1).zfill(2)
#         return f"[G{gid}]"
#     # também há casos onde o label começa com ' [G10 - ...' (com espaço à esquerda)
#     m2 = re.search(r"\[\s*G\s*0*(\d+)\s*[-\]]", label, flags=re.IGNORECASE)
#     if m2:
#         gid = m2.group(1).zfill(2)
#         return f"[G{gid}]"
#
#     # fallback: corta
#     return (label[:80] + "…") if len(label) > 80 else label
#
#
# def plot_stacked_likert(
#     pcts_df: pd.DataFrame,
#     profiles: Dict[str, Dict],
#     out_png: Path,
#     out_pdf: Path,
#     shorten_labels_flag: bool,
#     only_guidelines_flag: bool,
#     figsize_base: float = 0.42,
#     title: str = "Likert overview (partial survey)"
# ) -> None:
#     if pcts_df.empty:
#         log.warning("Nada a plotar: dataframe de percentuais vazio.")
#         return
#
#     # Reordena linhas: agrupa por escala e mantém ordem de colunas da respectiva escala
#     # Também permite filtrar para apenas perguntas com “[G…]” se solicitado
#     questions = list(pcts_df.index)
#     if only_guidelines_flag:
#         questions = [q for q in questions if re.search(r"\[\s*G\s*\d+", q, flags=re.IGNORECASE)]
#         if not questions:
#             log.warning("Flag --only-guidelines ativa, mas nenhuma pergunta com '[G..]' foi encontrada.")
#             return
#         pcts_df = pcts_df.loc[questions]
#
#     # Para plotar, garantimos que as colunas estejam em ordem consistente por linha (escala)
#     # Estratégia: dividir por escala e concatenar depois
#     agree_rows = [q for q in pcts_df.index if profiles[q]["scale"] == "agree"]
#     usef_rows = [q for q in pcts_df.index if profiles[q]["scale"] == "useful"]
#
#     parts = []
#     if agree_rows:
#         part_agree = pcts_df.loc[agree_rows, AGREE_ORDER]
#         parts.append(part_agree)
#     if usef_rows:
#         part_usef = pcts_df.loc[usef_rows, USEFULNESS_ORDER]
#         parts.append(part_usef)
#
#     plot_df = pd.concat(parts, axis=0) if parts else pcts_df
#
#     # Labels no eixo Y
#     y_labels = [shorten_label(q) if shorten_labels_flag else q for q in plot_df.index]
#
#     plt.figure(figsize=(10, max(3, figsize_base * len(plot_df))))
#     y_pos = np.arange(len(plot_df))
#
#     left = np.zeros(len(plot_df))
#     for level in plot_df.columns:
#         vals = plot_df[level].values
#         plt.barh(y_pos, vals, left=left, label=level)
#         left = left + vals
#
#     plt.yticks(y_pos, y_labels)
#     plt.xlabel("Percentage of responses (%)")
#     plt.title(title)
#     # Legenda fora, canto superior direito
#     plt.legend(loc="lower right", bbox_to_anchor=(1.0, 1.02))
#     plt.tight_layout()
#     out_png.parent.mkdir(parents=True, exist_ok=True)
#     out_pdf.parent.mkdir(parents=True, exist_ok=True)
#     plt.savefig(out_png, dpi=300, bbox_inches="tight")
#     plt.savefig(out_pdf, bbox_inches="tight")
#     plt.close()
#
#
# # ---------------------------
# # CSV robust loader
# # ---------------------------
#
# def load_csv_robust(path: Path) -> pd.DataFrame:
#     """
#     Tenta carregar o CSV do Google Forms de forma robusta.
#     """
#     # engine='python' com sep=None tenta inferir delimitador
#     try:
#         df = pd.read_csv(path, engine="python", sep=None)
#         return df
#     except Exception as e:
#         log.warning(f"Leitura com sep=None falhou ({e}), tentando UTF-8 padrão…")
#     # fallback simples
#     return pd.read_csv(path)
#
#
# # ---------------------------
# # CLI
# # ---------------------------
#
# def main():
#     ap = argparse.ArgumentParser(description="Generate Likert overview chart from survey CSV.")
#     ap.add_argument("--input", required=True, type=Path, help="Caminho do CSV exportado do Google Forms.")
#     ap.add_argument("--out-figs", default=Path("./figs"), type=Path, help="Diretório de saída das figuras.")
#     ap.add_argument("--out-tables", default=Path("./tables"), type=Path, help="Diretório de saída das tabelas.")
#     ap.add_argument("--basename", default="likert_overview", help="Nome base dos arquivos de saída.")
#     ap.add_argument("--scale", nargs="+", choices=["useful", "agree"], default=["useful", "agree"],
#                     help="Quais escalas considerar na detecção.")
#     ap.add_argument("--shorten-labels", action="store_true",
#                     help="Encurta rótulos (ex.: '[G01]').")
#     ap.add_argument("--only-guidelines", action="store_true",
#                     help="Plota apenas perguntas com padrão '[G..]'.")
#     ap.add_argument("--title", default="Likert overview (partial survey)", help="Título da figura.")
#     args = ap.parse_args()
#
#     df = load_csv_robust(args.input)
#     log.info(f"CSV carregado: {df.shape[0]} linhas, {df.shape[1]} colunas.")
#
#     profiles = detect_likert_columns(df, consider_scales=args.scale)
#     if not profiles:
#         log.error("Nenhuma coluna Likert detectada com as escalas selecionadas.")
#         return
#
#     log.info(f"Colunas detectadas ({len(profiles)}):")
#     for c, meta in profiles.items():
#         log.info(f" - {c[:80]}… | scale={meta['scale']} | coverage={meta['coverage']} | levels={meta['levels_observed']}")
#
#     counts_df, pcts_df = build_tables(df, profiles)
#
#     # Salvar tabelas
#     args.out_tables.mkdir(parents=True, exist_ok=True)
#     counts_path = args.out_tables / f"{args.basename}_counts.tables"
#     pcts_path = args.out_tables / f"{args.basename}_percentages.tables"
#     counts_df.to_csv(counts_path, encoding="utf-8")
#     pcts_df.to_csv(pcts_path, encoding="utf-8")
#     log.info(f"Tabelas salvas em:\n  - {counts_path}\n  - {pcts_path}")
#
#     # Plot
#     args.out_figs.mkdir(parents=True, exist_ok=True)
#     fig_png = args.out_figs / f"{args.basename}.png"
#     fig_pdf = args.out_figs / f"{args.basename}.pdf"
#     plot_stacked_likert(
#         pcts_df=pcts_df,
#         profiles=profiles,
#         out_png=fig_png,
#         out_pdf=fig_pdf,
#         shorten_labels_flag=args.shorten_labels,
#         only_guidelines_flag=args.only_guidelines,
#         title=args.title
#     )
#     log.info(f"Figuras salvas em:\n  - {fig_png}\n  - {fig_pdf}")
#
#     # Opcional: exportar mapeamento ID curto → label completo, útil pro paper
#     if args.shorten_labels:
#         mapping = pd.DataFrame({
#             "question": pcts_df.index,
#             "alias": [shorten_label(q) for q in pcts_df.index]
#         })
#         map_path = args.out_tables / f"{args.basename}_label_map.tables"
#         mapping.to_csv(map_path, index=False, encoding="utf-8")
#         log.info(f"Mapa de rótulos salvo em: {map_path}")
#
#
# if __name__ == "__main__":
#     main()
#

# python likert_scale_survey.py \
#   --input "../dataset/[Empirical_study]-survey_responses.tables" \
#   --out-figs "../figs" \
#   --out-tables "../tables" \
#   --basename "likert_usefulness_overview" \
#   --scale useful agree \
#   --shorten-labels \
#   --only-guidelines \
#   --title "Usefulness of Guidelines (partial survey)"
