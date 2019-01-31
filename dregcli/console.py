import argparse
import json

from dregcli.dregcli import DRegCliException, Client, Repository


class CommandHandler(object):
    def __init__(self):
        self.client = None

    def run(self, url, json_output):
        if not json_output:
            print(self.Meta.command)
        self.client = Client(url, verbose=not json_output)


class RepositoriesCommandHandler(CommandHandler):
    class Meta:
        command = "reps"

    def run(self, url, json_output):
        super().run(url, json_output)

        try:
            repositories = list(map(str, self.client.repositories()))
            if json_output:
                res = json.dumps({"result": repositories})
            else:
                res = ", ".join(repositories)
        except DRegCliException as e:
            res = str(e)
            if json_output:
                res = json.dumps({'error': res})
        print(res)


class TagsCommandHandler(CommandHandler):
    class Meta:
        command = "tags"

    def run(self, url, repo, json_output):
        super().run(url, json_output)

        try:
            repository = Repository(self.client, repo)
            tags = list(map(str, repository.tags()))
            if json_output:
                res = json.dumps({"result": tags})
            else:
                res = ", ".join(tags)
        except DRegCliException as e:
            res = str(e)
            if json_output:
                res = json.dumps({'error': res})
        print(res)


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
    subparser_repositories.add_argument(
        '-j', '--json',
        action='store_true',
        help='Json output'
    )
    subparser_repositories.set_defaults(
        func=lambda args: RepositoriesCommandHandler().run(args.url, args.json)
    )

    subparser_tags = subparsers.add_parser(
        'tags', help='List repositories'
    )
    subparser_tags.add_argument(
        'url',
        help='Url in the form protocol://host:port '
             'example: http://localhost:5001'
    )
    subparser_tags.add_argument(
        'repo',
        help='Repository '
             'example: library/alpine'
    )
    subparser_tags.add_argument(
        '-j', '--json',
        action='store_true',
        help='Json output'
    )
    subparser_tags.set_defaults(
        func=lambda args: TagsCommandHandler().run(
            args.url, args.repo, args.json)
    )

    arguments = parser.parse_args()
    if hasattr(arguments, 'func'):
        arguments.func(arguments)
    else:
        parser.print_help()
