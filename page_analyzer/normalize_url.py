from urllib.parse import urlparse


def normalize_url(url):
    url_parse = urlparse(url)
    formatted_url = f'{url_parse.scheme}://{url_parse.netloc}'
    return formatted_url
