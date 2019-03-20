import json

from .handler import CommandHandler
from dregcli.dregcli import DRegCliException, Repository


class ImagesCommandHandler(CommandHandler):
    class Meta:
        command = "images"

    @classmethod
    def set_parser(cls, subparsers):
        subparser_image = subparsers.add_parser(
            cls.Meta.command,
            help='list images by common tags'
        )

        subparser_image.add_argument(
            'url',
            help="Url in the form protocol://host:port\n"
                 'example: http://localhost:5001'
        )
        subparser_image.add_argument(
            'repo',
            help='Repository, example: library/alpine'
        )
        subparser_image.add_argument(
            '-j', '--json',
            action='store_true',
            help='Json output'
        )

        subparser_image.set_defaults(
            func=lambda args: cls().run(
                args.url, args.repo, args.json,
                user=args.user
            )
        )
        return subparser_image

    def run(self, url, repo, json_output, user=False):
        super().run(url, json_output, user=user)

        try:
            repository = Repository(self.client, repo)
            image = repository.image(tag)
            res = ''
        except DRegCliException as e:
            res = str(e)
            if json_output:
                res = json.dumps({'error': res})
        print(res)
