from hyperspace.html import HTMLPage
from hyperspace.hydra import HydraPage
import requests


def jump(url):
    response = requests.get(url)
    return mime_to_page(response.headers['Content-Type'])(response)

def mime_to_page(mime):
    return {
        "text/html": HTMLPage,
        'application/ld+json': HydraPage,
        }[mime]
