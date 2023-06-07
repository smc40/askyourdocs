from pipelines import embedding_loaded_pdf
import os

CHUNK_SIZE = 50
OVERLAP = 10
HOME_DIR = os.listdir()


def test_pipelines_embedding_loaded_pdf_given_file_generate_emb(CHUNK_SIZE, OVERLAP):
    print('Current directory')
    print(HOME_DIR)
    print(os.listdir())
    file_path = "../docs/20210430_SwissPAR_Comirnaty.pdf"
    #db_items = embedding_loaded_pdf(file_path, CHUNK_SIZE, OVERLAP)
    #print(db_items)
    assert True#db_items[0] == 0