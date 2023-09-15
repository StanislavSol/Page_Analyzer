from flask import (Flask,
                   render_template,
                   request,
                   url_for,
                   redirect,
                   flash,
                   get_flashed_messages)
import psycopg2
import os
from dotenv import load_dotenv
import validators
from urllib.parse import urlparse
from datetime import date


load_dotenv()

COLUMN_NAMES = ['id',
                'name',
                'created_at']
DATABASE_URL = os.getenv('DATABASE_URL')
connect = psycopg2.connect(DATABASE_URL)
CURSOR = connect.cursor()
CREATE_TABLES = CURSOR.execute(open('./database.sql', 'r').read())
app = Flask(__name__)
INDEX_DATA_WEBSITE = 0
PROTOCOL_HTTPS = 'https://'
app.secret_key =  os.getenv('SECRET_KEY')


def load_data_in_base(url):
    formatt_url = PROTOCOL_HTTPS + urlparse(url).netloc
    formatt_date = date.today().isoformat()
    CURSOR.execute(f'SELECT * FROM urls WHERE name = \'{formatt_url}\';')
    data_check = True if CURSOR.fetchall() else False
    if not data_check:
        flash('Страница успешно добавлена', 'success')
        CURSOR.execute(f'''INSERT INTO urls (name, created_at)
                       VALUES (\'{formatt_url}\',
                       \'{formatt_date}\');''')
    else:
        flash('Страница уже существует', 'success')


@app.route('/')
def get_home_page(value_url=''):
    messages = get_flashed_messages(with_categories=True)
    return render_template('home_page.html',
                           messages=messages,
                           value_url=value_url)


@app.route('/urls/<id>')
def get_id_page(id, massage=''):
    CURSOR.execute(f'SELECT name FROM urls WHERE id = {id};')
    website = CURSOR.fetchall()
    CURSOR.execute(f'SELECT * FROM urls WHERE id = {id};')
    data_website = CURSOR.fetchall()[INDEX_DATA_WEBSITE]
    messages = get_flashed_messages(with_categories=True)
    return render_template(
            'entering_and_address.html',
            messages=messages,
            website=website,
            data_website=data_website)


@app.route('/urls', methods=['GET', 'POST'])
def get_adress():
    URL = request.form.get('url')
    if request.method == 'GET':
        CURSOR.execute('SELECT * FROM urls')
        data_urls = CURSOR.fetchall()
        return render_template('urls.html', data_urls=data_urls)

    elif request.method == 'POST':
        if validators.url(URL):
            load_data_in_base(URL)
            correct_url = PROTOCOL_HTTPS + urlparse(URL).netloc
            CURSOR.execute(f'''SELECT id FROM urls
                            WHERE name = \'{correct_url}\';''')
            web_id = CURSOR.fetchall()[INDEX_DATA_WEBSITE]
            return redirect(url_for('get_id_page',
                                    id=web_id[INDEX_DATA_WEBSITE]))
        elif not URL:
            value_url = ''
            flash('URL обязателен', 'warning')

        elif not validators.url(URL):
            value_url = URL
            flash('Некорректный URL', 'warning')

        return redirect(url_for('get_home_page', value_url=value_url))
