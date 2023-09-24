import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import NamedTupleCursor
from datetime import date
from urllib.parse import urlparse
import requests
from page_analyzer.html_check import get_pars_html


load_dotenv()


DATABASE_URL = os.getenv('DATABASE_URL')
connect = psycopg2.connect(DATABASE_URL)


def add_data_to_page(url):
    format_url = f'{urlparse(url).scheme}://{urlparse(url).netloc}'
    format_date = date.today().isoformat()

    with connect.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''SELECT id FROM urls
                     WHERE name=%s;''', (format_url,))
        if curs.fetchone() is None:
            message = ('Страница успешно добавлена', 'success')
            curs.execute(f'''INSERT INTO urls (name, created_at)
                            VALUES (\'{format_url}\',
                            \'{format_date}\');''')
        else:
            message = ('Страница уже существует', 'success')

        curs.execute('''SELECT * FROM urls
                      WHERE name=%s;''', (format_url,))
        get_id = curs.fetchone()
        return get_id.id, message


def get_urls():
    with connect.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''SELECT DISTINCT urls.id, name,
                     url_checks.created_at, status_code
                     FROM urls
                     LEFT JOIN url_checks
                     ON urls.id = url_checks.url_id ORDER BY id DESC;''')
        urls = curs.fetchall()
        return urls


def get_data_by_id(id):
    with connect.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''SELECT * FROM urls
                     WHERE id=%s;''', (id,))
        return curs.fetchone()


def add_data_to_check(id, url):
    format_url = f'{urlparse(url).scheme}://{urlparse(url).netloc}'
    try:
        get_status = requests.get(format_url).status_code
    except requests.exceptions.ConnectionError:
        get_status = None
    if get_status == 200:
        head, title, description = get_pars_html(requests.get(format_url))
        with connect.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('''SELECT created_at FROM urls
                          WHERE id=%s;''', (id,))
            extract_date = curs.fetchone().created_at
            curs.execute(f'''INSERT INTO url_checks (url_id, status_code,
                          h1, title, description, created_at)
                          VALUES (\'{id}\', {get_status},
                          \'{head}\', \'{title}\', \'{description}\',
                          \'{extract_date}\');''')
            return 'Страница успешно проверена', 'success'
    return 'Произошла ошибка при проверке', 'danger'


def get_checks(id):
    with connect.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''SELECT * FROM url_checks
                     WHERE url_id=%s
                     ORDER BY id DESC;''', (id,))
        return curs.fetchall()
