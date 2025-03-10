import os
import psycopg2
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

def get_db_connection():
    """Создает и возвращает соединение с базой данных."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def create_users_table():
    """Создает таблицу пользователей, если она не существует."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                );
            """)
            conn.commit()

if __name__ == "__main__":
    create_users_table()
