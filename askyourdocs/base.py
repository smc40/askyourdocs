from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from datetime import datetime
from hashlib import sha256
import json
import reprlib
from typing import Any, List

import numpy as np


class Environment:
    def __init__(self, **kwargs):
        # Global arguments
        self.log_level: str | None = kwargs.get('log_level')

        # Services
        self.service: str | None = kwargs.get('service')
        self.storage: str | None = kwargs.get('storage')
        self.modelling: str | None = kwargs.get('modelling')
        self.pipeline: str | None = kwargs.get('pipeline')

        # Tika (Service(s): 'storage')
        self.tika_url: str | None = kwargs.get('tika_url')
        self.filename: str | None = kwargs.get('filename')

        # Solr arguments (Service(s): 'storage')
        self.solr_url: str | None = kwargs.get('solr_url')
        self.zk_urls: str | None = kwargs.get('zk_urls')
        self.collection: str | None = kwargs.get('collection')
        self.query: str | None = kwargs.get('query')
        self.commit: bool | None = kwargs.get('commit')

        # LLM arguments
        self.text: str | None = kwargs.get('text')

        # Frontend URL
        self.frontend_url: str | None = kwargs.get('frontend_url')


class Service(ABC):
    """Parent class for all services."""
    _entity_name = __qualname__  # type: ignore

    def __init__(self, environment: Environment, settings: dict):
        self._environment = environment
        self._settings = settings

    @abstractmethod
    def apply(self, **kwargs) -> Any:
        pass


@dataclass
class Document(ABC):

    id: str

    def __eq__(self, other) -> bool:
        if isinstance(other, Document):
            return self.id == other.id
        return False

    @property
    @abstractmethod
    def _id_prefix(self) -> str:
        pass

    def __post_init__(self):
        """With this method we can use Document(id='this is my identification string') and it turns it into a hash."""
        if not self.id.startswith(self._id_prefix):
            self.id = self._id_prefix + sha256(self.id.encode()).hexdigest()

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(eq=False)
class TextEntity(Document):

    text: str
    index: int | None = None
    doc_id: str | None = None

    @property
    def _id_prefix(self) -> str:
        return 'txt_ent_'


@dataclass(eq=False)
class EmbeddingEntity(Document):

    vector: List[float]
    doc_id: str | None = None
    txt_ent_id: str | None = None

    @property
    def _id_prefix(self) -> str:
        return 'emb_ent_'

    def __post_init__(self):
        super().__post_init__()
        vector = np.array(self.vector)
        self.vector = list(vector / np.linalg.norm(vector))


@dataclass(eq=False)
class SearchDocument(Document):

    name: str
    source: str
    text: str | None

    def __repr__(self):
        cls_name = self.__class__.__name__
        rlib = reprlib.Repr()
        id_repr = rlib.repr(self.id)
        name_repr = rlib.repr(self.name)
        source_repr = rlib.repr(self.source)
        text_repr = rlib.repr(self.text)
        return f'{cls_name}(id={id_repr}, name={name_repr}, source={source_repr}, text={text_repr})'

    @property
    def _id_prefix(self):
        return 'doc_'


class DocumentListEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Document):
            return obj.to_dict()
        if isinstance(obj, np.float32):
            return str(obj)
        if isinstance(obj, np.int64):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


DocumentList = List[Document]
