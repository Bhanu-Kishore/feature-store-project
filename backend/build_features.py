
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

INPUT_FILE = DATA_DIR / "telco_cleaned.csv"
OUTPUT_FILE = DATA_DIR / "telco_features.parquet"

df = pd.read_csv(INPUT_FILE)

# Convert customer attributes into Feast feature columns.
features = pd.DataFrame({
    "customer_id": df["customer_id"],
    "event_timestamp": pd.Timestamp("2026-01-01", tz="UTC"),
    "created_timestamp": pd.Timestamp("2026-01-01", tz="UTC"),
    "tenure": df["tenure"].astype("int64"),
    "monthly_charges": df["MonthlyCharges"].astype("float64"),
    "total_charges": df["TotalCharges"].astype("float64"),
    "senior_citizen": df["SeniorCitizen"].astype("int64"),
})

# Keep the prediction target separate from the Feast features.
features.to_parquet(OUTPUT_FILE, index=False)

print("Feast feature table created.")
print("Rows:", len(features))
print("\nColumns:")
print(features.dtypes)
print("\nSample:")
print(features.head().to_string(index=False))
print("\nSaved to:", OUTPUT_FILE)
