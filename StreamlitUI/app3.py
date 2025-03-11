import streamlit as st
import pandas as pd
import TalktoSQLAPI  # Import your local Python file
import TalktoFilesAPI  # Import the new module
import TalktofilesRAGAPI
import SQLAgent
from PIL import Image  # Import the Image class from PIL
from pandasai.responses.response_parser import ResponseParser

# Set Streamlit page configuration
st.set_page_config(page_title="💬 AI Chat Assistant", layout="wide")

# Align selection in the top-right corner
st.sidebar.title("Select Data Source")
chat_mode = st.sidebar.radio("Choose an option:", ("Chat with Database", "Chat with Files"))

# Store selection in session state to persist it
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = chat_mode

if chat_mode != st.session_state.chat_mode:
    st.session_state.chat_mode = chat_mode

st.title("💬 Chat with Your Data")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User query input
query = st.chat_input("Ask me a question...")

class StreamlitResponse:  # Modified StreamlitResponse
    def __init__(self, context):
        self.st = context

    def format_dataframe(self, result):
        self.st.dataframe(result)

    def format_plot(self, result):
        self.st.image(result)

    def format_other(self, result):
        self.st.write(result)

def handle_sql_query(query):
    """Handles SQL API query execution."""
    try:
        formatter = StreamlitResponse(st)  # Create formatter instance
        response = SQLAgent.main(query, formatter)  # Pass to SQLAgent
        st.session_state.messages.append({"role": "assistant", "content": response}) # Store the message
    except Exception as e:
        st.error(f"Error in SQL query: {e}")
        st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"}) # Store the error


def handle_file_query(query):
    """Handles File API query execution."""
    try:
        response = TalktofilesRAGAPI.main(query)  # Call File API
        #display_response(response)
        st.write(response)
    except Exception as e:
        st.error(f"Error in File query: {e}")


# Process the user query if provided
if query:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Call the appropriate function based on chat mode
    if st.session_state.chat_mode == "Chat with Database":
        handle_sql_query(query)
    elif st.session_state.chat_mode == "Chat with Files":
        handle_file_query(query)
    else:
        st.error("Please select a chat mode before asking a question.")
