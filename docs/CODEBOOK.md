# CODEBOOK

## Analytical Workflow

This package evaluates four candidate enteric-methane mitigation levers
for U.S. dairy production within a single economic and modeling
framework, propagates parameter uncertainty via Monte Carlo simulation,
and benchmarks the results against the only directly comparable
published U.S. government marginal abatement cost curve (MACC).

| Script | Description | Produces |
|---|---|---|
| `_paths.py` | Shared path configuration and every fixed model constant (animal assumptions, rumen-health constraints, carbon-price scenarios, lever-effect coefficients, adoption-rate assumptions), each with an inline literature citation; not run directly | -- |
| `_calc.py` | Shared calculation module: ECM, FPCM; not run directly | -- |
| `01_ingredient_library.py` | Loads and sanity-checks the ingredient library | (console check only) |
| `02_lever_a_optimization.py` | **Lever A core analysis.** For each dietary NDF floor point (28.0-37.2% DM), solves the constrained nonlinear optimization (SLSQP) for the IOFC-maximizing (feed-cost-minimizing at fixed milk output) diet | Table 4 |
| `03_lever_b_3nop.py` | **Lever B.** Applies the meta-analysis equation of Kebreab et al. (2022) at the reference dose (70.5 mg/kg DM) to both the BAU diet and the Lever-A-optimized diet, quantifying the Lever A x B interaction | Table 7 |
| `04_lever_c_fat.py` | **Lever C.** Rumen-available fat supplementation; values the milk-fat-yield revenue loss via the butterfat component price (not the all-milk price -- see "A Corrected Modeling Choice" below) | `LeverC_fat_results.csv` |
| `05_lever_d_replacement.py` | **Lever D.** Replacement-rate reduction; deterministic point estimates at two heifer-housing-cost scenarios | `LeverD_replacement_results.csv` |
| `06_macc_construction.py` | Assembles point estimates for all four levers into a single ranked MACC table (a quick sanity check; its `Table5_macc_ranked.csv` output is intentionally overwritten by script 07 -- see note below) | `Table5_macc_ranked.csv` (transient) |
| `07_monte_carlo_macc.py` | **Core uncertainty analysis.** 10,000-iteration Monte Carlo simulation propagating parameter uncertainty (biological, economic, and adoption-rate) into each lever's net $/ton CO2e and national-scale abatement estimate; overwrites `Table5_macc_ranked.csv` with the Monte Carlo median, 90% interval, and rank probabilities -- **this is the Table 5 the manuscript reports** | Table 5; `mc_raw_draws.npz` |
| `08_national_scaling.py` | Combines Monte Carlo abatement draws with the U.S. dairy cow inventory and lever-specific adoption-rate distributions | Table 8 |
| `09_lever_a_marginal_curve.py` | Constructs Lever A's within-lever incremental (marginal) abatement-cost relationship across the full NDF sweep (see "Why a Separate Marginal-Curve Script?" below) | Table 6 |
| `10_literature_comparison.py` | Benchmarks Lever C directly against USDA/ICF (2023)'s Feed Management chapter and Dutreuil et al. (2014) | Table 9 |
| `11_baseline_and_carbon_price_tables.py` | Assembles the baseline animal/diet parameter table and the carbon-price-scenario table | Table 3; Table 1 |
| `12_figure1_macc_chart.py` | Generates Figure 3 (stepped MACC chart) from Table 8 | Figure 3 |
| `13_figure2_mc_bands.py` | Generates Figure 4 (Monte Carlo uncertainty distributions per lever) | Figure 4 |
| `14_figure3_interaction_surface.py` | Generates Figure 2 (3-NOP efficacy as a joint function of dietary NDF and dose) | Figure 2 |
| `15_figure4_naive_vs_corrected.py` | Generates Figure 1 (naive-additive vs. interaction-corrected 3-NOP estimates) | Figure 1 |
| `16_figure5_tornado.py` | Generates Figure 5 (tornado diagram, Lever B sensitivity) | Figure 5 |
| `run_all.py` | Runs scripts 01-16 in the order above | All tables and figures |

## Why a Separate Marginal-Curve Script? (Table 6)

Script `02_lever_a_optimization.py` solves the full NDF-floor sweep
(28.0-37.2% DM) but Results and Figure 3 report Lever A's abatement
using only the two policy-relevant endpoints (the empirically defined
business-as-usual diet, 34.1% NDF, and the NFC-constrained optimum,
33.7% NDF). Script `09_lever_a_marginal_curve.py` instead computes the
**incremental** $/ton CO2e between each successive pair of adjacent
points on the same frontier, moving from the highest-NDF point toward
the NFC-constrained floor. This within-lever marginal structure --
ranging from -$1,702/ton for the first increment to -$592/ton for the
final increment, as the NFC ceiling constraint becomes binding -- is
what qualifies Lever A's contribution to the overall MACC as a marginal
cost-abatement relationship in the conventional sense, since Levers B,
C, and D are each represented by a single discrete intervention level
rather than a continuous sweep.

## A Corrected Modeling Choice (Lever C)

