# SQL Analytics & MySQL Database Architecture

## Project: Banking Credit Risk & Financial Analytics
**Phase 4 — Real MySQL 8.0 Execution & Verification**  
**Completed**: 2026-08-31

---

## 1. Overview & Verification Status

Phase 4 establishes an enterprise-grade relational analytical database layer on top of the clean dataset (`data/processed/credit_risk_clean.csv`). All 10 analytical SQL queries were executed and validated directly against a live **MySQL Server 8.0.43** instance.

### Live Environment Verification Details:
- **Database Engine**: MySQL Server 8.0
- **Verified Server Version**: `8.0.43`
- **Host / Port**: `localhost:3306`
- **Database Name**: `credit_risk_db`
- **Table Name**: `credit_card_clients`
- **Rows Ingested & Verified**: 30,000 records
- **Columns Verified**: 25 columns
- **Queries Executed**: 10 / 10 successfully executed on MySQL 8.0.43 (0 errors)
- **Fallback Status**: SQLite fallback was **NOT** used for final validation.

---

## 2. Relational Schema & Indexing Strategy

### Table: `credit_card_clients` (MySQL 8.0)

```sql
CREATE TABLE credit_card_clients (
    ID INT PRIMARY KEY COMMENT 'Customer Identifier (1-30000)',
    LIMIT_BAL INT NOT NULL COMMENT 'Credit Limit in NT$',
    SEX INT NOT NULL COMMENT 'Gender: 1=Male, 2=Female',
    EDUCATION INT NOT NULL COMMENT 'Education: 1=Graduate, 2=University, 3=High School, 4=Others',
    MARRIAGE INT NOT NULL COMMENT 'Marital Status: 1=Married, 2=Single, 3=Others',
    AGE INT NOT NULL COMMENT 'Age in years (21-79)',
    PAY_0 INT NOT NULL COMMENT 'Repayment status Sep 2005 (-2 to 8)',
    PAY_2 INT NOT NULL COMMENT 'Repayment status Aug 2005 (-2 to 8)',
    PAY_3 INT NOT NULL COMMENT 'Repayment status Jul 2005 (-2 to 8)',
    PAY_4 INT NOT NULL COMMENT 'Repayment status Jun 2005 (-2 to 8)',
    PAY_5 INT NOT NULL COMMENT 'Repayment status May 2005 (-2 to 8)',
    PAY_6 INT NOT NULL COMMENT 'Repayment status Apr 2005 (-2 to 8)',
    BILL_AMT1 INT NOT NULL COMMENT 'Bill Statement Sep 2005 (NT$)',
    BILL_AMT2 INT NOT NULL COMMENT 'Bill Statement Aug 2005 (NT$)',
    BILL_AMT3 INT NOT NULL COMMENT 'Bill Statement Jul 2005 (NT$)',
    BILL_AMT4 INT NOT NULL COMMENT 'Bill Statement Jun 2005 (NT$)',
    BILL_AMT5 INT NOT NULL COMMENT 'Bill Statement May 2005 (NT$)',
    BILL_AMT6 INT NOT NULL COMMENT 'Bill Statement Apr 2005 (NT$)',
    PAY_AMT1 INT NOT NULL COMMENT 'Payment Amount Sep 2005 (NT$)',
    PAY_AMT2 INT NOT NULL COMMENT 'Payment Amount Aug 2005 (NT$)',
    PAY_AMT3 INT NOT NULL COMMENT 'Payment Amount Jul 2005 (NT$)',
    PAY_AMT4 INT NOT NULL COMMENT 'Payment Amount Jun 2005 (NT$)',
    PAY_AMT5 INT NOT NULL COMMENT 'Payment Amount May 2005 (NT$)',
    PAY_AMT6 INT NOT NULL COMMENT 'Payment Amount Apr 2005 (NT$)',
    `DEFAULT` INT NOT NULL COMMENT 'Target: 1=Default next month, 0=No default'
);
```

### Indexing Strategy in MySQL
1. `idx_default (DEFAULT)`: Accelerates binary outcome filtering and portfolio default rate aggregations.
2. `idx_pay0 (PAY_0)`: Optimizes recency grouping.
3. `idx_education (EDUCATION)` & `idx_age (AGE)`: Optimizes demographic slices.
4. `idx_limit_bal (LIMIT_BAL)`: Accelerates credit tier range scans.
5. `idx_composite_risk (PAY_0, LIMIT_BAL, DEFAULT)`: Covering composite index for high-risk segment extraction.

