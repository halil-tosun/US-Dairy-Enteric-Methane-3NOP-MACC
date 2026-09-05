# A Nutrition-Based Marginal Abatement Cost Curve for Enteric Methane Mitigation in U.S. Dairy Production

## Reproducibility Package

This repository contains the complete reproducibility package
accompanying a manuscript that constructs a marginal abatement cost
curve (MACC) for enteric methane mitigation in U.S. dairy production,
using a mechanistically informed, cow-level diet-optimization framework
rather than literature-derived engineering assumptions. Four candidate
mitigation levers are evaluated within a single economic and modeling
framework: dietary neutral detergent fiber (NDF) reduction (Lever A),
3-nitrooxypropanol supplementation (Lever B), rumen-available fat
supplementation (Lever C), and cow replacement-rate reduction (Lever
D). Because 3-NOP efficacy depends on dietary NDF concentration, the
interaction between Levers A and B is explicitly modeled rather than
assumed additive, using a published meta-analysis equation. Parameter
uncertainty -- including adoption-rate uncertainty in the national-scale
scaling exercise -- is propagated via 10,000-iteration Monte Carlo
simulation.

This package is intentionally organized around the *study* rather than
any single journal submission. If the manuscript title, framing, or
target journal changes during peer review, this repository and its
contents remain valid without modification.

---

## Key Finding

Cost-effectiveness ranking and abatement-potential ranking are distinct
properties of a mitigation portfolio. Dietary NDF reduction and
replacement-rate reduction are cost-saving even without carbon market
participation (median -$594/ton and -$1,372/ton CO2e, respectively),
while 3-NOP supplementation is moderately cost-positive (median
$67/ton) and rumen-available fat supplementation has the highest median
cost of the four levers ($171/ton) -- yet the two most cost-effective
levers together account for only a small share of the total illustrative
national abatement potential identified, while the two more expensive
levers account for the large majority. Explicitly testing, rather than
assuming, the interaction between dietary NDF reduction and 3-NOP
supplementation reveals a modest effect (approximately 1% change in
cost-effectiveness), attributable to the U.S. dairy population's average
diet already sitting close to its rumen-health-constrained fiber floor.

---

## Repository Overview

This repository follows open science and computational reproducibility
principles and includes:

- Complete Python source code for the full pipeline: four mitigation
  levers, MACC construction, 10,000-iteration Monte Carlo uncertainty
  propagation, national-scale scaling, and all five manuscript figures
- The ingredient composition/price library used as a model input
- All nine result tables and five figures reported in the manuscript
- Comprehensive documentation of every model equation, constant,
  distributional choice, and data source
- Software environment specifications

---

## Repository Structure

```text
US-Dairy-Enteric-Methane-MACC/
├── code/
│   ├── _paths.py                                  # shared path config + every literature-cited constant
│   ├── _calc.py                                    # shared calculation functions (ECM, FPCM)
│   ├── 01_ingredient_library.py                     # sanity check
│   ├── 02_lever_a_optimization.py                   # Lever A -- CORE ANALYSIS
│   ├── 03_lever_b_3nop.py                           # Lever B + Lever A x B interaction -- Table 7
│   ├── 04_lever_c_fat.py                            # Lever C
│   ├── 05_lever_d_replacement.py                    # Lever D
│   ├── 06_macc_construction.py                      # point-estimate MACC (sanity check)
│   ├── 07_monte_carlo_macc.py                       # Monte Carlo -- CORE UNCERTAINTY ANALYSIS -- Table 5
│   ├── 08_national_scaling.py                       # Table 8
│   ├── 09_lever_a_marginal_curve.py                 # Table 6
│   ├── 10_literature_comparison.py                  # Table 9
│   ├── 11_baseline_and_carbon_price_tables.py       # Table 3, Table 1
│   ├── 12_figure1_macc_chart.py                     # Figure 3
│   ├── 13_figure2_mc_bands.py                       # Figure 4
│   ├── 14_figure3_interaction_surface.py            # Figure 2
│   ├── 15_figure4_naive_vs_corrected.py             # Figure 1
│   ├── 16_figure5_tornado.py                        # Figure 5
│   └── run_all.py
├── data/
│   └── processed/
│       └── ingredient_library.csv
├── output/                                            # generated tables (.csv, .npz)
├── figures/                                            # generated Figures 1-5 (.png)
├── docs/
│   ├── CODEBOOK.md
│   ├── DATA_DESCRIPTION.md
│   ├── REPRODUCIBILITY_CHECKLIST.md
│   └── Replication_Guide.md
├── README.md
├── CHANGELOG.md
├── CITATION.cff
├── .zenodo.json
├── LICENSE
├── requirements.txt
├── environment.yml
└── .gitignore
```

## Documentation

- **docs/CODEBOOK.md** -- analytical workflow, every model equation,
  the Monte Carlo distributional choices, and why Lever A is
  represented both by a two-point comparison and a separate marginal
  cost curve (important -- read before extending this package)
- **docs/DATA_DESCRIPTION.md** -- data sources, provenance, and
  variable definitions for every model input
