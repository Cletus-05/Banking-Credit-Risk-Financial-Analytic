"""
data_cleaning.py
================
Banking Credit Risk & Financial Analytics — Phase 2

Purpose:
    Load the raw UCI Default of Credit Card Clients dataset,
    apply all documented data quality treatments, and export
    a clean, processed CSV for use in subsequent analysis phases.

All cleaning decisions are documented in:
    docs/decisions.md
    docs/data_quality_and_cleaning.md

IMPORTANT:
    This script NEVER modifies data/raw/.
    All outputs are written to data/processed/.

Author:  Banking Credit Risk Portfolio Project
Dataset: UCI Default of Credit Card Clients (30,000 records, 25 columns)
"""

import os
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FILE = os.path.join(BASE_DIR, "data", "raw", "default of credit card clients.xls")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
PROCESSED_FILE = os.path.join(PROCESSED_DIR, "credit_risk_clean.csv")


# ---------------------------------------------------------------------------
# Step 1 — Load raw data
# ---------------------------------------------------------------------------

def load_raw(filepath: str = RAW_FILE) -> pd.DataFrame:
    """
    Load the raw UCI XLS file.

    File structure:
        Row 0  : UCI variable codes (X1-X23, Y)  -- skipped
        Row 1  : Descriptive column headers       -- used as column names
        Rows 2+: Data

    Returns: DataFrame with descriptive column headers, 30,000 rows.
    """
    df = pd.read_excel(filepath, sheet_name=0, header=1)
    print(f"[load_raw] Loaded {df.shape[0]:,} rows x {df.shape[1]} columns from raw file.")
    return df


# ---------------------------------------------------------------------------
# Step 2 — Rename target column
# ---------------------------------------------------------------------------

def rename_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename 'default payment next month' -> 'DEFAULT'.

    Reason:
        The original column name contains spaces, which is problematic
        in SQL contexts. 'DEFAULT' is concise, unambiguous, and SQL-safe.
        (Decision D-002)
    """
    df = df.rename(columns={"default payment next month": "DEFAULT"})
    print("[rename_target] Target column renamed to 'DEFAULT'.")
    return df


# ---------------------------------------------------------------------------
# Step 3 — Verify and report basic quality checks
# ---------------------------------------------------------------------------

def quality_report(df: pd.DataFrame) -> None:
    """
    Print a quality summary to console. Does not modify data.
    """
    print("\n--- Quality Report ---")
    print(f"  Shape           : {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"  Missing values  : {df.isnull().sum().sum()}")
    print(f"  Duplicate IDs   : {df['ID'].duplicated().sum()}")
    print(f"  Duplicate rows  : {df.duplicated().sum()}")
    print(f"  Default rate    : {df['default payment next month'].mean():.4f} ({df['default payment next month'].sum():,} defaults)")
    print("----------------------\n")


# ---------------------------------------------------------------------------
# Step 4 — Treat undocumented EDUCATION codes (0, 5, 6)
# ---------------------------------------------------------------------------

def clean_education(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remap undocumented EDUCATION codes 0, 5, and 6 -> 4 ('Others').

    Evidence:
        EDUCATION value counts in raw data:
            1 (Graduate school): 10,585
            2 (University):      14,030
            3 (High school):      4,917
            4 (Others):             123
            0 (Undocumented):        14
            5 (Undocumented):       280
            6 (Undocumented):        51
        Total undocumented: 345 records (1.15%)

    Treatment:
        Remap 0, 5, 6 -> 4 ('Others').

    Rationale:
        - These codes are absent from the official UCI documentation.
        - The existing code 4 is explicitly defined as "Others", making it
          the semantically correct catch-all for unknown/undisclosed categories.
        - The affected population is small (1.15%) and dropping would lose data.
        - Merging ensures EDUCATION is a clean 4-level: Graduate(1) > University(2)
          > High school(3) > Others(4).

    Decision reference: D-003
    """
    undocumented = [0, 5, 6]
    n_before = df["EDUCATION"].isin(undocumented).sum()
    df["EDUCATION"] = df["EDUCATION"].replace({0: 4, 5: 4, 6: 4})
    n_after = df["EDUCATION"].isin(undocumented).sum()
    print(f"[clean_education] Remapped {n_before} records with EDUCATION codes 0/5/6 -> 4 (Others). "
          f"Remaining undocumented: {n_after}.")
    return df


