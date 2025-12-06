#!/usr/bin/env bash
set -euo pipefail

source .venv/bin/activate

python scripts/deploy_openapi.py demo-api

python ./scripts/deploy_lambda.py status
python ./scripts/deploy_lambda.py echo
python ./scripts/deploy_lambda.py time
python ./scripts/deploy_lambda.py seed-sales-data

deactivate
