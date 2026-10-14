# Banking Credit Risk & Financial Analytics

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6.1-orange.svg)](https://scikit-learn.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue.svg)](https://www.mysql.com/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Desktop-yellow.svg)](https://powerbi.microsoft.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end credit risk analytics and machine learning pipeline that predicts customer default on revolving credit card accounts, identifies high-risk behavioral segments, optimizes operational decision thresholds, and delivers interactive portfolio dashboards.

---

## 1. Project Overview & Business Problem

In retail credit card portfolios, customer default causes direct charge-off losses, while excessive collections alerts create customer friction and unnecessary operational overhead. 

* **The Core Business Problem**: Credit risk managers must identify which revolving credit card accounts will default in the subsequent month (`DEFAULT = 1`) to initiate early intervention (e.g., credit line reduction, proactive payment restructuring, or risk-targeted collections) without overwhelming operational teams with false-positive alerts.
* **The Portfolio Reality**: Default is inherently imbalanced (baseline default rate is **$22.12\%$** / $6,636$ defaults out of $30,000$ accounts). A naive model predicting zero defaults achieves $77.88\%$ accuracy while failing to prevent a single dollar of credit loss.
* **Project Objective**: Build a robust, leakage-free analytical framework combining exploratory analysis, enterprise SQL querying, custom risk feature engineering, cross-validated machine learning modeling, out-of-sample holdout test assessment, operational threshold calibration, and business intelligence reporting.

---

## 2. End-to-End Analytics Workflow

```
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│ 1. DATA VERIFICATION    │ ──> │ 2. DATA QUALITY/CLEAN   │ ──> │ 3. EDA & BUSINESS STATS │
│ - 30,000 client records │     │ - Code consolidation    │     │ - Repayment & balance   │
│ - 25 raw attributes     │     │ - 0 rows dropped        │     │ - 10 diagnostic figures │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
                                                                              │
                                                                              ▼
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│ 6. MACHINE LEARNING     │ <── │ 5. FEATURE ENGINEERING  │ <── │ 4. MYSQL 8.0 ANALYTICS  │
│ - 80/20 Stratified Split│     │ - 19 risk features      │     │ - Live MySQL Server     │
│ - 5-Fold Stratified CV  │     │ - Delinquency/Util/Mom. │     │ - 10 analytical queries │
│ - LR vs RF vs HistGB    │     │ - 44 total columns      │     │ - Account-level KPIs    │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
            │
            ▼
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│ 7. HOLDOUT EVALUATION   │ ──> │ 8. POWER BI DASHBOARD   │ ──> │ 9. BUSINESS INSIGHTS    │
│ - 6,000 sealed test set │     │ - 4 interactive pages   │     │ - Portfolio takeaways   │
│ - F1 threshold: τ*=0.56 │     │ - Dynamic DAX measures  │     │ - Operational policy    │
│ - Generalization check  │     │ - Dedicated data models │     │ - Production roadmap    │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
```

---

## 3. Dataset & Data Cleaning

The analysis is conducted on the benchmark **UCI Default of Credit Card Clients Dataset** ($30,000$ accounts observed across a 6-month historical billing and payment cycle from April to September).

* **Record Scale**: Exactly $30,000$ customers, $25$ base features, zero null values, zero duplicate IDs.
* **Target Variable**: `DEFAULT` ($1 = \text{Default in October}$, $0 = \text{Non-Default}$).
  * Non-Default ($0$): $23,364$ accounts ($77.88\%$)
  * Default ($1$): $6,636$ accounts ($22.12\%$)
* **Data Cleaning & Standardization**:
  * `EDUCATION`: Undocumented categories ($0, 5, 6$) consolidated into category $4$ (`Others`), affecting $345$ records without row deletion.
  * `MARRIAGE`: Undocumented category ($0$) consolidated into category $3$ (`Others`), affecting $54$ records.
  * Output saved to `data/processed/credit_risk_clean.csv`.

---

## 4. Exploratory Data Analysis & Business Insights

Deep exploratory analysis was conducted across customer profiles, statement trajectories, and repayment patterns, generating 10 visual diagnostics in `data/processed/figures/`:

1. **Delinquency Recency is the Strongest Early Warning**: A customer delayed by 1 month in September (`PAY_0 = 1`) exhibits a **$33.9\%$** default rate; a 2-month delay (`PAY_0 = 2`) escalates the default rate to **$69.1\%$** (compared to $12.8\%$ for on-time revolving accounts).
2. **Revolving Credit Limit Inversion**: Lower credit limit tiers ($<50\text{k}\text{ NT\$}$) show a **$34.1\%$** default rate, whereas accounts with credit limits $>500\text{k}\text{ NT\$}$ default at **$11.6\%$**.
3. **Cash Repayment Insufficiency**: Defaulting customers pay on average only **$16.4\%$** of their billed statement balance, compared to **$45.2\%$** for non-defaulting accounts.
4. **Statement Balance Trajectories**: Defaulters exhibit persistent balance carryover across all 6 months, whereas non-defaulters actively amortize revolving balances.

![Figure 06: Default Rate by Repayment Status](data/processed/figures/pay0_default_rate.png)

---

## 5. Enterprise MySQL 8.0 Analytics

The clean customer dataset was loaded into a live **MySQL 8.0.43** database instance (`credit_risk_db.credit_card_clients`), where 10 analytical SQL queries were executed to extract business metrics:

* **Query Suite Highlights**:
  * Portfolio exposure & balance summaries (`LIMIT_BAL`, `BILL_AMT1` to `BILL_AMT6`).
  * Delinquency transition matrices across consecutive payment cycles.
  * Revolving utilization band segmentation ($<20\%$, $20-50\%$, $50-80\%$, $>80\%$, Over-Limit).
  * Window-aggregated payment-to-bill compliance ratios.
* **Artifacts**: [`src/database.py`](src/database.py), [`sql/analytics_queries.sql`](sql/analytics_queries.sql), [`docs/sql_analytics.md`](docs/sql_analytics.md).

---

## 6. Feature Engineering

To capture non-linear behavioral signals, $19$ domain-specific credit risk features were engineered, expanding the dataset to **$44$ columns**:

| Feature Category | Engineered Features | Business & Predictive Rationale |
|---|---|---|
| **Delinquency Dynamics** | `RECENT_DELAY`, `CONSEC_DELAY`, `DELAY_MONTHS_COUNT`, `MAX_PAY_DELAY`, `DELINQUENCY_TREND` | Quantifies delay recency, consecutive missed cycles, total delinquent months, and worsening delinquency momentum. |
| **Credit Utilisation** | `UTIL1` to `UTIL6`, `AVG_UTIL`, `MAX_UTIL`, `OVER_LIMIT_FLAG` | Measures credit line strain, peak 6-month utilization, and over-limit status. |
| **Repayment Compliance** | `PAY_TO_BILL_1`, `TOTAL_PAY_TO_BILL`, `ZERO_PAY_COUNT` | Measures cash repayment adequacy relative to billed amounts and counts zero-payment months. |
| **Exposure Aggregation** | `AVG_BILL_AMT`, `AVG_PAY_AMT` | Averages financial exposure over the 6-month observation window. |

*Output dataset saved to `data/processed/credit_risk_features.csv` ($30,000 \times 44$, verified 0 nulls, 0 infs).*

---

## 7. Machine Learning Methodology & Model Selection

### Leakage-Free Validation Strategy:
* **Partitioning**: $80\%$ Training ($24,000$ records) and $20\%$ Holdout Test ($6,000$ records), stratified by the target `DEFAULT` ($22.12\%$ default rate in both subsets).
* **Pipeline Encapsulation**: Categorical encoding (`OneHotEncoder(drop='first')`) and continuous feature scaling (`StandardScaler`) were fitted **only inside cross-validation folds on training data**, preventing data leakage.
* **Primary Evaluation Metric**: **PR-AUC (Precision-Recall AUC / Average Precision)** was selected as the primary metric because it directly evaluates precision and recall on the minority default class without false inflation from the dominant non-default class. **ROC-AUC** was tracked as a secondary discrimination metric.

### Model Architectures Evaluated:
1. **Logistic Regression**: Linear baseline benchmark (`class_weight='balanced'`).
2. **Random Forest**: Non-linear ensemble benchmark capturing feature interactions (`class_weight='balanced'`, 150 estimators, max depth 12).
3. **HistGradientBoosting**: Histogram-based gradient boosted decision trees natively supporting non-linear split dynamics (`class_weight='balanced'`, 150 iterations, learning rate 0.08, max depth 6).

### 5-Fold Training Cross-Validation Comparison ($N = 24,000$):

| Model Architecture | Model Role | 5-Fold CV PR-AUC (Primary) | 5-Fold CV ROC-AUC | 5-Fold CV F1-Score | Selection Outcome |
|---|---|:---:|:---:|:---:|:---:|
| **Logistic Regression** | Linear Baseline Benchmark | $0.5210 \pm 0.0137$ | $0.7719 \pm 0.0078$ | $0.5295$ | Benchmark |
| **Random Forest** | Non-Linear Ensemble Benchmark | $0.5583 \pm 0.0044$ | $\mathbf{0.7843 \pm 0.0055}$ | $0.5443$ | Benchmark |
| **HistGradientBoosting** | Gradient-Boosted Tree Pipeline | $\mathbf{0.5607 \pm 0.0067}$ | $0.7836 \pm 0.0060$ | $\mathbf{0.5395}$ | **CHAMPION MODEL** |

> **Methodological Note**: `HistGradientBoosting` was selected as the **Champion Model** strictly based on having the highest mean training CV PR-AUC ($0.5607$) prior to evaluating the holdout test set.

![Figure 11: Cross-Validation Model Comparison](data/processed/figures/fig11_model_cv_comparison.png)

---

## 8. Out-of-Sample Holdout Test Evaluation ($N = 6,000$)

The finalized model pipelines were evaluated in a single test on the **sealed 6,000-record holdout test set** ($1,327$ actual defaults and $4,673$ non-defaults):

| Model Architecture | Test PR-AUC (Primary) | Test ROC-AUC | Test Accuracy (@ 0.50) | Test Precision (@ 0.50) | Test Recall (@ 0.50) | Test F1-Score (@ 0.50) | Brier Score | Log Loss |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Logistic Regression** | $0.5135$ | $0.7592$ | $75.32\%$ | $45.60\%$ | $60.14\%$ | $0.5187$ | 0.1884 | 0.5693 |
| **Random Forest** | $\mathbf{0.5566}$ | $0.7760$ | $\mathbf{79.18\%}$ | $\mathbf{52.82\%}$ | $55.01\%$ | $\mathbf{0.5389}$ | $\mathbf{0.1607}$ | $\mathbf{0.4974}$ |
| **HistGradientBoosting** *(Champion)* | $0.5549$ | $\mathbf{0.7794}$ | $75.82\%$ | $46.56\%$ | $\mathbf{63.23\%}$ | $0.5363$ | 0.1776 | 0.5375 |

### Generalization Assessment:
Comparing 5-fold training CV against the holdout test set shows small CV-to-test performance gaps ($-0.0058$ in PR-AUC; $-0.0042$ in ROC-AUC for Champion), providing no strong evidence of overfitting based on the observed results.

![Figure 16: Holdout Test ROC and PR Curves](data/processed/figures/fig16_final_test_roc_pr_curves.png)

---

## 9. Decision Threshold Analysis & Business Simulation

### F1-Optimized Operating Threshold ($\tau^* = 0.56$):
The standard $0.50$ classification threshold is arbitrary. Using strictly the training out-of-fold predictions, the operating cutoff $\mathbf{\tau^* = 0.56}$ was pre-selected to maximize the $F_1$-score ($0.5451$ on train OOF).

When evaluated on the holdout test set ($N=6,000$), the $\tau^* = 0.56$ cutoff provides major operational benefits:

| Policy Strategy | Decision Cutoff ($\tau$) | Accuracy | Precision | Recall (Default Capture) | F1-Score | True Positives (TP) | False Positives (FP) | False Negatives (FN) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **High Recall Policy** | $\tau = 0.40$ | $66.90\%$ | $37.42\%$ | $\mathbf{73.85\%}$ | $0.4967$ | $980$ | $1,639$ | $347$ |
| **Default Cutoff** | $\tau = 0.50$ | $75.82\%$ | $46.56\%$ | $63.23\%$ | $0.5363$ | $839$ | $963$ | $488$ |
| **F1-Optimized Threshold** | $\mathbf{\tau^* = 0.56}$ | $\mathbf{78.82\%}$ | $\mathbf{51.89\%}$ | $\mathbf{57.87\%}$ | $\mathbf{0.5472}$ | $\mathbf{768}$ | $\mathbf{712}$ | $\mathbf{559}$ |
| **High Precision Policy** | $\tau = 0.70$ | $81.82\%$ | $63.02\%$ | $43.03\%$ | $0.5114$ | $571$ | $335$ | $756$ |

* **Operational Impact**: Shifting from $\tau = 0.50$ to $\tau^* = 0.56$ increases precision from $46.56\%$ to **$51.89\%$** (+5.33 percentage points) and eliminates **251 false-positive alerts** ($963 \rightarrow 712$), dramatically reducing wasted collections effort while capturing **$57.87\%$** ($768$ accounts) of all defaulting balances.

![Figure 15: Confusion Matrices Comparison](data/processed/figures/fig15_final_test_confusion_matrices.png)

### Illustrative Business Cost Simulation:
*(Note: Represents an illustrative simulation scenario modeling operational trade-offs and does not represent actual bank ledger data).*
* Assumes illustrative unmitigated default loss of $33,750\text{ NT\$}$ per False Negative ($75\%$ LGD on mean balance) and illustrative operational outreach friction of $1,500\text{ NT\$}$ per False Positive alert.
* Net simulated portfolio savings at $\tau^* = 0.56$ reach **$24.85\text{ Million NT\$}$** ($55.5\%$ reduction in unmitigated loss).

---

## 10. Power BI Business Dashboard

The project includes an executive-ready **4-page interactive Power BI dashboard** backed by clean data models, dynamic DAX measures, and dedicated Power Query ingestion scripts in `powerbi/`:

```
┌────────────────────────────────────────────────────────────────────────┐
│ PAGE 1: Portfolio Credit Risk Overview                                  │
│ └── Total exposure ($5.02B), baseline default rate (22.12%), limit tier│
├────────────────────────────────────────────────────────────────────────┤
│ PAGE 2: Customer Profile & Repayment Risk                              │
│ └── Delinquency recency (PAY_0), age groups, education x marriage matrix│
├────────────────────────────────────────────────────────────────────────┤
│ PAGE 3: Credit Utilisation & Leverage Drivers                          │
│ └── Utilisation tiers, 6-month balance trends, cash payment ratios     │
├────────────────────────────────────────────────────────────────────────┤
│ PAGE 4: Machine Learning Performance & Decision Thresholds             │
│ └── Model comparison, F1 cutoff (0.56), confusion matrix, cost curve   │
└────────────────────────────────────────────────────────────────────────┘
```

* **Data Model**: Fact table `Fact_Credit_Clients` ($30,000$ rows) with partition flags, connected to `Dim_Model_Metrics` and `Dim_Threshold_Policies`.
* **DAX Measure Library**: Fully dynamic measures (`[Total Customers]`, `[Portfolio Default Rate]`, `[Active Delinquency Rate]`, `[Test Precision (0.56)]`, `[Test Recall (0.56)]`) without hardcoded constants.
* **Specification Guide**: Complete wireframes and setup guide available in [`docs/power_bi_dashboard.md`](docs/power_bi_dashboard.md).

---

## 11. Key Business Recommendations

1. **Implement Multi-Tier Risk Interventions**:
   * **Stage 1 (Pre-Delinquent / Early Alert — $\tau \in [0.40, 0.55]$)**: Trigger proactive SMS/email payment reminders and offer temporary credit limit freezes.
   * **Stage 2 (High Risk — $\tau \ge 0.56$)**: Initiate proactive collections outreach, restrict revolving credit lines, and offer structured amortization payment plans.
2. **Flag 1-Month Delay as High-Hazard**: A 1-month payment delay increases default hazard nearly 3-fold ($12.8\% \rightarrow 33.9\%$). Accounts entering `PAY_0 = 1` should be placed under active monitoring.
3. **Incorporate Cash-to-Bill Ratios in Underwriting**: Customers paying $<20\%$ of statement balances should face dynamic credit line ceilings.

---

## 12. Repository Structure

```
banking-credit-risk/
│
├── data/
│   ├── raw/                           # UCI raw credit card dataset (untouched)
│   └── processed/                     # Clean, feature-engineered, and Power BI CSVs
│       ├── credit_risk_clean.csv      # Cleaned baseline dataset (30,000 x 25)
│       ├── credit_risk_features.csv   # Feature-engineered dataset (30,000 x 44)
│       ├── powerbi_credit_risk_dataset.csv  # Enriched fact table for Power BI (30,000 x 54)
│       ├── powerbi_ml_metrics_summary.csv   # Model comparison table
│       ├── powerbi_threshold_tradeoffs.csv  # Operating threshold matrix
│       └── figures/                   # 18 publication-quality diagnostic charts
│
├── sql/
│   └── analytics_queries.sql          # 10 production MySQL 8.0 analytical queries
│
├── src/
│   ├── database.py                    # MySQL 8.0 ingestion and SQL execution pipeline
│   ├── feature_engineering.py         # 19 custom credit risk feature transformers
│   ├── model_training.py              # 5-fold Stratified CV, preprocessing & threshold tuning
│   ├── model_evaluation.py            # Holdout test set assessment & diagnostic figures
│   └── export_powerbi_data.py         # Power BI dataset export module
│
├── models/
│   ├── credit_risk_champion_model.joblib # Persisted HistGradientBoosting pipeline
│   ├── train_test_data.joblib            # Partitioned 24k train / 6k test sets
│   ├── test_predictions.csv              # Holdout test set model probability outputs
│   └── test_evaluation_results.json      # Machine-readable test evaluation metrics
│
├── powerbi/
│   ├── measures.dax                   # Complete dynamic DAX measure library
│   ├── power_query_m_scripts.m        # Power Query (M) pre-typed ingestion scripts
│   └── README.md                      # Power BI Desktop build and assembly guide
│
├── notebooks/
│   └── 02_eda.ipynb                   # Exploratory data analysis notebook
│
├── docs/
│   ├── eda_and_business_insights.md   # Phase 3 exploratory findings
│   ├── sql_analytics.md               # Phase 4 SQL execution documentation
│   ├── ml_modeling_and_evaluation.md  # Phase 6 ML CV modeling report
│   ├── model_evaluation_and_test_results.md # Phase 7 holdout test results report
│   ├── power_bi_dashboard.md          # Phase 8 4-page dashboard specification
│   ├── decisions.md                   # Architectural decision record (D-001 to D-033)
│   └── progress.md                    # Project milestone log (Phases 1–9)
│
├── requirements.txt                   # Python dependencies
└── README.md                          # Master project documentation
```

---

## 13. Setup & Reproduction Guide

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/your-username/banking-credit-risk.git
cd banking-credit-risk
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Data Processing & Feature Engineering
```bash
python src/feature_engineering.py
```

### 3. Run Machine Learning Training & Cross-Validation
```bash
python src/model_training.py
```

### 4. Run Holdout Test Set Evaluation
```bash
python src/model_evaluation.py
```

### 5. Export Datasets for Power BI
```bash
python src/export_powerbi_data.py
```

---

## 14. Limitations & Future Work

* **Observation Window**: The dataset spans 6 monthly billing cycles; incorporating multi-year macroeconomic data (interest rates, unemployment indices) would enhance macroeconomic stress-testing.
* **Alternative Architectures**: Exploring cost-sensitive neural networks or XGBoost/LightGBM with custom loss functions aligned with actual loss given default (LGD) curves.
* **Real-Time Scoring**: Deploying the champion pipeline via a lightweight REST API (FastAPI / Docker) for real-time transaction underwriting.

---

## 15. Portfolio Highlights & Interview Talking Points

* **Full-Stack Lifecycle**: Successfully executes every stage from raw data validation, SQL analytics, and feature engineering to ML modeling, threshold optimization, and executive Power BI dashboards.
* **Zero Data Leakage**: Enforces strict train/test separation with encapsulated sklearn pipelines and cross-validated threshold optimization strictly on training out-of-fold predictions.
* **Business-Centric ML**: Uses PR-AUC for imbalanced evaluation and translates probabilities into actionable threshold policies that reduce operational friction by $251$ false alarms.

