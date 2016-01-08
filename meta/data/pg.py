import asyncio
import os
from urllib.parse import urlsplit

import aiopg
from meta.data.settings import get_settings
from schema_migrations import MigrationController

settings = get_settings()


def parse_pgurl(url):
    """Converts the database url into a dictionary."""

    parsed = urlsplit(url)

    return {
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path.lstrip('/'),
        'host': parsed.hostname,
        'port': parsed.port,
    }


@asyncio.coroutine
def create_pool():  # pragma: no cover
    """Creates a connection pool to the database."""

    pool = yield from aiopg.create_pool(
        minsize=settings.db_pool_min,
        maxsize=settings.db_pool_max,
        **parse_pgurl(settings.db_url)
    )

    return pool


def create_database():  # pragma: no cover
    """Creates the database, runs the migrations."""

    import psycopg2  # isort:skip
    settings = get_settings()

    dbdata = parse_pgurl(settings.db_url)
    pg_dbdata = dbdata.copy()
    pg_dbdata['database'] = 'postgres'
    conn = psycopg2.connect(**pg_dbdata)
    conn.set_isolation_level(0)
    cur = conn.cursor()

    cur.execute('CREATE DATABASE {}'.format(dbdata['database']))
    cur.close()
    conn.close()

    conn = psycopg2.connect(**dbdata)
    conn.set_isolation_level(0)
    cur = conn.cursor()

    cur.close()
    conn.close()

    run_migrations()


def drop_database():  # pragma: no cover
    """Drops the existing database."""

    import psycopg2  # isort:skip
    settings = get_settings()

    dbdata = parse_pgurl(settings.db_url)
    pg_dbdata = dbdata.copy()
    pg_dbdata['database'] = 'postgres'
    conn = psycopg2.connect(**pg_dbdata)
    conn.set_isolation_level(0)
    cur = conn.cursor()

    cur.execute('DROP DATABASE IF EXISTS {}'.format(dbdata['database']))
    cur.close()
    conn.close()


def run_migrations():  # pragma: no cover
    """Executes all the migrations in the database."""

    mc = MigrationController(
        databases=dict(ocret=settings.db_url),
        groups=dict(
            meta='meta/data/migrations'
        )
    )

    mc.migrate()
