# Analytical Decisions Log

## Project: Banking Credit Risk & Financial Analytics

This document records every significant analytical decision made during the project.
Each entry explains the problem, evidence, treatment chosen, alternatives considered, and limitations.
This log is intended to help explain the project's methodology during interviews.

---

## Decision Log

### D-001 — File Loading Strategy
**Phase**: 1 — Dataset Verification  
**Date**: 2026-08-30

**Context**: The UCI dataset file is a `.xls` format with a double-header structure. Row 0 contains generic variable codes (X1–X23, Y). Row 1 contains descriptive column names (LIMIT_BAL, SEX, EDUCATION, etc.).

**Decision**: Load the file using `pd.read_excel(..., header=1)` to use the descriptive names as column headers.

**Rationale**: Using descriptive names makes the code and analysis immediately readable and self-documenting. The UCI variable codes are preserved in `docs/dataset.md` for cross-reference.

**Alternatives considered**: Using row 0 (X1–X23) as headers — rejected because it makes code harder to read and less interview-friendly.

**Limitations**: None significant. Both header rows are available in the raw file.

---

### D-002 — Target Column Naming
**Phase**: 1 — Dataset Verification  
**Date**: 2026-08-30

**Context**: The target column name as read from the file header is `"default payment next month"` (a long string with spaces). The UCI documentation calls it simply `Y`.

**Decision**: Retain the original name `"default payment next month"` during loading. Rename to `DEFAULT` in the processed dataset for convenience.

**Rationale**: The original name is self-documenting. Renaming to `DEFAULT` in processed data avoids quoting issues in SQL and code while remaining unambiguous.

**Alternatives considered**: Keep long name throughout — rejected for SQL compatibility reasons.

---

### D-003 — Undocumented EDUCATION Codes (0, 5, 6)
**Phase**: 1 — Dataset Verification (flagged; decision deferred to Phase 2)  
**Date**: 2026-08-30 (flagged)

**Context**: EDUCATION column contains codes 0, 5, and 6 which are not defined in the UCI documentation. Official codes are 1=Graduate, 2=University, 3=High school, 4=Others.  
- Code 0: 14 records  
- Code 5: 280 records  
- Code 6: 51 records  
- Total: 345 records (1.15%)

**Status**: 🔶 Deferred to Phase 2 for investigation and formal treatment decision.

---

### D-004 — Undocumented MARRIAGE Code (0)
**Phase**: 1 — Dataset Verification (flagged; decision deferred to Phase 2)  
**Date**: 2026-08-30 (flagged)

**Context**: MARRIAGE column contains code 0 which is not defined in the UCI documentation. Official codes are 1=Married, 2=Single, 3=Others.  
- Code 0: 54 records (0.18%)

**Status**: 🔶 Deferred to Phase 2 for investigation and formal treatment decision.

---

### D-005 — PAY Column Code -2
**Phase**: 1 — Dataset Verification (flagged; decision deferred to Phase 2)  
**Date**: 2026-08-30 (flagged)

**Context**: PAY columns (PAY_0 through PAY_6) contain the value -2, which is not in the original UCI documentation. The documentation lists codes -1 to 8. The value -2 appears in all six PAY columns.

**Preliminary interpretation**: Research and community analysis of this dataset consistently interpret -2 as "no consumption" (the credit card was not used that month, or the balance was fully cleared with no new charges). This is distinct from -1 ("paid duly" — card was used and the full amount was paid).

**Status**: 🔶 Deferred to Phase 2 for formal decision and documentation.

---

### D-006 — Negative BILL_AMT Values
**Phase**: 1 — Dataset Verification (flagged; decision deferred to Phase 2)  
**Date**: 2026-08-30 (flagged)

**Context**: BILL_AMT columns contain negative values (590–688 per column). A negative bill statement balance in credit card accounting typically means the customer has a credit balance — for example, they overpaid a prior statement or received a refund/cashback.

**Preliminary assessment**: These values are financially valid, not data errors. They should NOT be removed or zeroed.

**Status**: 🔶 Deferred to Phase 2 for formal confirmation and documentation.

---

### D-007 — Class Imbalance Strategy
**Phase**: 1 — Dataset Verification (flagged; decision deferred to Phase 6)  
**Date**: 2026-08-30 (flagged)

