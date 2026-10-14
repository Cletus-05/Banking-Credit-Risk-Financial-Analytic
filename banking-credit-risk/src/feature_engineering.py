# feature_engineering.py
# Banking Credit Risk & Financial Analytics - Phase 5 Feature Engineering Module

import os
import sys
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV = os.path.join(BASE_DIR, 'data', 'processed', 'credit_risk_clean.csv')
OUTPUT_CSV = os.path.join(BASE_DIR, 'data', 'processed', 'credit_risk_features.csv')

PAY_COLS = ['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']
BILL_COLS = ['BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6']
PAY_AMT_COLS = ['PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6']


def engineer_delinquency_features(df: pd.DataFrame) -> pd.DataFrame:
    res = pd.DataFrame(index=df.index)
    res['MAX_PAY_DELAY'] = df[PAY_COLS].clip(lower=0).max(axis=1)
    res['DELAY_MONTHS_COUNT'] = (df[PAY_COLS] >= 1).sum(axis=1)
    res['RECENT_DELAY'] = ((df['PAY_0'] >= 1) | (df['PAY_2'] >= 1)).astype(int)
    res['CONSEC_DELAY'] = ((df['PAY_0'] >= 1) & (df['PAY_2'] >= 1)).astype(int)
    res['DELINQUENCY_TREND'] = df['PAY_0'].clip(lower=0) - df['PAY_6'].clip(lower=0)
    return res


def engineer_utilisation_features(df: pd.DataFrame) -> pd.DataFrame:
    res = pd.DataFrame(index=df.index)
    res['UTIL1'] = df['BILL_AMT1'] / df['LIMIT_BAL']
    res['AVG_BILL_AMT'] = df[BILL_COLS].mean(axis=1)
    res['AVG_UTIL'] = res['AVG_BILL_AMT'] / df['LIMIT_BAL']
    res['MAX_UTIL'] = df[BILL_COLS].max(axis=1) / df['LIMIT_BAL']
    res['OVER_LIMIT_FLAG'] = (df[BILL_COLS].max(axis=1) > df['LIMIT_BAL']).astype(int)
    return res


def engineer_payment_ratio_features(df: pd.DataFrame) -> pd.DataFrame:
    res = pd.DataFrame(index=df.index)
    res['AVG_PAY_AMT'] = df[PAY_AMT_COLS].mean(axis=1)
    
    ratio_1 = np.divide(
        df['PAY_AMT1'].values,
        df['BILL_AMT1'].values,
        out=np.zeros(len(df), dtype=float),
        where=(df['BILL_AMT1'].values > 0)
    )
    res['PAY_TO_BILL_1'] = np.where(
        df['BILL_AMT1'] > 0,
        np.clip(ratio_1, 0.0, 2.0),
        0.0
    )
    
    res['ZERO_BILL_1'] = (df['BILL_AMT1'] == 0).astype(int)
    res['CREDIT_BAL_1'] = (df['BILL_AMT1'] < 0).astype(int)
    
    sum_pos_bills = df[BILL_COLS].clip(lower=0).sum(axis=1).values
    sum_payments = df[PAY_AMT_COLS].sum(axis=1).values
    ratio_total = np.divide(
        sum_payments,
        sum_pos_bills,
        out=np.zeros(len(df), dtype=float),
        where=(sum_pos_bills > 0)
    )
    res['TOTAL_PAY_TO_BILL'] = np.where(
        sum_pos_bills > 0,
        np.clip(ratio_total, 0.0, 2.0),
        0.0
    )
    
    res['ZERO_PAY_COUNT'] = (df[PAY_AMT_COLS] == 0).sum(axis=1)
    return res


def engineer_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
    res = pd.DataFrame(index=df.index)
    res['BILL_AMT_CHANGE'] = df['BILL_AMT1'] - df['BILL_AMT6']
    res['PAY_AMT_CHANGE'] = df['PAY_AMT1'] - df['PAY_AMT6']
    res['LIMIT_BAL_LOG'] = np.log(df['LIMIT_BAL'])
    return res


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    print(f'[build_features] Input dataset shape: {df.shape}')
    delinq_df = engineer_delinquency_features(df)
    util_df = engineer_utilisation_features(df)
    pay_df = engineer_payment_ratio_features(df)
    momentum_df = engineer_momentum_features(df)
    
    engineered_df = pd.concat([df, delinq_df, util_df, pay_df, momentum_df], axis=1)
    print(f'[build_features] Engineered dataset shape: {engineered_df.shape}')
    print(f'[build_features] Total new features created: {len(delinq_df.columns) + len(util_df.columns) + len(pay_df.columns) + len(momentum_df.columns)}')
    
    assert engineered_df.isnull().sum().sum() == 0, 'Error: Null values detected in engineered features!'
    assert np.isinf(engineered_df.select_dtypes(include=np.number)).sum().sum() == 0, 'Error: Infinite values detected!'
    assert len(engineered_df) == len(df), f'Error: Row count mismatch! Expected {len(df)}, got {len(engineered_df)}'
    assert (engineered_df['DEFAULT'] == df['DEFAULT']).all(), 'Error: Target column was modified!'
    assert (engineered_df['ID'] == df['ID']).all(), 'Error: ID column was modified!'
    return engineered_df


def run_pipeline(input_path: str = INPUT_CSV, output_path: str = OUTPUT_CSV) -> pd.DataFrame:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f'Input clean CSV not found at: {input_path}')
    df_clean = pd.read_csv(input_path)
    df_features = build_features(df_clean)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_features.to_csv(output_path, index=False)
    print(f'[run_pipeline] Successfully saved engineered features to: {output_path}')
    return df_features


if __name__ == '__main__':
    run_pipeline()
