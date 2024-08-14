import logging
import os
from pathlib import Path
from typing import List

from askyourdocs import Environment
from askyourdocs.settings import SETTINGS
# from askyourdocs.storage.client import SolrClient


def get_solr_config_dir_settings(name: str) -> Path:
    return SETTINGS['paths']['root'] / SETTINGS['solr']['collections'].get(name)['config_files']


def get_solr_fields_settings(name: str) -> List[dict] | None:
    return SETTINGS['solr']['collections'].get(name).get('fields')


def get_solr_field_types_settings(name: str) -> List[dict] | None:
    return SETTINGS['solr']['collections'].get(name).get('field_types')


def get_solr_collection_names() -> List[str]:
    return [name for name in SETTINGS['solr']['collections']['map'].values()]


def load_environment() -> Environment:
    kwargs = {
        'log_level': os.getenv('LOG_LEVEL'),
        'tika_url': os.getenv('TIKA_URL'),
        'solr_url': os.getenv('SOLR_URL'),
        'zk_urls': os.getenv('ZK_URLS'),
    }
    return Environment(**kwargs)

# def get_user_settings_new(user_id: str) -> dict:
#     return SolrClient.get_user_settings(user_id)