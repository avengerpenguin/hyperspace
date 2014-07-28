import unittest

from rdflib import URIRef, Literal
import hyperspace
import responses


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
        responses.start()

    def tearDown(self):
        responses.stop()
        responses.reset()

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
        # Then - We should find the page URL has changed
        self.assertEqual('http://example.com/users/fiona', page.url)


class HTMLTest(LOTest):
    def setUp(self):
        super(HTMLTest, self).setUp()

        with open('./fixtures/users.html', 'rb') as fixture:
            responses.add(responses.GET, 'http://example.com/users/',
                          body=fixture.read(), status=200,
                          content_type='text/html')

        with open('./fixtures/fiona.html', 'rb') as fixture:
            responses.add(responses.GET, 'http://example.com/users/fiona',
                          body=fixture.read(), status=200,
                          content_type='text/html')


class HydraTest(HypermediaBaseTest):
    def setUp(self):
        super(HydraTest, self).setUp()

        with open('./fixtures/fiona.hydra', 'rb') as fixture:
            responses.add(responses.GET, 'http://example.com/users/fiona',
                          body=fixture.read(), status=200,
                          content_type='application/ld+json')


if __name__ == '__main__':
    unittest.main()
