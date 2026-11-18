GRANT USE CATALOG ON CATALOG workspace TO `account users`;
GRANT USE SCHEMA ON SCHEMA workspace.ecom_poc TO `account users`;
GRANT SELECT ON TABLE workspace.ecom_poc.gold_daily_sales TO `account users`;
GRANT SELECT ON TABLE workspace.ecom_poc.gold_revenue_breakdown TO `account users`;
GRANT SELECT ON TABLE workspace.ecom_poc.gold_payment_success TO `account users`;
GRANT SELECT ON TABLE workspace.ecom_poc.gold_top_customers TO `account users`;