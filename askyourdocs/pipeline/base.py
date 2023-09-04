import logging

from askyourdocs import Service, Environment, EmbeddingEntity, Document
from askyourdocs.storage.scraping import TikaExtractor
from askyourdocs.storage.management import SolrClient
from askyourdocs.modelling.llm import TextEmbedding, TextTokenizer


class Pipeline(Service):
    """Pipeline service."""
    _entity_name = __qualname__  # type: ignore

    def __init__(self, environment: Environment, settings: dict):
        logging.info(f"initializing service: {self._entity_name}")
        super().__init__(environment=environment, settings=settings)

        # Solr service
        self._solr_client = SolrClient(environment=environment, settings=settings)
        self._commit = environment.commit

        # Tika service
        self._tika_extractor = TikaExtractor(environment=environment, settings=settings)

        # Text embedding service
        model_name = settings['modeling']['model_name']
        self._model = TextEmbedding(environment=environment, settings=settings, model_name=model_name)

        # Text tokenizer service
        package = settings['modeling']['tokenizer_package']
        self._tokenizer = TextTokenizer(environment=environment, settings=settings, package=package)

    def _pipeline_from_text(self, text: str):
        text_entities = self._tokenizer.apply(text=text)
        logging.info(f'tokenized into {len(text_entities)} text entities')

        logging.info(f'compute embeddings for {len(text_entities)} text entities')
        documents = list[Document]()
        for te in text_entities:
            vector = self._model.apply(text=te)
            ee = EmbeddingEntity(id=te, vector=list(vector))
            logging.info(f'generated embedding with id "{ee.id}"')
            documents.append(ee)

        collection = self._environment.collection
        self._solr_client.add_documents(documents=documents, collection=collection, commit=self._commit)

    def apply(self):
        pipeline = self._environment.pipeline
        match pipeline:

            case 'add_text':
                logging.info('start adding embeddings from text')

                text = self._environment.text
                self._pipeline_from_text(text=text)

            case 'add_doc':
                logging.info(f'start adding embeddings from document')
                filename = self._environment.filename
                document = self._tika_extractor.apply(filename=filename)

                text = document.text
                self._pipeline_from_text(text=text)

