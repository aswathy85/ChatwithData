import streamlit as st
import pandas as pd
import TalktoSQLAPI  # Import your local Python file
import TalktoFilesAPI  # Import the new module
import TalktofilesRAGAPI

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

def write_response(response: dict):
    """Displays the response based on its type: text, table, or charts."""
    if "answer" in response:
        st.markdown(response["answer"])

    if "bar" in response:
        df = pd.DataFrame(response["bar"])
        df.set_index("columns", inplace=True)
        st.bar_chart(df)

    if "line" in response:
        df = pd.DataFrame(response["line"])
        df.set_index("columns", inplace=True)
        st.line_chart(df)

    if "table" in response:
        data = response["table"]
        df = pd.DataFrame(data["data"], columns=data["columns"])
        st.table(df)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User query input
query = st.chat_input("Ask me a question...")

def handle_sql_query(query):
    """Handles SQL API query execution."""
    # Call the function from TalktoSQLAPI.py
    try:
        # Get the response from TalktoSQLAPI.main(), assuming it returns a dictionary or list
        response = TalktoSQLAPI.main(query)

        # Debugging: Check if response is a dictionary or list and print
        st.write(response['output'])

        # Assuming response is a dictionary or list (not a string)
        if isinstance(response, (dict, list)):  # check if it's a dict or list
            with st.chat_message("assistant"):
                write_response(response['output'])  # Process the response
                st.session_state.messages.append({"role": "assistant", "content": response['output']})
        else:
            st.error("The response is not in the expected format. Ensure it's a dictionary or list.")

    except Exception as e:
        st.error(f"Error: {e}")

def handle_file_query(query):
    """Handles File API query execution."""
    try:
        response = TalktofilesRAGAPI.main(query)
        if response:
            with st.chat_message("assistant"):
                write_response(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            st.error("The response format is invalid.")
    except Exception as e:
        st.error(f"Error in File query: {e}")

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
