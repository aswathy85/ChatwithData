import os
from langchain_openai import AzureChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_postgres.vectorstores import PGVector
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Load Environment Variables
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_EMBEDDING_MODEL = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")
AZURE_OPEN_AI_CHAT_MODEL = os.getenv("AZURE_OPEN_AI_CHAT_MODEL")
api_version=os.getenv("AZURE_OPEN_AI_API_VERSION")
# Azure PostgreSQL Configurations
PG_CONFIG = {
    "dbname": os.getenv("PG_DBNAME"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "host": os.getenv("PG_HOST"),
    "port": os.getenv("PG_PORT", "5432"),
}

collection_name = os.getenv("PG_COLLECTION_NAME", "chatwithdatafiless")
connectionstring = f"postgresql://{PG_CONFIG['user']}:{PG_CONFIG['password']}@{PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['dbname']}"

# Initialize the OpenAI language model for response generation
llm = AzureChatOpenAI(deployment_name=AZURE_OPEN_AI_CHAT_MODEL,azure_endpoint=AZURE_OPENAI_ENDPOINT,api_key=AZURE_OPENAI_KEY,api_version=api_version)

# Initialize the embedding function
embeddings = AzureOpenAIEmbeddings(model="text-embedding-ada-002",azure_endpoint=AZURE_OPENAI_ENDPOINT)

vectorstore = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connectionstring,
    use_jsonb=True,
)

# Define the prompt template for generating AI responses
PROMPT_TEMPLATE = """
You are an AI assistant designed to provide complete and detailed responses based on the given context.
Please return the full contract details without summarizing or omitting any sections.
If the query is about State Contract Number or Master Agreement Number, consider both as the same.
<context>
{context}
</context>

<question>
{question}
</question>

"""

prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["context", "question"])
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

def format_docs(docs,max_length=6000):
    """Formats retrieved documents but limits token length."""
    formatted = "\n\n".join(doc.page_content[:max_length] for doc in docs)
    #print(formatted)
    return formatted if formatted else "No relevant context found."

# Define the RAG (Retrieval-Augmented Generation) chain
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
# Function to handle API requests
def main(question):
    """Retrieves relevant documents and generates an AI response."""
    try:
        #docs = vectorstore.similarity_search(question,search_type="mmr",  k=3,search_kwargs={"fetch_k": 10})
        docs = vectorstore.similarity_search("agreement", k=5)
          # If no relevant docs found, return a fallback response
        if not docs:
            print(" No relevant documents found in PGVector.")
        #if not docs:
           # return "I couldn't find relevant information in the provided database."       
       
        # Generate response using the RAG pipeline
        response = rag_chain.invoke(question)
        #response = rag_chain.invoke({"context": format_docs(docs), "question": question})
        return response
    
    except Exception as e:
        return f"Error: {str(e)}"  
 

if __name__ == "__main__":
    test_param = "How many Many master Agreements are there?"
    result = main(test_param)
    print(result)


