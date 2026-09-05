"""
_calc.py -- Shared calculation functions for the MACC study.

Implements diet-level physiology/economics (shared formulas with the
companion optimization study, since these are published external science --
seethe manuscript) plus this study's own additions:
rumen health constraints (NFC ceiling), and the Kebreab et al. (2022)
3-NOP x diet-composition interaction adjustment (Lever A x B).

Not run directly; imported by numbered scripts in code/.
"""
import numpy as np
from _paths import (
    BW, MILK, FAT, PROT_MILK, NEM_COEF, NEL_PER_KG_MILK, MILK_PRICE_100KG,
    MJ_PER_KG_CH4, GWP100_CH4, PREMIX_USD_PER_COW_DAY,
    FORAGE_NDF_MIN, TOTAL_NDF_MIN, NFC_MAX, RAEE_FAT_MAX,
    KEBREAB_INTERCEPT, KEBREAB_DOSE_COEF, KEBREAB_DOSE_MEAN,
    KEBREAB_NDF_COEF, KEBREAB_NDF_MEAN,
    KEBREAB_VALID_DOSE_RANGE, KEBREAB_VALID_NDF_RANGE,
)

# ---- Fixed, diet-independent animal quantities ----
ECM = 0.327 * MILK + 12.95 * (MILK * FAT / 100) + 7.2 * (MILK * PROT_MILK / 100)
FPCM = MILK * (0.337 + 0.116 * FAT + 0.06 * PROT_MILK)
NE_MAINTENANCE = NEM_COEF * BW ** 0.75
NE_LACTATION = MILK * NEL_PER_KG_MILK
MILK_REVENUE_USD_PER_DAY = (MILK / 100.0) * MILK_PRICE_100KG


def diet_stats(x, NDF, ADF, CP, FATpct, NEL, PRICE, forage_mask=None):
    """
    Given DM-basis ingredient inclusion shares `x` (must sum to 1) and
    parallel ingredient-attribute arrays, return diet-level outcomes:
    composition, DMI, enteric methane, GHG intensity, feed cost, IOFC,
    and rumen-health constraint diagnostics (NFC, forage NDF).

    Implements:
      - DMI = (NEmaintenance + NElactation) / Diet NEL density
      - CH4 (MJ/d) = 13.3 + 0.118*NDF - 0.130*ECM + 2.20*MF - 1.71*CP
        + 0.00521*BW   [Niu et al., 2018]
      - GHG intensity (kg CO2e/kg FPCM) = CH4(kg/d) * GWP100 / FPCM
      - NFC (% DM) = 100 - NDF - CP - FATpct - ash_assumed(7.5)
        [standard NRC (2001) approximation with typical ash]
      - Feed cost ($/d) = DMI * weighted ingredient price + premix
      - IOFC = Milk revenue - Feed cost
    """
    x = np.asarray(x, dtype=float)
    ndf = float(NDF @ x)
    adf = float(ADF @ x)
    cp = float(CP @ x)
    fat = float(FATpct @ x)
    nel = float(NEL @ x)
    price = float(PRICE @ x)

    dmi = (NE_MAINTENANCE + NE_LACTATION) / nel
    feed_cost_d = dmi * price + PREMIX_USD_PER_COW_DAY

    ch4_mj = 13.3 + 0.118 * (ndf * 100) - 0.130 * ECM + 2.20 * FAT - 1.71 * PROT_MILK + 0.00521 * BW
    ch4_kg = ch4_mj / MJ_PER_KG_CH4
    ch4_co2e_kg = ch4_kg * GWP100_CH4
    ghg_intensity = ch4_co2e_kg / FPCM

    iofc_d = MILK_REVENUE_USD_PER_DAY - feed_cost_d
    milk_100kg = MILK / 100.0

    ash_assumed = 0.075  # NRC (2001) typical ash fraction
    nfc = max(0.0, 1.0 - ndf - cp - fat - ash_assumed)

    out = dict(
        ndf=ndf, adf=adf, hemicellulose=ndf - adf, cp=cp, fat=fat, nfc=nfc,
        nel=nel, dmi=dmi,
        ch4_mj_d=ch4_mj, ch4_kg_d=ch4_kg, ch4_co2e_kg_d=ch4_co2e_kg,
        ghg_intensity=ghg_intensity,
        feed_cost_d=feed_cost_d, feed_cost_100kg=feed_cost_d / milk_100kg,
        iofc_d=iofc_d, iofc_100kg=iofc_d / milk_100kg,
        milk_revenue_d=MILK_REVENUE_USD_PER_DAY,
    )
    if forage_mask is not None:
        out["forage_ndf"] = float((NDF * forage_mask) @ x)

    # Rumen health constraint diagnostics
    # Small tolerance avoids floating-point false positives at the boundary.
    _TOL = 1e-6
    out["nfc_ceiling_violated"] = nfc > NFC_MAX + _TOL
    out["total_ndf_floor_violated"] = ndf < TOTAL_NDF_MIN - _TOL
    if forage_mask is not None:
        out["forage_ndf_floor_violated"] = out["forage_ndf"] < FORAGE_NDF_MIN - _TOL

    return out


def kebreab_3nop_ch4_intensity_change_pct(dose_mg_kg_dm, diet_ndf_pct_dm, warn=True):
    """
    Kebreab et al. (2022, J. Dairy Sci. 106:927-936) meta-analysis equation
    for the interaction-adjusted 3-NOP effect on CH4 intensity (Lever A x B
    interaction; seethe manuscript).

    Change (%) in CH4 intensity = -33.0 - 0.275*(dose-70.5) + 0.723*(NDF-32.9)

    dose_mg_kg_dm : 3-NOP dose, mg/kg DM
    diet_ndf_pct_dm : dietary NDF, % DM (NOT fraction -- e.g. 32.9, not 0.329)

    Returns the relative change in CH4 intensity (%, negative = reduction).
    Raises a warning if inputs fall outside the meta-analysis's validated
    range (dose ~40-130 mg/kg DM, NDF ~26.5-43.5% DM) -- extrapolation
    outside these bounds should be flagged in Monte Carlo draws.
    """
    if warn:
        d_lo, d_hi = KEBREAB_VALID_DOSE_RANGE
        n_lo, n_hi = KEBREAB_VALID_NDF_RANGE
        if not (d_lo <= dose_mg_kg_dm <= d_hi):
            print(f"WARNING: 3-NOP dose {dose_mg_kg_dm} outside validated range {KEBREAB_VALID_DOSE_RANGE}")
        if not (n_lo <= diet_ndf_pct_dm <= n_hi):
            print(f"WARNING: diet NDF {diet_ndf_pct_dm}% outside validated range {KEBREAB_VALID_NDF_RANGE}")

    return (KEBREAB_INTERCEPT
            + KEBREAB_DOSE_COEF * (dose_mg_kg_dm - KEBREAB_DOSE_MEAN)
            + KEBREAB_NDF_COEF * (diet_ndf_pct_dm - KEBREAB_NDF_MEAN))
