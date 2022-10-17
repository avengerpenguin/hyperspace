from hyperspace.html import HTMLPage
from hyperspace.hydra import HydraPage
from hyperspace.turtle import TurtlePage
import requests
import cgi


DEFAULT_HEADERS = {
    'Accept': 'text/turtle,text/html,application/ld+json',
    'User-Agent': 'Hyperspace (https://github.com/avengerpenguin/hyperspace)'
}


config = {}


def get_client(client=None):
    if not client:
        client = requests.Session()

    if 'client' in config:
        return config['client']

    for header, value in DEFAULT_HEADERS.items():
        if header not in client.headers:
            client.headers[header] = value

    config['client'] = client
    return client


def response_to_page(response):
    if 400 <= response.status_code < 500:
        raise Exception('Client error: ' + str(response.status_code) + ' ' + response.text)
    mime = cgi.parse_header(response.headers['Content-Type'])
    return mime_to_page(mime[0], **mime[1])(response)


def jump(url, client=None):
    response = get_client(client).get(url)
    return response_to_page(response)


def send(url, data, _, client=None):
    response = get_client(client).post(url, data=data)
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


def git(command, *args, **params):
    return {
        'commit': git_commit,
        'checkout': git_checkout,
    }[command](*args, **params)


def update(uri, _store):
    print('Updating: ' + uri)
    response = get_client().put(uri, _store.serialize(format='turtle'), headers={'Content-Type': 'text/turtle'})
    print(response.text)
    return response_to_page(response)
