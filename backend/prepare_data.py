
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

RAW_FILE = DATA_DIR / "telco_customer_churn.csv"
CLEAN_FILE = DATA_DIR / "telco_cleaned.csv"

df = pd.read_csv(RAW_FILE)

# Convert TotalCharges to numeric.
df["TotalCharges"] = pd.to_numeric(
    df["TotalCharges"].astype(str).str.strip(),
    errors="coerce"
)

# Remove rows with missing TotalCharges.
df = df.dropna(subset=["TotalCharges"]).copy()

# Encode the target: Yes = 1, No = 0.
df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})

# Rename the customer identifier for our feature-store project.
df = df.rename(columns={"customerID": "customer_id"})

df.to_csv(CLEAN_FILE, index=False)

print("Dataset preparation completed.")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("\nChurn distribution:")
print(df["Churn"].value_counts().sort_index())
print("\nSaved to:", CLEAN_FILE)