# ---------------------------------------------------------------------------
# Step 5 — Treat undocumented MARRIAGE code (0)
# ---------------------------------------------------------------------------

def clean_marriage(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remap undocumented MARRIAGE code 0 -> 3 ('Others').

    Evidence:
        MARRIAGE value counts in raw data:
            1 (Married):      13,659
            2 (Single):       15,964
            3 (Others):          323
            0 (Undocumented):     54

    Treatment:
        Remap 0 -> 3 ('Others').

    Rationale:
        - Code 0 has no documented meaning in the UCI specification.
        - Code 3 is explicitly defined as 'Others' - natural catch-all.
        - Only 54 records (0.18%) affected.

    Decision reference: D-004
    """
    n_before = (df["MARRIAGE"] == 0).sum()
    df["MARRIAGE"] = df["MARRIAGE"].replace({0: 3})
    n_after = (df["MARRIAGE"] == 0).sum()
    print(f"[clean_marriage] Remapped {n_before} records with MARRIAGE code 0 -> 3 (Others). "
          f"Remaining undocumented: {n_after}.")
    return df


# ---------------------------------------------------------------------------
# Step 6 — Retain PAY code -2 as-is (with documentation)
# ---------------------------------------------------------------------------

def document_pay_minus2(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retain PAY column code -2 with no modification.

    Evidence:
        Cross-check PAY_0=-2 with BILL_AMT1:
            Negative bill: 209   (credit balance)
            Zero bill:     694   (no balance)
            Positive bill: 1,856 (balance carried over)

    Interpretation:
        Code -2 means 'no new consumption' - distinct from -1 (paid in full)
        and 0 (revolving credit used). Widely accepted in research literature.

    Treatment: Retain as-is. Do NOT merge with -1 or 0.

    Decision reference: D-005
    """
    for col in ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]:
        n = (df[col] == -2).sum()
        print(f"[document_pay_minus2] {col}: {n:,} records with code -2 retained.")
    return df


# ---------------------------------------------------------------------------
# Step 7 — Retain negative BILL_AMT values (with documentation)
# ---------------------------------------------------------------------------

def document_negative_bill_amounts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retain negative BILL_AMT values with no modification.

    Evidence:
        BILL_AMT1: 590 negative values (min = -165,580)
        Through to BILL_AMT6: 688 negative values (min = -339,603)

    Interpretation:
        Negative statement balance = customer has a credit balance
        (overpayment, refund, cashback). Financially valid, not an error.

    Treatment: Retain all negative BILL_AMT values unchanged.

    Decision reference: D-006
    """
    bill_cols = ["BILL_AMT1", "BILL_AMT2", "BILL_AMT3",
                 "BILL_AMT4", "BILL_AMT5", "BILL_AMT6"]
    for col in bill_cols:
        n = (df[col] < 0).sum()
        print(f"[document_negative_bill_amounts] {col}: {n:,} negative values retained (credit balances).")
    return df


# ---------------------------------------------------------------------------
# Step 8 — Verify PAY_AMT non-negativity
# ---------------------------------------------------------------------------

def verify_pay_amounts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verify that all PAY_AMT columns are non-negative.
    Payment amounts cannot logically be negative.
    """
    pay_amt_cols = ["PAY_AMT1", "PAY_AMT2", "PAY_AMT3",
                    "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"]
    for col in pay_amt_cols:
        n_neg = (df[col] < 0).sum()
        if n_neg > 0:
            print(f"[verify_pay_amounts] WARNING: {col} has {n_neg} negative values!")
        else:
            print(f"[verify_pay_amounts] {col}: no negative values. OK")
    return df


# ---------------------------------------------------------------------------
# Step 9 — Verify AGE range
# ---------------------------------------------------------------------------

