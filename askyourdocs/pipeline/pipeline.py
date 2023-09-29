from abc import ABC, abstractmethod
import logging
from typing import Any, List

import nltk
import pandas as pd
from transformers import AutoTokenizer

from askyourdocs import Environment, SearchDocument, TextEntity, EmbeddingEntity
from askyourdocs.storage.scraping import TikaExtractor
from askyourdocs.storage.client import SolrClient
from askyourdocs.modelling.llm import TextEmbedder, TextTokenizer, Summarizer


class Pipeline(ABC):

    def __init__(self, environment: Environment, settings: dict):
        self._environment = environment
        self._settings = settings

        # Text embedding service
        model_name = settings['modelling']['model_name']
        cache_folder = settings['paths']['models']
        self._text_embedder = TextEmbedder(model_name=model_name, cache_folder=cache_folder)

    @abstractmethod
    def apply(self, **kwargs) -> Any:
        pass


class IngestionPipeline(Pipeline):

    def __init__(self, environment: Environment, settings: dict):
        super().__init__(environment=environment, settings=settings)

        # Solr database interaction client
        self._solr_client = SolrClient(environment=environment, settings=settings)

        # Document text extraction service
        self._tika_extractor = TikaExtractor(environment=environment, settings=settings)

        # Text tokenizer service
        package = settings['modelling']['tokenizer_package']
        self._text_tokenizer = TextTokenizer(package=package)

    def _get_document_from_file(self, filename: str) -> SearchDocument:
        """Extract the text from a given file."""
        document = self._tika_extractor.apply(filename=filename)
        return document

    @staticmethod
    def _get_text_entities_from_document(document: SearchDocument) -> List[TextEntity]:
        """Generate and return a list of (overlapping) text entities from a given document text."""
        text = document.text
        text_entities = nltk.sent_tokenize(text=text)
        return [TextEntity(id=f'{document.id}{i}{te}', text=te, doc_id=document.id, index=i)
                for i, te in enumerate(text_entities)]

    def _get_embedding_entities_from_text_entities(self,
                                                   text_entities: List[TextEntity],
                                                   show_progress_bar: bool = None,
                                                   normalize_embeddings: bool = True) -> List[EmbeddingEntity]:
        """Generate and return embeddings for a set of text entities."""
        texts = [te.text for te in text_entities]
        vectors = self._text_embedder.apply(texts=texts,
                                            show_progress_bar=show_progress_bar,
                                            normalize_embeddings=normalize_embeddings)
        embedding_entities = [EmbeddingEntity(id=te.text, vector=v, doc_id=te.doc_id, txt_ent_id=te.id)
                              for te, v in zip(text_entities, vectors)]
        return embedding_entities

    def apply(self, filename: str, commit: bool = False):
        logging.info(f'extract text from file "{filename}"')
        document = self._get_document_from_file(filename=filename)

        logging.info('split text into overlapping text entities')
        text_entities = self._get_text_entities_from_document(document=document)

        logging.info(f'generate text embeddings for {len(text_entities)} text entities')
        embedding_entities = self._get_embedding_entities_from_text_entities(text_entities=text_entities, show_progress_bar=True)

        logging.info(f'store document, texts, and embeddings to solr')
        collection = self._settings['solr']['collections']['map']['docs']
        doc_id = self._solr_client.add_document(document=document, collection=collection, commit=commit)
        collection = self._settings['solr']['collections']['map']['texts']
        self._solr_client.add_documents(documents=text_entities, collection=collection, commit=commit)
        collection = self._settings['solr']['collections']['map']['vecs']
        self._solr_client.add_documents(documents=embedding_entities, collection=collection, commit=commit)
        return doc_id


