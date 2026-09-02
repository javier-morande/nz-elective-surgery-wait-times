# New Zealand Elective Surgery Wait Times

Analysis and forecasting of elective treatment wait times across New Zealand using Health New Zealand waitlist data.

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

## Repository Files

- `elective_wait_times.qmd` — Main analysis and Quarto report

- `elective_wait_times.html` — Rendered project report

- `waitlist_prediction.py` — Python machine-learning analysis

- `data/` — Original waitlist dataset

## Notes

Health New Zealand reports some patient counts as `<5` to protect confidentiality. These suppressed observations were estimated as 2.5 for the purposes of this analysis.

Forecasts should be interpreted as estimates of future trends rather than exact future outcomes.
