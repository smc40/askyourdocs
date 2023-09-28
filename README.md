# askyourdocs
**Goal:** Locally hosted chatbot answering questions to your documents

**User Story:** As a *public relations employee* I would like to *ask questions to documents,* so *I can answer to requests faster*

## Links
- Q&A over Docs (LangChain): https://python.langchain.com/en/latest/use_cases/question_answering.html
- PrivateGPT: https://artificialcorner.com/privategpt-a-free-chatgpt-alternative-to-interact-with-your-documents-offline-ea1c98f98062


## Requirements
Use `python 3.10 virtual environment`
```shell
python3.10 -m venv venv
```
install requirements from `req_freeze.txt`
```shell
source venv/bin/activate
pip install -r req_freeze.txt
```
define environment variables
```shell
source .env
```
Note that you should have a `.env` file of the structure
```shell
# Logging
export LOG_LEVEL="INFO"

# TIKA
export TIKA_URL=<changeme>        # For local host use "http://172.17.0.1:9998"

# Solr
export SOLR_URL=<changeme>        # For local host use "http://172.17.0.1:8983"  
export ZK_URLS=<changeme>         # For local host use "172.17.0.1:2181"

# Frontend
export FRONTEND_URL=<changeme>    # For local host use "http://172.17.0.1:3000"
```

## Setup FastAPI backend
Make `ayd` alias
```shell
alias ayd='python -m askyourdocs'
```
run docker containers
```shell
docker compose -p ayd up -d
```
migrate database
```shell
chmod 777 db_migration.sh
./db_migration.sh
```

## Type checking
```shell
mypy --ignore-missing-imports askyourdocs
```

## Tests
```shell
pytest -s --cov=askyourdocs tests
```


## Frontend
Look at [README in app dir](./app/README.md)

## Cli

For the following commands we assume to have an alias
```shell
alias ayd='python -m askyourdocs'
```
and running docker services from `docker-compose.yml`
```shell
docker compose -p ayd up -d  
```

### Extract Text
```shell
ayd storage extract --filename <filename> 
# ayd storage extraction --filename "https://www.accessdata.fda.gov/drugsatfda_docs/label/2011/020895s036lbl.pdf"
```
`<filename>` is either the local path or the url of a file.

### Migrate Collection
(creating a collection or updating configuration)
```shell
ayd storage migration -c <collection>
# ayd storage migration -c "ayd_docs"
# ayd storage migration -c "ayd_texts"
# ayd storage migration -c "ayd_vecs"
```

### Add a Text Document
```shell
ayd storage add -c <collection> --filename <filename>
# ayd storage add -c "ayd_docs" --filename "https://www.accessdata.fda.gov/drugsatfda_docs/label/2011/020895s036lbl.pdf" --commit
# ayd storage add -c "ayd_docs" --filename "data/documents/swissmedic/Swissmedic_Annual_Report_2022_ENG.pdf" --commit
```


### Searching a Collection
```shell
ayd storage search -c <collection> -q <query>
# ayd storage search -c "ayd_docs" -q "annual report"
```

### Compute Embedding of a given Text
```shell
ayd modelling embedding -t <text>
# ayd modelling embedding -t "foo bar is far"
```

### Tokenize Text into text entities
```shell
ayd modelling tokenization -t <text>
# ayd modelling tokenization -t "Foo bar is far. My cat is fat"
```


### Ingest Document
```shell
ayd pipeline ingest --filename <filename>
# ayd pipeline ingest --filename "docs/20211203_SwissPAR_Spikevax_single_page_text.pdf" --commit
# ayd pipeline ingest --filename "docs/20210430_SwissPAR_Comirnaty.pdf" --commit
# ayd pipeline ingest --filename "docs/20211203_SwissPAR-Spikevax.pdf" --commit
# ayd pipeline ingest --filename "docs/SwissPAR COVID-19 Vaccine Janssen .pdf" --commit
```

### Ask Question
```shell
ayd pipeline query --text <your-text>
# ayd pipeline query --text "How to avoid covid" 
```
