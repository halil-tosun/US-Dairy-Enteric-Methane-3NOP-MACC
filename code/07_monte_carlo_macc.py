"""
07_monte_carlo_macc.py -- Monte Carlo uncertainty propagation across the
four levers, producing:
  - Table5_macc_ranked.csv (overwritten): point estimate + 90% CI + rank
    probabilities per lever
  - Table5 unaffected (kept from 06)

Distribution choices:
  - Normal, using reported SE: Kebreab et al. (2022) 3-NOP x NDF
    coefficients (SEs taken directly from their Table 7, selected model
    for CH4 intensity: intercept SE=1.2, dose-coef SE=0.054, NDF-coef
    SE=0.167).
  - Triangular (min/mode/max), for parameters with only a scenario range:
    carbon price, 3-NOP net cost (DSM vs. independent/Pupo bound), fat-CH4
    response (primary vs. upper-bound), Lever D replacement-EI coefficient.
  - Ingredient price shock: +/-20% multiplicative on Lever A's feed-cost
    delta (a lighter-weight proxy for full re-optimization at each draw,
    which would be too slow at 10,000 iterations for this pass -- full
    per-draw re-optimization is a disclosed next-iteration refinement).

Carbon price is drawn ONCE per iteration and applied to all four levers
(correct correlation structure: all levers face the same market price in
a given draw), while all other parameters are drawn independently per
lever, consistent with the "independence assumed" simplification stated
in Section 4.10.
"""
import numpy as np
import pandas as pd
from _paths import (OUTPUT, MC_ITERATIONS, MC_SEED, NASEM_MEAN_NDF,
                     KEBREAB_DOSE_MEAN, KEBREAB_NDF_MEAN,
                     NOP_COST_USD_PER_COW_YEAR, NOP_COST_INDEPENDENT_USD_PER_COW_YEAR,
                     FAT_CH4_REDUCTION_PCT_PER_PCT_DM_MEAN, FAT_CH4_REDUCTION_PCT_PER_PCT_DM_UPPER,
                     FAT_MILK_FAT_YIELD_LOSS_PCT, BUTTERFAT_PRICE_USD_PER_KG, RAEE_FAT_MAX,
                     REPLACEMENT_EI_REDUCTION_PCT_PER_10PT, HEIFER_REARING_COST_USD,
                     CARBON_PRICE_LOW_USD_PER_TON, CARBON_PRICE_MID_USD_PER_TON,
                     CARBON_PRICE_HIGH_RANGE_USD_PER_TON,
                     ADOPTION_RATE, ADOPTION_RATE_RANGE, NASS_DAIRY_COW_INVENTORY_HEAD,
                     MILK, FAT)
from _calc import FPCM, MILK_REVENUE_USD_PER_DAY

rng = np.random.default_rng(MC_SEED)
N = MC_ITERATIONS
FPCM_DAYS_PER_YEAR = 365

frontier = pd.read_csv(OUTPUT / "Table4_lever_a_ndf_frontier.csv")
bau = frontier.iloc[(frontier["ndf_floor"] - NASEM_MEAN_NDF).abs().idxmin()]
opt = frontier.loc[frontier["ndf_floor"].idxmin()]
lib = pd.read_csv(__import__("_paths").DATA_PROCESSED / "ingredient_library.csv")
cottonseed = lib.loc[lib["ingredient"] == "Whole cottonseed"].iloc[0]

# Kebreab (2022) Table 7 selected-model SEs (CH4 intensity)
KEBREAB_INTERCEPT_SE = 1.2
KEBREAB_DOSE_COEF_SE = 0.054
KEBREAB_NDF_COEF_SE = 0.167

# ---- Shared draw: carbon price (once per iteration, applied to all levers) ----
carbon_price = rng.triangular(CARBON_PRICE_LOW_USD_PER_TON, CARBON_PRICE_MID_USD_PER_TON,
                               np.mean(CARBON_PRICE_HIGH_RANGE_USD_PER_TON), N)

# ================= Lever A =================
abate_ghg_kg_A = bau["ghg_intensity"] - opt["ghg_intensity"]
abate_ton_yr_A = (abate_ghg_kg_A * FPCM * FPCM_DAYS_PER_YEAR) / 1000.0
cost_delta_base_A = (opt["feed_cost_d"] - bau["feed_cost_d"]) * 365
price_shock = rng.uniform(0.8, 1.2, N)
cost_delta_A = cost_delta_base_A * price_shock
net_cost_A = cost_delta_A - abate_ton_yr_A * carbon_price
dollar_per_ton_A = net_cost_A / abate_ton_yr_A

