"""Run the full pipeline: python run_all.py  (set KDHS_SAV or place KEIR8CFL.SAV in data/raw/)"""
import subprocess, sys
from pathlib import Path
src = Path(__file__).parent / "src"
for s in ["01_build_analytic_dataset.py", "02_descriptive_and_bivariate.py",
          "03_logistic_models.py", "04_geospatial_choropleth.py"]:
    print(f"\n=== {s} ===")
    subprocess.run([sys.executable, str(src / s)], check=True, cwd=src)
