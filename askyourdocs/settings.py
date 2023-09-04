from pathlib import Path

_root_path = Path(__file__).parents[1]

MODEL_NAME = "google/flan-t5-small"
MODEL_EMBEDDING_DIMENSION = 512

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
        'collections': {
            'ayd_search': {
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
                        'indexed': 'true',
                        'stored': 'false',
                        'multiValued': 'false'
                    },
                ]
            },
            'ayd_vector': {
                'config_files': 'resources/solr/conf',
                'fields': [
                    {
                        'name': 'vector',
                        'type': 'knn_vector',
                        'indexed': 'true',
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

    # Data
    'data': {
        'default_document': 'docs/20211203_SwissPAR_Spikevax_single_page_text.pdf'
    },


    # Modeling
    'modeling': {
        'model_name': MODEL_NAME,
        'tokenizer_package': 'punkt',
        'chunk_size': 200,
        'overlap': 10,
    },

    # Frontend
    'shiny_app': {
        'debug_mode': True,
    },
}
