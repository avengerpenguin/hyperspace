from rdflib import Graph


class Page(object):
    def __init__(self, data=None):
        self.data = data

def parse(html_string):
    g = Graph()
    g.parse(data=html_string, format='html')

    page = Page(data=g)
    return page
