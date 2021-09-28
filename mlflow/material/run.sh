#!/bin/bash

mlflow server --backend-store-uri "file:${MLFLOW_STORE_DIR:-/opt/mlflow}" --host 0.0.0.0 --port 5000
