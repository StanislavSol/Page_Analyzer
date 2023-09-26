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


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@contextmanager
def connect(bd_url):
    try:
        connection = psycopg2.connect(bd_url)
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
def get_home_page():
    return render_template('home_page.html')


@app.get('/urls')
def get_urls():
    with connect(DATABASE_URL) as conn:
        return render_template('urls.html', urls=db.get_urls(conn))


@app.post('/urls')
def post_adress():
    url = request.form.get('url')
    message = valid_url(url)
    if message:
        flash(*message)
        messages = get_flashed_messages(with_categories=True)
        return render_template('home_page.html',
                               messages=messages,
                               value_url=url), 422
    else:
        with connect(DATABASE_URL) as conn:
            get_id, message = db.add_data_to_page(url, conn)
            flash(*message)
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
        message = db.add_data_to_check(id, url, conn)
        flash(*message)
        return redirect(url_for('get_id_page', id=id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('error/500.html'), 500
