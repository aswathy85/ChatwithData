import os
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv(".env")

def main():
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPEN_AI_CHAT_MODEL")
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version=os.getenv("AZURE_OPEN_AI_API_VERSION","2024-05-01-preview")
    llm = AzureChatOpenAI(temperature=0,deployment_name=deployment,azure_endpoint=endpoint,api_key=subscription_key,api_version=api_version)
    return llm
"""
if __name__ == "__main__":
     resultdf = main()
     print(resultdf)
     """