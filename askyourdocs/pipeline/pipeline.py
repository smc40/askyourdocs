from abc import ABC, abstractmethod
import logging
from pathlib import Path
from typing import Any, List

import numpy as np
import pandas as pd
from transformers import AutoTokenizer

from askyourdocs import Environment, TextDocument, TextEntity, EmbeddingEntity, FeedbackDocument
from askyourdocs.storage.scraping import TikaExtractor
from askyourdocs.storage.client import SolrClient
from askyourdocs.modelling.llm import TextEmbedder, TextTokenizer, Summarizer

class Pipeline(ABC):

    def __init__(self, environment: Environment, settings: dict):
        self._environment = environment
        self._settings = settings

    @abstractmethod
    def apply(self, **kwargs) -> Any:
        pass


class IngestionPipeline(Pipeline):

    def __init__(self, environment: Environment, settings: dict):
        super().__init__(environment=environment, settings=settings)

        # Solr database interaction client
        self._solr_client = SolrClient(environment=environment, settings=settings)

        # Text tokenizer service
        package = settings['modelling']['tokenizer_package']
        self._text_tokenizer = TextTokenizer(package=package)

        # Text embedding service
        model_name = settings['modelling']['model_name']
        cache_folder = settings['paths']['models']
        self._text_embedder = TextEmbedder(model_name=model_name, cache_folder=cache_folder, settings=settings)

    def _get_document_from_file(self, filename: str, user_id: str) -> TextDocument:
        """Extract the text from a given file."""
        tika_extractor = TikaExtractor(environment=self._environment, settings=self._settings)
        document = tika_extractor.apply(filename=filename, user_id=user_id)
        return document

    def _get_text_entities_from_document(self, document: TextDocument, user_id: str) -> List[TextEntity]:
        """Generate and return a list of (overlapping) text entities from a given document text."""
        text = document.text
        if text is None:
            logging.error("OCR not yet implemented, empty PDF...")
            text = ""
        text_entities = self._text_tokenizer.get_text_entities(text=text)
        return [TextEntity(id=f'{document.id}{i}{te}', user_id=user_id, text=te, doc_id=document.id, index=i)
                for i, te in enumerate(text_entities)]

    def _get_embedding_entities_from_text_entities(self,
                                                   text_entities: List[TextEntity],
                                                   show_progress_bar: bool = None,
                                                   normalize_embeddings: bool = True,
                                                   user_id: str = None) -> List[EmbeddingEntity]:
        """Generate and return embeddings for a set of text entities."""
        texts = [te.text for te in text_entities]
        vectors = self._text_embedder.apply(texts=texts,
                                            show_progress_bar=show_progress_bar,
                                            normalize_embeddings=normalize_embeddings)
        embedding_entities = [EmbeddingEntity(id=te.text, user_id=user_id, vector=v, doc_id=te.doc_id, txt_ent_id=te.id)
                              for te, v in zip(text_entities, vectors)]
        return embedding_entities

    def _add_document(self, filename: str, commit: bool = False, user_id: str = None):
        logging.info(f'extract text from file "{filename}"')
        document = self._get_document_from_file(filename=filename, user_id=user_id)

        logging.info('split text into overlapping text entities')
        text_entities = self._get_text_entities_from_document(document=document, user_id=user_id)

        logging.info(f'generate text embeddings for {len(text_entities)} text entities')
        embedding_entities = self._get_embedding_entities_from_text_entities(text_entities=text_entities, show_progress_bar=True, user_id=user_id)

        logging.info(f'store document, texts, and embeddings to solr')
        collection = self._settings['solr']['collections']['map']['docs']
        doc_id = self._solr_client.add_document(document=document, collection=collection, commit=commit)
        collection = self._settings['solr']['collections']['map']['texts']
        self._solr_client.add_documents(documents=text_entities, collection=collection, commit=commit)
        collection = self._settings['solr']['collections']['map']['vecs']
        self._solr_client.add_documents(documents=embedding_entities, collection=collection, commit=commit)

        logging.info("from pipeline")
        logging.info(doc_id)
        return doc_id

    def apply(self, source: str, commit: bool = False, user_id: str = None):
        path = Path(source)
        if path.is_dir():
            files = [str(f) for f in path.iterdir() if f.is_file()]
            logging.info(f'adding {len(files)} files from directory {source}')
        elif path.is_file():
            files = [str(source)]
        else:
            files = []
            logging.error(f'{path} os not a file or a directory')

        doc_ids = []
        for f in files:
            doc_ids.append(self._add_document(filename=f, commit=commit, user_id=user_id))
        return doc_ids


