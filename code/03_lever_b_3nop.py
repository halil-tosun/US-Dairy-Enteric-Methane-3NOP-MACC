"""
03_lever_b_3nop.py -- Lever B: 3-NOP (Bovaer) supplementation.

Computes the interaction-adjusted CH4-intensity reduction (Kebreab et al.,
2022) and $/ton CO2e cost-effectiveness of adding 3-NOP on top of two diet
contexts: (a) the business-as-usual (BAU) diet (highest NDF floor point from
Lever A's frontier, representing a conventional ration), and (b) the
Lever-A-optimized diet (lowest feasible NDF floor point, after the NFC
ceiling binds). This directly demonstrates the Lever A x B interaction
: 3-NOP is MORE effective on the
lower-NDF diet, so stacking A then B is not equivalent to summing their
independently-estimated effects (the naive-additive fallacy).

Cost: NOP_COST_USD_PER_COW_YEAR (DSM-linked estimate) with
NOP_COST_INDEPENDENT_USD_PER_COW_YEAR (Pupo et al.) as an independent
sensitivity bound -- see COI note,the manuscript.
"""
import numpy as np
import pandas as pd
from _paths import (OUTPUT, KEBREAB_DOSE_MEAN, NOP_COST_USD_PER_COW_YEAR,
                     NOP_COST_INDEPENDENT_USD_PER_COW_YEAR,
                     CARBON_PRICE_LOW_USD_PER_TON, CARBON_PRICE_MID_USD_PER_TON,
                     CARBON_PRICE_HIGH_RANGE_USD_PER_TON, NASEM_MEAN_NDF)
from _calc import kebreab_3nop_ch4_intensity_change_pct, FPCM

FPCM_DAYS_PER_YEAR = 365

frontier = pd.read_csv(OUTPUT / "Table4_lever_a_ndf_frontier.csv")

bau_row = frontier.iloc[(frontier["ndf_floor"] - NASEM_MEAN_NDF).abs().idxmin()]  # NASEM empirical mean = BAU
lever_a_row = frontier.loc[frontier["ndf_floor"].idxmin()]  # lowest feasible = Lever-A-optimized


def apply_3nop(diet_row, dose=KEBREAB_DOSE_MEAN):
    ndf_pct_dm = diet_row["ndf"] * 100.0
    pct_change = kebreab_3nop_ch4_intensity_change_pct(dose, ndf_pct_dm, warn=False)
    baseline_ghg = diet_row["ghg_intensity"]  # kg CO2e / kg FPCM
    new_ghg = baseline_ghg * (1.0 + pct_change / 100.0)
    abatement_kg_co2e_per_kg_fpcm = baseline_ghg - new_ghg
    abatement_ton_co2e_per_cow_year = (abatement_kg_co2e_per_kg_fpcm * FPCM * FPCM_DAYS_PER_YEAR) / 1000.0
    return pct_change, new_ghg, abatement_ton_co2e_per_cow_year


results = []
for context_name, diet_row in [("BAU diet (highest NDF)", bau_row),
                                 ("Lever-A-optimized diet (NFC-constrained)", lever_a_row)]:
    pct_change, new_ghg, abate_ton_yr = apply_3nop(diet_row)
    for cost_label, cost_usd_yr in [
        ("DSM-linked cost", np.mean(NOP_COST_USD_PER_COW_YEAR)),
        ("Independent (Pupo) cost", NOP_COST_INDEPENDENT_USD_PER_COW_YEAR),  # already per-cow basis
    ]:
        for price_label, price in [
            ("low", CARBON_PRICE_LOW_USD_PER_TON),
            ("mid", CARBON_PRICE_MID_USD_PER_TON),
            ("high", np.mean(CARBON_PRICE_HIGH_RANGE_USD_PER_TON)),
        ]:
            carbon_revenue = abate_ton_yr * price
            net_cost_usd_yr = cost_usd_yr - carbon_revenue
            dollar_per_ton = net_cost_usd_yr / abate_ton_yr if abate_ton_yr > 0 else np.nan
            results.append(dict(
                context=context_name, cost_source=cost_label, carbon_price_scenario=price_label,
                pct_ch4_intensity_change=pct_change, abatement_ton_co2e_cow_yr=abate_ton_yr,
                gross_cost_usd_cow_yr=cost_usd_yr, carbon_revenue_usd_cow_yr=carbon_revenue,
                net_cost_usd_cow_yr=net_cost_usd_yr, net_dollar_per_ton_co2e=dollar_per_ton,
            ))

df = pd.DataFrame(results)
out_path = OUTPUT / "LeverB_3NOP_results.csv"
df.to_csv(out_path, index=False)

print("Lever B (3-NOP) results:\n")
print(df[["context", "cost_source", "carbon_price_scenario", "pct_ch4_intensity_change",
           "abatement_ton_co2e_cow_yr", "net_dollar_per_ton_co2e"]].to_string(index=False))
print(f"\nSaved to {out_path}")

# Interaction demonstration: how much does 3-NOP efficacy change between contexts?
bau_pct = results[0]["pct_ch4_intensity_change"]
lvA_pct = results[6]["pct_ch4_intensity_change"]  # first entry of second context block
print(f"\nLever A x B interaction check: 3-NOP effect is {bau_pct:.2f}% on BAU diet "
      f"vs. {lvA_pct:.2f}% on Lever-A-optimized diet.")
