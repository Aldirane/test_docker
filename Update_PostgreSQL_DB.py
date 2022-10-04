# psycopg2 для подключение к PostgreSQL, модуль requests для получения данных в формате json
import os.path, time, psycopg2, requests
# импортируемые библиотеки googleAPI необходимые для доступа и авторизации
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# подключается как проект check order в google cloud console только с правом чтения
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# ID эксель таблицы и диапазон значений
SAMPLE_SPREADSHEET_ID = '1euQqRJ3grldaec9m3nvejTALAMR5gFQETJgDEjXZxy8'
SAMPLE_RANGE_NAME = 'Лист1!A1:Z10000'

def get_rate():
    # Получит текущий курс доллара США к рублю с сайта ЦБ РФ
    data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    return data['Valute']['USD']['Value']


def update_data(rate, data):
    # Подключение к базе данных PostgreSQL
    conn = psycopg2.connect(database='test', user='docker', \
            password='docker', host='postgres_db')
    conn.autocommit = True
    cursor = conn.cursor()
    # Удаление таблицы если есть
    cursor.execute('drop table if exists test_canal')   
    # Создание таблицы
    sql_create = '''create table test_canal (№ int, заказ_№ int, 
    стоимость_$ int, стоимость_руб float, срок_поставки char(20))'''
    cursor.execute(sql_create)
    sql_insert = '''insert into test_canal (№, заказ_№, 
    стоимость_$, стоимость_руб, срок_поставки) values (
    %s, %s, %s, %s, %s)'''
    # Вставка значение в таблицу
    cursor.executemany(sql_insert, ((val[0],val[1], val[2],\
    '%.2f'%(int(val[2])*rate), val[3],) for val in data)
    )
    
    conn.commit()
    conn.close()



def get_sheets():
    """Проходит авторизацию через googleAPI используя секретные данные пользователя
       в файле credentials.json и возвращает данные эксель таблицы.
    """
    creds = None
    # Первый файл токен.json хранит доступ к пользователю и "обновляемые токены", он
    # создается автоматически когда происходит авторизация в первый раз.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        #build из googleDiscoveryAPI подключается к googleSheetsAPI
        service = build('sheets', 'v4', credentials=creds) 

        # вызывает googleSheetsAPI
        sheet = service.spreadsheets()
        #Получает данные с ID указанной excel таблицы, в определенном диапазоне по ключу range 
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', []) 
        
        if not values:
            print('No data found.')
            return
        else:
            return values
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    #импортирует из мудуля функцию для обновления базы данных PostgreSQL и
    #функцию для получения текущего обменного курса доллар США с сайта ЦБ РФ
    while True:
        time.sleep(10)
        rate = get_rate()
        values = get_sheets()
        update_data(rate, values[1:])
        print('Successfuly upgraded PostgreSQL database!')