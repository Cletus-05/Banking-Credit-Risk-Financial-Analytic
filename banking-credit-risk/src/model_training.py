# model_training.py
# Banking Credit Risk & Financial Analytics - Phase 6 Model Training & CV Pipeline

import os
import sys
import json
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    roc_auc_score, average_precision_score, f1_score,
    precision_score, recall_score, brier_score_loss, log_loss
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_CSV = os.path.join(BASE_DIR, "data", "processed", "credit_risk_features.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Explicit Column Categorization
CATEGORICAL_COLS = ["SEX", "EDUCATION", "MARRIAGE"]
CONTINUOUS_COLS = [
    "LIMIT_BAL", "AGE",
    "BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6",
    "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6",
    "UTIL1", "AVG_BILL_AMT", "AVG_UTIL", "MAX_UTIL",
    "AVG_PAY_AMT", "PAY_TO_BILL_1", "TOTAL_PAY_TO_BILL",
    "BILL_AMT_CHANGE", "PAY_AMT_CHANGE", "LIMIT_BAL_LOG"
]
ORDINAL_BINARY_COLS = [
    "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
    "MAX_PAY_DELAY", "DELAY_MONTHS_COUNT", "RECENT_DELAY", "CONSEC_DELAY", "DELINQUENCY_TREND",
    "OVER_LIMIT_FLAG", "ZERO_BILL_1", "CREDIT_BAL_1", "ZERO_PAY_COUNT"
]


def load_and_split_data(features_path: str = FEATURES_CSV, test_size: float = 0.20, random_state: int = 42):
    if not os.path.exists(features_path):
        raise FileNotFoundError(f"Features dataset not found at: {features_path}")
    
    df = pd.read_csv(features_path)
    print(f"[load_and_split_data] Loaded features dataset: {df.shape}")
    
    # Exclude ID and target DEFAULT from predictive feature matrix X
    X = df.drop(columns=["ID", "DEFAULT"])
    y = df["DEFAULT"]
    
    # 80/20 Stratified train/test partition
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    print(f"[load_and_split_data] Training set: {X_train.shape} (Default rate: {y_train.mean():.4f})")
    print(f"[load_and_split_data] Sealed Test set: {X_test.shape} (Default rate: {y_test.mean():.4f}) [HELD OUT]")
    
    return X_train, X_test, y_train, y_test


def build_preprocessors():
    # 1. Preprocessor for Linear Models: OneHotEncode categoricals + StandardScaler on continuous
    preprocessor_linear = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", drop="first"), CATEGORICAL_COLS),
            ("num", StandardScaler(), CONTINUOUS_COLS)
        ],
        remainder="passthrough"
    )
    
    # 2. Preprocessor for Tree & Boosting Models: OneHotEncode categoricals + passthrough numeric
    preprocessor_trees = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", drop="first"), CATEGORICAL_COLS)
        ],
        remainder="passthrough"
    )
    
    return preprocessor_linear, preprocessor_trees


def get_model_pipelines(random_state: int = 42) -> dict:
    prep_linear, prep_trees = build_preprocessors()
    
    models = {
        "Logistic_Regression": Pipeline([
            ("preprocessor", prep_linear),
            ("clf", LogisticRegression(
                class_weight="balanced",
                max_iter=1000,
                C=1.0,
                random_state=random_state
            ))
        ]),
        "Random_Forest": Pipeline([
            ("preprocessor", prep_trees),
            ("clf", RandomForestClassifier(
                n_estimators=200,
                max_depth=12,
                min_samples_split=10,
                min_samples_leaf=4,
                class_weight="balanced",
                random_state=random_state,
                n_jobs=-1
            ))
        ]),
        "Hist_Gradient_Boosting": Pipeline([
            ("preprocessor", prep_trees),
            ("clf", HistGradientBoostingClassifier(
                class_weight="balanced",
                max_iter=150,
                max_depth=6,
                min_samples_leaf=20,
                learning_rate=0.08,
                random_state=random_state
            ))
        ])
    }
    return models