---

## 3. Database Execution & Configuration

Connection parameters are read securely from the local `.env` file via `src/database.py` using SQLAlchemy `URL.create` and PyMySQL:

```ini
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=********
DB_NAME=credit_risk_db
```

Pipeline execution command:
```bash
python src/database.py
```

---

## 4. Analytical SQL Queries Breakdown (Validated on MySQL 8.0.43)

### Query 1: Portfolio Baseline & Executive KPIs

- **Business Question**: What is the portfolio-level baseline default rate, average credit limit, and monthly billing/payment volume across the entire credit portfolio?
- **SQL Techniques**: Aggregations (`COUNT`, `SUM`, `AVG`, `ROUND`), Reserved keyword quoting (`` `DEFAULT` ``).

```sql
SELECT 
    COUNT(*) AS total_customers,
    SUM(`DEFAULT`) AS total_defaulters,
    ROUND(AVG(`DEFAULT`) * 100, 2) AS default_rate_pct,
    ROUND(AVG(LIMIT_BAL), 0) AS avg_credit_limit,
    ROUND(AVG(BILL_AMT1), 0) AS avg_sep_bill,
    ROUND(AVG(PAY_AMT1), 0) AS avg_sep_payment
FROM credit_card_clients;
```

**Verified MySQL 8.0.43 Execution Results**:
| total_customers | total_defaulters | default_rate_pct | avg_credit_limit | avg_sep_bill | avg_sep_payment |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 30,000 | 6,636 | 22.12% | 167,484 NT$ | 51,223 NT$ | 5,664 NT$ |

**Business Interpretation & Banking Action**:
- Baseline default rate is **22.12%** ($n = 6,636$).
- In September 2005, the average customer carried a statement balance of 51,223 NT$ against an average payment of 5,664 NT$ (~11% repayment of statement balance).
- Serves as the executive benchmark for all risk tiering.

---

### Query 2: Demographic Risk Profile by Education Level

- **Business Question**: How does credit default risk vary across formal education tiers, and what is the relationship between education and assigned credit limits?
- **SQL Techniques**: `GROUP BY`, `CASE` label decoding, Aggregations, `ORDER BY`.

```sql
SELECT 
    CASE EDUCATION
        WHEN 1 THEN '1 - Graduate School'
        WHEN 2 THEN '2 - University'
        WHEN 3 THEN '3 - High School'
        WHEN 4 THEN '4 - Others'
        ELSE 'Unknown'
    END AS education_level,
    COUNT(*) AS total_customers,
    SUM(`DEFAULT`) AS default_count,
    ROUND(AVG(`DEFAULT`) * 100, 2) AS default_rate_pct,
    ROUND(AVG(LIMIT_BAL), 0) AS avg_credit_limit
FROM credit_card_clients
GROUP BY EDUCATION
ORDER BY EDUCATION;
```

**Verified MySQL 8.0.43 Execution Results**:
| education_level | total_customers | default_count | default_rate_pct | avg_credit_limit |
|---|:---:|:---:|:---:|:---:|
| 1 - Graduate School | 10,585 | 2,036 | 19.23% | 212,956 NT$ |
| 2 - University | 14,030 | 3,330 | 23.73% | 147,062 NT$ |
| 3 - High School | 4,917 | 1,237 | 25.16% | 126,550 NT$ |
| 4 - Others | 468 | 33 | 7.05% | 181,316 NT$ |

**Business Interpretation & Banking Action**:
- Higher formal education is associated with lower default rates: Graduate School cardholders default at 19.23% vs 25.16% for High School cardholders.
- Underwriting policies assign higher credit lines to Graduate cardholders (212,956 NT$ avg vs 126,550 NT$ for High School).
- **Action**: Factor education tiers into automated credit-line increase scorecards.

---

### Query 3: Demographic Risk Profile by Life-Stage Age Brackets

- **Business Question**: Which age brackets exhibit the highest propensity to default, and how does average credit limit differ across age groups?
- **SQL Techniques**: Multi-condition `CASE` binning, Grouping by expression, Sorting by risk rank.

