import unittest
from rdflib import URIRef, Literal
import hyperspace
import responses


class MicrodataTest(unittest.TestCase):

    def setUp(self):
        responses.start()

        with open('./fixtures/users.html', 'rb') as fixture:
            responses.add(responses.GET, 'http://example.com/users/',
                          body=fixture.read(), status=200,
                          content_type='text/html')

        with open('./fixtures/fiona.html', 'rb') as fixture:
            responses.add(responses.GET, 'http://example.com/users/fiona',
                          body=fixture.read(), status=200,
                          content_type='text/html')

    def tearDown(self):
        responses.stop()
        responses.reset()

    def test_finds_itemscope_with_basic_attributes(self):
        # Given
        fact = (URIRef('http://example.com/users/fiona#id'),
                URIRef('http://schema.org/name'),
                Literal('Fiona Bennett'))
        # When
        page = hyperspace.jump('http://example.com/users/fiona')
        # Then
        self.assertIn(fact, page.data)

    def test_finds_link_in_page(self):
        # When - We visit the users list page
        page = hyperspace.jump('http://example.com/users/')
        # Then - We should find there are some "user" links
        print page.links
        self.assertIn('user', page.links)

    def test_follows_links(self):
        # Given - Information we know should be held about a user
        fact = (URIRef('http://example.com/users/fiona#id'),
                URIRef('http://schema.org/name'),
                Literal('Fiona Bennett'))
        # When - We visit the users list page
        page = hyperspace.jump('http://example.com/users/')
        # And - Follow the link to the user in question
        page = page.links['user'][0].follow()
        # Then - We should find a known fact about that user
        self.assertIn(fact, page.data)



if __name__ == '__main__':
    unittest.main()
