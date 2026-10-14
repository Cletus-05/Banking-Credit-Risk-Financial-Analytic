# model_evaluation.py
# Banking Credit Risk & Financial Analytics — Phase 7 Final Model Evaluation Module

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.metrics import (
    roc_auc_score, average_precision_score, f1_score,
    precision_score, recall_score, accuracy_score,
    brier_score_loss, log_loss, confusion_matrix,
    roc_curve, precision_recall_curve, auc
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
FIGURES_DIR = os.path.join(BASE_DIR, "data", "processed", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Clean visualization formatting
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10})


def load_assets():
    """Load train/test data, training metadata, and champion model."""
    data = joblib.load(os.path.join(MODELS_DIR, "train_test_data.joblib"))
    with open(os.path.join(MODELS_DIR, "training_metadata.json"), "r") as f:
        meta = json.load(f)
    champion_pipeline = joblib.load(os.path.join(MODELS_DIR, "credit_risk_champion_model.joblib"))
    
    # Import model builder to re-fit baseline models on full training data for final comparison
    sys.path.append(os.path.join(BASE_DIR, "src"))
    from model_training import get_model_pipelines
    all_models = get_model_pipelines(random_state=42)
    
    return data["X_train"], data["y_train"], data["X_test"], data["y_test"], meta, champion_pipeline, all_models


def evaluate_all_models_on_test(X_train, y_train, X_test, y_test, all_models):
    """Fit all 3 models on full training set and evaluate single holdout test performance."""
    print("\n[evaluate_all_models_on_test] Evaluating all 3 model architectures on Sealed Test Set (N=6,000)...")
    results = {}
    test_probs = {}
    
    for name, pipeline in all_models.items():
        print(f"  Fitting & testing: {name}...")
        pipeline.fit(X_train, y_train)
        probs = pipeline.predict_proba(X_test)[:, 1]
        preds_default = (probs >= 0.50).astype(int)
        
        results[name] = {
            "PR_AUC": float(average_precision_score(y_test, probs)),
            "ROC_AUC": float(roc_auc_score(y_test, probs)),
            "Accuracy_0.50": float(accuracy_score(y_test, preds_default)),
            "Precision_0.50": float(precision_score(y_test, preds_default, zero_division=0)),
            "Recall_0.50": float(recall_score(y_test, preds_default, zero_division=0)),
            "F1_0.50": float(f1_score(y_test, preds_default, zero_division=0)),
            "Brier_Score": float(brier_score_loss(y_test, probs)),
            "Log_Loss": float(log_loss(y_test, probs))
        }
        test_probs[name] = probs
        print(f"    -> Test PR-AUC: {results[name]['PR_AUC']:.4f} | Test ROC-AUC: {results[name]['ROC_AUC']:.4f} | Test F1: {results[name]['F1_0.50']:.4f}")
        
    return results, test_probs


