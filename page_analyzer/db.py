from psycopg2.extras import NamedTupleCursor


def add_data_to_page(url, date, connection):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(f'''INSERT INTO urls (name, created_at)
                      VALUES (\'{url}\',
                      \'{date}\');''')
        curs.execute('''SELECT id FROM urls
                     WHERE name=%s;''', (url,))
        get_id = curs.fetchone()
        return get_id.id


def get_urls(connection):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''SELECT DISTINCT urls.id, name,
                     url_checks.created_at, status_code
                     FROM urls
                     LEFT JOIN url_checks
                     ON urls.id = url_checks.url_id ORDER BY id DESC;''')
        urls = curs.fetchall()
        return urls


def get_id_by_url(url, connection):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''SELECT id
                     FROM urls
                     WHERE name=%s;''', (url,))
        return curs.fetchone().id


def get_data_by_id(id, connection):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''SELECT id, name, created_at
                     FROM urls
                     WHERE id=%s;''', (id,))
        return curs.fetchone()


def add_data_to_check(id, url, get_status, head,
                      title, description, connection):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''SELECT created_at FROM urls
                     WHERE id=%s;''', (id,))
        extract_date = curs.fetchone().created_at
        curs.execute(f'''INSERT INTO url_checks (url_id, status_code,
                      h1, title, description, created_at)
                      VALUES (\'{id}\', {get_status},
                      \'{head}\', \'{title}\', \'{description}\',
                      \'{extract_date}\');''')


def get_checks(id, connection):
    with connection.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''SELECT id, status_code, h1,
                     title, description, created_at
                     FROM url_checks
                     WHERE url_id=%s
                     ORDER BY id DESC;''', (id,))
        return curs.fetchall()
