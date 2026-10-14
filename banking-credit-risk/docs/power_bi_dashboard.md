# Phase 8 — Power BI Business Dashboard Specification & Build Guide

## Project: Banking Credit Risk & Financial Analytics
**Date**: 2026-08-31  
**Module**: `src/export_powerbi_data.py` & Power BI Desktop Build Specifications

---

## 1. Executive Summary & Dashboard Purpose

This document provides the complete architecture, data model, DAX measure library, visual wireframes, and step-by-step build instructions for creating the 4-page interactive **Banking Credit Risk & Financial Analytics Dashboard** in Power BI Desktop.

### Primary Objectives:
1. **Portfolio Transparency**: Provide executive leadership with instant visibility into portfolio credit exposure, customer demographic distributions, and baseline default rates.
2. **Behavioral Diagnostics**: Equip risk analysts and underwriters with granular insights into delinquency recency, payment persistence, and revolving credit limit utilization.
3. **Machine Learning Explainability**: Transparently communicate model evaluation results, champion model selection rationale, and operating decision threshold trade-offs to non-technical stakeholders.
4. **Operational Actionability**: Quantify the trade-off between default capture rate (Recall) and collections outreach volume (Precision) across different risk policies.

---

## 2. Power BI Data Model & Architecture

The Power BI data model utilizes a clean, high-performance **star-like analytical schema** centered around the primary customer fact table and supported by model performance and threshold dimensions:

```
                  ┌──────────────────────────────────────────────┐
                  │          Fact_Credit_Clients                 │
                  │  (data/processed/powerbi_credit_risk_...csv) │
                  │  - N = 30,000 Rows (1 Row per Customer)     │
                  │  - Primary Key: ID                           │
                  │  - Key Attributes: SPLIT ('Train'/'Test')    │
                  │    DEMOGRAPHICS, DELINQUENCY, UTILISATION    │
                  │    CHAMPION_PRED_PROB (Test Only, N=6,000)   │
                  │    FLAGGED_AT_0_56 (Test Only, N=6,000)      │
                  └──────────────────────────────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
┌──────────────────────────────────┐           ┌──────────────────────────────────┐
│       Dim_Model_Metrics          │           │     Dim_Threshold_Policies       │
│ (powerbi_ml_metrics_summary.csv) │           │ (powerbi_threshold_tradeoffs.csv)│
│ - N = 3 Rows (Evaluated Models)  │           │ - N = 4 Rows (Operating Cutoffs) │
│ - Key: Model_Name / Model_ID     │           │ - Key: Threshold                 │
└──────────────────────────────────┘           └──────────────────────────────────┘
```

### Ingestion Source Files (Under `data/processed/`):
1. **`powerbi_credit_risk_dataset.csv`** ($30,000\text{ rows} \times 54\text{ columns}$): Enriched customer fact table containing baseline variables, human-readable labels, 19 engineered features, and test-partition prediction probabilities.
2. **`powerbi_ml_metrics_summary.csv`** ($3\text{ rows} \times 15\text{ columns}$): Comparative evaluation metrics across Logistic Regression, Random Forest, and HistGradientBoosting.
3. **`powerbi_threshold_tradeoffs.csv`** ($4\text{ rows} \times 14\text{ columns}$): Classification threshold comparison table ($\tau \in \{0.40, 0.50, 0.56, 0.70\}$) with confusion matrix counts and illustrative cost metrics.

---

## 3. Dynamic DAX Measure Library

All KPI cards and visual summaries are dynamically computed from data without hardcoded constants. Create a dedicated measure table `_Measures` and add the following DAX definitions:

