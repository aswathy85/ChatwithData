import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text
import urllib.parse

def main():
    # Load environment variables
    load_dotenv()

    # Load database credentials
    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE")
    username = os.getenv("SQL_USERNAME")
    password = os.getenv("SQL_PASSWORD")
    driver = "ODBC Driver 17 for SQL Server"

    # Encode password safely
    encoded_password = urllib.parse.quote_plus(password)

    # Construct the SQLAlchemy connection string
    conn_string = f"mssql+pyodbc://{username}:{encoded_password}@{server}/{database}?driver={urllib.parse.quote_plus(driver)}"

    # Create engine
    cnx = create_engine(conn_string)

    # Open a connection before running the query
    with cnx.connect() as connection:
        query = text("SELECT * FROM [PNL Data]")  # Use `text()` for raw SQL
        df = pd.read_sql_query(query, connection)

    return df

if __name__ == "__main__":
    resultdf = main()
    print(resultdf)
