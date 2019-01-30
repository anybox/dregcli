import argparse

from dregcli.dregcli import DRegCliException, Client, Repository


class CommandHandler(object):
    def run(self):
        print(self.Meta.command)


class RepositoriesCommandHandler(CommandHandler):
    class Meta:
        command = "reps"

    def run(self, url):
        super().run()
        print(
            ", ".join(
                map(str, Client(url, verbose=True).repositories())
            )
        )


def main():
    parser = argparse.ArgumentParser(
        prog="dregcli",
        description="Docker registry API v2 client",
    )

    subparsers = parser.add_subparsers(help='sub-commands')

    subparser_repositories = subparsers.add_parser(
        'reps', help='List repositories'
    )
    subparser_repositories.add_argument(
        'url',
        help='Url in the form protocol://host:port '
             'example: http://localhost:5001'
    )
    subparser_repositories.set_defaults(
        func=lambda args: RepositoriesCommandHandler().run(args.url)
    )

    arguments = parser.parse_args()
    if hasattr(arguments, 'func'):
        arguments.func(arguments)
    else:
        parser.print_help()
