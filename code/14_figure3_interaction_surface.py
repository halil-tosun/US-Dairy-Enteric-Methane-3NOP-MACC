"""
14_figure3_interaction_surface.py -- Figure 2: Lever A x B interaction
surface, per Kebreab et al. (2022): 3-NOP's CH4-intensity reduction (%)
as a joint function of dietary NDF and 3-NOP dose. Marks the study's two
reference points (NASEM-mean BAU diet and Lever-A-optimized diet) to show
where this study sits on the surface.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from _paths import FIGURES, OUTPUT, NASEM_MEAN_NDF, KEBREAB_VALID_NDF_RANGE, KEBREAB_VALID_DOSE_RANGE
from _calc import kebreab_3nop_ch4_intensity_change_pct

ndf_range = np.linspace(*KEBREAB_VALID_NDF_RANGE, 100)
dose_range = np.linspace(*KEBREAB_VALID_DOSE_RANGE, 100)
NDF_grid, DOSE_grid = np.meshgrid(ndf_range, dose_range)
Z = kebreab_3nop_ch4_intensity_change_pct(DOSE_grid, NDF_grid, warn=False)

frontier = pd.read_csv(OUTPUT / "Table4_lever_a_ndf_frontier.csv")
bau_ndf = frontier.iloc[(frontier["ndf_floor"] - NASEM_MEAN_NDF).abs().idxmin()]["ndf"] * 100
opt_ndf = frontier.loc[frontier["ndf_floor"].idxmin()]["ndf"] * 100

fig, ax = plt.subplots(figsize=(8, 6))
cs = ax.contourf(NDF_grid, DOSE_grid, Z, levels=20, cmap="RdYlGn_r")
cbar = fig.colorbar(cs, ax=ax)
cbar.set_label("Change in CH4 intensity (%) -- more negative = greater reduction")
cl = ax.contour(NDF_grid, DOSE_grid, Z, levels=[-40, -35, -30, -25], colors="black", linewidths=0.6)
ax.clabel(cl, inline=True, fontsize=7, fmt="%d%%")

ax.axvline(bau_ndf, color="blue", linestyle="--", linewidth=1)
ax.axvline(opt_ndf, color="darkgreen", linestyle="--", linewidth=1)
ax.text(bau_ndf + 0.3, 128, "BAU diet\n(NASEM mean)", color="blue", fontsize=8, va="top")
ax.text(opt_ndf - 0.3, 128, "Lever-A-\noptimized", color="darkgreen", fontsize=8, va="top", ha="right")

ax.set_xlabel("Dietary NDF (% DM)")
ax.set_ylabel("3-NOP dose (mg/kg DM)")
ax.set_title("Lever A x B Interaction Surface\n(Kebreab et al., 2022 meta-analysis equation)")
fig.tight_layout()
out_path = FIGURES / "Figure2_interaction_surface.png"
fig.savefig(out_path, dpi=150)
print(f"Saved {out_path}")
