Установите зависимости и вс
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

Установка своего айпи для сервера (или используйте домен если вы на сервере)
В файле .env измените параметр REACT_APP_API_URL на ваш действуйющий айпи + порт или на ваш домен

Запуск сервера
cd ./backend/server
uvicorn main:app --reload

запуск приложения
npm start
(если браузер сам не открылся перейдите по ссылке в консоли)

pytest
cd ./backend/server
pytest test_api.py -s
(если хотите провести тест несколько раз измените данные почты в тесте нового пользователя, иначе будет ошибка, что пользователь уже существует)


Информация
Доска с задачами kanban.

   Backend (Серверная часть)
Python 3.13 – основной язык программирования.
FastAPI – фреймворк для разработки REST API.
JWT (PyJWT) – аутентификация через токены.
Pydantic – валидация данных.
psycopg2 – подключение к PostgreSQL.
Passlib (bcrypt) – хеширование паролей.
pytest + httpx – тестирование API.
CORS Middleware – разрешение запросов с фронтенда.
dotenv – хранение конфигураций в .env.
   Database (База данных)
PostgreSQL – реляционная база данных.
   Frontend (Клиентская часть)
React.js – библиотека для интерфейса.
React Router – навигация между страницами.
React Hooks (useState, useEffect, useNavigate) – управление состоянием.
Fetch API – отправка запросов на backend.
React-Quill – текстовый редактор.

Визуал:
Форма входа
![image](https://github.com/user-attachments/assets/cbe85789-38ce-497f-9a41-859c7028a020)
Форма регистрации
![image](https://github.com/user-attachments/assets/08e2e4f5-f53a-4306-8270-162c29dcc552)
доска (с развернутым описанием 1 задачи)
![image](https://github.com/user-attachments/assets/80f10292-da86-4dc2-bd4d-d4c8da632113)
Форма редактирования задачи
![image](https://github.com/user-attachments/assets/f091b5f8-e62e-4828-8926-8edeb738469f)
Форма создания задачи
![image](https://github.com/user-attachments/assets/d8c0dc90-9def-4c8b-b7a4-5d5f90f66aa7)
Также реализованы инпуты с поиском по названию/описанию, сортировка по дате
Перенос задач по статусам осуществляется по принципу drag and drop