```sql
SELECT 
    CASE 
        WHEN AGE BETWEEN 21 AND 25 THEN '21-25 (Young Adult)'
        WHEN AGE BETWEEN 26 AND 35 THEN '26-35 (Early Career)'
        WHEN AGE BETWEEN 36 AND 50 THEN '36-50 (Mid Career)'
        WHEN AGE >= 51 THEN '51+ (Mature/Senior)'
        ELSE 'Other'
    END AS age_group,
    COUNT(*) AS total_customers,
    SUM(`DEFAULT`) AS default_count,
    ROUND(AVG(`DEFAULT`) * 100, 2) AS default_rate_pct,
    ROUND(AVG(LIMIT_BAL), 0) AS avg_credit_limit
FROM credit_card_clients
GROUP BY 
    CASE 
        WHEN AGE BETWEEN 21 AND 25 THEN '21-25 (Young Adult)'
        WHEN AGE BETWEEN 26 AND 35 THEN '26-35 (Early Career)'
        WHEN AGE BETWEEN 36 AND 50 THEN '36-50 (Mid Career)'
        WHEN AGE >= 51 THEN '51+ (Mature/Senior)'
        ELSE 'Other'
    END
ORDER BY default_rate_pct DESC;
```

**Verified MySQL 8.0.43 Execution Results**:
| age_group | total_customers | default_count | default_rate_pct | avg_credit_limit |
|---|:---:|:---:|:---:|:---:|
| 21-25 (Young Adult) | 3,871 | 1,032 | 26.66% | 73,764 NT$ |
| 51+ (Mature/Senior) | 2,269 | 577 | 25.43% | 164,416 NT$ |
| 36-50 (Mid Career) | 10,922 | 2,462 | 22.54% | 187,379 NT$ |
| 26-35 (Early Career) | 12,938 | 2,565 | 19.83% | 179,269 NT$ |

**Business Interpretation & Banking Action**:
- Bimodal risk distribution: Young Adults (21–25, 26.66%) and Mature/Seniors (51+, 25.43%) show higher default rates than Early Career professionals (26–35, 19.83%).
- Young Adults operate with lower credit limits (73,764 NT$), limiting gross loss exposure per account.
- **Action**: Implement graduated limit progression for young borrowers upon demonstrated payment consistency.

---

### Query 4: Credit Limit Segmentation & Exposure Concentration

- **Business Question**: How does default frequency vary across credit-limit tiers, and how is total billing exposure distributed across limit bands?
- **SQL Techniques**: Tiered `CASE` binning, Aggregate exposure calculation (`SUM(BILL_AMT1)/1M`), Ratio calculation.
- *Note:* Compares default frequencies across tiers; does not claim statistical correlation or causation.

```sql
SELECT 
    CASE 
        WHEN LIMIT_BAL <= 50000 THEN '1. Low (<= 50K)'
        WHEN LIMIT_BAL <= 100000 THEN '2. Moderate (50K - 100K)'
        WHEN LIMIT_BAL <= 200000 THEN '3. Medium (100K - 200K)'
        WHEN LIMIT_BAL <= 300000 THEN '4. Upper-Medium (200K - 300K)'
        WHEN LIMIT_BAL <= 500000 THEN '5. High (300K - 500K)'
        ELSE '6. Very High (> 500K)'
    END AS credit_limit_tier,
    COUNT(*) AS total_customers,
    SUM(`DEFAULT`) AS default_count,
    ROUND(AVG(`DEFAULT`) * 100, 2) AS default_rate_pct,
    ROUND(SUM(BILL_AMT1) / 1000000.0, 2) AS total_sep_exposure_millions
FROM credit_card_clients
GROUP BY 
    CASE 
        WHEN LIMIT_BAL <= 50000 THEN '1. Low (<= 50K)'
        WHEN LIMIT_BAL <= 100000 THEN '2. Moderate (50K - 100K)'
        WHEN LIMIT_BAL <= 200000 THEN '3. Medium (100K - 200K)'
        WHEN LIMIT_BAL <= 300000 THEN '4. Upper-Medium (200K - 300K)'
        WHEN LIMIT_BAL <= 500000 THEN '5. High (300K - 500K)'
        ELSE '6. Very High (> 500K)'
    END
ORDER BY credit_limit_tier;
```

