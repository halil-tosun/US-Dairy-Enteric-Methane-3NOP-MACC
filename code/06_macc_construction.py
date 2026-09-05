"""
06_macc_construction.py -- Combine Levers A-D into a point-estimate MACC.

Produces:
  - Table5_macc_ranked.csv (an intermediate, point-estimate version;
    superseded by the Monte Carlo-based Table 5 produced by
    07_monte_carlo_macc.py, which is what the manuscript reports)
  - Table7_naive_vs_corrected.csv (manuscript Table 7): the naive-additive
    vs. interaction-corrected comparison for Lever B (the lever whose
    efficacy depends on Lever A's diet context)

This script's point estimates are a useful sanity check on the Monte
Carlo medians produced downstream (07_monte_carlo_macc.py), but the
manuscript's reported MACC (Table 5) is the Monte Carlo version, not
this script's direct output. Both are retained in this package for
transparency.
"""
import numpy as np
import pandas as pd
from _paths import OUTPUT, CARBON_PRICE_MID_USD_PER_TON

FPCM_DAYS_PER_YEAR = 365

frontier = pd.read_csv(OUTPUT / "Table4_lever_a_ndf_frontier.csv")
lever_b = pd.read_csv(OUTPUT / "LeverB_3NOP_results.csv")
lever_c = pd.read_csv(OUTPUT / "LeverC_fat_results.csv")
lever_d = pd.read_csv(OUTPUT / "LeverD_replacement_results.csv")

# ---- Lever A's own standalone cost-effectiveness (BAU -> Lever-A-optimized diet) ----
bau = frontier.iloc[(frontier["ndf_floor"] - __import__("_paths").NASEM_MEAN_NDF).abs().idxmin()]
opt = frontier.loc[frontier["ndf_floor"].idxmin()]
abate_ghg_kg = bau["ghg_intensity"] - opt["ghg_intensity"]
from _calc import FPCM
abate_ton_yr_A = (abate_ghg_kg * FPCM * FPCM_DAYS_PER_YEAR) / 1000.0
cost_delta_usd_yr_A = (opt["feed_cost_d"] - bau["feed_cost_d"]) * 365  # positive = more expensive
carbon_rev_A = abate_ton_yr_A * CARBON_PRICE_MID_USD_PER_TON if abate_ton_yr_A > 0 else 0.0
net_cost_A = cost_delta_usd_yr_A - carbon_rev_A
dollar_per_ton_A = net_cost_A / abate_ton_yr_A if abate_ton_yr_A > 0 else np.nan

# ---- Representative point estimates for B, C, D at mid carbon price ----
b_naive = lever_b.query("context == 'BAU diet (highest NDF)' and cost_source == 'DSM-linked cost' and carbon_price_scenario == 'mid'").iloc[0]
b_corrected = lever_b.query("context == 'Lever-A-optimized diet (NFC-constrained)' and cost_source == 'DSM-linked cost' and carbon_price_scenario == 'mid'").iloc[0]
c_row = lever_c.query("effect_estimate == 'primary (3.77%/pt)' and carbon_price_scenario == 'mid'").iloc[0]
d_row = lever_d.query("ei_reduction_estimate == 'upper bound (5.0%/10pt)' and heifer_cost_scenario == 'dry-lot ($1594)' and carbon_price_scenario == 'mid'").iloc[0]

# ---- Table 7: ranked MACC (interaction-corrected version) ----
table4 = pd.DataFrame([
    dict(lever="D - Replacement rate reduction", abatement_ton_co2e_cow_yr=d_row["abatement_ton_co2e_cow_yr"],
         net_dollar_per_ton_co2e=d_row["net_dollar_per_ton_co2e"]),
    dict(lever="A - Dietary NDF reduction", abatement_ton_co2e_cow_yr=abate_ton_yr_A,
         net_dollar_per_ton_co2e=dollar_per_ton_A),
    dict(lever="B - 3-NOP (on Lever-A-optimized diet, interaction-corrected)",
         abatement_ton_co2e_cow_yr=b_corrected["abatement_ton_co2e_cow_yr"],
         net_dollar_per_ton_co2e=b_corrected["net_dollar_per_ton_co2e"]),
    dict(lever="C - Rumen-available fat supplementation", abatement_ton_co2e_cow_yr=c_row["abatement_ton_co2e_cow_yr"],
         net_dollar_per_ton_co2e=c_row["net_dollar_per_ton_co2e"]),
]).sort_values("net_dollar_per_ton_co2e").reset_index(drop=True)
table4.insert(0, "macc_rank", range(1, len(table4) + 1))
table4.to_csv(OUTPUT / "Table5_macc_ranked.csv", index=False)  # manuscript Table 5 (MACC ranked)

# ---- Table 7 (manuscript numbering): naive-additive vs. interaction-corrected (Lever B) ----
pct_diff_efficacy = (b_corrected["pct_ch4_intensity_change"] - b_naive["pct_ch4_intensity_change"]) / abs(b_naive["pct_ch4_intensity_change"]) * 100
pct_diff_dollar = (b_corrected["net_dollar_per_ton_co2e"] - b_naive["net_dollar_per_ton_co2e"]) / b_naive["net_dollar_per_ton_co2e"] * 100

table5 = pd.DataFrame([dict(
    lever="B - 3-NOP",
    naive_context="Applied independently (BAU diet efficacy assumed)",
    corrected_context="Applied after Lever A (NFC-constrained optimized diet)",
    naive_pct_ch4_change=b_naive["pct_ch4_intensity_change"],
    corrected_pct_ch4_change=b_corrected["pct_ch4_intensity_change"],
    pct_difference_efficacy=pct_diff_efficacy,
    naive_dollar_per_ton=b_naive["net_dollar_per_ton_co2e"],
    corrected_dollar_per_ton=b_corrected["net_dollar_per_ton_co2e"],
    pct_difference_dollar_per_ton=pct_diff_dollar,
)])
table5.to_csv(OUTPUT / "Table7_naive_vs_corrected.csv", index=False)  # manuscript Table 7

print("=" * 70)
print("TABLE 5 (manuscript numbering) -- Ranked MACC (interaction-corrected, mid carbon price)")
print("=" * 70)
print(table4.to_string(index=False))

print("\n" + "=" * 70)
print("TABLE 4 (manuscript numbering) -- Naive-additive vs. interaction-corrected (Lever B)")
print("=" * 70)
print(table5.to_string(index=False))

print(f"\nKey finding: ignoring the Lever A x B interaction changes Lever B's "
      f"efficacy estimate by {pct_diff_efficacy:.1f}% and its cost-effectiveness "
      f"by {pct_diff_dollar:.1f}%.")
