"""
11_baseline_and_carbon_price_tables.py -- Table 3 (baseline animal/diet parameters)
and Table 1 (carbon price scenarios), formatted from _paths.py constants.
These are reference/documentation tables, not derived from analysis --
run last, independent of the rest of the pipeline.
"""
import pandas as pd
from _paths import (OUTPUT, BW, MILK, FAT, PROT_MILK, MILK_PRICE_100KG,
                     PREMIX_USD_PER_COW_DAY, GWP100_CH4, NASEM_MEAN_NDF,
                     FORAGE_NDF_MIN, TOTAL_NDF_MIN, NFC_MAX, RAEE_FAT_MAX,
                     CARBON_PRICE_LOW_USD_PER_TON, CARBON_PRICE_MID_USD_PER_TON,
                     CARBON_PRICE_HIGH_RANGE_USD_PER_TON)

table1 = pd.DataFrame([
    dict(parameter="Body weight (BW)", value=f"{BW:.0f} kg", source="Representative lactating Holstein cow"),
    dict(parameter="Milk yield (MILK)", value=f"{MILK:.1f} kg/d", source="Representative lactating Holstein cow"),
    dict(parameter="Milk fat (FAT)", value=f"{FAT:.1f}%", source="Representative lactating Holstein cow"),
    dict(parameter="Milk true protein (PROT_MILK)", value=f"{PROT_MILK:.1f}%", source="Representative lactating Holstein cow"),
    dict(parameter="Milk price", value=f"${MILK_PRICE_100KG:.2f}/100 kg", source="US all-milk price, May 2026 (USDA ERS, 2026)"),
    dict(parameter="Premix cost", value=f"${PREMIX_USD_PER_COW_DAY:.2f}/cow/d", source="Fixed, consistent with companion optimization study"),
    dict(parameter="Methane GWP100", value=f"{GWP100_CH4:.1f} kg CO2e/kg CH4", source="IPCC AR6 (2021)"),
    dict(parameter="BAU dietary NDF (empirical mean)", value=f"{NASEM_MEAN_NDF*100:.1f}% DM", source="NASEM (2021) published U.S. mean, 34.1 +/- 4.6% DM"),
    dict(parameter="Forage NDF floor", value=f"{FORAGE_NDF_MIN*100:.0f}% DM", source="NRC (2001) / NASEM (2021)"),
    dict(parameter="Total dietary NDF floor", value=f"{TOTAL_NDF_MIN*100:.0f}% DM", source="NRC (2001)"),
    dict(parameter="NFC ceiling", value=f"{NFC_MAX*100:.0f}% DM", source="NRC (2001) / Ohio State Extension"),
    dict(parameter="Rumen-available fat ceiling (Lever C)", value=f"{RAEE_FAT_MAX*100:.1f}% DM", source="Honan et al. (2021); biohydrogenation/MFD risk boundary"),
])
table1.to_csv(OUTPUT / "Table3_baseline_parameters.csv", index=False)

table3 = pd.DataFrame([
    dict(scenario="Low", price_usd_per_ton=f"${CARBON_PRICE_LOW_USD_PER_TON:.2f}",
         source="Ecosystem Marketplace SOVCM 2025 (primary source, verified)"),
    dict(scenario="Mid", price_usd_per_ton=f"${CARBON_PRICE_MID_USD_PER_TON:.2f}",
         source="Athian's first verified dairy carbon transaction, quoted via Agri-Pulse (primary source)"),
    dict(scenario="High", price_usd_per_ton=f"${CARBON_PRICE_HIGH_RANGE_USD_PER_TON[0]:.0f}-{CARBON_PRICE_HIGH_RANGE_USD_PER_TON[1]:.0f}",
         source="General premium/ICVCM-screened corporate market ceiling (NOT livestock-specific; disclosed limitation)"),
])
table3.to_csv(OUTPUT / "Table1_carbon_price_scenarios.csv", index=False)

print("TABLE 1 -- Baseline animal/diet parameters\n")
print(table1.to_string(index=False))
print("\n\nTABLE 3 -- Carbon price scenarios\n")
print(table3.to_string(index=False))
print(f"\nSaved to {OUTPUT / 'Table3_baseline_parameters.csv'} and Table1_carbon_price_scenarios.csv")
