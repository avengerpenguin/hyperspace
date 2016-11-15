from rdflib import URIRef, Literal
import hyperspace
import httpretty
from . import HypermediaBaseTest


class LOTest(HypermediaBaseTest):
    def test_finds_link_in_page(self):
        # When - We visit the users list page
        page = hyperspace.jump('http://example.com/users/')
        # Then - We should find there are some "user" links
        self.assertIn('http://example.com/relations/user', page.links.keys())

    def test_follows_links(self):
        # Given - Information we know should be held about a user
        fact = (URIRef('http://example.com/users/fiona#id'),
                URIRef('http://schema.org/name'),
                Literal('Fiona Bennett'))
        # When - We visit the users list page
        page = hyperspace.jump('http://example.com/users/')
        # And - Follow the link to the user in question
        page = page.links['http://example.com/relations/user'][0].follow()
        # Then - We should find the page URL has changed
        self.assertEqual('http://example.com/users/fiona', page.url)


class LTTest(HypermediaBaseTest):
    def test_performs_templated_query(self):
        # Given - We are on the users home page
        page = hyperspace.jump('http://example.com/users/')
        # When - We fill in a search form on that page
        for query in page.queries:
            print(query)
        results_page = page.queries['#search'][0].build({'q': 'fiona'}).submit()
        # Then - We should get to a results page for that search
        self.assertIn('http://example.com/users/fiona',
                      [link.href for link in results_page.links])


class LNTest(HypermediaBaseTest):
    def test_sends_nonidempotent_update(self):
        # Given - We are on the users home page
        page = hyperspace.jump('http://example.com/users/')
        # When - We fill in a search form on that page
        page.templates['newuser'][0].build({'name': 'Dennis Felt'}).submit()
        # Then - A POST is received
        self.assertEqual(
            httpretty.core.httpretty.latest_requests[-2].body.decode('utf-8'),
            u'name=Dennis+Felt')

    def test_handles_redirect_after_update(self):
        fact = (URIRef('http://example.com/users/dennis#id'),
                URIRef('http://schema.org/name'),
                Literal('Dennis Felt'))
        page = hyperspace.jump('http://example.com/users/')        
        page = page.templates['newuser'][0].build(
            {'name': 'Dennis Felt'}).submit()
        # Expect to be magically redirected to the new user's page
        self.assertIn(fact, page.data)
