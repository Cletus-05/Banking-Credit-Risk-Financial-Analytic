"""
eda_stats.py
============
Banking Credit Risk -- Phase 3 EDA Supporting Statistics

Purpose:
    Reproducible numerical EDA calculations supporting notebooks/02_eda.ipynb.
    This script computes all key statistics used in the EDA.
    It does NOT create features for modeling.
    It does NOT modify data/raw/ or data/processed/credit_risk_clean.csv.

Run from the banking-credit-risk/ directory:
    python eda_stats.py

Output: printed tables to console (no file writes).

Author: Banking Credit Risk Portfolio Project
Data:   data/processed/credit_risk_clean.csv
"""

import pandas as pd
import numpy as np
import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
CSV_PATH = os.path.join(BASE_DIR, "data", "processed", "credit_risk_clean.csv")

PAY_COLS     = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
BILL_COLS    = ["BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6"]
PAY_AMT_COLS = ["PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"]
MONTH_LABELS = ["Sep-05", "Aug-05", "Jul-05", "Jun-05", "May-05", "Apr-05"]

def sep(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def load_data():
    df = pd.read_csv(CSV_PATH)
    assert df.shape == (30000, 25), f"Unexpected shape: {df.shape}"
    print(f"Loaded {df.shape[0]:,} rows x {df.shape[1]} columns from {CSV_PATH}")
    return df


# ---------------------------------------------------------------------------
# 1. CUSTOMER PROFILE
# ---------------------------------------------------------------------------

def profile_age(df):
    sep("1. AGE PROFILE")
    print(df["AGE"].describe(percentiles=[.1, .25, .5, .75, .9, .99]).round(2))
    age_bins = [20, 25, 30, 35, 40, 45, 50, 60, 80]
    age_lbls = ["21-25", "26-30", "31-35", "36-40", "41-45", "46-50", "51-60", "61+"]
    grp = df.groupby(pd.cut(df["AGE"], bins=age_bins, labels=age_lbls), observed=True)["DEFAULT"]
    print(grp.agg(["count", "sum", "mean"]).rename(columns={"mean": "default_rate"}).round(4))


def profile_sex(df):
    sep("2. SEX PROFILE")
    grp = df.groupby("SEX")["DEFAULT"].agg(["count", "sum", "mean"])
    grp.index = ["Male (1)", "Female (2)"]
    grp.columns = ["count", "defaults", "default_rate"]
    print(grp.round(4))


def profile_education(df):
    sep("3. EDUCATION PROFILE")
    grp = df.groupby("EDUCATION")["DEFAULT"].agg(["count", "sum", "mean"])
    grp.index = ["Graduate (1)", "University (2)", "High school (3)", "Others (4)"]
    grp.columns = ["count", "defaults", "default_rate"]
    print(grp.round(4))


def profile_marriage(df):
    sep("4. MARRIAGE PROFILE")
    grp = df.groupby("MARRIAGE")["DEFAULT"].agg(["count", "sum", "mean"])
    grp.index = ["Married (1)", "Single (2)", "Others (3)"]
    grp.columns = ["count", "defaults", "default_rate"]
    print(grp.round(4))


def profile_credit_limit(df):
    sep("5. CREDIT LIMIT PROFILE")
    print("--- Descriptive statistics ---")
    print(df["LIMIT_BAL"].describe(percentiles=[.01, .1, .25, .5, .75, .9, .99]).round(0))
    print("\n--- Unique credit limit values:", df["LIMIT_BAL"].nunique())
    print("\n--- Mean LIMIT_BAL by DEFAULT ---")
    print(df.groupby("DEFAULT")["LIMIT_BAL"].mean().round(0))

    lim_bins = [0, 50000, 100000, 200000, 300000, 500000, 1_000_001]
    lim_lbls = ["<=50K", "50-100K", "100-200K", "200-300K", "300-500K", ">500K"]
    grp = df.groupby(pd.cut(df["LIMIT_BAL"], bins=lim_bins, labels=lim_lbls), observed=True)["DEFAULT"]
    print("\n--- Default rate by credit limit segment ---")
    print(grp.agg(["count", "sum", "mean"]).rename(columns={"mean": "default_rate"}).round(4))


# ---------------------------------------------------------------------------
# 2. REPAYMENT BEHAVIOUR
# ---------------------------------------------------------------------------

def repayment_pay0(df):
    sep("6. REPAYMENT STATUS (PAY_0) -- most recent month")
    grp = df.groupby("PAY_0")["DEFAULT"].agg(["count", "sum", "mean"])
    grp.columns = ["count", "defaults", "default_rate"]
    print(grp.round(4))
    print("\n--- Median PAY_AMT1 by PAY_0 code ---")
    print(df.groupby("PAY_0")["PAY_AMT1"].median().round(0))


def repayment_all_pay(df):
    sep("7. ALL PAY COLUMNS -- delay counts")
    print("--- Customers with any delay (PAY >= 1) per column ---")
    for col in PAY_COLS:
        n = (df[col] >= 1).sum()
        print(f"  {col}: {n:,} ({n/len(df)*100:.1f}%)")


def delinquency_analysis(df):
    sep("8. DELINQUENCY ANALYSIS")
    # ---- Definition 1: Any delay ----
    any_del = (df[PAY_COLS] >= 1).any(axis=1)
    print("--- Any delinquency (PAY >= 1 in any month) ---")
    print(df.groupby(any_del.astype(int).rename("ANY_DELAY"))["DEFAULT"]
          .agg(["count", "sum", "mean"]).rename(columns={"mean": "default_rate"}).round(4))

    # ---- Definition 2: Number of delinquent months ----
    n_del = (df[PAY_COLS] >= 1).sum(axis=1)
    print("\n--- Default rate by number of months with payment delay ---")
    print(df.groupby(n_del.rename("N_DELAY_MONTHS"))["DEFAULT"]
          .agg(["count", "sum", "mean"]).rename(columns={"mean": "default_rate"}).round(4))

    # ---- Definition 3: Maximum payment delay ----
    max_del = df[PAY_COLS].clip(lower=0).max(axis=1)
    print("\n--- Default rate by maximum payment delay code ---")
    print(df.groupby(max_del.rename("MAX_DELAY"))["DEFAULT"]
          .agg(["count", "sum", "mean"]).rename(columns={"mean": "default_rate"}).round(4))

    # ---- Definition 4: Recent delinquency (PAY_0 or PAY_2 >= 1) ----
    recent = ((df["PAY_0"] >= 1) | (df["PAY_2"] >= 1))
    print("\n--- Recent delinquency (PAY_0 or PAY_2 >= 1) ---")
    print(df.groupby(recent.astype(int).rename("RECENT_DELAY"))["DEFAULT"]
          .agg(["count", "sum", "mean"]).rename(columns={"mean": "default_rate"}).round(4))

    # ---- Definition 5: Persistent/consecutive delinquency ----
    consec = ((df["PAY_0"] >= 1) & (df["PAY_2"] >= 1))
    print("\n--- Consecutive delay (PAY_0 >= 1 AND PAY_2 >= 1) ---")
    print(df.groupby(consec.astype(int).rename("CONSEC_DELAY"))["DEFAULT"]
          .agg(["count", "sum", "mean"]).rename(columns={"mean": "default_rate"}).round(4))

    # ---- Definition 6: Severe delinquency (PAY_0 >= 2) ----
    severe = (df["PAY_0"] >= 2)
    print("\n--- Severe delinquency (PAY_0 >= 2) ---")
    print(df.groupby(severe.astype(int).rename("SEVERE_DELAY"))["DEFAULT"]
          .agg(["count", "sum", "mean"]).rename(columns={"mean": "default_rate"}).round(4))


# ---------------------------------------------------------------------------
# 3. BILLING ANALYSIS
# ---------------------------------------------------------------------------

def billing_analysis(df):
    sep("9. BILLING ANALYSIS")
    print("--- BILL_AMT1 (Sep-05) percentiles ---")
    print(df["BILL_AMT1"].describe(percentiles=[.1, .25, .5, .75, .9, .95, .99]).round(0))

    print("\n--- Mean and Median bill amounts by DEFAULT ---")
    for col, month in zip(BILL_COLS, MONTH_LABELS):
        m0  = df[df["DEFAULT"] == 0][col].mean()
        md0 = df[df["DEFAULT"] == 0][col].median()
        m1  = df[df["DEFAULT"] == 1][col].mean()
        md1 = df[df["DEFAULT"] == 1][col].median()
        print(f"  {month} {col}: Non-def mean={m0:.0f} median={md0:.0f} | Default mean={m1:.0f} median={md1:.0f}")

    print("\n--- Positive / Zero / Negative bill counts (BILL_AMT1) ---")
    for col in BILL_COLS:
        n_neg  = (df[col] < 0).sum()
        n_zero = (df[col] == 0).sum()
        n_pos  = (df[col] > 0).sum()
        print(f"  {col}: positive={n_pos:,} zero={n_zero:,} negative={n_neg:,}")


# ---------------------------------------------------------------------------
# 4. PAYMENT ANALYSIS
# ---------------------------------------------------------------------------

def payment_analysis(df):
    sep("10. PAYMENT ANALYSIS")
    print("--- PAY_AMT1 (Sep-05) percentiles ---")
    print(df["PAY_AMT1"].describe(percentiles=[.1, .25, .5, .75, .9, .95, .99]).round(0))

    print("\n--- Median payment amounts by DEFAULT ---")
    print(df.groupby("DEFAULT")[PAY_AMT_COLS].median().round(0))

    print("\n--- Mean payment amounts by DEFAULT ---")
    print(df.groupby("DEFAULT")[PAY_AMT_COLS].mean().round(0))

    print("\n--- Zero payment rate per month by DEFAULT ---")
    for col in PAY_AMT_COLS:
        z0 = (df[df["DEFAULT"] == 0][col] == 0).mean()
        z1 = (df[df["DEFAULT"] == 1][col] == 0).mean()
        print(f"  {col}: Non-default={z0:.3f}  Default={z1:.3f}")


# ---------------------------------------------------------------------------
# 5. PAYMENT-TO-BILL RATIO
# ---------------------------------------------------------------------------

def payment_to_bill_analysis(df):
    sep("11. PAYMENT-TO-BILL RATIO ANALYSIS (Sep-05: PAY_AMT1 / BILL_AMT1)")
    print("""
FORMULA:  Ratio = PAY_AMT1 / BILL_AMT1

SCOPE:    Computed only for records where BILL_AMT1 > 0 (positive outstanding balance).

EXCLUDED:
  - BILL_AMT1 == 0: ratio undefined (no outstanding balance); these customers owe nothing.
  - BILL_AMT1 <  0: ratio is misleading; negative bill = credit balance (overpayment/refund).
    A payment against a credit balance does not reflect repayment of debt.

NOTE: This calculation is for EDA interpretation only.
      It is NOT a modelling feature and is NOT added to the processed dataset.
""")
    n_total = len(df)
    n_valid = (df["BILL_AMT1"] > 0).sum()
    n_zero  = (df["BILL_AMT1"] == 0).sum()
    n_neg   = (df["BILL_AMT1"] < 0).sum()
    print(f"  BILL_AMT1 > 0 (ratio computed): {n_valid:,} ({n_valid/n_total*100:.1f}%)")
    print(f"  BILL_AMT1 == 0 (undefined):     {n_zero:,} ({n_zero/n_total*100:.1f}%)")
    print(f"  BILL_AMT1 < 0 (credit balance): {n_neg:,} ({n_neg/n_total*100:.1f}%)")

    df_v = df[df["BILL_AMT1"] > 0].copy()
    df_v["RATIO"] = df_v["PAY_AMT1"] / df_v["BILL_AMT1"]

    print("\n--- Ratio distribution (unwinsorized) ---")
    print(df_v["RATIO"].describe(percentiles=[.1, .25, .5, .75, .9]).round(4))

    # Use median for group comparison -- more robust given outliers > 1.0 (overpayments)
    print("\n--- Ratio by DEFAULT (median more meaningful than mean due to outliers) ---")
    print(df_v.groupby("DEFAULT")["RATIO"].agg(["median", "mean", "count"]).round(4))
    print("NOTE: mean is distorted by customers who paid more than their bill (ratio > 1.0)")
    print("      Median is the preferred central tendency measure here.")

    print("\n--- Payment tier (as % of outstanding bill) ---")
    df_v["PAY_TIER"] = pd.cut(df_v["RATIO"],
        bins=[-0.001, 0, 0.05, 0.30, 1.0, 1e9],
        labels=["No payment (0%)", "Minimal (<5%)", "Low (5-30%)",
                "Substantial (30-100%)", "Full or over (>100%)"])
    tier_grp = df_v.groupby("PAY_TIER", observed=True)["DEFAULT"].agg(["count", "sum", "mean"])
    tier_grp.columns = ["count", "defaults", "default_rate"]
    print(tier_grp.round(4))

    n_zero_pay = (df_v["RATIO"] == 0).sum()
    n_partial  = ((df_v["RATIO"] > 0) & (df_v["RATIO"] < 1.0)).sum()
    n_full     = (df_v["RATIO"] >= 1.0).sum()
    print(f"\nAmong {n_valid:,} customers with positive outstanding bill:")
    print(f"  Paid nothing (0%):         {n_zero_pay:,} ({n_zero_pay/n_valid*100:.1f}%)")
    print(f"  Partial payment (0-100%):  {n_partial:,} ({n_partial/n_valid*100:.1f}%)")
    print(f"  Full/over payment (>=100%): {n_full:,} ({n_full/n_valid*100:.1f}%)")


# ---------------------------------------------------------------------------
# 6. CREDIT UTILISATION
# ---------------------------------------------------------------------------

def credit_utilisation(df):
    sep("12. CREDIT UTILISATION (BILL_AMT1 / LIMIT_BAL)")
    print("Computed for: BILL_AMT1 > 0 (positive outstanding balance) only.")
    df_v = df[(df["BILL_AMT1"] > 0) & (df["LIMIT_BAL"] > 0)].copy()
    df_v["UTIL"] = df_v["BILL_AMT1"] / df_v["LIMIT_BAL"]
    util_bins = pd.cut(df_v["UTIL"],
        bins=[0, 0.3, 0.6, 0.9, 1.0, 1e9],
        labels=["Low (<30%)", "Moderate (30-60%)", "High (60-90%)", "Critical (90-100%)", "Over-limit (>100%)"])
    grp = df_v.groupby(util_bins, observed=True)["DEFAULT"].agg(["count", "sum", "mean"])
    grp.columns = ["count", "defaults", "default_rate"]
    print(grp.round(4))


# ---------------------------------------------------------------------------
# 7. CROSS-SEGMENT
# ---------------------------------------------------------------------------

def cross_segment(df):
    sep("13. CROSS-SEGMENT ANALYSIS")
    print("--- Default rate: AGE group x LIMIT_BAL segment ---")
    age_bins = [20, 30, 40, 50, 80]
    age_lbls = ["21-30", "31-40", "41-50", "51+"]
    lim_bins = [0, 100000, 300000, 1_000_001]
    lim_lbls = ["Low (<=100K)", "Mid (100-300K)", "High (>300K)"]
    df2 = df.copy()
    df2["AG"] = pd.cut(df2["AGE"], bins=age_bins, labels=age_lbls)
    df2["LS"] = pd.cut(df2["LIMIT_BAL"], bins=lim_bins, labels=lim_lbls)
    print(df2.groupby(["AG", "LS"], observed=True)["DEFAULT"].mean().round(4).unstack())

    print("\n--- High-risk composite segment: PAY_0 >= 2 AND LIMIT_BAL <= 100K ---")
    hr = df[(df["PAY_0"] >= 2) & (df["LIMIT_BAL"] <= 100_000)]
    print(f"  Count: {len(hr):,} ({len(hr)/len(df)*100:.1f}% of portfolio)")
    print(f"  Default rate: {hr['DEFAULT'].mean():.4f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    df = load_data()

    profile_age(df)
    profile_sex(df)
    profile_education(df)
    profile_marriage(df)
    profile_credit_limit(df)

    repayment_pay0(df)
    repayment_all_pay(df)
    delinquency_analysis(df)

    billing_analysis(df)
    payment_analysis(df)
    payment_to_bill_analysis(df)
    credit_utilisation(df)
    cross_segment(df)

    print("\n" + "=" * 60)
    print("eda_stats.py complete.")
    print("=" * 60)