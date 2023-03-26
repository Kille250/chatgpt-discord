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
    def convmessages_get(self, user_id, conv_id, limit=5, cur=None):
        query = """select * from (
                    select * from Convmessage
                    where role != 'system'
                    and user_id = ?
                    and conv_id = ?
                    order by id DESC
                    limit ?)
                    order by id asc;
        """

        cur.execute(query, (user_id, conv_id, limit))
        rows = cur.fetchall()

        return rows
    
    @dbconnection(path)
    def convmessages_role_get(self, user_id, role, limit=-1, cur=None):
        query = """select *
                    from Convmessage
                    where user_id = ?
                    and role = ?
                    order by id desc
                    limit ?;
        """

        cur.execute(query, (user_id, role, limit))
        rows = cur.fetchall()

        return rows
    
    @dbconnection(path)
    def convmessages_system_get(self, user_id, conv_id, limit=1, cur=None):
        query = """select * from Convmessage
                    where role = 'system'
                    and user_id = ?
                    and conv_id = ?
                    order by id DESC
                    limit ?
        """

        cur.execute(query, (user_id, conv_id, limit,))
        rows = cur.fetchall()

        return rows

    @dbconnection(path)
    def conv_update_status(self, user_id, cur=None):
        query = """UPDATE Conv SET status = 0
                    where user_id = ?
                    and status = 1"""

        cur.execute(query, (user_id,))

        return cur.rowcount
    
    @dbconnection(path)
    def whitelist_get(self, user_id, cur=None):
        query = """
                select * 
                from Whitelist 
                where user_id = ?;
                """

        cur.execute(query, (user_id,))

        rows = cur.fetchall()

        return rows
    
    @dbconnection(path)
    def whitelist_set(self, user_id, command, cur=None):
        query = """
                insert into Whitelist (user_id, command) 
                values (?, ?)
                """

        cur.execute(query, (user_id, command,))

        return cur.lastrowid
    
    @dbconnection(path)
    def whitelist_remove(self, user_id, command, cur=None):
        query = """
                delete from Whitelist
                where user_id = ?
                and command = ?
                """

        cur.execute(query, (user_id, command,))

        return cur.rowcount
