#!/usr/bin/env bash
# Uploads Azure credentials and deployment targets to GitHub Actions.
# Requires confirmation: this modifies repository settings.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .azure-deployment.env ]; then
    echo "ERROR: .azure-deployment.env not found. Run infra/deploy.sh first." >&2
    exit 1
fi
if [ ! -f .azure-credentials.json ]; then
    echo "ERROR: .azure-credentials.json not found." >&2
    exit 1
fi

# shellcheck disable=SC1091
source .azure-deployment.env

if [ "${CONFIRM_GITHUB_CONFIG:-}" != "yes" ]; then
    echo "This will write secrets and variables to the GitHub repository."
    echo "Re-run with CONFIRM_GITHUB_CONFIG=yes to proceed."
    exit 2
fi

gh secret set AZURE_CREDENTIALS < .azure-credentials.json
gh secret set ACR_NAME --body "$ACR_NAME"
gh secret set ACR_LOGIN_SERVER --body "$ACR_LOGIN_SERVER"
gh secret set AZURE_RESOURCE_GROUP --body "$AZURE_RESOURCE_GROUP"
gh secret set AZURE_CONTAINER_APP --body "$AZURE_CONTAINER_APP"
gh secret set AZURE_FRONTEND_APP --body "$AZURE_FRONTEND_APP"

gh variable set BACKEND_URL --body "$BACKEND_URL"
gh variable set FRONTEND_URL --body "$FRONTEND_URL"
gh variable set AZURE_DEPLOY_ENABLED --body "true"

echo "GitHub Actions secrets and variables configured."
