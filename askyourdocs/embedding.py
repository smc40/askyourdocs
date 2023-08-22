from sentence_transformers import SentenceTransformer


# GET EMBEDDINGS
def get_embedding_sentence_transformer(input_text, model_card='multi-qa-distilbert-cos-v1'):
    """
    :param input_text: should be the text string to be embedded
    :param model_card: model_id from 'sentence_transformers' package (originally huggingface hub)
    :return:
    """
    model = SentenceTransformer(model_card)
    query_embedding = model.encode(input_text)
    return query_embedding

