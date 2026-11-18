import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

# Reproducibility seed
SEED = 42
rng = np.random.default_rng(SEED)
NUM_ROWS = 1_000_000
OUTPUT_DIR = "./deshikart_raw_csvs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Generating DeshiKart Orders (1,000,000 rows)...")

# Base clean data
order_ids = np.array([f"ORD-{i:07d}" for i in range(1, NUM_ROWS + 1)])
customer_ids = np.array([f"CUST-{rng.integers(1, 150_001):06d}" for _ in range(NUM_ROWS)])
base_date = datetime(2026, 1, 1)
order_dates = np.array([(base_date + timedelta(days=int(d))).strftime("%Y-%m-%d") for d in rng.integers(0, 315, NUM_ROWS)])
categories = rng.choice(["Groceries", "Fashion", "Electronics", "Home & Kitchen", "Health & Beauty"], NUM_ROWS, p=[0.40, 0.25, 0.15, 0.12, 0.08])
quantities = rng.integers(1, 10, NUM_ROWS).astype(object)
unit_prices = np.round(rng.uniform(150.0, 12000.0, NUM_ROWS), 2).astype(object)
order_statuses = rng.choice(["DELIVERED", "CANCELLED", "PENDING", "RETURNED"], NUM_ROWS, p=[0.78, 0.12, 0.06, 0.04])
countries = rng.choice(["Bangladesh", "BD", "bangladesh", "  Bangladesh  "], NUM_ROWS, p=[0.85, 0.07, 0.05, 0.03]) # Inconsistent labels/whitespace

# --- INJECT 6 DIRTY-DATA ANOMALIES IN ORDERS ---
# 1. Null/Blank customer_id (~0.5% -> 5,000 rows)
null_cust_idx = rng.choice(NUM_ROWS, 5_000, replace=False)
customer_ids[null_cust_idx] = None

# 2. Text inside numeric fields (~0.3% -> 3,000 rows)
bad_qty_idx = rng.choice(NUM_ROWS, 3_000, replace=False)
quantities[bad_qty_idx] = rng.choice(["two", "N/A", "?", "five"], 3_000)

# 3. Negative or zero unit_price (~0.4% -> 4,000 rows)
neg_price_idx = rng.choice(NUM_ROWS, 4_000, replace=False)
unit_prices[neg_price_idx] = -np.abs(unit_prices[neg_price_idx].astype(float))

# 4. Future or invalid timestamps (~0.3% -> 3,000 rows)
bad_date_idx = rng.choice(NUM_ROWS, 3_000, replace=False)
order_dates[bad_date_idx] = rng.choice(["2027-08-15", "2028-01-01", "invalid-date"], 3_000)

# 5. Invalid order_status (~0.2% -> 2,000 rows)
bad_status_idx = rng.choice(NUM_ROWS, 2_000, replace=False)
order_statuses[bad_status_idx] = rng.choice(["UNKNOWN", "LOST_IN_TRANSIT", ""], 2_000)

# 6. Duplicate business keys (order_id) (~0.5% -> 5,000 rows)
dup_target_idx = rng.choice(range(10_000, NUM_ROWS), 5_000, replace=False)
dup_source_idx = rng.choice(range(0, 10_000), 5_000, replace=True)
order_ids[dup_target_idx] = order_ids[dup_source_idx]

orders_df = pd.DataFrame({
    "order_id": order_ids,
    "customer_id": customer_ids,
    "order_date": order_dates,
    "category": categories,
    "quantity": quantities,
    "unit_price": unit_prices,
    "order_status": order_statuses,
    "country": countries
})

orders_path = os.path.join(OUTPUT_DIR, "orders.csv")
orders_df.to_csv(orders_path, index=False)
print(f"Saved {orders_path}: {len(orders_df):,} rows | {os.path.getsize(orders_path):,} bytes")


print("\nGenerating DeshiKart Transactions (1,000,000 rows)...")

txn_ids = np.array([f"TXN-{i:07d}" for i in range(1, NUM_ROWS + 1)])
# Link transactions to existing order_ids
txn_order_ids = rng.choice(order_ids, NUM_ROWS, replace=True)
payment_methods = rng.choice(["bKash", "Nagad", "Card", "COD", "Rocket"], NUM_ROWS, p=[0.42, 0.25, 0.15, 0.15, 0.03])
amounts = np.round(rng.uniform(150.0, 45000.0, NUM_ROWS), 2).astype(object)
currencies = rng.choice(["BDT", "bdt", " BDT "], NUM_ROWS, p=[0.90, 0.06, 0.04])
txn_statuses = rng.choice(["SUCCESS", "FAILED", "PENDING", "REFUNDED"], NUM_ROWS, p=[0.82, 0.10, 0.05, 0.03])
txn_ts = np.array([(base_date + timedelta(days=int(d), seconds=int(s))).strftime("%Y-%m-%d %H:%M:%S")
                   for d, s in zip(rng.integers(0, 315, NUM_ROWS), rng.integers(0, 86400, NUM_ROWS))])

# --- INJECT 6 DIRTY-DATA ANOMALIES IN TRANSACTIONS ---
# 1. Orphan order_ids not present in orders.csv (~0.6% -> 6,000 rows)
orphan_idx = rng.choice(NUM_ROWS, 6_000, replace=False)
txn_order_ids[orphan_idx] = [f"ORD-99{i:05d}" for i in range(6_000)]

# 2. Text inside amount field (~0.3% -> 3,000 rows)
bad_amt_idx = rng.choice(NUM_ROWS, 3_000, replace=False)
amounts[bad_amt_idx] = rng.choice(["ERROR", "NaN_BDT", "free"], 3_000)

# 3. Negative or zero amounts (~0.4% -> 4,000 rows)
available_amt_idx = np.setdiff1d(np.arange(NUM_ROWS), bad_amt_idx)
neg_amt_idx = rng.choice(available_amt_idx, 4_000, replace=False)
amounts[neg_amt_idx] = -np.abs(amounts[neg_amt_idx].astype(float))

# 4. Unsupported currencies (~0.2% -> 2,000 rows)
bad_curr_idx = rng.choice(NUM_ROWS, 2_000, replace=False)
currencies[bad_curr_idx] = rng.choice(["USD", "INR", "XXX"], 2_000)

# 5. Future timestamps (~0.3% -> 3,000 rows)
future_ts_idx = rng.choice(NUM_ROWS, 3_000, replace=False)
txn_ts[future_ts_idx] = "2027-12-31 23:59:59"

# 6. Duplicate webhook retries (duplicate txn_id) (~0.5% -> 5,000 rows)
dup_txn_target = rng.choice(range(10_000, NUM_ROWS), 5_000, replace=False)
dup_txn_source = rng.choice(range(0, 10_000), 5_000, replace=True)
txn_ids[dup_txn_target] = txn_ids[dup_txn_source]

txns_df = pd.DataFrame({
    "txn_id": txn_ids,
    "order_id": txn_order_ids,
    "payment_method": payment_methods,
    "amount": amounts,
    "currency": currencies,
    "txn_status": txn_statuses,
    "txn_ts": txn_ts
})

txns_path = os.path.join(OUTPUT_DIR, "transactions.csv")
txns_df.to_csv(txns_path, index=False)
print(f"Saved {txns_path}: {len(txns_df):,} rows | {os.path.getsize(txns_path):,} bytes")