**Verified MySQL 8.0.43 Execution Results**:
| credit_limit_tier | total_customers | default_count | default_rate_pct | total_sep_exposure_millions |
|---|:---:|:---:|:---:|:---:|
| 1. Low (<= 50K) | 7,676 | 2,440 | 31.79% | 172.03 M NT$ |
| 2. Moderate (50K - 100K) | 4,822 | 1,244 | 25.80% | 211.49 M NT$ |
| 3. Medium (100K - 200K) | 7,880 | 1,535 | 19.48% | 436.85 M NT$ |
| 4. Upper-Medium (200K - 300K) | 5,059 | 812 | 16.05% | 330.69 M NT$ |
| 5. High (300K - 500K) | 4,357 | 582 | 13.36% | 350.80 M NT$ |
| 6. Very High (> 500K) | 206 | 23 | 11.17% | 34.83 M NT$ |

**Business Interpretation & Banking Action**:
- Clear monotonic relationship: default frequency drops steadily from **31.79%** in the $\le 50\text{K}$ tier to **11.17%** in the $> 500\text{K}$ tier.
- The largest share of outstanding debt sits in the Medium to High tiers (Medium alone accounts for 436.85 M NT$).
- **Action**: Differentiate risk operations: credit-tightening and loss mitigation on low-tier accounts; utilization monitoring on high-balance accounts.

---

### Query 5: Immediate Delinquency Risk Signal (`PAY_0` Status)

- **Business Question**: What is the empirical default probability associated with each repayment status code in the most recent billing cycle (September 2005)?
- **SQL Techniques**: Behavioral code mapping with `CASE`, Grouping by status code.
- *Note on -2:* Code `-2` is interpreted as "No consumption" per project analytical convention (D-005/D-012); not an official UCI specification.

```sql
SELECT 
    PAY_0 AS repayment_status_code,
    CASE PAY_0
        WHEN -2 THEN 'No consumption (analytical interpretation)'
        WHEN -1 THEN 'Paid duly (in full)'
        WHEN 0 THEN 'Revolving credit (min payment made)'
        WHEN 1 THEN '1 month delay'
        WHEN 2 THEN '2 months delay'
        WHEN 3 THEN '3 months delay'
        ELSE '4+ months delay'
    END AS repayment_behavior,
    COUNT(*) AS customer_count,
    SUM(`DEFAULT`) AS default_count,
    ROUND(AVG(`DEFAULT`) * 100, 2) AS default_rate_pct
FROM credit_card_clients
GROUP BY 
    PAY_0,
    CASE PAY_0
        WHEN -2 THEN 'No consumption (analytical interpretation)'
        WHEN -1 THEN 'Paid duly (in full)'
        WHEN 0 THEN 'Revolving credit (min payment made)'
        WHEN 1 THEN '1 month delay'
        WHEN 2 THEN '2 months delay'
        WHEN 3 THEN '3 months delay'
        ELSE '4+ months delay'
    END
ORDER BY PAY_0;
```

**Verified MySQL 8.0.43 Execution Results**:
| repayment_status_code | repayment_behavior | customer_count | default_count | default_rate_pct |
|:---:|---|:---:|:---:|:---:|
| -2 | No consumption (analytical interpretation) | 2,759 | 365 | 13.23% |
| -1 | Paid duly (in full) | 5,686 | 954 | 16.78% |
| 0 | Revolving credit (min payment made) | 14,737 | 1,888 | 12.81% |
| 1 | 1 month delay | 3,688 | 1,252 | 33.95% |
| 2 | 2 months delay | 2,667 | 1,844 | **69.14%** |
| 3 | 3 months delay | 322 | 244 | **75.78%** |
| 4 | 4+ months delay | 76 | 52 | 68.42% |
| 5 | 4+ months delay | 26 | 13 | 50.00% |
| 6 | 4+ months delay | 11 | 6 | 54.55% |
| 7 | 4+ months delay | 9 | 7 | 77.78% |
| 8 | 4+ months delay | 19 | 11 | 57.89% |

