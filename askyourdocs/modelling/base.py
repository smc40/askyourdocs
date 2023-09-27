import logging

from askyourdocs import Environment, Service, EmbeddingEntity
from askyourdocs.modelling.llm import TextEmbedder, TextTokenizer


class ModellingService(Service):
    """Modelling service."""
    _entity_name = __qualname__  # type: ignore

    def __init__(self, environment: Environment, settings: dict):
        logging.info(f"initializing service: {self._entity_name}")
        super().__init__(environment=environment, settings=settings)

    def apply(self):
        modelling = self._environment.modelling
        match modelling:

            case 'embedding':
                logging.info(f'start text embedding')
                model_name = self._settings['modelling']['model_name']
                cache_folder = self._settings['paths']['models']
                model = TextEmbedder(model_name=model_name, cache_folder=cache_folder)

                text = self._environment.text
                vector = model.apply(texts=text)
                embedding = EmbeddingEntity(id=text, vector=list(vector))
                logging.info(f'vector has length{len(embedding.vector)}')

            case 'tokenization':
                logging.info(f'start text tokenization')
                package = self._settings['modelling']['tokenizer_package']
                tokenizer = TextTokenizer(package=package)

                text = self._environment.text
                text_entities = tokenizer.get_text_entities(text=text)
                logging.info(f'tokenized into {len(text_entities)} text entities')
