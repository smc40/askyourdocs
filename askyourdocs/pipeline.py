import logging
from typing import List, Tuple

from tqdm import tqdm

from askyourdocs import SearchDocument, TextEntity, EmbeddingEntity
import askyourdocs.utils as utl
from askyourdocs.settings import SETTINGS as settings
from askyourdocs.storage.scraping import TikaExtractor
from askyourdocs.modelling.llm import TextEmbedder, TextTokenizer

# from askyourdocs.embedding import get_embedding_sentence_transformer
# from askyourdocs.similarity import model_qa, cosine_similarity

environment = utl.load_environment()
_TIKA_EXTRACTOR = TikaExtractor(environment=environment, settings=settings)

model_name = settings['modeling']['model_name']
cache_folder = settings['paths']['models']
_TEXT_EMBEDDER = TextEmbedder(model_name=model_name, cache_folder=cache_folder)

# Text tokenizer service
package = settings['modeling']['tokenizer_package']
_TEXT_TOKENIZER = TextTokenizer(package=package)


def text_from_file(filename: str) -> SearchDocument:
    logging.info(f'extract text from file "{filename}"')
    document = _TIKA_EXTRACTOR.apply(filename=filename)
    return document


def text_entity_embeddings_from_document(document: SearchDocument) -> List[Tuple[TextEntity, EmbeddingEntity]]:
    # Split text into (overlapping) text chunks
    logging.info('split text into overlapping text entities')
    text = document.text
    chunk_size = settings['modeling']['chunk_size']
    overlap = settings['modeling']['overlap']
    text_entities = _TEXT_TOKENIZER.get_overlapping_text_entities(text=text, chunk_size=chunk_size, overlap=overlap)

    # Generate text embeddings from the text entities
    embedding_entities = []
    for entity in tqdm(text_entities):
        embeddings = _TEXT_EMBEDDER.apply(text=entity)
        te = TextEntity(id=entity, text=text, doc_id=document.id)
        ee = EmbeddingEntity(id=entity, vector=embeddings, text_ent_id=te.id)
        embedding_entities.append((te, ee))

    return embedding_entities



################################ TODO ################################
# Continue from here
# - remove what is below


def embedding_loaded_pdf(file_path, chunk_size, overlap):

    # FIRST WE LOAD PDF
    text = TikaExtractor().apply(filename=file_path).text
    # text_chunks = pdf_get_text_chunks(file_path, chunk_size, overlap)
    text_entities = utl.get_overlapping_text_entities(text=text, chunk_size=chunk_size, overlap=overlap)

    # GENERATE DB_ITEMS UTILIZING ALL CHUNKS
    db_items = []
    for entity in tqdm(text_entities):
        vector = get_embedding_sentence_transformer(entity.text)
        db_items.append(['filename', text, vector])

    return db_items


def pipeline_return_question_and_answer(query, db_items, n_chunks):

    # WE TRANSFORM THE QUERY TEXT INTO AN EMBEDDING
    query_emb = get_embedding_sentence_transformer(query)

    # GIVEN A DB_ITEMS COLLECTION, GET TOP MATCHES
    top_items = cosine_similarity(query_emb, db_items, top_pick=n_chunks)

    print(f"{top_items}")
    # PROVIDE QUESTION, TOP MATCHES ON THE EMBEDDED LIST OF ITEMS
    answer = model_qa(query, top_items, model_card='google/flan-t5-small')

    return answer

#############
# optional - for debugging / testing
#############
# db_items = embedding_loaded_pdf('docs/20211203_SwissPAR_Spikevax_single_page_text.pdf', 50, 10)
# print(db_items)
# answer = pipeline_return_question_and_answer('What did the applicant want?', db_items)
# print(answer)
