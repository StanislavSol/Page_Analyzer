import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import NamedTupleCursor

load_dotenv()


DATABASE_URL = os.getenv('DATABASE_URL')
connect = psycopg2.connect(DATABASE_URL)


def add_data_to_page(url, date):
    with connect.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(f'''SELECT id FROM urls
                      WHERE name=%s;''', (url,))
        if curs.fetchone() is None:
            message = ('Страница успешно добавлена', 'success')
            curs.execute(f'''INSERT INTO urls (name, created_at)
                            VALUES (\'{url}\',
                            \'{date}\');''')
        else:
            message = ('Страница уже существует', 'success')

        curs.execute(f'''SELECT id FROM urls
                      WHERE name=%s;''', (url,))
        get_id = curs.fetchone() 
        return get_id.id, message


def get_urls():
    with connect.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('SELECT * FROM urls;')
        urls = curs.fetchall()
        return urls


def get_data_by_id(id):
    with connect.cursor(cursor_factory=NamedTupleCursor) as curs:
         curs.execute(f'SELECT * FROM urls WHERE id=%s;', (id,))
         return curs.fetchone()
