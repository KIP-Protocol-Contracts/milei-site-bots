import pymysql
from loguru import logger
from typing import List, Dict

import pymysql.cursors
from utils.config import DB_CONFIG

def get_db_connection():
    """Create and return a database connection"""
    return pymysql.connect(
        **DB_CONFIG,
    )

def insert_chat_history(user_id: str, message: str, sender: str, session_id: str) -> bool:
    """Insert a chat message into the database"""
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO mlw_dogs_chat_history (user_id, message, sender, session_id)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (user_id, message, sender, session_id))
            connection.commit()
            return True
    except Exception as e:
        logger.error(f"Error inserting chat history: {e}")
        return False
        

def get_chat_history(session_id: str, limit: int = 10) -> List[Dict]:
    """Retrieve chat history for a user"""
    try:
        with get_db_connection() as connection:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                    SELECT message, sender, created_at
                    FROM mlw_dogs_chat_history
                    WHERE session_id = %s
                """

                # If limit is 0, return all messages
                if limit == 0:
                    sql += " ORDER BY id ASC"
                else:
                    sql += " ORDER BY id DESC"
                    sql += " LIMIT %s"

                parameters = (session_id, limit) if limit != 0 else (session_id,)

                cursor.execute(sql, parameters)
                result = cursor.fetchall()

                return result
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise e
