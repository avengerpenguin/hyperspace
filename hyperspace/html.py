import collections
import urlparse
import re
from bs4 import BeautifulSoup
from hyperspace.affordances import Page, FilterableList, Link, Query
from rdflib import Graph


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
        for a_tag in self.soup.find_all('a', attrs={'rel': re.compile('.+')}):
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
            if 'method' not in form_tag.attrs or form_tag.attrs['method'].lower() == 'get':
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

