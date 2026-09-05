"""
15_figure4_naive_vs_corrected.py -- Figure 1: naive-additive vs.
interaction-corrected comparison for Lever B (3-NOP), the study's central
methodological demonstration.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from _paths import FIGURES, OUTPUT

t5 = pd.read_csv(OUTPUT / "Table7_naive_vs_corrected.csv").iloc[0]

fig, axes = plt.subplots(1, 2, figsize=(9.5, 5))

ax = axes[0]
vals = [t5["naive_pct_ch4_change"], t5["corrected_pct_ch4_change"]]
bars = ax.bar(["Naive-additive\n(independent estimate)", "Interaction-corrected\n(applied after Lever A)"],
               vals, color=["#B0B0B0", "#DD8452"], edgecolor="black")
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v - 1, f"{v:.1f}%", ha="center", va="top", fontsize=10)
ax.set_ylabel("Change in CH4 intensity (%)")
ax.set_title("3-NOP efficacy estimate")
ax.axhline(0, color="black", linewidth=0.8)

ax = axes[1]
vals2 = [t5["naive_dollar_per_ton"], t5["corrected_dollar_per_ton"]]
bars2 = ax.bar(["Naive-additive", "Interaction-corrected"], vals2, color=["#B0B0B0", "#DD8452"], edgecolor="black")
for b, v in zip(bars2, vals2):
    ax.text(b.get_x() + b.get_width() / 2, v + 1, f"${v:.1f}/ton", ha="center", va="bottom", fontsize=10)
ax.set_ylabel("Net $/ton CO2e (mid carbon price)")
ax.set_title("3-NOP cost-effectiveness")

fig.suptitle(f"Ignoring the Lever A x B interaction changes the efficacy estimate by "
             f"{t5['pct_difference_efficacy']:.1f}% and cost-effectiveness by "
             f"{t5['pct_difference_dollar_per_ton']:.1f}%", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.94])
out_path = FIGURES / "Figure1_naive_vs_corrected.png"
fig.savefig(out_path, dpi=150)
print(f"Saved {out_path}")
