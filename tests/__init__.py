import httpretty
from rdflib import Literal, URIRef

import hyperspace


class HypermediaBaseTest:
    def setUp(self):
        httpretty.enable()
        self.addCleanup(httpretty.disable)
        self.addCleanup(httpretty.reset)

    def test_finds_item_with_basic_attributes(self):
        # Given
        fact = (
            URIRef("http://example.com/users/fiona#id"),
            URIRef("http://schema.org/name"),
            Literal("Fiona Bennett"),
        )
        # When
        page = hyperspace.jump("http://example.com/users/fiona")
        # Then
        self.assertIn(fact, page.data)