# ================= Lever B (interaction-corrected: on Lever-A-optimized diet) =================
intercept = rng.normal(-33.0, KEBREAB_INTERCEPT_SE, N)
ndf_coef = rng.normal(0.723, KEBREAB_NDF_COEF_SE, N)
diet_ndf_pct = opt["ndf"] * 100.0
# NOTE: 3-NOP dose is fixed at the reference/mean dose used in the Kebreab
# et al. (2022) meta-analysis (70.5 mg/kg DM; see Table 3). Because the
# dose term in their equation is expressed relative to this same mean
# (Dose - 70.5), evaluating at Dose = 70.5 makes this term vanish
# identically (0), regardless of the dose-response slope coefficient's
# value. The dose coefficient's sampling uncertainty is therefore
# mathematically irrelevant to the point estimate under this study's
# fixed-dose design and is excluded from Monte Carlo sampling and from
# the tornado sensitivity analysis (Figure 5) for this reason -- not
# because it was tested and found negligible, but because its inclusion
# would carry zero information by construction. This is stated explicitly
# in Methods.
pct_change_B = intercept + ndf_coef * (diet_ndf_pct - KEBREAB_NDF_MEAN)
new_ghg_B = opt["ghg_intensity"] * (1.0 + pct_change_B / 100.0)
abate_ton_yr_B = np.clip((opt["ghg_intensity"] - new_ghg_B) * FPCM * FPCM_DAYS_PER_YEAR / 1000.0, 1e-6, None)
nop_cost = rng.triangular(NOP_COST_USD_PER_COW_YEAR[0], np.mean(NOP_COST_USD_PER_COW_YEAR),
                            NOP_COST_INDEPENDENT_USD_PER_COW_YEAR, N)
net_cost_B = nop_cost - abate_ton_yr_B * carbon_price
dollar_per_ton_B = net_cost_B / abate_ton_yr_B

# ================= Lever C =================
# CORRECTED: fat-yield-based (component price) revenue loss, not overall
# milk yield -- see 04_lever_c_fat.py header for full explanation.
baseline_fat_pct_dm = opt["fat"] * 100.0
increment_pct_dm = max(0.0, (RAEE_FAT_MAX * 100.0) - baseline_fat_pct_dm)
increment_kg_dm_day = (increment_pct_dm / 100.0) * opt["dmi"]
fat_effect = rng.triangular(FAT_CH4_REDUCTION_PCT_PER_PCT_DM_MEAN, FAT_CH4_REDUCTION_PCT_PER_PCT_DM_MEAN,
                              FAT_CH4_REDUCTION_PCT_PER_PCT_DM_UPPER, N)
pct_ch4_reduction_C = np.clip(fat_effect * increment_pct_dm, 0, 95)
new_ghg_C = opt["ghg_intensity"] * (1.0 - pct_ch4_reduction_C / 100.0)
abate_ton_yr_C = (opt["ghg_intensity"] - new_ghg_C) * FPCM * FPCM_DAYS_PER_YEAR / 1000.0
baseline_avg_price = opt["feed_cost_d"] / opt["dmi"]
ingredient_cost_delta_C = increment_kg_dm_day * (cottonseed["price_usd_per_kg_dm"] - baseline_avg_price) * 365
baseline_fat_yield_kg_d = MILK * (FAT / 100.0)
fat_yield_loss_kg_d = baseline_fat_yield_kg_d * (FAT_MILK_FAT_YIELD_LOSS_PCT / 100.0)
milk_loss_C = fat_yield_loss_kg_d * BUTTERFAT_PRICE_USD_PER_KG * 365
gross_cost_C = ingredient_cost_delta_C + milk_loss_C
net_cost_C = gross_cost_C - abate_ton_yr_C * carbon_price
dollar_per_ton_C = net_cost_C / abate_ton_yr_C

# ================= Lever D =================
ei_reduction_D = rng.triangular(REPLACEMENT_EI_REDUCTION_PCT_PER_10PT[0],
                                  np.mean(REPLACEMENT_EI_REDUCTION_PCT_PER_10PT),
                                  REPLACEMENT_EI_REDUCTION_PCT_PER_10PT[1], N)
new_ghg_D = opt["ghg_intensity"] * (1.0 - ei_reduction_D / 100.0)
abate_ton_yr_D = (opt["ghg_intensity"] - new_ghg_D) * FPCM * FPCM_DAYS_PER_YEAR / 1000.0
heifer_cost = rng.triangular(HEIFER_REARING_COST_USD[0], np.mean(HEIFER_REARING_COST_USD),
                               HEIFER_REARING_COST_USD[1], N)
cost_savings_D = 0.10 * heifer_cost  # 10-pt reduction scenario
gross_cost_D = -cost_savings_D
net_cost_D = gross_cost_D - abate_ton_yr_D * carbon_price
dollar_per_ton_D = net_cost_D / abate_ton_yr_D

# ================= Assemble, summarize, rank =================
levers = {
    "A - Dietary NDF reduction": dollar_per_ton_A,
    "B - 3-NOP (interaction-corrected)": dollar_per_ton_B,
    "C - Rumen-available fat": dollar_per_ton_C,
    "D - Replacement rate reduction": dollar_per_ton_D,
}
abatements = {
    "A - Dietary NDF reduction": abate_ton_yr_A,
    "B - 3-NOP (interaction-corrected)": abate_ton_yr_B,
    "C - Rumen-available fat": abate_ton_yr_C,
    "D - Replacement rate reduction": abate_ton_yr_D,
}

