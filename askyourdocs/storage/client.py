import json
import logging
from pathlib import Path
from typing import List

import requests
from kazoo.client import KazooClient

from askyourdocs import Document, DocumentList, DocumentListEncoder
from askyourdocs import Environment, utils as utl


class SolrClient:
    _headers = {'content-type': 'application/json'}

    def __init__(self, environment: Environment, settings: dict):
        self._environment = environment
        self._settings = settings

        self._url = environment.solr_url
        self._url_api = self._url + '/api'
        self._url_api_collections = self._url_api + '/collections'

        self._zk_client: KazooClient | None = None
        self._zk_urls = environment.zk_urls

        self._nshards = settings.get('solr').get('nshards')

    def __repr__(self):
        cls_name = type(self).__name__
        return f'{cls_name}(environment={self._environment})'

    def __str__(self):
        return str(self.__repr__())

    @staticmethod
    def _delete(url: str, commit: bool = True):
        if commit:
            url += '?commit=true'
        response = requests.delete(url)
        response.raise_for_status()

    def _get(self, url: str, params: dict | None = None) -> dict:
        if params is None:
            params = dict()
        res = requests.get(url, headers=self._headers, params=params)
        res.raise_for_status()
        return res.json()

    def _post(self, url: str, data: dict) -> dict:
        res = requests.post(url, headers=self._headers, data=json.dumps(data))
        res.raise_for_status()
        return res.json()

    @staticmethod
    def _get_dest_dir(name: str):
        return f'/configs/{name}'

    @property
    def zk_client(self):
        if self._zk_client is None:
            self._zk_client = KazooClient(self._zk_urls, read_only=True)
            self._zk_client.start()
        return self._zk_client

    def _upload_file(self, filename: Path, zk_key: str):
        """Uploads a local file to a zookeeper key"""
        logging.info(f'uploading "{filename}" to zookeeper key "{zk_key}"')
        with open(filename, 'rb') as cfile:
            content = cfile.read()
        if self.zk_client.exists(zk_key):
            self.zk_client.set(zk_key, content)
        else:
            self.zk_client.create(zk_key, content)

    def _upload_directory(self, directory: Path, dest_dir: str):
        """Uploads a local directory to a zookeeper key"""

        if not self.zk_client.exists(dest_dir):
            self.zk_client.create(dest_dir)

        for filename in directory.iterdir():
            name = filename.name
            dest_dir_name = f'{dest_dir}/{name}'
            if filename.is_dir():
                self._upload_directory(directory=filename, dest_dir=dest_dir_name)
            else:
                self._upload_file(filename=filename, zk_key=dest_dir_name)

    def _upload_config(self, config_files: Path, dest_dir: str):
        """Uploads a local confiset to zookeeper."""
        if not config_files.exists():
            logging.error(f'config directory "{str(config_files)}" does not exist')

        if not self.zk_client.exists(dest_dir):
            self.zk_client.create(dest_dir)
        self._upload_directory(directory=config_files, dest_dir=dest_dir)

    def _create_collection(self, name: str) -> dict:
        """Creates a configured collection."""
        data = {
            "name": name,
            "config": name,
            "numShards": self._nshards
        }
        return self._post(url=self._url_api_collections, data=data)

    def _get_collections(self) -> list:
        """Returns all existing collections."""
        return self._get(self._url_api_collections)["collections"]

    def delete_collection(self, name: str, commit: bool = True) -> None:
        """Deletes a collection"""
        dest_dir = self._get_dest_dir(name=name)
        if self.zk_client.exists(dest_dir):
            self.zk_client.delete(dest_dir, recursive=True)

        url = f'{self._url_api_collections}/{name}'
        self._delete(url=url, commit=commit)

    def exists_collection(self, name: str) -> bool:
        """Checks if a given collection exists"""
        collections = self._get_collections()
        return name in collections

    def _file_changed(self, filename: Path, dest_dir: str):
        """Check if the content of the local file is the same as the value located under key in zookeeper"""
        logging.debug(f'comparing file contents of "{filename}" with "{dest_dir}"')
        with open(filename, 'rb') as cfile:
            content = cfile.read()
        return self.zk_client.get(dest_dir)[0] != content

    def _content_changed(self, config_files: Path, dest_dir: str) -> bool:
        """Check if the content of the local directory is the same as the value located under key in zookeeper"""
        logging.debug(f'comparing directory "{config_files}" with "{dest_dir}"')
        for filename in config_files.iterdir():
            name = filename.name
            if filename.is_dir():
                if self._content_changed(config_files=filename, dest_dir=f'{dest_dir}/{name}'):
                    return True
            else:
                if self._file_changed(filename=filename, dest_dir=f'{dest_dir}/{name}'):
                    return True
        return False

    def _config_changed(self, config_files: Path, dest_dir: str) -> bool:
        """Check if the content of the local configset is the same as the one stored in zookeeper"""
        name = config_files.name
        logging.info(f'checking if config files changed for collection "{name}')

        if not self.zk_client.exists(dest_dir):
            logging.error(f'Config for collection {name} does not exist in zookeeper')
            return False
        return self._content_changed(config_files=config_files, dest_dir=dest_dir)

    def _reindex_collection(self, name: str, batch_size: int = 1000):
        """Reindex all documents of a given collection"""
        logging.error(f'function "reindex_collection" not implemented yet')
        # TODO do reindexing
        #
        #
        #
        # results = self.get_client(Collections.SEARCH).delete(q="*:*")
        #
        # logging.info("Reinserting everything ...")
        # params = {"sort": "id asc", "cursorMark": "*"}
        # results = self.get_client(Collections.RAW).search("*:*", **params)
        # count = 0
        # for batch in chunks(results, batch_size):
        #     data = DocumentList()
        #     data.load_json([json.loads(x["data"]) for x in batch])
        #     count += len(data)
        #     self.add_docs(data, update=False)
        # return count

    def migrate_collection(self, name: str):
        """Migration of a collection"""
        logging.info(f'migrating collection "{name}"')
        config_files = utl.get_solr_config_dir_settings(name=name)
        dest_dir = self._get_dest_dir(name=name)

        reindex_docs = False
        if not self.exists_collection(name=name):
            logging.info(f'upload configuration files for collection "{name}"')
            dest_dir = self._get_dest_dir(name=name)
            self._upload_config(config_files=config_files, dest_dir=dest_dir)

            logging.info(f'create collection "{name}"')
            self._create_collection(name=name)

        elif self._config_changed(config_files=config_files, dest_dir=dest_dir):
            logging.info(f'upload configuration files for collection "{name}"')
            self._upload_config(config_files=config_files, dest_dir=dest_dir)
            reindex_docs = True
        else:
            logging.warning(f"Nothing to migrate for collection {name}")

        if (field_types := utl.get_solr_field_types_settings(name=name)) is not None:
            logging.info(f'migrate collection field types')
            self.migrate_collection_field_types(name=name, field_types=field_types)

        if (fields := utl.get_solr_fields_settings(name=name)) is not None:
            logging.info(f'migrate collection fields')
            self.migrate_collection_fields(name=name, fields=fields)

        if reindex_docs:
            logging.warning(f'starting reindexing of collection "{name}" this might take a while...')
            self._reindex_collection(name=name)
        logging.info("migration terminated")

    def add_document(self, document: Document, collection: str, commit: bool = False) -> str:
        logging.info(f'add {document.id} to collection "{collection}"')
        url = f'{self._url_api_collections}/{collection}/update'
        if commit:
            url += '?commit=true'

        response = requests.post(url, headers=self._headers, data=json.dumps(document.to_dict()))
        response.raise_for_status()

        return document.id


    def add_documents(self, documents: DocumentList, collection: str, commit: bool = False):
        logging.info(f'add {len(documents)} documents to collection "{collection}"')
        url = f'{self._url_api_collections}/{collection}/update'
        if commit:
            url += '?commit=true'
        data = json.dumps(documents, cls=DocumentListEncoder)
        response = requests.post(url, headers=self._headers, data=data)
        response.raise_for_status()

    def _get_collection_fields(self, name: str):
        url = f'{self._url_api_collections}/{name}/schema/fields'
        return self._get(url=url)['fields']

    def migrate_collection_fields(self, name: str, fields: List[dict]):
        url = f'{self._url_api_collections}/{name}/schema'
        field_names = [f['name'] for f in self._get_collection_fields(name=name)]

        for data in fields:
            if data['name'] in field_names:
                self._post(url=url, data={'replace-field': data})
            else:
                self._post(url=url, data={'add-field': data})

    def _get_collection_field_types(self, name: str):
        url = f'{self._url_api_collections}/{name}/schema/fieldtypes'
        return self._get(url=url)['fieldTypes']

    def migrate_collection_field_types(self, name: str, field_types: List[dict]):
        url = f'{self._url_api_collections}/{name}/schema'
        field_type_names = [ft['name'] for ft in self._get_collection_field_types(name=name)]

        for data in field_types:
            if data['name'] in field_type_names:
                self._post(url=url, data={'replace-field-type': data})
            else:
                self._post(url=url, data={'add-field-type': data})

    def search(self, query: str, collection: str, params: dict | None = None) -> dict:
        """Main search interface"""
        url = f'{self._url}/solr/{collection}/query'

        if params is None:
            params = dict()

        data = {
            "params": {
                "q": query,
                **params
            }
        }
        response = self._post(url=url, data=data)
        return response['response']

    def delete_document(self, by: str, collection: str, commit: bool = False):
        url = f'{self._url}/solr/{collection}/update'
        if commit:
            url += '?commit=true'

        delete_request = {'delete': {'query': by}}
        self._post(url=url, data=delete_request)