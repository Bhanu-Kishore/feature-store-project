import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

import mlflow.sklearn
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from feast import FeatureStore
from pydantic import BaseModel, field_validator

BASE_DIR = Path(__file__).resolve().parent
FEAST_REPO_PATH = os.getenv("FEAST_REPO_PATH", str(BASE_DIR))
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "model"))
MLFLOW_MODEL_URI = os.getenv("MLFLOW_MODEL_URI", "").strip()

FEATURE_COLUMNS = [
    "tenure",
    "monthly_charges",
    "total_charges",
    "senior_citizen",
]
RESULT_LABELS = {
    0: "No churn — customer stayed",
    1: "Churn — customer left",
}

logger = logging.getLogger("uvicorn.error")

state: dict = {"store": None, "model": None, "model_error": None}


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "*")
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or ["*"]


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Loading Feast feature store from %s", FEAST_REPO_PATH)
    state["store"] = FeatureStore(repo_path=FEAST_REPO_PATH)

    model_uri = MLFLOW_MODEL_URI or MODEL_PATH
    logger.info("Loading model from %s", model_uri)
    try:
        state["model"] = mlflow.sklearn.load_model(model_uri)
        state["model_error"] = None
    except Exception as exc:  # keep the API up so /health can report the problem
        state["model_error"] = str(exc)
        logger.exception("Model could not be loaded from %s", model_uri)
    yield


app = FastAPI(
    title="Customer Churn Prediction API",
    description=(
        "Telco customer churn inference served by FastAPI, with features "
        "retrieved from the Feast online store and a Random Forest model "
        "tracked in MLflow."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionRequest(BaseModel):
    customer_id: str

    @field_validator("customer_id")
    @classmethod
    def customer_id_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("customer_id must not be empty")
        return value


@app.get("/")
def root():
    return {"message": "Customer Churn Prediction API is running"}


@app.get("/health")
def health():
    if state["model"] is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model not loaded: {state['model_error']}",
        )
    return {"status": "ok", "model": "loaded", "feature_store": "online"}


@app.post("/predict")
def predict(request: PredictionRequest):
    if state["model"] is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")

    try:
        feature_response = state["store"].get_online_features(
            features=[f"customer_features:{column}" for column in FEATURE_COLUMNS],
            entity_rows=[{"customer_id": request.customer_id}],
        ).to_dict()

        values = {column: feature_response[column][0] for column in FEATURE_COLUMNS}
        if any(value is None for value in values.values()):
            raise HTTPException(
                status_code=404,
                detail=(
                    "Customer features not found. Check the customer ID and "
                    "Feast materialization."
                ),
            )

        features = pd.DataFrame([values], columns=FEATURE_COLUMNS)
        prediction = int(state["model"].predict(features)[0])
        churn_probability = float(state["model"].predict_proba(features)[0][1])

        return {
            "customer_id": request.customer_id,
            "features": {column: values[column] for column in FEATURE_COLUMNS},
            "prediction": prediction,
            "prediction_label": RESULT_LABELS[prediction],
            "churn_probability": round(churn_probability, 4),
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Prediction failed for %s", request.customer_id)
        raise HTTPException(status_code=500, detail="Prediction failed.") from exc
