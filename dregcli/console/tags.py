import json

from .handler import CommandHandler
from dregcli.dregcli import DRegCliException, Repository


class TagsCommandHandler(CommandHandler):
    class Meta:
        command = "tags"

    @classmethod
    def set_parser(cls, subparsers):
        subparser_tags = subparsers.add_parser(
            'tags', help='List repository tags'
        )
        subparser_tags.add_argument(
            'url',
            help='Url in the form protocol://host:port, '
                 'example: http://localhost:5001'
        )
        subparser_tags.add_argument(
            'repo',
            help='Repository, example: library/alpine'
        )
        subparser_tags.add_argument(
            '-j', '--json',
            action='store_true',
            help='Json output'
        )
        subparser_tags.set_defaults(
            func=lambda args: cls().run(
                args.url, args.repo, args.json,
                user=args.user
            )
        )
        return subparser_tags

    def run(self, url, repo, json_output, user=False):
        super().run(url, json_output, user=user)

        try:
            repository = Repository(self.client, repo)
            images = repository.get_tags_by_date()

            if json_output:
                res = json.dumps({
                    'result': [
                        {
                            'tag': image['image'].tag,
                            'date': self.date2str(image['data'])
                        } for image in images
                    ]
                })
            else:
                res = "\n".join([
                    "{tag}\t\t({dt})".format(
                        tag=t,
                        dt=self.date2str(dates[t])
                    ) for t in tags
                ])
        except DRegCliException as e:
            res = str(e)
            if json_output:
                res = json.dumps({'error': res})
        print(res)
