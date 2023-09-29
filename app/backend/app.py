import sys
sys.path.append('../../')

from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi import File, UploadFile


import askyourdocs.utils as utl
from askyourdocs.settings import SETTINGS as settings
from askyourdocs.pipeline.pipeline import QueryPipeline, IngestionPipeline, RemovalPipeline, SearchPipeline
from askyourdocs import Environment


import settings as app_settings
import logging

#logging.basicConfig(level=logging.INFO)

environment = utl.load_environment()
_INGESTION_PIPELINE = IngestionPipeline(environment=environment, settings=settings)
_QUERY_PIPELINE = QueryPipeline(environment=environment, settings=settings)
_REMOVAL_PIPELINE = RemovalPipeline(environment=environment, settings=settings)
_SEARCH_PIPELINE = SearchPipeline(environment=environment, settings=settings)

def middleware():
    return [
        Middleware(CORSMiddleware,
                   allow_origins=[str(origin) for origin in app_settings.CORS_ORIGINS],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])
    ]


app = FastAPI(title="AYD", middleware=middleware())

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
async def get_documents():
    query = f'*'
    collection = settings['solr']['collections']['map']['docs']
    params={'fl':'name,id'}
    response = _SEARCH_PIPELINE.apply(query=query, collection=collection, params = params)

    return {
        "data":response
    }

@app.delete("/delete_document", response_model=Text)
async def delete_document(id: str):
    logging.info(f"deleting doc {id} in SOLR")
    _REMOVAL_PIPELINE.apply(id_=id, commit=True)
    return {
        "data": "successfully deleted."
    }

@app.post("/upload_file", response_model=Text)
async def upload_file(file: UploadFile = File(...)):
    if file and file.filename:
        logging.info(f'uploading file  {file.filename}')
        filepath = f"./uploads/{file.filename}"
        with open(filepath, "wb") as f:
            f.write(file.file.read())
        doc = _INGESTION_PIPELINE.apply(filename=filepath, commit=True)
        return {"data": doc}
    else:
        return {"data": "No file provided"}

