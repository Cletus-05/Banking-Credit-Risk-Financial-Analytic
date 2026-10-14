# export_powerbi_data.py
# Banking Credit Risk & Financial Analytics — Phase 8 Power BI Export Module

import os
import json
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(PROCESSED_DIR, exist_ok=True)


def export_powerbi_datasets():
    print("=" * 80)
    print("Exporting Power BI Datasets from Verified Project Artifacts...")
    print("=" * 80)
    
    # ---------------------------------------------------------------------------
    # 1. Primary Fact Table: powerbi_credit_risk_dataset.csv (30,000 rows)
    # ---------------------------------------------------------------------------
    feat_path = os.path.join(PROCESSED_DIR, "credit_risk_features.csv")
    df_feat = pd.read_csv(feat_path)
    
    # Load train/test data to assign explicit partition tags
    tt_data = joblib.load(os.path.join(MODELS_DIR, "train_test_data.joblib"))
    test_indices = set(tt_data["X_test"].index)
    
    # Load test predictions
    test_preds = pd.read_csv(os.path.join(MODELS_DIR, "test_predictions.csv"), index_col=0)
    
    # Create enriched customer dataset for Power BI
    df_pbi = df_feat.copy()
    
    # Partition flag
    df_pbi["SPLIT"] = np.where(df_pbi.index.isin(test_indices), "Test", "Train")
    
    # Human-readable demographic labels
    edu_map = {1: "Graduate School", 2: "University", 3: "High School", 4: "Others"}
    marr_map = {1: "Married", 2: "Single", 3: "Others"}
    sex_map = {1: "Male", 2: "Female"}
    
    df_pbi["EDUCATION_LABEL"] = df_pbi["EDUCATION"].map(edu_map)
    df_pbi["MARRIAGE_LABEL"] = df_pbi["MARRIAGE"].map(marr_map)
    df_pbi["SEX_LABEL"] = df_pbi["SEX"].map(sex_map)
    
    # Age grouping
    age_bins = [18, 25, 35, 45, 55, 65, 100]
    age_labels = ["20-25", "26-35", "36-45", "46-55", "56-65", "65+"]
    df_pbi["AGE_GROUP"] = pd.cut(df_pbi["AGE"], bins=age_bins, labels=age_labels, right=True)
    
    # Credit limit tier
    limit_bins = [0, 50000, 100000, 200000, 300000, 500000, 1500000]
    limit_labels = ["<50k", "50k-100k", "100k-200k", "200k-300k", "300k-500k", ">500k"]
    df_pbi["LIMIT_BAL_TIER"] = pd.cut(df_pbi["LIMIT_BAL"], bins=limit_bins, labels=limit_labels, right=True)
    
    # Repayment status label for PAY_0
    pay_labels = {
        -2: "No Consumption (-2)",
        -1: "Paid in Full (-1)",
        0: "Revolving Credit (0)",
        1: "1-Month Delay (1)",
        2: "2-Month Delay (2)",
        3: "3-Month Delay (3)",
        4: "4-Month Delay (4)",
        5: "5-Month Delay (5)",
        6: "6-Month Delay (6)",
        7: "7-Month Delay (7)",
        8: "8-Month Delay (8)"
    }
    df_pbi["PAY_0_LABEL"] = df_pbi["PAY_0"].map(pay_labels)
    
    # Utilisation tier
    util_bins = [-1.0, 0.0, 0.20, 0.50, 0.80, 1.0, 15.0]
    util_labels = ["Credit Balance (<=0%)", "Low (0-20%)", "Moderate (20-50%)", "High (50-80%)", "Very High (80-100%)", "Over-Limit (>100%)"]
    df_pbi["AVG_UTIL_TIER"] = pd.cut(df_pbi["AVG_UTIL"], bins=util_bins, labels=util_labels, right=True)
    
    # Attach test predictions ONLY to the 6,000 test observations (NaN for training records)
    df_pbi["CHAMPION_PRED_PROB"] = np.nan
    df_pbi.loc[test_preds.index, "CHAMPION_PRED_PROB"] = test_preds["Hist_Gradient_Boosting"]
    
    # Pre-calibrated F1-optimized threshold (0.56) flag for test records
    df_pbi["FLAGGED_AT_0_56"] = np.nan
    df_pbi.loc[test_preds.index, "FLAGGED_AT_0_56"] = (test_preds["Hist_Gradient_Boosting"] >= 0.56).astype(int)
    
    out_fact_csv = os.path.join(PROCESSED_DIR, "powerbi_credit_risk_dataset.csv")
    df_pbi.to_csv(out_fact_csv, index=False)
    print(f"1. Saved primary customer dataset to: {out_fact_csv} (Shape: {df_pbi.shape})")
    
    # ---------------------------------------------------------------------------
    # 2. Supporting Table: powerbi_ml_metrics_summary.csv (3 rows)
    # ---------------------------------------------------------------------------
    with open(os.path.join(MODELS_DIR, "training_metadata.json"), "r") as f:
        train_meta = json.load(f)
    with open(os.path.join(MODELS_DIR, "test_evaluation_results.json"), "r") as f:
        test_meta = json.load(f)
        
    models_list = ["Logistic_Regression", "Random_Forest", "Hist_Gradient_Boosting"]
    clean_names = ["Logistic Regression", "Random Forest", "Hist Gradient Boosting (Champion)"]
    
    ml_records = []
    for m, cname in zip(models_list, clean_names):
        ml_records.append({
            "Model_ID": m,
            "Model_Name": cname,
            "Is_Champion": "Yes" if "Champion" in cname else "No",
            "Train_CV_PR_AUC_Mean": round(train_meta["cv_results"][m]["PR_AUC_Mean"], 4),
            "Train_CV_PR_AUC_Std": round(train_meta["cv_results"][m]["PR_AUC_Std"], 4),
            "Train_CV_ROC_AUC_Mean": round(train_meta["cv_results"][m]["ROC_AUC_Mean"], 4),
            "Train_CV_ROC_AUC_Std": round(train_meta["cv_results"][m]["ROC_AUC_Std"], 4),
            "Test_PR_AUC": round(test_meta["all_models_test_metrics"][m]["PR_AUC"], 4),
            "Test_ROC_AUC": round(test_meta["all_models_test_metrics"][m]["ROC_AUC"], 4),
            "Test_Accuracy_050": round(test_meta["all_models_test_metrics"][m]["Accuracy_0.50"], 4),
            "Test_Precision_050": round(test_meta["all_models_test_metrics"][m]["Precision_0.50"], 4),
            "Test_Recall_050": round(test_meta["all_models_test_metrics"][m]["Recall_0.50"], 4),
            "Test_F1_050": round(test_meta["all_models_test_metrics"][m]["F1_0.50"], 4),
            "Test_Brier_Score": round(test_meta["all_models_test_metrics"][m]["Brier_Score"], 4),
            "Test_Log_Loss": round(test_meta["all_models_test_metrics"][m]["Log_Loss"], 4)
        })
        
    df_ml = pd.DataFrame(ml_records)
    out_ml_csv = os.path.join(PROCESSED_DIR, "powerbi_ml_metrics_summary.csv")
    df_ml.to_csv(out_ml_csv, index=False)
    print(f"2. Saved ML metrics summary table to: {out_ml_csv} (Shape: {df_ml.shape})")
    
    # ---------------------------------------------------------------------------
    # 3. Supporting Table: powerbi_threshold_tradeoffs.csv (4 rows)
    # ---------------------------------------------------------------------------
    thresh_records = []
    for sname, sdata in test_meta["champion_threshold_analysis"].items():
        thresh_records.append({
            "Policy_Name": sname,
            "Threshold": sdata["Threshold"],
            "Is_Optimal_F1": "Yes" if sdata["Threshold"] == 0.56 else "No",
            "Accuracy": round(sdata["Accuracy"], 4),
            "Precision": round(sdata["Precision"], 4),
            "Recall": round(sdata["Recall"], 4),
            "F1_Score": round(sdata["F1_Score"], 4),
            "True_Negatives_TN": sdata["TN"],
            "False_Positives_FP": sdata["FP"],
            "False_Negatives_FN": sdata["FN"],
            "True_Positives_TP": sdata["TP"],
            "Illustrative_Total_Cost_NTD": sdata["Illustrative_Total_Cost_NTD"],
            "Illustrative_Cost_Savings_NTD": sdata["Illustrative_Cost_Savings_NTD"],
            "Illustrative_Savings_Pct": round(sdata["Illustrative_Savings_Pct"], 2)
        })
        
    df_thresh = pd.DataFrame(thresh_records)
    out_thresh_csv = os.path.join(PROCESSED_DIR, "powerbi_threshold_tradeoffs.csv")
    df_thresh.to_csv(out_thresh_csv, index=False)
    print(f"3. Saved threshold trade-offs table to: {out_thresh_csv} (Shape: {df_thresh.shape})")
    
    print("\n" + "=" * 80)
    print("Power BI Export Completed Successfully!")
    print("=" * 80)


if __name__ == "__main__":
    export_powerbi_datasets()
