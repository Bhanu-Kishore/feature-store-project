#!/usr/bin/env bash
# Provision the Azure resources, build/push both images, deploy the frontend,
# and write the values needed to configure GitHub Actions.
#
# This script creates billable Azure resources. Set CONFIRM_DEPLOY=yes only
# after reviewing the cost estimate printed below and approving the spend.
set -euo pipefail

# Git Bash rewrites arguments that start with "/" into Windows paths, which
# corrupts Azure resource IDs. Disable that conversion for every az call.
export MSYS_NO_PATHCONV=1

cd "$(dirname "$0")/.."

RG="${RESOURCE_GROUP:-rg-churn-feature-store}"
LOCATION="${AZURE_LOCATION:-centralindia}"
PREFIX="${PREFIX:-churn}"
MIN_REPLICAS="${MIN_REPLICAS:-0}"
MAX_REPLICAS="${MAX_REPLICAS:-1}"
TAG="$(date -u +%Y%m%d%H%M%S)"

cat <<'EOF'
==============================================================================
Azure resources to be created (approval required before continuing)
==============================================================================
- Resource group (centralindia, the region allowed by the student policy)
- Azure Container Registry, Basic tier ............ fixed ~ $5.00 / month
- Azure Container Apps environment
- Backend Container App (0.5 vCPU / 1 GiB, min replicas 0)
- Frontend Container App (0.25 vCPU / 0.5 GiB, min replicas 0, Nginx)
  Static Web Apps is unavailable in the policy-allowed regions, so the
  frontend runs as a container app in the same environment.
- Log Analytics workspace (30-day retention) ...... ~ $0-1 / month at demo volume
- Storage account: 1 GiB Azure Files share + blob
  container for datasets/model .................... ~ $0.10-0.30 / month
------------------------------------------------------------------------------
Estimated total: roughly $5-7 / month while idle, consumed from the Azure for
Students credit. Container Apps scale to zero; ACR Basic is the main fixed
charge. Set MIN_REPLICAS=1 to keep both apps warm (usage above the free grant).
==============================================================================
EOF

if ! az account show >/dev/null 2>&1; then
    echo "ERROR: Azure CLI is not authenticated. Run: az login" >&2
    exit 1
fi

if [ "${CONFIRM_DEPLOY:-}" != "yes" ]; then
    echo "Deployment not confirmed. Re-run with CONFIRM_DEPLOY=yes to proceed."
    exit 2
fi

SUB_ID="$(az account show --query id -o tsv)"
echo "Subscription: ${SUB_ID}"
echo "Resource group: ${RG} (${LOCATION})"

if az group show --name "$RG" >/dev/null 2>&1; then
    echo "Resource group ${RG} already exists; deploying resources to ${LOCATION}."
else
    az group create --name "$RG" --location "$LOCATION" --output none
fi

echo "Deploying Bicep template..."
az deployment group create \
    --resource-group "$RG" \
    --template-file infra/main.bicep \
    --parameters location="$LOCATION" prefix="$PREFIX" minReplicas="$MIN_REPLICAS" maxReplicas="$MAX_REPLICAS" \
    --output none

output() {
    az deployment group show \
        --resource-group "$RG" \
        --name main \
        --query "properties.outputs.$1.value" \
        --output tsv
}

ACR_NAME="$(output acrName)"
ACR_LOGIN_SERVER="$(output acrLoginServer)"
CONTAINER_APP="$(output containerAppName)"
FRONTEND_APP="$(output frontendAppName)"
STORAGE_ACCOUNT="$(output storageAccountName)"
BACKEND_URL="$(output backendUrl)"
FRONTEND_URL="$(output frontendUrl)"

echo "ACR: ${ACR_LOGIN_SERVER}"
echo "Backend: ${BACKEND_URL}"
echo "Frontend: ${FRONTEND_URL}"

echo "Logging in to ACR..."
if ! az acr login --name "$ACR_NAME" >/dev/null; then
    ACR_USER="$(az acr credential show --name "$ACR_NAME" --query username -o tsv)"
    ACR_PASS="$(az acr credential show --name "$ACR_NAME" --query 'passwords[0].value' -o tsv)"
    printf '%s' "$ACR_PASS" | docker login "$ACR_LOGIN_SERVER" --username "$ACR_USER" --password-stdin
fi

BACKEND_IMAGE="${ACR_LOGIN_SERVER}/churn-backend:${TAG}"
echo "Building the backend image locally (ACR Tasks may be blocked by subscription policy)..."
docker build \
    -t "$BACKEND_IMAGE" \
    -t "${ACR_LOGIN_SERVER}/churn-backend:latest" \
    ./backend
docker push "$BACKEND_IMAGE"
docker push "${ACR_LOGIN_SERVER}/churn-backend:latest"

