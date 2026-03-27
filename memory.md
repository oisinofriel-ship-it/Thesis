# Thesis Project Memory

## Overview
- **Student**: Oisin
- **Institution**: University College Dublin (UCD)
- **Topic**: Macro-augmented HAR-RV models for forecasting realised volatility of the S&P 500 (SPX), with a focus on the impact of macroeconomic announcements and tariff policy events
- **Main Report**: `C:\Users\oisin\Thesis\Final_Report.tex` (LaTeX, with `references.bib`)

---

## Directory Structure
- **Thesis root**: `C:\Users\oisin\Thesis\` — LaTeX report, references, memory
- **Model/data directory**: `C:\Users\oisin\OneDrive - University College Dublin\THESIS\Model\SPX\`
- **Primary notebook**: `SPX_stats.ipynb` — all models, OOS evaluation, comparison table

## Key Data Files (in SPX directory)
| File | Description |
|------|-------------|
| `SPX_1.xlsx` to `SPX_14.xlsx` | Raw intraday SPX data (split across files) |
| `Macro_dates.xlsx` | FOMC, CPI, NFP announcement dates |
| `Macro_Expected_back_to_2023.xlsx` | Consensus forecasts, actuals, and pre-computed surprise categories (0/1/2) for FOMC, CPI, NFP, PPI, PCE, ADP, JOLTS, CLAIMS from Jan 2023 onward |
| `tariff_wss_v2.xlsx` | Tariff event scoring (Weighted Severity Score); TARIFF dummy = 1 when WSS >= 5 |
| `rv_spx.xlsx` | Computed daily realised variance |

---

## Notebook Structure (SPX_stats.ipynb)

### Data Preparation (Cells 0-3)
- Imports: numpy, pandas, scipy, statsmodels, matplotlib, sklearn
- Computes daily realised variance (RV) from intraday data
- Descriptive statistics for log(RV)
- Plot: RV time series with macro event lines overlaid

### HAR Feature Construction
- `build_har_features(rv)` — standard HAR: RV_d (1-day lag), RV_w (5-day rolling mean, lagged), RV_m (22-day rolling mean, lagged)
- `build_har_features_adj(rv, macro_flag)` — adjusted version for Model 5: RV_d skips macro/tariff event days and uses most recent non-event day's log-RV
- Target variable: `y = log(RV)`

### Sample Periods
- **Data starts**: `START_DATE = pd.Timestamp("2025-07-22")`
- **In-sample**: 2025-07-22 to `CUTOFF = pd.Timestamp("2026-01-29")`
- **Out-of-sample**: `2026-01-30` to `2026-03-20`

---

## Models

### Model 1 — Baseline HAR-RV (Cell 4)
- Features: RV_d, RV_w, RV_m
- OLS with HAC standard errors (Newey-West, 5 lags)
- Variables: `har_model`, `is_rmse`, `is_mae`, `full_base`, `har_is`

### Model 2 — HAR-RV + Individual Macro Dummies (Cell 7)
- Features: RV_d, RV_w, RV_m + FOMC, CPI, NFP, TARIFF (binary 0/1 dummies)
- Event dates from `Macro_dates.xlsx`; tariff from `tariff_wss_v2.xlsx`
- Variables: `har_model_m2`, `is_rmse_m2`, `is_mae_m2`, `full_m2`, `feat_m2`

### Model 3a — Expected vs Surprise (Cell 9)
- Parses `Macro_Expected_back_to_2023.xlsx` via `parse_macro_b23()`
- Builds per-event per-category dummies (e.g. CPI_0, CPI_1, CPI_2)
- Collapses all non-FOMC events into composite MACRO_0, MACRO_1, MACRO_2 (daily max across CPI, NFP, PPI, PCE, ADP, JOLTS, CLAIMS)
- FOMC_exp = FOMC_0; FOMC_unexp = max(FOMC_1, FOMC_2)
- Features: RV_d, RV_w, RV_m + MACRO_0/1/2, FOMC_exp, FOMC_unexp, TARIFF
- Variables: `har_model_m3a`, `is_rmse_m3a`, `is_mae_m3a`, `full_m3a`, `feat_m3a`

### Model 3b — FOMC exp/unexp + CPI/NFP Only Macro Tiers (Cell 11)
- Same as 3a but MACRO_0/1/2 constructed from **CPI and NFP only** (excludes PPI, PCE, ADP, JOLTS, CLAIMS)
- Uses `macro_b23_dummies_4b` (separate dummy frame)
- Features: RV_d, RV_w, RV_m + MACRO_0/1/2, FOMC_exp, FOMC_unexp, TARIFF
- Variables: `har_model_m3b`, `is_rmse_m3b`, `is_mae_m3b`, `full_m3b`, `feat_m3b`

### Model 4 — Three-Tier Individual Dummies (Cell 13)
- Individual event-level dummies: CPI_0/1/2, NFP_0/1/2, FOMC_0/1/2 + TARIFF
- Dummies with zero in-sample occurrences are dropped (e.g. CPI_2, NFP_2, FOMC_2 were dropped)
- Features: RV_d, RV_w, RV_m + `macro_ind_avail` + TARIFF
- Variables: `har_model_m4`, `is_rmse_m4`, `is_mae_m4`, `full_m4`, `feat_m4`

### Model 5 — Three-Tier + Adjusted RV_d Lag (Cell 15)
- Same features as Model 4 but RV_d lag is adjusted: when previous day was a macro/tariff event day, uses most recent prior non-event day's log-RV instead
- Macro days identified as: any CPI/NFP/FOMC category (0/1/2) OR TARIFF = 1
- Variables: `har_model_m5`, `is_rmse_m5`, `is_mae_m5`, `full_m5`, `feat_m5`, `is_macro_day`

### Model 6 — Random Forest (Cell 17)
- `RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1)`
- Uses **exact same data and features as Model 5** (`har_is_m5`, `feat_m5`)
- Computes feature importances (Gini-based)
- Variables: `rf_model_m6`, `is_rmse_m6`, `is_mae_m6`, `is_r2_m6`, `is_r2_adj_m6`
- Note: RF will overfit in-sample (high IS R²); OOS performance is the real test

---

## Out-of-Sample Evaluation (Cell 19)
- Period: 2026-01-30 to 2026-03-20
- For OLS models (1-5): slices OOS rows from `full_*` dataframes, adds constant, calls `.predict()`
- For RF (Model 6): uses same OOS slice as Model 5, calls `rf_model_m6.predict()`
- Metrics computed per model: OOS RMSE, OOS MAE, OOS R², OOS Adjusted R²
- Helper function: `oos_adj_r2(y_true, y_pred, p)` — formula: `1 - (1-R²)(n-1)/(n-p-1)`

---

## Comparison Table (Cell 21)
- Columns: Description, In-Sample R², Adjusted R², IS RMSE, IS MAE, OOS R², OOS Adj R², OOS RMSE, OOS MAE
- Styled HTML table with `highlight_best()` — bold blue for best in each column (highest for R², lowest for RMSE/MAE)
- Caption includes both IS and OOS date ranges

---

## Three-Tier Surprise Classification System
- Category 0: In line with expectations
- Category 1: Moderate surprise
- Category 2: Large/big surprise
- Categories are pre-computed in `Macro_Expected_back_to_2023.xlsx` (column index 6)
- Historical data from Jan 2023 used to build standard deviation distributions for thresholds
- Applied to: FOMC, CPI, NFP, PPI, PCE, ADP, JOLTS, CLAIMS

## Tariff Dummy Construction
- Source: `tariff_wss_v2.xlsx`, sheet "Tariff Event Scoring"
- Each date assigned a Weighted Severity Score (WSS)
- TARIFF = 1 when WSS >= 5, else 0
- Parsed via `_parse_tariff()` function applied to "Scoring Notes" column

---

## Naming History
- "Model 3" was renamed to "Model 3a" (all macro events in composite)
- "Model 4b" was renamed to "Model 3b" (CPI/NFP only composite)
- All variable suffixes updated accordingly (_m3 -> _m3a, _m4b -> _m3b)

---

## Metrics Glossary
| Metric | Direction | Description |
|--------|-----------|-------------|
| R² | Higher = better | Proportion of variance explained |
| Adjusted R² | Higher = better | R² penalised for number of features |
| RMSE | Lower = better | Root mean squared error (penalises large errors) |
| MAE | Lower = better | Mean absolute error (treats all errors equally) |

---

## Potential Next Steps (discussed but not yet implemented)
- **QLIKE** loss function — asymmetric, penalises under-prediction of volatility more (standard in RV literature, Patton 2011)
- **Diebold-Mariano test** — pairwise statistical test of forecast accuracy differences between models
- **Model Confidence Set (MCS)** — Hansen et al. (2011), identifies statistically indistinguishable best models

---

## Technical Notes
- All OLS models use HAC standard errors (Newey-West, 5 lags)
- Significance stars: *** (p<0.01), ** (p<0.05), * (p<0.10)
- In-sample dummies with zero occurrences are excluded to avoid perfect multicollinearity
- The `full_*` dataframes are built over the **full sample** so that OOS lags (RV_w, RV_m) can use in-sample history
- CUTOFF defined once in Cell 4 and reused by all models
