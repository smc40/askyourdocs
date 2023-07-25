from pydantic import BaseSettings


class Settings(BaseSettings):
    qa_model_card: str = "google/flan-t5-small"
    sentence_model_card: str = "multi-qa-distilbert-cos-v1"
    debug_mode: bool = True
    default_doc: str = "docs/20211203_SwissPAR_Spikevax_single_page_text.pdf"

    class Config:
        env_prefix = "ayd_"

