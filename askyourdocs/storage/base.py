import logging
import json

from askyourdocs import Environment, Service
from askyourdocs.storage.client import SolrClient
from askyourdocs.storage.scraping import TikaExtractor


class StorageService(Service):
    """Storage service."""
    _entity_name = __qualname__  # type: ignore

    def __init__(self, environment: Environment, settings: dict):
        logging.info(f"initializing service: {self._entity_name}")
        super().__init__(environment=environment, settings=settings)

        # Solr service
        self._solr_client = SolrClient(environment=environment, settings=settings)
        self._commit = environment.commit

        # Tika service
        self._tika_extractor = TikaExtractor(environment=environment, settings=settings)

    def apply(self):
        storage = self._environment.storage
        match storage:

            case 'creation':
                logging.info(f'start collection creation')
                collection = self._environment.collection
                self._solr_client.create_collection(name=collection)

            case 'extraction':
                logging.info(f'start text extraction')
                filename = self._environment.filename
                self._tika_extractor.apply(filename=filename)

            case 'search':
                collection = self._environment.collection or ""
                query = self._environment.query or ""
                res = self._solr_client.search(collection=collection, query=query)
                logging.info(json.dumps(res, indent=4))
