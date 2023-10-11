from psycopg2.extras import NamedTupleCursor
import psycopg2
from contextlib import contextmanager


@contextmanager
def create_connection(db_url):
    try:
        connection = psycopg2.connect(db_url)
        yield connection
    except Exception:
        if connection:
            connection.rollback()
        raise
    else:
        if connection:
            connection.commit()


def close_connection(connection):
    if connection:
        connection.close()


def add_url(connection, url):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''INSERT INTO urls (name)
                     VALUES (%s) RETURNING id;''', (url,))
        return curs.fetchone()


def get_urls(connection):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('SELECT id, name FROM urls ORDER BY id DESC;')
        urls = curs.fetchall()
        curs.execute('''SELECT url_id, created_at, status_code
                     FROM url_checks
                     ORDER BY created_at DESC;''')
        url_checks = curs.fetchall()
        if url_checks:
            result = []
            for url in urls:
                flag = False
                for check in url_checks:
                    if url.id == check.url_id:
                        result.append(url._asdict() | check._asdict())
                        flag = True
                        break
                if not flag:
                    result.append(url._asdict())
            return result
        return urls


def get_url_by_name(connection, name):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''SELECT id, name, created_at
                     FROM urls
                     WHERE name=%s;''', (name,))
        return curs.fetchone()


def get_url_by_id(connection, id):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''SELECT id, name, created_at
                     FROM urls
                     WHERE id=%s;''', (id,))
        return curs.fetchone()


def add_url_check(connection, check):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''INSERT INTO url_checks (url_id, status_code,
                     h1, title, description)
                     VALUES (%s, %s, %s, %s, %s);''',
                     (check['id'],
                      check['status'],
                      check['head'],
                      check['title'],
                      check['description'],))


def get_checks(connection, id):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''SELECT id, status_code, h1,
                     title, description, created_at
                     FROM url_checks
                     WHERE url_id=%s
                     ORDER BY id DESC;''', (id,))
        return curs.fetchall()
