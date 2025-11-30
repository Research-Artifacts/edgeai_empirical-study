import pandas as pd
import matplotlib.pyplot as plt

# === CONFIGURAÇÕES ===
PALETTE = ["#3b5b92", "#6c8ebf", "#8aa8d6", "#b7c7ea",
           "#777777", "#a0a0a0", "#c8c8c8", "#e0e0e0"]

# Caminho do arquivo CSV
csv_path = "../dataset/[Empirical Study]-sa_doc(70).csv"

# === LEITURA DO CSV ===
df = pd.read_csv(csv_path)

# Filtra colunas de interesse (as que representam os tipos de documento/views)
# Exemplo genérico — ajuste se os nomes das colunas forem diferentes
view_cols = [
    "arch_overview", "diagrams", "adrs", "context",
    "deployment", "quality_attrs", "interface", "evaluation", "stakeholders"
]

# Conta quantos repositórios têm cada tipo de view/documento
view_counts = df[view_cols].notna().sum().sort_values(ascending=True)

# === PLOT ===
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(view_counts.index, view_counts.values, color=PALETTE[:len(view_counts)])

# Adiciona rótulos numéricos
for bar in bars:
    width = bar.get_width()
    ax.text(width + 0.3, bar.get_y() + bar.get_height()/2,
            str(int(width)), va='center', fontsize=10)

# === ESTILO ===
ax.set_xlabel("Number of documents found", fontsize=15)
ax.set_ylabel("View type", fontsize=15)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig("../results/figs/views_per_repo_histogram.png", dpi=300, bbox_inches="tight")
plt.show()
