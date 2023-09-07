from abc import ABC, abstractmethod
import logging
from typing import Any, List

from askyourdocs import Environment, SearchDocument, TextEntity, EmbeddingEntity
from askyourdocs.storage.scraping import TikaExtractor
from askyourdocs.storage.management import SolrClient
from askyourdocs.modelling.llm import TextEmbedder, TextTokenizer


class Pipeline(ABC):

    def __init__(self, environment: Environment, settings: dict):
        # Document text extraction service
        self._tika_extractor = TikaExtractor(environment=environment, settings=settings)

        # Text embedding service
        model_name = settings['modeling']['model_name']
        cache_folder = settings['paths']['models']
        self._text_embedder = TextEmbedder(model_name=model_name, cache_folder=cache_folder)

        # Text tokenizer service
        package = settings['modeling']['tokenizer_package']
        self._text_tokenizer = TextTokenizer(package=package)
        self._chunk_size = settings['modeling']['chunk_size']
        self._overlap = settings['modeling']['overlap']

    @abstractmethod
    def apply(self, **kwargs) -> Any:
        pass

    def _get_document_from_file(self, filename: str) -> SearchDocument:
        """Extract the text from a given file."""
        document = self._tika_extractor.apply(filename=filename)
        return document

    def _get_text_entities_from_document(self, document: SearchDocument) -> List[TextEntity]:
        """Generate and return a list of (overlapping) text entities from a given document text."""
        text = document.text
        chunk_size = self._chunk_size
        overlap = self._overlap
        text_entities = self._text_tokenizer.get_overlapping_text_entities(text=text, chunk_size=chunk_size, overlap=overlap)

        return [TextEntity(id=te, text=te, doc_id=document.id) for te in text_entities]

    def _get_embedding_entities_from_text_entities(self,
                                                   text_entities: List[TextEntity],
                                                   show_progress_bar: bool = None,
                                                   normalize_embeddings: bool = True) -> List[EmbeddingEntity]:
        """Generate and return embeddings for a set of text entities."""
        texts = [te.text for te in text_entities]
        vectors = self._text_embedder.apply(texts=texts,
                                            show_progress_bar=show_progress_bar,
                                            normalize_embeddings=normalize_embeddings)
        embedding_entities = [EmbeddingEntity(id=te.text, vector=v, doc_id=te.doc_id, text_ent_id=te.id)
                              for te, v in zip(text_entities, vectors)]
        return embedding_entities


class IngestionPipeline(Pipeline):

    def __init__(self, environment: Environment, settings: dict):
        super().__init__(environment=environment, settings=settings)
        self._solr_client = SolrClient(environment=environment, settings=settings)

    def apply(self, filename: str, commit: bool = False):
        logging.info(f'extract text from file "{filename}"')
        document = self._get_document_from_file(filename=filename)

        logging.info('split text into overlapping text entities')
        text_entities = self._get_text_entities_from_document(document=document)

        logging.info(f'generate text embeddings for {len(text_entities)} text entities')
        embedding_entities = self._get_embedding_entities_from_text_entities(text_entities=text_entities, show_progress_bar=True)

        logging.info(f'store document and embeddings to solr')
        self._solr_client.add_document(document=document, collection='ayd_search', commit=commit)
        self._solr_client.add_documents(embedding_entities, collection='ayd_vector', commit=commit)





################################ TODO ################################
# Continue from here
# - remove what is below
#
#
# def embedding_loaded_pdf(file_path, chunk_size, overlap):
#
#     # FIRST WE LOAD PDF
#     text = TikaExtractor().apply(filename=file_path).text
#     # text_chunks = pdf_get_text_chunks(file_path, chunk_size, overlap)
#     text_entities = utl.get_overlapping_text_entities(text=text, chunk_size=chunk_size, overlap=overlap)
#
#     # GENERATE DB_ITEMS UTILIZING ALL CHUNKS
#     db_items = []
#     for entity in tqdm(text_entities):
#         vector = get_embedding_sentence_transformer(entity.text)
#         db_items.append(['filename', text, vector])
#
#     return db_items
#
#
# def pipeline_return_question_and_answer(query, db_items, n_chunks):
#
#     # WE TRANSFORM THE QUERY TEXT INTO AN EMBEDDING
#     query_emb = get_embedding_sentence_transformer(query)
#
#     # GIVEN A DB_ITEMS COLLECTION, GET TOP MATCHES
#     top_items = cosine_similarity(query_emb, db_items, top_pick=n_chunks)
#
#     print(f"{top_items}")
#     # PROVIDE QUESTION, TOP MATCHES ON THE EMBEDDED LIST OF ITEMS
#     answer = model_qa(query, top_items, model_card='google/flan-t5-small')
#
#     return answer

#############
# optional - for debugging / testing
#############
# db_items = embedding_loaded_pdf('docs/20211203_SwissPAR_Spikevax_single_page_text.pdf', 50, 10)
# print(db_items)
# answer = pipeline_return_question_and_answer('What did the applicant want?', db_items)
# print(answer)

if __name__ == '__main__':
    import askyourdocs.utils as utl
    from askyourdocs.settings import SETTINGS as settings
    environment = utl.load_environment()
    filename = str(settings['paths']['root'] / settings['data']['default_document'])

    ingestion_pipeline = IngestionPipeline(environment=environment, settings=settings)
    ingestion_pipeline.apply(filename=filename, commit=True)
