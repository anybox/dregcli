import json

from .handler import CommandHandler
from dregcli.dregcli import DRegCliException


class RepositoriesCommandHandler(CommandHandler):
    class Meta:
        command = "reps"

    @classmethod
    def set_parser(cls, subparsers):
        subparser_repositories = subparsers.add_parser(
            'reps', help='List repositories'
        )
        subparser_repositories.add_argument(
            'url',
            help='Url in the form protocol://host:port, '
                 'example: http://localhost:5001'
        )
        subparser_repositories.add_argument(
            '-j', '--json',
            action='store_true',
            help='Json output'
        )
        subparser_repositories.set_defaults(
            func=lambda args: cls().run(args.url, args.json, user=args.user)
        )
        return subparser_repositories

    def run(self, url, json_output, user=False):
        super().run(url, json_output, user=user)

        try:
            repositories = list(map(str, self.client.repositories()))
            if json_output:
                res = json.dumps({"result": repositories})
            else:
                res = "\n".join(repositories)
        except DRegCliException as e:
            res = str(e)
            if json_output:
                res = json.dumps({'error': res})
        print(res)
