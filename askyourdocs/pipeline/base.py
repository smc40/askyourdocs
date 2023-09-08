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

                filename = self._environment.filename
                commit = self._environment.commit
                ingestion_pipeline.apply(filename=filename, commit=commit)

            case 'query':
                logging.info('start query pipeline')
                logging.error(f'query pipeline is not implemented yet')
                # query_pipeline = QueryPipeline(environment=self._environment, settings=self._settings)
