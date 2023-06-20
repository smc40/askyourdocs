from scipy.spatial.distance import cosine
from transformers import T5ForConditionalGeneration, AutoTokenizer

def calculate_cosine_similarity(vector1, vector2):
    return 1 - cosine(vector1, vector2)


def cosine_similarity(query_emb, db_items, top_pick=5):
    similarities = []
    for filename, text, vector in db_items:
        similarity = calculate_cosine_similarity(query_emb, vector)
        similarities.append(similarity)

    top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_pick]
    top_items = [db_items[i][1] for i in top_indices]
    return top_items


# QA model
def model_qa(question, refs, qa_model=None, qa_tokenizer=None, model_card='google/flan-t5-small', max_new_length=512):
    """

    :param question: string
    :param refs:
    :param qa_model: preload qa model
    :param qa_tokenizer: preload qa tokenzier
    :param model_card: if not preload qa model, then load the model from defined model_card
    :return:
    """
    if not qa_model:
        tokenizer = AutoTokenizer.from_pretrained(model_card)
        model = T5ForConditionalGeneration.from_pretrained(model_card)
    else:
        tokenzier = qa_tokenzier
        model = qa_model

    # define the max_new_length of output:
    model.config.max_new_tokens = max_new_length
    
    reference_doc = "\n".join(refs)
    input_text = "context: {} question: {}".format(reference_doc, question)
    inputs = tokenizer.encode(input_text, return_tensors='pt')

    outputs = model.generate(inputs)
    answer = tokenizer.decode(outputs[0])
    return answer
