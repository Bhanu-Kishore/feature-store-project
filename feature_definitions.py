from feast import Entity, FeatureView, Field, FileSource, ValueType
from feast.types import Int64, Float64, String

# Entity
user = Entity(
    name="user",
    join_keys=["user_id"],
    value_type=ValueType.STRING,
    description="User identifier",
)


# Offline feature source
user_activity_source = FileSource(
    name="user_activity_features",
    path="data/features.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)


# Feature View
user_activity_features = FeatureView(
    name="user_activity_features",
    entities=[user],
    ttl=None,
    schema=[
        Field(
            name="transaction_count_7d",
            dtype=Int64,
            description="Number of transactions in the previous 7 days",
        ),
        Field(
            name="avg_transaction_amount_7d",
            dtype=Float64,
            description="Average transaction amount over the previous 7 days",
        ),
        Field(
            name="total_spend_30d",
            dtype=Float64,
            description="Total spending over the previous 30 days",
        ),
        Field(
            name="avg_session_duration_7d",
            dtype=Float64,
            description="Average session duration over the previous 7 days",
        ),
        Field(
            name="days_since_last_transaction",
            dtype=Float64,
            description="Number of days since the previous transaction",
        ),
    ],
    online=True,
    source=user_activity_source,
)