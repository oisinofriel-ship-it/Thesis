# CLAUDE.md: Thesis Agent Configuration

## Context
- **Audience**: Mechanical engineering (UCD). All finance/economics concepts must be explained clearly — no assumed background.
- **Topic**: HAR-RV models augmented with macro/tariff variables — SPX, GBP/USD, XAU/USD
- **Canonical LaTeX**: `C:\Users\oisin\Thesis\Final_Report.tex` — do NOT edit the OneDrive copy

## Memory — Read at Every Session Start
1. `memory.md` — model specs, results, naming, data files
2. `CLAUDE.md` (this file)
3. `skills.md` — modelling task instructions

## Chapter 3 Key Facts (for Ch4 writing)
- **RV construction**: sum of squared 5-min log-returns; log-transformed for estimation (Eqs 3.1–3.3)
- **HAR components**: RV_d = y_{t-1}; RV_w = mean of y_{t-1..t-5}; RV_m = mean of y_{t-1..t-22} (Eqs 3.4–3.6)
- **Estimation**: fixed IS window, OLS + HAC SE (Newey-West, 5 lags); no re-estimation in OOS; OOS lags from full dataset
- **All metrics on log-RV scale** (R², Adj R², RMSE, MAE) — do not back-transform
- **Three-tier thresholds**: Cat 0 ≤ 0.5 SD; Cat 1 (0.5, 1.0] SD; Cat 2 > 1.0 SD (standardised surprise)
- **FOMC**: CME futures-implied expectation (not survey); FOMC_exp = Cat 0, FOMC_unexp = Cat 1 or 2
- **TARIFF**: WSS ≥ 5 threshold; 15 of 36 events qualify; de-escalation events not excluded from dummy
- **M5 adjusted lag**: replaces RV_d on ~15% of SPX IS trading days (post-event days)
- **Historical SPX**: no TARIFF dummy (zero events in May–Oct 2023 sample); 80:20 dynamic split
- **OOS**: SPX ~35 trading days (30 Jan – 20 Mar 2026); GBP/XAU OOS periods shorter
- **Cross-references**: cite equations as `Equation~\ref{...}` and sections as `Section~\ref{...}` using Ch3 labels

## Writing Standards
- Formal, third-person, analytical. No AI clichés.
- Citations: add to `references.bib` first, then `\cite{}`. Harvard format.
- Terminology: "realised variance (RV)" on first mention; never "realised volatility".
- Equations: standalone `\begin{equation}`, `\noindent` after; multiline uses `\begin{split}`.

## Key Rules
- Never fabricate results — all metrics from actual model output.
- Variable naming: `_m1` … `_m6` — check `memory.md` before any rename.
- HAC SE: Newey-West, 5 lags. Significance: *** p<0.01, ** p<0.05, * p<0.10.

## Git / Overleaf
- Always `git pull` before pushing.
- Conflicts: keep correct GBP/XAU trading hours (22:00–22:00 UTC), VIX figure, detailed Data Cleaning.
