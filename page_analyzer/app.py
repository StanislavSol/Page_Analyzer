import app


@app.route('/')
def hello_world():
    return 'Welcom to Flask'