**Business Interpretation & Banking Action**:
- Accounts with `PAY_0 <= 0` default at 12.8%–16.8%.
- Moving to a 1-month delay (`PAY_0 = 1`) more than doubles risk to 33.95%.
- A 2-month delay (`PAY_0 = 2`) triggers a severe risk cliff, surging to **69.14%**.
- **Action**: Trigger automated notifications at `PAY_0 = 1` before accounts cross into `PAY_0 = 2`.

---

### Query 6: Delinquency Persistence & Multi-Month Streak Analysis

- **Business Question**: How does default risk escalate as the number of delinquent months (`PAY_i >= 1`) increases across the 6-month window?
- **SQL Techniques**: Common Table Expression (CTE), Multi-column boolean logic, Portfolio share computation.
- *Note:* Evaluates all 6 months (`PAY_0`, `PAY_2`, `PAY_3`, `PAY_4`, `PAY_5`, `PAY_6`). Delinquency is strictly defined as `PAY_i >= 1`.

```sql
WITH DelinquencyCounts AS (
    SELECT 
        ID,
        `DEFAULT`,
        ((CASE WHEN PAY_0 >= 1 THEN 1 ELSE 0 END) +
         (CASE WHEN PAY_2 >= 1 THEN 1 ELSE 0 END) +
         (CASE WHEN PAY_3 >= 1 THEN 1 ELSE 0 END) +
         (CASE WHEN PAY_4 >= 1 THEN 1 ELSE 0 END) +
         (CASE WHEN PAY_5 >= 1 THEN 1 ELSE 0 END) +
         (CASE WHEN PAY_6 >= 1 THEN 1 ELSE 0 END)) AS delinquent_months_count
    FROM credit_card_clients
)
SELECT 
    delinquent_months_count,
    COUNT(*) AS total_customers,
    SUM(`DEFAULT`) AS default_count,
    ROUND(AVG(`DEFAULT`) * 100, 2) AS default_rate_pct,
    ROUND(COUNT(*) * 100.0 / 30000.0, 2) AS pct_of_portfolio
FROM DelinquencyCounts
GROUP BY delinquent_months_count
ORDER BY delinquent_months_count;
```

**Verified MySQL 8.0.43 Execution Results**:
| delinquent_months_count | total_customers | default_count | default_rate_pct | pct_of_portfolio |
|:---:|:---:|:---:|:---:|:---:|
| 0 | 19,931 | 2,334 | 11.71% | 66.44% |
| 1 | 4,426 | 1,320 | 29.82% | 14.75% |
| 2 | 1,899 | 736 | 38.76% | 6.33% |
| 3 | 1,154 | 587 | 50.87% | 3.85% |
| 4 | 951 | 545 | 57.31% | 3.17% |
| 5 | 298 | 171 | 57.38% | 0.99% |
| 6 | 1,341 | 943 | 70.32% | 4.47% |

**Business Interpretation & Banking Action**:
- 66.44% of cardholders have never experienced a payment delay in the 6 months (11.71% default rate).
- Risk scales directly with streak duration: from 29.82% at 1 month to **70.32% at 6 months**.
- **Action**: Implement early-warning rules: accounts reaching 3+ delinquent months should be restricted from new credit authorizations.

---

### Query 7: Recent Consecutive Delinquency vs Transitioning Accounts

- **Business Question**: What is the default risk differential between accounts with persistent consecutive delays (Sep & Aug) vs newly delayed or recovering accounts?
- **SQL Techniques**: CTE, Mutually Exclusive & Collectively Exhaustive `CASE` logic.

```sql
WITH DelinquencyProfile AS (
    SELECT 
        ID,
        LIMIT_BAL,
        `DEFAULT`,
        CASE 
            WHEN PAY_0 >= 1 AND PAY_2 >= 1 THEN '1. Consecutive Delay in Sep & Aug'
            WHEN PAY_0 >= 1 AND PAY_2 < 1 THEN '2. New Delay in Sep Only'
            WHEN PAY_0 < 1 AND PAY_2 >= 1 THEN '3. Delayed in Aug, Current in Sep'
            ELSE '4. Current / Paid in Both Months'
        END AS recent_repayment_pattern
    FROM credit_card_clients
)
SELECT 
    recent_repayment_pattern,
    COUNT(*) AS customer_count,
    SUM(`DEFAULT`) AS default_count,
    ROUND(AVG(`DEFAULT`) * 100, 2) AS default_rate_pct,
    ROUND(AVG(LIMIT_BAL), 0) AS avg_credit_limit
FROM DelinquencyProfile
GROUP BY recent_repayment_pattern
ORDER BY default_rate_pct DESC;
```

