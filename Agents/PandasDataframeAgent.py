#pip install langchain_experimental
#pip install tabulate
from langchain_core.output_parsers import JsonOutputParser
from langchain_experimental.agents import create_pandas_dataframe_agent
from Agents.LLMChatAgent import main as llm_main
from CreatePandasDataframe import main as pdf_main



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
Let's decode the way to respond to the queries. The final output should always be a JSON.
The structure of the responses depend on the type of information requested in the query. 

1. If the query requires a table, format your answer like this:
    {"table": {"headers": ["column1", "column2", ...], "rows": [[value1, value2, ...], [value1, value2, ...], ...]}}

2. For a bar chart, respond like this:
    {"bar": {"x_axis": ["A", "B", "C", ...], "y_axis": [25, 24, 10, ...]}}

3. If a line chart is more appropriate, your reply should look like this:
    {"line": {"x_axis": ["A", "B", "C", ...], "y_axis": [25, 24, 10, ...]}}

Note: We only accommodate two types of charts: "bar" and "line".

4. For a plain question that doesn't need a chart or table, your response should be:
    {"answer": "Your answer goes here"}

For example:
    {"answer": "The Product with the highest Orders is '15143Exfo'"}

5. If the answer is not known or available, respond with:
    {"answer": "I do not know."}

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
    
    df = pdf_main()
    llm = llm_main()
    agent = create_pandas_dataframe_agent(llm, df, verbose=True, allow_dangerous_code=True, agent_executor_kwargs={"handle_parsing_errors": True})
    # Query the agent.
    response = ask_agent(agent=agent, query=query_input)
    return response

if __name__ == "__main__":
    Query="show an yearly trend of revnue?"
    print(main(Query))
