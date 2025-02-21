import sqlite3
from logs import logger_database
conn = sqlite3.connect("data/users.db")
cur = conn.cursor()

def create_user_db(cur: sqlite3.Cursor = cur):
    try:
        cur.execute("CREATE TABLE IF NOT EXISTS users(telegram_id INTEGER, username TEXT,word TEXT,attempts INTEGER, guessed_words INTEGER,guessed_word INTEGER,notifications_enabled INTEGER,hints INTEGER,referrals INTEGER DEFAULT 0, referrer_id INTEGER,exp INTEGER DEFAULT 0, coins INTEGER DEFAULT 0,level INTEGER DEFAULT 0,chat_linked INTEGER)")
        logger_database.info("Таблица users создана.")
    except Exception as e:
        logger_database.error(f"Возникла непредвиденная ошибка при создании таблицы users: {e}")


def create_promo_db(cur: sqlite3.Cursor = cur):
    try:
        cur.execute("CREATE TABLE IF NOT EXISTS promos(name TEXT, activations INTEGER, hints INTEGER, users_activated TEXT)")
        logger_database.info("Таблица promos создана.")
    except Exception as e:
        logger_database.error(f"Возникла непредвиденная ошибка при создании таблицы promos: {e}")

def reset_parameter(db_name: str,column: str,value,conn: sqlite3.Connection = conn,cur: sqlite3.Cursor = cur,condition: str = ""):
    try:
        sql = f"UPDATE {db_name} SET {column} = {value} {condition}"
        cur.execute(sql)
        conn.commit()
        logger_database.info(f"Был выполнен запрос: {sql}")
    except Exception as e:
        logger_database.error(f"Возникла непредвиденная ошибка при SQL-запросе {sql}: {e}")

def fetch_data(db_name: str,column: str,conn: sqlite3.Connection = conn,cur: sqlite3.Cursor = cur,condition: str = ""):
    try:
        sql = f"SELECT {column} FROM {db_name} {condition}"
        cur.execute(sql)
        logger_database.info(f"Был выполнен запрос: {sql}")
        return cur.fetchall()
    except Exception as e:
        logger_database.error(f"Возникла непредвиденная ошибка при SQL-запросе {sql}: {e}")



def insert_data(db_name: str,columns: str,values: str,conn: sqlite3.Connection = conn,cur: sqlite3.Cursor = cur):
    try:
        sql = f"INSERT INTO {db_name} ({columns}) VALUES ({values})"    
        cur.execute(sql)
        conn.commit()
        logger_database.info(f"Был выполнен запрос: {sql}")
    except Exception as e:
        logger_database.error(f"Возникла непредвиденная ошибка при SQL-запросе {sql}: {e}")

def insert_data_from_table(
    target_table: str,
    target_columns: str,
    source_query: str,
    conn: sqlite3.Connection = conn,
    cur: sqlite3.Cursor = cur
):
    try:
        sql = f"INSERT INTO {target_table} ({target_columns}) {source_query}"
        cur.execute(sql)
        conn.commit()
        logger_database.info(f"Выполнен запрос: {sql}")
    except Exception as e:
        logger_database.error(f"Ошибка: {e}")

def get_top10(column: str,condition: str,cur: sqlite3.Cursor = cur):
    try:
        sql = f"SELECT {column} FROM users ORDER BY {condition} DESC LIMIT 10"
        cur.execute(sql)
        logger_database.info(f"Был выполнен запрос: {sql}")
        return cur.fetchall()
    except Exception as e:
        logger_database.error(f"Возникла непредвиденная ошибка при SQL-запросе {sql}: {e}")

def create_chats_db(cur: sqlite3.Cursor = cur):
    try:
        cur.execute("CREATE TABLE IF NOT EXISTS chats(chat_id INTEGER, chat_name TEXT)")
        logger_database.info("Таблица chats создана.")
    except Exception as e:
        logger_database.error(f"Возникла непредвиденная ошибка при создании таблицы chats: {e}")

def create_chat_db(id: int,cur: sqlite3.Cursor = cur):
    try:
        cur.execute(f"CREATE TABLE IF NOT EXISTS chat_{id}(user_id INTEGER, username TEXT)")
        logger_database.info(f"Таблица чата {id} создана.")
    except Exception as e:
        logger_database.error(f"Возникла непредвиденная ошибка при создании таблицы чата {id}: {e}")
def close_conn(conn: sqlite3.Connection = conn):
    conn.close()