import hyperspace
from rdflib import Graph


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
        return hyperspace.jump(self.href)

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
        return hyperspace.jump(self.href + '?' + '&'.join(
            [key + '=' + value for key, value in self.params.iteritems()]))

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
