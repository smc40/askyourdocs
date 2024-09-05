from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, UploadFile, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.websockets import WebSocketState
from starlette.middleware import Middleware
from app.backend.authentication import AuthenticationMiddleware, validate_token
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

class WebSocketSession:
    def __init__(self, websocket: WebSocket, user_id: dict):
        self.websocket = websocket
        self.user_id = user_id
    
    async def receive_json(self):
        return await self.websocket.receive_json()

    async def send_json(self, data):
        await self.websocket.send_json(data)

    async def close(self, code: int = 1000):
        await self.websocket.close(code=code)
        
    async def get_user_model_name(user_id: str):
        solr_url = environment.solr_url + '/solr/ayd_user/select'
        query_params = {
            'q': f"user_id:{user_id}",
            'rows': 1,
            'fl': 'llm_model_name'
        }

        try:
            response = solr_client._get(solr_url, params=query_params)
            # Check if the response contains 'response' and 'docs'
            if response and 'response' in response and 'docs' in response['response']:
                docs = response['response']['docs']
                
                if docs:
                    llm_model_name = docs[0].get('llm_model_name', "gpt-4-32k")
                    print(f"LLM Model Name: {llm_model_name}")
                else:
                    # Return default model name if docs is empty
                    llm_model_name = "gpt-4-32k"
                    print(f"No document found, using default model: {llm_model_name}")
            else:
                # Handle the case where the response doesn't have the expected structure
                llm_model_name = "gpt-4-32k"
                print(f"Unexpected response structure, using default model: {llm_model_name}")       
        except requests.exceptions.RequestException as e:
            # Handle network or HTTP errors
            llm_model_name = "gpt-4-32k"
            logging.error(f"Error querying Solr for user_id {user_id}: {e}, using default model: {llm_model_name}")

        return llm_model_name

@app.websocket("/ws/query")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get('token')
    user_id = websocket.query_params.get('user_id')  # Fetch the user_id from query params
    print(f"User ID from websocket: {user_id}")
    print(f"Token from websocket: {token}")
    
    websocket_session = WebSocketSession(websocket=websocket, user_id=user_id)
    
    if not token or not user_id:
        logging.error("No token or user_id provided")
        await websocket.close(code=1008)
        return

    try:
        # Validate the token and make sure the user_id is valid
        user_info = validate_token(token)
        
        # if user_info['sub'] != user_id:
        #     raise Exception("Token does not match user_id")
        
        logging.info(f"User {user_id} connected with token: {token}")
        
    except Exception as e:
        logging.error(f"Error during token validation: {e}")
        await websocket.close(code=1008)
        return
    
    query_pipeline = QueryPipeline(environment=environment, settings=settings, user_id=websocket_session.user_id)

    await websocket.accept()
    
    try:
        while True:
            message = await websocket.receive_json()
            data = message.get("data")
            logging.info(f"Received data from user {user_id}: {data}")
            context = message.get("context", [])
            combined_text = ""

            for msg in context:
                combined_text += f"{msg['type']}: {msg['text']} "

            combined_text += f"user: {data}"

            if data.strip():
                print(f"user_id before query pipeline applied: {websocket_session.user_id}")
                answer = query_pipeline.apply(text=combined_text, answer_only=False, user_id=websocket_session.user_id)
                await websocket.send_json(answer)
            else:
                await websocket.send_json({"error": "Empty input"})
    except WebSocketDisconnect:
        pass
    finally:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()

@app.get("/api/get_documents", response_model=DataList)
async def get_documents(request: Request):
    user_id = request.state.userinfo["id"]
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
async def upload_file(request: Request, file: UploadFile = File(...)):
    user_id = request.state.userinfo["id"]
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
async def update_user_settings(request: Request):
    user_id = request.state.userinfo["id"]
    user_settings = await request.json()
    collection = settings['solr']['collections']['map']['user_settings']
    doc_id = f"user_{user_id}"
    doc = UserSettingDocument(id=doc_id, user_id=user_id, llm_model_name=user_settings.get('llm_model_name'))
    solr_client.add_document(document=doc, collection=collection, commit=True)

    return {"data": "User settings updated successfully"}

@app.get("/api/default-model", response_model=UserSettings)
async def get_default_model_name(request: Request):
    user_id = request.state.userinfo["id"]
    print(f'User ID from default model: {user_id}')
    solr_url = environment.solr_url + '/solr/ayd_user/select'
    query_params = {
        'q': f"user_id:{user_id}",
        'rows': 1,
        'fl': 'llm_model_name'
    }

    try:
        response = solr_client._get(solr_url, params=query_params)
        # Check if the response contains 'response' and 'docs'
        if response and 'response' in response and 'docs' in response['response']:
            docs = response['response']['docs']
            
            if docs:
                llm_model_name = docs[0].get('llm_model_name', "gpt-4-32k")
                print(f"LLM Model Name: {llm_model_name}")
            else:
                # Return default model name if docs is empty
                llm_model_name = "gpt-4-32k"
                print(f"No document found, using default model: {llm_model_name}")
        else:
            # Handle the case where the response doesn't have the expected structure
            llm_model_name = "gpt-4-32k"
            print(f"Unexpected response structure, using default model: {llm_model_name}")       
    except requests.exceptions.RequestException as e:
        # Handle network or HTTP errors
        llm_model_name = "gpt-4-32k"
        logging.error(f"Error querying Solr for user_id {user_id}: {e}, using default model: {llm_model_name}")

    return {'llm_model_name': llm_model_name}

    
