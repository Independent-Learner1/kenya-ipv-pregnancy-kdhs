# Data

| Folder | Contents | In repo? |
|---|---|---|
| `raw/` | `KEIR8CFL.SAV`, KDHS 2022 Women's Individual Recode | **No.** Restricted. |
| `processed/county_prevalence.csv` | County-level aggregates (n, cases, weighted %, EB-smoothed %) | Yes |
| `processed/county_labels.csv` | DHS `V024` code to county name | Yes |
| `processed/analytic_dataset.csv` | Individual-level analytic file, created by step 1 | No (git-ignored) |
| `geo/` | County boundaries from geoBoundaries (gbOpen, ADM1, Kenya), CC BY 4.0 | Yes |

## Getting the KDHS data
1. Register at https://dhsprogram.com and request access to the **Kenya 2022** survey.
2. Download the Women's Individual Recode (`KEIR8CFL`), SPSS format (`.SAV`).
3. Put it in `data/raw/` or set `KDHS_SAV=/path/to/KEIR8CFL.SAV`.

DHS terms prohibit passing the datasets to third parties, so the raw file is deliberately not in this repository.
