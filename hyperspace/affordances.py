try:
    from urllib import parse as urlparse
except ImportError:
    import urlparse
from uritemplate import expand, variables
import hyperspace
from rdflib import Graph, URIRef, RDF, OWL
from laconia import ThingFactory, Thing
import yarl


class FilterableList(list):
    def __init__(self, base_url=None):
        self.base_url = base_url

    def __getitem__(self, item_name):
        if isinstance(item_name, int):
            return list.__getitem__(self, item_name)
        if self.base_url:
            item_name = urlparse.urljoin(self.base_url, item_name)

        matches = [item for item in self if item.name == item_name]
        if matches:
            if len(matches) == 1:
                return matches[0]
            else:
                return matches
        else:
            other_names = ','.join({item.name for item in self})
            raise KeyError(
                'No item with name "{name}". Available: {other_names} (Using base URL: {base})'.format(
                    name=item_name, other_names=other_names, base=self.base_url))

    def __add__(self, other):
        new = FilterableList(base_url=self.base_url)
        for item in self:
            new.append(item)
        for item in other:
            new.append(item)
        return new

    def keys(self):
        return set(sorted(item.name for item in self))


class Link(object):
    def __init__(self, name, href):
        self.name = name
        self.href = href

    def follow(self):
        return hyperspace.jump(self.href)

    def __str__(self):
        return '[{name}]({href})'.format(name=self.name, href=self.href)


class Query(object):
    def __init__(self, rel, uri_template, base_url=None):
        self.name = rel
        self.uri_template = uri_template
        self.uri = expand(uri_template)
        self.base_url = base_url

    def build(self, params):
        self.uri = expand(self.uri_template, **params)
        if self.base_url:
            self.uri = urlparse.urljoin(self.base_url, self.uri)
        return self

    def submit(self):
        """Very naive URL creation."""
        return hyperspace.jump(self.uri)

    def __call__(self, **params):
        return self.build(params).submit()

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return u'[{name}]({href})'.format(
            name=self.name, href=self.uri_template)

    def keys(self):
        return variables(self.uri_template)


class Template(object):
    def __init__(self, name, href, params, content_type):
        self.name = name
        self.href = href
        self.params = params
        self.content_type = content_type

    def build(self, newparams):
        for name, value in newparams.items():
            self.params[name] = value
        return self

    def submit(self):
        return hyperspace.send(self.href, self.params, self.content_type)

    def __str__(self):
        flat_params = u', '.join(
            [u'{name}={value}'.format(name=unicode(name), value=unicode(value))
             for name, value in self.params.items()]
        )

        return u'[{name}]({href}){{{params}}}'.format(
            name=self.name, href=self.href, params=flat_params)


class Entity(Thing):
    def update(self):
        return hyperspace.update(self._id, self._store)

    def follow(self):
        print('Following: ' + str(self._id))
        return hyperspace.jump(str(self._id))


class EntityFactory(ThingFactory):
    def __call__(self, ident=None, **props):
        return Entity(self.store, self.schema_store, self.alias_map, ident, props)


class Page(object):
    def __init__(self, response):
        self.response = response
        self.url = response.url
        self.content_type = response.headers['Content-Type']
        self.extract_data()
        self.extract_links()
        self.extract_queries()
        self.extract_templates()

    def extract_data(self):
        self.data = Graph()
        self.data.parse(data=self.response.text, publicID=self.response.url)

    def extract_links(self):
        self.links = FilterableList()

    def extract_queries(self):
        self.queries = FilterableList()

    def extract_templates(self):
        self.templates = FilterableList()

    def entity(self, uri):
        self.data.bind('schema', 'http://schema.org/', override=True)
        return EntityFactory(self.data)(uri)

    @property
    def entities(self):
        thing = URIRef(urlparse.urljoin(self.response.url, '/vocab#Thing'))
        return [EntityFactory(self.data)(uri)
                for uri in self.data.subjects(predicate=RDF.type, object=thing)]

    def __getattr__(self, item):
        try:
            item_url = str(yarl.URL(self.url).with_fragment(item))
            return self.queries[item_url]
        except KeyError:
            print(self.data.serialize(format='turtle').decode('utf-8'))
            raise

    def __getitem__(self, item):
        if type(item) == int:
            try:
                return self.entities[item]
            except IndexError:
                print('Cannot find entity in: ' + self.data.serialize(format='turtle').decode('utf-8'))
                raise
        else:
            if item in self.data.subjects():
                return self.entity(item)
            else:
                return self.templates[item]

    def __str__(self):
        return u'Page:\n\tData:\n{data}\n\tLinks:\n\t\t{links}\n\tQueries:\n\t\t{queries}\n\tTemplates:\n\t\t{templates}'.format(
            data=self.data.serialize(format='turtle').decode('utf-8'),
            links=u'\n\t\t'.join([unicode(l) for l in self.links]),
            queries=u'\n\t\t'.join([unicode(f) for f in self.queries]),
            templates=u'\n\t\t'.join([unicode(t) for t in self.templates])).encode('utf-8')
