# CHANGELOG

All notable changes to this reproducibility package will be documented
in this file.

The format is inspired by *Keep a Changelog* and follows semantic
versioning where appropriate.

---

## Version 1.0.0 (Initial Public Release)

### Added
- Complete Python source code for the full analytical pipeline: Lever A
  (dietary NDF reduction, constrained nonlinear optimization), Lever B
  (3-nitrooxypropanol, with an explicitly modeled Lever A x B
  interaction), Lever C (rumen-available fat supplementation), Lever D
  (replacement-rate reduction), MACC construction, 10,000-iteration
  Monte Carlo uncertainty propagation, national-scale scaling, and all
  five figures.
- Ingredient composition/price library
  (`data/processed/ingredient_library.csv`).
- All nine result tables (`output/Table1-9*` and lever-results CSVs)
  and all five figures (`figures/Figure1-5*.png`), numbered to match
  the accompanying manuscript exactly.
- README.md with repository overview and usage instructions.
- CODEBOOK.md describing the analytical workflow, every model equation,
  the Monte Carlo distributional choices, and the script-to-output
  correspondence.
- DATA_DESCRIPTION.md documenting the ingredient library and every
  literature-cited model constant, with full provenance.
- REPRODUCIBILITY_CHECKLIST.md, including a full internal-consistency
  verification of every reported statistic against the manuscript.
- Replication_Guide.md with complete, step-by-step replication and
  extension instructions.
- CITATION.cff and .zenodo.json for software citation and Zenodo
  metadata.
- LICENSE, requirements.txt, environment.yml, .gitignore.

### Reproducibility
- One-command Python workflow via `run_all.py` (16 scripts,
  approximately 8-15 seconds total runtime).
- Every statistic reported in the accompanying manuscript's Tables 1-9
  and Figures 1-5 was independently regenerated from a clean state and
  confirmed to match exactly prior to release; see
  `docs/REPRODUCIBILITY_CHECKLIST.md`, "Internal Consistency Checks."
- Fixed random seed (`MC_SEED = 42`) for the stochastic Monte Carlo
  component; the Lever A diet-optimization component is fully
  deterministic (no randomness).
- All monetary figures (milk price, feed cost, income over feed cost)
  are reported in metric units (US dollars per 100 kg), matching the
  manuscript throughout; see `docs/DATA_DESCRIPTION.md`.
- Repository organized to remain valid regardless of eventual journal,
  manuscript title, or submission outcome.

### Notes
- **A documented analytical correction (Lever C).** During development,
  this study's Lever C (rumen-available fat supplementation) economics
  were corrected: the source meta-analysis (de Ondarza et al., 2024)
  reports a reduction in milk fat *yield*, kg/d (-6.0%) -- not overall
  milk yield, which the source does not report as significantly
  affected. The milk-fat revenue loss is valued here via the butterfat
  component price applied to the fat-yield reduction, not via the
  all-milk price applied to overall milk yield. This is disclosed for
  full scientific transparency; see `docs/CODEBOOK.md`, "A Corrected
  Modeling Choice," and `docs/REPRODUCIBILITY_CHECKLIST.md`, "Known,
  Documented Analytical Corrections," for the full account.
- Script filenames (`01_` through `16_`) follow execution/dependency
  order, a deliberately different numbering system from the
  manuscript's table/figure order; see `docs/CODEBOOK.md`.
- The Zenodo DOI will be added once assigned upon archival release. The
  manuscript's own DOI (once published) will be added to this file and
  to the citation metadata files at that time.
