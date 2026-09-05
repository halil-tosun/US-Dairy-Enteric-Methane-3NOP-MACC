"""
16_figure5_tornado.py -- Figure 5: tornado diagram, ranking which uncertain
parameters most influence Lever B's ($/ton CO2e) cost-effectiveness
estimate. Uses standardized-regression sensitivity on the existing Monte
Carlo draws (regression-based sensitivity analysis) rather than a separate
one-at-a-time simulation, since the paired input/output draws already
exist from 07_monte_carlo_macc.py.

Four parameters are tested (NOT five): the Kebreab et al. (2022) dose
coefficient is excluded because, under this study's fixed-dose design
(3-NOP dose = 70.5 mg/kg DM, the meta-analysis's own reference dose), its
contribution to the predicted CH4 change is structurally zero regardless
of the coefficient's value (see 07_monte_carlo_macc.py for the algebraic
explanation). Including a parameter whose effect is zero by construction,
rather than by data, would misrepresent the sensitivity analysis.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from _paths import FIGURES, OUTPUT

d = np.load(OUTPUT / "mc_raw_draws.npz")
y = d["dollar_per_ton_B"]

inputs = {
    "Carbon price ($/ton)": d["carbon_price"],
    "3-NOP cost ($/cow/yr)": d["nop_cost"],
    "Kebreab intercept": d["intercept"],
    "Kebreab NDF coefficient": d["ndf_coef"],
}

names = list(inputs.keys())
X = np.column_stack([inputs[n] for n in names])
Xz = (X - X.mean(axis=0)) / X.std(axis=0)
yz = (y - y.mean()) / y.std()

Xz1 = np.column_stack([np.ones(len(yz)), Xz])
coefs, *_ = np.linalg.lstsq(Xz1, yz, rcond=None)
std_coefs = coefs[1:]

order = np.argsort(np.abs(std_coefs))
names_sorted = [names[i] for i in order]
coefs_sorted = std_coefs[order]

fig, ax = plt.subplots(figsize=(7.5, 4.5))
colors = ["#C44E52" if c > 0 else "#4C72B0" for c in coefs_sorted]
ax.barh(names_sorted, coefs_sorted, color=colors, edgecolor="black")
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("Standardized regression coefficient\n(effect on Lever B $/ton CO2e, per SD change in input)")
ax.set_title("Tornado Diagram -- Sensitivity of Lever B (3-NOP)\nCost-Effectiveness to Uncertain Parameters")
fig.tight_layout()
out_path = FIGURES / "Figure5_tornado_diagram.png"
fig.savefig(out_path, dpi=150)
print(f"Saved {out_path}")
print("\nStandardized coefficients (ranked by |effect|):")
for n, c in zip(names_sorted[::-1], coefs_sorted[::-1]):
    print(f"  {n}: {c:+.3f}")
