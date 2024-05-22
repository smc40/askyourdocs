from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, File, UploadFile, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.websockets import WebSocketState
from starlette.middleware import Middleware
from app.backend.authentication import AuthenticationMiddleware, validate_token
from app.backend.context_manager import get_current_user_id, user_id
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
import os

from askyourdocs.settings import SETTINGS as settings
from askyourdocs.pipeline.pipeline import QueryPipeline, IngestionPipeline, RemovalPipeline, SearchPipeline, FeedbackPipeline
import askyourdocs.utils as utl
from askyourdocs import UserSettingDocument, TextEntity

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
            allow_origins=settings.get('cors_origins', ['http://localhost:8000', 'http://localhost:3000', 'http://app:8000', 'http://app:3000', 'http://app.ayd-sandbox.4punkt0.ch']),
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
    
class UserSettings(BaseModel):
    llm_model_name: str

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

def get_user_id() -> str:
    return get_current_user_id()

@app.websocket("/ws/query")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get('token')
    if not token:
        await websocket.close(code=1008)
        return

    try:
        user_info = validate_token(token)
        user_id.set(user_info['id'])  # Set the user ID in context_manager
    except Exception as e:
        logging.error("Error during token validation: ", e)
        await websocket.close(code=1008)
        return

    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_json()
            data = message.get("data")
            context = message.get("context", [])
            combined_text = ""

            for msg in context:
                combined_text += f"{msg['type']}: {msg['text']} "

            combined_text += f"user: {data}"

            if data.strip():
                answer = _QUERY_PIPELINE.apply(text=combined_text, answer_only=False, user_id=user_id.get())
                await websocket.send_json(answer)
            else:
                await websocket.send_json({"error": "Empty input"})
    except WebSocketDisconnect:
        pass
    finally:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()

@app.get("/api/get_documents", response_model=DataList)
async def get_documents(user_id: str = Depends(get_user_id)):
    query = f'user_id:{user_id}'
    collection = settings['solr']['collections']['map']['docs']
    params = {'fl': 'name,id'}
    response = _SEARCH_PIPELINE.apply(query=query, collection=collection, params=params)
    return {
        "data": response
    }

@app.get("/api/get_documents_by_id", response_model=DataList)
async def get_documents(id: str):
    query = f'id:{id}'
    collection = settings['solr']['collections']['map']['docs']
    params = {'fl': 'name,id,source'}
    response = _SEARCH_PIPELINE.apply(query=query, collection=collection, params=params)
    return {
        "data": response
    }

@app.delete("/api/delete_document", response_model=Text)
async def delete_document(id: str):
    logging.info(f"deleting doc {id} in SOLR")
    _REMOVAL_PIPELINE.apply(id_=id, commit=True)
    return {
        "data": "successfully deleted."
    }

@app.post("/api/ingest", response_model=ListText)
async def upload_file(file: UploadFile = File(...), user_id: str = Depends(get_user_id)):
    if file and file.filename:
        logging.info(f'uploading file  {file.filename}')
        filepath = f"./app/backend/uploads/{file.filename}"
        with open(filepath, "wb") as f:
            f.write(file.file.read())
        doc = _INGESTION_PIPELINE.apply(source=filepath, commit=True, user_id=user_id)
        logging.info(doc)
        return {"data": doc}
    else:
        return {"data": "No file provided"}

@app.post("/api/ingest_feedback", response_model=Text)
async def upload_feedback(feedback: Feedback):
    doc = _FEEDBACK_PIPELINE.apply(feedback_type=feedback.feedbackType, feedback_text=feedback.feedbackText, feedback_to=feedback.feedbackTo, email=feedback.email, commit=True)
    return {"data": doc}

@app.post("/api/update_user_settings", response_model=Text)
async def update_user_settings(request: Request, user_id: str = Depends(get_user_id)):
    user_settings = await request.json()
    collection = settings['solr']['collections']['map']['user_settings']
    doc_id = f"user_{user_id}"
    doc = UserSettingDocument(id=doc_id, entry_id=doc_id, user_id=user_id, llm_model_name=user_settings.get('llm_model_name'))
    solr_client.add_document(document=doc, collection=collection, commit=True)

    return {"data": "User settings updated successfully"} 

@app.get("/api/solr/default-model", response_model=UserSettings)
async def get_default_model_name():
    solr_url = settings['solr']['url'] + '/your_collection/select'
    query_params = {
        'q': '*:*',
        'rows': 1,
        'fl': 'llm_model_name'
    }

    try:
        response = solr_client.get(solr_url, params=query_params)
        results = response.json()

        if results['response']['numFound'] > 0:
            llm_model_name = results['response']['docs'][0].get('llm_model_name')
            if llm_model_name:
                return {"llm_model_name": llm_model_name}
        return {"llm_model_name": "gpt-4-32k"}  # Default value if no model name found
    except Exception as e:
        logging.error(f"Error querying Solr: {e}")
        raise HTTPException(status_code=500, detail="Error querying Solr")