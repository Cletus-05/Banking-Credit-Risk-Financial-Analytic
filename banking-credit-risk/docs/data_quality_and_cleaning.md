# Data Quality & Cleaning

## Project: Banking Credit Risk & Financial Analytics
**Phase 2 — Completed: 2026-08-30**

---

## Overview

This document records every data quality issue found in the raw dataset,  
the evidence gathered, and the treatment applied.

**Raw file**: `data/raw/default of credit card clients.xls`  
**Processed file**: `data/processed/credit_risk_clean.csv`  
**Rows dropped**: 0  
**New missing values introduced**: 0  
**Total cleaning operations**: 2 remappings (399 records total)

---

## Dataset Quality Summary

| Check | Result |
|---|---|
| Total rows | 30,000 |
| Total columns | 25 |
| Missing values | **0** (confirmed across all 30,000 x 25 cells) |
| Duplicate IDs | **0** |
| Duplicate full rows | **0** |
| SEX codes | Clean — only 1 and 2 |
| EDUCATION codes | 3 undocumented codes — **treated** |
| MARRIAGE codes | 1 undocumented code — **treated** |
| PAY codes (-2) | Not in UCI docs — **retained with documentation** |
| BILL_AMT negatives | **Retained** (financially valid credit balances) |
| PAY_AMT negatives | None — as expected |
| AGE range | 21-79 — **plausible, no treatment needed** |
| LIMIT_BAL range | 10,000-1,000,000 NT$ — **plausible, no treatment needed** |

---

## Issue 1 — File Format: Double-Header XLS

**Problem**:  
The raw file `default of credit card clients.xls` has two header rows:
- Row 0: UCI variable codes (X1-X23, Y)
- Row 1: Descriptive English names (LIMIT_BAL, SEX, EDUCATION, ..., default payment next month)

**Evidence**:  
Direct inspection of raw file with `pd.read_excel(..., header=None, nrows=5)`.

**Treatment**:  
Load with `pd.read_excel(..., header=1)` to use descriptive names as column headers.

**Why this treatment**:  
Descriptive names make all subsequent code, SQL queries, and analysis self-documenting.  
The UCI codes are preserved in `docs/dataset.md` for cross-reference.

**Decision reference**: D-001

---

## Issue 2 — Target Column Name Contains Spaces

**Problem**:  
The target column is named `"default payment next month"` — contains spaces,  
which causes quoting issues in SQL and awkward code.

**Evidence**:  
Column `df.columns[24]` = `'default payment next month'`.

**Treatment**:  
Renamed to `DEFAULT` in all processed outputs and downstream scripts.

**Why this treatment**:  
- `DEFAULT` is concise, SQL-safe, and unambiguous
- The original meaning is fully preserved

**Alternatives considered**:  
- Keep original name: rejected for SQL incompatibility
- Use `TARGET`: less descriptive

**Decision reference**: D-002

---

## Issue 3 — EDUCATION: Undocumented Codes 0, 5, 6

**Problem**:  
The EDUCATION column contains codes not defined in the UCI documentation.

**Evidence**:

| Code | Documented Meaning | Count | Default Rate |
|---|---|---|---|
| 1 | Graduate school | 10,585 | 19.2% |
| 2 | University | 14,030 | 23.7% |
| 3 | High school | 4,917 | 25.2% |
| 4 | Others | 123 | 5.7% |
| **0** | **Undocumented** | **14** | **0.0%** |
| **5** | **Undocumented** | **280** | **6.4%** |
| **6** | **Undocumented** | **51** | **15.7%** |

Total undocumented: **345 records (1.15% of dataset)**

**Treatment**:  
Remap codes 0, 5, and 6 to code 4 (`Others`).

After cleaning:
| Code | Meaning | Count |
|---|---|---|
| 1 | Graduate school | 10,585 |
| 2 | University | 14,030 |
| 3 | High school | 4,917 |
| 4 | Others (includes former 0, 5, 6) | 468 |

**Why this treatment**:  
- Code 4 is explicitly defined as "Others" in the UCI documentation — it is the  
  semantically correct catch-all for unknown or undisclosed education categories
- Dropping affected records would cause unnecessary data loss (only 1.15%)  
  and could introduce a subtle selection bias
- The undocumented codes cannot be meaningfully distinguished from one another  
  (their sample sizes are too small for separate reliable analysis)