```dax
// ==============================================================================
// 1. CORE PORTFOLIO MEASURES (Full Portfolio N = 30,000)
// ==============================================================================

Total Customers = 
COUNTROWS(Fact_Credit_Clients)

Total Defaulted Customers = 
CALCULATE(
    COUNTROWS(Fact_Credit_Clients),
    Fact_Credit_Clients[DEFAULT] = 1
)

Total Non-Default Customers = 
CALCULATE(
    COUNTROWS(Fact_Credit_Clients),
    Fact_Credit_Clients[DEFAULT] = 0
)

Portfolio Default Rate = 
DIVIDE([Total Defaulted Customers], [Total Customers], 0)

Total Credit Limit Exposure = 
SUM(Fact_Credit_Clients[LIMIT_BAL])

Average Credit Limit = 
AVERAGE(Fact_Credit_Clients[LIMIT_BAL])

Average Statement Balance = 
AVERAGE(Fact_Credit_Clients[AVG_BILL_AMT])

Average Monthly Payment = 
AVERAGE(Fact_Credit_Clients[AVG_PAY_AMT])

Average Credit Utilisation = 
AVERAGE(Fact_Credit_Clients[AVG_UTIL])

Average Payment-to-Bill Ratio = 
AVERAGE(Fact_Credit_Clients[PAY_TO_BILL_1])


// ==============================================================================
// 2. DELINQUENCY & RISK SEGMENT MEASURES
// ==============================================================================

Active Delinquent Accounts = 
CALCULATE(
    COUNTROWS(Fact_Credit_Clients),
    Fact_Credit_Clients[RECENT_DELAY] = 1
)

Active Delinquency Rate = 
DIVIDE([Active Delinquent Accounts], [Total Customers], 0)

Multi-Month Delayed Accounts = 
CALCULATE(
    COUNTROWS(Fact_Credit_Clients),
    Fact_Credit_Clients[CONSEC_DELAY] = 1
)

Over-Limit Accounts = 
CALCULATE(
    COUNTROWS(Fact_Credit_Clients),
    Fact_Credit_Clients[OVER_LIMIT_FLAG] = 1
)

Over-Limit Rate = 
DIVIDE([Over-Limit Accounts], [Total Customers], 0)


// ==============================================================================
// 3. MACHINE LEARNING & THRESHOLD MEASURES (Holdout Test Set N = 6,000 Only)
// ==============================================================================

Test Set Total Accounts = 
CALCULATE(
    COUNTROWS(Fact_Credit_Clients),
    Fact_Credit_Clients[SPLIT] = "Test"
)

Test Set Actual Defaults = 
CALCULATE(
    COUNTROWS(Fact_Credit_Clients),
    Fact_Credit_Clients[SPLIT] = "Test",
    Fact_Credit_Clients[DEFAULT] = 1
)

Test Set Baseline Default Rate = 
DIVIDE([Test Set Actual Defaults], [Test Set Total Accounts], 0)

Test Flagged High-Risk Accounts (0.56) = 
CALCULATE(
    COUNTROWS(Fact_Credit_Clients),
    Fact_Credit_Clients[SPLIT] = "Test",
    Fact_Credit_Clients[FLAGGED_AT_0_56] = 1
)

Test True Positives (0.56) = 
CALCULATE(
    COUNTROWS(Fact_Credit_Clients),
    Fact_Credit_Clients[SPLIT] = "Test",
    Fact_Credit_Clients[FLAGGED_AT_0_56] = 1,
    Fact_Credit_Clients[DEFAULT] = 1
)

Test False Positives (0.56) = 
CALCULATE(
    COUNTROWS(Fact_Credit_Clients),
    Fact_Credit_Clients[SPLIT] = "Test",
    Fact_Credit_Clients[FLAGGED_AT_0_56] = 1,
    Fact_Credit_Clients[DEFAULT] = 0
)

Test Precision (0.56) = 
DIVIDE([Test True Positives (0.56)], [Test Flagged High-Risk Accounts (0.56)], 0)

Test Recall (0.56) = 
DIVIDE([Test True Positives (0.56)], [Test Set Actual Defaults], 0)

Test F1-Score (0.56) = 
DIVIDE(
    2 * [Test Precision (0.56)] * [Test Recall (0.56)],
    [Test Precision (0.56)] + [Test Recall (0.56)],
    0
)
```

---

## 4. Detailed 4-Page Dashboard Specification

### Page 1 — Portfolio Credit Risk Overview

* **Objective**: Executive overview of portfolio volume, total financial exposure, and baseline credit risk.
* **Top Slicers**: `EDUCATION_LABEL`, `MARRIAGE_LABEL`, `LIMIT_BAL_TIER`.

| Visual # | Visual Title | Visual Type | Data Fields & Mappings | Business Question Answered |
|---|---|---|---|---|
| **V1.1** | **Executive KPI Cards** | Multi-Card / Cards | `[Total Customers]`, `[Total Defaulted Customers]`, `[Portfolio Default Rate]`, `[Total Credit Limit Exposure]`, `[Average Credit Limit]` | What is the total scale and baseline credit risk exposure of the card portfolio? |
| **V1.2** | **Portfolio Default Composition** | Donut Chart | **Legend**: `DEFAULT` ($0, 1$); **Values**: `[Total Customers]` | What proportion of cardholders default on their next payment? |
| **V1.3** | **Default Rate by Credit Limit Tier** | Clustered Column Chart | **X-Axis**: `LIMIT_BAL_TIER`; **Y-Axis**: `[Portfolio Default Rate]`; **Tooltip**: `[Total Customers]` | How does credit default risk vary across customer credit lines? |
| **V1.4** | **Customer Volume & Default Concentration by Education** | 100% Stacked Bar Chart | **Y-Axis**: `EDUCATION_LABEL`; **X-Axis**: `[Total Customers]`; **Legend**: `DEFAULT` | Which education segments represent the largest share of defaulted accounts? |
| **V1.5** | **Balance vs. Payment Exposure Matrix** | Table / Matrix | **Rows**: `LIMIT_BAL_TIER`; **Values**: `[Average Statement Balance]`, `[Average Monthly Payment]`, `[Average Credit Utilisation]` | Are higher credit tier accounts maintaining proportional payment volume? |