**Context**: Default rate is 22.12% (6,636 of 30,000 records). This represents a moderate class imbalance.

**Preliminary assessment**: Options include class weighting in models, threshold tuning post-training, or resampling (SMOTE on training set only). Given the imbalance is moderate (not extreme), class weighting is likely the preferred first approach.

**Status**: 🔶 Deferred to Phase 6 for formal decision after EDA and feature engineering.

---

*Entries will be added throughout the project as decisions are made.*

---

### D-008 — AGE Range: No Treatment Required
**Phase**: 2 — Data Quality + Cleaning
**Date**: 2026-08-30

**Context**: AGE ranges from 21 (minimum) to 79 (maximum).
- 15 records with age > 70
- 67 records with age == 21 (minimum possible)
- 0 records with age < 18 or > 100

**Decision**: Retain all AGE values. No treatment required.

**Rationale**: The range 21-79 is entirely plausible for credit card holders in Taiwan in 2005. Age 21 was the legal age of civil majority in Taiwan at that time, making it the natural minimum for credit cardholders. Age 79 is uncommon but not impossible.

**Limitations**: No corroborating identity data to verify individual ages.

---

### D-009 — LIMIT_BAL: No Treatment Required
**Phase**: 2 — Data Quality + Cleaning
**Date**: 2026-08-30

**Context**: Credit limit ranges from 10,000 to 1,000,000 NT$ (mean 167,484 NT$).
- No zero or negative values
- 81 distinct credit limit levels (multiples of 10,000)
- 1st percentile = 10,000; 99th percentile = 500,000

**Decision**: Retain all LIMIT_BAL values. No treatment required.

**Rationale**: All values are positive and within a plausible range for a Taiwanese credit card portfolio in 2005. The round-number nature of credit limits (multiples of 10,000) reflects standard banking practice.

---

### D-010 — PAY_AMT Zero Values: Retain
**Phase**: 2 — Data Quality + Cleaning
**Date**: 2026-08-30

**Context**: Zero payment amounts range from 5,249 (PAY_AMT1, 17.5%) to 7,173 (PAY_AMT6, 23.9%). No negative payment amounts found.

**Decision**: Retain all zero PAY_AMT values as genuine records of "no payment made."

**Rationale**: A zero payment is financially valid and highly informative — it indicates the customer made no payment in that month, which is strongly correlated with delinquency and default. Treating zeros as missing would lose this signal entirely.

---

### D-011 — BILL_AMT Negative Values: Retain (Formal Decision)
**Phase**: 2 — Data Quality + Cleaning
**Date**: 2026-08-30

**Context**: 590-688 negative bill amounts per column (2.0-2.3%). Minimum value: -339,603 NT$.

**Decision**: Retain all negative BILL_AMT values as financially valid credit balances.

**Rationale**: In credit card accounting, a negative statement balance is a credit balance — arising from overpayment or refunds. This is standard and valid. The pattern is consistent across all 6 BILL_AMT columns, supporting the interpretation as genuine data rather than entry errors.

**Limitations**: No way to distinguish overpayment from refund/cashback credits. Both interpretations are valid retentions.

---

### D-012 — PAY Code -2: Retain (Formal Decision)
**Phase**: 2 — Data Quality + Cleaning
**Date**: 2026-08-30

**Context**: Code -2 in PAY columns (2,759 to 4,895 records per column, 9-16% of data). Not in UCI documentation.

**Decision**: Retain -2 as a valid, separate repayment status category distinct from -1 and 0.

**Evidence**: Cross-check of PAY_0=-2 with BILL_AMT1 shows:
- 209 records with negative BILL_AMT1 (credit balance — consistent with overpayment)
- 694 with zero BILL_AMT1 (no balance)
- 1,856 with positive BILL_AMT1 (balance exists but no new charges)

This pattern is consistent with "no new consumption" rather than "paid in full" (-1) or "revolving credit used" (0).

**Limitations**: The exact definition remains undocumented by UCI. Community consensus is used.

---

*Phase 2 complete. Next decisions will be added in Phase 3.*

---

