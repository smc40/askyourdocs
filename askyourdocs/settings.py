from pathlib import Path
import os

_root_path = Path(__file__).parents[1]

MODEL_NAME = "gpt-35-turbo"  #"google/flan-t5-small"
EMBEDDING_MODEL_NAME = "text-embedding-ada-002"
MODEL_EMBEDDING_DIMENSION = 1536 if 'gpt-' in MODEL_NAME else 512 # 1024 #512 #to find out, load the HF model and print the model in a console. look for the 'in_feature' variable
MODEL_NTOKENS = 1024 if 'gpt-' in MODEL_NAME else 512   # this is half the input size of the model 2048 is max token with prompt + answer

DOCS_COLLECTION = 'ayd_docs'
TEXTS_COLLECTION = 'ayd_texts'
VECS_COLLECTION = 'ayd_vecs'
FEEDBACK_COLLECTION = 'ayd_feedback'

CORS_ALLOWED_STR = os.getenv('CORS_ALLOWED', 'http://localhost:8000,http://localhost:3000')
CORS_ALLOWED_LIST = CORS_ALLOWED_STR.split(',')

SETTINGS = {
    # Generic Settings
    'paths': {
        'root': _root_path,
        'models': _root_path / 'models',
    },
    'cors_origins': CORS_ALLOWED_LIST,

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
                    {
                        'name': 'email',
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
        'embedding_model_name': EMBEDDING_MODEL_NAME,
        'embedding_dimension': MODEL_EMBEDDING_DIMENSION,
        'tokenizer_package': 'punkt',
        'ntok_max': MODEL_NTOKENS,
        'no_repeat_ngram_size': 4,
        'ntok_context_fraction': 0.5,
    },

    # Frontend
    'app': {
        'keycloak_url': os.environ.get('KEYCLOAK_URL', "http://keycloak:8080/"),
        'keycloak_realm':'ayd',
        'keycloak_client_id':'ayd-backend',
        'keycloak_client_secret':os.environ.get('BACKEND_KEYCLOAK_SECRET','bQwuuesYTIfcJmOxI4t4fltV48OQsAQq'),
    },
}
