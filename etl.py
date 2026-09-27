import pandas as pd
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent / "data"
RAW_FILE = DATA_DIR / "raw_data.csv"
FEATURE_FILE = DATA_DIR / "features.parquet"


# Load raw data
df = pd.read_csv(RAW_FILE)

# Convert timestamp
df["event_timestamp"] = pd.to_datetime(df["event_timestamp"], utc=True)

# Sort data for time-based calculations
df = df.sort_values(["user_id", "event_timestamp"])


def create_features(group):
    group = group.copy()
    group = group.set_index("event_timestamp")

    # Previous 7-day transaction count
    group["transaction_count_7d"] = (
        group["transaction_amount"]
        .rolling("7D", closed="left")
        .count()
        .fillna(0)
        .astype(int)
    )

    # Previous 7-day average transaction amount
    group["avg_transaction_amount_7d"] = (
        group["transaction_amount"]
        .rolling("7D", closed="left")
        .mean()
        .fillna(0)
    )

    # Previous 30-day total spending
    group["total_spend_30d"] = (
        group["transaction_amount"]
        .rolling("30D", closed="left")
        .sum()
        .fillna(0)
    )

    # Previous 7-day average session duration
    group["avg_session_duration_7d"] = (
        group["session_duration"]
        .rolling("7D", closed="left")
        .mean()
        .fillna(0)
    )

    # Time since previous transaction
    group["days_since_last_transaction"] = (
        group.index.to_series()
        .diff()
        .dt.total_seconds()
        .div(86400)
        .fillna(0)
    )

    return group.reset_index()


# Generate features for each user
features = (
    df.groupby("user_id", group_keys=False)
    .apply(create_features)
    .reset_index(drop=True)
)

# Add creation timestamp
features["created_timestamp"] = features["event_timestamp"]

# Keep only the columns needed by Feast
features = features[
    [
        "user_id",
        "event_timestamp",
        "created_timestamp",
        "transaction_count_7d",
        "avg_transaction_amount_7d",
        "total_spend_30d",
        "avg_session_duration_7d",
        "days_since_last_transaction",
    ]
]

# Save offline feature table
features.to_parquet(FEATURE_FILE, index=False)

print("Feature engineering completed.")
print(f"Offline feature table saved to: {FEATURE_FILE}")
print(f"Number of rows: {len(features)}")
print("\nFeature table:")
print(features.to_string(index=False))