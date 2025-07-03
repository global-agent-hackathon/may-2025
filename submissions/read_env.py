import os
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT')
AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT')
OPENAI_API_VERSION = os.getenv('OPENAI_API_VERSION')
LLM_MODEL_TYPE ='AZUREOPENAI'

if LLM_MODEL_TYPE == 'AZUREOPENAI' :
    LLM_MODEL_GPT3 = AzureChatOpenAI(
        azure_deployment="XXXXXXX",
    )

    LLM_MODEL_GPT3_16k = AzureChatOpenAI(
        azure_deployment="XXXXXXX",
    )

    
    LLM_MODEL_GPT4 = AzureChatOpenAI(
        azure_deployment="XXXXXXX",
    )

    LLM_MODEL_GPT4O =AzureChatOpenAI(
        azure_deployment="XXXXXXX",
    )

    LLM_MODEL_GPT4O_MINI =AzureChatOpenAI(
        azure_deployment="XXXXXXX",
    )

    EMBEDDINGS_MODEL = AzureOpenAIEmbeddings(
            azure_deployment="XXXXXXX")

