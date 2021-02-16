import unittest

import httpretty

from .hfactors import LOTest


class HydraTest(LOTest, unittest.TestCase):
    def setUp(self):
        super().setUp()

        with open("./fixtures/context.jsonld") as context:
            httpretty.register_uri(
                httpretty.GET,
                "http://www.w3.org/ns/hydra/context.jsonld",
                body=context.read(),
            )

        with open("./fixtures/users.hydra", "rb") as fixture:
            httpretty.register_uri(
                httpretty.GET,
                "http://example.com/users/",
                body=fixture.read(),
                content_type="application/ld+json",
            )

        with open("./fixtures/fiona.hydra", "rb") as fixture:
            httpretty.register_uri(
                httpretty.GET,
                "http://example.com/users/fiona",
                body=fixture.read(),
                content_type="application/ld+json",
            )
