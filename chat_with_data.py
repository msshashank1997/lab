
from promptflow import tool
from promptflow.connections import AzureOpenAIConnection, CognitiveSearchConnection
import os
import openai
import dotenv

@tool
def my_python_tool(question: str, history: str, deployment: str, search_index : str, ai_connection : AzureOpenAIConnection = None, search_connection : CognitiveSearchConnection = None) -> str:
    dotenv.load_dotenv()

    if ai_connection is None:
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    else:
        endpoint = ai_connection.api_base
        api_key = ai_connection.api_key
    
    if search_connection is None:
        search_endpoint = os.environ.get("AZURE_AI_SEARCH_ENDPOINT")
        search_api_key = os.environ.get("AZURE_AI_SEARCH_API_KEY")
    else:
        search_endpoint = search_connection.api_base
        search_api_key = search_connection.api_key



    client = openai.AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-02-01",
    )

    message = f"Please add the full filename as reference behind the hotel name.\nEither use nice written text with structured paragraphs or use lists and sublist.\n\nQuestion: {question}\nChat History: {history}"

    completion = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "user",
                "content": message,
            },
        ],
        extra_body={
            "data_sources":[
                {
                    "type": "azure_search",
                    "parameters": {
                        "endpoint": search_endpoint,
                        "index_name": search_index,
                        "authentication": {
                            "type": "api_key",
                            "key": search_api_key,
                        }
                    }
                }
            ],
        }
    )

    return completion.choices[0].message.content