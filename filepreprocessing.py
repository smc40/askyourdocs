import os
import PyPDF2
from nltk import word_tokenize


# given pdffile path returns list of text sections with overlap, based on wordcount
def pdf_get_text_chunks(file_path, chunk_size, overlap):
    chunks = []
    filename = os.path.basename(file_path)  # Get the filename from the file path

    # open pdf file based on path
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)

        # extract all text of pdf
        text = ""
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text += page.extract_text()

        # tokenize text to words
        words = word_tokenize(text)
        num_words = len(words)

        # make chuncks with overlap of words
        i = 0
        while i < num_words:
            chunk_end = min(i + chunk_size, num_words)
            chunk = ' '.join(words[i:chunk_end])
            chunks.append(chunk)
            i += chunk_size - overlap

    return (filename, chunks)


# calls pdf_get_text_chunks for entire folder returning filename and chunks
def pdf_folder_to_chunks(folder_path, chunk_size, overlap):
    folder = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            chunks = pdf_get_text_chunks(file_path, chunk_size, overlap)
            folder.append(chunks)

    return folder



# Example usage 1 document and entire folder
folder_path = "docs"
file_path = f"{folder_path}/20211203_SwissPAR-Spikevax.pdf"

chunk_size = 200
overlap = 50

text_chunks = pdf_get_text_chunks(file_path, chunk_size, overlap)
all_pdfs = pdf_folder_to_chunks(folder_path, chunk_size, overlap)


# would like:
# preprocessing of text (punctation not included in wordcount etc) and potentially sections