### D-013 — Age Group Segmentation Strategy
**Phase**: 3 — EDA + Business Analysis
**Date**: 2026-08-30

**Context**: Age spans 21 to 79. Granular 5-year groupings show clear inflection points: default rates are elevated at 21–25 (26.7%) and 61+ (26.8%), while stabilizing in the core 31–35 group (19.4%).

**Decision**: For broad demographic risk tables and heatmaps, use 4 life-stage segments: Young Adults (21–30), Core Working Age (31–40), Mature Working Age (41–50), and Older / Senior (51+). For granular analysis, use 8 five-year bins.

**Rationale**: Aligns with retail credit lifecycle stages while retaining sufficient sample size in each bin for statistically reliable default rate estimates.

---

### D-014 — Credit Limit Segmentation Boundaries
**Phase**: 3 — EDA + Business Analysis
**Date**: 2026-08-30

**Context**: Credit limits range from 10,000 to 1,000,000 NT$. The distribution is heavily clustered at round increments (50K, 100K, 200K, 300K, 500K).

**Decision**: Segment credit limits into 6 tiers: `<=50K`, `50K–100K`, `100K–200K`, `200K–300K`, `300K–500K`, `>500K`. For 3-tier cross-tabulation, collapse into Low (`<=100K`), Mid (`100K–300K`), and High (`>300K`).

**Rationale**: Mirrors standard banking tiering and captures the sharp risk gradient (default rate drops monotonically from 31.8% in `<=50K` to 11.2% in `>500K`).

---

### D-015 — Delinquency Definitions and Measurement
**Phase**: 3 — EDA + Business Analysis
**Date**: 2026-08-30

**Context**: Delinquency can be evaluated on multiple dimensions (occurrence, recency, duration, and severity).

**Decision**: Formally define five distinct delinquency metrics for EDA:
1. *Any Delinquency*: `PAY_i >= 1` in any of the 6 months (33.6% of portfolio; 42.7% default rate).
2. *Delinquency Streak / Months Count*: Sum of months where `PAY_i >= 1` (0 to 6 months).
3. *Maximum Payment Delay*: Highest delay code observed across 6 months (`max(PAY_i)` clipped at 0).
4. *Recent Delinquency*: Payment delay in the two most recent cycles (`PAY_0 >= 1` OR `PAY_2 >= 1`; 24.2% of portfolio; 49.5% default rate).
5. *Persistent / Consecutive Delinquency*: Payment delay in both recent cycles (`PAY_0 >= 1` AND `PAY_2 >= 1`; 13.3% of portfolio; 57.8% default rate).

**Rationale**: Differentiates between one-off payment friction and systemic repayment distress.

---

### D-016 — Payment-to-Bill Ratio Formulation & Handling of Edge Cases
**Phase**: 3 — EDA + Business Analysis
**Date**: 2026-08-30

**Context**: Evaluating repayment sufficiency requires comparing payments (`PAY_AMT1`) against billing balances (`BILL_AMT1`). However, statement balances can be zero (no debt) or negative (credit balance).

**Decision**:
- Ratio is strictly defined as `PAY_AMT1 / BILL_AMT1`.
- Computed *only* for records where `BILL_AMT1 > 0` (27,402 accounts; 91.3% of portfolio).
- Excluded from ratio calculation: `BILL_AMT1 == 0` (undefined; 2,008 accounts) and `BILL_AMT1 < 0` (credit balance; 590 accounts).
- Use medians and categorized payment tiers (`0%`, `<5%`, `5–30%`, `30–100%`, `>100%`) rather than arithmetic means to avoid distortion from customers who significantly overpaid.
- This calculation is strictly an EDA exploratory helper and is NOT part of the official modeling feature set at this stage.

**Rationale**: Prevents division-by-zero errors and mathematically misleading ratios while accurately capturing payment sufficiency.

---

### D-017 — Credit Utilisation Definition
**Phase**: 3 — EDA + Business Analysis
**Date**: 2026-08-30

**Context**: Credit utilisation indicates how close a customer is to maxing out their assigned credit limit.

**Decision**: Defined as `BILL_AMT1 / LIMIT_BAL` evaluated on accounts with `BILL_AMT1 > 0` and `LIMIT_BAL > 0`. Binned into 5 tiers: Low (`<30%`), Moderate (`30–60%`), High (`60–90%`), Critical (`90–100%`), and Over-limit (`>100%`).

