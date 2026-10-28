"""Step 3. Weighted multivariable logistic regression.

GLM Binomial with frequency weights approximates SPSS WEIGHT BY + LOGISTIC REGRESSION.
It does not use PSU/strata, so confidence intervals can be narrower than a full
complex-survey analysis (svy in Stata, survey in R). State this when reporting.
County fixed effects are used for care-seeking outcomes and omitted for child survival
(only ~193 deaths, so 47 dummies cause separation).
"""
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from config import PROCESSED, TABLES, OUTCOMES
warnings.filterwarnings("ignore", category=RuntimeWarning)

BASE = "IPV_preg + C(AgeGroup) + C(V106) + V190 + Urban + C(Parity) + PartnerEduc"


def fit(dv, formula_rhs, d):
    f = f"{dv} ~ {formula_rhs}"
    cols = d.columns
    m = smf.glm(f, data=d, family=sm.families.Binomial(), freq_weights=d["DVweight"])
    return m.fit()


def tidy(res, label):
    ci = res.conf_int()
    t = pd.DataFrame({"Model": label, "Term": res.params.index,
                      "aOR": np.exp(res.params.values),
                      "CI_low": np.exp(ci[0].values), "CI_high": np.exp(ci[1].values),
                      "p": res.pvalues.values})
    return t[~t.Term.str.startswith("C(V024)") & (t.Term != "Intercept")]


def main():
    d = pd.read_csv(PROCESSED / "analytic_dataset.csv")
    d["V024"] = d["V024"].astype(int)
    results = []
    for dv, name in OUTCOMES.items():
        rhs = BASE + ("" if dv == "Child_alive" else " + C(V024)")
        dd = d.dropna(subset=[dv, "IPV_preg", "PartnerEduc"])
        res = fit(dv, rhs, dd)
        t = tidy(res, name); t["n"] = int(res.nobs) if False else len(dd)
        results.append(t)
        r = t[t.Term == "IPV_preg"].iloc[0]
        print(f"{name:32s} n={len(dd):5d}  aOR={r.aOR:.3f} ({r.CI_low:.3f}-{r.CI_high:.3f}) p={r.p:.3f}")
    # Predictors of IPV during pregnancy
    dd = d.dropna(subset=["IPV_preg", "PartnerEduc"])
    res = fit("IPV_preg", BASE.replace("IPV_preg + ", ""), dd)
    t = tidy(res, "Predictors of IPV in pregnancy"); t["n"] = len(dd); results.append(t)
    out = pd.concat(results).round(4)
    out.to_csv(TABLES / "table3_logistic_models.csv", index=False)


if __name__ == "__main__":
    main()
