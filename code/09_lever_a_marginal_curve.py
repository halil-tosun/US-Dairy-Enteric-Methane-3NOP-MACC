"""
09_lever_a_marginal_curve.py -- Constructs the within-Lever-A incremental
(marginal) abatement cost relationship across the full NDF floor sweep,
rather than only the two-point (BAU vs. optimized) comparison used
elsewhere. This directly addresses reviewer feedback that a MACC lever
represented by a single discrete intervention level does not demonstrate
a true marginal (incremental) cost-abatement relationship.

Moving from the highest-NDF point (37.2% floor, most similar to BAU) toward
the lowest feasible point (33.7%, NFC-constrained), the incremental $/ton
CO2e is calculated between each successive pair of adjacent frontier
points, showing that the marginal cost of each additional unit of NDF
reduction is not constant -- it is the internal structure that qualifies
Lever A's contribution to the MACC as a true marginal cost relationship,
not a single discrete before/after comparison.
"""
import numpy as np
import pandas as pd
from _paths import OUTPUT, CARBON_PRICE_MID_USD_PER_TON
from _calc import FPCM

FPCM_DAYS_PER_YEAR = 365

df = pd.read_csv(OUTPUT / "Table4_lever_a_ndf_frontier.csv")
df = df.drop_duplicates(subset="ndf", keep="first").sort_values("ndf", ascending=False).reset_index(drop=True)

rows = []
for i in range(len(df) - 1):
    hi = df.iloc[i]
    lo = df.iloc[i + 1]
    d_ghg = hi["ghg_intensity"] - lo["ghg_intensity"]
    incremental_abate_ton_yr = (d_ghg * FPCM * FPCM_DAYS_PER_YEAR) / 1000.0
    d_cost = (lo["feed_cost_d"] - hi["feed_cost_d"]) * 365
    carbon_rev = incremental_abate_ton_yr * CARBON_PRICE_MID_USD_PER_TON if incremental_abate_ton_yr > 0 else 0
    net_cost = d_cost - carbon_rev
    marginal_dollar_per_ton = net_cost / incremental_abate_ton_yr if incremental_abate_ton_yr > 1e-9 else np.nan
    rows.append(dict(
        ndf_from_pct=round(hi["ndf"] * 100, 2), ndf_to_pct=round(lo["ndf"] * 100, 2),
        incremental_abatement_ton_co2e_cow_yr=incremental_abate_ton_yr,
        incremental_feed_cost_usd_cow_yr=d_cost,
        marginal_dollar_per_ton_co2e=marginal_dollar_per_ton,
    ))

marginal_df = pd.DataFrame(rows)
marginal_df.to_csv(OUTPUT / "Table6_lever_a_marginal_curve.csv", index=False)
print("Lever A marginal (incremental) abatement cost curve, high-to-low NDF:\n")
print(marginal_df.round(2).to_string(index=False))
print(f"\nSaved to {OUTPUT / 'Table6_lever_a_marginal_curve.csv'}")
