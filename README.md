# 🛒 DeshiKart E-Commerce Lakehouse & BI Analytics Platform

End-to-end Medallion Lakehouse pipeline, automated Lakeflow orchestration, Unity Catalog least-privilege governance, AI/BI Genie validation, and cross-tool Power BI reconciliation built on **Databricks** and **Power BI Desktop**.

---

## 🏗️ Architecture & Medallion Data Flow

```text
Raw E-Commerce CSVs (/Volumes/workspace/ecom_poc/raw_files)
       │
       ▼  [01_bronze_ingestion.py] — Schema-on-read (all STRING) + lineage metadata
┌─────────────────────────────────────────────────────────────┐
│ BRONZE LAYER (workspace.ecom_poc)                           │
│ • Raw orders & payment logs with batch_id & ingestion_ts    │
└─────────────────────────────────────────────────────────────┘
       │
       ▼  [02_silver_reconciliation.py] — Deduplication, casting, payment-order reconciliation
┌─────────────────────────────────────────────────────────────┐
│ SILVER LAYER (workspace.ecom_poc)                           │
│ • Cleansed, typed orders & reconciled payment transactions  │
└─────────────────────────────────────────────────────────────┘
       │
       ▼  [03_gold_marts.sql] — Business-level aggregations & KPI marts
┌─────────────────────────────────────────────────────────────┐
│ GOLD LAYER (workspace.ecom_poc)                             │
│ • gold_daily_sales         • gold_revenue_breakdown         │
│ • gold_payment_success     • gold_top_customers             │
└─────────────────────────────────────────────────────────────┘
       │
       ├──────────────────────────┬───────────────────────────┐
       ▼                          ▼                           ▼
 Databricks AI/BI          Genie Space Agent           Power BI Desktop
 (Executive Dashboard)     (Natural Language SQL)      (Import Mode + DAX)