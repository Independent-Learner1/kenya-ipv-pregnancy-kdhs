"""Shared configuration and helpers."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_SAV = Path(os.environ.get("KDHS_SAV", ROOT / "data" / "raw" / "KEIR8CFL.SAV"))
PROCESSED = ROOT / "data" / "processed"
GEO = ROOT / "data" / "geo"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
MAPS = ROOT / "outputs" / "maps"
for p in (PROCESSED, GEO, TABLES, FIGURES, MAPS):
    p.mkdir(parents=True, exist_ok=True)

# Orange sequential palette used throughout
ORANGES = ["#FFF5EB", "#FEE6CE", "#FDD0A2", "#FDAE6B", "#FD8D3C", "#E6550D", "#A63603"]

OUTCOMES = {
    "ANC_adequate": "4+ antenatal visits",
    "ANC_early": "ANC in first trimester",
    "Facility_delivery": "Facility delivery",
    "PNC_48h": "Postnatal check within 48h",
    "Child_alive": "Child alive",
}

# DHS county label -> geoBoundaries shapeName
NAME_FIX = {"Tharaka-Nithi": "Tharaka"}