def evaluate_champion_thresholds(y_test, champion_probs, opt_threshold):
    """
    Evaluate champion model across multiple operating business thresholds.
    Includes an illustrative business cost scenario for decision trade-off analysis.
    """
    thresholds = [0.40, 0.50, opt_threshold, 0.70]
    thresh_names = ["High_Recall (0.40)", "Default_Cutoff (0.50)", f"Optimal_F1 ({opt_threshold:.2f})", "High_Precision (0.70)"]
    
    records = {}
    
    # Illustrative financial cost parameters (for business scenario simulation only)
    # Scenario: Assumes illustrative unmitigated default loss of 33,750 NT$ per false negative
    # and illustrative collections/review operational friction of 1,500 NT$ per false positive.
    ILLUSTRATIVE_COST_FN = 33750
    ILLUSTRATIVE_COST_FP = 1500
    
    unmitigated_loss = int(y_test.sum() * ILLUSTRATIVE_COST_FN)
    
    print("\n[evaluate_champion_thresholds] Evaluating Champion Policy Across Operating Cutoffs:")
    print("  (Cost metrics represent an illustrative business simulation scenario)")
    for th, tname in zip(thresholds, thresh_names):
        preds = (champion_probs >= th).astype(int)
        cm = confusion_matrix(y_test, preds)
        tn, fp, fn, tp = cm.ravel()
        
        acc = float(accuracy_score(y_test, preds))
        prec = float(precision_score(y_test, preds, zero_division=0))
        rec = float(recall_score(y_test, preds, zero_division=0))
        f1 = float(f1_score(y_test, preds, zero_division=0))
        
        total_cost = int((fn * ILLUSTRATIVE_COST_FN) + (fp * ILLUSTRATIVE_COST_FP))
        cost_savings = int(unmitigated_loss - total_cost)
        savings_pct = float(cost_savings / unmitigated_loss * 100)
        
        records[tname] = {
            "Threshold": th,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1_Score": f1,
            "TN": int(tn),
            "FP": int(fp),
            "FN": int(fn),
            "TP": int(tp),
            "Illustrative_Total_Cost_NTD": total_cost,
            "Illustrative_Cost_Savings_NTD": cost_savings,
            "Illustrative_Savings_Pct": savings_pct
        }
        print(f"  {tname:<25} -> Precision: {prec*100:.2f}% | Recall: {rec*100:.2f}% | F1: {f1:.4f} | Illus. Cost: {total_cost:,} NT$ (Savings: {savings_pct:.1f}%)")
        
    return records


