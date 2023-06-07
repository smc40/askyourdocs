from filepreprocessing import pdf_get_text_chunks
import tqdm
from embedding import get_embedding_sentence_transformer


def embedding_loaded_pdf(file_path, chunk_size, overlap):

    # FIRST WE LOAD PDF
    text_chunks = pdf_get_text_chunks(file_path, chunk_size, overlap)

    # GENERATE DB_ITEMS UTILIZING ALL CHUNKS
    db_items = []
    for text in tqdm(text_chunks):
        vector = get_embedding_sentence_transformer(text)
        db_items.append([text, vector])

    return db_items
