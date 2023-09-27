from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import askyourdocs.utils as utl
from askyourdocs.settings import SETTINGS as settings
from askyourdocs.pipeline.pipeline import QueryPipeline, IngestionPipeline

environment = utl.load_environment()
_INGESTION_PIPELINE = IngestionPipeline(environment=environment, settings=settings)
_QUERY_PIPELINE = QueryPipeline(environment=environment, settings=settings)

app = FastAPI()
# Add CORS middleware to allow cross-origin requests from given url
app.add_middleware(
    CORSMiddleware,
    allow_origins=[environment.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Text(BaseModel):
    text: str


@app.get('/', response_model=Text)
def root():
    return {'text': 'Ask your docs api service is ready!!!'}


@app.get('/query', response_model=Text)
def query(data: Text):
    answer = _QUERY_PIPELINE.apply(text=data.text)
    return {'text': answer}

