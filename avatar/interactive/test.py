import dotenv
import openai
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from ingest import generate_embeddings

config = dotenv.dotenv_values()

openai.api_type = "azure"
openai.api_key = config["AZURE_OPENAI_API_KEY"]
openai.api_base = config["AZURE_OPENAI_ENDPOINT"]
openai.api_version = config["AZURE_OPENAI_API_VERSION"]

search_client = SearchClient(
    endpoint=config["AZURE_SEARCH_ENDPOINT"],
    index_name=config["AZURE_SEARCH_INDEX"],
    credential=AzureKeyCredential(config["AZURE_SEARCH_API_KEY"]),
)


query = "Wat moet ik doen om eerder met pensioen te gaan?"
results = search_client.search(
    search_text=None,
    vector=generate_embeddings(query),
    top_k=3,
    vector_fields="question_vector, answer_vector, keywords_vector",
    select=["question", "answer", "keywords"],
)

for result in results:
    print(result)
