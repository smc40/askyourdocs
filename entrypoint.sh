#!/bin/bash
set -e

python -m askyourdocs storage migration -c "ayd_docs"
python -m askyourdocs storage migration -c "ayd_texts"
python -m askyourdocs storage migration -c "ayd_vecs"
python -m askyourdocs storage migration -c "ayd_feedback"
python -m askyourdocs pipeline ingest --source "docs" --commit

uvicorn app.backend.app:app --host 0.0.0.0 --port 8000