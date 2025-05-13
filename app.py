import streamlit as st
import pandas as pd
from datetime import datetime

# Importing Agents
from TalktofilesRAGAPI import main as TalktofilesRAGAPI
#from Agents.PandasAIAgent import main as PandasAIAgent
from Langchain_SQLAgent import main as LSQLAgent
#from Agents.PandasDataframeAgent import main as PandasDataframeAgent
from CreatePandasDataframe import main as CreatePandasDataframe

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

# Initialize separate chat histories for each mode
if "db_messages" not in st.session_state:
    st.session_state.db_messages = []
if "file_messages" not in st.session_state:
    st.session_state.file_messages = []
if "charts" not in st.session_state:
    st.session_state.charts = []

# Contextual Details
if st.session_state.chat_mode == "Chat with Database":
    st.markdown("Gain insights from your financial data by chatting with it.")
    #database_option = st.sidebar.radio("Select Database Agent:", ("Langchain SQL Toolkit", "PandasAI", "Langchain Pandas Framework"))
    database_option = "Langchain SQL Toolkit"
    st.session_state.database_option = database_option
    messages = st.session_state.db_messages  # Use database chat history
    try:
        df = CreatePandasDataframe()
        if isinstance(df, pd.DataFrame):
            with st.expander("🔍 View Data", expanded=False):
                st.dataframe(df)
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", csv, f"data_{timestamp}.csv", "text/csv")
        else:
            st.error("Error: Returned object is not a DataFrame.")
    except Exception as e:
        st.error(f"Error loading data: {e}")

elif st.session_state.chat_mode == "Chat with Files":
    st.markdown("Easily ask questions about your financial documents stored in Azure Blob Storage.")
    messages = st.session_state.file_messages  # Use file chat history


# Display chat history
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
# Display charts (ONLY in "Chat with Database" mode)
if st.session_state.chat_mode == "Chat with Database":
    for chart_data in st.session_state.charts:
        
        if chart_data["type"] == "bar_chart":
            try:
                df = pd.DataFrame(chart_data["content"])
                st.bar_chart(df, width=500, height=300, use_container_width=False)
            except Exception as e:
                st.error(f"Error displaying bar chart: {e}")
        elif chart_data["type"] == "line_chart":
            try:
                df = pd.DataFrame(chart_data["content"])
                #st.line_chart(df.set_index(df.columns[0]))
                st.line_chart(df, width=500, height=300, use_container_width=False)
            except Exception as e:
                st.error(f"Error displaying line chart: {e}")
        elif chart_data["type"] == "area_chart":
            try:
                df = pd.DataFrame(chart_data["content"])
                #st.line_chart(df.set_index(df.columns[0]))
                st.line_chart(df, width=500, height=300, use_container_width=False)
            except Exception as e:
                st.error(f"Error displaying line chart: {e}")
        elif chart_data["type"] == "table":
            try:
                df = pd.DataFrame(chart_data["content"]["rows"], columns=chart_data["content"]['headers'])
                st.table(df)
            except Exception as e:
                st.error(f"Error displaying table: {e}")


def write_answer(response_dict: dict):
    """
    Write a response from an agent to a Streamlit app.

    Args:
        response_dict: The response from the agent.

    Returns:
        None.
    """

    # Check if the response is an answer.
    if "answer" in response_dict:
        #st.write(response_dict["answer"])
        response_text = response_dict["answer"]
        with st.chat_message("assistant"):
            st.markdown(response_text)
        # Append to the correct session state based on chat mode      
        messages.append({"role": "assistant", "content": response_text})
    
    # Check if the response is a bar chart.
    for chart_type in ["bar", "line","area"]:
        if chart_type in response_dict:
            data = response_dict[chart_type]
            width=500
            height=300
            df_data = {col: [x[i] for x in data['data']] for i, col in enumerate(data['columns'])}
            df = pd.DataFrame(df_data)
            if not df.empty:
                df_chart = df.set_index(df.columns[0])
                if chart_type == "bar":
                    st.bar_chart(df_chart, width=width, height=height, use_container_width=False)
                else:
                    st.line_chart(df_chart, width=width, height=height, use_container_width=False)
                st.session_state.charts.append({"role": "assistant","type": f"{chart_type}_chart", "width": width, "height": height, "content": df_chart.to_dict()})
            else:
                st.error("No data to display.")
    # Check if the response is a table.
    if "table" in response_dict:
        data = response_dict["table"]
        df = pd.DataFrame(data["rows"], columns=data['headers'])
        st.table(df)
        st.session_state.charts.append({"role": "assistant","type": "table", "content": data})

def handle_sql_query(query):    
    """Executes the query using the selected database agent."""
    try:
        if st.session_state.database_option == "Langchain SQL Toolkit":
            response_dict = LSQLAgent(query)
        #elif st.session_state.database_option == "PandasAI":
         #   response_dict = PandasAIAgent(query)
        #elif st.session_state.database_option == "Langchain Pandas Framework":
         #   response_dict = PandasDataframeAgent(query)
        else:
            st.error("Invalid database selection.")
            return

        write_answer(response_dict)

    except Exception as e:
        #st.error(f"Error in SQL query: {e}")
         messages.append({"role": "assistant", "content": {e}})  # Store response
     

def handle_file_query(query):
    """Handles File API query execution."""
    try:
        response = TalktofilesRAGAPI(query)  # Call File API
        messages.append({"role": "assistant", "content": response})  # Store response
        with st.chat_message("assistant"):
            st.markdown(response)
    except Exception as e:
        st.error(f"Error in File query: {e}")

# Process User Query
query = st.chat_input("Ask me a question...")

# Process User Query
if query:
    messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
    if st.session_state.chat_mode == "Chat with Database":
        handle_sql_query(query)
    elif st.session_state.chat_mode == "Chat with Files":
        handle_file_query(query)
    else:
        st.error("Please select a chat mode before asking a question.")
