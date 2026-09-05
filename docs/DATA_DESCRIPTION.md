# DATA_DESCRIPTION

## Overview

This study does not analyze a pre-existing observational dataset. It
computes every table and figure from (1) a small ingredient-composition
library and (2) a set of literature-cited constants (animal parameters,
carbon-price scenarios, lever-effect coefficients, and adoption-rate
assumptions), each documented with an inline citation directly in
`code/_paths.py`. This design choice maximizes computational
transparency: every intermediate number, from a single ingredient's
price-per-kg-DM to the final national abatement estimate, can be traced
to a specific line of code and a specific cited source.

There is no separate `data/raw/` folder in this package (unlike some
observational-data reproducibility packages) because there is no raw
external dataset requiring a transformation step: the ingredient
library below is used directly, as-is, and every other empirical input
is a single cited number rather than a tabular dataset.

---

## `data/processed/ingredient_library.csv`

The composition and price of every feed ingredient used across the four
levers.

| Column | Description |
|---|---|
| `ingredient` | Ingredient name |
| `dm_pct` | Dry matter, % as-fed |
| `ndf_pct_dm` | Neutral detergent fiber, % of DM |
| `adf_pct_dm` | Acid detergent fiber, % of DM |
| `cp_pct_dm` | Crude protein, % of DM |
| `fat_pct_dm` | Ether extract (fat), % of DM |
| `nel_mcal_kg_dm` | Net energy for lactation, Mcal/kg DM |
| `price_usd_per_kg_dm` | Price, USD per kg dry matter |
| `role` | `forage` or `concentrate` (Levers A, B); `fat_source_C` (Lever C only -- whole cottonseed and tallow, rumen-available/unprotected fat sources) |

### Composition and price provenance

Composition values for the five primary Lever A/B ingredients (alfalfa
haylage, corn silage, grass hay, corn grain, soybean meal) follow
representative published NASEM (2021) feed-library values. Prices
reflect national-average 2026 vintages from USDA NASS Agricultural
Prices and USDA WASDE. Whole cottonseed and tallow (Lever C-only fat
sources) follow standard published composition references for these
ingredients; unprotected/rumen-available sources only (calcium-soap and
other bypass/rumen-protected fats are excluded by mechanism -- see
`docs/CODEBOOK.md`).

All prices are **national averages** as of 2026, not region- or
farm-specific. The manuscript's Discussion and this package's
`REPRODUCIBILITY_CHECKLIST.md` both flag this explicitly: results
should be treated as illustrative of a directionally robust phenomenon
rather than as precise, farm-specific estimates.

---

## Literature-Cited Constants (`code/_paths.py`)

Every non-ingredient-library empirical input to this study is a single
cited constant rather than a tabular dataset, documented inline in
`code/_paths.py` with its literature source. The table below summarizes
each; full bibliographic details for every source are provided in the
accompanying manuscript's Literature Cited section.

| Constant(s) | Value | Source |
|---|---|---|
| Animal parameters (BW, milk yield, fat, protein) | 650 kg; 38.0 kg/d; 3.8%; 3.1% | Representative mid-lactation Holstein cow |
| Milk price | $46.96/100 kg | US all-milk price, May 2026 (USDA ERS, 2026) |
| Methane gross energy value | 55.65 MJ/kg CH4 | Brouwer, 1965 |
| GWP100 (methane) | 27.9 kg CO2e/kg CH4 | IPCC AR6, 2021 |
| Rumen health constraints (forage NDF floor, total NDF floor, NFC ceiling) | 19%, 25%, 40% DM | NRC, 2001; NASEM, 2021; Ohio State University Extension, 1999 |
| Rumen-available fat ceiling (Lever C) | 5.5% DM | Honan et al., 2021 |
| BAU dietary NDF (empirical population mean) | 34.1% DM | NASEM, 2021 |
| 3-NOP efficacy equation (Lever B) | See `docs/CODEBOOK.md` | Kebreab et al., 2022 |
| 3-NOP cost | $93-105/cow/yr (manufacturer-linked); $128.32/cow/yr (independent) | See manuscript Materials and Methods, Lever B |
| Fat-methane response coefficient (Lever C) | 3.77%/pct-DM (primary); 19.5%/pct-DM (upper bound) | de Ondarza et al., 2024; Hristov et al., 2022 |
| Milk-fat production penalty (Lever C) | -7.8% (fat %); -6.0% (fat yield, kg/d) | de Ondarza et al., 2024 |
| Butterfat component price | $3.5107/kg ($1.5921/lb) | USDA AMS, 2026 (Advanced Butterfat Pricing Factor, January 2026) |
| Replacement-emission-intensity coefficient (Lever D) | 2.7-5.0% per 10-pt reduction | Chen et al., 2026 (Denmark); Sommerseth et al., 2024 (Norway) -- no U.S.-specific coefficient identified |
| Heifer-rearing cost (Lever D) | $1,594-$1,919/heifer | Hawkins et al., 2020; corroborated by Heinrichs et al., 2013 |
| Baseline replacement rate | ~31% | USDA APHIS NAHMS, 2018 (Northeastern U.S. average annual cull rate, 31.4%) |
| Carbon price scenarios (low/mid/high) | $6.34; $30.00; $45-60/ton | Ecosystem Marketplace, 2025; Agri-Pulse, 2024 (Athian transaction); general premium/ICVCM market (disclosed as not livestock-specific) |
| U.S. dairy cow inventory | 9.65 million head | USDA NASS, 2026 (Cattle report, released 24 July 2026) |
| Lever-specific adoption-rate assumptions | 25-60% (point estimates); +/-10 pts (uncertainty range) | Illustrative, following USDA/ICF (2023)'s own expert-judgment methodology; not survey-derived |
| Feed-cost accounting-scope reconciliation | ~65% of whole-farm feed expenditure is lactating-cow ration | Zoller, 2019 |
| Carbon-credit registry methodologies | Verra VM0041/VM0042; ACR AMS-III.BK; Gold Standard | Ruden et al., 2025 |

---

## `output/*.csv` (Generated, Not Raw Input)

All nine tables and the two intermediate lever-results files in
`output/` are **generated** by the pipeline, not raw data; see
`docs/CODEBOOK.md` for the script-to-output correspondence. They are
committed to this repository (not `.gitignore`d) so the package is
immediately inspectable without first running the pipeline, but running
`code/run_all.py` regenerates every one of them from the inputs
documented above.

---

## External Validation Benchmark Data (Table 2)

Table 2 of the manuscript (an external benchmark comparison of the
underlying dietary-optimization framework used to construct Lever A)
draws on benchmark data and results from a companion analysis by the
same research program, which has not yet been submitted for
publication and is therefore not independently archived in this
repository. The relevant benchmark comparison values are reported in
full directly in the manuscript's Table 2, rather than by reference to
an external, not-yet-public data source.

---

## Data Access and Terms of Use

- USDA NASS, USDA WASDE, USDA ERS, USDA AMS, and USDA APHIS NAHMS data
  are publicly available at no cost and require no special access
  permissions.
- NASEM (2021) benchmark figures are drawn from a copyrighted book;
  only the specific summary values used as model constants are
  reproduced here, consistent with fair use for research and
  educational purposes. Readers wishing to consult the full underlying
  reference should obtain the original publication.
- Peer-reviewed journal article coefficients (Kebreab et al., 2022; de
  Ondarza et al., 2024; Hristov et al., 2022; Chen et al., 2026;
  Sommerseth et al., 2024; Niu et al., 2018; and others) are used as
  cited model parameters (regression coefficients, effect sizes), not
  as reproduced datasets or text.