---

### Page 2 — Customer Profile & Repayment Risk

* **Objective**: Granular diagnosis of demographic risk profiles and delinquency persistence.
* **Top Slicers**: `SEX_LABEL`, `AGE_GROUP`, `EDUCATION_LABEL`.

| Visual # | Visual Title | Visual Type | Data Fields & Mappings | Business Question Answered |
|---|---|---|---|---|
| **V2.1** | **Risk Diagnosis KPIs** | Card Row | `[Active Delinquent Accounts]`, `[Active Delinquency Rate]`, `[Multi-Month Delayed Accounts]` | What volume of customers currently display active payment delinquency? |
| **V2.2** | **Default Rate by Recent Payment Delay Status (`PAY_0`)** | Clustered Column Chart | **X-Axis**: `PAY_0_LABEL`; **Y-Axis**: `[Portfolio Default Rate]` | How sharply does default probability escalate when a payment is delayed by 1 or 2 months? |
| **V2.3** | **Default Rate Trajectory Across Age Groups** | Line Chart | **X-Axis**: `AGE_GROUP`; **Y-Axis**: `[Portfolio Default Rate]` | Are younger or older cardholders at higher risk of default? |
| **V2.4** | **Risk Concentration by Education $\times$ Marital Status** | Matrix Heatmap | **Rows**: `EDUCATION_LABEL`; **Columns**: `MARRIAGE_LABEL`; **Values**: `[Portfolio Default Rate]` | Which combined demographic intersections exhibit the highest default rates? |
| **V2.5** | **Default Hazard by Delinquency Persistence** | Bar Chart | **X-Axis**: `DELAY_MONTHS_COUNT` ($0\text{ to }6$); **Y-Axis**: `[Portfolio Default Rate]` | How does chronic multi-month delinquency impact default rate? |

---

### Page 3 — Credit Utilisation & Leverage Drivers

* **Objective**: Analyze the relationship between revolving credit utilization, statement balance trends, and cash repayment sufficiency.
* **Top Slicers**: `AVG_UTIL_TIER`, `LIMIT_BAL_TIER`, `RECENT_DELAY`.

| Visual # | Visual Title | Visual Type | Data Fields & Mappings | Business Question Answered |
|---|---|---|---|---|
| **V3.1** | **Leverage & Compliance KPIs** | Card Row | `[Average Credit Utilisation]`, `[Over-Limit Accounts]`, `[Over-Limit Rate]`, `[Average Payment-to-Bill Ratio]` | What is the overall leverage and repayment compliance health of the portfolio? |
| **V3.2** | **Default Rate by Credit Utilisation Tier** | Clustered Bar Chart | **Y-Axis**: `AVG_UTIL_TIER`; **X-Axis**: `[Portfolio Default Rate]` | At what revolving utilization threshold does credit default risk sharply increase? |
| **V3.3** | **Statement Balance vs. Payment Amount Distribution** | Scatter Plot | **X-Axis**: `AVG_BILL_AMT`; **Y-Axis**: `[AVG_PAY_AMT]`; **Legend**: `DEFAULT` | Do defaulting customers pay proportionally less cash relative to their statement balances? |
| **V3.4** | **6-Month Balance & Payment Momentum Trends** | Line Chart | **X-Axis**: Months ($t-5\text{ to }t$); **Y-Axis**: Average Balance & Payment; **Legend**: `DEFAULT` | How do balance accumulation and cash repayment trajectories diverge between defaulting and non-defaulting accounts? |
| **V3.5** | **Top Risk Drivers (Permutation Feature Importance)** | Horizontal Bar Chart | **Y-Axis**: Feature Name; **X-Axis**: Importance Score (PR-AUC Drop) | Which behavioral and financial indicators provide the strongest predictive power? |

---

### Page 4 — Machine Learning Performance & Decision Thresholds

* **Objective**: Transparently communicate model evaluation metrics, champion selection rationale, decision threshold trade-offs, and operational workload implications.
* **Data Sources**: `Dim_Model_Metrics`, `Dim_Threshold_Policies`, and `Fact_Credit_Clients` (`SPLIT = 'Test'`).

