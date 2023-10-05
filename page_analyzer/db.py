from psycopg2.extras import NamedTupleCursor
import psycopg2
from dotenv import load_dotenv
import os
from contextlib import contextmanager


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


@contextmanager
def create_connection():
    try:
        connection = psycopg2.connect(DATABASE_URL)
        yield connection
    except Exception:
        if connection:
            connection.rollback()
        raise
    else:
        if connection:
            connection.commit()
    finally:
        if connection:
            connection.close()


def add_url_to_page(connection, url, date):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        try:
            curs.execute('''INSERT INTO urls (name, created_at)
                         VALUES (%s, %s) RETURNING id;''', (url, date))
            get_id = curs.fetchone()
            return get_id.id
        except psycopg2.errors.UniqueViolation:
            return None


def get_urls(connection):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('SELECT id, name FROM urls ORDER BY id DESC;')
        extract_names_and_id = curs.fetchall()
        urls = []
        for data in extract_names_and_id:
            curs.execute('''SELECT created_at, status_code
                         FROM url_checks
                         WHERE url_id = %s;''', (data.id,))
            extract_status = curs.fetchone()
            if extract_status:
                urls.append(data._asdict() | extract_status._asdict())
            else:
                urls.append(data._asdict())
        return urls


def get_id_by_url(connection, url):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''SELECT id
                     FROM urls
                     WHERE name=%s;''', (url,))
        return curs.fetchone().id


def get_data_by_id(connection, id):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''SELECT id, name, created_at
                     FROM urls
                     WHERE id=%s;''', (id,))
        return curs.fetchone()


def add_data_to_check(connection, id, url, get_status, head,
                      title, description, date):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''INSERT INTO url_checks (url_id, status_code,
                     h1, title, description, created_at)
                     VALUES (%s, %s, %s, %s, %s, %s);''',
                     (id, get_status, head, title, description, date))


def get_checks(connection, id):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''SELECT id, status_code, h1,
                     title, description, created_at
                     FROM url_checks
                     WHERE url_id=%s
                     ORDER BY id DESC;''', (id,))
        return curs.fetchall()