class QueryPipeline(Pipeline):

    _txt_sep = ' '
    _nte_max = 100

    def __init__(self, environment: Environment, settings: dict):
        super().__init__(environment=environment, settings=settings)
        self._solr_client = SolrClient(environment=environment, settings=settings)
        self._texts_collection = settings['solr']['collections']['map']['texts']

        # Text embedding service
        model_name = settings['modelling']['model_name']
        cache_folder = settings['paths']['models']
        self._text_embedder = TextEmbedder(model_name=model_name, cache_folder=cache_folder, settings=settings)

        self._ntok_max = 1000 if 'gpt-3.5' in model_name else 10000 if 'gpt-4' in model_name else 512
        self._ntok_context_fraction = settings['modelling']['ntok_context_fraction']
        self._ntok_context = int(self._ntok_max * self._ntok_context_fraction)

        self._summarizer = Summarizer(settings=settings)
        self._tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small") if 'gpt-' in model_name else AutoTokenizer.from_pretrained(model_name)

    @staticmethod
    def _add_similarity_values(vector: np.ndarray, knn_embedding_entities: List[dict]):
        for ent in knn_embedding_entities:
            ent['score'] = np.dot(vector, ent['vector'])
        return knn_embedding_entities

    def _get_knn_vecs_from_text(self, text: str, user_id: str, show_progress_bar: bool = True, normalize_embeddings: bool = True) -> List[dict]:
        vector = self._text_embedder.apply(texts=text, show_progress_bar=show_progress_bar, normalize_embeddings=normalize_embeddings)
        top_k = self._settings['solr']['top_k']
        vec_str = '[' + ', '.join(map(str, vector)) + ']'
        knn_query = f'{{!knn f=vector topK={top_k}}}{vec_str}'

        collection = self._settings['solr']['collections']['map']['vecs']
        # Perform the Solr search with the constructed query and filter query
        params = {
            'fq': f'user_id:{user_id}'  # Filter query for user_id
        }
    
        response = self._solr_client.search(query=knn_query, collection=collection, params=params)
        knn_embedding_entities = self._add_similarity_values(vector=vector, knn_embedding_entities=response['docs'])
        
        if threshold := self._settings['solr']['filter_on_score']:
            knn_embedding_entities = [ent for ent in knn_embedding_entities if ent['score'] > threshold]
            f"scores: {[ent['score'] for ent in knn_embedding_entities]}"
        return knn_embedding_entities

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
            if 'gpt-' in self._settings['modelling']['model_name']:
                ntoks = len(text.split())
            else:
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
                text = _te.get('text') if _te.get('text') else ''
                doc_texts[(_te['doc_id'], _te['index'])] = text

        candidates = [(te['doc_id'], te['index']) for te in text_entities]
        context_texts = pd.Series([], index=multi_index)
        while len(candidates):
            #TODO: start from the beginning and not from the end (pop(0) instead of pop())
            doc_id, index = candidates.pop(0)
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

    def apply(self, text: str, answer_only: bool = True, user_id: str = None) -> List[dict]:
        logging.info(f'generate text embeddings for text "{text}"')

        logging.info(f'search k-nearest-neighbors for text')
        knn_vecs = self._get_knn_vecs_from_text(text=text, user_id=user_id)

        logging.info(f'search text entities')
        text_entities = self._get_text_entities_from_knn_vecs(knn_vecs=knn_vecs)

        logging.info(f'extract context from documents')
        context = self._get_context_from_text_entities(text_entities=text_entities)

        logging.info(f'generate answer to "{text}" based on context "{context[:200]}..."')
        answer = self._summarizer.get_answer(query=text, context=context)

        logging.info(f'answer: {answer}')

        doc_ids = [doc.get('doc_id') for doc in text_entities]
        indexes = [doc.get('index') for doc in text_entities]
        texts = [doc.get('text') for doc in text_entities]
        

        # Perform a Solr lookup to get the names associated with doc_ids
        collection = self._settings['solr']['collections']['map']['docs']
        query = " OR ".join([f'id:{doc_id}' for doc_id in doc_ids])
        params = {"fl": "id,name"}  # Assuming the name field in your Solr collection is named "name"
        response = self._solr_client.search(query=query, collection=collection, params=params)

        # Extract the names from the Solr response and create the names list
        doc_id_to_name = {doc['id']: doc['name'] for doc in response['docs']}
        names = [doc_id_to_name.get(doc_id, '') for doc_id in doc_ids]

        if answer_only:
            return [{"answer" : answer}]
        else:
            return [{"answer": answer, "doc_ids" : doc_ids, "indexes" : indexes, "texts": texts, "names": names}]


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
        self.solr_client = SolrClient(environment=environment, settings=settings)

    def apply(self, query: str, collection: str, params: dict, user_id: str = None):
        response = self.solr_client.search(query=query, collection=collection, params=params)
        return response['docs'] if 'ayd_docs' in collection else response.get('user_settings')['llm_model_name']


class FeedbackPipeline(Pipeline):

    def __init__(self, environment: Environment, settings: dict):  
        super().__init__(environment=environment, settings=settings)
        self._solr_client = SolrClient(environment=environment, settings=settings)

    def apply(self, feedback_type:str, feedback_text:str , email:str, commit: bool, feedback_to: str):
        collection = self._settings['solr']['collections']['map']['feedback']
        feedback = FeedbackDocument(id=feedback_type+feedback_text, feedback_type=feedback_type, text=feedback_text, feedback_to=feedback_to, email=email)
        logging.info(feedback)
        response = self._solr_client.add_document(document=feedback, collection=collection, commit=commit)

        return response
    
    
if __name__ == "__main__":
    
    # execute in shell: export PYTHONPATH="/home/bouldermaettel/Documents/python-projects/askyourdocs:$PYTHONPATH"
    import sys
    from askyourdocs.settings import SETTINGS as settings
    sys.path.append('/home/bouldermaettel/Documents/python-projects/askyourdocs')
    
    Environment.solr_url = "http://localhost:8983"
    Environment.zk_urls = "http://localhost:2181"
    
    query_pipeline = QueryPipeline(environment=Environment, settings=settings)

    # Perform a query
    results = query_pipeline._get_knn_vecs_from_text(text="is bern considered a city?", user_id='1749b037-7a7f-42a4-b57e-c543f0702863')
    print([result.get('score') for result in results])
    result_text = query_pipeline._get_text_entities_from_knn_vecs(knn_vecs=results, user_id='1749b037-7a7f-42a4-b57e-c543f0702863')
    text = query_pipeline._get_context_from_text_entities(text_entities=result_text, user_id='1749b037-7a7f-42a4-b57e-c543f0702863')
    print(text)
