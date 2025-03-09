from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import psycopg2
from fastapi.middleware.cors import CORSMiddleware
# Инициализация приложения
app = FastAPI()


# Pydantic модели для работы с данными
class TaskCreate(BaseModel):
    title: str
    description: Optional[str]
    status: str
    deadline: Optional[str]


class TaskUpdate(BaseModel):
    status: str


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Разрешаем запросы с React
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы (GET, POST, PATCH, DELETE)
    allow_headers=["*"],  # Разрешаем любые заголовки
)

# Функция для получения соединения с базой данных
def get_db_connection():
    conn = psycopg2.connect(
        dbname="task_manage",
        user="postgres",
        password="Tujh7562",
        host="localhost",
        port="5432"
    )
    return conn


# Функция для закрытия пула соединений
def shutdown_db_pool():
    pass


# Эндпоинт для создания задачи
@app.post("/tasks/")
def create_task(task: TaskCreate, db_conn=Depends(get_db_connection)):
    try:
        cursor = db_conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (title, description, status, deadline)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (task.title, task.description, task.status, task.deadline)
        )
        task_id = cursor.fetchone()[0]
        db_conn.commit()
        return {"message": "Задача успешно создана", "id": task_id}
    except Exception as e:
        db_conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


# Эндпоинт для получения списка задач
@app.get("/tasks/")
def get_tasks(db_conn=Depends(get_db_connection)):
    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT id, title, description, status, deadline FROM tasks")
        tasks = cursor.fetchall()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


@app.patch("/tasks/{task_id}")
def update_task_status(task_id: int, task_update: TaskUpdate, db_conn=Depends(get_db_connection)):
    print(f"Получены данные: {task_update.dict()}")
    allowed_statuses = ["новая", "в процессе", "завершена"]
    if task_update.status not in allowed_statuses:
        raise HTTPException(status_code=422, detail=f"Недопустимый статус: {task_update.status}")
    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
        task = cursor.fetchone()
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        cursor.execute(
            """
            UPDATE tasks
            SET status = %s
            WHERE id = %s
            """, (task_update.status, task_id)
        )
        db_conn.commit()
        return {"message": f"Статус задачи обновлён на '{task_update.status}'"}
    except Exception as e:
        db_conn.rollback()
        print(f"Ошибка в процессе выполнения запроса: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()




# Эндпоинт для удаления задачи
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db_conn=Depends(get_db_connection)):
    try:
        cursor = db_conn.cursor()

        cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
        task_exists = cursor.fetchone()
        if not task_exists:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        db_conn.commit()
        return {"message": "Задача успешно удалена"}
    except Exception as e:
        db_conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