def cross_validate_models(X_train: pd.DataFrame, y_train: pd.Series, models: dict, n_splits: int = 5, random_state: int = 42):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    cv_results = {}
    oof_predictions = {}
    
    print(f"\n[cross_validate_models] Running {n_splits}-Fold Stratified CV on Training Data (N={len(X_train)})...")
    
    for name, pipeline in models.items():
        print(f"  Evaluating: {name} (Fold-level preprocessing fitting)...")
        oof_probs = np.zeros(len(X_train))
        fold_roc_aucs = []
        fold_pr_aucs = []
        fold_f1_defaults = []
        
        for fold, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train), 1):
            X_tr, y_tr = X_train.iloc[train_idx], y_train.iloc[train_idx]
            X_val, y_val = X_train.iloc[val_idx], y_train.iloc[val_idx]
            
            # Fit pipeline (preprocessor + model) ONLY on training fold
            pipeline.fit(X_tr, y_tr)
            val_probs = pipeline.predict_proba(X_val)[:, 1]
            oof_probs[val_idx] = val_probs
            
            fold_roc_aucs.append(roc_auc_score(y_val, val_probs))
            fold_pr_aucs.append(average_precision_score(y_val, val_probs))
            fold_f1_defaults.append(f1_score(y_val, (val_probs >= 0.50).astype(int)))
            
        cv_results[name] = {
            "PR_AUC_Mean": float(np.mean(fold_pr_aucs)),
            "PR_AUC_Std": float(np.std(fold_pr_aucs)),
            "ROC_AUC_Mean": float(np.mean(fold_roc_aucs)),
            "ROC_AUC_Std": float(np.std(fold_roc_aucs)),
            "F1_Default_Mean": float(np.mean(fold_f1_defaults)),
            "F1_Default_Std": float(np.std(fold_f1_defaults)),
            "Brier_Score": float(brier_score_loss(y_train, oof_probs)),
            "Log_Loss": float(log_loss(y_train, oof_probs))
        }
        oof_predictions[name] = oof_probs
        print(f"    -> PR-AUC: {cv_results[name]['PR_AUC_Mean']:.4f} (+/- {cv_results[name]['PR_AUC_Std']:.4f}) | ROC-AUC: {cv_results[name]['ROC_AUC_Mean']:.4f}")
        
    return cv_results, oof_predictions


def find_optimal_threshold(y_true: pd.Series, y_probs: np.ndarray) -> dict:
    thresholds = np.arange(0.10, 0.90, 0.01)
    best_thresh = 0.50
    best_f1 = 0.0
    records = []
    
    for th in thresholds:
        preds = (y_probs >= th).astype(int)
        rec = float(recall_score(y_true, preds, zero_division=0))
        prec = float(precision_score(y_true, preds, zero_division=0))
        f1 = float(f1_score(y_true, preds, zero_division=0))
        
        records.append({
            "threshold": round(float(th), 2),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4)
        })
        
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = th
            
    thresh_df = pd.DataFrame(records)
    return {
        "optimal_threshold": round(float(best_thresh), 2),
        "best_f1_score": round(float(best_f1), 4),
        "threshold_curve": thresh_df
    }


