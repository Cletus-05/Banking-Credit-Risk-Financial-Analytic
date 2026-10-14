# generate_training_diagnostics.py
# Generates Phase 6 CV comparison, threshold curve, and feature interpretability plots

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.inspection import permutation_importance
from sklearn.metrics import precision_recall_curve, roc_curve, auc, average_precision_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
FIGURES_DIR = os.path.join(BASE_DIR, "data", "processed", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Set clean visualization style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10})

# 1. Load Data & OOF Predictions
oof_df = pd.read_csv(os.path.join(MODELS_DIR, "oof_predictions.csv"), index_col=0)
thresh_df = pd.read_csv(os.path.join(MODELS_DIR, "threshold_curve.csv"))
with open(os.path.join(MODELS_DIR, "training_metadata.json"), "r") as f:
    meta = json.load(f)

y_true = oof_df["y_true"]

# ---------------------------------------------------------------------------
# Figure 1: 5-Fold Cross-Validation Model Comparison (PR-AUC vs ROC-AUC)
# ---------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

models = ["Logistic_Regression", "Random_Forest", "Hist_Gradient_Boosting"]
clean_names = ["Logistic Regression", "Random Forest", "Hist Gradient Boosting"]
pr_means = [meta["cv_results"][m]["PR_AUC_Mean"] for m in models]
pr_stds = [meta["cv_results"][m]["PR_AUC_Std"] for m in models]
roc_means = [meta["cv_results"][m]["ROC_AUC_Mean"] for m in models]
roc_stds = [meta["cv_results"][m]["ROC_AUC_Std"] for m in models]

x = np.arange(len(models))
colors = ["#3498db", "#2ecc71", "#e74c3c"]

bars1 = ax1.bar(x, pr_means, yerr=pr_stds, capsize=5, color=colors, alpha=0.85, edgecolor="black")
ax1.set_title("Primary Metric: 5-Fold CV PR-AUC (Average Precision)")
ax1.set_ylabel("PR-AUC Score")
ax1.set_xticks(x)
ax1.set_xticklabels(clean_names, rotation=10)
ax1.set_ylim(0.40, 0.65)
for bar in bars1:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.008, f"{yval:.4f}", ha="center", va="bottom", fontweight="bold")

bars2 = ax2.bar(x, roc_means, yerr=roc_stds, capsize=5, color=colors, alpha=0.85, edgecolor="black")
ax2.set_title("Discrimination Metric: 5-Fold CV ROC-AUC")
ax2.set_ylabel("ROC-AUC Score")
ax2.set_xticks(x)
ax2.set_xticklabels(clean_names, rotation=10)
ax2.set_ylim(0.70, 0.85)
for bar in bars2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.005, f"{yval:.4f}", ha="center", va="bottom", fontweight="bold")

plt.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, "fig11_model_cv_comparison.png"), dpi=300)
plt.close(fig)
print("Saved: fig11_model_cv_comparison.png")

# ---------------------------------------------------------------------------
# Figure 2: Out-of-Fold ROC and Precision-Recall Curves
# ---------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

for m, cname, col in zip(models, clean_names, colors):
    fpr, tpr, _ = roc_curve(y_true, oof_df[m])
    roc_val = auc(fpr, tpr)
    ax1.plot(fpr, tpr, label=f"{cname} (AUC = {roc_val:.4f})", color=col, linewidth=2)

ax1.plot([0, 1], [0, 1], "k--", alpha=0.6, label="Random Guess (AUC = 0.5000)")
ax1.set_title("Out-of-Fold ROC Curves (Training Data)")
ax1.set_xlabel("False Positive Rate (1 - Specificity)")
ax1.set_ylabel("True Positive Rate (Recall)")
ax1.legend(loc="lower right")

for m, cname, col in zip(models, clean_names, colors):
    prec, rec, _ = precision_recall_curve(y_true, oof_df[m])
    pr_val = average_precision_score(y_true, oof_df[m])
    ax2.plot(rec, prec, label=f"{cname} (AP = {pr_val:.4f})", color=col, linewidth=2)

baseline = y_true.mean()
ax2.axhline(baseline, color="k", linestyle="--", alpha=0.6, label=f"No-Skill Baseline ({baseline:.4f})")
ax2.set_title("Out-of-Fold Precision-Recall Curves (Training Data)")
ax2.set_xlabel("Recall (True Positive Rate)")
ax2.set_ylabel("Precision (Positive Predictive Value)")
ax2.legend(loc="upper right")

plt.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, "fig12_oof_roc_pr_curves.png"), dpi=300)
plt.close(fig)
print("Saved: fig12_oof_roc_pr_curves.png")

# ---------------------------------------------------------------------------
# Figure 3: Optimal Threshold Calibration Curve (Training OOF Only)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(thresh_df["threshold"], thresh_df["f1"], label="F1-Score (Default)", color="#e74c3c", linewidth=2.5)
ax.plot(thresh_df["threshold"], thresh_df["precision"], label="Precision", color="#3498db", linewidth=1.8, linestyle="--")
ax.plot(thresh_df["threshold"], thresh_df["recall"], label="Recall", color="#2ecc71", linewidth=1.8, linestyle="--")

opt_th = meta["optimal_threshold"]
opt_f1 = meta["best_cv_f1_at_optimal_threshold"]
ax.axvline(opt_th, color="purple", linestyle=":", linewidth=2, label=f"Optimal Threshold (τ* = {opt_th:.2f}, F1 = {opt_f1:.4f})")
ax.axvline(0.50, color="gray", linestyle="--", alpha=0.7, label="Default Cutoff (τ = 0.50)")

ax.set_title(f"Threshold Optimization on Out-of-Fold Predictions ({meta['champion_model']})")
ax.set_xlabel("Decision Threshold (Probability Cutoff)")
ax.set_ylabel("Metric Value")
ax.set_xlim(0.15, 0.85)
ax.set_ylim(0.20, 0.90)
ax.legend(loc="center right")

plt.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, "fig13_threshold_calibration_curve.png"), dpi=300)
plt.close(fig)
print("Saved: fig13_threshold_calibration_curve.png")

# ---------------------------------------------------------------------------
# Figure 4: Feature Importance (Permutation Importance on Training Set)
# ---------------------------------------------------------------------------
data_dict = joblib.load(os.path.join(MODELS_DIR, "train_test_data.joblib"))
champion_model = joblib.load(os.path.join(MODELS_DIR, "credit_risk_champion_model.joblib"))

X_train = data_dict["X_train"]
y_train = data_dict["y_train"]

print("Calculating Permutation Feature Importance on Training Set (n_repeats=5)...")
perm_imp = permutation_importance(champion_model, X_train, y_train, n_repeats=5, random_state=42, scoring="average_precision", n_jobs=-1)

imp_df = pd.DataFrame({
    "feature": X_train.columns,
    "importance_mean": perm_imp.importances_mean,
    "importance_std": perm_imp.importances_std
}).sort_values("importance_mean", ascending=False).head(15)

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    data=imp_df,
    x="importance_mean",
    y="feature",
    ax=ax,
    palette="viridis",
    edgecolor="black"
)
ax.set_title("Top 15 Predictive Features (Permutation Importance in PR-AUC — Training Set)")
ax.set_xlabel("Drop in PR-AUC (Average Precision)")
ax.set_ylabel("Feature Name")

plt.tight_layout()
fig.savefig(os.path.join(FIGURES_DIR, "fig14_top15_feature_importance.png"), dpi=300)
plt.close(fig)
print("Saved: fig14_top15_feature_importance.png")
