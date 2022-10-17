import unittest
import httpretty
from rdflib import URIRef, Literal
import hyperspace
from . import HypermediaBaseTest
from .hfactors import LOTest, LTTest, LNTest


class CollectionJsonTest(LOTest, LTTest, LNTest, unittest.TestCase):
    def setUp(self):
        super(CollectionJsonTest, self).setUp()

        with open('./fixtures/users.collection.json', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET,
                                   'http://example.com/users/',
                                   body=fixture.read(),
                                   content_type='application/vnd.collection+json')

        with open('./fixtures/fiona.collection.json', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET,
                                   'http://example.com/users/fiona',
                                   body=fixture.read(),
                                   content_type='application/vnd.collection+json')

        with open('./fixtures/dennis.collection.json', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET,
                                   'http://example.com/users/dennis',
                                   body=fixture.read(),
                                   content_type='application/vnd.collection+json')

        with open('./fixtures/results.collection.json', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET,
                                   'http://example.com/users/search?q=fiona',
                                   body=fixture.read(),
                                   content_type='application/vnd.collection+json',
                                   match_querystring=True)

        httpretty.register_uri(httpretty.POST,
                               'http://example.com/users',
                               status=201,
                               location='http://example.com/users/dennis')

