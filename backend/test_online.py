from feast import FeatureStore

store = FeatureStore(repo_path=".")

features = store.get_online_features(
    features=[
        "user_activity_features:transaction_count_7d",
        "user_activity_features:avg_transaction_amount_7d",
        "user_activity_features:total_spend_30d",
        "user_activity_features:avg_session_duration_7d",
        "user_activity_features:days_since_last_transaction",
    ],
    entity_rows=[
        {"user_id": "user_001"},
        {"user_id": "user_002"},
        {"user_id": "user_003"},
    ],
).to_dict()

print("\nOnline Feature Retrieval Result:\n")

for key, values in features.items():
    print(f"{key}: {values}")