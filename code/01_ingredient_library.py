"""
01_ingredient_library.py -- Load and validate the ingredient library.

Prints a sanity-check summary. Not a results-generating script; run first
to confirm the library loads correctly before optimization scripts (02+).
"""
import numpy as np
import pandas as pd
from _paths import DATA_PROCESSED, NFC_MAX, FORAGE_NDF_MIN

lib = pd.read_csv(DATA_PROCESSED / "ingredient_library.csv")

print("Ingredient library loaded:", len(lib), "ingredients")
print(lib[["ingredient", "ndf_pct_dm", "fat_pct_dm", "price_usd_per_kg_dm", "role"]].to_string(index=False))

# Sanity check: NDF, CP, fat, ash should not exceed 100% DM for any ingredient
for _, row in lib.iterrows():
    total = row["ndf_pct_dm"] + row["cp_pct_dm"] + row["fat_pct_dm"]
    assert total <= 100.0, f"{row['ingredient']}: NDF+CP+fat = {total}% exceeds 100% DM"

print("\nSanity check passed: no ingredient exceeds 100% DM in NDF+CP+fat.")
print(f"\nRumen health ceilings in effect: NFC max = {NFC_MAX*100:.0f}% DM, "
      f"forage NDF min = {FORAGE_NDF_MIN*100:.0f}% DM")
