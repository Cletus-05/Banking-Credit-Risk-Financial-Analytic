# Dataset Documentation

## Overview

| Property | Value |
|---|---|
| **Dataset Name** | Default of Credit Card Clients |
| **Source** | UCI Machine Learning Repository |
| **URL** | https://archive.ics.uci.edu/ml/datasets/default+of+credit+card+clients |
| **Original Paper** | Yeh, I. C., & Lien, C. H. (2009). The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients. *Expert Systems with Applications*, 36(2), 2473–2480. |
| **License** | Creative Commons Attribution 4.0 International (CC BY 4.0) |
| **Year Collected** | April–September 2005 |
| **Geography** | Taiwan |
| **Institution** | Chung Hua University / Tamkang University |

---

## File Information

| Property | Value |
|---|---|
| **Filename** | `default of credit card clients.xls` |
| **Format** | Microsoft Excel 97–2003 Workbook (.xls) |
| **File Size** | ~5.3 MB |
| **Location** | `data/raw/default of credit card clients.xls` |
| **Header Structure** | Row 0: variable codes (X1–X23, Y); Row 1: descriptive column names; Data: rows 2–30001 |

> **Note on file format**: The dataset was distributed as an `.xls` file. Row 0 contains the UCI variable codes (X1–X23, Y). Row 1 contains descriptive English names. This project loads the file using `header=1` (row index 1) so that the descriptive names are used as column headers. The UCI variable codes are preserved in this documentation for cross-reference.

---

## Dataset Shape (Verified)

| Metric | Value |
|---|---|
| **Total Rows** | 30,000 |
| **Total Columns** | 25 |
| **Feature Columns** | 23 (X1–X23) |
| **Identifier** | 1 (ID) |
| **Target Column** | 1 (`default payment next month`) |

---

## Column Mapping

The source documentation uses generic variable codes X1–X23 and Y. This project uses the descriptive names from the dataset's own header row.

| UCI Code | Column Name | Type | Description |
|---|---|---|---|
| — | `ID` | Integer | Customer identifier (1–30000) |
| X1 | `LIMIT_BAL` | Integer | Credit limit in NT dollars |
| X2 | `SEX` | Integer (categorical) | Gender: 1=Male, 2=Female |
| X3 | `EDUCATION` | Integer (categorical) | Education level (see codes below) |
| X4 | `MARRIAGE` | Integer (categorical) | Marital status (see codes below) |
| X5 | `AGE` | Integer | Age in years |
| X6 | `PAY_0` | Integer (categorical) | Repayment status September 2005 |
| X7 | `PAY_2` | Integer (categorical) | Repayment status August 2005 |
| X8 | `PAY_3` | Integer (categorical) | Repayment status July 2005 |
| X9 | `PAY_4` | Integer (categorical) | Repayment status June 2005 |
| X10 | `PAY_5` | Integer (categorical) | Repayment status May 2005 |
| X11 | `PAY_6` | Integer (categorical) | Repayment status April 2005 |
| X12 | `BILL_AMT1` | Integer | Bill statement amount September 2005 (NT$) |
| X13 | `BILL_AMT2` | Integer | Bill statement amount August 2005 (NT$) |
| X14 | `BILL_AMT3` | Integer | Bill statement amount July 2005 (NT$) |
| X15 | `BILL_AMT4` | Integer | Bill statement amount June 2005 (NT$) |
| X16 | `BILL_AMT5` | Integer | Bill statement amount May 2005 (NT$) |
| X17 | `BILL_AMT6` | Integer | Bill statement amount April 2005 (NT$) |
| X18 | `PAY_AMT1` | Integer | Payment amount September 2005 (NT$) |
| X19 | `PAY_AMT2` | Integer | Payment amount August 2005 (NT$) |
| X20 | `PAY_AMT3` | Integer | Payment amount July 2005 (NT$) |
| X21 | `PAY_AMT4` | Integer | Payment amount June 2005 (NT$) |
| X22 | `PAY_AMT5` | Integer | Payment amount May 2005 (NT$) |
| X23 | `PAY_AMT6` | Integer | Payment amount April 2005 (NT$) |
| Y | `default payment next month` | Integer (binary) | Target: 1=Default, 0=No default |

