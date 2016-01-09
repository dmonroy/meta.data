from aiohttp import request

import meta.data

from chilero.web.test import WebTestCase, asynctest


def test_imports():
    # It doesn't fails when importing meta.data
    import meta.data


class TestMeta(WebTestCase):
    routes = meta.data.routes

    @asynctest
    def test_index(self):
        resp = yield from request(
            'GET', self.full_url('/'), loop=self.loop,
        )

        self.assertEqual(resp.status,200)
        resp.close()