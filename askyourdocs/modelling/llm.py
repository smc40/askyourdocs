import logging
from typing import List

import torch.cuda
import nltk.data
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, T5ForConditionalGeneration
import os
from openai import AzureOpenAI
from askyourdocs.settings import SETTINGS as settings

class AzureOpenAIClient:
    def __init__(self, api_key: None | str = None, azure_endpoint: None | str = None, api_version: str = "2023-05-15", settings=settings):
        if api_key:
            self._api_key = api_key
        else:
            self._api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if azure_endpoint:
            self._azure_endpoint = azure_endpoint
        else:
            self._azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self._api_version = api_version
        
    def get_client(self):
        if self._api_key and self._azure_endpoint:
            return AzureOpenAI(api_key=self._api_key, 
                            api_version=self._api_version,
                            azure_endpoint=self._azure_endpoint)
            
        else:
            logging.error("Azure OpenAI API key or endpoint not provided")
            return None
        
    def get_embedding(self, text: str, model: str = settings['modelling']['embedding_model_name']):
        client = self.get_client()
        if client:
            return client.embeddings.create(input=[text], model=model).data[0].embedding
        else:
            return None
    
    def get_summary(self, task: str, query: str, context: str, summarizing_model: str = settings['modelling']['model_name']):
        client = self.get_client()
        if client:
            messages=[
                {"role": "system", "content": f'{task}'},
                {"role": "user", "content": f'{query}'},
                {"role": "assistant", "content": f'{context}'},
            ]
            
            response = client.chat.completions.create(
                model=summarizing_model,
                messages=messages
            )
            return response.choices[0].message.content
        else:
            return None
        
        

class TextEmbedder:

    def __init__(self, model_name: str, cache_folder: str, settings: dict):
        self._settings = settings
        self._model_name = model_name
        self._cache_folder = cache_folder
        self._device = 'cuda' if torch.cuda.is_available() else 'cpu'            
        self._client, self._model = (AzureOpenAIClient(), None) if 'gpt-' in model_name else (None, SentenceTransformer(model_name, cache_folder=cache_folder, device=self._device))
        

    def apply(self, texts: str | List[str], show_progress_bar: bool = None, normalize_embeddings: bool = True) -> np.ndarray:
        # Ensure `texts` is always treated as a list for uniform processing
        texts, flatten = ([texts], True) if isinstance(texts, str) else (texts, False)
        
        if self._client:
            # Fetch embeddings
            embeddings_list = [self._client.get_embedding(text=text, model=self._settings['modelling'].get('embedding_model_name')) for text in texts if isinstance(text, str) and len(text) > 10]
            embeddings = np.array(embeddings_list)  # Convert list to NumPy array for uniform processing
            
            if normalize_embeddings and embeddings.size > 0:
                norms = np.linalg.norm(embeddings, axis=-1 if embeddings.ndim == 1 else 1, keepdims=True)
                norms[norms == 0] = 1  # Prevent division by zero
                embeddings = embeddings / norms
        else:
            # Assuming the model's encode method returns a NumPy array or can be treated as such
            embeddings = self._model.encode(
                sentences=texts,
                show_progress_bar=show_progress_bar,
                device=self._device,
                normalize_embeddings=normalize_embeddings,
            )
        
        # Decide whether to return a single embedding or all embeddings based on the input
        return embeddings[0] if flatten and embeddings.ndim > 1 else embeddings

class TextTokenizer:

    def __init__(self, package: str = 'punkt'):
        self._package = package
        try:
            nltk.data.find(f'tokenizers/{package}')
        except LookupError:
            nltk.download(f'{package}')

    def get_text_entities(self, text: str, entity: str = 'sentence') -> List[str]:
        match entity:
            case 'sentence':
                logging.info('tokenizing text into sentences')
                sentences = nltk.sent_tokenize(text=text)
                sentences = self._ensure_sentence_length(sentences, text)
                return sentences
            case 'word':
                logging.info('tokenizing text into words')
                return nltk.word_tokenize(text=text)

            case _:
                logging.error(f'unknown token entity {entity}')
                
    @staticmethod
    def _ensure_sentence_length(sentences: List[str], original_text: str, min_length: int = 20) -> List[str]:
        """
        Ensure sentences have at least `min_length` characters, concatenating them if necessary,
        and keep original spacing after dots.
        """
        processed_sentences = []
        sentence_buffer = ""
        for i, sentence in enumerate(sentences):
            sentence_with_space = sentence + " "
            if len(sentence_buffer + sentence_with_space) >= min_length and len(sentence_buffer) < min_length:
                processed_sentences.append((sentence_buffer + sentence_with_space).strip())
                sentence_buffer = ""
            else:
                sentence_buffer += sentence_with_space

            # Check if it's the last sentence and add it to the processed sentences
            if i == len(sentences) - 1 and len(processed_sentences) >= min_length:
                processed_sentences.append(sentence_buffer.strip())

        return processed_sentences


class Summarizer:

    _task = """I want you to act like a most rational person that only give answers for which he has strong evidence. 
    Therefore, I don't want you to give me any information that is not contained in the provided context. 
    Please just summarize the context with respect to the asked question in simple words. If there is no 
    related information in the context please inform me accordingly and do not generate the answer from your knowledge. 
    The context provided includes the chat history where the bot is your generated answer and the user is the query from the user.
    Please refer to the last user input and take the chat history into account when appropiate. Generate the answer in the language
    of the last user input."""

    def __init__(self, settings: dict):
        self._settings = settings
        model_name = settings['modelling']['model_name']
        cache_folder = settings['paths']['models']
        self._client, self._model = (AzureOpenAIClient(), None) if 'gpt-' in model_name else (None, T5ForConditionalGeneration.from_pretrained(model_name, cache_dir=cache_folder))
            
        self._tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small") # use always the same tokenizer
        # TODO do not use T5ForConditionalGeneration but rather a generic model
        self._ntok_max = settings['modelling']['ntok_max']
        self._no_repeat_ngram_size = settings['modelling']['no_repeat_ngram_size']

    def get_answer(self, query: str, context: str) -> str:
        prompt = (f'{self._task} Context: {context}\n\n. Briefly summarize the above context with respect to the'
        f'following question: {query}')
        if self._client:
            answer = self._client.get_summary(task=self._task, query=query, context=context)
        else:
            inputs = self._tokenizer.encode(prompt, return_tensors='pt')
            outputs = self._model.generate(inputs, max_length=self._ntok_max, no_repeat_ngram_size=self._no_repeat_ngram_size)
            answer = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
            
        return answer
    
if __name__ ==  '__main__':
    
    # execute in shell: export PYTHONPATH="/home/bouldermaettel/Documents/python-projects/askyourdocs:$PYTHONPATH"
    from askyourdocs.settings import SETTINGS as settings
    summarizer = Summarizer(settings=settings)
    query = "What is the capital of Switzerland?"
    context = "Berlin is the capital of Germany. Belarus is a country. Switzerland is a country."
    answer = summarizer.get_answer(query=query, context=context)
    print(answer) 

    
    model_name = settings['modelling']['model_name']
    cache_folder = settings['paths']['models']

    # text = ["Hello, world! i want more world!", 'be as you are']
    text = "Hello, world! i want more world!"
    text_embedder = TextEmbedder(model_name=model_name, cache_folder=cache_folder,settings=settings)
    emb = text_embedder.apply(text, normalize_embeddings=True)
    print(emb)
    
    tokenizer = TextTokenizer()
    sents = tokenizer.get_text_entities(text="Hello, world! i want more world! 1. 2. Helllo", entity='sentence')
    print(sents)
    #test
    