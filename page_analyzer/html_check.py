from bs4 import BeautifulSoup
import requests


def get_pars_html(url):
    result = {'get_status': None,
              'head': None,
              'title': None,
              'description': None}
    try:
        get_status = requests.get(url).status_code
        request = requests.get(url)
        soup = BeautifulSoup(request.content, 'html5lib')
        result['get_status'] = get_status
        result['head'] = soup.h1.string if soup.h1 else ''
        result['title'] = soup.title.string if soup.title else ''
        for link in soup.find_all('meta'):
            if link.get('name') == 'description':
                result['description'] = link.get('content')
                break
    except requests.exceptions.ConnectionError:
        pass

    return (result['get_status'],
            result['head'],
            result['title'],
            result['description'])
