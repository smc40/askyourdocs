import PyPDF2
from nltk import word_tokenize

# given pdffile path returns list of text sections with overlap, based on wordcount
def pdf_get_text_chunks(file_path, chunk_size, overlap):
    chunks = []
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        
        text = ""
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text += page.extract_text()
        
        words = word_tokenize(text)
        num_words = len(words)

        i = 0
        while i < num_words:
            chunk_end = min(i + chunk_size, num_words)
            chunk = ' '.join(words[i:chunk_end])
            chunks.append(chunk)
            i += chunk_size - overlap

    return chunks

# Example usage
file_path = "docs/20211203_SwissPAR-Spikevax.pdf"
chunk_size = 200
overlap = 50

text_chunks = pdf_get_text_chunks(file_path, chunk_size, overlap)


# would like:
# preprocessing of text (punctation not included in wordcount etc) and potentially sections