**Rationale**: Standard financial metric in credit risk scoring; provides direct insight into customer leverage and borrowing capacity.

---

### D-018 — Relational Schema and Indexing Architecture
**Phase**: 4 — MySQL + SQL Analytics
**Date**: 2026-08-31

**Context**: Ingesting the 30,000-record dataset into an analytical SQL database requires robust column constraints, appropriate primary key enforcement, and indexes to support complex groupings and aggregations.

**Decision**: 
- Create single analytical table `credit_card_clients` with `ID` as integer primary key.
- Apply non-nullable integer constraints across all 25 features.
- Create single-column indexes on high-frequency filtering fields (`DEFAULT`, `PAY_0`, `EDUCATION`, `AGE`, `LIMIT_BAL`).
- Create composite index `idx_composite_risk` on `(PAY_0, LIMIT_BAL, DEFAULT)` for high-risk segment queries.

**Rationale**: Guarantees fast analytical query execution and mirrors production data warehouse table design.

---

### D-019 — SQL Analytical Query Suite Design & Window Functions
**Phase**: 4 — MySQL + SQL Analytics
**Date**: 2026-08-31

**Context**: SQL analysis must answer key business questions across portfolio baselines, demographic segments, delinquency persistence, credit utilisation, and exposure ranking without unnecessary query complexity.

**Decision**:
- Construct 10 targeted analytical queries in `sql/analytics_queries.sql`.
- Use ANSI-compliant SQL constructs (`CASE` expressions, `CTE`s, `UNION ALL`, `GROUP BY`, and Window functions like `DENSE_RANK() OVER (...)`).
- Ensure all queries are cross-compatible between MySQL 8.0+ and SQLite 3.25+.

**Rationale**: Demonstrates advanced analytical SQL capabilities (CTEs, window functions, aggregations) while delivering direct actionable answers for banking stakeholders.

---

### D-020 — Real MySQL 8.0.43 Server Execution & Direct Verification
**Phase**: 4 — MySQL + SQL Analytics
**Date**: 2026-08-31

**Context**: Earlier development testing used an embedded SQLite runner because MySQL credentials were not configured. To genuinely support production analytics and resume claims, execution was run against a live MySQL Server instance.

**Decision**:
- Read credentials securely from local `.env` via `URL.create` in SQLAlchemy (avoiding URL encoding/special character parsing issues with passwords).
- Target live **MySQL Server 8.0.43** on `localhost:3306` (service `MYSQL80`).
- Create database `credit_risk_db` and table `credit_card_clients`.
- Ingest and verify all 30,000 clean records (25 columns).
- Execute and validate all 10 analytical queries directly against MySQL 8.0.43.

**Rationale**: Guarantees authentic enterprise validation on MySQL 8.0 with zero syntax or dialect discrepancies.

---

### D-021 -- Delinquency Dynamics Feature Set and Non-Negative Delay Scaling
**Phase**: 5 -- Feature Engineering
**Date**: 2026-08-31

**Context**: Repayment status columns (PAY_0 through PAY_6) contain codes -2 (No consumption), -1 (Paid in full), 0 (Revolving credit), and 1..8 (Months delayed). A raw difference PAY_0 - PAY_6 would produce arithmetic artifacts (e.g. transitioning from -2 to 0 would yield +2, erroneously suggesting a 2-month delinquency worsening).

**Decision**:
- Construct MAX_PAY_DELAY: clip(lower=0).max(axis=1) (maps non-delinquent -2, -1, 0 to 0, and delay months 1..8 to their true delay magnitude).
- Construct DELAY_MONTHS_COUNT: sum(PAY_i >= 1) across all 6 months.
- Construct RECENT_DELAY: (PAY_0 >= 1) | (PAY_2 >= 1).
- Construct CONSEC_DELAY: (PAY_0 >= 1) & (PAY_2 >= 1).
- Construct DELINQUENCY_TREND: clip(PAY_0, 0) - clip(PAY_6, 0) on the non-negative delay scale.

**Rationale**: Eliminates non-linear code distortion while capturing delinquency severity, persistence, recency, and directional momentum.

