import unittest
import httpretty
from rdflib import URIRef, Literal
import hyperspace
from . import HypermediaBaseTest
from .hfactors import LOTest, LTTest, LNTest


class HTMLTest(LOTest, LTTest, LNTest, unittest.TestCase):
    def setUp(self):
        super(HTMLTest, self).setUp()

        with open('./fixtures/users.html', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET,
                                   'http://example.com/users/',
                                   body=fixture.read(),
                                   content_type='text/html')

        with open('./fixtures/fiona.html', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET,
                                   'http://example.com/users/fiona',
                                   body=fixture.read(),
                                   content_type='text/html')

        with open('./fixtures/dennis.html', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET,
                                   'http://example.com/users/dennis',
                                   body=fixture.read(),
                                   content_type='text/html')

        with open('./fixtures/results.html', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET,
                                   'http://example.com/users/search?q=fiona',
                                   body=fixture.read(),
                                   content_type='text/html',
                                   match_querystring=True)

        httpretty.register_uri(httpretty.POST,
                               'http://example.com/users',
                               status=201,
                               location='http://example.com/users/dennis')