**Verified MySQL 8.0.43 Execution Results**:
| recent_repayment_pattern | customer_count | default_count | default_rate_pct | avg_credit_limit |
|---|:---:|:---:|:---:|:---:|
| 1. Consecutive Delay in Sep & Aug | 3,991 | 2,306 | **57.78%** | 100,340 NT$ |
| 2. New Delay in Sep Only | 2,827 | 1,123 | **39.72%** | 171,259 NT$ |
| 3. Delayed in Aug, Current in Sep | 447 | 170 | **38.03%** | 149,217 NT$ |
| 4. Current / Paid in Both Months | 22,735 | 3,037 | **13.36%** | 179,161 NT$ |

**Business Interpretation & Banking Action**:
- Mutually exclusive & collectively exhaustive ($3,991 + 2,827 + 447 + 22,735 = 30,000$).
- Consecutive delay in the two most recent cycles results in a **57.78% default rate** on lower average credit limits (100,340 NT$).
- Accounts that missed August but paid in September still carry an elevated default rate (38.03%), indicating residual instability.
- **Action**: Route Consecutive Delinquents directly to intensive collections; send payment reminder nudges to New Delinquents.

---

### Query 8: Credit Utilisation Tiers & Leverage Risk

- **Business Question**: How does revolving credit utilisation (`BILL_AMT1 / LIMIT_BAL`) relate to default frequency, and what is the risk among over-limit accounts?
- **SQL Techniques**: CTE with floating-point ratio, Mutually Exclusive & Collectively Exhaustive leverage tiers.
- *Note on Safety:* Division by `LIMIT_BAL` is safe as min `LIMIT_BAL` is 10,000 NT$ (zero/negative limits do not exist). Negative/zero statement balances are isolated.

```sql
WITH UtilisationBands AS (
    SELECT 
        ID,
        `DEFAULT`,
        LIMIT_BAL,
        BILL_AMT1,
        (BILL_AMT1 * 1.0 / LIMIT_BAL) AS util_ratio,
        CASE 
            WHEN BILL_AMT1 <= 0 THEN '0. Zero or Credit Balance'
            WHEN (BILL_AMT1 * 1.0 / LIMIT_BAL) < 0.30 THEN '1. Low (< 30%)'
            WHEN (BILL_AMT1 * 1.0 / LIMIT_BAL) < 0.60 THEN '2. Moderate (30% - 60%)'
            WHEN (BILL_AMT1 * 1.0 / LIMIT_BAL) < 0.90 THEN '3. High (60% - 90%)'
            WHEN (BILL_AMT1 * 1.0 / LIMIT_BAL) <= 1.00 THEN '4. Near Limit (90% - 100%)'
            ELSE '5. Over-Limit (> 100%)'
        END AS utilisation_tier
    FROM credit_card_clients
)
SELECT 
    utilisation_tier,
    COUNT(*) AS total_customers,
    SUM(`DEFAULT`) AS default_count,
    ROUND(AVG(`DEFAULT`) * 100, 2) AS default_rate_pct,
    ROUND(AVG(LIMIT_BAL), 0) AS avg_limit
FROM UtilisationBands
GROUP BY utilisation_tier
ORDER BY utilisation_tier;
```

**Verified MySQL 8.0.43 Execution Results**:
| utilisation_tier | total_customers | default_count | default_rate_pct | avg_limit |
|---|:---:|:---:|:---:|:---:|
| 0. Zero or Credit Balance | 2,598 | 643 | 24.75% | 209,784 NT$ |
| 1. Low (< 30%) | 12,194 | 2,065 | 16.93% | 216,468 NT$ |
| 2. Moderate (30% - 60%) | 4,307 | 999 | 23.19% | 144,718 NT$ |
| 3. High (60% - 90%) | 4,851 | 1,338 | 27.58% | 117,058 NT$ |
| 4. Near Limit (90% - 100%) | 3,935 | 955 | 24.27% | 106,203 NT$ |
| 5. Over-Limit (> 100%) | 2,115 | 636 | **30.07%** | 109,141 NT$ |

