import psycopg2

# Настройки подключения
connection = psycopg2.connect(
    dbname="task_manage",  # Имя вашей базы данных
    user="postgres",  # Имя пользователя PostgreSQL
    password="Tujh7562",  # Пароль для пользователя postgres
    host="localhost",  # Локальный хост
    port="5432"  # Стандартный порт PostgreSQL
)

# Убедимся, что соединение установлено
print("Подключение успешно!")

# Закрытие соединения
connection.close()
