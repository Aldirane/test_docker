# test_docker
Тестовое задание для Канал Сервис / Unwind Digital

Start:
    скачать в одну директорию все файлы с git репозитория
    и выполнить в консоли команду: docker-compose up
    
docker-compose контейнер запускает сервисы:
- postgres_db "база данных PostgreSQL"
- python_app "докер файл с образом python:3.9 запускающий файл Update_PostgreSQL_DB.py"
- adminer_db "сервис для просмотра базы данных"

В dockerfile запускающий Update_PostgreSQL_DB.py:
- устанавливаются необходимые библиотеки посредством python -m pip install -r requirements.txt
  где:
    psycopg2 для соединения с БД PostgreSQL
    google-api-python-client для запроса к серверу google cloud
    google-auth-httplib2 и google-auth-oauthlib для аутентификации с помощью credentials.json пользователя 

Назначение файла Update_PostgreSQL_DB.py авторизоваться в googleAPI для доступа к googleSheetsAPI,
который возвращает значения в excel таблице "test" и занесения их в созданную таблицу test_canal в базе данных test PostgreSQL.
Функции файла Update_PostgreSQL_DB.py:
    - get_rate возвращает текущий курс ЦБ РФ доллара США к рублю посредством request файла json сайта ЦБ РФ
    - update_data подключается к базе данных test PostgreSQL, затем создает таблицу и вставляет полученные значения с функции get_sheets.
    - get_sheets авторизуется постредством credentials.json в google auth API, затем скачивает найденные данные с помощью google Discovery API
      который находит и возвращает google Sheets API
Файл Update_PostgreSQL_DB.py обновляется каждые 10 секунд.

