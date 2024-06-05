import json
import logging
from uuid import uuid4

import dotenv
import openai
import search_index
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from tenacity import retry, stop_after_attempt, wait_random_exponential

logging.getLogger("urllib3").setLevel(logging.ERROR)

config = dotenv.dotenv_values()

openai.api_type = "azure"
openai.api_key = config["AZURE_OPENAI_API_KEY"]
openai.api_base = config["AZURE_OPENAI_ENDPOINT"]
openai.api_version = config["AZURE_OPENAI_API_VERSION"]


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def generate_embeddings(
    text: str,
    engine: str = "text-embedding-ada-002",
) -> list[float]:
    response = openai.Embedding.create(input=text, engine=engine)
    embeddings = response["data"][0]["embedding"]
    return embeddings


if __name__ == "__main__":

    index_client = SearchIndexClient(
        endpoint=config["AZURE_SEARCH_ENDPOINT"],
        credential=AzureKeyCredential(config["AZURE_SEARCH_API_KEY"]),
    )
    search_index.delete(index_client, config["AZURE_SEARCH_INDEX"])
    search_index.create(index_client, config["AZURE_SEARCH_INDEX"])

    search_client = SearchClient(
        endpoint=config["AZURE_SEARCH_ENDPOINT"],
        index_name=config["AZURE_SEARCH_INDEX"],
        credential=AzureKeyCredential(config["AZURE_SEARCH_API_KEY"]),
    )

    def generate_document_vectors(document: dict[str, str]) -> dict:
        return {
            "id": uuid4().hex,
            "question": document["question"],
            "answer": document["answer"],
            "keywords": document["keywords"],
            "question_vector": generate_embeddings(document["question"]),
            "answer_vector": generate_embeddings(document["answer"]),
            "keywords_vector": generate_embeddings(document["keywords"]),
        }

    with open("data/pggm_QnA.ndjson", "r", encoding="utf8") as fh:
        documents = [
            generate_document_vectors(json.loads(line)) for line in fh.readlines()
        ]

    with open("data/pggm_QnA_vectors.ndjson", "w", encoding="utf8") as outf:
        for doc in documents:
            outf.write(f"{json.dumps(doc)}\n")

    result = search_client.upload_documents(documents)

    n = search_client.get_document_count()
    print(f"Indexed {n} documents.")
