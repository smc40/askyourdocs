# Ask Your Documents
**Goal:** Locally hosted chatbot answering questions to your documents

## Requirements

- 15 GB free space
- At least 4 GB of free memory
- Python 3.10
- docker-compose

## Overview of Pipelines
### Ingestion
At the ingestion stage, one or several documents are stored into the database with the corresponding semantic 
embeddings. The `IngestionPipeline` object defined in `askyourdocs.pipeline.pipeline` enchains the following steps: 

|   | Stage           | Remark                                         | Related Object(s)                                 |        
|---|-----------------|------------------------------------------------|---------------------------------------------------|
| 1 | Extraction      | Extracts the text from the retrieved documents | `askyourdocs.storage.scraping` -> `TikaExtractor` |        
| 2 | Text Entities   | Split text into text chunks                    | `askyourdocs.modelling.llm` -> `TextTokenizer`    |        
| 3 | Text Embeddings | Compute vector embeddings of the text chunks   | `askyourdocs.modelling.llm` -> `TextEmbedder`     |        
| 4 | Storage in Solr | Add documents and embeddings to Solr           | `askyourdocs.storage.client` -> `SolrClient`      |

### Query
At the query stage, a given user input is transformed into a semantic vector, from which semantically related document
parts are retrieved and used for formulating an answer. The `QueryPipeline` object defined in 
`askyourdocs.pipeline.pipeline` enchains the following steps: 

|   | Stage               | Remark                                        | Related Object(s)                             |        
|---|---------------------|-----------------------------------------------|-----------------------------------------------|
| 1 | Text Embeddings     | Compute vector embeddings of query            | `askyourdocs.modelling.llm` -> `TextEmbedder` |       
| 2 | k-nearest-neighbors | Search the semantically closest text entities | `askyourdocs.storage.client` -> `SolrClient`  |        
| 3 | Create context      | Create text context from relevant documents   | -                                             |        
| 4 | Answer              | Use context to form an answer to the query    | `askyourdocs.modelling.llm` -> `Summarizer`   |


## Automatic Setup
For easy-of-use we have added the run_ayd.sh script. You only need to make it executable and run it:

```shell
source .env  #only needed if you want to overwrite the default envs from docker compose
 chmod +x run_ayd.sh
 ./run_ayd.sh

```
The script first creates a solr container and then for hosting the documents it mounts the volume `/opt/solr` into the `bitnami/solr` container. Make sure that the default
user in the bitnami containers (1001) has the appropriate rights by
```shell
sudo chown 1001 /opt/solr #done by the script
```
!!! ATTENTION !!!
You also want to make sure that this folder is empty when you initially start the backend container.
Run the docker containers
```shell
docker compose -p ayd up -d  #done by the script
```
As we are using keycloak as authentication service, we need to create a testuser with the following command:
```shell
docker exec -i ayd-postgres-1 psql -U "${AYD_PSQL_USER:-ayd_dba}" -d $"${AYD_PSQL_DB:-ayd}" -a -f /user_scripts/user_entity_data.sql  #done by the script
```

then checkout `localhost:3000` with "test" as username/password and see the magic happening ;-D.

!!! ATTENTION !!!
- If you plan to use askyourdocuments on real data, remove the testuser from your keycloak admin console.
- Running the docker compose will create the app for you (be patient, the backend need to download the models first so 
it might take up to 10 minutes to be ready, check `docker logs ayd-backend-1 -f` to see the following message:
`INFO:     Application startup complete.`)

## Manual Setup
Start by setting up the three services `Apache/Tika`, `Solr`, and `ZooKeeper` (you might want to get inspired by
the `docker-compose.yml` file).
```shell
docker run -d --name tika -p 9998:9998 apache/tika:latest
docker run -d --name zoo1 -p 2181:2181 -e ZOO_MY_ID=1 -e ZOO_SERVERS=server.1=zoo1:2888:3888;2181 -e ZOO_4LW_COMMANDS_WHITELIST=mntr,conf,ruok zookeeper
docker run -d --name solr -p 8983:8983 -v /opt/solr:/bitnami -e ZK_HOST=zoo1:2181 -e SOLR_JAVA_MEM="-Xms1g -Xmx1g"
```
Then define the environment variables:
```shell
# Logging
export LOG_LEVEL="INFO"

# TIKA
export TIKA_URL=<changeme>        # For local host use "http://localhost:9998"

# Solr
export SOLR_URL=<changeme>        # For local host use "http://localhost:8983"  
export ZK_URLS=<changeme>         # For local host use "localhost:2181"

# Frontend
export FRONTEND_URL=<changeme>    # For local host use "http://localhost:3000"

# Postgres
export AYD_PSQL_USER=<changeme> 
export AYD_PSQL_PASSWORD=<changeme> 
export AYD_PSQL_DB=<changeme> 

# Keycloak
export KEYCLOAK_URL=<changeme>     # For local deployment via uvicorn use http://localhost:8080/
export BACKEND_KEYCLOAK_SECRET=<changeme>  #For initial value use bQwuuesYTIfcJmOxI4t4fltV48OQsAQq. If changed, make sure to adjust in app/keycloak/realm-export.json as well.
```

With a `venv` as and an alias `ayd` defined as
```shell
python -m venv venv
source venv/bin/activate
pip install -r req_freeze.txt
alias ayd='python -m askyourdocs'
```
and the necessary Solr collections `ayd_docs`, `ayd_texts`, and `ayd_vecs` setup through
```shell
ayd storage creation -c "ayd_docs"
ayd storage creation -c "ayd_texts"
ayd storage creation -c "ayd_vecs"
```
you can start to play with ask-your-documents through the CLI.

### Add Sample Documents
```shell
ayd pipeline ingest --source "docs" --commit
```

### Extract Text
```shell
ayd storage extract --filename <filename> 
# ayd storage extraction --filename "https://www.accessdata.fda.gov/drugsatfda_docs/label/2011/020895s036lbl.pdf"
```
`<filename>` is either the local path or the url of a file.

### Searching a Collection
```shell
ayd storage search -c <collection> -q <query>
# ayd storage search -c "ayd_docs" -q "annual report"
# ayd storage search -c "ayd_feedback" -q "*:*"
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

### Ask Question
```shell
ayd pipeline query --text <your-text>
# ayd pipeline query --text "How to avoid covid" 
```

You can also choose to run the FastAPI backend and/or the React frontend locally.

### Run Fastapi Backend locally
From the base directory run
```shell
uvicorn app.backend.app:app --host 0.0.0.0 --port 8686 --reload
```


### Run React Frontend Locally

```sh
cd app/frontend # move to the frontend directory
npm install # install the dependencies
```
```sh
npm run start # start the app
```

## Tests (WIP)
Run type checking
```shell
mypy --ignore-missing-imports askyourdocs
```
and unit-tests
```shell
pytest -s --cov=askyourdocs tests
```


## One More Thing
Enter `magic schnauz` in the user input field of the frontend :-D
