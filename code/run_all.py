"""
run_all.py -- Runs the full MACC pipeline end-to-end, in order, from a
clean state. This is the authoritative execution order (matches the
numeric filename prefixes exactly, unlike an earlier internal draft of
this package -- see CHANGELOG.md).
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

SCRIPTS = [
    "01_ingredient_library.py",
    "02_lever_a_optimization.py",
    "03_lever_b_3nop.py",
    "04_lever_c_fat.py",
    "05_lever_d_replacement.py",
    "06_macc_construction.py",
    "07_monte_carlo_macc.py",
    "08_national_scaling.py",
    "09_lever_a_marginal_curve.py",
    "10_literature_comparison.py",
    "11_baseline_and_carbon_price_tables.py",
    "12_figure1_macc_chart.py",
    "13_figure2_mc_bands.py",
    "14_figure3_interaction_surface.py",
    "15_figure4_naive_vs_corrected.py",
    "16_figure5_tornado.py",
]

failures = []
t0 = time.time()
for script in SCRIPTS:
    print(f"\n{'=' * 70}\nRunning {script}\n{'=' * 70}")
    result = subprocess.run([sys.executable, str(HERE / script)], cwd=str(HERE))
    if result.returncode != 0:
        failures.append(script)

elapsed = time.time() - t0
print(f"\n{'#' * 70}")
if failures:
    print(f"PIPELINE FAILED. {len(failures)}/{len(SCRIPTS)} scripts failed: {failures}")
else:
    print(f"PIPELINE COMPLETE. All {len(SCRIPTS)} scripts ran successfully in {elapsed:.1f}s.")
print(f"{'#' * 70}")
sys.exit(1 if failures else 0)
