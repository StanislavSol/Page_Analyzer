from bs4 import BeautifulSoup
import requests


def parse_html(url):
    result = {'status': None,
              'head': None,
              'title': None,
              'description': None}
    try:
        request = requests.get(url)
        get_status = request.status_code
        soup = BeautifulSoup(request.content, 'html5lib')
        result['status'] = get_status
        result['head'] = soup.h1.string if soup.h1 else None
        result['title'] = soup.title.string if soup.title else None
        for link in soup.find_all('meta'):
            if link.get('name') == 'description':
                result['description'] = link.get('content')
                break
    except requests.exceptions.ConnectionError:
        pass

    return result
