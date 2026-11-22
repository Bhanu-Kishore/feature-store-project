
from feast import Entity, FeatureView, Field, FileSource, ValueType
from feast.types import Int64, Float64

# Customer entity
customer = Entity(
    name="customer",
    join_keys=["customer_id"],
    value_type=ValueType.STRING,
    description="Telco customer identifier",
)

# Offline feature source
customer_source = FileSource(
    name="telco_customer_features",
    path="data/telco_features.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)

# Customer feature view
customer_features = FeatureView(
    name="customer_features",
    entities=[customer],
    ttl=None,
    schema=[
        Field(
            name="tenure",
            dtype=Int64,
            description="Number of months the customer has stayed",
        ),
        Field(
            name="monthly_charges",
            dtype=Float64,
            description="Customer's monthly charges",
        ),
        Field(
            name="total_charges",
            dtype=Float64,
            description="Customer's total charges",
        ),
        Field(
            name="senior_citizen",
            dtype=Int64,
            description="Whether the customer is a senior citizen",
        ),
    ],
    online=True,
    source=customer_source,
)