def generate_evaluation_figures(y_test, test_probs, champion_probs, cv_meta, opt_threshold, champ_thresh_results):
    """Generate publication-ready figures for Phase 7."""
    print("\n[generate_evaluation_figures] Generating Phase 7 Evaluation Visualizations...")
    
    # ---------------------------------------------------------------------------
    # Figure 15: Confusion Matrices (Default 0.50 vs Optimal 0.56)
    # ---------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    cm_050 = confusion_matrix(y_test, (champion_probs >= 0.50).astype(int))
    cm_opt = confusion_matrix(y_test, (champion_probs >= opt_threshold).astype(int))
    
    sns.heatmap(cm_050, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax1,
                xticklabels=["Non-Default (0)", "Default (1)"], yticklabels=["Non-Default (0)", "Default (1)"])
    ax1.set_title(f"Default Cutoff (τ = 0.50)\nPrecision: {champ_thresh_results['Default_Cutoff (0.50)']['Precision']*100:.2f}% | Recall: {champ_thresh_results['Default_Cutoff (0.50)']['Recall']*100:.2f}%")
    ax1.set_xlabel("Predicted Class")
    ax1.set_ylabel("Actual Class")
    
    sns.heatmap(cm_opt, annot=True, fmt="d", cmap="Greens", cbar=False, ax=ax2,
                xticklabels=["Non-Default (0)", "Default (1)"], yticklabels=["Non-Default (0)", "Default (1)"])
    ax2.set_title(f"Optimal Threshold (τ* = {opt_threshold:.2f})\nPrecision: {champ_thresh_results[f'Optimal_F1 ({opt_threshold:.2f})']['Precision']*100:.2f}% | Recall: {champ_thresh_results[f'Optimal_F1 ({opt_threshold:.2f})']['Recall']*100:.2f}%")
    ax2.set_xlabel("Predicted Class")
    ax2.set_ylabel("Actual Class")
    
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig15_final_test_confusion_matrices.png"), dpi=300)
    plt.close(fig)
    print("  Saved: fig15_final_test_confusion_matrices.png")
    
    # ---------------------------------------------------------------------------
    # Figure 16: Test Set ROC and Precision-Recall Curves
    # ---------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    colors = {"Logistic_Regression": "#3498db", "Random_Forest": "#2ecc71", "Hist_Gradient_Boosting": "#e74c3c"}
    clean_names = {"Logistic_Regression": "Logistic Regression", "Random_Forest": "Random Forest", "Hist_Gradient_Boosting": "Hist Gradient Boosting (Champion)"}
    
    for m, probs in test_probs.items():
        fpr, tpr, _ = roc_curve(y_test, probs)
        roc_val = auc(fpr, tpr)
        ax1.plot(fpr, tpr, label=f"{clean_names[m]} (AUC = {roc_val:.4f})", color=colors[m], linewidth=2)
        
    ax1.plot([0, 1], [0, 1], "k--", alpha=0.6, label="Random Guess (AUC = 0.5000)")
    ax1.set_title("Final Holdout Test ROC Curves (N=6,000)")
    ax1.set_xlabel("False Positive Rate (1 - Specificity)")
    ax1.set_ylabel("True Positive Rate (Recall)")
    ax1.legend(loc="lower right")
    
    for m, probs in test_probs.items():
        prec, rec, _ = precision_recall_curve(y_test, probs)
        pr_val = average_precision_score(y_test, probs)
        ax2.plot(rec, prec, label=f"{clean_names[m]} (AP = {pr_val:.4f})", color=colors[m], linewidth=2)
        
    baseline = y_test.mean()
    ax2.axhline(baseline, color="k", linestyle="--", alpha=0.6, label=f"No-Skill Baseline ({baseline:.4f})")
    ax2.set_title("Final Holdout Test Precision-Recall Curves (N=6,000)")
    ax2.set_xlabel("Recall (True Positive Rate)")
    ax2.set_ylabel("Precision (Positive Predictive Value)")
    ax2.legend(loc="upper right")
    
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig16_final_test_roc_pr_curves.png"), dpi=300)
    plt.close(fig)
    print("  Saved: fig16_final_test_roc_pr_curves.png")
    
    # ---------------------------------------------------------------------------
    # Figure 17: Train CV vs Final Test Generalization Comparison
    # ---------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    models = ["Logistic_Regression", "Random_Forest", "Hist_Gradient_Boosting"]
    x = np.arange(len(models))
    width = 0.35
    
    cv_pr = [cv_meta["cv_results"][m]["PR_AUC_Mean"] for m in models]
    test_pr = [average_precision_score(y_test, test_probs[m]) for m in models]
    
    ax1.bar(x - width/2, cv_pr, width, label="5-Fold Train CV", color="#34495e", alpha=0.85, edgecolor="black")
    ax1.bar(x + width/2, test_pr, width, label="Final Test Set", color="#3498db", alpha=0.85, edgecolor="black")
    ax1.set_title("Generalization: PR-AUC (Train CV vs Final Test)")
    ax1.set_ylabel("PR-AUC Score")
    ax1.set_xticks(x)
    ax1.set_xticklabels([clean_names[m].replace(" (Champion)", "") for m in models], rotation=10)
    ax1.set_ylim(0.40, 0.65)
    ax1.legend(loc="lower right")
    
    cv_roc = [cv_meta["cv_results"][m]["ROC_AUC_Mean"] for m in models]
    test_roc = [roc_auc_score(y_test, test_probs[m]) for m in models]
    
    ax2.bar(x - width/2, cv_roc, width, label="5-Fold Train CV", color="#34495e", alpha=0.85, edgecolor="black")
    ax2.bar(x + width/2, test_roc, width, label="Final Test Set", color="#2ecc71", alpha=0.85, edgecolor="black")
    ax2.set_title("Generalization: ROC-AUC (Train CV vs Final Test)")
    ax2.set_ylabel("ROC-AUC Score")
    ax2.set_xticks(x)
    ax2.set_xticklabels([clean_names[m].replace(" (Champion)", "") for m in models], rotation=10)
    ax2.set_ylim(0.70, 0.85)
    ax2.legend(loc="lower right")
    
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig17_train_vs_test_generalization.png"), dpi=300)
    plt.close(fig)
    print("  Saved: fig17_train_vs_test_generalization.png")
    
    # ---------------------------------------------------------------------------
    # Figure 18: Illustrative Financial Cost Curve & Portfolio Savings Scenario
    # ---------------------------------------------------------------------------
    thresholds_range = np.arange(0.10, 0.90, 0.01)
    costs = []
    savings = []
    ILLUSTRATIVE_COST_FN = 33750
    ILLUSTRATIVE_COST_FP = 1500
    unmitigated = int(y_test.sum() * ILLUSTRATIVE_COST_FN)
    
    for th in thresholds_range:
        p = (champion_probs >= th).astype(int)
        cm = confusion_matrix(y_test, p)
        tn, fp, fn, tp = cm.ravel()
        c = (fn * ILLUSTRATIVE_COST_FN) + (fp * ILLUSTRATIVE_COST_FP)
        costs.append(c / 1e6)  # Millions NT$
        savings.append((unmitigated - c) / 1e6)
        
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(thresholds_range, costs, color="#e74c3c", linewidth=2.5, label="Expected Total Cost (FN Loss + FP Outreach)")
    ax.plot(thresholds_range, savings, color="#2ecc71", linewidth=2.5, label="Net Cost Savings vs Unmitigated Baseline")
    ax.axhline(unmitigated / 1e6, color="black", linestyle="--", label=f"Unmitigated Baseline Loss ({unmitigated/1e6:.2f}M NT$)")
    ax.axvline(opt_threshold, color="purple", linestyle=":", linewidth=2, label=f"Optimal Decision Cutoff (τ* = {opt_threshold:.2f})")
    
    ax.set_title("Illustrative Financial Cost & Savings Scenario Across Decision Thresholds (Test Set)")
    ax.set_xlabel("Decision Threshold (Probability Cutoff)")
    ax.set_ylabel("Amount (Millions NT$)")
    ax.legend(loc="center right")
    
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig18_financial_cost_curve.png"), dpi=300)
    plt.close(fig)
    print("  Saved: fig18_financial_cost_curve.png")


