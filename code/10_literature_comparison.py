"""
10_literature_comparison.py -- Table 9 (manuscript numbering):
literature comparison, using REAL extracted values from USDA/ICF (2023)
Chapter 4 (Feed Management, dairy lipids scenario -- the closest USDA/ICF
analog to our Lever C) and Dutreuil et al. (2014).

USDA/ICF (2023) dairy lipid scenario, extracted directly from the report
(Table 3, 2, 5, 6, 13 of their Chapter 4):
  - CH4 reduction: 9.0% (Eugene et al., 2008, single meta-analysis)
  - Feed efficiency gain: 6.4% (same source) -- assumed to translate
    DIRECTLY into feed cost savings, with NO milk yield or milk fat
    penalty modeled.
  - Net recurring cost: -$6.26 to $58.44/head/year across 12 USDA regions
    (unweighted mean = $6.44/head/year)
  - Implied $/ton CO2e = $6.44 / 0.34 tCO2e abated = ~$18.94/ton

This diverges sharply (~28x) from this study's Lever C estimate. The
mechanistic reason is disclosed, not hidden: USDA/ICF's single-study basis
(Eugene et al., 2008) assumes a feed-efficiency GAIN with no production
penalty, whereas this study's Lever C uses a much larger, more recent
(2024) 35-study meta-analysis documenting real milk yield (-6.0%) and
milk fat (-7.8%) losses with rumen-available fat supplementation -- a
revenue cost that dominates the net cost calculation and that USDA/ICF's
model does not include.
"""
import pandas as pd
from _paths import OUTPUT

t4 = pd.read_csv(OUTPUT / "Table5_macc_ranked.csv")
our_lever_c = t4.loc[t4["lever"] == "C - Rumen-available fat"].iloc[0]

usda_icf_dairy_lipid_dollar_per_ton = 6.44 / 0.34

rows = [
    dict(
        comparison_axis="Data vintage / basis",
        this_study="2024 meta-analysis, 35 studies (rumen-available fat)",
        usda_icf_2023="Eugene et al. (2008), single meta-analysis",
        dutreuil_2014="IFSM whole-farm simulation, 3 Wisconsin farms (2014)",
    ),
    dict(
        comparison_axis="CH4 reduction assumption",
        this_study="3.77% per pct-DM fat (primary); 19.5% (upper bound)",
        usda_icf_2023="9.0% (fixed, for ~2 pct-DM fat increment)",
        dutreuil_2014="Not applicable (feeding/manure strategies, not fat supplementation)",
    ),
    dict(
        comparison_axis="Production-effect assumption",
        this_study="Milk fat percentage -7.8%, milk fat yield -6.0% (revenue LOSS via butterfat component value)",
        usda_icf_2023="Feed efficiency +6.4% (revenue GAIN, no yield penalty)",
        dutreuil_2014="Milk production held constant in primary scenario",
    ),
    dict(
        comparison_axis="Net $/ton CO2e (dairy fat/lipid lever)",
        this_study=f"${our_lever_c['dollar_per_ton_median']:.0f}/ton (median, mid carbon price)",
        usda_icf_2023=f"${usda_icf_dairy_lipid_dollar_per_ton:.0f}/ton (implied, unweighted 12-region mean)",
        dutreuil_2014="Not reported in this format (% GHG change + $ net return by scenario)",
    ),
    dict(
        comparison_axis="3-NOP (Lever B) coverage",
        this_study="Included -- Kebreab et al. (2022) interaction-adjusted",
        usda_icf_2023="EXPLICITLY EXCLUDED -- \"due to lack of market readiness and FDA approval\" (2023)",
        dutreuil_2014="Not applicable -- predates 3-NOP commercial availability",
    ),
    dict(
        comparison_axis="Lever interaction modeled",
        this_study="Yes -- Lever A x B quantitatively (Kebreab equation)",
        usda_icf_2023="No -- practice-by-practice; explicitly noted as own limitation",
        dutreuil_2014="No",
    ),
]

table6 = pd.DataFrame(rows)
table6.to_csv(OUTPUT / "Table9_literature_comparison.csv", index=False)

pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 60)
print(table6.to_string(index=False))
print(f"\nSaved to {OUTPUT / 'Table9_literature_comparison.csv'}")
print(f"\nKey divergence: this study's Lever C estimate is "
      f"{our_lever_c['dollar_per_ton_median'] / usda_icf_dairy_lipid_dollar_per_ton:.1f}x "
      f"higher than USDA/ICF's implied estimate for the closest analogous practice.")
