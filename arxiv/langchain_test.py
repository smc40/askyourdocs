from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
import os
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "XXXX"

# location of the pdf file/files.
doc_reader = PdfReader('../data/book.pdf')

raw_text = ''
for i, page in enumerate(doc_reader.pages):
    text = page.extract_text()
    if text:
        raw_text += text

### SPLITTING

# Splitting up the text into smaller chunks for indexing
text_splitter = CharacterTextSplitter(
    separator = "\n",
    chunk_size = 500,
    chunk_overlap  = 200, #striding over the text
    length_function = len,
)
texts = text_splitter.split_text(raw_text)

from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import Chroma

vectorstore_path = "../data/20230607_db"

class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self._embedding_function = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        embeddings = self._embedding_function.encode(texts, convert_to_numpy=True).tolist()
        return [list(map(float, e)) for e in embeddings]

    def embed_query(self, text):
        embeddings = self._embedding_function.encode([text], convert_to_numpy=True).tolist()
        return [list(map(float, e)) for e in embeddings][0]


vectorstore = Chroma

reset_database = True

embeddings = SentenceTransformerEmbeddings()

if reset_database:
    print("[*] deleting the collection...")
    db = vectorstore(persist_directory=vectorstore_path, embedding_function=embeddings)
    db.delete_collection()
    db = None

print("[*] opening vectorstore...")
db = vectorstore(persist_directory=vectorstore_path, embedding_function=embeddings)
db.persist_directory = vectorstore_path
print(db.persist_directory)

if reset_database:
    # num_tokens = llm.get_num_tokens(text="\n".join(texts))
    # print("[*] embedding input documents and populating vectorstore (%d tokens)..." % num_tokens)
    db.add_texts(texts=texts)
    db = vectorstore.from_texts(texts, embeddings, persist_directory=vectorstore_path)
    print("[*] writing vectorstore to disk...")
    db.persist()

from langchain.chains.question_answering import load_qa_chain
from langchain import HuggingFaceHub
#llm=HuggingFaceHub(repo_id="google/flan-t5-xl", model_kwargs={"temperature":0, "max_length":512})
llm=HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.7, "max_length":64})
chain = load_qa_chain(llm, chain_type="stuff")

queries = [
    "Who did I meet for coffee and what did we talk about?",
    "What does my coffee buddy do for a living?",
    "What sort of clouds did I see on a rainy day?",
]

max_query = 4
total_docs = db._collection.count()  # chromadb specific hack
print(f'Total number of docs is: {total_docs}')
num_query = max_query if len(texts) > max_query and max_query > 0 else total_docs

# from llama_cpp import Llama
# llm = Llama(model_path="../models/alpaca-7B/ggml-alpaca-7b-q4.bin")
# -------------
# DEFINE CHAIN
# --------------
from langchain.chains.question_answering import load_qa_chain

chain = load_qa_chain(llm, chain_type="stuff")

for query in queries:
    print("\n[*] embedding query (\"%s\")..." % query)
    embedding_vector = embeddings.embed_query(query)

    print("[*] performing document search...")
    # docs = db.similarity_search(query, num_query)
    docs = db.similarity_search_by_vector(embedding_vector, num_query)

    result = chain({"input_documents": docs, "question": query})
    for i in range(0, len(docs)):
        print('\nNEW MATCH')
        print(docs[i])

    print("\nHUMAN:", query)
    print(f"ASSISTANT: {result['output_text']} \n")