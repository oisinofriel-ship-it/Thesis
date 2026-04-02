# Thesis Project Memory

## Overview
- **Topic**: Macro-augmented HAR-RV models for RV forecasting — SPX, GBP/USD, XAU/USD
- **Report**: `C:\Users\oisin\Thesis\Final_Report.tex` + `references.bib`
- **Git repo**: `https://github.com/oisinofriel-ship-it/Thesis` (synced with Overleaf)

---

## Directory Structure
| Path | Contents |
|------|----------|
| `C:\Users\oisin\Thesis\` | LaTeX report, references, memory |
| `...\THESIS\Model\SPX\` | SPX notebook (`SPX_stats.ipynb`), data |
| `...\THESIS\Model\CABLE\` | GBP notebook (`GBP_stats.ipynb`), data |
| `...\THESIS\Model\XAU\Full_Data\` | XAU notebook (`XAU_stats.ipynb`), data |
| `...\THESIS\Model\Historical_SPX\` | Historical SPX notebook, CSV data |

## Key Data Files (all model dirs share macro/tariff files)
| File | Description |
|------|-------------|
| `SPX_1.xlsx`–`SPX_14.xlsx` | Raw intraday SPX data |
| `Macro_dates.xlsx` | FOMC, CPI, NFP announcement dates |
| `Macro_Expected_back_to_2023.xlsx` | Consensus forecasts, actuals, surprise categories (0/1/2) from Jan 2023 |
| `tariff_wss_v2.xlsx` | Tariff WSS scores; TARIFF=1 when WSS≥5 |
| `rv_spx.xlsx` | Computed daily RV |

## Sample Periods
| Dataset | In-Sample | Out-of-Sample |
|---------|-----------|---------------|
| SPX (main) | 2025-07-22 – 2026-01-29 | 2026-01-30 – 2026-03-20 |
| SPX (historical) | 2023-05-01 – ~2023-09-25 (80%) | ~2023-09-26 – 2023-10-31 |
| GBP/USD | 2025-10-29 – (cutoff TBD) | TBD |
| XAU/USD | 2025-12-04 – (cutoff TBD) | TBD |

## Trading Hours
- **SPX**: 09:30–16:00 ET (6.5 hr)
- **GBP/USD**: 22:00 Sun – 22:00 Fri UTC, continuous 24 hr
- **XAU/USD**: 22:00 Sun – 22:00 Fri UTC, 23 hr/day (break 22:00–23:00 UTC daily)
- GBP/XAU have mechanically higher daily RV than SPX due to longer sessions

---

## Models
| Model | Description | Key extra features |
|-------|-------------|-------------------|
| 1 | Baseline HAR-RV | — |
| 2 | HAR-RV + Individual Macro Dummies | FOMC, CPI, NFP, TARIFF |
| 3a | Expected vs Surprise (all non-FOMC events) | MACRO_0/1/2, FOMC_exp, FOMC_unexp, TARIFF |
| 3b | Expected vs Surprise (CPI+NFP only) | MACRO*_0/1/2, FOMC_exp, FOMC_unexp, TARIFF |
| 4 | Three-Tier Individual Dummies | CPI_0/1, NFP_0/1, FOMC_0/1, TARIFF (tier-2 dummies dropped — zero occurrences) |
| 5 | Three-Tier + Adjusted RV_d Lag | Same as 4 but RV_d replaced with RV_d* on days after event days |
| 6 | Random Forest (500 trees, seed=42) | Same features as Model 5; Gini feature importances |

**Naming history**: Model 3→3a, Model 4b→3b (variable suffixes: _m3→_m3a, _m4b→_m3b)

### Three-Tier Classification
- Cat 0 (in-line): |std surprise| ≤ 0.5 SD
- Cat 1 (moderate): 0.5 < |std surprise| ≤ 1.0 SD
- Cat 2 (large): |std surprise| > 1.0 SD
- FOMC uses CME futures-implied expectation; all others use Investing.com survey consensus

---

## SPX In-Sample Results (IS window: 2025-09-24 – 2026-01-29, n=86)
### Coefficients (HAC SE, Newey-West 5 lags)
| Variable | M1 | M2 | M3a | M4 | M5 |
|----------|----|----|-----|----|----|
| α | -4.9885** | -4.8633*** | -4.6182** | -4.6989** | -5.0763** |
| β_d | 0.4258*** | 0.4642*** | 0.4734*** | 0.4798*** | 0.3649*** |
| β_w | 0.1868 | 0.2231 | 0.1967 | 0.1801 | 0.2479 |
| β_m | -0.0876 | -0.1420 | -0.1049 | -0.1000 | -0.0923 |
| γ1/FOMC | — | 1.2258*** | — | — | — |
| γ2/CPI | — | 0.0667 | — | — | — |
| γ3/NFP | — | 0.6274*** | — | — | — |
| λ/TARIFF | — | 0.4072 | 0.3431 | 0.3893 | 0.6842** |
| δ0/MACRO_0 | — | — | -0.0966 | — | — |
| δ1/MACRO_1 | — | — | 0.2028 | — | — |
| δ2/MACRO_2 | — | — | -0.1904 | — | — |
| φ1/FOMC_exp | — | — | 1.1548*** | — | — |
| φ2/FOMC_unexp | — | — | 1.2623*** | — | — |
| γ_CPI,0 | — | — | — | 0.4963*** | 0.3536** |
| γ_CPI,1 | — | — | — | -0.1594 | -0.1993 |
| γ_NFP,0 | — | — | — | 0.0048 | -0.0385 |
| γ_NFP,1 | — | — | — | 1.2221*** | 1.2420*** |
| γ_FOMC,0 | — | — | — | 1.1819*** | 1.0476** |
| γ_FOMC,1 | — | — | — | 1.2851*** | 1.1479*** |

### Fit Statistics
| Metric | M1 | M2 | M3a | M4 | M5 | M6 (RF) |
|--------|----|----|-----|----|----|---------|
| IS R² | 0.2531 | 0.3429 | 0.3317 | 0.3528 | 0.2930 | 0.8681 |
| IS Adj R² | 0.2258 | 0.2839 | 0.2525 | 0.2666 | 0.1987 | 0.8546 |
| IS RMSE | 0.7335 | 0.6880 | 0.6939 | 0.6828 | 0.7137 | 0.3105 |
| OOS R² | -0.3390 | -0.5881 | -0.4969 | -0.6446 | -0.7126 | -0.7680 |
| OOS RMSE | 0.6663 | 0.7256 | 0.7045 | 0.7384 | 0.7535 | 0.7656 |

### Model 6 SPX Feature Importances
| Feature | Importance |
|---------|-----------|
| RV_d | 0.4030 |
| RV_w | 0.2702 |
| RV_m | 0.2186 |
| FOMC_1 | 0.0366 |
| TARIFF | 0.0279 |
| FOMC_0 | 0.0210 |
| NFP_1 | 0.0150 |
| CPI_1 | 0.0041 |
| NFP_0 | 0.0028 |
| CPI_0 | 0.0008 |

---

## Chapter 4 Structure (Final_Report.tex, as of 2026-04-02)
- **4.1** Descriptive Statistics — intro para, raw RV stats table (×10^6, all 4 assets), RV plots, per-asset macro event tables, tariff summary table (`tab:tariff_summary`), cross-asset suitability discussion, supplementary stats recommendations
- **4.2** In-Sample Estimation Results — section intro + discussion paragraphs after each model table
  - 4.2.1 Baseline and Binary Macro Augmentation — M1 (daily lag dominant, weekly/monthly NS), M2 (FOMC***, NFP***, CPI NS, negative TARIFF for GBP)
  - 4.2.2 Surprise-Differentiated Specifications — M3a (FOMC exp≈unexp, MACRO tiers NS), M3b (CPI+NFP only, better adj R²), M4 (best IS linear, NFP_1 dominant, FOMC both tiers ***), M5 (lag adjustment, TARIFF NS still)
  - 4.2.3 Random Forest Benchmark — HAR components dominate importance (89%), severe OOS overfitting
- **4.3** Out-of-Sample Forecast Comparison — section intro + OOS discussion: all models negative OOS R², baseline best for SPX/GBP, RF worst for SPX, RF best for XAU

**Table format**: Cross-asset tables (SPX, SPX 2023, GBP, XAU) with Coef. + (t-stat) columns; N=109/78/40/14 in-sample respectively. M6 uses feature importance table. OOS table (tab:cross_asset) has `\scriptsize` descriptor labels.

**Tariff table** (`tab:tariff_summary`): unified cross-asset — SPX=14 days, GBP=6, XAU=5 with WSS≥5.

**Key file**: `C:\Users\oisin\Thesis\Final_Report.tex` is the git/Overleaf canonical version. The OneDrive copy (`...\THESIS\Final Report\Final_Report.tex`) is a divergent older copy — do NOT edit it.

## Chapter 3 Structure
- **3.1**: Data (Intraday Price Data, Data Cleaning, Macro Data, Tariff Data, Sample Periods)
- **3.2**: Realised Variance Construction (Daily RV, Log Transform, Multi-Horizon Components)
- **3.3**: Model Framework (Models 1–6, summary table `\ref{tab:model_summary}`)
- **3.4**: Estimation (OLS/HAC, Estimation Window + OOS method, RF Benchmark)
- **3.5**: Evaluation Framework (Performance Metrics, Cross-Asset Replication)

---

## Outstanding Issues
- **GBP/XAU IS/OOS split dates** not stated in 3.1.5
- **De-escalation TARIFF**: de-esc events excluded from dummy — acknowledge in limitations
- **Stationarity**: ADF tests in Ch4 should cross-reference 3.4.1
- **Log RV descriptive stats for GBP/XAU**: notebooks compute raw RV stats — need to recompute in log space to complete Table tab:summary_stats
- **JB/ADF values**: placeholders in 4.1 text — `[statistics to be inserted]`
- **Correlation table placeholder**: `% [PLACEHOLDER: Cross-asset log RV correlation table...]` in 4.1
- **Chapter 5 (Discussion)** and **Chapter 6 (Conclusion)** not yet drafted

## Potential Next Steps
- QLIKE loss function (Patton 2011) — asymmetric, standard in RV literature
- Diebold-Mariano test — pairwise forecast accuracy differences
- Model Confidence Set — Hansen et al. (2011)

---

## LaTeX / Citation Rules
- **Citations**: add to `references.bib` FIRST, then `\cite{}` in tex. Never cite without bib entry.
- Equations: standalone `\begin{equation}`, `\noindent` after; multiline uses `\begin{split}`
- Use `\citep{}` parenthetical, `\citet{}` textual
- Avoid hardcoded sample numbers (e.g. "130 trading days")
- Terminology: "realised variance (RV)" on first mention; never "realised volatility"

## Git / Overleaf
- Always `git pull` before pushing — Overleaf pushes can cause conflicts
- When resolving conflicts: keep correct GBP/XAU trading hours (22:00–22:00 UTC)

## Technical Notes
- All OLS: HAC SE (Newey-West, 5 lags); significance: *** p<0.01, ** p<0.05, * p<0.10
- Zero-occurrence dummies dropped (CPI_2, NFP_2, FOMC_2 absent from Models 4/5)
- `full_*` dataframes built over full sample so OOS lags use actual history
- RF (Model 6) overfits in-sample (IS R²=0.87); OOS is the real test
- 53 BibTeX entries in `references.bib` (as of 2026-03-28)
