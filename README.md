# Physical intimate partner violence during pregnancy, maternal care seeking and child survival in Kenya (KDHS 2022)

Reproducible Python pipeline for a secondary analysis of the 2022 Kenya Demographic and Health Survey,
with a **county-level geospatial component** (empirical Bayes smoothing, Moran's I, LISA) and
**choropleth mapping** (static and interactive).

Author: Briton Kavulavu ([@Independent-Learner1](https://github.com/Independent-Learner1)).

## What it does
| Step | Script | Output |
|---|---|---|
| 1 | `src/01_build_analytic_dataset.py` | Filters the domestic violence module sample (n = 8,559), recodes exposure, outcomes and covariates |
| 2 | `src/02_descriptive_and_bivariate.py` | Weighted prevalence by characteristic, bivariate tests (`outputs/tables`) |
| 3 | `src/03_logistic_models.py` | Weighted multivariable logistic regression, adjusted odds ratios |
| 4 | `src/04_geospatial_choropleth.py` | County prevalence, EB smoothing, Moran's I, LISA clusters, maps (`outputs/maps`) |
| any | `src/choropleth.py` | Reusable tool: map any county-level CSV (`--csv --value-col --out`) |

## Run it
```bash
git clone https://github.com/Independent-Learner1/kenya-ipv-pregnancy-kdhs.git
cd kenya-ipv-pregnancy-kdhs
pip install -r requirements.txt
# put KEIR8CFL.SAV in data/raw/  (see data/README.md)
python run_all.py
```
Map your own county data:
```bash
python src/choropleth.py --csv my.csv --county-col county --value-col rate --title "Rate (%)" --out outputs/maps/my_map
```

## Key results (reproduced by the code)
- Weighted prevalence of physical IPV during pregnancy: **2.70%** (n = 8,559 women with a birth in the last 5 years).
- Adjusted association with child survival: **aOR 0.43 (95% CI 0.21 to 0.89), p = 0.023**.
- Associations with 4+ ANC visits, early ANC, facility delivery and PNC within 48 hours were not significant after adjustment.
- Spatial: global Moran's I on smoothed county IPV prevalence = 0.16 (p = 0.03); for 4+ ANC visits = 0.30 (p = 0.001). See `outputs/tables`.

## Methods notes and limitations
- Weights: `D005 / 1,000,000` (domestic violence module weight).
- Models use `statsmodels` GLM (binomial) with frequency weights. This matches SPSS `WEIGHT BY` but does **not** model PSU/strata, so standard errors may be too small relative to a full complex-survey analysis (use R `survey` or Stata `svy` for that).
- Child survival is modelled without county fixed effects because there are few deaths (193).
- County samples are small (a handful of IPV cases per county). Raw county rates are very noisy, so the maps show empirical Bayes shrunken estimates (Marshall 1991) alongside raw ones. Spatial statistics are **exploratory**, based on queen contiguity with 9,999 permutations; LISA clusters should not be read as confirmed hotspots.
- Distance-to-facility and marital status were excluded from the primary models (high missingness; collinearity).

## Data and licences
- Code: MIT.
- KDHS 2022 microdata: **not included**; obtain from the DHS Program (see `data/README.md`).
- Boundaries: geoBoundaries gbOpen, Kenya ADM1, CC BY 4.0 (Runfola et al. 2020, https://www.geoboundaries.org).

## Repository layout
```
src/            scripts (01-04, choropleth.py, config.py)
data/geo/       county boundaries
data/processed/ aggregated county data (no individual records)
outputs/        tables, figures, maps (incl. interactive_ipv_map.html)
run_all.py
```

## Citation
Kavulavu, B. (2026) *Physical intimate partner violence during pregnancy, maternal healthcare seeking and child survival in Kenya: analysis code (KDHS 2022)*. GitHub: https://github.com/Independent-Learner1/kenya-ipv-pregnancy-kdhs
