from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from feast import FeatureStore
import mlflow.sklearn
import pandas as pd


app = FastAPI(
    title="Feature Store Prediction API",
    description="FastAPI + Feast + MLflow demonstration",
    version="1.0"
)


# Feast
store = FeatureStore(repo_path=".")


# MLflow model
MODEL_URI = "runs:/4c4ec1b4ee6f4063ba8af192f11ed803/model"
model = mlflow.sklearn.load_model(MODEL_URI)


# Request schema
class PredictionRequest(BaseModel):
    user_id: str


@app.get("/")
def root():
    return {
        "message": "Feature Store Prediction API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/predict")
def predict(request: PredictionRequest):

    try:
        # Retrieve features from Feast Online Store
        feature_response = store.get_online_features(
            features=[
                "user_activity_features:transaction_count_7d",
                "user_activity_features:avg_transaction_amount_7d",
                "user_activity_features:total_spend_30d",
                "user_activity_features:avg_session_duration_7d",
                "user_activity_features:days_since_last_transaction",
            ],
            entity_rows=[
                {"user_id": request.user_id}
            ],
        ).to_dict()

        # Check whether user exists
        if feature_response["user_id"][0] is None:
            raise HTTPException(
                status_code=404,
                detail="User features not found"
            )

        # Convert Feast response to DataFrame
        features = pd.DataFrame({
            "transaction_count_7d": [
                feature_response["transaction_count_7d"][0]
            ],
            "avg_transaction_amount_7d": [
                feature_response["avg_transaction_amount_7d"][0]
            ],
            "total_spend_30d": [
                feature_response["total_spend_30d"][0]
            ],
            "avg_session_duration_7d": [
                feature_response["avg_session_duration_7d"][0]
            ],
            "days_since_last_transaction": [
                feature_response["days_since_last_transaction"][0]
            ],
        })

        # Model prediction
        prediction = model.predict(features)[0]

        return {
            "user_id": request.user_id,
            "features": features.iloc[0].to_dict(),
            "prediction": int(prediction)
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )