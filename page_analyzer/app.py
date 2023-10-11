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
from urllib.parse import urlparse
from page_analyzer.html_check import get_pars_html


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def get_urls():
    with db.create_connection(DATABASE_URL) as conn:
        urls = db.get_urls(conn)
    db.close_connection(conn)
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def post_urls():
    url = request.form.get('url')
    errors = valid_url(url)
    formatted_url = f'{urlparse(url).scheme}://{urlparse(url).netloc}'
    if errors:
        flash(*errors)
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html',
                               messages=messages,
                               value_url=url), 422
    with db.create_connection(DATABASE_URL) as conn:
        get_url = db.get_url_by_name(conn, formatted_url)
        if not get_url:
            get_url = db.add_url(conn, formatted_url)
            flash('Страница успешно добавлена', 'success')
        else:
            flash('Страница уже существует', 'success')
    db.close_connection(conn)
    return redirect(url_for('get_url_page',
                            id=get_url.id))


@app.route('/urls/<int:id>')
def get_url_page(id):
    with db.create_connection(DATABASE_URL) as conn:
        checks = db.get_checks(conn, id)
        url = db.get_url_by_id(conn, id)
        messages = get_flashed_messages(with_categories=True)
    db.close_connection(conn)
    return render_template(
            'url.html',
            messages=messages,
            url=url,
            checks=checks)


@app.post('/urls/<int:id>/checks')
def get_check(id):
    with db.create_connection(DATABASE_URL) as conn:
        url = db.get_url_by_id(conn, id).name
        with db.create_connection(DATABASE_URL) as conn:
            get_status, head, title, description = get_pars_html(url)
            if get_status == 200:
                check = {'id': id,
                         'status': get_status,
                         'head': head,
                         'title': title,
                         'description': description}
                db.add_url_check(conn, check)
                flash('Страница успешно проверена', 'success')
            else:
                flash('Произошла ошибка при проверке', 'danger')
    db.close_connection(conn)
    return redirect(url_for('get_url_page', id=id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
