import logging
from typing import List

import nltk.data
import numpy as np
from sentence_transformers import SentenceTransformer


class TextEmbedder:

    def __init__(self, model_name: str, cache_folder: str):
        self._model_name = model_name
        self._cache_folder = cache_folder
        self._model = SentenceTransformer(model_name, cache_folder=cache_folder, device='cuda')

    def apply(self, text: str, normalized: bool = True) -> np.array:
        embeddings = self._model.encode(text)
        if normalized:
            embeddings = embeddings / np.linalg.norm(embeddings)
        return embeddings


class TextTokenizer:

    def __init__(self, package: str = 'punkt'):
        self._package = package
        try:
            nltk.data.find(f'tokenizers/{package}')
        except LookupError:
            nltk.download(f'{package}')

    def get_overlapping_text_entities(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        if chunk_size < overlap:
            overlap = chunk_size
            logging.warning(f'overlap has been reduced to chunk_size (={chunk_size})')

        words = self.get_text_entities(text=text, entity='word')
        nwords = len(words)

        index, chunk_end = 0, 0
        entities = []
        while index < nwords and chunk_end < nwords:
            chunk_end = min(index + chunk_size, nwords)
            chunk = ' '.join(words[index:chunk_end])
            entities.append(chunk)
            index += chunk_size - overlap

        return entities

    @staticmethod
    def get_text_entities(text: str, entity: str = 'sentence') -> List[str]:
        match entity:
            case 'sentence':
                logging.info('tokenizing text into sentences')
                return nltk.sent_tokenize(text=text)
            case 'word':
                logging.info('tokenizing text into words')
                return nltk.word_tokenize(text=text)

            case _:
                logging.error(f'unknown token entity {entity}')