- **docs/REPRODUCIBILITY_CHECKLIST.md** -- reproducibility checklist
  and full internal consistency verification against the manuscript
- **docs/Replication_Guide.md** -- complete, step-by-step replication
  guide, including how to adapt this package to different prices,
  scenarios, or lever coefficients

## Installation

```bash
conda env create -f environment.yml
conda activate dairy-macc-repro
```

or

```bash
pip install -r requirements.txt
```

## Run

```bash
cd code
python run_all.py
```

This reproduces the complete analytical workflow: all four mitigation
levers, the point-estimate and Monte Carlo MACC constructions,
national-scale abatement scaling, the literature comparison, the
baseline parameter tables, and all five figures.

Expected runtime: approximately 10-15 seconds on a standard laptop. The
Lever A diet-optimization component is fully **deterministic** (no
randomness); the Monte Carlo uncertainty-propagation component
(`07_monte_carlo_macc.py` and everything downstream of it) uses a fixed
random seed (`MC_SEED = 42` in `_paths.py`), so every run produces
identical output (see `docs/CODEBOOK.md`, "Determinism").

## Script-to-Output Correspondence

| Script | Produces |
|---|---|
| `01_ingredient_library.py` | Ingredient library sanity check (console only) |
| `02_lever_a_optimization.py` | Table 4 (Lever A diet composition and outcomes) -- **core analysis** |
| `03_lever_b_3nop.py` | Table 7 (naive-additive vs. interaction-corrected 3-NOP estimates) |
| `04_lever_c_fat.py` | Lever C results (feeds into Table 5) |
| `05_lever_d_replacement.py` | Lever D results (feeds into Table 5) |
| `06_macc_construction.py` | Point-estimate MACC (sanity check; superseded by script 07) |
| `07_monte_carlo_macc.py` | Table 5 (Monte Carlo-based MACC ranking) -- **core uncertainty analysis** |
| `08_national_scaling.py` | Table 8 (national-scale abatement potential) |
| `09_lever_a_marginal_curve.py` | Table 6 (Lever A's within-lever marginal cost curve) |
| `10_literature_comparison.py` | Table 9 (comparison with USDA/ICF, 2023, and Dutreuil et al., 2014) |
| `11_baseline_and_carbon_price_tables.py` | Table 3 (baseline parameters); Table 1 (carbon price scenarios) |
| `12_figure1_macc_chart.py` | Figure 3 (stepped MACC chart) |
| `13_figure2_mc_bands.py` | Figure 4 (Monte Carlo uncertainty distributions per lever) |
| `14_figure3_interaction_surface.py` | Figure 2 (3-NOP efficacy as a function of NDF and dose) |
| `15_figure4_naive_vs_corrected.py` | Figure 1 (naive-additive vs. interaction-corrected 3-NOP) |
| `16_figure5_tornado.py` | Figure 5 (tornado diagram, Lever B sensitivity) |

Note: the manuscript's Table 2 (an external benchmark comparison of the
underlying dietary-optimization framework) is not generated by this
pipeline -- see `docs/DATA_DESCRIPTION.md`, "External Validation
Benchmark Data."

## A Note on Script Numbering

This package's scripts are numbered 01-16 in clean execution order,
matching the manuscript's table and figure numbering as closely as
possible. An earlier internal working version of this pipeline numbered
scripts by authorship/creation order rather than execution order; see
`CHANGELOG.md` for the full account of this renaming (a documentation
change only -- no calculation logic was altered).

## A Note on Lever A's Two Representations

Lever A (dietary NDF reduction) appears in this package in two forms,
for a substantive methodological reason, not redundancy: Table 4 and
Figure 3 report Lever A using only the two policy-relevant endpoints
(the empirically defined business-as-usual diet and the NFC-constrained
optimum), while Table 6 (`09_lever_a_marginal_curve.py`) reports the
full **within-lever marginal cost structure** across the entire NDF
sweep. This is explained in full in `docs/CODEBOOK.md`, "Why a Separate
Marginal-Curve Script?" -- **read this before extending or reusing the
optimization code.**

## Citation

Please cite both the published article (once available) and this
archived repository. Citation metadata are provided in `CITATION.cff`
and `.zenodo.json`.

## License

MIT License (code and derived/processed data in this repository). See
`docs/DATA_DESCRIPTION.md` for the provenance of every underlying price,
composition, and coefficient figure, and their own terms of use.

## Contact

**Halil Tosun**
Department of Animal Science, School of Agricultural and Food Sciences,
ADA University, Baku, Azerbaijan
ORCID: https://orcid.org/0000-0001-5117-0390
Email: halilibrahimtosun@gmail.com

**Ermias Kebreab**
Department of Animal Science, University of California, Davis,
Davis, CA 95616, USA
ORCID: https://orcid.org/0000-0002-0833-1352
Email: ekebreab@ucdavis.edu

**Victor E. Cabrera**
Department of Animal and Dairy Sciences, University of Wisconsin-Madison,
Madison, WI, USA
ORCID: https://orcid.org/0000-0003-1739-7457
Email: vcabrera@wisc.edu

**Zenodo DOI:** [DOI will be added once assigned upon archival release]

**Version:** 1.0.0
