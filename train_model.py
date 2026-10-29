
import pandas as pd
import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load the prepared churn training dataset
df = pd.read_parquet("data/telco_training_dataset.parquet")

feature_columns = [
    "tenure",
    "monthly_charges",
    "total_charges",
    "senior_citizen",
]

X = df[feature_columns]
y = df["Churn"]

# Split data while preserving the churn class proportions
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

mlflow.set_experiment("Customer_Churn_Feature_Store")

with mlflow.start_run():
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    mlflow.log_param("model_type", "RandomForestClassifier")
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("feature_count", len(feature_columns))
    mlflow.log_metric("accuracy", accuracy)

    mlflow.sklearn.log_model(
        model,
        name="model",
        skops_trusted_types=["sklearn.tree._tree.Tree"],
    )

    print("Customer churn model trained successfully.")
    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows: {len(X_test)}")
    print(f"Accuracy: {accuracy:.4f}")
    print("\nClassification report:")
    print(classification_report(y_test, predictions, zero_division=0))
    print(f"\nMLflow run ID: {mlflow.active_run().info.run_id}")
