from openai import OpenAI
import os
from database_utils import DatabaseUtils
from prettytable import PrettyTable
import mysql.connector


class SQLInfo:
    def __init__(self, cursor1, cursor2, args):
        self.client = OpenAI ( api_key=os.environ.get('OPENAI_API_KEY'),)
        self.cursor1 = cursor1
        self.cursor2 = cursor2
        self.args = args
    
    def generate_sql_query(self, user_input):
        prompt = f"Generate a SQL query to {user_input}. Only print the query"
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    
    def execute_sql_query(self, sql_query):
        if sql_query is None:
            print("No SQL query provided.")
            return

        if sql_query.strip().upper().startswith("SELECT"):
            if self.cursor2 is None:
                self.cursor1.execute(sql_query)
                print(self.cursor1.fetchall())
                return
            else:
                self.cursor1.execute(sql_query)
                print(self.cursor1.fetchall())
                self.cursor2.execute(sql_query)
                print(self.cursor2.fetchall())
                return
        else:
            if self.cursor2 is None:
                self.cursor1.execute(sql_query)
                return
            else:
                self.cursor1.execute(sql_query)
                self.cursor2.execute(sql_query)
                return
    def get_input(self):
        user_input = input("What information would you like to query?")
        sql_query = self.generate_sql_query(user_input)
        print(sql_query)
        self.execute_sql_query(sql_query)

    def list_databases(self, server, user, password, host, port):
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        cursor = conn.cursor()
        databases = DatabaseUtils.get_database_names(cursor)

        table = PrettyTable(["Databases on {}".format(server)])
        table.align["Databases on {}".format(server)] = 'l'
        for database in databases:
            table.add_row([database])

        conn.close()
        print(table)
        return table

    
    def main(self):
        if self.args['list']:
            user1, password1, host1, port1 = DatabaseUtils.parse_connection_string(self.args['server1'])
            self.list_databases("Server 1", user1, password1, host1, port1)
            
            if self.args['server2']:
                user2, password2, host2, port2 = DatabaseUtils.parse_connection_string(self.args['server2'])
                self.list_databases("Server 2", user2, password2, host2, port2)
            else:
                pass

        if self.args['tables']:
            if self.args['database'] is None:
                print("Error: --database is required. with --tables")
                return
            else:
                self.print_tables()

        if self.args['sql_query'] is not None:
            if self.args['openai']:
                self.get_input()
            else:
                self.execute_sql_query(self.args['sql_query'])
            