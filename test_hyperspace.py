import unittest
from rdflib import URIRef, Literal
from hyperspace import parse
import os


class MicrodataTest(unittest.TestCase):
    def test_finds_itemscope_with_basic_attributes(self):
        print os.getcwd()
        with open('./fixtures/microdata.html', 'rb') as fixture:
            page = parse(fixture.read())

        fact = (URIRef('http://example.com/fiona'), URIRef('http://schema.org/name'), Literal('Fiona Bennett'))

        self.assertIn(fact, page.data)

if __name__ == '__main__':
    unittest.main()
