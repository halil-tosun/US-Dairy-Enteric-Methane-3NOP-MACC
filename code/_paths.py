"""
_paths.py -- Shared path configuration and constants for this repository.

A Nutrition-Based Marginal Abatement Cost Curve for Enteric Methane
Mitigation in U.S. Dairy Production (Tosun, Kebreab & Cabrera).

This is an INDEPENDENT repository. Physiological/animal constants are
shared with the companion optimization study (Niu et al. 2018 methane
equation, NASEM 2021 energy partitioning) because they are published
external science, not this project's own results. Ingredient library,
prices, and NDF range are independently re-parameterized for this
multi-lever framework (see docs/DATA_DESCRIPTION.md).

Not run directly. Imported by every numbered script in code/.
"""
from pathlib import Path

# ---- Repository-relative paths ----
ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUT = ROOT / "output"
FIGURES = ROOT / "figures"

for p in (DATA_PROCESSED, OUTPUT, FIGURES):
    p.mkdir(parents=True, exist_ok=True)

# ---- Fixed animal / production assumptions ----
# Shared with companion optimization study (published physiological science,
# not a reuse of this study's own results).
BW = 650.0                   # body weight, kg
MILK = 38.0                  # milk yield, kg/d
FAT = 3.8                    # milk fat, %
PROT_MILK = 3.1               # milk true protein, %
NEM_COEF = 0.080              # NEmaintenance coefficient, Mcal/kg BW^0.75
NEL_PER_KG_MILK = 0.74        # NEl per kg milk, Mcal/kg
MILK_PRICE_100KG = 46.96      # USD/100 kg, US all-milk price, May 2026 (USDA ERS, 2026);
                                # converted from $21.30/cwt (1 cwt = 45.359237 kg) via
                                # x (100/45.359237) = 2.204623
PREMIX_USD_PER_COW_DAY = 0.55

# ---- Methane / GWP constants ----
MJ_PER_KG_CH4 = 55.65          # gross energy value of methane (Brouwer, 1965)
GWP100_CH4 = 27.9              # 100-yr GWP, kg CO2e/kg CH4 (IPCC AR6, 2021)

# ---- Rumen health constraints (shared across Levers A and C) ----
FORAGE_NDF_MIN = 0.19            # NRC (2001)/NASEM (2021) minimum forage NDF, % DM
TOTAL_NDF_MIN = 0.25             # NRC (2001) minimum total dietary NDF, % DM
NFC_MAX = 0.40                   # NRC (2001)/Ohio State Extension NFC ceiling, % DM
                                  # (pairs with 27-32% NDF guidance; source verified)
RAEE_FAT_MAX = 0.055              # Lever C: rumen-available fat ceiling, % DM
                                  # (biohydrogenation intermediates / MFD risk boundary)

# NOTE (honesty flag -- Section 4.3 of planning doc): physically effective NDF
# (peNDF) / particle size is explicitly OUT OF SCOPE for this ingredient-
# composition-level model (no Penn State Shaker Box data available). This is
# disclosed in Methods as a standard simplification for this model class,
# consistent with NASEM (2021)'s own guidance that paNDF is for diet
# evaluation, not formulation.

# ---- Optimization bounds (independently re-specified for this study;
# consistent in spirit with the companion optimization study's Methods,
# not copied verbatim) ----
CP_MIN, CP_MAX = 0.160, 0.185  # NASEM (2021) dairy CP recommendation range for
                                 # high-producing lactating cows.
FORAGE_MIN, FORAGE_MAX = 0.35, 0.65
SINGLE_FORAGE_CAP = 0.45
CORNGRAIN_CAP = 0.40
SBM_CAP = 0.20

# ---- Lever A: Dietary NDF reduction ----
# Independently re-parameterized ingredient library / price vintage for this
# study (NOT copied from the companion optimization study's Table 3).
# See docs/DATA_DESCRIPTION.md for full provenance.
NDF_FLOOR_POINTS = [0.28, 0.30, 0.32, 0.34, 0.341, 0.35, 0.36, 0.37, 0.372]
NASEM_MEAN_NDF = 0.341   # NASEM (2021) published U.S. lactating-cow mean, 34.1 +/- 4.6% DM
                          # -- used as the empirically-grounded BAU reference point
                          # (NOT the top of our own sweep range) for Lever A/B baseline.

# ---- Lever B: 3-NOP (Bovaer) ----
# Kebreab, Bannink, Pressman, Walker, Karagiannis, van Gastelen, Dijkstra
# (2022). J. Dairy Sci. 106:927-936. doi:10.3168/jds.2022-22211
# CH4 intensity change (%) = -33.0 - 0.275*(dose-70.5) + 0.723*(NDF-32.9)
# dose in mg/kg DM; NDF in % DM. Valid range: dose ~40-130 mg/kg DM,
# NDF ~26.5-43.5% DM. COI note: this source is DSM-funded (Bovaer
# manufacturer); triangulated
# against an independent/skeptical cost estimate (Pupo et al.) in
# sensitivity analysis.
KEBREAB_INTERCEPT = -33.0
KEBREAB_DOSE_COEF = -0.275
KEBREAB_DOSE_MEAN = 70.5      # mg/kg DM
KEBREAB_NDF_COEF = 0.723
KEBREAB_NDF_MEAN = 32.9       # % DM
KEBREAB_VALID_DOSE_RANGE = (40.0, 130.0)   # mg/kg DM
KEBREAB_VALID_NDF_RANGE = (26.5, 43.5)     # % DM

