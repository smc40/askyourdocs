from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi import File, UploadFile

from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.backend.authentication import get_user_info


import askyourdocs.utils as utl
from askyourdocs.settings import SETTINGS as settings
from askyourdocs.pipeline.pipeline import QueryPipeline, IngestionPipeline, RemovalPipeline, SearchPipeline, FeedbackPipeline

import logging

environment = utl.load_environment()
_INGESTION_PIPELINE = IngestionPipeline(environment=environment, settings=settings)
_QUERY_PIPELINE = QueryPipeline(environment=environment, settings=settings)
_REMOVAL_PIPELINE = RemovalPipeline(environment=environment, settings=settings)
_SEARCH_PIPELINE = SearchPipeline(environment=environment, settings=settings)
_FEEDBACK_PIPELINE = FeedbackPipeline(environment=environment, settings=settings)


app = FastAPI(title="AYD")

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get('authorization')
        userinfo = get_user_info(token)
        request.state.userinfo = userinfo
        response = await call_next(request)
        return response

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get('cors_origins'),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(CustomMiddleware)


solr_client = _SEARCH_PIPELINE.solr_client
for name in utl.get_solr_collection_names():
    solr_client.create_collection(name=name)


class Text(BaseModel):
    data: str


class ListText(BaseModel):
    data: list


class Feedback(BaseModel):
    feedbackType: str
    feedbackText: str
    feedbackTo: str
    email: str

class DataList(BaseModel):
    data: list[dict] = []


@app.get('/', response_model=Text)
def root():
    return {'data': 'Ask your docs api service is ready!!!'}

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

@app.post("/ingest", response_model=ListText)
async def upload_file(file: UploadFile = File(...)):
    if file and file.filename:
        logging.info(f'uploading file  {file.filename}')
        filepath = f"./app/backend/uploads/{file.filename}"
        with open(filepath, "wb") as f:
            f.write(file.file.read())
        doc = _INGESTION_PIPELINE.apply(source=filepath, commit=True)
        logging.info(doc)
        return {"data": doc}
    else:
        return {"data": "No file provided"}


@app.post("/ingest_feedback", response_model=Text)
async def upload_feedback(feedback: Feedback):
    doc = _FEEDBACK_PIPELINE.apply(feedback_type = feedback.feedbackType, feedback_text=feedback.feedbackText, feedback_to=feedback.feedbackTo, email=feedback.email, commit=True)
    return {"data": doc}
