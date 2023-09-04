import logging

from askyourdocs import Environment, Service
from askyourdocs.storage.management import SolrClient
from askyourdocs.storage.scraping import TikaExtractor


class Storage(Service):
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

            case 'migration':
                logging.info(f'start collection migration')
                collection = self._environment.collection
                self._solr_client.migrate_collection(name=collection)

            case 'search':
                logging.info(f'start collection search')
                collection = self._environment.collection
                query = self._environment.query
                logging.error(f'search not implemented yet')

            case 'extraction':
                logging.info(f'start text extraction')
                filename = self._environment.filename
                self._tika_extractor.apply(filename=filename)

            case 'add':
                logging.info(f'start adding a document')
                filename = self._environment.filename
                collection = self._environment.collection
                document = self._tika_extractor.apply(filename=filename)
                self._solr_client.add_document(document=document, collection=collection, commit=self._commit)
