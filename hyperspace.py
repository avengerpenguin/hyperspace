import collections
from rdflib import Graph
import requests
from bs4 import BeautifulSoup
import urlparse


class Link(object):
    def __init__(self, href):
        self.href = href

    def follow(self):
        return jump(self.href)


class Page(object):
    def __init__(self, response):
        self.url = response.url

        self.data = Graph()
        self.data.parse(data=response.text, format='html')

        soup = BeautifulSoup(response.text)

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



def jump(url):
    return Page(requests.get(url))
