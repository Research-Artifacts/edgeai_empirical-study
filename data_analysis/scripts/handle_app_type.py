# -*- coding: utf-8 -*-
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

INPUT = Path("../dataset/[Empirical Study]-sa_doc(70).csv")
OUT_DIR_FIG = Path("../results/figs")
OUT_DIR_TAB = Path("../results/tables")
OUT_DIR_FIG.mkdir(parents=True, exist_ok=True)
OUT_DIR_TAB.mkdir(parents=True, exist_ok=True)

FIG_BASENAME = "distribution_arch_layers"
PNG_PATH = OUT_DIR_FIG / f"{FIG_BASENAME}.png"
PDF_PATH = OUT_DIR_FIG / f"{FIG_BASENAME}.pdf"
CSV_COUNTS_PATH = OUT_DIR_TAB / f"{FIG_BASENAME}_counts.csv"

plt.rcParams.update({
    "figure.dpi": 180, "savefig.dpi": 300, "figure.figsize": (6.3, 3.4),
    "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
    "xtick.labelsize": 9, "ytick.labelsize": 9, "axes.grid": True,
    "grid.alpha": 0.25, "grid.linestyle": "--", "axes.spines.top": False,
    "axes.spines.right": False,
})

# Ordem final padronizada
ORDER = ["Meta-Architecture", "Platform/Infrastructure", "System", "Subsystem"]

def _str(x) -> str:
    """Coerção segura para string, evitando NaN/None/numéricos."""
    return x if isinstance(x, str) else ""

def normalize_label(raw: str) -> str:
    s = _str(raw).strip().lower().replace("_", " ").replace("-", "")
    s = s.replace("full system", "system")
    s = s.replace("sub system", "subsystem")
    s = s.replace("sub-sistema", "subsystem")
    s = s.replace("sistema", "system")
    s = s.replace("plataforma", "platform")
    return s

def map_arch_layer(label: str, name_hint: str = "") -> str:
    """
    Mapeia application_type + pista textual ('desc.') para:
      Meta-Architecture | Platform/Infrastructure | System | Subsystem
    """
    l = normalize_label(label)
    n = _str(name_hint).lower()

    # mapeamentos diretos
    if l == "system":
        return "System"
    if l == "subsystem":
        return "Subsystem"
    if l in {"platform", "platform/framework", "framework/platform"}:
        return "Platform/Infrastructure"
    if l == "framework":
        # Heurística: meta vs platform
        meta_keys = [
            "42010", "reference architecture", "viewpoint", "viewpoints",
            "metamodel", "iso 30141", "30141", "togaf", "dodaf", "adl",
            "architecture description", "architecture framework", "reference model",
            " ra ", " ra:", " ra-", " ra/", "model-driven"
        ]
        plat_keys = [
            "ros", "ros2", "kubernetes", "triton", "tensorrt", "tensorflow",
            "pytorch", "sdk", "runtime", "broker", "mqtt", "kafka", "grpc",
            "onnx", "inference", "edge", "jetson", "cuda", "rcl", "operator",
            "operator-sdk", "helm", "microservice", "deployment"
        ]
        if any(k in n for k in meta_keys):
            return "Meta-Architecture"
        if any(k in n for k in plat_keys):
            return "Platform/Infrastructure"
        return "Platform/Infrastructure"

    return "System"

# =========================
# Carrega e trata o dataset
# =========================
df = pd.read_csv(INPUT)

# Checagem correta da coluna usada
if "application_type" not in df.columns:
    raise ValueError("Coluna 'architectural_layer' não encontrada no CSV.")

# Drop de linhas sem rótulo
df = df.dropna(subset=["application_type"]).copy()

# Usa 'desc.' (se existir) como pista textual
hint_col = "desc." if "desc." in df.columns else None

# AQUI estava o bug: garantir coerção str antes da heurística
if hint_col:
    df["Architectural Layer"] = df.apply(
        lambda r: map_arch_layer(r["application_type"], _str(r.get(hint_col, ""))),
        axis=1
    )
else:
    df["Architectural Layer"] = df.apply(
        lambda r: map_arch_layer(r["application_type"]),
        axis=1
    )

# Categoria ordenada & alinhada à ORDER
df["Architectural Layer"] = pd.Categorical(df["Architectural Layer"], categories=ORDER, ordered=True)

# Contagens + percentuais
counts = df["Architectural Layer"].value_counts(dropna=False).reindex(ORDER).fillna(0).astype(int)
total = int(counts.sum())
perc = (counts / total * 100.0).round(1)

# Salva tabela
out_counts = pd.DataFrame({"Layer": ORDER, "Count": counts.values, "Percent": perc.values})
out_counts.to_csv(CSV_COUNTS_PATH, index=False)

# Plot
fig, ax = plt.subplots()
# paleta com 4 cores → casa com ORDER de 4 itens
colors = ["#3b5b92", "#6c8ebf", "#888888", "#b0b0b0"]
bars = ax.bar(ORDER, counts.values, color=colors, edgecolor="#222222", linewidth=0.8)

ax.set_xlabel("Application Type (Normalized)")
ax.set_ylabel("Frequency")
ax.grid(axis="y")

for rect, c, p in zip(bars, counts.values, perc.values):
    height = rect.get_height()
    label = f"{c} ({p:.1f}%)" if total > 0 else "0 (0%)"
    ax.annotate(label, xy=(rect.get_x() + rect.get_width()/2, height),
                xytext=(0, 5), textcoords="offset points",
                ha="center", va="bottom", fontsize=9)

plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
fig.tight_layout()
fig.savefig(PNG_PATH, dpi=300, bbox_inches="tight")
fig.savefig(PDF_PATH, bbox_inches="tight")

print(f"[OK] Figura salva em:\n - {PNG_PATH}\n - {PDF_PATH}")
print(f"[OK] Tabela de contagens salva em:\n - {CSV_COUNTS_PATH}")

