"""Step 1. Build the analytic dataset from the KDHS 2022 Women's Individual Recode.

Input : data/raw/KEIR8CFL.SAV (or path in env var KDHS_SAV). Obtain from https://dhsprogram.com
Output: data/processed/analytic_dataset.csv  (individual level, git-ignored)
        data/processed/county_prevalence.csv  (aggregated, safe to share; made in step 4)
"""
import sys
import numpy as np
import pandas as pd
import pyreadstat
from config import RAW_SAV, PROCESSED

COLS = ["CASEID", "V044", "V222", "D005", "D118A", "V024", "V025", "V012", "V106",
        "V190", "V201", "V701", "V743A", "V467D", "V502",
        "M14$1", "M13$1", "M15$1", "M62$1", "M63$1", "M66$1", "M67$1", "B5$01"]


def build(path=RAW_SAV):
    if not path.exists():
        sys.exit(f"Dataset not found at {path}. Download KEIR8CFL.SAV from the DHS Program "
                 "and place it in data/raw/ or set KDHS_SAV.")
    df, _ = pyreadstat.read_sav(str(path), usecols=COLS)
    # Domestic violence module subsample, live birth in last 5 years
    s = df[(df["V044"] == 1) & (df["V222"] < 60)].copy()
    out = pd.DataFrame(index=s.index)
    out["caseid"] = s["CASEID"]
    out["V024"] = s["V024"].astype(int)
    out["DVweight"] = s["D005"] / 1_000_000
    out["IPV_preg"] = s["D118A"].map({0: 0, 1: 1})
    m14, m13, m15 = s["M14$1"], s["M13$1"], s["M15$1"]
    out["ANC_adequate"] = np.where(m14.between(0, 3), 0, np.where(m14.between(4, 90), 1, np.nan))
    out["ANC_early"] = np.where(m13.between(0, 3), 1, np.where(m13.between(4, 90), 0, np.nan))
    out["Facility_delivery"] = np.where(m15.between(10, 12), 0, np.where(m15.between(20, 96), 1, np.nan))
    c1 = (s["M62$1"] == 1) & (s["M63$1"] <= 201)
    c2 = (s["M66$1"] == 1) & (s["M67$1"] <= 201)
    pnc = np.where(c1 | c2, 1.0, 0.0)
    pnc[(s["M62$1"].isna() & s["M66$1"].isna()).values] = np.nan
    out["PNC_48h"] = pnc
    out["Child_alive"] = s["B5$01"].map({0: 0, 1: 1})
    out["AgeGroup"] = pd.cut(s["V012"], [14, 19, 29, 39, 49], labels=[1, 2, 3, 4]).astype(float)
    out["V106"] = s["V106"]
    out["V190"] = s["V190"]
    out["Urban"] = (s["V025"] == 1).astype(int)
    out["Parity"] = np.where(s["V201"] <= 1, 1, np.where(s["V201"] <= 3, 2, 3))
    pe = s["V701"]
    out["PartnerEduc"] = np.where(pe.isin([0, 1]), 0, np.where(pe.isin([2, 3]), 1, np.nan))
    out["Autonomy"] = np.where(s["V743A"].isin([1, 2]), 1, np.where(s["V743A"] == 4, 0, np.nan))
    out["DistanceBarrier"] = np.where(s["V467D"] == 1, 1, np.where(s["V467D"].isin([0, 2]), 0, np.nan))
    out["MaritalStatus"] = (s["V502"] == 1).astype(int)
    return out.reset_index(drop=True)


if __name__ == "__main__":
    d = build()
    d.to_csv(PROCESSED / "analytic_dataset.csv", index=False)
    w = d["DVweight"]
    print(f"Analytic n = {len(d):,}")
    print(f"Weighted IPV during pregnancy prevalence = {100*np.average(d.IPV_preg.dropna(), weights=w[d.IPV_preg.notna()]):.2f}%")
