from pandasai import SmartDataframe
import pandas as pd
from Agents.CreatePandasDataframe import main as pdf_main
from Agents.LLMChatAgent import main as llm_main
from langchain_core.output_parsers import JsonOutputParser

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
Generate a structured JSON response for the given query.
The structure of the responses depend on the type of information requested in the query.
Given the following financial data, analyze trends, compare metrics, and generate insights based on revenue, expenses, and profitability. Answer the following questions:" 
**Data:**
Vertical	Account	Year	Month	Revenue	Resource Cost	Direct Expense	Sales Expense	G&A Expense	EBITDA With Forex	Gross Margin with forex
Insurance	Ins3MAccount	2024	September	17107.91	11620.69	4.76	0	394.5	5087.96	5482.46

**Example Questions**
1. Compare the revenue trends for September and December 2024.
2. Identify the major cost components impacting EBITDA.
3. What is the percentage change in Gross Margin from September to December?
4. If resource costs were reduced by 10%, how would EBITDA change?
5. Predict the revenue trend for the next quarter based on this data.
6. What is the average monthly revenue for 2024?


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
    response = agent.chat(prompt)
    #print(response)
    parsed_output = parser.parse(response['output'])

    # Return the json response
    return parsed_output
   
def main(query):
    pdf = pdf_main()  # Ensure this returns a pandas DataFrame
    llm = llm_main()
    # Create SmartDataFrame using PandasAI
    Agent = SmartDataframe(pdf, config={"llm": llm})

    try:
        # Query the agent
        #response = ask_agent(Agent, query)         
        response = Agent.chat(query) 
        return response

    except Exception as e:
        return {"error": str(e)}    

if __name__ == "__main__":
    Query="show an yearly trend of revnue?"
    print(main(Query))

