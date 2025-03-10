from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer
from pydantic import BaseModel
from typing import Optional
import psycopg2
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()


def get_db_connection():
    """Создает соединение с базой данных PostgreSQL."""
    return psycopg2.connect(
        dbname="task_manage",
        user="postgres",
        password="Tujh7562",
        host="localhost",
        port="5432"
    )


def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля хешу."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """Создает JWT-токен."""
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Security(oauth2_scheme)) -> str:
    """Получает текущего пользователя из JWT-токена."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Срок действия токена истек")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Недействительный токен")


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


@app.post("/register/")
def register(user: UserCreate):
    """Регистрирует нового пользователя."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Пользователь уже существует")

            cursor.execute(
                "INSERT INTO users (email, password) VALUES (%s, %s)",
                (user.email, hash_password(user.password))
            )
            conn.commit()

    return {"message": "Пользователь успешно зарегистрирован"}


@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Авторизация пользователя и получение JWT-токена."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, email, password FROM users WHERE email = %s", (form_data.username,))
            user = cursor.fetchone()

            if not user or not verify_password(form_data.password, user[2]):
                raise HTTPException(status_code=401, detail="Неверные учетные данные")

            access_token = create_access_token(
                data={"sub": user[1]},
                expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/tasks/")
def create_task(task: TaskCreate, current_user: str = Depends(get_current_user)):
    """Создает новую задачу."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tasks (title, description, status, deadline)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (task.title, task.description, task.status, task.deadline)
            )
            task_id = cursor.fetchone()[0]
            conn.commit()

    return {"message": "Задача успешно создана", "id": task_id}


@app.get("/tasks/")
def get_tasks(current_user: str = Depends(get_current_user)):
    """Возвращает список задач."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, description, status, deadline FROM tasks")
            tasks = cursor.fetchall()

    return tasks


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user: str = Depends(get_current_user)):
    """Удаляет задачу."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Задача не найдена")

            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            conn.commit()

    return {"message": "Задача успешно удалена"}


@app.patch("/tasks/{task_id}")
def update_task_status(
        task_id: int,
        task_update: TaskUpdate,
        current_user: str = Depends(get_current_user),
):
    """Обновляет статус задачи."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Задача не найдена")

            cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (task_update.status, task_id))
            conn.commit()

    return {"message": "Статус задачи обновлен"}