---

### D-022 -- Credit Utilisation and Peak Leverage Formulations
**Phase**: 5 -- Feature Engineering
**Date**: 2026-08-31

**Context**: Measuring revolving credit leverage requires comparing billed balances to assigned credit limits across single-month and multi-month horizons.

**Decision**:
- Construct UTIL1: BILL_AMT1 / LIMIT_BAL (most recent utilisation).
- Construct AVG_BILL_AMT: mean(BILL_AMT1..6).
- Construct AVG_UTIL: AVG_BILL_AMT / LIMIT_BAL.
- Construct MAX_UTIL: max(BILL_AMT1..6) / LIMIT_BAL.
- Construct OVER_LIMIT_FLAG: (max(BILL_AMT1..6) > LIMIT_BAL).astype(int).
- Verified that LIMIT_BAL >= 10,000 NT$ across all 30,000 records, making division mathematically safe without zero-division errors. Negative statement balances are preserved to reflect true credit balance states.

**Rationale**: Provides linear and tree models with both point-in-time and cumulative exposure metrics without artificial clipping distortions.

---

### D-023 -- Payment-to-Bill Ratios and Explicit Indicator Flags for Zero and Credit Balances
**Phase**: 5 -- Feature Engineering
**Date**: 2026-08-31

**Context**: Payment-to-bill ratios (PAY_AMT / BILL_AMT) are undefined or non-interpretable when BILL_AMT == 0 (no positive debt due) or BILL_AMT < 0 (credit/overpaid balance). Blindly assigning 1.0 would falsely classify zero-balance accounts as having paid an active statement liability.

**Decision**:
- When BILL_AMT1 > 0: PAY_TO_BILL_1 = (PAY_AMT1 / BILL_AMT1).clip(0, 2.0) (winsorized at 200% to suppress extreme cash overpayment spikes).
- When BILL_AMT1 == 0: PAY_TO_BILL_1 = 0.0 with explicit binary flag ZERO_BILL_1 = 1.
- When BILL_AMT1 < 0: PAY_TO_BILL_1 = 0.0 with explicit binary flag CREDIT_BAL_1 = 1.
- Construct TOTAL_PAY_TO_BILL: sum(PAY_AMT1..6) / sum(max(BILL_AMT1..6, 0)) for cumulative positive debt obligations (winsorized at 2.0; 0.0 if zero positive debt).
- Construct ZERO_PAY_COUNT: sum(PAY_AMTi == 0) tracking cash payment inactivity frequency.

**Rationale**: Preserves analytical validity, avoids division-by-zero, and equips downstream models with explicit structural indicators to differentiate zero/credit balance accounts from delinquent non-payers.

---

### D-024 -- Chronological Balance/Payment Momentum and Scale Transformations
**Phase**: 5 -- Feature Engineering
**Date**: 2026-08-31

**Context**: Assessing whether a customer financial distress or repayment capacity is expanding or contracting over time.

**Decision**:
- Construct BILL_AMT_CHANGE: BILL_AMT1 - BILL_AMT6 (September balance minus April balance). Positive = debt accumulation; negative = debt reduction.
- Construct PAY_AMT_CHANGE: PAY_AMT1 - PAY_AMT6 (September payment minus April payment). Positive = payment increase; negative = payment contraction.
- Construct LIMIT_BAL_LOG: log(LIMIT_BAL) to normalize the right-skewed credit limit distribution.

**Rationale**: Encodes 6-month financial trajectory and stabilizes scale variance for linear and gradient-based estimators.
---

### D-025 — Stratified 80/20 Train/Test Partition & Training-Only Cross-Validation Protocol
**Phase**: 6 — Machine Learning  
**Date**: 2026-08-31

**Context**: Ensuring reliable out-of-sample generalization and preventing data leakage across model exploration and hyperparameter validation.

**Decision**:
- Partitioned dataset into 80% Training Set ($N=24,000$, 22.12% Default) and 20% Test Set ($N=6,000$, 22.12% Default) using `StratifiedShuffleSplit` / `train_test_split` with `random_state=42`.
- Sealed the 6,000-row test set in `models/train_test_data.joblib` without computing any evaluation metrics.
- Executed 5-fold Stratified Cross-Validation strictly within the 24,000 training records.

