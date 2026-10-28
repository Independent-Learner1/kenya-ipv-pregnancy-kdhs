"""Step 2. Weighted prevalence of IPV in pregnancy, patterning, and bivariate tests."""
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from config import PROCESSED, TABLES, OUTCOMES

LABELS = {
    "AgeGroup": {1: "15-19", 2: "20-29", 3: "30-39", 4: "40-49"},
    "V106": {0: "No education", 1: "Primary", 2: "Secondary", 3: "Higher"},
    "V190": {1: "Poorest", 2: "Poorer", 3: "Middle", 4: "Richer", 5: "Richest"},
    "Urban": {0: "Rural", 1: "Urban"},
    "Parity": {1: "1 birth", 2: "2-3 births", 3: "4+ births"},
    "PartnerEduc": {0: "None/primary", 1: "Secondary/higher"},
}


def wprev(x, w):
    m = x.notna()
    return 100 * np.average(x[m], weights=w[m]) if m.any() else np.nan


def main():
    d = pd.read_csv(PROCESSED / "analytic_dataset.csv")
    w = d["DVweight"]
    rows = []
    for var, lab in LABELS.items():
        for k, name in lab.items():
            g = d[d[var] == k]
            rows.append({"Variable": var, "Category": name, "n": len(g),
                         "Weighted IPV in pregnancy (%)": round(wprev(g.IPV_preg, g.DVweight), 2)})
    rows.append({"Variable": "Overall", "Category": "All", "n": len(d),
                 "Weighted IPV in pregnancy (%)": round(wprev(d.IPV_preg, w), 2)})
    pd.DataFrame(rows).to_csv(TABLES / "table1_ipv_by_characteristic.csv", index=False)

    # Bivariate: outcome by IPV (weighted % and Rao-Scott-free chi-square on weighted counts)
    out = []
    for o, name in OUTCOMES.items():
        m = d[o].notna() & d.IPV_preg.notna()
        g = d[m]
        p1 = wprev(g[g.IPV_preg == 1][o], g[g.IPV_preg == 1].DVweight)
        p0 = wprev(g[g.IPV_preg == 0][o], g[g.IPV_preg == 0].DVweight)
        tab = pd.crosstab(g.IPV_preg, g[o], values=g.DVweight, aggfunc="sum").fillna(0)
        chi, p, _, _ = chi2_contingency(tab.values)
        out.append({"Outcome": name, "n": len(g), "% among IPV": round(p1, 1),
                    "% among no IPV": round(p0, 1), "Chi-square (weighted)": round(chi, 2),
                    "p": round(p, 4)})
    pd.DataFrame(out).to_csv(TABLES / "table2_bivariate_outcomes_by_ipv.csv", index=False)
    print(pd.DataFrame(rows).to_string(index=False)); print(pd.DataFrame(out).to_string(index=False))


if __name__ == "__main__":
    main()
