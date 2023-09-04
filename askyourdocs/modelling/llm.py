import logging
from typing import List

import nltk.data
import numpy as np
from sentence_transformers import SentenceTransformer

from askyourdocs import Service, Environment


class TextEmbedding(Service):

    def __init__(self, environment: Environment, settings: dict, model_name: str):
        super().__init__(environment=environment, settings=settings)
        self._model_name = model_name
        self._model = SentenceTransformer(model_name, cache_folder=settings['paths']['models'], device='cuda')

    def apply(self, text: str) -> np.array:
        return self._model.encode(text)


class TextTokenizer(Service):

    def __init__(self, environment: Environment, settings: dict, package: str):
        super().__init__(environment=environment, settings=settings)
        self._package = package
        try:
            nltk.data.find(f'tokenizers/{package}')
        except LookupError:
            nltk.download(f'{package}')

    def apply(self, text: str) -> List[str]:
        logging.info('tokenizing text')
        return nltk.sent_tokenize(text=text)
