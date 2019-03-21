import json
from operator import itemgetter
from tabulate import tabulate

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
            groups, _ = repository.group_tags()

            tags_date = []
            for key in groups:
                tags_date.append([
                    [img.tag for img in groups[key]],
                    groups[key][0].get_date()
                ])
            tags_date_desc = sorted(tags_date, key=itemgetter(1), reverse=True)

            if json_output:
                res = json.dumps({
                    'result': [{
                        'tags': tdd[0],
                        'date': self.date2str(tdd[1])
                    } for tdd in tags_date_desc]
                })
            else:
                res = tabulate(
                    [
                        [','.join(tdd[0]), self.date2str(tdd[1])]
                        for tdd in tags_date_desc
                    ],
                    headers=['Tags', 'Date']
                )
        except DRegCliException as e:
            res = str(e)
            if json_output:
                res = json.dumps({'error': res})
        print(res)
