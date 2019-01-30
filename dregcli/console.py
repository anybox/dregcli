import argparse


class CommandHandler(object):
    def run(self, args):
        print(self.Meta.command)


class RepositoriesCommandHandler(CommandHandler):
    class Meta:
        command = "reps"

    def run(self, args):
        super().run(args)


def main():
    parser = argparse.ArgumentParser(
        prog="dregcli",
        description="Docker registry API v2 client",
    )

    subparsers = parser.add_subparsers(help='sub-commands')

    subparser_repositories = subparsers.add_parser(
        'reps', help='List repositories'
    )
    subparser_repositories.set_defaults(
        func=lambda args: RepositoriesCommandHandler().run(args)
    )

    arguments = parser.parse_args()
    if hasattr(arguments, 'func'):
        arguments.func(arguments)
    else:
        parser.print_help()
