import pandas as pd
import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# Load Feast-generated training dataset
df = pd.read_parquet("data/training_dataset.parquet")

# Features provided by Feast
feature_columns = [
    "transaction_count_7d",
    "avg_transaction_amount_7d",
    "total_spend_30d",
    "avg_session_duration_7d",
    "days_since_last_transaction",
]

X = df[feature_columns]
y = df["target_label"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.4,
    random_state=42
)

# MLflow experiment
mlflow.set_experiment("Feature_Store_Demo")

with mlflow.start_run():

    # Model
    model = RandomForestClassifier(
        n_estimators=50,
        random_state=42
    )

    model.fit(X_train, y_train)

    # Prediction
    predictions = model.predict(X_test)

    # Metric
    accuracy = accuracy_score(y_test, predictions)

    # Log parameters
    mlflow.log_param("model_type", "RandomForestClassifier")
    mlflow.log_param("n_estimators", 50)

    # Log metric
    mlflow.log_metric("accuracy", accuracy)

    # Log model
    mlflow.sklearn.log_model(
        model,
        name="model",
        skops_trusted_types=["sklearn.tree._tree.Tree"]
    )

    print(f"Model trained successfully.")
    print(f"Accuracy: {accuracy:.4f}")