# SKILLS.md: Thesis Model & Analysis AI Agent Capabilities

## Functional Skills
This file defines the specialized skills and capabilities for the modelling and analysis work in this directory.

| Skill Name | Objective | Key Instructions & Steps |
|:---|:---|:---|
| **Model Implementation** | Build and modify HAR-RV model specifications in the Jupyter notebook. | 1. Read `memory.md` to check current model specs and variable naming conventions. 2. Read the target cell in `SPX_stats.ipynb` before editing. 3. Follow established patterns (OLS + HAC SE for linear models, sklearn for ML). 4. Compute all standard metrics (R², Adj R², RMSE, MAE). 5. Update the comparison table. 6. Update `memory.md` with new model details. |
| **OOS Evaluation** | Apply fitted models to out-of-sample data and compute forecast metrics. | 1. Slice OOS period from `full_*` dataframes (already built over full sample). 2. For OLS: add constant, call `.predict()`. For RF: call `.predict()` on feature array. 3. Compute OOS RMSE, MAE, R², Adjusted R². 4. Update comparison table with results. |
| **Notebook Cell Editing** | Safely modify Jupyter notebook cells without breaking dependencies. | 1. Always read the cell before editing. 2. Check variable names against `memory.md`. 3. Verify upstream/downstream dependencies (e.g., if renaming a variable, update all cells that reference it). 4. Use NotebookEdit for cell modifications, Bash+Python for bulk changes across multiple cells. |
| **Variable Renaming** | Rename model variables consistently across the entire notebook. | 1. Read `memory.md` Naming History for context. 2. Identify ALL cells referencing the old name (code cells, markdown cells, HTML output). 3. Replace in all locations. 4. Update `memory.md` Naming History. 5. Verify no stale references remain. |
| **Results Interpretation** | Describe and analyse model outputs for thesis writing. | 1. Read model coefficients, significance levels, and fit statistics from notebook output. 2. Compare IS vs OOS performance across specifications. 3. Identify which macro variables are significant and interpret their economic meaning. 4. Contextualise within existing literature (Corsi 2009, Patton 2011, etc.). 5. Use formal academic tone per CLAUDE.md standards. |
| **Data & Results Reporting** | Generate thesis-ready tables and descriptions of model results. | 1. Extract coefficient tables with HAC standard errors and significance stars. 2. Format comparison tables with all IS and OOS metrics. 3. Describe results in formal academic prose (third person, Harvard citations). 4. Flag the best-performing model in each metric category. |
| **Memory Maintenance** | Keep memory.md current as a living project knowledge base. | 1. At session start: read `memory.md`, `CLAUDE.md`, `skills.md`. 2. During session: update `memory.md` immediately when models change, variables are renamed, metrics are added, or new analysis is performed. 3. At session end: verify `memory.md` reflects all changes made. 4. Never let memory files go stale. |
| **Literature Synthesis** | Analyse and compare sources on volatility forecasting for thesis writing. | 1. Summarise each source's main contribution. 2. Group by theme (RV theory, HAR models, macro-volatility linkage, ML approaches). 3. Identify agreements, contradictions, and gaps. 4. Synthesise into cohesive narrative supporting the research questions. |
| **Academic Tone Refinement** | Convert informal language into formal academic prose. | 1. Remove AI cliches and filler phrases (see CLAUDE.md prohibited list). 2. Use precise financial econometrics terminology. 3. Ensure objective, analytical, third-person tone. 4. Maintain clarity and brevity. |
| **Citation Management** | Add references and insert citations into the thesis. | 1. **ALWAYS add the reference to `references.bib` FIRST** before inserting any citation into `Final_Report.tex`. 2. Use BibTeX key format `AuthorYear` (e.g., `Corsi2009`, `BakerBloomDavis2016`). 3. Insert citation in LaTeX using `\cite{Key}` or `\citep{Key}`. 4. Never cite a study that does not have a corresponding entry in `references.bib`. 5. Verify the entry exists by reading `references.bib` before inserting. |

