import sqlite3
from logs import logger_database
conn = sqlite3.connect("data\\users.db")
cur = conn.cursor()

def create_user_db(cur: sqlite3.Cursor = cur):
    try:
        cur.execute("CREATE TABLE IF NOT EXISTS users(telegram_id INTEGER, username TEXT,word TEXT,attempts INTEGER, guessed_words INTEGER,guessed_word INTEGER,notifications_enabled INTEGER,hints INTEGER,referrals INTEGER DEFAULT 0, referrer_id INTEGER,exp INTEGER DEFAULT 0, coins INTEGER DEFAULT 0,level INTEGER DEFAULT 0)")
        logger_database.info("Таблица users создана.")
    except Exception as e:
        logger_database.error(f"Возникла непредвиденная ошибка при создании таблицы users: {e}")


def create_promo_db(cur: sqlite3.Cursor = cur):
    try:
        cur.execute("CREATE TABLE IF NOT EXISTS promos(name TEXT, activations INTEGER, hints INTEGER, users_activated TEXT)")
        logger_database.info("Таблица promos создана.")
    except Exception as e:
        logger_database.error(f"Возникла непредвиденная ошибка при создании таблицы promos: {e}")

def create_clans_db(cur: sqlite3.Cursor = cur):
    try:
        cur.execute("CREATE TABLE IF NOT EXISTS clans(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, photo TEXT, desc TEXT, members INTEGER, members_limit INTEGER, bank INTEGER)")
        logger_database.info("Таблица clans создана.")
    except Exception as e:
        logger_database.error(f"Возникла непредвиденная ошибка при создании таблицы clans: {e}")


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

def get_top10(column: str,condition: str,cur: sqlite3.Cursor = cur):
    try:
        sql = f"SELECT {column} FROM users ORDER BY {condition} DESC LIMIT 10"
        cur.execute(sql)
        logger_database.info(f"Был выполнен запрос: {sql}")
        return cur.fetchall()
    except Exception as e:
        logger_database.error(f"Возникла непредвиденная ошибка при SQL-запросе {sql}: {e}")

def sort_clan_members(clan_id: int,parameter: str,cur: sqlite3.Cursor = cur):
    try:
        sql = f"SELECT c.* FROM clan_{clan_id} AS c JOIN users AS u ORDER BY u.{parameter}"
        cur.execute(sql)
        logger_database.info(f"Был выполнен запрос: {sql}")
        return cur.fetchall()
    except Exception as e:
        logger_database.error(f"Возникла непредвиденная ошибка при SQL-запросе {sql}: {e}")

def create_clan_db(cur: sqlite3.Cursor = cur):
    try:
        result = fetch_data("clans", "id", "WHERE id=(SELECT max(id) FROM clans)")
        id = result[0][0] + 1 if result else 1
        cur.execute(f"CREATE TABLE IF NOT EXISTS clan_{id}(id INTEGER, role TEXT)")
        logger_database.info(f"Таблица clan_{id} создана.")
    except Exception as e:
        logger_database.error(f"Возникла непредвиденная ошибка при запросе хз: {e}")

def close_conn(conn: sqlite3.Connection = conn):
    conn.close()