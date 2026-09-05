"""
04_lever_c_fat.py -- Lever C: rumen-available fat supplementation.

Scope: rumen-available (unprotected) fat sources only (whole cottonseed
used here as the representative source) -- calcium soaps / hydrogenated
(bypass) fats are excluded by mechanism.
Fat inclusion is capped at RAEE_FAT_MAX (rumen health constraint).

Cost includes BOTH the ingredient cost delta AND a milk-fat component
revenue loss, calculated from the source meta-analysis's milk FAT YIELD
(kg fat/d) reduction (6.0%) valued at the USDA AMS butterfat component
price, NOT from overall milk yield -- unlike Lever B, where 3-NOP has no
reported production penalty.

CORRECTED (see repository history / manuscript review record): an earlier
version of this script incorrectly applied the source's 6.0% "milk fat
yield" reduction to overall MILK (kg/d) via the all-milk price, which
substantially overstated the revenue-loss component. The source abstract
(de Ondarza et al., 2024) reports reductions in milk FAT PERCENTAGE
(-7.8%) and milk FAT YIELD, kg/d (-6.0%) specifically -- not overall milk
yield, which the source does not report as significantly affected. This
version instead values the fat-yield reduction directly via a butterfat
component price, consistent with how the source's own production penalty
is actually expressed and with standard federal milk-order component
pricing.

This is a first-pass approximation (fixed increment, not a full
re-optimization of the diet); refining this into a full constrained
optimization is a next-iteration task.
"""
import numpy as np
import pandas as pd
from _paths import (OUTPUT, DATA_PROCESSED, RAEE_FAT_MAX,
                     FAT_CH4_REDUCTION_PCT_PER_PCT_DM_MEAN, FAT_CH4_REDUCTION_PCT_PER_PCT_DM_UPPER,
                     FAT_MILK_FAT_YIELD_LOSS_PCT, FAT_MILK_FAT_PCT_LOSS_PCT, BUTTERFAT_PRICE_USD_PER_KG,
                     CARBON_PRICE_LOW_USD_PER_TON, CARBON_PRICE_MID_USD_PER_TON,
                     CARBON_PRICE_HIGH_RANGE_USD_PER_TON, MILK, FAT)
from _calc import FPCM, MILK_REVENUE_USD_PER_DAY

FPCM_DAYS_PER_YEAR = 365

# Baseline milk fat yield (kg fat/d) = MILK (kg/d) x FAT (% as fraction)
BASELINE_FAT_YIELD_KG_D = MILK * (FAT / 100.0)

lib = pd.read_csv(DATA_PROCESSED / "ingredient_library.csv")
frontier = pd.read_csv(OUTPUT / "Table4_lever_a_ndf_frontier.csv")
lever_a_row = frontier.loc[frontier["ndf_floor"].idxmin()]
baseline_fat_pct_dm = lever_a_row["fat"] * 100.0
baseline_dmi = lever_a_row["dmi"]
baseline_ghg = lever_a_row["ghg_intensity"]
baseline_avg_price = lever_a_row["feed_cost_d"] / baseline_dmi  # implied $/kg DM

cottonseed = lib.loc[lib["ingredient"] == "Whole cottonseed"].iloc[0]

increment_pct_dm = (RAEE_FAT_MAX * 100.0) - baseline_fat_pct_dm
increment_pct_dm = max(0.0, increment_pct_dm)
increment_kg_dm_day = (increment_pct_dm / 100.0) * baseline_dmi

results = []
for effect_label, effect_pct_per_unit in [
    ("primary (3.77%/pt)", FAT_CH4_REDUCTION_PCT_PER_PCT_DM_MEAN),
    ("upper bound (19.5%/pt)", FAT_CH4_REDUCTION_PCT_PER_PCT_DM_UPPER),
]:
    pct_ch4_reduction = effect_pct_per_unit * increment_pct_dm
    pct_ch4_reduction = min(pct_ch4_reduction, 95.0)  # sanity cap
    new_ghg = baseline_ghg * (1.0 - pct_ch4_reduction / 100.0)
    abatement_kg_co2e_per_kg_fpcm = baseline_ghg - new_ghg
    abate_ton_yr = (abatement_kg_co2e_per_kg_fpcm * FPCM * FPCM_DAYS_PER_YEAR) / 1000.0

    ingredient_cost_delta_usd_day = increment_kg_dm_day * (cottonseed["price_usd_per_kg_dm"] - baseline_avg_price)
    ingredient_cost_delta_usd_yr = ingredient_cost_delta_usd_day * 365

    # CORRECTED: milk-fat component revenue loss, from fat YIELD (kg/d) reduction,
    # valued at the butterfat component price -- not from overall milk yield.
    fat_yield_loss_kg_day = BASELINE_FAT_YIELD_KG_D * (FAT_MILK_FAT_YIELD_LOSS_PCT / 100.0)
    milk_fat_revenue_loss_usd_yr = fat_yield_loss_kg_day * BUTTERFAT_PRICE_USD_PER_KG * 365

    gross_cost_usd_yr = ingredient_cost_delta_usd_yr + milk_fat_revenue_loss_usd_yr

    for price_label, price in [
        ("low", CARBON_PRICE_LOW_USD_PER_TON),
        ("mid", CARBON_PRICE_MID_USD_PER_TON),
        ("high", np.mean(CARBON_PRICE_HIGH_RANGE_USD_PER_TON)),
    ]:
        carbon_revenue = abate_ton_yr * price if abate_ton_yr > 0 else 0.0
        net_cost_usd_yr = gross_cost_usd_yr - carbon_revenue
        dollar_per_ton = net_cost_usd_yr / abate_ton_yr if abate_ton_yr > 0 else np.nan
        results.append(dict(
            effect_estimate=effect_label, carbon_price_scenario=price_label,
            increment_pct_dm_fat=increment_pct_dm, pct_ch4_reduction=pct_ch4_reduction,
            abatement_ton_co2e_cow_yr=abate_ton_yr,
            ingredient_cost_delta_usd_yr=ingredient_cost_delta_usd_yr,
            milk_fat_revenue_loss_usd_yr=milk_fat_revenue_loss_usd_yr,
            gross_cost_usd_yr=gross_cost_usd_yr, carbon_revenue_usd_yr=carbon_revenue,
            net_cost_usd_yr=net_cost_usd_yr, net_dollar_per_ton_co2e=dollar_per_ton,
        ))

df = pd.DataFrame(results)
out_path = OUTPUT / "LeverC_fat_results.csv"
df.to_csv(out_path, index=False)

print(f"Lever C (rumen-available fat): increment = {increment_pct_dm:.2f} pct-DM "
      f"(baseline diet fat {baseline_fat_pct_dm:.2f}% -> ceiling {RAEE_FAT_MAX*100:.1f}%)")
print(f"Baseline fat yield: {BASELINE_FAT_YIELD_KG_D:.3f} kg/d; "
      f"fat yield loss (6.0%): {BASELINE_FAT_YIELD_KG_D*0.06:.4f} kg/d\n")
print(df[["effect_estimate", "carbon_price_scenario", "pct_ch4_reduction",
           "abatement_ton_co2e_cow_yr", "milk_fat_revenue_loss_usd_yr", "net_dollar_per_ton_co2e"]].to_string(index=False))
print(f"\nSaved to {out_path}")

