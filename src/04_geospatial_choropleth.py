"""Step 4. County-level geospatial analysis and choropleth maps.

1. County weighted prevalence (IPV in pregnancy; adequate ANC)
2. Empirical Bayes shrinkage (Marshall 1991), needed because counties have few cases
3. Global Moran's I and Local Moran's I (LISA) on smoothed rates, queen contiguity
4. Static and interactive choropleth maps

Caution: county samples are small (the DV module has roughly 100-300 women per county), so
raw rates are noisy and spatial tests have limited power. Treat results as exploratory.
"""
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
from libpysal.weights import Queen, KNN, lat2W
from esda.moran import Moran, Moran_Local
from config import PROCESSED, TABLES, MAPS, FIGURES
from choropleth import load_counties, static_choropleth, categorical_map, interactive_choropleth

warnings.filterwarnings("ignore")
SEED = 20260101


def county_table(d, labels):
    rows = []
    for k, g in d.groupby("V024"):
        r = {"county": labels[k], "V024": k, "n_women": len(g), "sum_w": g.DVweight.sum(),
             "sum_w2": (g.DVweight ** 2).sum()}
        for var in ("IPV_preg", "ANC_adequate"):
            m = g[var].notna(); w = g.DVweight[m]
            r[f"{var}_n"] = int(m.sum())
            r[f"{var}_cases"] = int(g[var][m].sum())
            r[f"{var}_pct"] = 100 * np.average(g[var][m], weights=w) if m.sum() else np.nan
            r[f"{var}_neff"] = w.sum() ** 2 / (w ** 2).sum() if m.sum() else np.nan
        rows.append(r)
    return pd.DataFrame(rows)


def eb_smooth(p, neff):
    """Global empirical Bayes (Marshall) shrinkage of proportions p (0-1) with effective n."""
    p = np.asarray(p, float); n = np.asarray(neff, float)
    m = np.nansum(p * n) / np.nansum(n)
    s2 = np.nansum(n * (p - m) ** 2) / np.nansum(n) - m * (1 - m) / np.nanmean(n)
    s2 = max(s2, 1e-8)
    shrink = s2 / (s2 + m * (1 - m) / n)
    return m + shrink * (p - m), shrink


def main():
    d = pd.read_csv(PROCESSED / "analytic_dataset.csv")
    import pyreadstat
    labels = {}
    try:
        from config import RAW_SAV
        _, meta = pyreadstat.read_sav(str(RAW_SAV), usecols=["V024"], row_limit=1)
        labels = {int(k): v for k, v in meta.variable_value_labels["V024"].items()}
    except Exception:
        pass
    if not labels:  # fallback: labels bundled with the repo
        labels = pd.read_csv(PROCESSED / "county_labels.csv").set_index("V024")["county"].to_dict()
    ct = county_table(d, labels)

    for var in ("IPV_preg", "ANC_adequate"):
        ct[f"{var}_eb_pct"], ct[f"{var}_shrink"] = eb_smooth(ct[f"{var}_pct"] / 100, ct[f"{var}_neff"])
        ct[f"{var}_eb_pct"] *= 100
    ct.round(3).to_csv(PROCESSED / "county_prevalence.csv", index=False)

    gdf = load_counties().merge(ct, on="county", how="left")
    assert gdf["V024"].notna().all(), "County name mismatch between DHS and boundary file"
    gdf = gdf.sort_values("V024").reset_index(drop=True)

    w = Queen.from_dataframe(gdf, use_index=True)
    if w.islands:
        print("Queen islands:", [gdf.county[i] for i in w.islands], "-> using 4-nearest neighbours instead")
        w = KNN.from_dataframe(gdf.to_crs(21037), k=4)
    w.transform = "r"

    res = []
    for var, name in (("IPV_preg", "IPV in pregnancy"), ("ANC_adequate", "Adequate ANC (4+ visits)")):
        y = gdf[f"{var}_eb_pct"].values
        mi = Moran(y, w, permutations=9999)
        res.append({"Indicator": name, "Moran_I": round(mi.I, 3), "Expected_I": round(mi.EI, 3),
                    "z_sim": round(mi.z_sim, 2), "p_sim": round(mi.p_sim, 4)})
        np.random.seed(SEED)
        li = Moran_Local(y, w, permutations=9999, seed=SEED)
        q = {1: "High-High", 2: "Low-High", 3: "Low-Low", 4: "High-Low"}
        gdf[f"{var}_lisa"] = [q[a] if s else "Not significant" for a, s in zip(li.q, li.p_sim < 0.05)]
        gdf[f"{var}_lisa_p"] = li.p_sim
        print(name, "Moran's I =", round(mi.I, 3), "p =", round(mi.p_sim, 4))
        print(gdf[gdf[f"{var}_lisa"] != "Not significant"][["county", f"{var}_lisa"]].to_string(index=False))
    pd.DataFrame(res).to_csv(TABLES / "table4_morans_i.csv", index=False)
    gdf.drop(columns="geometry")[["county", "IPV_preg_lisa", "IPV_preg_lisa_p", "ANC_adequate_lisa",
                                  "ANC_adequate_lisa_p"]].round(4).to_csv(TABLES / "table5_lisa_clusters.csv", index=False)

    # ---- maps ----
    static_choropleth(gdf, "IPV_preg_pct", "Raw weighted prevalence of IPV during pregnancy (%)\nKenya counties, KDHS 2022",
                      MAPS / "map1_ipv_raw.png", legend_title="%")
    static_choropleth(gdf, "IPV_preg_eb_pct", "Empirical Bayes smoothed prevalence of IPV during pregnancy (%)",
                      MAPS / "map2_ipv_eb_smoothed.png", legend_title="%")
    static_choropleth(gdf, "ANC_adequate_eb_pct", "Smoothed prevalence of 4+ antenatal visits (%)",
                      MAPS / "map3_anc_eb_smoothed.png", legend_title="%")
    colors = {"High-High": "#A63603", "Low-Low": "#6baed6", "High-Low": "#FDAE6B", "Low-High": "#9ecae1",
              "Not significant": "#eeeeee"}
    categorical_map(gdf, "IPV_preg_lisa", colors, "LISA clusters: IPV during pregnancy (p < 0.05)", MAPS / "map4_ipv_lisa.png")
    categorical_map(gdf, "ANC_adequate_lisa", colors, "LISA clusters: 4+ antenatal visits (p < 0.05)", MAPS / "map5_anc_lisa.png")
    interactive_choropleth(gdf, "IPV_preg_eb_pct", "IPV during pregnancy, EB smoothed (%)",
                           MAPS / "interactive_ipv_map.html",
                           tooltip_cols=["IPV_preg_pct", "IPV_preg_eb_pct", "IPV_preg_cases", "n_women", "IPV_preg_lisa"])
    print("Maps written to", MAPS)


if __name__ == "__main__":
    main()