NOP_COST_USD_PER_COW_YEAR = (93.0, 105.0)         # DSM-linked estimate, 300-cow herd
NOP_COST_INDEPENDENT_USD_PER_COW_YEAR = 128.32    # Pupo et al., 1000-cow herd basis
                                                    # (independent/skeptical estimate,
                                                    # used as sensitivity bound)

# ---- Lever C: Rumen-available fat supplementation ----
# Scope explicitly limited to rumen-available (unprotected) fat sources;
# calcium soaps / hydrogenated (bypass) fats excluded by mechanism (see
# the manuscript's Materials and Methods).
FAT_CH4_REDUCTION_PCT_PER_PCT_DM_MEAN = 3.77    # primary estimate (35-study meta-analysis)
FAT_CH4_REDUCTION_PCT_PER_PCT_DM_UPPER = 19.5   # sensitivity upper bound (Hristov et al. 2022,
                                                  # multi-species)
FAT_MILK_FAT_PCT_LOSS_PCT = 7.8   # relative milk FAT PERCENTAGE reduction
                                    # (de Ondarza et al., 2024, verified)
FAT_MILK_FAT_YIELD_LOSS_PCT = 6.0  # relative milk FAT YIELD (kg fat/d) reduction
                                     # -- CORRECTED: the source abstract reports
                                     # "milk fat percentage and yield (kg/d)" reduced
                                     # by 7.8% and 6.0% respectively; both figures
                                     # pertain to milk FAT, not overall milk yield.
                                     # An earlier version of this analysis incorrectly
                                     # applied the 6.0% figure to overall MILK (kg/d),
                                     # which the source abstract does not report as
                                     # significantly reduced. This was caught via
                                     # independent reviewer cross-checking against the
                                     # primary source and corrected.
BUTTERFAT_PRICE_USD_PER_KG = 3.5107  # USDA AMS Advanced Butterfat Pricing Factor,
                                       # January 2026: $1.5921/lb (verified primary
                                       # source) / 0.453592 kg per lb.

# ---- Lever D: Replacement rate reduction (herd demographic dilution) ----
# Scope note: this lever's emission accounting includes rearing-phase
# (heifer) enteric + manure emissions, which differs from the lactating-cow-
# only boundary of Levers A-C .
# Triangulated range (geographic transferability flagged -- see Section 4.7):
REPLACEMENT_EI_REDUCTION_PCT_PER_10PT = (2.7, 5.0)  # % EI reduction per 10-pt
                                                       # replacement-rate reduction,
                                                       # triangulated from two
                                                       # independent European herd-
                                                       # simulation studies: Chen et al.
                                                       # (2026, Denmark) and Sommerseth
                                                       # et al. (2024, Norway). No
                                                       # U.S.-specific coefficient was
                                                       # identified in the literature.
HEIFER_REARING_COST_USD = (1594.0, 1919.0)  # dry-lot to confinement range,
                                              # Hawkins et al. (2020), birth-to-calving

# ---- Carbon price scenarios ----
CARBON_PRICE_LOW_USD_PER_TON = 6.34    # Ecosystem Marketplace SOVCM 2025 (primary source)
CARBON_PRICE_MID_USD_PER_TON = 30.0    # Athian's first verified dairy transaction,
                                         # quoted via Agri-Pulse (primary source)
CARBON_PRICE_HIGH_RANGE_USD_PER_TON = (45.0, 60.0)  # general premium/ICVCM-screened
                                                       # corporate market ceiling --
                                                       # NOT livestock-specific;
                                                       # used only as a conservative
                                                       # upper bound (flagged in Methods)

# ---- Monte Carlo specification ----
MC_ITERATIONS = 10_000
MC_SEED = 42

# ---- National scaling ----
# USDA NASS Cattle report, July 1, 2026 (most recent available; released
# July 24, 2026): U.S. milk cow inventory = 9.65 million head.
NASS_DAIRY_COW_INVENTORY_HEAD = 9_650_000

# Lever-specific adoption-rate assumptions. Following USDA/ICF (2023)'s own
# methodology of expert-judgment-based adoption rates (their published
# digester/practice adoption assumptions range 10-50%), these are illustrative
# assumptions reflecting relative ease of adoption -- disclosed throughout as
# expert-judgment estimates, not survey-derived rates (hence the uncertainty
# range below, propagated through Monte Carlo simulation).
ADOPTION_RATE = {
    "A": 0.60,  # dietary reformulation -- low-cost, no new infrastructure
    "B": 0.25,  # 3-NOP -- new technology, feeding-system/verification barriers
    "C": 0.40,  # fat supplementation -- already common practice on many farms
    "D": 0.30,  # reproductive/replacement management -- requires genetic/breeding investment
}

# Adoption-rate UNCERTAINTY range (+/- 10 percentage points around the point
# estimate above, bounded to [0.05, 0.90]), used to sample a triangular
# distribution in the Monte Carlo national-scaling calculation (Section on
# "National-Scale Abatement Potential"). This range reflects that the point
# estimates above are expert-judgment illustrative assumptions, not
# survey-derived rates, and are therefore themselves a source of uncertainty
# rather than fixed inputs -- addressed per JDS reviewer feedback that
# treating adoption deterministically while propagating biological/economic
# uncertainty via Monte Carlo was internally inconsistent.
ADOPTION_RATE_RANGE = {
    "A": (0.50, 0.70),
    "B": (0.15, 0.35),
    "C": (0.30, 0.50),
    "D": (0.20, 0.40),
}