rank_matrix = np.array([levers[k] for k in levers]).argsort(axis=0).argsort(axis=0) + 1
lever_names = list(levers.keys())

rows = []
for i, name in enumerate(lever_names):
    vals = levers[name]
    ranks_i = rank_matrix[i]
    row = dict(
        lever=name,
        abatement_ton_co2e_cow_yr_median=np.median(abatements[name]),
        dollar_per_ton_median=np.median(vals),
        dollar_per_ton_p5=np.percentile(vals, 5),
        dollar_per_ton_p95=np.percentile(vals, 95),
    )
    for r in [1, 2, 3, 4]:
        row[f"pct_rank_{r}"] = 100.0 * np.mean(ranks_i == r)
    rows.append(row)

table4 = pd.DataFrame(rows).sort_values("dollar_per_ton_median").reset_index(drop=True)
table4.insert(0, "macc_rank_point_estimate", range(1, len(table4) + 1))
table4.to_csv(OUTPUT / "Table5_macc_ranked.csv", index=False)

# ================= National-scale abatement: adoption rate now stochastic =================
# Per JDS reviewer feedback: adoption rates were previously deterministic
# point estimates while biological/economic parameters were Monte Carlo
# sampled -- an internal inconsistency, since adoption rates are themselves
# expert-judgment illustrative assumptions (Section "MACC Construction and
# National-Scale Abatement Potential"). Each lever's adoption rate is now
# drawn from a triangular distribution (min/point-estimate/max from
# ADOPTION_RATE_RANGE) independently per iteration, and combined with the
# corresponding per-cow abatement draw to propagate uncertainty all the way
# through to the national MMT CO2e/yr estimate.
abatement_draws = {"A": abate_ton_yr_A, "B": abate_ton_yr_B, "C": abate_ton_yr_C, "D": abate_ton_yr_D}
national_rows = []
national_mmt_draws = {}
for code, name in zip(["A", "B", "C", "D"], lever_names):
    lo, hi = ADOPTION_RATE_RANGE[code]
    pt = ADOPTION_RATE[code]
    adoption_draw = rng.triangular(lo, pt, hi, N)
    national_ton_yr = abatement_draws[code] * NASS_DAIRY_COW_INVENTORY_HEAD * adoption_draw
    national_mmt = national_ton_yr / 1e6
    national_mmt_draws[code] = national_mmt
    national_rows.append(dict(
        lever=name, adoption_rate_point_estimate=pt,
        adoption_rate_range_low=lo, adoption_rate_range_high=hi,
        national_abatement_MMT_median=np.median(national_mmt),
        national_abatement_MMT_p5=np.percentile(national_mmt, 5),
        national_abatement_MMT_p95=np.percentile(national_mmt, 95),
    ))

national_total_mmt = sum(national_mmt_draws.values())
table6_mc = pd.DataFrame(national_rows)
table6_mc.to_csv(OUTPUT / "Table8_national_scaling_MC.csv", index=False)
print(f"\nNational total (median): {np.median(national_total_mmt):.2f} MMT CO2e/yr "
      f"(90% interval: {np.percentile(national_total_mmt, 5):.2f}-{np.percentile(national_total_mmt, 95):.2f})")
print(table6_mc.round(3).to_string(index=False))

# Save raw draws for downstream figures (Figure 4 uncertainty bands, Figure 5 tornado)
np.savez(OUTPUT / "mc_raw_draws.npz",
          carbon_price=carbon_price,
          dollar_per_ton_A=dollar_per_ton_A, dollar_per_ton_B=dollar_per_ton_B,
          dollar_per_ton_C=dollar_per_ton_C, dollar_per_ton_D=dollar_per_ton_D,
          nop_cost=nop_cost, fat_effect=fat_effect, ei_reduction_D=ei_reduction_D,
          heifer_cost=heifer_cost, price_shock=price_shock,
          intercept=intercept, ndf_coef=ndf_coef,
          national_mmt_A=national_mmt_draws["A"], national_mmt_B=national_mmt_draws["B"],
          national_mmt_C=national_mmt_draws["C"], national_mmt_D=national_mmt_draws["D"],
          national_total_mmt=national_total_mmt)
# NOTE: dose_coef intentionally NOT saved/sampled -- see explanatory comment
# above (Lever B block): its contribution is structurally zero under this
# study's fixed-dose design (Dose = 70.5 mg/kg DM = the meta-analysis mean).

pd.set_option("display.width", 160)
print(f"Monte Carlo: {N:,} iterations, seed={MC_SEED}\n")
print(table4.round(1).to_string(index=False))
print(f"\nSaved to {OUTPUT / 'Table5_macc_ranked.csv'}")