**Rationale**: Guarantees zero data leakage and establishes an honest, untainted holdout benchmark for final model evaluation.

---

### D-026 — Model-Specific Class Imbalance Handling
**Phase**: 6 — Machine Learning  
**Date**: 2026-08-31

**Context**: Target class distribution is imbalanced (77.88% non-default vs 22.12% default). Different estimator architectures support different class-weighting implementations.

**Decision**:
- For `LogisticRegression`: Utilized `class_weight='balanced'` within the standard-scaled pipeline.
- For `RandomForestClassifier`: Utilized `class_weight='balanced'` within the ensemble.
- For `HistGradientBoostingClassifier`: Utilized native `class_weight='balanced'` in Scikit-Learn 1.6.1.
- Avoided synthetic oversampling (SMOTE) to preserve discrete delinquency codes and eliminate risk of artificial training-sample leakage.

**Rationale**: Cost-sensitive weighting appropriately penalizes default misclassifications without corrupting the underlying empirical feature distributions.

---

### D-027 — Machine Learning Pipeline Architecture & Fold-Level Preprocessing Encapsulation
**Phase**: 6 — Machine Learning  
**Date**: 2026-08-31

**Context**: Preprocessing operations (standardization and one-hot encoding) must not leak statistics across cross-validation folds or into the test partition.

**Decision**:
- Wrapped all transformers and estimators inside `sklearn.pipeline.Pipeline`.
- Applied `ColumnTransformer` with `OneHotEncoder(handle_unknown='ignore', drop='first')` on categorical columns (`SEX`, `EDUCATION`, `MARRIAGE`).
- Applied `StandardScaler` on continuous numerical columns for Logistic Regression.
- Passed numerical/ordinal columns through directly for tree and gradient boosting models.
- All transformers were fitted strictly on the training partition of each CV fold.

**Rationale**: Fully isolates fold-level feature statistics, preventing data snooping and variance leakage.

---

### D-028 — Primary Metric Prioritization (PR-AUC) & Training-Only Out-of-Fold Threshold Calibration
**Phase**: 6 — Machine Learning  
**Date**: 2026-08-31

**Context**: In imbalanced credit risk classification, accuracy is misleading. Additionally, arbitrary default probability cutoffs ($\tau = 0.50$) fail to balance false negatives (unmitigated default loss) against false positives (operational alert volume).

**Decision**:
- Selected **PR-AUC (Average Precision)** as the primary ranking metric for model selection, with **ROC-AUC** as the secondary discrimination metric.
- Evaluated models using out-of-fold validation probabilities (`y_prob_oof`) across all 24,000 training records.
- Selected `HistGradientBoostingClassifier` as the champion model (Top CV PR-AUC = 0.5607 ± 0.0067; CV ROC-AUC = 0.7836 ± 0.0060).
- Calibrated the optimal decision threshold $\tau^*$ on training out-of-fold predictions only, finding $\tau^* = 0.56$ which maximizes $F_1$-score at 0.5451 (Precision: 0.4789, Recall: 0.6327).
- Persisted champion model pipeline to `models/credit_risk_champion_model.joblib`.

**Rationale**: Aligns model selection and operational cutoffs directly with banking portfolio economics without using test set performance.
---

### D-029 — Holdout Test Set Evaluation Protocol & Generalization Verification
**Phase**: 7 — Model Evaluation & Test Assessment  
**Date**: 2026-08-31

**Context**: Conducting the final out-of-sample test evaluation without data leakage or post-hoc model tuning.

**Decision**:
- Evaluated all 3 fitted model pipelines on the sealed 6,000-record test set ($N=6,000$, 22.12% Default baseline).
- Measured PR-AUC, ROC-AUC, Brier score, log loss, and classification metrics at default ($\tau=0.50$) and pre-selected optimal ($\tau^*=0.56$) thresholds.
- Verified that performance gaps between 5-fold training CV and holdout test set were minimal (PR-AUC gap $< 0.008$; ROC-AUC gap $< 0.013$), confirming zero overfitting.

**Rationale**: Provides empirical proof of generalization on unseen customer data.

