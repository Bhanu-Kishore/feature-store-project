import pandas as pd
from feast import FeatureStore

# Create Feast store
store = FeatureStore(repo_path=".")

# Training observations
entity_df = pd.read_csv(
    "data/observations.csv",
    parse_dates=["event_timestamp"]
)

entity_df["event_timestamp"] = pd.to_datetime(
    entity_df["event_timestamp"],
    utc=True
)

# Retrieve historical features
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "user_activity_features:transaction_count_7d",
        "user_activity_features:avg_transaction_amount_7d",
        "user_activity_features:total_spend_30d",
        "user_activity_features:avg_session_duration_7d",
        "user_activity_features:days_since_last_transaction",
    ],
).to_df()
training_df.to_parquet(
    "data/training_dataset.parquet",
    index=False
)

print("Training dataset saved successfully.")
print("\nHistorical Feature Retrieval Result:\n")
print(training_df.to_string(index=False))