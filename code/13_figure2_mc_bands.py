"""
13_figure2_mc_bands.py -- Figure 4: Monte Carlo uncertainty bands per lever
(violin plots of the $/ton CO2e distribution across 10,000 iterations).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from _paths import FIGURES, OUTPUT

d = np.load(OUTPUT / "mc_raw_draws.npz")
data = [d["dollar_per_ton_D"], d["dollar_per_ton_A"], d["dollar_per_ton_B"], d["dollar_per_ton_C"]]
labels = ["D: Replacement\nrate", "A: Dietary\nNDF", "B: 3-NOP\n(interaction-corr.)", "C: Fat\nsupplementation"]
colors = ["#55A868", "#4C72B0", "#DD8452", "#C44E52"]

fig, ax = plt.subplots(figsize=(8, 6))
parts = ax.violinplot(data, showmedians=True, widths=0.8)
for pc, color in zip(parts["bodies"], colors):
    pc.set_facecolor(color)
    pc.set_edgecolor("black")
    pc.set_alpha(0.75)
for key in ["cbars", "cmins", "cmaxes", "cmedians"]:
    parts[key].set_color("black")

for i, vals in enumerate(data, start=1):
    p5, p95 = np.percentile(vals, [5, 95])
    ax.text(i, p95 + 40, f"P95={p95:.0f}", ha="center", fontsize=7)
    ax.text(i, p5 - 60, f"P5={p5:.0f}", ha="center", fontsize=7)

ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.set_xticks(range(1, len(labels) + 1))
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("Net cost of abatement ($/ton CO2e)")
ax.set_title("Monte Carlo Uncertainty Distributions per Lever\n(10,000 iterations)")
fig.tight_layout()
out_path = FIGURES / "Figure4_MC_uncertainty_bands.png"
fig.savefig(out_path, dpi=150)
print(f"Saved {out_path}")
