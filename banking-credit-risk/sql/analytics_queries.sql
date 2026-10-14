-- ============================================================================
-- BANKING CREDIT RISK & FINANCIAL ANALYTICS
-- SQL Analytics Queries Suite (Production MySQL 8.0+)
-- ============================================================================
-- Table: credit_card_clients (30,000 records, 25 columns)
-- Target Dialect: MySQL 8.0+ (ANSI SQL standard compliant)
-- Identifier Quoting: Backticks used for reserved keywords (e.g. `DEFAULT`)
-- Author: Banking Credit Risk Portfolio Project
-- ============================================================================


-- ============================================================================
-- QUERY 1: Portfolio Baseline & Executive KPIs
-- Business Question: What is the portfolio-level baseline default rate, average credit limit, 
--                    and monthly billing/payment volume across the entire credit portfolio?
-- SQL Techniques: Aggregations (COUNT, SUM, AVG, ROUND), Keyword Quoting (`DEFAULT`)
-- ============================================================================
SELECT 
    COUNT(*) AS total_customers,
    SUM(`DEFAULT`) AS total_defaulters,
    ROUND(AVG(`DEFAULT`) * 100, 2) AS default_rate_pct,
    ROUND(AVG(LIMIT_BAL), 0) AS avg_credit_limit,
    ROUND(AVG(BILL_AMT1), 0) AS avg_sep_bill,
    ROUND(AVG(PAY_AMT1), 0) AS avg_sep_payment
FROM credit_card_clients;


-- ============================================================================
-- QUERY 2: Demographic Risk Profile by Education Level
-- Business Question: How does credit default risk vary across formal education tiers,
--                    and what is the relationship between education and assigned credit limits?
-- SQL Techniques: GROUP BY, CASE Label Decoding, Aggregations, ORDER BY
-- ============================================================================
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


-- ============================================================================
-- QUERY 3: Demographic Risk Profile by Life-Stage Age Brackets
-- Business Question: Which age brackets exhibit the highest propensity to default,
--                    and how does average credit limit differ across age groups?
-- SQL Techniques: Multi-condition CASE Binning, Grouping by Expression, Sorting by Risk
-- ============================================================================
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


-- ============================================================================
-- QUERY 4: Credit Limit Segmentation & Exposure Concentration
-- Business Question: How does default frequency vary across credit-limit tiers,
--                    and how is total billing exposure distributed across limit bands?
-- SQL Techniques: Tiered CASE Binning, Aggregations, Monetary Scaling (Millions NT$)
-- Note: Compares default frequencies across tiers; does not claim statistical correlation or causation.
-- ============================================================================
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


-- ============================================================================
-- QUERY 5: Immediate Delinquency Risk Signal (PAY_0 Status)
-- Business Question: What is the empirical default probability associated with each
--                    repayment status code in the most recent billing cycle (September 2005)?
-- SQL Techniques: Behavioral Code Mapping with CASE, Grouping by Status Code
-- Note on -2: Code -2 is interpreted as 'No consumption' (card not used / balance cleared)
--             per project analytical convention (D-005/D-012); not an official UCI spec.
-- ============================================================================
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


-- ============================================================================
-- QUERY 6: Delinquency Persistence & Multi-Month Streak Analysis
-- Business Question: How does default risk escalate as the number of delinquent months
--                    (months with delay >= 1) increases across the 6-month window?
-- SQL Techniques: Common Table Expression (CTE), Boolean Addition Logic, Portfolio Share Calculation
-- Note: Evaluates all 6 months: PAY_0, PAY_2, PAY_3, PAY_4, PAY_5, PAY_6.
--       Delinquency is strictly defined as PAY_i >= 1 (1+ months payment delay).
-- ============================================================================
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


-- ============================================================================
-- QUERY 7: Recent Consecutive Delinquency vs Transitioning Accounts
-- Business Question: What is the default risk differential between accounts with persistent
--                    consecutive delays (Sep & Aug) vs newly delayed or recovering accounts?
-- SQL Techniques: CTE, Mutually Exclusive & Collectively Exhaustive CASE Logic
-- Categories:
--   1. Consecutive Delay: PAY_0 >= 1 AND PAY_2 >= 1 (both months delayed)
--   2. New Delay:        PAY_0 >= 1 AND PAY_2 < 1  (delayed Sep only)
--   3. Recovering/Cured: PAY_0 < 1  AND PAY_2 >= 1 (delayed Aug, current Sep)
--   4. Current/Paid:     PAY_0 < 1  AND PAY_2 < 1  (current/paid both months)
-- ============================================================================
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


-- ============================================================================
-- QUERY 8: Credit Utilisation Tiers & Leverage Risk
-- Business Question: How does revolving credit utilisation (bill balance / credit limit)
--                    relate to default frequency, and what is the risk among over-limit accounts?
-- SQL Techniques: CTE with Floating-Point Ratio, Mutually Exclusive Tiers
-- Note: Division by LIMIT_BAL is safe (min LIMIT_BAL = 10,000 NT$; no zero/negative limits).
--       Negative/zero bills represent credit or zero balances per Phase 2/3 decisions.
-- ============================================================================
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


-- ============================================================================
-- QUERY 9: 6-Month Chronological Statement Balance Volume vs Payment Trend
-- Business Question: How has net statement balance volume and customer repayment amount
--                    evolved chronologically from April 2005 to September 2005?
-- SQL Techniques: UNION ALL Pipeline, Chronological Sorting (Apr -> Sep)
-- Note on Statement Balances: SUM(BILL_AMTi) represents net reported statement balance volume,
--                              reflecting outstanding debt net of credit/overpayment balances.
-- Mapping: BILL_AMT6/PAY_AMT6 = Apr, BILL_AMT5/PAY_AMT5 = May, BILL_AMT4/PAY_AMT4 = Jun,
--          BILL_AMT3/PAY_AMT3 = Jul, BILL_AMT2/PAY_AMT2 = Aug, BILL_AMT1/PAY_AMT1 = Sep.
-- ============================================================================
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


-- ============================================================================
-- QUERY 10: High-Risk Analytical Prioritization & Exposure Ranking
-- Business Question: Which individual accounts in the high-risk analytical segment
--                    (PAY_0 >= 2, LIMIT_BAL <= 100,000 NT$, BILL_AMT1 > 0) carry the
--                    largest outstanding balances for priority collections outreach?
-- SQL Techniques: CTE, Window Functions (DENSE_RANK() OVER), Risk Rule Filtering
-- Note: This is an analytical heuristic prioritization rule for collections operations,
--       NOT a predictive machine learning score.
-- ============================================================================
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