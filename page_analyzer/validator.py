import validators


def valid_url(url):
    error = []
    if not url:
        error = ['URL обязателен', 'danger']
    elif len(url) > 255:
        error = ['URL больше 255 символов', 'danger']
    elif not validators.url(url):
        error = ['Некорректный URL', 'danger']
    return error
