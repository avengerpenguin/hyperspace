import unittest
import httpretty
from . import HypermediaBaseTest


class TurtleTest(HypermediaBaseTest, unittest.TestCase):
    def setUp(self):
        super(TurtleTest, self).setUp()

        with open('./fixtures/fiona.turtle', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET, 'http://example.com/users/fiona',
                                   body=fixture.read(),
                                   content_type='text/turtle')
