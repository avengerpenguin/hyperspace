import collections
from rdflib import Graph, URIRef
import requests
from bs4 import BeautifulSoup
import urlparse
from rdflib.namespace import Namespace, RDF


HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')

class FilterableList(list):
    def __getitem__(self, item_name):
        return [item for item in self if item.name == item_name]

    def keys(self):
        return set(sorted(item.name for item in self))

class Link(object):
    def __init__(self, name, href):
        self.name = name
        self.href = href

    def follow(self):
        return jump(self.href)

class Query(object):
    def __init__(self, name, href, params):
        self.name = name
        self.href = href
        self.params = params

    def build(self, params):
        for key, value in params.iteritems():
            if key in self.params:
                self.params[key] = value
            else:
                error_message = 'No query param {} exists in current ' \
                                'query template "{}"'.format(key, self.name)
                raise KeyError(error_message)
        return self

    def submit(self):
        return jump(self.href + '?' + '&'.join([key + '=' + value for key, value in self.params.iteritems()]))

class Page(object):
    def __init__(self, response):
        self.response = response
        self.url = response.url
        self.content_type = response.headers['Content-Type']
        self.extract_data()
        self.extract_links()
        self.extract_queries()

    def extract_data(self):
        self.data = Graph()
        self.data.parse(data=self.response.text)

    def extract_links(self):
        pass

    def extract_queries(self):
        pass


class HTMLPage(Page):
    def __init__(self, response):
        self.soup = BeautifulSoup(response.text)
        super(HTMLPage, self).__init__(response)

    def extract_data(self):
        self.data = Graph()
        self.data.parse(data=self.response.text, format='html')

    def extract_links(self):
        # We use a dictionary to allow lookup of links by rel
        self.links = FilterableList()
        # Find all <a/> tags
        for a_tag in self.soup.find_all('a'):
            # For now, we only consider <a/> tags with rel attributes
            if 'rel' in a_tag.attrs:
                # The rel attribute can be multivalued, so it's probably
                # alright to duplicate a link instance against multiple rel keys
                for rel in a_tag['rel']:
                    # Allow for href values to be relative...
                    absolute_href = urlparse.urljoin(self.url, a_tag['href'])
                    link = Link(rel, absolute_href)
                    self.links.append(link)

    def extract_queries(self):
        self.queries = collections.defaultdict(list)
        for form_tag in self.soup.find_all('form'):
            if 'rel' not in form_tag.attrs or form_tag.attrs['method'].lower() == 'get':
                if 'name' in form_tag.attrs:
                    name = form_tag.attrs['name']
                    params = {}
                    for input_field in form_tag.find_all('input'):
                        if 'name' in input_field.attrs:
                            field_name = input_field.attrs['name']
                            if 'value' in input_field.attrs:
                                params[field_name] = input_field.attrs['value']
                            else:
                                params[field_name] = ''

                    href = form_tag.attrs['action'] if 'action' in form_tag.attrs else self.url
                    absolute_href = urlparse.urljoin(self.url, href)

                    self.queries[name].append(Query(name, absolute_href, params))


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
                link = Link(unicode(o). unicode(o))
                self.links.append(link)

def mime_to_page(mime):
    return {
        "text/html": HTMLPage,
        'application/ld+json': HydraPage,
        }[mime]


def jump(url):
    response = requests.get(url)
    return mime_to_page(response.headers['Content-Type'])(response)
