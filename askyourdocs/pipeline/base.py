import logging

from askyourdocs import Environment, Service
from askyourdocs.pipeline.pipeline import IngestionPipeline, QueryPipeline


class PipelineService(Service):
    """Modelling service."""
    _entity_name = __qualname__  # type: ignore

    def __init__(self, environment: Environment, settings: dict):
        logging.info(f"initializing service: {self._entity_name}")
        super().__init__(environment=environment, settings=settings)

    def apply(self):
        pipeline = self._environment.pipeline
        match pipeline:

            case 'ingest':
                logging.info('start document ingestion pipeline')
                ingestion_pipeline = IngestionPipeline(environment=self._environment, settings=self._settings)

                source = self._environment.source
                commit = self._environment.commit
                ingestion_pipeline.apply(source=source, commit=commit)

            case 'query':
                logging.info('start query pipeline')
                query_pipeline = QueryPipeline(environment=self._environment, settings=self._settings)
                text = self._environment.text
                query_pipeline.apply(text=text)
