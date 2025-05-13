#pip install langchain_experimental
#pip install tabulate
import os
import pyodbc
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
#from langchain.prompts import PromptTemplate        
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from LLMChatAgent import main as llm_main
#from CreatePandasDataframe import main as pdf_main


parser = JsonOutputParser()

def ask_agent(agent, query):
    """
    Query an agent and return the response as a string.

    Args:
        agent: The agent to query.
        query: The query to ask the agent.

    Returns:
        The response from the agent as a string.
    """
    # Prepare the prompt with query guidelines and formatting
    prompt = """\
Write a SQL Server query in T-SQL format. Do not use backticks (`). Use square brackets ([ ]) for table and column names.
The final output should always be a JSON.
The structure of the responses depend on the type of information requested in the query.
Given the following financial data, analyze trends, compare metrics, and generate insights based on revenue, expenses, and profitability. Answer the following questions:" 
**Data:**
Vertical	Account	Year	Month	Revenue	Resource Cost	Direct Expense	Sales Expense	G&A Expense	EBITDA With Forex	Gross Margin with forex
Insurance	Ins3MAccount	2024	September	17107.91	11620.69	4.76	0	394.5	5087.96	5482.46
### **Financial Data Context**
Analyze revenue trends, cost impact, and profitability insights. When analyzing revenue trends, compare changes across multiple years and highlight key reasons behind revenue increases or decreases. Consider major cost components such as Resource Cost, Direct Expense, Sales Expense, and G&A Expense.
### **Analysis Approach**
- First, sum the total revenue for each year to avoid excessive token usage.
- Then, compare trends between years to identify revenue increases or decreases.
- Highlight the key reasons behind revenue changes (e.g., resource costs, sales expenses).
- **Revenue, Costs, and Financial Figures** should be formatted for better readability **only in plain text answers, not in charts or tables**:
  - **Thousands (K)** → Example: `150,000` should be `150K`
  - **Millions (M)** → Example: `3,200,000` should be `3.2M`
  - **Billions (B)** → Example: `5,600,000,000` should be `5.6B`
- **If the response includes a chart or table, retain the original numerical values without formatting** to ensure accurate visualization.
**Example Analysis Tasks**  
1. Show revenue growth trends over the past 4 years.  
2. Identify the major reasons for revenue drops or hikes over this period.  
3. Compare EBITDA changes due to resource cost variations.  
4. Calculate the percentage impact of each cost category on overall revenue.  
5. Predict revenue trends for next year based on historical data.
### **Formatting Guidelines:**
- **If percentages are mentioned**, use up to **two decimal places** (e.g., `4.25%`).
- **Provide insights in simple, easy-to-read sentences.**
- **Ensure proper spacing between sentences for readability and keep same font type.**
### **Response Formatting Guidelines**
1. If the query requires a table, format your answer like this:
    {"table": {"headers": ["column1", "column2", ...], "rows": [[value1, value2, ...], [value1, value2, ...], ...]}}

2. For a bar chart, respond like this:
    {"bar": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

3. If a line chart is more appropriate, your reply should look like this:
    {"line": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

Note: We only accommodate two types of charts: "bar" and "line".

4. For a plain question that doesn't need a chart or table, your response should be:
    {"answer": "Your answer goes here"}

For example:
    {"answer": "As of December 31, 2024, Amazon reported annual revenue of $637.96 billion, reflecting a 10.99% increase from the previous year.'"}

5. If the answer is not known or available, respond with:
    {"answer": "I do not know."}
6. Output should be in the format,For example for line chart
  {"line":{"columns": ["Products", "Orders"], "data": [["51993Masc", 191], ["49631Foun", 152]]}}


Tool names:
    - python_repl_ast

Now, let's tackle the query step by step. Here's the query for you to work on: 
""" + query

    # Run the prompt through the agent and capture the response.
    response = agent.invoke(prompt)
    #print(response)
    parsed_output = parser.parse(response['output'])

    # Return the json response
    return parsed_output

def main(query_input):    
   
    # Load database credentials from .env file
    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE")
    username = os.getenv("SQL_USERNAME")
    password = os.getenv("SQL_PASSWORD")
    driver = "{ODBC Driver 17 for SQL Server}"  # Ensure this driver is installed

    # Connect to Azure SQL Database
    conn_string = f"DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}"
    db = SQLDatabase.from_uri(f"mssql+pyodbc:///?odbc_connect={conn_string}") 
    llm = llm_main()     
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
     #df = pdf_main()    
    agent = create_sql_agent(
    llm=llm,toolkit=toolkit,    
    dialect="mssql",
    verbose=True,  # Set to True for detailed output
    top_k=99999999999,
    agent_executor_kwargs={"handle_parsing_errors": True}
    )
    response = ask_agent(agent=agent, query=query_input)
  
    return response

if __name__ == "__main__":
     resultdf = main("please explain about the data")
     print(resultdf)
