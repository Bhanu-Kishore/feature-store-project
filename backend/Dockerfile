FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Rebuild the deterministic Feast snapshot at image build time: clean the CSV,
# create the feature table, apply the registry and materialize the online store.
RUN python prepare_data.py \
    && python build_features.py \
    && python prepare_training_data.py \
    && python scripts/build_feature_store.py \
    && mkdir -p /app/seed \
    && cp data/telco_features.parquet data/registry.db data/online_store.db /app/seed/

RUN chmod +x scripts/entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/health || exit 1

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
