# Project Progress Log

## Project: Banking Credit Risk and Financial Analytics

**Started**: 2026-08-30  
**Completed**: 2026-08-31

---

## Current Status

| Field | Value |
|---|---|
| **Current Phase** | Phase 9 — Final Project Documentation & Portfolio Polish |
| **Status** | COMPLETE (End-to-End Project Finished) |
| **Deliverables** | Verified Dataset, MySQL Analytics, ML Pipeline, Holdout Evaluation, Power BI Data Model & Dashboard Architecture, Comprehensive Documentation |

---

## Phase Log

### Phase 1 — Dataset Verification
**Status**: Complete | **Completed**: 2026-08-30
- 30,000 rows x 25 columns verified from UCI repository; zero nulls, zero duplicates; 22.12% default rate baseline.

### Phase 2 — Data Quality + Cleaning
**Status**: Complete | **Completed**: 2026-08-30
- EDUCATION undocumented codes (0, 5, 6) consolidated to 4 (Others, 345 records); MARRIAGE code 0 consolidated to 3 (Others, 54 records).
- Output: `data/processed/credit_risk_clean.csv` (30,000 x 25).

### Phase 3 — EDA + Business Analysis
**Status**: Complete | **Completed**: 2026-08-30
- Deep exploratory data analysis across demographics, repayment history, revolving utilization, and payment compliance.
- Artifacts: `notebooks/02_eda.ipynb`, `eda_stats.py`, 10 diagnostic figures (`fig01` to `fig10`), `docs/eda_and_business_insights.md`.

### Phase 4 — MySQL + SQL Analytics
**Status**: Complete | **Completed**: 2026-08-31
- Ingested 30,000 records into live MySQL Server 8.0.43 on localhost:3306 (`credit_risk_db.credit_card_clients`).
- Executed 10 analytical SQL queries covering portfolio KPIs, delinquency recency, utilization bands, and payment-to-bill compliance.
- Artifacts: `src/database.py`, `sql/analytics_queries.sql`, `docs/sql_analytics.md`.

### Phase 5 — Feature Engineering
**Status**: Complete | **Completed**: 2026-08-31
- Engineered 19 risk features across Delinquency, Utilisation, Repayment Compliance, and Momentum.
- Output: `data/processed/credit_risk_features.csv` (30,000 rows x 44 columns; 0 nulls, 0 infs, target unchanged).

### Phase 6 — Machine Learning Training & Model Selection
**Status**: Complete | **Completed**: 2026-08-31
- 80/20 stratified split: 24,000 training records / 6,000 sealed holdout test records.
- 5-fold Stratified CV on training data comparing Logistic Regression, Random Forest, and HistGradientBoosting.
- Selected `HistGradientBoostingClassifier` as Champion based on highest training CV PR-AUC ($0.5607 \pm 0.0067$).
- Calibrated operating threshold $\tau^* = 0.56$ strictly on training out-of-fold predictions.
- Artifacts: `src/model_training.py`, `models/credit_risk_champion_model.joblib`, `models/train_test_data.joblib`, Figures 11–14, `docs/ml_modeling_and_evaluation.md`.

### Phase 7 — Model Evaluation & Test Assessment
**Status**: Complete | **Completed**: 2026-08-31
- Single out-of-sample evaluation on sealed 6,000-record test set: Champion Test PR-AUC = 0.5549, Test ROC-AUC = 0.7794.
- F1-Optimized Threshold $\tau^* = 0.56$ test results: Precision = 51.89%, Recall = 57.87%, F1 = 0.5472 (reducing false-positive alert volume by 251 vs default 0.50 cutoff).
- Illustrative business cost simulation demonstrating operational trade-offs.
- Artifacts: `src/model_evaluation.py`, `models/test_evaluation_results.json`, Figures 15–18, `docs/model_evaluation_and_test_results.md`.

### Phase 8 — Power BI Dashboard Architecture & Datasets
**Status**: Complete | **Completed**: 2026-08-31
- Prepared 3 dedicated, verified CSV datasets: `powerbi_credit_risk_dataset.csv` (30,000 rows), `powerbi_ml_metrics_summary.csv`, and `powerbi_threshold_tradeoffs.csv`.
- Complete 4-page dashboard specification, visual mappings, dynamic DAX measures library, and Power Query M ingestion scripts.
- Artifacts: `src/export_powerbi_data.py`, `powerbi/measures.dax`, `powerbi/power_query_m_scripts.m`, `docs/power_bi_dashboard.md`.

### Phase 9 — Finalization & Portfolio Polish
**Status**: Complete | **Completed**: 2026-08-31
- End-to-end repository cleanup, relative link validation, and production of the master `README.md`.
- Appended Decision D-033 to `docs/decisions.md`.
