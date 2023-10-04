alias ayd='python -m askyourdocs'

ayd storage migration -c "ayd_docs"
ayd storage migration -c "ayd_texts"
ayd storage migration -c "ayd_vecs"

ayd pipeline ingest --source "docs" --commit