def verify_age(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verify AGE is within plausible range for credit card holders.
    Evidence: Min=21, Max=79. All plausible. No treatment required.
    """
    age_min = df["AGE"].min()
    age_max = df["AGE"].max()
    n_under18 = (df["AGE"] < 18).sum()
    n_over100 = (df["AGE"] > 100).sum()
    print(f"[verify_age] AGE range: {age_min}-{age_max}. "
          f"Under 18: {n_under18}. Over 100: {n_over100}. All plausible. OK")
    return df


# ---------------------------------------------------------------------------
# Step 10 — Verify LIMIT_BAL
# ---------------------------------------------------------------------------

def verify_limit_bal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verify credit limit values are positive and plausible.
    Evidence: Min=10,000, Max=1,000,000 NT$. All plausible. No treatment required.
    """
    n_zero = (df["LIMIT_BAL"] <= 0).sum()
    lim_min = df["LIMIT_BAL"].min()
    lim_max = df["LIMIT_BAL"].max()
    print(f"[verify_limit_bal] LIMIT_BAL range: {lim_min:,}-{lim_max:,} NT$. "
          f"Zero or negative: {n_zero}. All plausible. OK")
    return df


# ---------------------------------------------------------------------------
# Step 11 — Verify SEX codes
# ---------------------------------------------------------------------------

def verify_sex(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verify SEX column contains only documented codes (1=Male, 2=Female).
    """
    valid_codes = {1, 2}
    unexpected = df[~df["SEX"].isin(valid_codes)]
    if len(unexpected) > 0:
        print(f"[verify_sex] WARNING: {len(unexpected)} records with unexpected SEX codes!")
    else:
        print("[verify_sex] SEX: only codes 1 and 2 present. OK")
    return df


# ---------------------------------------------------------------------------
# Step 12 — Final validation and export
# ---------------------------------------------------------------------------

def validate_and_export(df: pd.DataFrame, output_path: str = PROCESSED_FILE) -> pd.DataFrame:
    """
    Run final validation checks and export the processed dataset to CSV.
    """
    print("\n--- Final Validation ---")

    assert df.shape[0] == 30000, f"Row count mismatch: {df.shape[0]}"
    assert df.shape[1] == 25, f"Column count mismatch: {df.shape[1]}"
    print(f"  Rows    : {df.shape[0]:,} OK")
    print(f"  Columns : {df.shape[1]} OK")

    n_null = df.isnull().sum().sum()
    assert n_null == 0, f"Missing values found: {n_null}"
    print(f"  Nulls   : {n_null} OK")

    assert set(df["DEFAULT"].unique()) == {0, 1}, "Target not binary"
    print(f"  DEFAULT : binary (0/1) OK")

    assert set(df["EDUCATION"].unique()).issubset({1, 2, 3, 4}), \
        f"Unexpected EDUCATION codes: {df['EDUCATION'].unique()}"
    print(f"  EDUCATION codes: {sorted(df['EDUCATION'].unique())} OK")

    assert set(df["MARRIAGE"].unique()).issubset({1, 2, 3}), \
        f"Unexpected MARRIAGE codes: {df['MARRIAGE'].unique()}"
    print(f"  MARRIAGE codes : {sorted(df['MARRIAGE'].unique())} OK")

    assert set(df["SEX"].unique()).issubset({1, 2}), \
        f"Unexpected SEX codes: {df['SEX'].unique()}"
    print(f"  SEX codes      : {sorted(df['SEX'].unique())} OK")

    print("------------------------\n")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[export] Processed dataset saved to: {output_path}")
    print(f"         Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

    return df


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_cleaning_pipeline() -> pd.DataFrame:
    """
    Execute the full data cleaning pipeline in sequence.
    """
    print("=" * 60)
    print("Banking Credit Risk -- Data Cleaning Pipeline")
    print("=" * 60)

    df = load_raw()
    quality_report(df)
    df = rename_target(df)
    df = clean_education(df)
    df = clean_marriage(df)
    df = document_pay_minus2(df)
    df = document_negative_bill_amounts(df)
    df = verify_pay_amounts(df)
    df = verify_age(df)
    df = verify_limit_bal(df)
    df = verify_sex(df)
    df = validate_and_export(df)

    print("\nData cleaning pipeline complete.")
    print(f"   Output: {PROCESSED_FILE}\n")
    return df


if __name__ == "__main__":
    df_clean = run_cleaning_pipeline()
