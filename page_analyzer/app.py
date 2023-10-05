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
from datetime import date
from urllib.parse import urlparse
from page_analyzer.html_check import get_pars_html


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def get_urls():
    with db.create_connection() as conn:
        urls = db.get_urls(conn)
        return render_template('urls.html', urls=urls)


@app.post('/urls')
def post_urls():
    url = request.form.get('url')
    errors = valid_url(url)
    formatted_url = f'{urlparse(url).scheme}://{urlparse(url).netloc}'
    formatted_date = date.today().isoformat()
    if errors:
        flash(*errors)
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html',
                               messages=messages,
                               value_url=url), 422
    else:
        with db.create_connection() as conn:
            get_id = db.add_url_to_page(conn, formatted_url,
                                        formatted_date)
            if get_id is None:
                with db.create_connection() as conn:
                    get_id = db.get_id_by_url(conn, formatted_url)
                    flash('Страница уже существует', 'success')
            else:
                flash('Страница успешно добавлена', 'success')
    return redirect(url_for('get_url_page',
                            id=get_id))


@app.route('/urls/<int:id>')
def get_url_page(id):
    with db.create_connection() as conn:
        checks = db.get_checks(conn, id)
        url = db.get_data_by_id(conn, id)
        messages = get_flashed_messages(with_categories=True)
        return render_template('url.html',
                               messages=messages,
                               url=url,
                               checks=checks)


@app.post('/urls/<int:id>/checks')
def get_check(id):
    with db.create_connection() as conn:
        url = db.get_data_by_id(conn, id).name
        formatted_date = date.today().isoformat()
        with db.create_connection() as conn:
            get_status, head, title, description = get_pars_html(url)
            try:
                db.add_data_to_check(conn, id, url, get_status, head,
                                     title, description, formatted_date)
                flash('Страница успешно проверена', 'success')
            except Exception:
                flash('Произошла ошибка при проверке', 'danger')

        return redirect(url_for('get_url_page', id=id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