update_app() {
    local app_name="$1"
    local image="$2"
    for attempt in 1 2 3 4 5; do
        if az containerapp update \
            --name "$app_name" \
            --resource-group "$RG" \
            --image "$image" \
            --output none; then
            return 0
        fi
        if [ "$attempt" = "5" ]; then
            echo "Updating ${app_name} failed after 5 attempts." >&2
            return 1
        fi
        echo "Retrying in 20s (ACR pull role assignment may still be propagating)..."
        sleep 20
    done
}

echo "Updating the backend Container App with ${BACKEND_IMAGE}..."
update_app "$CONTAINER_APP" "$BACKEND_IMAGE"

echo "Waiting for the backend health endpoint..."
for attempt in $(seq 1 20); do
    if curl -fsS --max-time 20 "${BACKEND_URL}/health" >/dev/null 2>&1; then
        break
    fi
    if [ "$attempt" = "20" ]; then
        echo "WARNING: backend health did not become ready yet; check Container App logs." >&2
    fi
    sleep 15
done

BACKEND_URL_VALUE="$BACKEND_URL"

FRONTEND_IMAGE="${ACR_LOGIN_SERVER}/churn-frontend:${TAG}"
echo "Building the frontend image against ${BACKEND_URL_VALUE}..."
docker build \
    --build-arg "VITE_API_URL=${BACKEND_URL_VALUE}" \
    -t "$FRONTEND_IMAGE" \
    -t "${ACR_LOGIN_SERVER}/churn-frontend:latest" \
    ./frontend
docker push "$FRONTEND_IMAGE"
docker push "${ACR_LOGIN_SERVER}/churn-frontend:latest"

echo "Updating the frontend Container App with ${FRONTEND_IMAGE}..."
update_app "$FRONTEND_APP" "$FRONTEND_IMAGE"

echo "Uploading datasets and model artifacts to Blob Storage..."
STORAGE_KEY="$(az storage account keys list --resource-group "$RG" --account-name "$STORAGE_ACCOUNT" --query '[0].value' -o tsv)"
upload_asset() {
    local source_path="$1"
    local blob_name="$2"
    if [ -f "$source_path" ]; then
        az storage blob upload \
            --account-name "$STORAGE_ACCOUNT" \
            --account-key "$STORAGE_KEY" \
            --container-name assets \
            --file "$source_path" \
            --name "$blob_name" \
            --overwrite \
            --output none
        echo "  uploaded ${blob_name}"
    fi
}
upload_asset "backend/model/model.skops" "model/model.skops"
upload_asset "backend/model/model_info.json" "model/model_info.json"
upload_asset "backend/model/MLmodel" "model/MLmodel"
upload_asset "backend/data/telco_customer_churn.csv" "data/telco_customer_churn.csv"
upload_asset "backend/data/telco_features.parquet" "data/telco_features.parquet"
upload_asset "backend/data/telco_training_dataset.parquet" "data/telco_training_dataset.parquet"

cat > .azure-deployment.env <<EOF
AZURE_SUBSCRIPTION_ID=${SUB_ID}
AZURE_RESOURCE_GROUP=${RG}
AZURE_LOCATION=${LOCATION}
ACR_NAME=${ACR_NAME}
ACR_LOGIN_SERVER=${ACR_LOGIN_SERVER}
AZURE_CONTAINER_APP=${CONTAINER_APP}
AZURE_FRONTEND_APP=${FRONTEND_APP}
AZURE_STORAGE_ACCOUNT=${STORAGE_ACCOUNT}
BACKEND_URL=${BACKEND_URL_VALUE}
FRONTEND_URL=${FRONTEND_URL}
BACKEND_SWAGGER_URL=${BACKEND_URL_VALUE}/docs
EOF

echo "Wrote .azure-deployment.env (git-ignored)."

if [ "${CREATE_SERVICE_PRINCIPAL:-yes}" = "yes" ] && [ ! -s .azure-credentials.json ]; then
    echo "Creating a service principal for GitHub Actions..."
    if az ad sp create-for-rbac \
        --name "gh-${PREFIX}-${TAG}" \
        --role Contributor \
        --scopes "/subscriptions/${SUB_ID}/resourceGroups/${RG}" \
        --sdk-auth > .azure-credentials.json; then
        SP_APP_ID="$(python -c 'import json;print(json.load(open(".azure-credentials.json"))["appId"])')"
        ACR_ID="$(az acr show --name "$ACR_NAME" --resource-group "$RG" --query id -o tsv)"
        az role assignment create \
            --assignee "$SP_APP_ID" \
            --role AcrPush \
            --scope "$ACR_ID" \
            --output none
        echo "Wrote .azure-credentials.json (git-ignored)."
    else
        rm -f .azure-credentials.json
        echo "WARNING: could not create the service principal automatically." >&2
        echo "Ask a subscription admin to create one, or use OIDC federation." >&2
    fi
fi

echo
echo "Deployment complete."
echo "Backend:  ${BACKEND_URL_VALUE}"
echo "Swagger:  ${BACKEND_URL_VALUE}/docs"
echo "Frontend: ${FRONTEND_URL}"
