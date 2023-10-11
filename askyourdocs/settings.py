from pathlib import Path

_root_path = Path(__file__).parents[1]

MODEL_NAME = "google/flan-t5-base"
MODEL_EMBEDDING_DIMENSION = 768
MODEL_NTOKENS = 512

DOCS_COLLECTION = 'ayd_docs'
TEXTS_COLLECTION = 'ayd_texts'
VECS_COLLECTION = 'ayd_vecs'
FEEDBACK_COLLECTION = 'ayd_feedback'

SETTINGS = {
    # Generic Settings
    'paths': {
        'root': _root_path,
        'models': _root_path / 'models',
    },
    'cors_origins': ['http://localhost:3000', 'http://ayd-frontend-1:3000'],

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
                'feedback': FEEDBACK_COLLECTION,
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
            FEEDBACK_COLLECTION: {
                'config_files': 'resources/solr/conf',
                'fields': [
                    {
                        'name': 'feedback_type',
                        'type': 'string',
                        'indexed': 'false',
                        'stored': 'true',
                        'multiValued': 'false'
                    },
                    {
                        'name': 'text',
                        'type': 'string',
                        'indexed': 'false',
                        'stored': 'true',
                        'multiValued': 'false'
                    },
                    {
                        'name': 'feedback_to',
                        'type': 'string',
                        'indexed': 'false',
                        'stored': 'true',
                        'multiValued': 'false'
                    },
                ]
            },
            'test_origin': {
                'config_files': 'tests/data/storage/config/test_origin'
            },
        }
    },

    # Modeling
    'modelling': {
        'model_name': MODEL_NAME,
        'embedding_dimension': MODEL_EMBEDDING_DIMENSION,
        'tokenizer_package': 'punkt',
        'ntok_max': MODEL_NTOKENS,
        'no_repeat_ngram_size': 4,
        'ntok_context_fraction': 0.8,
    },

    # Frontend
    'shiny_app': {
        'debug_mode': True,
    },
}
