from functools import wraps
import sqlite3
import os
from dotenv import load_dotenv


class Database():

    load_dotenv()
    path = os.getenv("DATABASE_PATH")

    def dbconnection(dbname):
        def wrapper(fun):
            @wraps(fun)
            def inner_function(*args, **kwargs):
                con = sqlite3.connect(dbname)
                cur = con.cursor()
                kwargs['cur'] = cur
                retval = fun(*args, **kwargs)
                con.commit()
                con.close()
                return retval
            return inner_function
        return wrapper

    @dbconnection(path)
    def create_table(self, table_name: str, tables: list, cur=None):
        tables = ', '.join(tables)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({tables});"

        cur.execute(query)
        return True

    @dbconnection(path)
    def conv_insert(self, user_id, status, cur=None):
        query = """INSERT INTO Conv (user_id, status)
                    VALUES(?, ?)"""

        cur.execute(query, (user_id, status,))

        return cur.lastrowid

    @dbconnection(path)
    def convmessage_insert(self, user_id, conv_id, role, message, cur=None):
        query = """INSERT INTO Convmessage (user_id, conv_id, role, message)
                    VALUES(?, ?, ?, ?)"""

        cur.execute(query, (user_id, conv_id, role, message,))

        return cur.lastrowid

    @dbconnection(path)
    def conv_get(self, user_id, cur=None):
        query = """SELECT * from Conv
                    where user_id = ?
                    and status = 1"""

        cur.execute(query, (user_id,))
        rows = cur.fetchall()

        return rows

    @dbconnection(path)
    def convmessage_get(self, user_id, conv_id, cur=None):
        query = """select * from (
                    select * from Convmessage
                    where role != 'system'
                    and user_id = ?
                    and conv_id = ?
                    order by id DESC
                    limit 5)
                    order by id asc;
        """

        cur.execute(query, (user_id, conv_id,))
        rows = cur.fetchall()

        return rows
    
    @dbconnection(path)
    def convmessage_system_get(self, user_id, conv_id, cur=None):
        query = """select * from Convmessage
                    where role = 'system'
                    and user_id = ?
                    and conv_id = ?
                    order by id DESC
                    limit 1
        """

        cur.execute(query, (user_id, conv_id,))
        rows = cur.fetchall()

        return rows

    @dbconnection(path)
    def conv_update_status(self, user_id, cur=None):
        query = """UPDATE Conv SET status = 0
                    where user_id = ?
                    and status = 1"""

        cur.execute(query, (user_id,))
        
        return cur.rowcount
