import logging
from typing import List

import torch.cuda
import nltk.data
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, T5ForConditionalGeneration


class TextEmbedder:

    def __init__(self, model_name: str, cache_folder: str):
        self._model_name = model_name
        self._cache_folder = cache_folder
        self._device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self._model = SentenceTransformer(model_name, cache_folder=cache_folder, device=self._device)

    def apply(self, texts: str | List[str], show_progress_bar: bool = None, normalize_embeddings: bool = True) -> np.ndarray:
        embeddings = self._model.encode(
            sentences=texts,
            show_progress_bar=show_progress_bar,
            device=self._device,
            normalize_embeddings=normalize_embeddings,
        )
        return embeddings


class TextTokenizer:

    def __init__(self, package: str = 'punkt'):
        self._package = package
        try:
            nltk.data.find(f'tokenizers/{package}')
        except LookupError:
            nltk.download(f'{package}')

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


class Summarizer:

    def __init__(self, model_name: str, cache_folder: str):
        self._model_name = model_name
        self._cache_folder = cache_folder

        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._model = T5ForConditionalGeneration.from_pretrained(model_name, cache_dir=cache_folder)

    def get_answer(self, query: str, context: str) -> str:
        prompt = f'context: {context} question: {query}'
        inputs = self._tokenizer.encode(prompt, return_tensors='pt')

        outputs = self._model.generate(inputs)
        answer = self._tokenizer.decode(outputs[0])
        return answer
