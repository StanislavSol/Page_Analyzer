import validators


def valid_url(url):
    error = []
    if not url:
        error = ['URL обязателен', 'warning']
    elif len(url) > 255:
        error = ['URL больше 255 символов', 'warning']
    elif not validators.url(url):
        error = ['Некорректный URL', 'warning']
    return error
