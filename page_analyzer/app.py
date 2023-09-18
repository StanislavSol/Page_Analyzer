from flask import (Flask,
                   render_template,
                   request,
                   url_for,
                   redirect,
                   flash,
                   get_flashed_messages)
from urllib.parse import urlparse
from datetime import date
from page_analyzer.validator import valid_url
from page_analyzer import db
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def get_home_page():
    return render_template('home_page.html')


@app.route('/urls/<id>')
def get_id_page(id):
    get_data = db.get_data_by_id(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template('entering_and_address.html',
                           messages=messages,
                           website=get_data.name,
                           data_website=get_data)


@app.get('/urls')
def get_urls():
    return render_template('urls.html', urls=db.get_urls())


@app.post('/urls')
def post_adress():
    url = request.form.get('url')
    message = valid_url(url)
    if message:
        flash(*message)
        messages = get_flashed_messages(with_categories=True)
        return render_template('home_page.html',
                                messages=messages,
                                value_url=url)
    else:
        formatt_url = urlparse(url).scheme + '://' + urlparse(url).netloc
        formatt_date = date.today().isoformat()
        get_id, message = db.add_data_to_page(formatt_url,
                                          formatt_date)
        flash(*message)
        return redirect(url_for('get_id_page',
                                id=get_id))
