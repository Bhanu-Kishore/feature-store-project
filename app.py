
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from feast import FeatureStore
import mlflow.sklearn
import pandas as pd

app = FastAPI(
    title="Customer Churn Prediction API",
    description="Feast + MLflow + FastAPI customer churn demonstration",
    version="2.0",
)

store = FeatureStore(repo_path=".")

# New customer churn model logged in MLflow
MODEL_URI = "runs:/d38dea83b0c142a6be4790c017a1923e/model"
model = mlflow.sklearn.load_model(MODEL_URI)

class PredictionRequest(BaseModel):
    customer_id: str

@app.get("/")
def root():
    return {"message": "Customer Churn Prediction API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        # Retrieve customer features from Feast's online store
        feature_response = store.get_online_features(
            features=[
                "customer_features:tenure",
                "customer_features:monthly_charges",
                "customer_features:total_charges",
                "customer_features:senior_citizen",
            ],
            entity_rows=[{"customer_id": request.customer_id}],
        ).to_dict()

        # Check whether the customer exists
        if feature_response["tenure"][0] is None:
            raise HTTPException(
                status_code=404,
                detail="Customer features not found. Check the customer ID and Feast materialization.",
            )

        features = pd.DataFrame({
            "tenure": [feature_response["tenure"][0]],
            "monthly_charges": [feature_response["monthly_charges"][0]],
            "total_charges": [feature_response["total_charges"][0]],
            "senior_citizen": [feature_response["senior_citizen"][0]],
        })

        prediction = int(model.predict(features)[0])

        result = {
            0: "No churn — customer stayed",
            1: "Churn — customer left",
        }

        return {
            "customer_id": request.customer_id,
            "features": features.iloc[0].to_dict(),
            "prediction": prediction,
            "prediction_label": result[prediction],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
