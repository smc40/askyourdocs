import logging
import os
from pathlib import Path
from typing import List

from askyourdocs import Environment
from askyourdocs.settings import SETTINGS


def get_solr_config_dir_settings(name: str) -> Path:
    return SETTINGS['paths']['root'] / SETTINGS['solr']['collections'].get(name)['config_files']


def get_solr_fields_settings(name: str) -> List[dict] | None:
    return SETTINGS['solr']['collections'].get(name).get('fields')


def get_solr_field_types_settings(name: str) -> List[dict] | None:
    return SETTINGS['solr']['collections'].get(name).get('field_types')


def load_environment() -> Environment:
    kwargs = {
        'log_level': os.getenv('LOG_LEVEL'),
        'tika_url': os.getenv('TIKA_URL'),
        'solr_url': os.getenv('SOLR_URL'),
        'zk_urls': os.getenv('ZK_URLS'),
        'frontend_url': os.getenv('FRONTEND_URL'),
    }
    return Environment(**kwargs)

