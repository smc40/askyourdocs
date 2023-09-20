from pathlib import Path

_root_path = Path(__file__).parents[1]

MODEL_NAME = "google/flan-t5-base"
MODEL_EMBEDDING_DIMENSION = 768
MODEL_NTOKENS = 512

DOCS_COLLECTION = 'ayd_docs'
TEXTS_COLLECTION = 'ayd_texts'
VECS_COLLECTION = 'ayd_vecs'

SETTINGS = {
    # Generic Settings
    'paths': {
        'root': _root_path,
        'models': _root_path / 'models',
    },

    # Solr Settings
    "solr": {
        'nshards': 1,
        'datetime_format': "%Y-%m-%dT%H:%M:%S.%fZ",
        'top_k': 5,
        'collections': {
            'map': {
                'docs': DOCS_COLLECTION,
                'texts': TEXTS_COLLECTION,
                'vecs': VECS_COLLECTION,
            },
            DOCS_COLLECTION: {
                'config_files': 'resources/solr/conf',
                'fields': [
                    {
                        'name': 'name',
                        'type': 'string',
                        'indexed': 'false',
                        'stored': 'false',
                        'multiValued': 'false'
                    },
                    {
                        'name': 'source',
                        'type': 'string',
                        'indexed': 'false',
                        'stored': 'false',
                        'multiValued': 'false'
                    },
                    {
                        'name': 'text',
                        'type': 'text_general',
                        'indexed': 'false',
                        'stored': 'true',
                        'multiValued': 'false'
                    },
                ]
            },
            TEXTS_COLLECTION: {
                'config_files': 'resources/solr/conf',
                'fields': [
                    {
                        'name': 'text',
                        'type': 'text_general',
                        'indexed': 'true',
                        'stored': 'true',
                        'multiValued': 'false'
                    },
                    {
                        'name': 'index',
                        'type': 'pint',
                        'indexed': 'false',
                        'stored': 'true',
                        'multiValued': 'false'
                    },
                    {
                        'name': 'doc_id',
                        'type': 'string',
                        'indexed': 'false',
                        'stored': 'true',
                        'multiValued': 'false'
                    },
                ],
            },
            VECS_COLLECTION: {
                'config_files': 'resources/solr/conf',
                'fields': [
                    {
                        'name': 'vector',
                        'type': 'knn_vector',
                        'indexed': 'true',
                        'stored': 'true',
                    },
                    {
                        'name': 'doc_id',
                        'type': 'string',
                        'indexed': 'false',
                        'stored': 'true',
                    },
                    {
                        'name': 'txt_ent_id',
                        'type': 'string',
                        'indexed': 'false',
                        'stored': 'true',
                    },
                ],
                'field_types': [
                    {
                        'name': 'knn_vector',
                        'class': 'solr.DenseVectorField',
                        'vectorDimension': MODEL_EMBEDDING_DIMENSION,
                        'similarityFunction': 'dot_product'
                    },
                ],
            },
            'test_origin': {
                'config_files': 'tests/data/storage/config/test_origin'
            },
        }
    },

    # Modeling
    'modeling': {
        'model_name': MODEL_NAME,
        'embedding_dimension': MODEL_EMBEDDING_DIMENSION,
        'tokenizer_package': 'punkt',
        'ntok_max': MODEL_NTOKENS,
    },

    # Frontend
    'shiny_app': {
        'debug_mode': True,
    },
}
