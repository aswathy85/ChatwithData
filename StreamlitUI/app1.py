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

def display_response(response):
    """Handles different response types and renders them in Streamlit."""
    if isinstance(response, dict):
        with st.chat_message("assistant"):
            if "type" in response and "value" in response:
                if response["type"] == "number":
                    st.markdown(f"**Result:** `{response['value']}`")
                elif response["type"] == "text":
                    st.markdown(response["value"])
                elif response["type"] == "table":
                    df = pd.DataFrame(response["value"]["data"], columns=response["value"]["columns"])
                    st.table(df)
                elif response["type"] == "bar":
                    df = pd.DataFrame(response["value"])
                    df.set_index("columns", inplace=True)
                    st.bar_chart(df)
                elif response["type"] == "line":
                    df = pd.DataFrame(response["value"])
                    df.set_index("columns", inplace=True)
                    st.line_chart(df)
                elif response["type"] == "plot":
                    """plot_path = response["value"]  # Get image file path                   
                    image = Image.open(plot_path)  # Open image
                    st.image(image, caption="Generated Chart", use_column_width=True)  # Display image in Streamlit
                    """
                    st.markdown("test" )
            else:
                st.write(response)  # Default dict response display
        st.session_state.messages.append({"role": "assistant", "content": str(response)})

    elif isinstance(response, list):
        with st.chat_message("assistant"):
            for item in response:
                if isinstance(item, dict):
                    display_response(item)  # Handle dictionaries inside lists
                else:
                    st.markdown(f"**{item}**")  # Show list items as text
        st.session_state.messages.append({"role": "assistant", "content": str(response)})

    elif isinstance(response, pd.DataFrame):
        with st.chat_message("assistant"):
            st.write("📊 **Data Table:**")
            st.dataframe(response)  # Display DataFrame as an interactive table
        st.session_state.messages.append({"role": "assistant", "content": response.to_json()})

    elif isinstance(response, str):
        with st.chat_message("assistant"):
            st.markdown(response)  # Display plain text
        st.session_state.messages.append({"role": "assistant", "content": response})

    elif isinstance(response, (int, float)):
        with st.chat_message("assistant"):
            st.markdown(f"**Result:** `{response}`")  # Display numerical values
        st.session_state.messages.append({"role": "assistant", "content": str(response)})
    

    else:
        st.error("⚠️ The response is not in an expected format. Please check the API output.")


def handle_sql_query(query):
    """Handles SQL API query execution."""
    try:
        df=SQLAgent.main(query)
        response=df.chat(query)
        #response = SQLAgent.main(query)  # Call SQL API
        #display_response(response)
    except Exception as e:
        st.error(f"Error in SQL query: {e}")


def handle_file_query(query):
    """Handles File API query execution."""
    try:
        response = TalktofilesRAGAPI.main(query)  # Call File API
        display_response(response)
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
