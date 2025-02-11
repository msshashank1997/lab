from promptflow import tool
from promptflow.connections import CustomStrongTypeConnection
from promptflow.contracts.types import Secret
import psycopg2
import os

class PostgreConnection(CustomStrongTypeConnection):
    hostname : str
    port : int
    user : str
    passwd : Secret
    database : str

@tool
def return_answer(sql_answer: str, chat_answer, postgresql : PostgreConnection = None) -> str:
    if sql_answer:
        try:
            if postgresql is None:
                info = {
                    "host" : os.environ.get("PGHOST"),
                    "port" : os.environ.get("PGPORT"),
                    "user" : os.environ.get("PGUSER"),
                    "password" : os.environ.get("PGPASSWORD"),
                    "database" : os.environ.get("PGDATABASE")
                }
            else:
                info = {
                    "host" : postgresql.hostname,
                    "port" : postgresql.port,
                    "user" : postgresql.user,
                    "password" : postgresql.passwd,
                    "database" : postgresql.database
                }
            connection = psycopg2.connect(host=info["host"], port=info["port"], user=info["user"], password=info["password"], database=info["database"])
            cursor = connection.cursor()
            cursor.execute(sql_answer)
            columnNames = [desc[0] for desc in cursor.description]
            # limit to 100 rows
            result = cursor.fetchmany(100)
            mdtable = f"| {' | '.join(columnNames)} |\n| {' | '.join(['---' for _ in columnNames])} |\n" + "\n".join([f"| {' | '.join([str(cell) for cell in row])} |" for row in result])
            cursor.close()
            connection.close()
            # return markdown table with headers columnNames and rows result
            return "running query " + sql_answer + "\n\n" + mdtable
        except:
            return "Failed to query SQL database."
    else:
        return chat_answer
