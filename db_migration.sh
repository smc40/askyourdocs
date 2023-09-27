alias ayd='python -m askyourdocs'

ayd storage migration -c "ayd_docs"
ayd storage migration -c "ayd_texts"
ayd storage migration -c "ayd_vecs"

ayd pipeline ingest --filename "docs/20211203_SwissPAR_Spikevax_single_page_text.pdf" --commit
ayd pipeline ingest --filename "docs/20210430_SwissPAR_Comirnaty.pdf" --commit
ayd pipeline ingest --filename "docs/20211203_SwissPAR-Spikevax.pdf" --commit
ayd pipeline ingest --filename "docs/SwissPAR COVID-19 Vaccine Janssen .pdf" --commit