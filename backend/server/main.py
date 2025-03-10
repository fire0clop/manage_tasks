from fastapi import FastAPI, HTTPException, Depends, Security
from pydantic import BaseModel
from typing import Optional
import psycopg2
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer

# Инициализация FastAPI
app = FastAPI()

# Настройки CORS (для связи с React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Разрешаем запросы с React
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы (GET, POST, PATCH, DELETE)
    allow_headers=["*"],  # Разрешаем любые заголовки
)

# Конфигурация JWT и хеширования паролей
SECRET_KEY = "your_secret_key"  # Замени на свой секретный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()

# Функция подключения к БД PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        dbname="task_manage",
        user="postgres",
        password="Tujh7562",
        host="localhost",
        port="5432"
    )
    return conn

# Хеширование пароля
def hash_password(password: str):
    return pwd_context.hash(password)

# Проверка пароля
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Создание JWT-токена
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Проверка токена (аутентификация пользователя)
def get_current_user(token: str = Security(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Срок действия токена истек")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Недействительный токен")

# Pydantic-модели
class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str]
    status: str
    deadline: Optional[str]

class TaskUpdate(BaseModel):
    status: str

# Эндпоинт регистрации пользователя
@app.post("/register/")
def register(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
    existing_user = cursor.fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed_password = hash_password(user.password)
    cursor.execute(
        "INSERT INTO users (email, password) VALUES (%s, %s)",
        (user.email, hashed_password)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Пользователь успешно зарегистрирован"}

# Эндпоинт входа (получение JWT-токена)
@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, password FROM users WHERE email = %s", (form_data.username,))
    user = cursor.fetchone()
    if not user or not verify_password(form_data.password, user[2]):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

    access_token = create_access_token(
        data={"sub": user[1]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    cursor.close()
    conn.close()

    return {"access_token": access_token, "token_type": "bearer"}

# Эндпоинт для создания задачи (защищен токеном)
@app.post("/tasks/")
def create_task(task: TaskCreate, current_user: str = Depends(get_current_user), db_conn=Depends(get_db_connection)):
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

# Эндпоинт для получения списка задач (защищен токеном)
@app.get("/tasks/")
def get_tasks(current_user: str = Depends(get_current_user), db_conn=Depends(get_db_connection)):
    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT id, title, description, status, deadline FROM tasks")
        tasks = cursor.fetchall()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

# Эндпоинт для удаления задачи (защищен токеном)
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user: str = Depends(get_current_user), db_conn=Depends(get_db_connection)):
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

# Эндпоинт для обновления задачи (изменения статуса)
@app.patch("/tasks/{task_id}")
def update_task_status(
        task_id: int,
        task_update: TaskUpdate,
        current_user: str = Depends(get_current_user),
        db_conn=Depends(get_db_connection),
):
    try:
        cursor = db_conn.cursor()

        # Проверяем, существует ли задача
        cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
        task_exists = cursor.fetchone()
        if not task_exists:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        # Обновляем статус
        cursor.execute(
            "UPDATE tasks SET status = %s WHERE id = %s",
            (task_update.status, task_id),
        )
        db_conn.commit()

        return {"message": "Статус задачи обновлен"}
    except Exception as e:
        db_conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

