
import pandas as pd
from pathlib import Path
from feast import FeatureStore

DATA_DIR = Path(__file__).parent / "data"

store = FeatureStore(repo_path=".")

# Load customer observations and their actual churn labels.
customers = pd.read_csv(DATA_DIR / "telco_cleaned.csv")

# Each customer has one snapshot observation.
entity_df = pd.DataFrame({
    "customer_id": customers["customer_id"],
    "event_timestamp": pd.to_datetime(
        "2026-01-01 00:00:00", utc=True
    ),
    "Churn": customers["Churn"].astype("int64"),
})

# Retrieve customer features from Feast's offline source.
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "customer_features:tenure",
        "customer_features:monthly_charges",
        "customer_features:total_charges",
        "customer_features:senior_citizen",
    ],
).to_df()

# Save the retrieved features and labels for model training.
output_file = DATA_DIR / "telco_training_dataset.parquet"
training_df.to_parquet(output_file, index=False)

print("Feast historical retrieval completed.")
print("Rows:", len(training_df))
print("\nColumns:")
print(training_df.columns.tolist())
print("\nSample records:")
print(training_df.head().to_string(index=False))
print("\nChurn distribution:")
print(training_df["Churn"].value_counts().sort_index())
print("\nSaved to:", output_file)