`04_lever_c_fat.py` values the milk-fat revenue loss associated with
rumen-available fat supplementation using the **milk fat yield** (kg
fat/d) reduction reported by the source meta-analysis (de Ondarza et
al., 2024; -6.0%), valued at the USDA AMS butterfat component price --
not the overall milk yield, which the source does not report as
significantly affected. An earlier internal version of this analysis
had applied the source's 6.0% milk-fat-yield figure to overall milk
revenue via the all-milk price, which substantially overstated this
lever's revenue-loss component (the corrected calculation reduces
Lever C's gross cost from a milk-revenue-loss component of $390.79/cow/yr
to $111.02/cow/yr). This was identified via independent cross-checking
of this study's source-attribution against the source meta-analysis's
own reported endpoints prior to release. See `docs/REPRODUCIBILITY_CHECKLIST.md`,
"Known, Documented Analytical Corrections," for the full account.

## Core Equations

| Quantity | Equation | Source |
|---|---|---|
| Energy-corrected milk (ECM) | ECM = 0.327xMilk + 12.95x(Milk x Fat/100) + 7.2x(Milk x Protein/100) | Tyrrell and Reid, 1965 |
| Fat- and protein-corrected milk (FPCM) | FPCM = Milk x (0.337 + 0.116xFat% + 0.06xProtein%) | Sjaunja et al., 1990; reconsidered by Hall, 2023 |
| Net energy for maintenance | NEm (Mcal/d) = 0.080xBW^0.75 | NASEM, 2021 |
| Net energy for lactation | NEl (Mcal/d) = Milk x 0.74 | NASEM, 2021 |
| Dry matter intake (dilution of maintenance) | DMI = (NEm + NEl) / Diet NEL density | Bauman and Currie, 1980 |
| Enteric methane (Levers A, C) | CH4 (MJ/d) = 13.3 + 0.118xNDF - 0.130xECM + 2.20xFAT - 1.71xPROT + 0.00521xBW | Niu et al., 2018 |
| Methane mass | CH4 (kg/d) = CH4(MJ/d) / 55.65 | Brouwer, 1965 (gross energy value of methane) |
| GHG intensity | kg CO2e/kg FPCM = CH4(kg/d) x 27.9 / FPCM | IPCC AR6 (2021), GWP100 |
| 3-NOP efficacy (Lever B) | dCH4 intensity (%) = -33.0 - 0.275x(Dose-70.5) + 0.723x(NDF-32.9) | Kebreab et al., 2022 |
| Fat-methane response (Lever C) | % CH4 reduction = k x dFat (percentage points DM) | de Ondarza et al., 2024 (primary); Hristov et al., 2022 (upper bound) |
| Feed cost | $/d = DMI x Sum(x_i x Price_i) + Premix | This study |
| Income over feed cost | IOFC = Milk revenue - Feed cost | This study |

Full bibliographic details, including DOIs where independently
confirmed, are provided in the accompanying manuscript's Literature
Cited section and in `docs/DATA_DESCRIPTION.md`.

## Optimization Method (Lever A)

Solved with SciPy's SLSQP (Sequential Least-Squares Quadratic
Programming; Kraft, 1988) implementation (`scipy.optimize.minimize`,
`method="SLSQP"`), convergence tolerance 1e-10, maximum 500 iterations.
Solver convergence was confirmed at each NDF floor point evaluated by
independently re-verifying feasibility against every constraint.

## Monte Carlo Uncertainty Propagation (`07_monte_carlo_macc.py`)

10,000 iterations, fixed random seed (`MC_SEED = 42` in `_paths.py`)
for reproducibility. Distributional choices follow the nature of the
underlying evidence:

- **Normal distributions** for parameters with a reported standard
  error: the Kebreab et al. (2022) regression intercept (SE = 1.2) and
  NDF coefficient (SE = 0.167); heifer-rearing cost.
- **Triangular distributions** (minimum/mode/maximum from the
  low/primary/high literature values) for parameters supported only by
  a bounded literature range without a formal variance estimate: carbon
  price, 3-NOP net cost, the fat-methane response coefficient, the
  Lever D replacement-emission-intensity coefficient, and (in the
  national-scaling exercise, `08_national_scaling.py`) each lever's
  adoption rate (+/-10 percentage points around its point estimate).
- **Not sampled**: the Kebreab et al. (2022) dose coefficient. Because
  3-NOP dose is held fixed at 70.5 mg/kg DM (the reference dose about
  which the source equation's dose term is centered), this
  coefficient's contribution to the predicted CH4 change is exactly
  zero regardless of its value, so its sampling uncertainty carries no
  information under this study's fixed-dose design. This is a
  structural feature of the model, not an oversight; it is also why
  the tornado sensitivity analysis (Figure 5) tests four parameters,
  not five.
- Carbon price is drawn **once per iteration** and applied identically
  across all four levers within that iteration (all levers face the
  same prevailing market price in a given draw); all other parameters
  are sampled independently across levers.

For the high carbon-price scenario specifically, because it is itself
defined as a range ($45-60/ton) rather than a single value, the
triangular distribution uses minimum = $6.34/ton (low scenario),
mode = $30.00/ton (mid scenario), and maximum = $52.50/ton (the
midpoint of the $45-60/ton high-scenario range) -- lower than the high
scenario's own upper bound ($60/ton) used for the deterministic point
estimates reported in Results (Table 1). See `_paths.py`, and the
manuscript's Materials and Methods ("Uncertainty Propagation"), for the
full statement of this distinction.

## Determinism

This package combines a **deterministic** optimization component
(Lever A, `02_lever_a_optimization.py`; no randomness) with a
**stochastic** Monte Carlo component (`07_monte_carlo_macc.py` and
everything downstream of it) that consumes NumPy's random number
generator via a fixed seed (`MC_SEED = 42`). Given the same input
constants and the same NumPy/SciPy versions, every script in this
package produces bit-for-bit identical output on every run and on every
machine.
