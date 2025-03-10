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