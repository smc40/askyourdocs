#!/bin/bash
set -e

./db_migration.sh
uvicorn app.backend.app:app --host 0.0.0.0 --port 8000