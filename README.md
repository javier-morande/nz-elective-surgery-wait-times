# New Zealand Elective Surgery Wait Times

Analysis and forecasting of elective treatment wait times across New Zealand using Health New Zealand waitlist data.

## Explore the project

- **[Visual project overview](https://javier-morande.github.io/nz-elective-surgery-wait-times/)** — specialty, district and ethnicity comparisons, national trends, forecasts and evaluation.
- **[View the complete rendered analysis](https://javier-morande.github.io/nz-elective-surgery-wait-times/elective_wait_times.html)** — the full Quarto report with all 16 original figures, code and statistical outputs.
- [Quarto source](elective_wait_times.qmd) · [Python forecasting code](waitlist_prediction.py)

The homepage presents selected findings and links to their original report sections. Additional charts can be expanded in each section; click any chart to view the original PNG at full size.

## Project Overview

This project investigates elective treatment wait times in New Zealand, with a particular focus on patients waiting longer than 120 days.

The analysis explores differences across specialties, districts and ethnic groups, examines how waitlist performance has changed over time, and uses forecasting models to estimate national waitlist outcomes through 2027.

## Key Questions

- Which specialties have the highest proportion waiting over 120 days?

- Which districts are experiencing the greatest waitlist pressure?

- How does waitlist performance differ across ethnic groups?

- How has elective waitlist performance changed over time?

- What could national elective wait times look like during 2026 and 2027?

## Data

The project uses Health New Zealand elective waitlist data covering June 2015 to September 2025.

The dataset includes information on:

- District

- Region

- Specialty

- Ethnicity

- Month

- Total number waiting

- Number waiting under 120 days

Suppressed values reported as `<5` were estimated using a midpoint value of 2.5 for analysis.

## Methods

The project combines exploratory data analysis, statistical analysis and predictive modelling.

Methods include:

- Data cleaning and suppression handling

- Time-series analysis

- Specialty and district comparisons

- Ethnicity analysis

- ARIMA forecasting

- Random Forest regression

- Gradient Boosting

- Persistence baseline modelling

- Rolling forecast validation

Machine-learning models were evaluated using chronological training, validation and test periods rather than random data splitting.

## Key Findings

The analysis identified substantial differences in elective waitlist performance across districts and specialties.

Orthopaedic Surgery frequently appeared among the worst-performing specialties across districts, while several district-specialty combinations showed particularly high proportions waiting longer than 120 days.

National forecasting suggests that the percentage waiting over 120 days could remain around the mid-30% range through 2026 and 2027.

The total elective waitlist is forecast to increase to approximately:

- **84,000 by December 2026**

- **86,200 by December 2027**

These results suggest that substantial improvement would still be required for elective wait-time performance to approach the national target.

## Tools

**R**

- tidyverse

- ggplot2

- lubridate

- forecast

**Python**

- pandas

- scikit-learn

**Other**

- RStudio

- Quarto

- Git

- GitHub

## Repository files

| Path | Purpose |
| --- | --- |
| `index.html`, `assets/portfolio.css` | Responsive GitHub Pages project homepage |
| `elective_wait_times.qmd` | Complete R analysis and Quarto source |
| `elective_wait_times.html` | Self-contained rendered report, including all figures, styles and scripts |
| `elective_wait_times_files/figure-html/` | All 16 original PNG figures, also used on the homepage |
| `assets/figures.json` | Figure paths, report section anchors, dimensions and SHA-256 checksums |
| `waitlist_prediction.py` | Python subgroup models and national forecasting backtest |
| `data/Waitlist-detail-extract-Q1-2025-26.xlsx` | Original source workbook |
| `scripts/export_figures.py` | Exports the existing report's embedded PNGs without running analysis |
| `scripts/check_site.py` | Checks links, anchors, assets and exact figure integrity locally or after deployment |

## Run and reproduce

The published report can be opened directly in a browser; R and Python are not required to read it.

To serve the portfolio locally from the repository root:

```sh
python3 -m http.server 8000
```

Then open `http://localhost:8000/`.

To deliberately rerun the analysis, install Quarto, R and the R packages `tidyverse`, `readxl` and `forecast`, then run from the repository root:

```sh
quarto render elective_wait_times.qmd
```

The source uses `embed-resources: true`, so the complete report remains portable. Rendering also generates `waitlist_cleaned.csv`, the input to `waitlist_prediction.py`. To run that existing Python analysis, install `pandas`, `scikit-learn` (1.4 or later, for `root_mean_squared_error`) and `statsmodels`, then run:

```sh
python3 waitlist_prediction.py
```

Model results can depend on package versions; no package-version lockfile was present in the original project. Review results before publishing a newly executed analysis.

## Publishing and asset checks

The repository root is the GitHub Pages publishing directory on `main`. `.nojekyll` serves the static files directly. Internal site links are relative to the repository root so they work under the GitHub Pages project path.

The restored publication uses the existing local self-contained report. **No statistical code was rerun or changed for the asset repair.** All 16 exported PNGs are byte-for-byte copies of the images embedded in that report. Its required JavaScript, CSS and fonts are embedded as well; no separate `libs/` folder is needed for this report.

After a future intentional render:

```sh
python3 scripts/export_figures.py
python3 scripts/check_site.py
```

The exporter preserves the existing Quarto chunk filenames. If the number or order of figures changes, review `CHUNKS` in the exporter and the homepage captions/links before publishing. Commit the rendered HTML, updated source, the entire required `elective_wait_times_files/` directory, and `assets/figures.json` together. `.gitignore` excludes the temporary `.quarto/` cache, not published `_files` directories.

After deployment:

```sh
python3 scripts/check_site.py --base-url https://javier-morande.github.io/nz-elective-surgery-wait-times/
```

This checks every local homepage/report link and section anchor, fetches every exported graph, and compares all 16 graphs with the embedded report images and their saved hashes. Run it before and after publishing to catch missing assets.

## Notes

Health New Zealand reports some patient counts as `<5` to protect confidentiality. These suppressed observations were estimated as 2.5 for the purposes of this analysis.

Forecasts should be interpreted as estimates of future trends rather than exact future outcomes.
