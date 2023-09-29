from flask import (Flask,
                   render_template,
                   request,
                   url_for,
                   redirect,
                   flash,
                   get_flashed_messages)
from page_analyzer.validator import valid_url
from page_analyzer import db
from dotenv import load_dotenv
import os
import psycopg2
from contextlib import contextmanager
from datetime import date
from urllib.parse import urlparse
import requests
from page_analyzer.html_check import get_pars_html


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@contextmanager
def connect(db_url):
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
    finally:
        if connection:
            connection.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def get_urls():
    with connect(DATABASE_URL) as conn:
        return render_template('urls.html', urls=db.get_urls(conn))


@app.post('/urls')
def post_adress():
    url = request.form.get('url')
    errors = valid_url(url)
    format_url = f'{urlparse(url).scheme}://{urlparse(url).netloc}'
    format_date = date.today().isoformat()
    if errors:
        flash(*errors)
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html',
                               messages=messages,
                               value_url=url), 422
    else:
        with connect(DATABASE_URL) as conn:
            try:
                get_id = db.add_data_to_page(format_url,
                                             format_date,
                                             conn)
                flash('Страница успешно добавлена', 'success')
            except Exception:
                with connect(DATABASE_URL) as conn:
                    get_id = db.get_id_by_url(format_url, conn)
                    flash('Страница уже существует', 'success')

            return redirect(url_for('get_id_page',
                                    id=get_id))


@app.route('/urls/<int:id>')
def get_id_page(id):
    with connect(DATABASE_URL) as conn:
        result_check = db.get_checks(id, conn)
        get_data = db.get_data_by_id(id, conn)
        messages = get_flashed_messages(with_categories=True)
        return render_template('entering_and_address.html',
                               messages=messages,
                               data_website=get_data,
                               result_check=result_check)


@app.post('/urls/<int:id>/checks')
def get_check_website(id):
    with connect(DATABASE_URL) as conn:
        url = db.get_data_by_id(id, conn).name
        try:
            get_status = requests.get(url).status_code
        except requests.exceptions.ConnectionError:
            get_status = None

        if get_status == 200:
            head, title, description = get_pars_html(requests.get(url))
            try:
                db.add_data_to_check(id, url, get_status, head,
                                     title, description, conn)
                flash('Страница успешно проверена', 'success')
            except Exception:
                flash('Произошла ошибка при проверке', 'danger')
        else:
            flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_id_page', id=id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
