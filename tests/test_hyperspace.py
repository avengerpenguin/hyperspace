import unittest

import httpretty
from rdflib import URIRef, Literal
import hyperspace


class HypermediaBaseTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(HypermediaBaseTest, self).__init__(*args, **kwargs)
        self.helper = None

        # Kludge alert: We want this class to carry test cases without being run
        # by the unit test framework, so the `run' method is overridden to do
        # nothing.  But in order for sub-classes to be able to do something when
        # run is invoked, the constructor will rebind `run' from TestCase.
        if self.__class__ != HypermediaBaseTest:
            # Rebind `run' from the parent class.
            self.run = unittest.TestCase.run.__get__(self, self.__class__)
        else:
            self.run = lambda self, *args, **kwargs: None

    def setUp(self):
        httpretty.enable()
        self.addCleanup(httpretty.disable)
        self.addCleanup(httpretty.reset)

    def test_finds_item_with_basic_attributes(self):
        # Given
        fact = (URIRef('http://example.com/users/fiona#id'),
                URIRef('http://schema.org/name'),
                Literal('Fiona Bennett'))
        # When
        page = hyperspace.jump('http://example.com/users/fiona')
        # Then
        self.assertIn(fact, page.data)


class LOTest(HypermediaBaseTest):
    def __init__(self, *args, **kwargs):
        super(LOTest, self).__init__(*args, **kwargs)
        self.helper = None

        # Kludge alert: We want this class to carry test cases without being run
        # by the unit test framework, so the `run' method is overridden to do
        # nothing.  But in order for sub-classes to be able to do something when
        # run is invoked, the constructor will rebind `run' from TestCase.
        if self.__class__ != LOTest:
            # Rebind `run' from the parent class.
            self.run = unittest.TestCase.run.__get__(self, self.__class__)
        else:
            self.run = lambda self, *args, **kwargs: None

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
    def __init__(self, *args, **kwargs):
        super(LTTest, self).__init__(*args, **kwargs)
        self.helper = None

        # Kludge alert: We want this class to carry test cases without being run
        # by the unit test framework, so the `run' method is overridden to do
        # nothing.  But in order for sub-classes to be able to do something when
        # run is invoked, the constructor will rebind `run' from TestCase.
        if self.__class__ != LTTest:
            # Rebind `run' from the parent class.
            self.run = unittest.TestCase.run.__get__(self, self.__class__)
        else:
            self.run = lambda self, *args, **kwargs: None

    def test_performs_templated_query(self):
        # Given - We are on the users home page
        page = hyperspace.jump('http://example.com/users/')
        # When - We fill in a search form on that page
        results_page = page.queries['search'][0].build({'q': 'fiona'}).submit()
        # Then - We should get to a results page for that search
        self.assertIn('http://example.com/users/fiona', [link.href for link in results_page.links])


class LNTest(HypermediaBaseTest):
    def __init__(self, *args, **kwargs):
        super(LNTest, self).__init__(*args, **kwargs)
        self.helper = None

        # Kludge alert: We want this class to carry test cases without being run
        # by the unit test framework, so the `run' method is overridden to do
        # nothing.  But in order for sub-classes to be able to do something when
        # run is invoked, the constructor will rebind `run' from TestCase.
        if self.__class__ != LNTest:
            # Rebind `run' from the parent class.
            self.run = unittest.TestCase.run.__get__(self, self.__class__)
        else:
            self.run = lambda self, *args, **kwargs: None

    def test_sends_nonidempotent_update(self):
        # Given - We are on the users home page
        page = hyperspace.jump('http://example.com/users/')
        # When - We fill in a search form on that page
        page.templates['newuser'][0].build({'name': 'Dennis Felt'}).submit()
        # Then - A POST is received
        self.assertEqual(httpretty.core.httpretty.latest_requests[-2].body, 'name=Dennis+Felt')

    def test_handles_redirect_after_update(self):
        fact = (URIRef('http://example.com/users/dennis#id'),
                URIRef('http://schema.org/name'),
                Literal('Dennis Felt'))
        page = hyperspace.jump('http://example.com/users/')        
        page = page.templates['newuser'][0].build({'name': 'Dennis Felt'}).submit()
        # Expect to be magically redirected to the new user's page
        self.assertIn(fact, page.data)
        

class HTMLTest(LOTest, LTTest, LNTest):
    def setUp(self):
        super(HTMLTest, self).setUp()

        with open('./fixtures/users.html', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET, 'http://example.com/users/',
                               body=fixture.read(), content_type='text/html')

        with open('./fixtures/fiona.html', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET, 'http://example.com/users/fiona',
                                   body=fixture.read(), content_type='text/html')

        with open('./fixtures/dennis.html', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET, 'http://example.com/users/dennis',
                                   body=fixture.read(), content_type='text/html')

        with open('./fixtures/results.html', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET, 'http://example.com/users/search?q=fiona',
                          body=fixture.read(),
                          content_type='text/html', match_querystring=True)

        httpretty.register_uri(httpretty.POST, 'http://example.com/users',
                               status=201, location='http://example.com/users/dennis')


class HydraTest(LOTest):
    def setUp(self):
        super(HydraTest, self).setUp()

        with open('./fixtures/context.jsonld') as context:
            httpretty.register_uri(
                httpretty.GET,
                'http://www.w3.org/ns/hydra/context.jsonld',
                body=context.read())

        with open('./fixtures/users.hydra', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET, 'http://example.com/users/',
                                   body=fixture.read(),
                                   content_type='application/ld+json')

        with open('./fixtures/fiona.hydra', 'rb') as fixture:
            httpretty.register_uri(httpretty.GET, 'http://example.com/users/fiona',
                                   body=fixture.read(),
                                   content_type='application/ld+json')


if __name__ == '__main__':
    unittest.main()
