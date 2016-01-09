import argparse

from chilero import web

from meta.data import pg
from meta.data.resource import Resource

routes = [
    ['/', Resource]
]


def run():  # pragma: no cover
    web.run(web.Application, routes)


def main():  # pragma: no cover
    parser = argparse.ArgumentParser()

    commands = dict(
        create_database=pg.create_database,
        drop_database=pg.drop_database,
        migrate=pg.run_migrations,
        server=run
    )

    cmd_help = ', '.join(sorted(commands.keys()))

    parser.add_argument(
        'command',
        help=cmd_help,
        type=lambda x: commands.get(x)
    )

    args = parser.parse_args()

    if args.command is None:
        raise SystemExit(
            'Must specify one of: ' + cmd_help
        )

    args.command()

if __name__ == '__main__':  # pragma: no cover
    main()