**Business Interpretation & Banking Action**:
- Accounts with low credit utilisation ($< 30\%$) default at 16.93%.
- Default rates rise across utilisation bands, peaking at **30.07%** for over-limit cardholders ($> 100\%$ utilisation, $n = 2,115$).
- **Action**: Enforce hard credit authorization blocks when accounts reach 100% of their limit.

---

### Query 9: 6-Month Chronological Statement Balance Volume vs Payment Trend

- **Business Question**: How has net statement balance volume and customer repayment amount evolved chronologically from April 2005 to September 2005?
- **SQL Techniques**: `UNION ALL` pipeline, Chronological sorting index (April $\rightarrow$ September).
- *Note on Statement Balances:* `SUM(BILL_AMT)` reflects net reported statement balance volume (debt net of credit/overpayments).

```sql
SELECT 
    'April 2005' AS billing_month,
    1 AS chronological_order,
    ROUND(AVG(BILL_AMT6), 0) AS avg_statement_balance,
    ROUND(AVG(PAY_AMT6), 0) AS avg_payment_amount,
    ROUND(SUM(BILL_AMT6) / 1000000.0, 2) AS net_statement_volume_millions,
    ROUND(SUM(PAY_AMT6) / 1000000.0, 2) AS total_payment_volume_millions
FROM credit_card_clients
UNION ALL
SELECT 
    'May 2005', 2,
    ROUND(AVG(BILL_AMT5), 0), ROUND(AVG(PAY_AMT5), 0),
    ROUND(SUM(BILL_AMT5) / 1000000.0, 2), ROUND(SUM(PAY_AMT5) / 1000000.0, 2)
FROM credit_card_clients
UNION ALL
SELECT 
    'June 2005', 3,
    ROUND(AVG(BILL_AMT4), 0), ROUND(AVG(PAY_AMT4), 0),
    ROUND(SUM(BILL_AMT4) / 1000000.0, 2), ROUND(SUM(PAY_AMT4) / 1000000.0, 2)
FROM credit_card_clients
UNION ALL
SELECT 
    'July 2005', 4,
    ROUND(AVG(BILL_AMT3), 0), ROUND(AVG(PAY_AMT3), 0),
    ROUND(SUM(BILL_AMT3) / 1000000.0, 2), ROUND(SUM(PAY_AMT3) / 1000000.0, 2)
FROM credit_card_clients
UNION ALL
SELECT 
    'August 2005', 5,
    ROUND(AVG(BILL_AMT2), 0), ROUND(AVG(PAY_AMT2), 0),
    ROUND(SUM(BILL_AMT2) / 1000000.0, 2), ROUND(SUM(PAY_AMT2) / 1000000.0, 2)
FROM credit_card_clients
UNION ALL
SELECT 
    'September 2005', 6,
    ROUND(AVG(BILL_AMT1), 0), ROUND(AVG(PAY_AMT1), 0),
    ROUND(SUM(BILL_AMT1) / 1000000.0, 2), ROUND(SUM(PAY_AMT1) / 1000000.0, 2)
FROM credit_card_clients
ORDER BY chronological_order;
```

**Verified MySQL 8.0.43 Execution Results**:
| billing_month | chronological_order | avg_statement_balance | avg_payment_amount | net_statement_volume_millions | total_payment_volume_millions |
|---|:---:|:---:|:---:|:---:|:---:|
| April 2005 | 1 | 38,872 NT$ | 5,216 NT$ | 1,166.15 M NT$ | 156.47 M NT$ |
| May 2005 | 2 | 40,311 NT$ | 4,799 NT$ | 1,209.34 M NT$ | 143.98 M NT$ |
| June 2005 | 3 | 43,263 NT$ | 4,826 NT$ | 1,297.89 M NT$ | 144.78 M NT$ |
| July 2005 | 4 | 47,013 NT$ | 5,226 NT$ | 1,410.39 M NT$ | 156.77 M NT$ |
| August 2005 | 5 | 49,179 NT$ | 5,921 NT$ | 1,475.37 M NT$ | 177.63 M NT$ |
| September 2005 | 6 | 51,223 NT$ | 5,664 NT$ | 1,536.70 M NT$ | 169.91 M NT$ |

