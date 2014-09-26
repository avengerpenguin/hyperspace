import unittest
import httpretty
from rdflib import URIRef, Literal
import hyperspace
from . import HypermediaBaseTest
from .hfactors import LOTest, LTTest, LNTest


class TurtleTest(HypermediaBaseTest, unittest.TestCase):
    def setUp(self):
        super(TurtleTest, self).setUp()

        with open('./fixtures/fiona.turtle', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET, 'http://example.com/users/fiona',
                                   body=fixture.read(),
                                   content_type='text/turtle')
