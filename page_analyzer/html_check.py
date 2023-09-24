from bs4 import BeautifulSoup


def get_pars_html(request):
    soup = BeautifulSoup(request.content, 'html5lib')
    head = soup.h1.string if soup.h1 else ''
    title = soup.title.string if soup.title else ''
    description = ''
    for link in soup.find_all('meta'):
        if link.get('name') == 'description':
            description = link.get('content')
            break
    return head, title, description
