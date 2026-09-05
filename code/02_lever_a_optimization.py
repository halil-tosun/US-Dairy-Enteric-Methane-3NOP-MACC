"""
02_lever_a_optimization.py -- Lever A: dietary NDF reduction, IOFC-maximizing
diet at each NDF floor point, subject to rumen health constraints
(forage NDF floor AND NFC ceiling -- the latter is this study's own
addition beyond the companion optimization study).

Uses the primary 5-ingredient set (2 forages + corn grain + soybean meal +
one additional forage), excluding the Lever-C-only fat sources (whole
cottonseed, tallow) and byproduct feeds (DDGS, soybean hulls) to keep
Lever A's baseline comparable in composition to a conventional ration.
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from _paths import (DATA_PROCESSED, OUTPUT, NDF_FLOOR_POINTS,
                     FORAGE_NDF_MIN, NFC_MAX, CP_MIN, CP_MAX,
                     FORAGE_MIN, FORAGE_MAX, SINGLE_FORAGE_CAP, CORNGRAIN_CAP, SBM_CAP)
from _calc import diet_stats

lib = pd.read_csv(DATA_PROCESSED / "ingredient_library.csv")
lib5 = lib[lib["ingredient"].isin(
    ["Alfalfa haylage", "Corn silage", "Grass hay", "Corn grain ground", "Soybean meal 48pct CP"]
)].reset_index(drop=True)
names = lib5["ingredient"].values
n = len(lib5)

NDF = lib5["ndf_pct_dm"].values / 100.0
ADF = lib5["adf_pct_dm"].values / 100.0
CP = lib5["cp_pct_dm"].values / 100.0
FATpct = lib5["fat_pct_dm"].values / 100.0
NEL = lib5["nel_mcal_kg_dm"].values
PRICE = lib5["price_usd_per_kg_dm"].values
FORAGE_MASK = np.isin(names, ["Alfalfa haylage", "Corn silage", "Grass hay"]).astype(float)
idx = {nm: i for i, nm in enumerate(names)}


def neg_iofc(x, ndf_floor):
    stats = diet_stats(x, NDF, ADF, CP, FATpct, NEL, PRICE, forage_mask=FORAGE_MASK)
    return -stats["iofc_100kg"]


def solve_for_ndf_floor(ndf_floor):
    x0 = np.full(n, 1.0 / n)
    bounds = [(0.0, 1.0)] * n
    cons = [
        {"type": "eq", "fun": lambda x: np.sum(x) - 1.0},
        {"type": "ineq", "fun": lambda x: (NDF @ x) - ndf_floor},          # total NDF >= floor
        {"type": "ineq", "fun": lambda x: (FORAGE_MASK * NDF) @ x - FORAGE_NDF_MIN},  # forage NDF floor
        {"type": "ineq", "fun": lambda x: NFC_MAX - (1.0 - (NDF @ x) - (CP @ x) - (FATpct @ x) - 0.075)},  # NFC ceiling
        {"type": "ineq", "fun": lambda x: (CP @ x) - CP_MIN},
        {"type": "ineq", "fun": lambda x: CP_MAX - (CP @ x)},
        {"type": "ineq", "fun": lambda x: FORAGE_MASK @ x - FORAGE_MIN},
        {"type": "ineq", "fun": lambda x: FORAGE_MAX - FORAGE_MASK @ x},
        {"type": "ineq", "fun": lambda x: CORNGRAIN_CAP - x[idx["Corn grain ground"]]},
        {"type": "ineq", "fun": lambda x: SBM_CAP - x[idx["Soybean meal 48pct CP"]]},
    ]
    for forage_name in ["Alfalfa haylage", "Corn silage", "Grass hay"]:
        cons.append({"type": "ineq", "fun": (lambda x, i=idx[forage_name]: SINGLE_FORAGE_CAP - x[i])})

    res = minimize(neg_iofc, x0, args=(ndf_floor,), method="SLSQP", bounds=bounds,
                    constraints=cons, options={"maxiter": 500, "ftol": 1e-10})
    if not res.success:
        print(f"WARNING: solver did not converge for NDF floor {ndf_floor}: {res.message}")
    return res


rows = []
for floor in NDF_FLOOR_POINTS:
    res = solve_for_ndf_floor(floor)
    x = res.x
    stats = diet_stats(x, NDF, ADF, CP, FATpct, NEL, PRICE, forage_mask=FORAGE_MASK)
    row = {"ndf_floor": floor, **stats}
    for i, nm in enumerate(names):
        row[f"share_{nm}"] = x[i]
    rows.append(row)

df = pd.DataFrame(rows)
out_path = OUTPUT / "Table4_lever_a_ndf_frontier.csv"
df.to_csv(out_path, index=False)

print(f"Lever A optimization complete: {len(df)} NDF floor points solved.")
print(df[["ndf_floor", "ndf", "nfc", "ghg_intensity", "iofc_100kg",
          "nfc_ceiling_violated", "forage_ndf_floor_violated"]].to_string(index=False))
print(f"\nSaved to {out_path}")
