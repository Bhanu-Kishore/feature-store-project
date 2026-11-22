
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

CLEAN_FILE = DATA_DIR / "telco_cleaned.csv"
OUTPUT_FILE = DATA_DIR / "telco_training_dataset.parquet"

df = pd.read_csv(CLEAN_FILE)

# Keep the target separate from the input features.
training_df = df[
    [
        "customer_id",
        "tenure",
        "MonthlyCharges",
        "TotalCharges",
        "SeniorCitizen",
        "Churn",
    ]
].copy()

training_df = training_df.rename(columns={
    "MonthlyCharges": "monthly_charges",
    "TotalCharges": "total_charges",
    "SeniorCitizen": "senior_citizen",
})

training_df.to_parquet(OUTPUT_FILE, index=False)

print("Training dataset created.")
print("Rows:", len(training_df))
print("\nTarget distribution:")
print(training_df["Churn"].value_counts().sort_index())
print("\nSaved to:", OUTPUT_FILE)
