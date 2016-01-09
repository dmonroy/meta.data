import psycopg2
from psycopg2._json import Json
from pytest import fixture

from meta.data.pg import parse_pgurl
from meta.data.settings import get_settings


@fixture(scope='module')
def settings():
    return get_settings()


@fixture(scope='module')
def conn(request, settings):

    db_data = parse_pgurl(settings.db_url)
    _conn = psycopg2.connect(**db_data)

    def fin():
        _conn.close()
    request.addfinalizer(fin)
    return _conn


def test_insert(conn):
    data = dict(
        source='test_insert',
        tags=['test', 'insert']
    )
    c = conn.cursor()
    c.execute("insert into meta (data) values (%s)", (Json(data),))
    c.execute("select count(1) from meta where data ->> 'source' = 'test_insert'")
    assert c.fetchone()[0] == 1
