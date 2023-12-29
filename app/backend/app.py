from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi import File, UploadFile

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.websockets import WebSocketState
from app.backend.authentication import AuthenticationMiddleware

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


import askyourdocs.utils as utl
from askyourdocs.settings import SETTINGS as settings
from askyourdocs.pipeline.pipeline import QueryPipeline, IngestionPipeline, RemovalPipeline, SearchPipeline, FeedbackPipeline

import logging
import os

environment = utl.load_environment()
_INGESTION_PIPELINE = IngestionPipeline(environment=environment, settings=settings)
_QUERY_PIPELINE = QueryPipeline(environment=environment, settings=settings)
_REMOVAL_PIPELINE = RemovalPipeline(environment=environment, settings=settings)
_SEARCH_PIPELINE = SearchPipeline(environment=environment, settings=settings)
_FEEDBACK_PIPELINE = FeedbackPipeline(environment=environment, settings=settings)

def middleware():
    return [
        Middleware(
            CORSMiddleware,
            allow_origins=settings.get('cors_origins', ['http://localhost:8000','http://localhost:3000']),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        ),
        Middleware(AuthenticationMiddleware)
    ]

app = FastAPI(title="AYD", middleware=middleware())
app.add_middleware(GZipMiddleware, minimum_size=500)

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

app.mount("/app", StaticFiles(directory="/app/static"), name="static")
app.mount("/public", StaticFiles(directory="/app/public"), name="public")

pdfs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
app.mount("/uploads", StaticFiles(directory=pdfs_dir), name="uploads")

@app.get("/")
async def read_root():
    landing_page_path = "/app/index.html"
    try:
        return FileResponse(landing_page_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/query")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            answer = _QUERY_PIPELINE.apply(text=data, answer_only=False)
            await websocket.send_json(answer)
    except WebSocketDisconnect:
        pass
    finally:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()


@app.get("/api/get_documents", response_model=DataList)
async def get_documents():
    query = f'*'
    collection = settings['solr']['collections']['map']['docs']
    params={'fl':'name,id'}
    response = _SEARCH_PIPELINE.apply(query=query, collection=collection, params = params)

    return {
        "data":response
    }

@app.get("/api/get_documents_by_id", response_model=DataList)
async def get_documents(id: str):
    query = f'id:{id}'
    collection = settings['solr']['collections']['map']['docs']
    params={'fl':'name,id,source'}
    response = _SEARCH_PIPELINE.apply(query=query, collection=collection, params = params)
    return {
        "data":response
    }

@app.delete("/api/delete_document", response_model=Text)
async def delete_document(id: str):
    logging.info(f"deleting doc {id} in SOLR")
    _REMOVAL_PIPELINE.apply(id_=id, commit=True)
    return {
        "data": "successfully deleted."
    }

@app.post("/api/ingest", response_model=ListText)
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


@app.post("/api/ingest_feedback", response_model=Text)
async def upload_feedback(feedback: Feedback):
    doc = _FEEDBACK_PIPELINE.apply(feedback_type = feedback.feedbackType, feedback_text=feedback.feedbackText, feedback_to=feedback.feedbackTo, email=feedback.email, commit=True)
    return {"data": doc}
