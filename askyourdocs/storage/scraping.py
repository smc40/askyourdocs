import logging
from pathlib import Path
import re
import requests
from tika import parser
import validators

from askyourdocs import Environment, Service, TextDocument

import logging
import requests
from pathlib import Path
from tika import parser
import re

from askyourdocs import Environment, Service, TextDocument

class TikaExtractor(Service):
    """Text extractor for PDFs using Tika with OCR capabilities."""

    _nchar_log_text = 150
    _success_status = 200

    def __init__(self, environment: Environment, settings: dict):
        super().__init__(environment=environment, settings=settings)
        self._tika_url = "http://localhost:9999"  # Default Tika server URL

    def _get_log_text(self, text: str):
        """Truncate and clean log text for easier readability."""
        text = re.sub('\n', ' ', text.strip())
        text = re.sub('\s{2,}', ' ', text)[:self._nchar_log_text]
        return text

    def apply(self, filename: str, user_id: str = None) -> TextDocument:
        """Extract text from PDFs with OCR enabled using Tika."""
        tika_ocr_headers = {
            'X-Tika-PDFOcrStrategy': 'ocr_and_text',  # 'ocr_only' if you want OCR only
            'X-Tika-OCRLanguage': 'deu',              # Adjust OCR language (e.g., 'eng', 'deu')
            'Accept': 'application/json'
        }

        try:
            # Reading file content to send manually using requests
            with open(filename, 'rb') as file:
                response = requests.put(
                    f'{self._tika_url}/tika',
                    headers=tika_ocr_headers,
                    data=file,
                    timeout=1200  # Set timeout to 1200 seconds or adjust as necessary
                )
            
            # Check if response was successful
            if response.status_code != self._success_status:
                logging.error(f"Failed to extract text. Status code: {response.status_code}")
                return None
            
            # Get text content from the response
            text = response.text

        except requests.exceptions.Timeout:
            logging.error(f"Timeout occurred while extracting text from '{filename}'")
            return None

        except Exception as e:
            logging.error(f"Error occurred while extracting text: {e}")
            return None

        # Log and return extracted text
        logging.info(f"text (len={len(text)}): '{self._get_log_text(text=text)}...'")

        return TextDocument(id=str(filename), user_id=user_id, name=Path(filename).name, source=str(Path(filename).parent), text=text)