def train_and_persist_pipeline(X_train, y_train, X_test, y_test, champion_name, models, cv_results, thresh_res, oof_preds, output_dir=MODELS_DIR):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Retrain champion pipeline on full training set
    champion_pipeline = models[champion_name]
    print(f"\n[train_and_persist_pipeline] Retraining Champion Pipeline ({champion_name}) on full training set (N={len(X_train)})...")
    champion_pipeline.fit(X_train, y_train)
    
    # 2. Persist fitted champion pipeline
    model_path = os.path.join(output_dir, "credit_risk_champion_model.joblib")
    joblib.dump(champion_pipeline, model_path)
    print(f"[train_and_persist_pipeline] Saved fitted champion pipeline to: {model_path}")
    
    # 3. Persist partitioned data (with sealed test set)
    data_path = os.path.join(output_dir, "train_test_data.joblib")
    joblib.dump({
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test
    }, data_path)
    print(f"[train_and_persist_pipeline] Saved train/test data partitions to: {data_path}")
    
    # 4. Persist training metadata & OOF results
    meta_path = os.path.join(output_dir, "training_metadata.json")
    meta_payload = {
        "champion_model": champion_name,
        "random_state": 42,
        "train_size": len(X_train),
        "test_size": len(X_test),
        "train_default_rate": float(y_train.mean()),
        "test_default_rate": float(y_test.mean()),
        "cv_results": cv_results,
        "optimal_threshold": thresh_res["optimal_threshold"],
        "best_cv_f1_at_optimal_threshold": thresh_res["best_f1_score"]
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_payload, f, indent=2)
    print(f"[train_and_persist_pipeline] Saved training metadata to: {meta_path}")
    
    # 5. Persist OOF predictions for all models
    oof_df = pd.DataFrame(oof_preds, index=X_train.index)
    oof_df["y_true"] = y_train
    oof_path = os.path.join(output_dir, "oof_predictions.csv")
    oof_df.to_csv(oof_path, index=True)
    print(f"[train_and_persist_pipeline] Saved out-of-fold predictions to: {oof_path}")
    
    # 6. Persist threshold tuning curve
    thresh_path = os.path.join(output_dir, "threshold_curve.csv")
    thresh_res["threshold_curve"].to_csv(thresh_path, index=False)
    print(f"[train_and_persist_pipeline] Saved threshold curve to: {thresh_path}")


def run_training_pipeline():
    print("=" * 80)
    print("Banking Credit Risk — Phase 6 Model Training & CV Pipeline")
    print("=" * 80)
    
    # 1. Load and Partition Data (80/20 Stratified)
    X_train, X_test, y_train, y_test = load_and_split_data()
    
    # 2. Initialize Model Pipelines with Encapsulated Preprocessing
    models = get_model_pipelines()
    
    # 3. 5-Fold Stratified Cross-Validation on Training Data ONLY
    cv_results, oof_preds = cross_validate_models(X_train, y_train, models)
    
    # 4. Summary & Comparison Table
    summary_df = pd.DataFrame(cv_results).T
    print("\n" + "=" * 80)
    print("5-Fold Cross-Validation Performance Comparison (Training Data Only):")
    print("=" * 80)
    print(summary_df[["PR_AUC_Mean", "PR_AUC_Std", "ROC_AUC_Mean", "ROC_AUC_Std", "F1_Default_Mean", "Brier_Score", "Log_Loss"]].round(4).to_string())
    
    # 5. Select Champion Model based on primary ranking metric PR-AUC
    champion_name = summary_df["PR_AUC_Mean"].idxmax()
    print(f"\n>>> CHAMPION MODEL SELECTED: {champion_name} <<<")
    print(f"    Mean CV PR-AUC : {summary_df.loc[champion_name, 'PR_AUC_Mean']:.4f} (+/- {summary_df.loc[champion_name, 'PR_AUC_Std']:.4f})")
    print(f"    Mean CV ROC-AUC: {summary_df.loc[champion_name, 'ROC_AUC_Mean']:.4f} (+/- {summary_df.loc[champion_name, 'ROC_AUC_Std']:.4f})")
    
    # 6. Optimize Classification Threshold using Champion OOF Predictions ONLY
    thresh_res = find_optimal_threshold(y_train, oof_preds[champion_name])
    print(f"\n>>> THRESHOLD CALIBRATION (Training OOF Only) <<<")
    print(f"    Default Threshold (0.50) CV F1: {f1_score(y_train, (oof_preds[champion_name] >= 0.50).astype(int)):.4f}")
    print(f"    Optimal Threshold ({thresh_res['optimal_threshold']}) CV F1: {thresh_res['best_f1_score']:.4f}")
    
    # 7. Retrain & Persist Champion Pipeline (Test Set Remains Sealed)
    train_and_persist_pipeline(X_train, y_train, X_test, y_test, champion_name, models, cv_results, thresh_res, oof_preds)
    
    print("\n" + "=" * 80)
    print("Phase 6 Model Training & Cross-Validation Pipeline Completed Successfully.")
    print("Test set remains SEALED and UNTOUCHED.")
    print("=" * 80)


if __name__ == "__main__":
    run_training_pipeline()