---

### D-030 — Decision Threshold Policy & Illustrative Financial Cost Simulation
**Phase**: 7 — Model Evaluation & Test Assessment  
**Date**: 2026-08-31

**Context**: Translating predictive probabilities into actionable operational policies and business cost savings.

**Decision**:
- Established the primary operational policy at the pre-calibrated threshold $\mathbf{\tau^* = 0.56}$, achieving 51.89% precision and 57.87% recall on the holdout test set (F1 = 0.5472), eliminating 251 false-positive alerts relative to the standard 0.50 threshold.
- Formulated an illustrative financial cost scenario modeling the trade-off between unmitigated default losses (False Negatives) and operational outreach friction (False Positives), demonstrating substantial potential net cost savings across operating policies.

**Rationale**: Connects technical ML metrics directly to bank portfolio risk management and operational workload constraints.
---

### D-031 — Power BI Data Model Architecture & Dedicated Export Pipeline
**Phase**: 8 — Power BI Dashboard  
**Date**: 2026-08-31

**Context**: Structuring datasets for business intelligence consumption without duplicating customer records or introducing schema complexity.

**Decision**:
- Implemented `src/export_powerbi_data.py` to produce 3 clean, dedicated CSV tables:
  1. `data/processed/powerbi_credit_risk_dataset.csv` ($30,000$ rows): Primary fact table with human-readable demographic labels, engineered risk features, and an explicit `SPLIT` flag (`'Train'` / `'Test'`). Test-set prediction probabilities (`CHAMPION_PRED_PROB`) and binary flags (`FLAGGED_AT_0_56`) are populated exclusively for the 6,000 holdout test observations.
  2. `data/processed/powerbi_ml_metrics_summary.csv` ($3$ rows): Comparative model performance table.
  3. `data/processed/powerbi_threshold_tradeoffs.csv` ($4$ rows): Operational cutoff matrix ($0.40, 0.50, 0.56, 0.70$).

**Rationale**: Maintains single-source-of-truth analytical rigor, avoids record duplication, and guarantees that test ML evaluation metrics evaluate strictly over the holdout partition.

---

### D-032 — Dynamic DAX Measure Architecture & ML Reporting Protocol
**Phase**: 8 — Power BI Dashboard  
**Date**: 2026-08-31

**Context**: Ensuring all portfolio KPIs, delinquency rates, and ML metrics respond dynamically to user filter context without hardcoding constants.

**Decision**:
- Defined explicit DAX measures for all KPIs (Total Customers, Total Defaults, Default Rate, Total Exposure, Average Limit, Utilisation, and Test Precision/Recall).
- Designated $\tau^* = \mathbf{0.56}$ as the **F1-Optimized Operating Threshold** in all visual headers and matrices.
- Segregated the illustrative financial cost simulation from model-selection criteria to maintain clear business communication.

**Rationale**: Adheres to business intelligence best practices, making the dashboard fully interactive, technically sound, and interview-explainable.
---

### D-033 — Final Project Documentation & GitHub Portfolio Standards
**Phase**: 9 — Finalization & Portfolio Polish  
**Date**: 2026-08-31

**Context**: Assembling a cohesive, professional, interview-ready repository narrative spanning all 8 prior analytical phases.

**Decision**:
- Structured the root `README.md` to communicate the full end-to-end data lifecycle: Data Cleaning $\rightarrow$ EDA $\rightarrow$ MySQL 8.0 Integration $\rightarrow$ Feature Engineering $\rightarrow$ Machine Learning $\rightarrow$ Holdout Test Assessment $\rightarrow$ Power BI Dashboard $\rightarrow$ Business Insights.
- Preserved exact methodological distinctions: `HistGradientBoosting` selected as Champion strictly via training 5-fold CV PR-AUC ($0.5607$), $\tau^* = \mathbf{0.56}$ designated as the **F1-Optimized Operating Threshold**, and financial cost figures clearly framed as an **Illustrative Business Simulation Scenario**.
- Replaced all local/machine-specific absolute URIs with repository-relative paths to ensure complete cross-platform portability on GitHub.

**Rationale**: Guarantees technical defensibility, transparency, and portfolio excellence for data analytics and credit risk interviews.