- Merging creates a clean 4-level ordinal structure

**Alternatives considered**:  
1. **Drop rows with undocumented codes**: Rejected — small but unnecessary data loss
2. **Keep as separate categories**: Rejected — no documented meaning; would create false distinctions
3. **Impute with mode (University)**: Rejected — no evidence to support this assumption

**Limitations**:  
- The true meaning of codes 0, 5, 6 is unknown. If they encode a real category  
  (e.g., vocational school), this remapping loses that nuance.
- Impact is minimal at 1.15%.

**Decision reference**: D-003

---

## Issue 4 — MARRIAGE: Undocumented Code 0

**Problem**:  
The MARRIAGE column contains code 0, which has no documented meaning.

**Evidence**:

| Code | Documented Meaning | Count | Default Rate |
|---|---|---|---|
| 1 | Married | 13,659 | 23.5% |
| 2 | Single | 15,964 | 20.9% |
| 3 | Others | 323 | 26.0% |
| **0** | **Undocumented** | **54** | **9.3%** |

Total undocumented: **54 records (0.18% of dataset)**

**Treatment**:  
Remap code 0 to code 3 (`Others`).

After cleaning:
| Code | Meaning | Count |
|---|---|---|
| 1 | Married | 13,659 |
| 2 | Single | 15,964 |
| 3 | Others (includes former 0) | 377 |

**Why this treatment**:  
- Code 3 (`Others`) is the natural home for unknown or undisclosed marital status
- Only 54 records (0.18%) — negligible impact
- The default rate difference between code 0 (9.3%) and code 3 (26.0%) is notable  
  but with only 54 records there is insufficient statistical basis to treat separately

**Alternatives considered**:  
1. **Drop rows**: Rejected — 54 records with valid feature data
2. **Keep as separate category**: Rejected — no documented meaning
3. **Impute with mode (Single)**: Rejected — no evidence

**Decision reference**: D-004

---

## Issue 5 — PAY Columns: Code -2 (Undocumented)

**Problem**:  
The repayment status columns (PAY_0 through PAY_6) contain the value -2,  
which does not appear in the original UCI documentation (documented range: -1 to 8).

**Evidence**:

| Column | Count of -2 | % of rows |
|---|---|---|
| PAY_0 | 2,759 | 9.2% |
| PAY_2 | 3,782 | 12.6% |
| PAY_3 | 4,085 | 13.6% |
| PAY_4 | 4,348 | 14.5% |
| PAY_5 | 4,546 | 15.2% |
| PAY_6 | 4,895 | 16.3% |

**Cross-check analysis** (PAY_0 = -2 vs BILL_AMT1):
| BILL_AMT1 | Count |
|---|---|
| Negative (credit balance) | 209 |
| Zero (no balance) | 694 |
| Positive (balance exists) | 1,856 |

**Interpretation**:  
Code -2 represents "no new consumption" — the credit card had no new charges  
in that billing cycle. This is distinct from:
- -1 (card used and full balance paid)
- 0 (revolving credit used, minimum payment made)

The presence of positive BILL_AMT1 for PAY_0 = -2 (1,856 records) is consistent  
with a balance carried over from prior months with no new charges.

**Treatment**:  
Retain -2 as a valid, separate repayment status category. Do NOT merge with -1 or 0.

**Why this treatment**:  
- -2 is quantitatively distinguishable from -1 and 0 in the data
- Merging with -1 would conflate "no consumption" with "paid in full" — different behaviours
- Merging with 0 would be financially incorrect (opposite meaning)
- This interpretation is widely used in academic research on this dataset
- Dropping would remove up to 4,895 records (16.3%)

**Alternatives considered**:  
1. **Merge with -1**: Rejected — distinct customer behaviour
2. **Merge with 0**: Rejected — opposite financial meaning
3. **Drop rows with -2**: Rejected — affects too many records

**Note on PAY_5 and PAY_6**: These columns contain no value of 1 (1-month delay),  
meaning no customer had exactly a 1-month delay in those months in this dataset.  
This is not an error — it is simply the empirical distribution.

**Decision reference**: D-005

---

## Issue 6 — BILL_AMT: Negative Values

**Problem**:  
The bill statement amount columns contain negative values.

**Evidence**:

| Column | Negative Count | Min Value | % of rows |
|---|---|---|---|
| BILL_AMT1 | 590 | -165,580 | 2.0% |
| BILL_AMT2 | 669 | -69,777 | 2.2% |
| BILL_AMT3 | 655 | -157,264 | 2.2% |
| BILL_AMT4 | 675 | -170,000 | 2.3% |
| BILL_AMT5 | 655 | -81,334 | 2.2% |
| BILL_AMT6 | 688 | -339,603 | 2.3% |

**Interpretation**:  
In credit card accounting, a negative statement balance indicates the customer has  
a **credit balance** — they paid more than was owed, or received a refund/cashback credit.  
This is a standard and completely valid financial state.

**Treatment**:  
Retain all negative BILL_AMT values unchanged.

**Why this treatment**:  
- Financial domain knowledge confirms negative balances are valid
- Zeroing them would distort credit utilisation calculations in feature engineering
- The records with negative bills contain otherwise valid feature data
- There is no evidence these represent data entry errors

**Alternatives considered**:  
1. **Replace with 0**: Rejected — loses meaningful financial information
2. **Take absolute value**: Rejected — changes the financial interpretation
3. **Drop rows**: Rejected — valid data with no grounds for removal

**Decision reference**: D-006

---

## Issue 7 — PAY_AMT: Zero Values

**Problem**:  
The payment amount columns have many zero values, raising the question of  
whether these are missing data or genuine zero payments.

**Evidence**:

| Column | Zero Count | % of rows |
|---|---|---|
| PAY_AMT1 | 5,249 | 17.5% |
| PAY_AMT2 | 5,396 | 18.0% |
| PAY_AMT3 | 5,968 | 19.9% |
| PAY_AMT4 | 6,408 | 21.4% |
| PAY_AMT5 | 6,703 | 22.3% |
| PAY_AMT6 | 7,173 | 23.9% |

**Interpretation**:  
A zero payment amount means the customer made no payment in that billing cycle.  
This is a financially valid and expected situation — particularly for customers  
who are in default or significantly delayed.

**Treatment**:  
Retain all zero PAY_AMT values.

**Why this treatment**:  
- Zero payment is a genuine and informative customer behaviour
- Customers with PAY code >= 1 (delayed) naturally tend to have zero payments
- No PAY_AMT values are negative (confirmed: 0 negatives across all columns)

---

## Issue 8 — AGE: Range Validation

**Problem**:  
Verify whether AGE values are within a plausible range.

**Evidence**:  
Min: 21, Max: 79, Mean: 35.49, Median: 34  
Ages > 70: 15 records  
Ages == 21 (minimum): 67 records  
Ages < 18 or > 100: 0 records

**Treatment**:  
Retain all. Range 21-79 is entirely plausible for credit card holders in Taiwan in 2005.  
Age 21 was the legal age of full civil majority in Taiwan at the time.

---

## Issue 9 — LIMIT_BAL: Range Validation

**Problem**:  
Verify whether credit limit values are plausible.

**Evidence**:  
Min: 10,000 NT$, Max: 1,000,000 NT$, Mean: 167,484 NT$  
1st percentile: 10,000, 99th percentile: 500,000  
Zero or negative values: 0

**Treatment**:  
Retain all. The range is plausible for a Taiwanese credit card portfolio in 2005.

---

## Processed Dataset — Final State

| Property | Value |
|---|---|
| File | `data/processed/credit_risk_clean.csv` |
| Rows | 30,000 (unchanged) |
| Columns | 25 (unchanged) |
| Missing values | 0 |
| Rows dropped | **0** |
| Target column name | `DEFAULT` (renamed from original) |
| EDUCATION unique codes | 1, 2, 3, 4 (cleaned) |
| MARRIAGE unique codes | 1, 2, 3 (cleaned) |
| SEX unique codes | 1, 2 |
| Default rate | 22.12% (unchanged) |
| File size | ~2.76 MB |

---

## Column Mapping (Raw -> Processed)

| Raw Name | Processed Name | Change |
|---|---|---|
| `default payment next month` | `DEFAULT` | Renamed |
| `EDUCATION` | `EDUCATION` | Codes 0,5,6 -> 4 |
| `MARRIAGE` | `MARRIAGE` | Code 0 -> 3 |
| All other columns | Unchanged | No modification |
