"""
08_national_scaling.py -- Table 8 (manuscript numbering): national-
scale abatement potential, using USDA NASS's July 2026 dairy cow inventory
and lever-specific adoption-feasibility assumptions, with adoption-rate
uncertainty now propagated through Monte Carlo (see 07_monte_carlo_macc.py)
rather than treated as a deterministic point estimate. This revision
responds directly to reviewer feedback that adoption assumptions -- which
are themselves expert-judgment illustrative estimates, not survey-derived
-- should not be the one deterministic input in an otherwise fully
probabilistic framework.
"""
import numpy as np
import pandas as pd
from _paths import OUTPUT, NASS_DAIRY_COW_INVENTORY_HEAD, ADOPTION_RATE, ADOPTION_RATE_RANGE

t5 = pd.read_csv(OUTPUT / "Table5_macc_ranked.csv")
t6mc = pd.read_csv(OUTPUT / "Table8_national_scaling_MC.csv")

lever_code_map = {
    "D - Replacement rate reduction": "D",
    "A - Dietary NDF reduction": "A",
    "B - 3-NOP (interaction-corrected)": "B",
    "C - Rumen-available fat": "C",
}

rows = []
for _, row in t5.iterrows():
    code = lever_code_map[row["lever"]]
    mc_row = t6mc.loc[t6mc["lever"] == row["lever"]].iloc[0]
    lo, hi = ADOPTION_RATE_RANGE[code]
    applicable_cows_point = NASS_DAIRY_COW_INVENTORY_HEAD * ADOPTION_RATE[code]
    rows.append(dict(
        lever=row["lever"],
        adoption_rate_point_pct=ADOPTION_RATE[code] * 100,
        adoption_rate_range_pct=f"{lo*100:.0f}\u2013{hi*100:.0f}",
        applicable_cows_point_estimate=applicable_cows_point,
        per_cow_abatement_ton_yr_median=row["abatement_ton_co2e_cow_yr_median"],
        national_abatement_MMT_median=mc_row["national_abatement_MMT_median"],
        national_abatement_MMT_p5=mc_row["national_abatement_MMT_p5"],
        national_abatement_MMT_p95=mc_row["national_abatement_MMT_p95"],
        dollar_per_ton_median=row["dollar_per_ton_median"],
    ))

table6 = pd.DataFrame(rows).sort_values("dollar_per_ton_median").reset_index(drop=True)
table6.to_csv(OUTPUT / "Table8_national_scaling.csv", index=False)

national_total_median = table6["national_abatement_MMT_median"].sum()
d = np.load(OUTPUT / "mc_raw_draws.npz")
total_draws = d["national_total_mmt"]
total_p5, total_p95 = np.percentile(total_draws, [5, 95])

pd.set_option("display.width", 160)
print(f"U.S. dairy cow inventory (NASS, July 2026): {NASS_DAIRY_COW_INVENTORY_HEAD:,} head\n")
print(table6.round(3).to_string(index=False))
print(f"\nTotal national abatement potential (all 4 levers, adoption-rate uncertainty propagated): "
      f"median {national_total_median:.2f} MMT CO2e/yr (90% interval: {total_p5:.2f}-{total_p95:.2f})")
print(f"\nSaved to {OUTPUT / 'Table8_national_scaling.csv'}")
