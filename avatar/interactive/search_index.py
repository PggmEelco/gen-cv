from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    PrioritizedFields,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticSettings,
    SimpleField,
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
)


def delete(index_client: SearchIndexClient, index_name: str):
    index_client.delete_index(index_name)


def create(index_client: SearchIndexClient, index_name: str):

    vector_search = VectorSearch(
        algorithm_configurations=[
            VectorSearchAlgorithmConfiguration(
                name="my-vector-config",
                kind="hnsw",
                hnsw_parameters={
                    "m": 4,
                    "efConstruction": 400,
                    "efSearch": 500,
                    "metric": "cosine",
                },
            )
        ]
    )

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="keywords", type=SearchFieldDataType.String),
        SearchableField(name="question", type=SearchFieldDataType.String),
        SearchableField(name="answer", type=SearchFieldDataType.String),
        SearchField(
            name="keywords_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_configuration="my-vector-config",
        ),
        SearchField(
            name="question_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_configuration="my-vector-config",
        ),
        SearchField(
            name="answer_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_configuration="my-vector-config",
        ),
    ]

    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=PrioritizedFields(
            title_field=None,
            prioritized_keywords_fields=[SemanticField(field_name="keywords")],
            prioritized_content_fields=[
                SemanticField(field_name="question"),
                SemanticField(field_name="answer"),
            ],
        ),
    )

    semantic_settings = SemanticSettings(configurations=[semantic_config])

    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search,
        semantic_settings=semantic_settings,
    )
    result = index_client.create_or_update_index(index)

    return result
