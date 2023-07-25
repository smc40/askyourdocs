from filepreprocessing import pdf_get_text_chunks
from tqdm import tqdm
from embedding import get_embedding_sentence_transformer
from similarity import model_qa, cosine_similarity

## it may be more efficient to preload embedding and QA models to accelerate the running time.
# from sentence_transformers import SentenceTransformer
# from transformers import T5ForConditionalGeneration, AutoTokenizer

# embed_modelcard = 'multi-qa-distilbert-cos-v1'
# qa_modelcard = 'google/flan-t5-large'
# embed_model = SentenceTransformer(embed_modelcard)
# qa_tokenizer = AutoTokenizer.from_pretrained(qa_modelcard, model_max_length = 1024) # modify the max_length of tokenizer for longer texts.
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') # preload the model into GPU if applicable
# qa_model = T5ForConditionalGeneration.from_pretrained(qa_modelcard).to(device) 

def embedding_loaded_pdf(file_path, chunk_size, overlap):

    # FIRST WE LOAD PDF
    text_chunks = pdf_get_text_chunks(file_path, chunk_size, overlap)

    # GENERATE DB_ITEMS UTILIZING ALL CHUNKS
    db_items = []
    for filename, text in tqdm(text_chunks):
        # vector = get_embedding_sentence_transformer(embed_model, text) # if embed_model is preloaded
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
    # answer = model_qa(query, top_items, qa_model, qa_tokenizer, model_card='google/flan-t5-small')
    answer = model_qa(query, top_items, model_card='google/flan-t5-small')
    return answer

#############
# optional - for debugging / testing
#############
# db_items = embedding_loaded_pdf('docs/20211203_SwissPAR_Spikevax_single_page_text.pdf', 50, 10)
# print(db_items)
# answer = pipeline_return_question_and_answer('What did the applicant want?', db_items)
# print(answer)