def run_evaluation_pipeline():
    print("=" * 80)
    print("Banking Credit Risk — Phase 7 Final Model Evaluation & Test Assessment")
    print("=" * 80)
    
    X_train, y_train, X_test, y_test, meta, champion_pipeline, all_models = load_assets()
    opt_threshold = meta["optimal_threshold"]
    
    # 1. Evaluate all models on test set
    test_metrics, test_probs = evaluate_all_models_on_test(X_train, y_train, X_test, y_test, all_models)
    
    # 2. Evaluate champion model across operating thresholds
    champion_probs = test_probs["Hist_Gradient_Boosting"]
    champ_thresh_results = evaluate_champion_thresholds(y_test, champion_probs, opt_threshold)
    
    # 3. Generate diagnostic figures
    generate_evaluation_figures(y_test, test_probs, champion_probs, meta, opt_threshold, champ_thresh_results)
    
    # 4. Persist test results
    test_results_payload = {
        "test_size": len(y_test),
        "test_default_count": int(y_test.sum()),
        "test_non_default_count": int((y_test == 0).sum()),
        "test_default_rate": float(y_test.mean()),
        "champion_model": meta["champion_model"],
        "optimal_threshold": opt_threshold,
        "all_models_test_metrics": test_metrics,
        "champion_threshold_analysis": champ_thresh_results
    }
    
    res_path = os.path.join(MODELS_DIR, "test_evaluation_results.json")
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump(test_results_payload, f, indent=2)
    print(f"\n[run_evaluation_pipeline] Saved test evaluation results to: {res_path}")
    
    test_preds_df = pd.DataFrame(test_probs, index=X_test.index)
    test_preds_df["y_true"] = y_test
    test_preds_path = os.path.join(MODELS_DIR, "test_predictions.csv")
    test_preds_df.to_csv(test_preds_path, index=True)
    print(f"[run_evaluation_pipeline] Saved test predictions to: {test_preds_path}")
    
    print("\n" + "=" * 80)
    print("Phase 7 Model Evaluation & Test Assessment Completed Successfully.")
    print("=" * 80)


if __name__ == "__main__":
    run_evaluation_pipeline()
