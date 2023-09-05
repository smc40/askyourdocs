import logging

from askyourdocs import Environment, Service, EmbeddingEntity
from askyourdocs.modelling.llm import TextEmbedder, TextTokenizer


class Modelling(Service):
    """Modelling service."""
    _entity_name = __qualname__  # type: ignore

    def __init__(self, environment: Environment, settings: dict):
        logging.info(f"initializing service: {self._entity_name}")
        super().__init__(environment=environment, settings=settings)

        model_name = settings['modeling']['model_name']
        cache_folder = settings['paths']['models']
        self._model = TextEmbedder(model_name=model_name, cache_folder=cache_folder)

        package = settings['modeling']['tokenizer_package']
        self._tokenizer = TextTokenizer(package=package)

    def apply(self):
        modelling = self._environment.modelling
        match modelling:

            case 'embedding':
                logging.info(f'start text embedding')
                text = self._environment.text
                vector = self._model.apply(text=text)
                embedding = EmbeddingEntity(id=text, vector=list(vector))
                logging.info(f'vector has length{len(embedding.vector)}')

            case 'tokenization':
                logging.info(f'start text tokenization')
                text = self._environment.text
                text_entities = self._tokenizer.get_text_entities(text=text)
                logging.info(f'tokenized into {len(text_entities)} text entities')
