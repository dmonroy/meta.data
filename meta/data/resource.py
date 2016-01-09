import asyncio
import datetime
import json
import os

from chilero import web
from meta.data.pg import create_pool


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime) \
                or isinstance(obj, datetime.date):

            return obj.isoformat(sep=' ')

        return None


class PGResource(web.Resource):

    LIST_QUERY = None
    DETAIL_QUERY = None
    COUNT_QUERY = None
    ORDER_BY = 'id'

    encoder_class = JSONEncoder

    @property
    def offset(self):
        return int(self.request.GET.get('offset') or 0)

    @property
    def limit(self):
        return int(self.request.GET.get('limit') or 0) \
            or int(os.environ.get('PAGE_LIMIT') or 0) \
            or 20

    @property
    def prev_offset(self):
        if self.limit <= 0:
            return 0

        offset = self.offset - self.limit
        return offset if offset > 0 else 0

    @property
    def next_offset(self):
        if self.limit <= 0:
            return 0

        return self.offset + self.limit

    def _build_url(self, args):
        return '{}?{}'.format(
            self.get_full_url('/'),
            '&'.join(
                ['{}={}'.format(k, v) for k, v in args.items()]
            )
        )

    def next_url(self, conditions, count):
        if self.next_offset <= self.offset or self.next_offset >= count:
            return None

        args = conditions.copy()
        args.update(
            dict(
                offset=self.next_offset,
                limit=self.limit
            )
        )
        return self._build_url(args)

    def prev_url(self, conditions):
        if self.prev_offset >= self.offset:
            return None

        args = conditions.copy()
        args.update(
            dict(
                offset=self.prev_offset,
                limit=self.limit
            )
        )
        return self._build_url(args)

    def set_limit(self, query):
        if self.offset > 0:
            query = '{query} OFFSET {offset}'.format(
                query=query, offset=self.offset
            )

        return query

    def set_offset(self, query):
        if self.limit > 0:
            query = '{query} LIMIT {limit}'.format(
                query=query, limit=self.limit
            )

        return query

    def serialize(self, obj):
        return obj

    @asyncio.coroutine
    def get_pool(self):
        if not hasattr(self, 'db_pool'):
            self.db_pool = yield from create_pool()

        return self.db_pool

    @asyncio.coroutine
    def get_cursor(self):
        pool = yield from self.get_pool()
        cursor = yield from pool.cursor()
        return cursor

    @asyncio.coroutine
    def get_count(self, conditions=None):
        assert self.COUNT_QUERY is not None, 'LIST_QUERY is not specified'
        query = self.COUNT_QUERY

        args = None
        if conditions:
            fields = conditions.keys()
            filters = ', '.join(['{}=%s'.format(f) for f in fields])
            query = '{query} WHERE {filters}'.format(
                query=query, filters=filters
            )
            args = tuple([conditions[f] for f in fields])

        with (yield from self.get_cursor()) as cur:
            if args:
                yield from cur.execute(query, args)
            else:
                yield from cur.execute(query)

            for row in (yield from cur.fetchall()):
                return row[0]

    @asyncio.coroutine
    def do_index(self, conditions=None):
        assert self.LIST_QUERY is not None, 'LIST_QUERY is not specified'
        query = self.LIST_QUERY
        conditions = conditions or {}
        args = None
        if conditions:
            fields = conditions.keys()
            filters = ', '.join(['{}=%s'.format(f) for f in fields])
            query = '{query} WHERE {filters}'.format(
                query=query, filters=filters
            )
            args = tuple([conditions[f] for f in fields])

        query = self.set_offset(self.set_limit(query))

        count = yield from self.get_count(conditions)
        response = dict(
            self=self.get_self_url(),
            meta=dict(
                offset=self.offset,
                limit=self.limit,
                next=self.next_url(conditions, count),
                prev=self.prev_url(conditions),
                count=count
            ),
            index=[]
        )

        with (yield from self.get_cursor()) as cur:
            yield from cur.execute(query, args)
            for record in (yield from cur.fetchall()):
                response['index'].append(self.serialize(record))

        response['meta']['length'] = len(response['index'])

        return response


class Resource(PGResource):
    COUNT_QUERY = 'SELECT count(1) FROM meta'
    LIST_QUERY = 'SELECT * FROM meta'
    DETAIL_QUERY = LIST_QUERY

    def index(self):
        index = yield from self.do_index()
        return self.response(index)

    def serialize(self, obj):
        return dict(
            id=obj[0],
            meta=obj[1],
            created=obj[2]
        )
