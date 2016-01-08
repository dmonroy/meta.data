import os
import sys
from functools import lru_cache

import yaml
from attrdict import AttrDict

DEFAULT_DATABASE = 'psycopg2+postgresql://postgres@localhost:5432/metadb'

if sys.argv[0].endswith('/py.test'):
    DATABASE_URL = '{}_test_{}{}{}'.format(
        DEFAULT_DATABASE,
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
    )
    DATABASE_POOL_MIN = 1
    DATABASE_POOL_MAX = 1
else:  # pragma: no cover
    DATABASE_URL = os.getenv('DATABASE_URL', DEFAULT_DATABASE)
    DATABASE_POOL_MIN = int(os.getenv('DATABASE_POOL_MIN', 1))
    DATABASE_POOL_MAX = int(os.getenv('DATABASE_POOL_MAX', 10))


BASE_SETTINGS = dict(
    db_url=DATABASE_URL,
    db_pool_min=DATABASE_POOL_MIN,
    db_pool_max=DATABASE_POOL_MAX
)


@lru_cache()
def cached_settings(settings):
    settings = dict(settings)

    if 'APP_SETTINGS_YAML' in os.environ:  # pragma: no cover
        with open(os.getenv('APP_SETTINGS_YAML')) as f:
            settings.update(yaml.safe_load(f))

    return AttrDict(settings)


def get_settings(base=None):
    base = base or BASE_SETTINGS
    return cached_settings(frozenset(base.items()))
