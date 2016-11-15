import unittest
import httpretty
from .hfactors import LTTest


class TurtleTest(LTTest, unittest.TestCase):
    def setUp(self):
        super(TurtleTest, self).setUp()

        with open('./fixtures/fiona.turtle', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET,
                                   'http://example.com/users/fiona',
                                   body=fixture.read(),
                                   content_type='text/turtle')

        with open('./fixtures/users.turtle', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET, 'http://example.com/users/',
                                   body=fixture.read(),
                                   content_type='text/turtle')

        with open('./fixtures/results.turtle', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET,
                                   'http://example.com/users/search?q=fiona',
                                   body=fixture.read(),
                                   content_type='text/turtle',
                                   match_querystring=True)
