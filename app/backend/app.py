import sys
sys.path.append('../../')

from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi import File, UploadFile


import askyourdocs.utils as utl
from askyourdocs.settings import SETTINGS as settings
from askyourdocs.pipeline.pipeline import QueryPipeline, IngestionPipeline
from askyourdocs.storage.client import SolrClient
from askyourdocs import Environment


import settings as app_settings
import logging

logging.basicConfig(level=logging.INFO)
environment = utl.load_environment()
solr_client = SolrClient(environment=environment, settings=settings)
_INGESTION_PIPELINE = IngestionPipeline(environment=environment, settings=settings)
_QUERY_PIPELINE = QueryPipeline(environment=environment, settings=settings)

def middleware():
    return [
        Middleware(CORSMiddleware,
                   allow_origins=[str(origin) for origin in app_settings.CORS_ORIGINS],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])
    ]


app = FastAPI(title="AYD", middleware=middleware())

class Count(BaseModel):
    count: int

class ResponseModel(BaseModel):
    data: Count

class Text(BaseModel):
    data: str

class DataList(BaseModel):
    data: list[dict] = []


@app.get('/', response_model=Text)
def root():
    return {'text': 'Ask your docs api service is ready!!!'}

@app.post("/query", response_model=Text)
async def get_answer(question_input: Text):
    answer = _QUERY_PIPELINE.apply(text=question_input.data)
    return {
        "data":answer
    }

@app.get("/get_documents", response_model=DataList)
async def get_documents(user: str = ""):
    data = {'text': user}
    query = f'*'
    collection = settings['solr']['collections']['map']['docs']
    response = solr_client.search(query='*', collection=collection, params={'fl':'name,id'}).get('docs')
    return {
        "data":response
    }

@app.delete("/delete_document", response_model=ResponseModel, status_code=200)
async def delete_document(name: str):
    logging.info(f"TBD --> delete doc {name} in SOLR")
    return {
        "data": {
            "count": 1
        }
    }

@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    if file and file.filename:
        filepath = f"./uploads/{file.filename}"
        with open(filepath, "wb") as f:
            f.write(file.file.read())
        _INGESTION_PIPELINE.apply(filename=filepath, commit=True)
        return {"message": "File uploaded successfully"}
    else:
        return {"message": "No file provided"}

