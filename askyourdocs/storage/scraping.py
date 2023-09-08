from abc import abstractmethod
import logging
from pathlib import Path
import re

import requests
from tika import parser
import validators

from askyourdocs import Environment, Service, SearchDocument


class Extractor(Service):
    """Abstract base class for all scrapers (text-extractors)"""

    def __init__(self, environment: Environment, settings: dict):
        super().__init__(environment=environment, settings=settings)

    @abstractmethod
    def apply(self, url: str) -> SearchDocument:
        pass


class TikaExtractor(Extractor):
    """Text extractors for pdfs using tika."""

    _nchar_log_text = 150
    _success_status = 200

    def __init__(self, environment: Environment, settings: dict):
        super().__init__(environment=environment, settings=settings)
        self._tika_url = self._environment.tika_url

    def _get_log_text(self, text: str):
        text = re.sub('\n', ' ', text.strip())
        text = re.sub('\s{2,}', ' ', text)[:self._nchar_log_text]
        return text

    def apply(self, filename: str) -> SearchDocument:
        """Extracting the text from pdfs."""

        if Path(filename).is_file():
            logging.info(f'parsing local file "{filename}"')
            parsed = parser.from_file(filename=filename)
            text = parsed['content']

        elif validators.url(filename):
            logging.info(f'parsing url "{filename}"')
            response = requests.get(filename)

            if not (status := response.status_code) == self._success_status:
                logging.error(f'pdf request for url="{filename}" exited with status code {status}')
                text = None

            else:
                parsed = parser.from_buffer(response.content, self._tika_url)
                text = parsed['content']

        else:
            logging.error(f'unable to parse document "{filename}"')
            text = None

        if text:
            # Clean newline characters
            logging.info(f'text (len={len(text)}): "{self._get_log_text(text=text)}..."')
        filename = Path(filename)
        return SearchDocument(id=str(filename), name=filename.name, source=str(filename.parent), text=text)