| Visual # | Visual Title | Visual Type | Data Fields & Mappings | Business Question Answered |
|---|---|---|---|---|
| **V4.1** | **Champion Model Test KPIs (Holdout $N = 6,000$)** | Card Banner | Champion: `HistGradientBoosting`<br>Test PR-AUC: `0.5549`<br>F1-Optimized Cutoff: `τ* = 0.56`<br>Precision: `51.89%`<br>Recall: `57.87%`<br>Alerts Reduced: `-251` | How does the champion machine learning model perform on unseen holdout test customers? |
| **V4.2** | **Model Architecture Comparison Table** | Table | **Columns**: `Model_Name`, `Train_CV_PR_AUC_Mean`, `Test_PR_AUC`, `Test_ROC_AUC`, `Test_Precision_050`, `Test_Recall_050`, `Test_F1_050`, `Is_Champion` | Why was `HistGradientBoosting` selected over Logistic Regression and Random Forest? |
| **V4.3** | **Decision Threshold Trade-Off Analysis** | Table / Matrix | **Columns**: `Policy_Name`, `Threshold`, `Precision`, `Recall`, `F1_Score`, `True_Positives_TP`, `False_Positives_FP`, `False_Negatives_FN` | How does adjusting the classification cutoff shift the trade-off between default capture and operational alert volume? |
| **V4.4** | **Precision vs. Recall vs. F1 Threshold Curve** | Line Chart | **X-Axis**: `Threshold` ($0.10\text{ to }0.90$); **Y-Axis**: Precision, Recall, F1-Score lines; **Reference Line**: $\tau^* = 0.56$ | Where is the optimal operational balance for collections capacity? |
| **V4.5** | **Illustrative Business Cost Simulation Callout** | Callout Box / Cards | Illustrative Net Savings at $\tau^* = 0.56$: **24.85M NT$** ($55.5\%$ reduction in unmitigated loss). Clearly labeled *Illustrative Business Scenario*. | What is the simulated financial impact under hypothetical collections outreach vs default loss trade-offs? |

---

## 5. Step-by-Step Power BI Desktop Build Instructions

1. **Step 1 — Launch & Ingest Datasets**:
   - Open Power BI Desktop $\rightarrow$ Click **Get Data** $\rightarrow$ **Text/CSV**.
   - Load [`powerbi_credit_risk_dataset.csv`](../data/processed/powerbi_credit_risk_dataset.csv) (Rename table to `Fact_Credit_Clients`).
   - Load [`powerbi_ml_metrics_summary.csv`](../data/processed/powerbi_ml_metrics_summary.csv) (Rename table to `Dim_Model_Metrics`).
   - Load [`powerbi_threshold_tradeoffs.csv`](../data/processed/powerbi_threshold_tradeoffs.csv) (Rename table to `Dim_Threshold_Policies`).

2. **Step 2 — Configure DAX Measures**:
   - Click **Enter Data** to create a blank table named `_Measures`.
   - Add all DAX formulas from Section 3.

3. **Step 3 — Build Visual Canvas (4 Pages)**:
   - Configure Page Dimensions: $16:9$ ($1280 \times 720\text{ px}$).
   - Set Theme Color Palette:
     - Primary Navy: `#1E3A8A`
     - Risk Highlight (Default): `#E11D48`
     - Safe / Non-Default: `#10B981`
     - Accent Blue: `#3B82F6`
     - Neutral Slate: `#64748B`
   - Build Pages 1 through 4 following Section 4 wireframes.

4. **Step 4 — Save Power BI File**:
   - Save report as `banking_credit_risk_dashboard.pbix` in the project root.

---

## 6. Interview Defense & Business Talking Points

When presenting this dashboard in data analyst or risk analytics interviews:
1. **"Why use PR-AUC as the primary metric?"**: In imbalanced credit portfolios ($22.12\%$ default rate), standard accuracy is misleading (a naive classifier achieves $77.88\%$ accuracy while catching 0 defaults). PR-AUC focuses on precision and recall without false inflation from true negatives.
2. **"Why was HistGradientBoosting chosen as the Champion?"**: Selected based on the highest 5-fold cross-validation PR-AUC ($0.5607$) strictly on training data prior to testing. On the holdout test set, it maintained strong discrimination ($0.7794$ ROC-AUC) and achieved the highest default capture rate ($63.23\%$ at 0.50 cutoff).
3. **"Why calibrate the operating threshold to $\tau^* = 0.56$?"**: Standard $0.50$ produces excessive false alarms ($963$ false positives on test set). Shifting to the $F_1$-optimized cutoff ($\tau^* = 0.56$) raises precision from $46.56\%$ to $51.89\%$, eliminating $251$ false alarms while retaining $57.87\%$ of all actual defaulters.

