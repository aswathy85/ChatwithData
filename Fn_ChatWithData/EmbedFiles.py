# Install required packages
# pip install PyMuPDF pdf2image pytesseract pandas azure-storage-blob langchain-openai langchain-text-splitters langchain-postgres
import os
import json
import fitz  # PyMuPDF for PDFs
import pytesseract  # OCR for scanned PDFs
import pandas as pd  # For CSV handling
from pdf2image import convert_from_bytes  # Convert PDF pages to images
from docx import Document  # For Word documents
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from langchain_text_splitters import TokenTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector

# Load environment variables
load_dotenv()

# Azure Configurations
AZURE_BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
AZURE_BLOB_CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER_NAME")
AZURE_PROCESSED_FOLDER = os.getenv("AZURE_PROCESSED_FOLDER", "processed")

# OpenAI and PostgreSQL Configurations
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_EMBEDDING_MODEL = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")

PG_CONFIG = {
    "dbname": os.getenv("PG_DBNAME"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "host": os.getenv("PG_HOST"),
    "port": os.getenv("PG_PORT", "5432"),
}

collection_name = os.getenv("PG_COLLECTION_NAME", "chatwithdatafiles")
connectionstring = f"postgresql://{PG_CONFIG['user']}:{PG_CONFIG['password']}@{PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['dbname']}"

# Initialize Clients
blob_service_client = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_BLOB_CONTAINER_NAME)
processed_blobs = {blob.name for blob in container_client.list_blobs(name_starts_with=AZURE_PROCESSED_FOLDER)}

embeddings = AzureOpenAIEmbeddings(
    model=AZURE_OPENAI_EMBEDDING_MODEL,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY
)

text_splitter = TokenTextSplitter(model_name=AZURE_OPENAI_EMBEDDING_MODEL)

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connectionstring,
    use_jsonb=True
)
vector_store.create_tables_if_not_exists()
vector_store.create_collection()

# File Processing Functions
def extract_text_from_pdf(pdf_data):
    text = ""
    try:
        with fitz.open(stream=pdf_data, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except:
        images = convert_from_bytes(pdf_data)
        text = "\n".join([pytesseract.image_to_string(img) for img in images])
    return text

def extract_text_from_docx(docx_data):
    return "\n".join([p.text for p in Document(docx_data).paragraphs])

def extract_text_from_txt(txt_data):
    return txt_data.decode("utf-8", errors="ignore")

def extract_text_from_json(json_data):
    return json.dumps(json.loads(json_data.decode("utf-8", errors="ignore")), indent=2)

def extract_text_from_csv(csv_data):
    df = pd.read_csv(pd.compat.StringIO(csv_data.decode("utf-8", errors="ignore")))
    return df.to_csv(index=False)

# Processing Pipeline
for blob in container_client.list_blobs():
    blob_name = blob.name
    
    # Skip files inside the processed folder
    if blob_name.startswith(f"{AZURE_PROCESSED_FOLDER}/"):
        continue
    
    print(f"Processing file: {blob_name}")
    blob_client = container_client.get_blob_client(blob_name)
    file_data = blob_client.download_blob().readall()
    
    if blob_name.lower().endswith(".pdf"):
        file_contents = extract_text_from_pdf(file_data)
    elif blob_name.lower().endswith(".docx"):
        file_contents = extract_text_from_docx(file_data)
    elif blob_name.lower().endswith(".txt"):
        file_contents = extract_text_from_txt(file_data)
    elif blob_name.lower().endswith(".json"):
        file_contents = extract_text_from_json(file_data)
    elif blob_name.lower().endswith(".csv"):
        file_contents = extract_text_from_csv(file_data)
    else:
        print(f"Skipping {blob_name}: Unsupported file type.")
        continue
    
    if not file_contents.strip():
        print(f"Skipping {blob_name}: No extractable text found.")
        continue
    
    texts = text_splitter.split_text(file_contents)
    docs = text_splitter.create_documents(texts)
    for idx, doc in enumerate(docs):
        doc.metadata = {"id": f"{blob_name}_{idx}", "file_name": blob_name}
    
    vector_store.add_documents(docs, ids=[doc.metadata["id"] for doc in docs])
    
    # Move file to processed folder
    destination_blob_name = f"{AZURE_PROCESSED_FOLDER}/{blob_name}"
    container_client.get_blob_client(destination_blob_name).upload_blob(file_data, overwrite=True)
    blob_client.delete_blob()
    print(f"Moved {blob_name} to {destination_blob_name}")

print("Processing complete.")