> **Note on PAY column naming**: The dataset skips `PAY_1` — the most recent month uses `PAY_0` (September 2005), followed by `PAY_2` (August 2005), `PAY_3` (July 2005), etc. This numbering is preserved from the original source.

---

## Categorical Code Definitions

### EDUCATION (X3)
As documented in the original paper:

| Code | Meaning | Count |
|---|---|---|
| 1 | Graduate school | 10,585 |
| 2 | University | 14,030 |
| 3 | High school | 4,917 |
| 4 | Others | 123 |
| 0 | Undocumented | 14 |
| 5 | Undocumented | 280 |
| 6 | Undocumented | 51 |

> **Data quality note**: Codes 0, 5, and 6 are not defined in the original UCI documentation. Together they represent 345 records (1.15% of the dataset). These are flagged as undocumented/unknown categories and will be investigated in Phase 2.

### MARRIAGE (X4)
As documented in the original paper:

| Code | Meaning | Count |
|---|---|---|
| 1 | Married | 13,659 |
| 2 | Single | 15,964 |
| 3 | Others | 323 |
| 0 | Undocumented | 54 |

> **Data quality note**: Code 0 is not defined in the original UCI documentation. It represents 54 records (0.18%). Will be investigated in Phase 2.

### SEX (X2)

| Code | Meaning | Count |
|---|---|---|
| 1 | Male | 11,888 |
| 2 | Female | 18,112 |

> No unexpected codes found.

### PAY_0 through PAY_6 (X6–X11)
As documented in the original paper:

| Code | Meaning |
|---|---|
| -2 | No consumption (balance paid in full, no bill) |
| -1 | Paid in full / pay duly |
| 0 | Use of revolving credit (minimum payment made) |
| 1 | Payment delayed 1 month |
| 2 | Payment delayed 2 months |
| 3 | Payment delayed 3 months |
| 4 | Payment delayed 4 months |
| 5 | Payment delayed 5 months |
| 6 | Payment delayed 6 months |
| 7 | Payment delayed 7 months |
| 8 | Payment delayed 8 months or more |

> **Data quality note**: The value `-2` does not appear in the original UCI documentation (which lists -1 to 8). However, it is present in the data (it appears in all PAY columns). Research suggests `-2` means no consumption / full balance carried over. This will be formally investigated in Phase 2. Additionally, `PAY_5` and `PAY_6` do not contain a value of `1` in this dataset, which may indicate no customers had exactly 1 month delay during those months.

---

## Numerical Column Summary (Verified)

### LIMIT_BAL (Credit Limit)
| Statistic | Value |
|---|---|
| Min | 10,000 NT$ |
| Max | 1,000,000 NT$ |
| Mean | 167,484 NT$ |

### AGE
| Statistic | Value |
|---|---|
| Min | 21 years |
| Max | 79 years |
| Mean | 35.49 years |
| Median | 34 years |

### BILL_AMT1–6 (Monthly Bill Statements)
| Column | Min | Max | Mean | Negative Values | Zero Values |
|---|---|---|---|---|---|
| BILL_AMT1 | -165,580 | 964,511 | 51,223 | 590 | 2,008 |
| BILL_AMT2 | -69,777 | 983,931 | 49,179 | 669 | 2,506 |
| BILL_AMT3 | -157,264 | 1,664,089 | 47,013 | 655 | 2,870 |
| BILL_AMT4 | -170,000 | 891,586 | 43,263 | 675 | 3,195 |
| BILL_AMT5 | -81,334 | 927,171 | 40,311 | 655 | 3,506 |
| BILL_AMT6 | -339,603 | 961,664 | 38,872 | 688 | 4,020 |

> **Data quality note**: Negative bill amounts are financially valid — they represent credit balances (e.g., a customer overpaid or received a refund). Zero bill amounts represent months with no outstanding balance. These are NOT errors and will be retained.

