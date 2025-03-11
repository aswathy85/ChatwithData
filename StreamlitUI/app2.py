import os
import streamlit as st
from pandasai import SmartDataframe
#from pandasai import BaseCallback
from pandasai.llm.azure_openai import AzureOpenAI
from pandasai.responses.response_parser import ResponseParser
import pandas as pd
from dotenv import load_dotenv
import pyodbc
import sqlalchemy as sa

load_dotenv(".env")

# Load database credentials from .env file
server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_DATABASE")
username = os.getenv("SQL_USERNAME")
password = os.getenv("SQL_PASSWORD")
driver = "{ODBC Driver 17 for SQL Server}"  # Ensure this driver is installed
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPEN_AI_CHAT_MODEL")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version=os.getenv("AZURE_OPEN_AI_API_VERSION","2024-05-01-preview")

# Connect to Azure SQL Database
conn_string = f"DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}"

"""
class StreamlitCallback(BaseCallback):
    def __init__(self, container) -> None:
        
        self.container = container

    def on_code(self, response: str):
        self.container.code(response)
"""

class StreamlitResponse(ResponseParser):
    def __init__(self, context) -> None:
        super().__init__(context)

    def format_dataframe(self, result):
        st.dataframe(result["value"])
        return

    def format_plot(self, result):
        st.image(result["value"])
        return

    def format_other(self, result):
        st.write(result["value"])
        return


st.write("# Chat with Credit Card Fraud Dataset 🦙")
conn = sa.conn.connect(conn_string)
query = "SELECT *  FROM [dbo].[FinancialData]"
df = pd.read_sql(query, conn)
conn.close()

with st.expander("🔎 Dataframe Preview"):
    st.write(df.tail(3))

query = st.text_area("🗣️ Chat with Dataframe")
container = st.container()

if query:
    llm = AzureOpenAI(temperature=0.7,deployment_name=deployment,azure_endpoint=endpoint,api_key=subscription_key,api_version=api_version)
    query_engine = SmartDataframe(
        df,
        config={
            "llm": llm,
            "response_parser": StreamlitResponse,
           
        },
    )

    answer = query_engine.chat(query)