class QueryPipeline(Pipeline):

    _txt_sep = ' '
    _nte_max = 100

    def __init__(self, environment: Environment, settings: dict):
        super().__init__(environment=environment, settings=settings)
        self._solr_client = SolrClient(environment=environment, settings=settings)
        self._texts_collection = settings['solr']['collections']['map']['texts']

        self._summarizer = Summarizer(settings=settings)
        self._tokenizer = AutoTokenizer.from_pretrained(settings['modelling']['model_name'])

        self._ntok_max = settings['modelling']['ntok_max']
        self._ntok_context_fraction = settings['modelling']['ntok_context_fraction']
        self._ntok_context = int(self._ntok_max * self._ntok_context_fraction)

    def _get_knn_vecs_from_text(self, text: str) -> List[dict]:
        vector = self._text_embedder.apply(texts=text)
        top_k = self._settings['solr']['top_k']
        vec_str = '[' + ', '.join(str(v) for v in vector) + ']'
        query = f'{{!knn f=vector topK={top_k}}}{vec_str}'

        collection = self._settings['solr']['collections']['map']['vecs']
        response = self._solr_client.search(query=query, collection=collection)
        return response['docs']

    def _get_text_entities_from_knn_vecs(self, knn_vecs: List[dict]) -> List[dict]:
        te_ids = list(set(v['txt_ent_id'] for v in knn_vecs))
        query = f'id:({" OR ".join(te_ids)})'
        collection = self._settings['solr']['collections']['map']['texts']
        response = self._solr_client.search(query=query, collection=collection)
        return response['docs']

    def _get_context_from_text_entities(self, text_entities: List[dict]) -> str:

        def _concatenate_texts_from_series(cntxt: pd.Series) -> str:
            return self._txt_sep.join(cntxt.sort_index())

        def _is_below_ntok_max(cntxt: pd.Series) -> bool:
            text = _concatenate_texts_from_series(cntxt=cntxt)
            ntoks = len(self._tokenizer.tokenize(text))
            return ntoks <= self._ntok_context

        multi_index = pd.MultiIndex.from_arrays([[], []], names=['doc_id', 'txt_ind'])
        doc_texts = pd.Series([], index=multi_index)
        for te in text_entities:
            start = max(0, te['index'] - self._nte_max // 2)
            rows = self._nte_max
            query = f'doc_id:{te["doc_id"]}'
            params = {'start': start, 'rows': rows, "sort": "index asc"}
            response = self._solr_client.search(query=query, collection=self._texts_collection, params=params)
            for _te in response['docs']:
                doc_texts[(_te['doc_id'], _te['index'])] = _te['text']

        candidates = [(te['doc_id'], te['index']) for te in text_entities]
        context_texts = pd.Series([], index=multi_index)
        while len(candidates):
            doc_id, index = candidates.pop()
            if (doc_id, index) not in context_texts:
                context_texts[(doc_id, index)] = doc_texts[(doc_id, index)]

                if not _is_below_ntok_max(context_texts):
                    context_texts.drop((doc_id, index), inplace=True)
                    break

                if (doc_id, index - 1) in doc_texts:
                    candidates.append((doc_id, index - 1))
                if (doc_id, index + 1) in doc_texts:
                    candidates.append((doc_id, index + 1))

        return _concatenate_texts_from_series(context_texts)

    def apply(self, text: str) -> str:
        logging.info(f'generate text embeddings for text "{text}"')

        logging.info(f'search k-nearest-neighbors for text')
        knn_vecs = self._get_knn_vecs_from_text(text=text)

        logging.info(f'search text entities')
        text_entities = self._get_text_entities_from_knn_vecs(knn_vecs=knn_vecs)

        logging.info(f'extract context from documents')
        context = self._get_context_from_text_entities(text_entities=text_entities)

        logging.info(f'generate answer to "{text}" based on context "{context[:200]}..."')
        answer = self._summarizer.get_answer(query=text, context=context)
        return answer

class RemovalPipeline(Pipeline):

    def __init__(self, environment: Environment, settings: dict):
        super().__init__(environment=environment, settings=settings)
        self._solr_client = SolrClient(environment=environment, settings=settings)

    def apply(self, id_: str, commit: bool = False):
        collection = self._settings['solr']['collections']['map']['docs']
        self._solr_client.delete_document(by=f"id:{id_}", collection=collection, commit=commit)
        collection = self._settings['solr']['collections']['map']['texts']
        self._solr_client.delete_document(by=f"doc_id:{id_}", collection=collection, commit=commit)
        collection = self._settings['solr']['collections']['map']['vecs']
        self._solr_client.delete_document(by=f"doc_id:{id_}", collection=collection, commit=commit)


class SearchPipeline(Pipeline):

    def __init__(self, environment: Environment, settings: dict):
        super().__init__(environment=environment, settings=settings)
        self._solr_client = SolrClient(environment=environment, settings=settings)

    def apply(self, query: str, collection: str, params: dict):
        response = self._solr_client.search(query=query, collection=collection, params=params)
        return response['docs']