### PAY_AMT1–6 (Monthly Payments Made)
| Column | Min | Max | Mean | Negative Values | Zero Values |
|---|---|---|---|---|---|
| PAY_AMT1 | 0 | 873,552 | 5,664 | 0 | 5,249 |
| PAY_AMT2 | 0 | 1,684,259 | 5,921 | 0 | 5,396 |
| PAY_AMT3 | 0 | 896,040 | 5,226 | 0 | 5,968 |
| PAY_AMT4 | 0 | 621,000 | 4,826 | 0 | 6,408 |
| PAY_AMT5 | 0 | 426,529 | 4,799 | 0 | 6,703 |
| PAY_AMT6 | 0 | 528,666 | 5,216 | 0 | 7,173 |

> Zero payment amounts are financially valid — they indicate no payment was made in that month. No negative values found, which is expected.

---

## Target Variable

| Label | Description | Count | Percentage |
|---|---|---|---|
| 0 | No default | 23,364 | 77.88% |
| 1 | Default | 6,636 | 22.12% |

> **Class imbalance noted**: The dataset has a moderate class imbalance (~78% / ~22%). This is a realistic and expected distribution for a credit default dataset. The imbalance is not extreme but must be handled appropriately in Phase 6 (Machine Learning). Accuracy alone would be a misleading metric.

---

## Data Quality — High-Level Summary

| Check | Result |
|---|---|
| Missing values | **None** (0 nulls across all 30,000 × 25) |
| Duplicate IDs | **None** |
| Duplicate full rows | **None** |
| SEX codes | Clean (only 1 and 2) |
| EDUCATION codes | **3 undocumented codes** (0, 5, 6) — 345 records |
| MARRIAGE codes | **1 undocumented code** (0) — 54 records |
| PAY codes | **-2 not documented** in UCI spec — present in all PAY columns |
| BILL_AMT negative values | Present — **financially valid** (credit balances) |
| PAY_AMT negative values | **None** — as expected |
| AGE range | 21–79 — plausible for credit card holders |
| LIMIT_BAL range | 10,000–1,000,000 NT$ — plausible |

All data quality issues identified here will be formally investigated and treated in **Phase 2 (Data Quality + Cleaning)**.

---

## Dataset Context and Limitations

### Context
- Data covers a cohort of Taiwanese credit card holders from April to September 2005
- The target variable reflects whether a customer defaulted on their payment in **October 2005**
- All monetary values are in **New Taiwan Dollars (NT$)**; 1 USD ≈ 32 NT$ (approximate 2005 rate)
- The dataset is widely used in academic research and ML benchmarking

### Known Limitations

1. **Temporal limitation**: Data is from 2005 in Taiwan. Credit risk patterns, economic conditions, and lending practices may differ significantly from modern contexts or other geographies. Results should not be directly generalized.

2. **No macroeconomic context**: The dataset includes no external economic variables (interest rates, GDP growth, unemployment). Macro factors are known to influence credit default rates.

3. **Definition ambiguity — PAY codes**: The -2 code and the precise distinction between -1 and 0 in PAY columns are ambiguous in the original documentation. The -2 code appears to mean "no consumption" but is not formally defined in the original UCI page.

4. **Definition ambiguity — EDUCATION/MARRIAGE 0 codes**: Codes 0 for EDUCATION and MARRIAGE have no documented meaning. They may represent "other", "undisclosed", or data errors.

5. **Snapshot dataset**: This is a single cross-sectional snapshot, not a longitudinal panel. Customers cannot be tracked beyond October 2005.

6. **No behavioral or external features**: Variables such as income, employment status, credit score, number of credit cards, or loan history are not included.

7. **Potential selection bias**: The population reflects customers of a specific Taiwanese bank during a specific period, which may not represent all credit card holders.

---

## Source Citation

Yeh, I. C., & Lien, C. H. (2009). The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients. *Expert Systems with Applications*, 36(2), 2473–2480. https://doi.org/10.1016/j.eswa.2007.12.020

UCI ML Repository: https://archive.ics.uci.edu/ml/datasets/default+of+credit+card+clients
