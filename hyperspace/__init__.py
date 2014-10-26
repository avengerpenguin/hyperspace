from hyperspace.html import HTMLPage
from hyperspace.hydra import HydraPage
from hyperspace.turtle import TurtlePage
import requests
import cgi


session = requests.Session()
session.headers['User-Agent'] = 'Hyperspace (https://github.com/avengerpenguin/hyperspace)'
session.headers['Accept'] = 'text/html,application/ld+json,text/turtle'


def response_to_page(response):
    mime = cgi.parse_header(response.headers['Content-Type'])
    return mime_to_page(mime[0], **mime[1])(response)


def jump(url):
    response = session.get(url)
    return response_to_page(response)


def send(url, data, _):
    response = session.post(url, data=data)
    if 'Location' in response.headers:
        return jump(response.headers['Location'])
    else:
        return response_to_page(response)


def mime_to_page(mime, **kwargs):
    return {
        'text/html': HTMLPage,
        'application/ld+json': HydraPage,
        'text/turtle': TurtlePage,
    }[mime]

