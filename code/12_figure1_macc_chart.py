"""
12_figure1_macc_chart.py -- Figure 3: classic stepped MACC chart.

X-axis: national-scale cumulative abatement potential (MMT CO2e/yr), from
Table 8 (manuscript numbering; USDA NASS July 2026 dairy cow inventory x
lever-specific adoption
feasibility).
Y-axis: net $/ton CO2e (median, from Monte Carlo).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from _paths import OUTPUT, FIGURES

t4 = pd.read_csv(OUTPUT / "Table8_national_scaling.csv").sort_values("dollar_per_ton_median").reset_index(drop=True)

short_names = {
    "D - Replacement rate reduction": "D: Replacement\nrate",
    "A - Dietary NDF reduction": "A: Dietary\nNDF",
    "B - 3-NOP (interaction-corrected)": "B: 3-NOP\n(interaction-corr.)",
    "C - Rumen-available fat": "C: Fat\nsupplementation",
}
colors = {"A - Dietary NDF reduction": "#4C72B0", "B - 3-NOP (interaction-corrected)": "#DD8452",
          "C - Rumen-available fat": "#C44E52", "D - Replacement rate reduction": "#55A868"}

fig, ax = plt.subplots(figsize=(9, 6))
x_cursor = 0.0
lefts, widths, heights, labels, bar_colors = [], [], [], [], []
for _, row in t4.iterrows():
    width = row["national_abatement_MMT_median"]
    height = row["dollar_per_ton_median"]
    lefts.append(x_cursor)
    widths.append(width)
    heights.append(height)
    labels.append(short_names[row["lever"]])
    bar_colors.append(colors[row["lever"]])
    x_cursor += width

ax.bar(lefts, heights, width=widths, align="edge", color=bar_colors, edgecolor="black", linewidth=0.8)
label_offsets = {"A: Dietary\nNDF": 220, "D: Replacement\nrate": 0,
                  "B: 3-NOP\n(interaction-corr.)": 0, "C: Fat\nsupplementation": 0}
for left, width, height, label in zip(lefts, widths, heights, labels):
    extra = label_offsets.get(label, 0)
    va = "bottom" if height >= 0 else "top"
    ax.text(left + width / 2, height + (15 + extra if height >= 0 else -(15 + extra)),
            label, ha="center", va=va, fontsize=8.5)

ax.axhline(0, color="black", linewidth=1)
ax.set_xlabel("Cumulative national abatement potential (MMT CO2e/yr)\n"
              "(USDA NASS July 2026 dairy cow inventory x lever-specific adoption assumption)")
ax.set_ylabel("Net cost of abatement ($/ton CO2e)")
ax.set_title("Marginal Abatement Cost Curve -- Enteric Methane Mitigation\nU.S. Dairy Production (national scale; median Monte Carlo estimates)")
ax.set_xlim(0, x_cursor * 1.05)
ymin, ymax = min(heights), max(heights)
yr = ymax - ymin
ax.set_ylim(ymin - 0.15 * yr, ymax + 0.15 * yr)
fig.tight_layout()
out_path = FIGURES / "Figure3_MACC_stepped_chart.png"
fig.savefig(out_path, dpi=150)
print(f"Saved {out_path}")
