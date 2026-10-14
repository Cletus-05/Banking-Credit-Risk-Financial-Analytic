# Power BI Dashboard Quickstart Guide

## Project: Banking Credit Risk & Financial Analytics
**Directory**: `banking-credit-risk/powerbi/`

---

## 3-Minute Quick Build in Power BI Desktop

1. **Open Power BI Desktop**.
2. **Import Data**:
   - Go to **Home** -> **Get Data** -> **Text/CSV**.
   - Load `data/processed/powerbi_credit_risk_dataset.csv`, `powerbi_ml_metrics_summary.csv`, and `powerbi_threshold_tradeoffs.csv`.
3. **Add DAX Measures**:
   - Create a blank table named `_Measures` and copy DAX definitions from [`measures.dax`](measures.dax).
4. **Create 4 Pages**:
   - Follow the detailed layout and visual specifications in [`../docs/power_bi_dashboard.md`](../docs/power_bi_dashboard.md).
