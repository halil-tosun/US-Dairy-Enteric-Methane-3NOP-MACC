"""
05_lever_d_replacement.py -- Lever D: replacement rate reduction
(herd demographic dilution).

Independent of diet composition (no interaction with Levers A-C).
System boundary note: this lever's
abatement is expressed as a % reduction applied to the lactating-cow
enteric CH4 intensity metric, as a practical approximation consistent
with how the source coefficients are reported (whole-herd EI per kg
milk) -- the rearing-phase emissions are implicitly included in that
literature coefficient, not separately modeled here. This simplification
is disclosed as a scope caveat, not hidden.

Baseline replacement rate: ~31% (northeastern U.S. benchmark, Talukder
et al. 2025 citing USDA/industry data). Scenario: 10-percentage-point
reduction (31% -> 21%).
"""
import numpy as np
import pandas as pd
from _paths import (OUTPUT, REPLACEMENT_EI_REDUCTION_PCT_PER_10PT,
                     HEIFER_REARING_COST_USD,
                     CARBON_PRICE_LOW_USD_PER_TON, CARBON_PRICE_MID_USD_PER_TON,
                     CARBON_PRICE_HIGH_RANGE_USD_PER_TON)
from _calc import FPCM

FPCM_DAYS_PER_YEAR = 365
BASELINE_REPLACEMENT_RATE = 0.31
REPLACEMENT_RATE_REDUCTION_PTS = 10.0  # scenario: 10-percentage-point reduction

frontier = pd.read_csv(OUTPUT / "Table4_lever_a_ndf_frontier.csv")
lever_a_row = frontier.loc[frontier["ndf_floor"].idxmin()]
baseline_ghg = lever_a_row["ghg_intensity"]

heifers_avoided_per_cow_yr = REPLACEMENT_RATE_REDUCTION_PTS / 100.0
heifer_cost_low, heifer_cost_high = HEIFER_REARING_COST_USD

results = []
for ei_label, ei_reduction_pct in [
    ("lower bound (2.7%/10pt)", REPLACEMENT_EI_REDUCTION_PCT_PER_10PT[0]),
    ("upper bound (5.0%/10pt)", REPLACEMENT_EI_REDUCTION_PCT_PER_10PT[1]),
]:
    new_ghg = baseline_ghg * (1.0 - ei_reduction_pct / 100.0)
    abatement_kg_co2e_per_kg_fpcm = baseline_ghg - new_ghg
    abate_ton_yr = (abatement_kg_co2e_per_kg_fpcm * FPCM * FPCM_DAYS_PER_YEAR) / 1000.0

    for cost_label, heifer_cost in [("dry-lot ($1594)", heifer_cost_low),
                                      ("confinement ($1919)", heifer_cost_high)]:
        cost_savings_usd_yr = heifers_avoided_per_cow_yr * heifer_cost
        gross_cost_usd_yr = -cost_savings_usd_yr

        for price_label, price in [
            ("low", CARBON_PRICE_LOW_USD_PER_TON),
            ("mid", CARBON_PRICE_MID_USD_PER_TON),
            ("high", np.mean(CARBON_PRICE_HIGH_RANGE_USD_PER_TON)),
        ]:
            carbon_revenue = abate_ton_yr * price if abate_ton_yr > 0 else 0.0
            net_cost_usd_yr = gross_cost_usd_yr - carbon_revenue
            dollar_per_ton = net_cost_usd_yr / abate_ton_yr if abate_ton_yr > 0 else np.nan
            results.append(dict(
                ei_reduction_estimate=ei_label, heifer_cost_scenario=cost_label,
                carbon_price_scenario=price_label,
                abatement_ton_co2e_cow_yr=abate_ton_yr,
                heifer_cost_savings_usd_yr=cost_savings_usd_yr,
                gross_cost_usd_yr=gross_cost_usd_yr, carbon_revenue_usd_yr=carbon_revenue,
                net_cost_usd_yr=net_cost_usd_yr, net_dollar_per_ton_co2e=dollar_per_ton,
            ))

df = pd.DataFrame(results)
out_path = OUTPUT / "LeverD_replacement_results.csv"
df.to_csv(out_path, index=False)

print(f"Lever D (replacement rate {BASELINE_REPLACEMENT_RATE*100:.0f}% -> "
      f"{BASELINE_REPLACEMENT_RATE*100 - REPLACEMENT_RATE_REDUCTION_PTS:.0f}%):\n")
print(df[["ei_reduction_estimate", "heifer_cost_scenario", "carbon_price_scenario",
           "abatement_ton_co2e_cow_yr", "net_dollar_per_ton_co2e"]].to_string(index=False))
print(f"\nSaved to {out_path}")
print(f"\nNote: negative $/ton values indicate a WIN-WIN (cost-saving) outcome "
      f"even before carbon revenue is counted.")
