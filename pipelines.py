from filepreprocessing import pdf_get_text_chunks
from tqdm import tqdm
from embedding import get_embedding_sentence_transformer
from similarity import model_qa, cosine_similarity


def embedding_loaded_pdf(file_path, chunk_size, overlap):

    # FIRST WE LOAD PDF
    text_chunks = pdf_get_text_chunks(file_path, chunk_size, overlap)

    # GENERATE DB_ITEMS UTILIZING ALL CHUNKS
    db_items = []
    for filename, text in tqdm(text_chunks):
        vector = get_embedding_sentence_transformer(text)
        db_items.append([filename, text, vector])

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