## Specialized Sub-Skills
- **Econometric Reporting:** Present regression output following academic conventions — coefficient tables, significance stars (*/**/***), HAC-robust standard errors in parentheses, goodness-of-fit statistics.
- **Three-Tier Classification:** Understand and modify the surprise classification system (Category 0 = in line, 1 = moderate surprise, 2 = large surprise) applied to FOMC, CPI, NFP, PPI, PCE, ADP, JOLTS, CLAIMS.
- **Tariff Dummy Construction:** Understand the WSS (Weighted Severity Score) framework from `tariff_wss_v2.xlsx` and the threshold (WSS >= 5) for the binary TARIFF dummy.
- **Adjusted Lag Specification:** Understand Model 5's RV_d adjustment logic — when the previous day is a macro/tariff event day, use the most recent prior non-event day's log-RV.
- **Random Forest Benchmarking:** Fit and evaluate sklearn RandomForestRegressor as an ML benchmark against OLS models, using identical features for apples-to-apples comparison. (Neural network removed — RF is the only ML benchmark.)
- **Cross-Model Comparison:** Structure comparison tables with IS and OOS metrics (R², Adj R², RMSE, MAE) and highlight best performers.
- **Statistical Testing:** Implement QLIKE loss, Diebold-Mariano tests, and Model Confidence Sets when requested.
- **Supervisor PDF Review:** Extract annotations from supervisor-annotated PDFs using PyMuPDF (`fitz`), identify highlighted sections and comments, and implement changes directly in `Final_Report.tex`.
- **LaTeX Equation Formatting:** Ensure all equations are standalone (`\begin{equation}...\end{equation}`), use `\noindent` for continuation, `\begin{split}` for multiline, `\frac{}{}` for fractions, proper math mode for variables in prose.
- **Cross-Asset Awareness:** Understand that GBP/USD (24hr) and XAU/USD (23hr) have longer sessions than SPX (6.5hr), producing mechanically higher daily RV via the squared-return summation in Equation 3.2.
- **Git/Overleaf Conflict Resolution:** When `Final_Report.tex` has merge conflicts from Overleaf sync, resolve by keeping correct content from each side (HEAD for correct GBP/XAU sessions and VIX figure, Overleaf for detailed Data Cleaning). Always commit the merge resolution before pushing.
- **Reference PDF Automation:** Run `download_references.py` to bulk-download open-access PDFs from `references.bib` via Crossref/Unpaywall/Semantic Scholar. Output in `reference_pdfs/`. Paywalled papers require UCD library access.

## Key Technical Conventions
- All OLS models: `sm.OLS().fit(cov_type="HAC", cov_kwds={"maxlags": 5})`
- Target variable: `y = log(RV)` (natural log of realised variance)
- HAR features: `RV_d` (1-day lag), `RV_w` (5-day rolling mean, lagged), `RV_m` (22-day rolling mean, lagged)
- In-sample cutoff (SPX): `CUTOFF = pd.Timestamp("2026-01-29")`
- OOS period (SPX): `2026-01-30` to `2026-03-20`
- GBP/USD sample: 2025-10-29 to 2026-03-26
- XAU/USD sample: 2025-12-04 to 2026-03-26
- Historical SPX sample: 2023-05-01 to 2023-10-31 (80:20 dynamic split)
- Variable naming: `_m1` (baseline), `_m2`, `_m3a`, `_m3b`, `_m4`, `_m5`, `_m6` (RF)
- Dummies with zero in-sample occurrences are excluded from estimation

## 60-Page Chapter Budget (for thesis writing tasks)

| Chapter | Budget | Status |
|:---|:---:|:---|
| Ch 1: Introduction | 7 pages | Drafted |
| Ch 2: Literature Review | 14 pages | Drafted |
| Ch 3: Methodology | 14 pages | Revised per supervisor feedback (Sections 3.1–3.5 updated) |
| Ch 4: Results | 16 pages | In progress — SPX models complete, OOS done |
| Ch 5: Discussion | 6 pages | Not started |
| Ch 6: Conclusion | 3 pages | Not started |
| **Total** | **60 pages** | |

1 page ≈ 350-400 words (Times New Roman 12pt, 1.5 spacing). Tables count toward page budget.
