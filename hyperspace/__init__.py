import collections
from rdflib import Graph, URIRef
import requests
from bs4 import BeautifulSoup
import urlparse
from rdflib.namespace import Namespace, RDF


HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')

class Link(object):
    def __init__(self, href):
        self.href = href

    def follow(self):
        return jump(self.href)


class Page(object):
    def __init__(self, response):
        self.response = response
        self.url = response.url
        self.content_type = response.headers['Content-Type']
        self.extract_data()
        self.extract_links()

    def extract_data(self):
        self.data = Graph()
        self.data.parse(data=self.response.text)

    def extract_links(self, _):
        pass


class HTMLPage(Page):
    def __init__(self, response):
        super(HTMLPage, self).__init__(response)

    def extract_data(self):
        self.data = Graph()
        self.data.parse(data=self.response.text, format='html')

    def extract_links(self):
        soup = BeautifulSoup(self.response.text)
        # We use a dictionary to allow lookup of links by rel
        self.links = collections.defaultdict(list)
        # Find all <a/> tags
        for a_tag in soup.find_all('a'):
            # For now, we only consider <a/> tags with rel attributes
            if 'rel' in a_tag.attrs:
                # The rel attribute can be multivalued, so it's probably
                # alright to duplicate a link instance against multiple rel keys
                for rel in a_tag['rel']:
                    # Allow for href values to be relative...
                    absolute_href = urlparse.urljoin(self.url, a_tag['href'])
                    link = Link(absolute_href)
                    self.links[rel].append(link)


class HydraPage(Page):
    def __init__(self, response):
        super(HydraPage, self).__init__(response)

    def extract_data(self):
        self.data = Graph()
        self.data.parse(data=self.response.text, format='json-ld', identifier=self.url)

    def extract_links(self):
        self.links = collections.defaultdict(list)
        for p, o in self.data.predicate_objects(URIRef(self.url)):
            if isinstance(o, URIRef):
                link = Link(unicode(o))
                self.links[unicode(p)].append(link)

def mime_to_page(mime):
    return {
        "text/html": HTMLPage,
        'application/ld+json': HydraPage,
        }[mime]


def jump(url):
    response = requests.get(url)
    return mime_to_page(response.headers['Content-Type'])(response)