**Business Interpretation & Banking Action**:
- Net statement balance volume grew +31.8% from 1.166 B NT$ in April to 1.537 B NT$ in September.
- Aggregate monthly repayments remained steady (~144M to 178M NT$), indicating accumulating portfolio leverage.
- **Action**: Bank risk committees should prepare loan-loss provisions in anticipation of increased default volume.

---

### Query 10: High-Risk Analytical Prioritization & Exposure Ranking

- **Business Question**: Which individual accounts in the high-risk analytical segment (`PAY_0 >= 2`, `LIMIT_BAL <= 100,000 NT$`, `BILL_AMT1 > 0`) carry the largest outstanding balances for priority collections outreach?
- **SQL Techniques**: CTE, Window Functions (`DENSE_RANK() OVER`), Risk rule filtering.
- *Note:* This is an operational heuristic prioritization rule for collections workflows, NOT an ML prediction.

```sql
WITH RankedHighRisk AS (
    SELECT 
        ID,
        LIMIT_BAL,
        AGE,
        PAY_0,
        BILL_AMT1,
        PAY_AMT1,
        `DEFAULT`,
        ROUND((BILL_AMT1 * 1.0 / LIMIT_BAL) * 100, 1) AS util_pct,
        DENSE_RANK() OVER (ORDER BY BILL_AMT1 DESC) AS exposure_rank
    FROM credit_card_clients
    WHERE PAY_0 >= 2 AND LIMIT_BAL <= 100000 AND BILL_AMT1 > 0
)
SELECT 
    ID AS customer_id,
    LIMIT_BAL AS credit_limit,
    AGE AS customer_age,
    PAY_0 AS sep_delay_code,
    BILL_AMT1 AS sep_bill_balance,
    PAY_AMT1 AS sep_payment,
    util_pct AS utilisation_pct,
    `DEFAULT` AS defaulted,
    exposure_rank
FROM RankedHighRisk
WHERE exposure_rank <= 10
ORDER BY exposure_rank;
```

**Verified MySQL 8.0.43 Execution Results (Top 10 High-Risk Accounts)**:
| customer_id | credit_limit | customer_age | sep_delay_code | sep_bill_balance | sep_payment | utilisation_pct | defaulted | exposure_rank |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 15803 | 100,000 | 24 | 2 | 177,646 NT$ | 7,900 NT$ | 177.6% | 0 | 1 |
| 2466 | 100,000 | 29 | 4 | 175,441 NT$ | 0 NT$ | 175.4% | 1 | 2 |
| 23149 | 100,000 | 41 | 2 | 155,351 NT$ | 105,200 NT$ | 155.4% | 1 | 3 |
| 23616 | 80,000 | 39 | 2 | 129,966 NT$ | 9,685 NT$ | 162.5% | 1 | 4 |
| 24766 | 50,000 | 44 | 2 | 127,510 NT$ | 0 NT$ | 255.0% | 1 | 5 |
| 8998 | 80,000 | 31 | 8 | 126,786 NT$ | 0 NT$ | 158.5% | 0 | 6 |
| 19323 | 60,000 | 38 | 7 | 126,220 NT$ | 0 NT$ | 210.4% | 0 | 7 |
| 3564 | 90,000 | 24 | 2 | 124,457 NT$ | 6,600 NT$ | 138.3% | 1 | 8 |
| 2942 | 90,000 | 26 | 2 | 121,368 NT$ | 0 NT$ | 134.9% | 0 | 9 |
| 8834 | 90,000 | 37 | 2 | 117,793 NT$ | 6,732 NT$ | 130.9% | 0 | 10 |

**Business Interpretation & Banking Action**:
- Ranks severely delinquent accounts (`PAY_0 >= 2`) with low credit lines and extreme leverage (utilisation reaching up to **255%**).
- Multiple accounts (e.g. 2466, 24766, 8998) made **0 NT$ in payments** against balances $> 125,000\text{ NT\$}$.
- **Action**: Assign these specific prioritized accounts to senior recovery agents for early workout / settlement negotiations.