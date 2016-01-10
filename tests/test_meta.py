import json

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

        self.assertEqual(resp.status, 200)
        resp.close()

    @asynctest
    def test_empty_create(self):
        resp = yield from request(
            'POST', self.full_url('/'), loop=self.loop
        )

        self.assertEqual(resp.status, 400)

    @asynctest
    def test_wrong_create(self):
        data = dict(
            dat=dict(a=1, b=2)
        )
        resp = yield from request(
            'POST', self.full_url('/'), loop=self.loop, data=json.dumps(data)
        )

        self.assertEqual(resp.status, 400)

    @asynctest
    def test_valid_create(self):
        data = dict(
            data=dict(a=1, b=2)
        )
        resp = yield from request(
            'POST', self.full_url('/'), loop=self.loop, data=json.dumps(data)
        )

        self.assertEqual(resp.status, 201)
        location = resp.headers['Location']

        resp2 = yield from request(
            'GET', self.full_url(location), loop=self.loop
        )

        self.assertEqual(resp2.status, 200)
        jresp = yield from resp2.json()

        body = jresp['body']
        self.assertIn('id', body)
        self.assertIn('data', body)
        self.assertIn('created', body)

        self.assertEqual(body['data'], data['data'])
