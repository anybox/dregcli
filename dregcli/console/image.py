import json

from .handler import CommandHandler
from dregcli.dregcli import DRegCliException, Repository


class ImageCommandHandler(CommandHandler):
    class Meta:
        command = "image"

    @classmethod
    def set_parser(cls, subparsers):
        subparser_image = subparsers.add_parser(
            'image', help='get image digest/manifest, delete image'
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
            'tag',
            help='Tag, example: 3.8'
        )
        subparser_image.add_argument(
            '-m', '--manifest',
            action='store_true',
            help='Output image manifest'
        )
        subparser_image.add_argument(
            '-j', '--json',
            action='store_true',
            help='Json output'
        )
        subparser_image.add_argument(
            '-d', '--delete',
            action='store_true',
            help='Delete image (incompatible with --manifest or --json)'
        )
        subparser_image.add_argument(
            '-y', '--yes',
            action='store_true',
            help='Always yes. Be careful with delete'
        )

        subparser_image.set_defaults(
            func=lambda args: cls().run(
                args.url, args.repo, args.tag, args.manifest, args.json,
                args.delete, args.yes,
                user=args.user
            )
        )
        return subparser_image

    def run(self, url, repo, tag, manifest, json_output, delete, yes,
            user=False):
        super().run(url, json_output, user=user)

        if delete and manifest:
            print('--delete is incompatible with --manifest')
            return

        try:
            repository = Repository(self.client, repo)
            image = repository.image(tag)

            if delete:
                confirm = yes and 'yes' or \
                    input("Please type 'yes' word to confirm")
                if confirm == 'yes':
                    image.delete()
                    if json_output:
                        res = json.dumps({
                            'result': {
                                'digest': image.digest,
                                'message': 'deleted',
                            }
                        })
                    else:
                        res = "{digest}\ndeleted".format(digest=image.digest)
                else:
                    return
            else:
                if json_output:
                    res = {'result': {'digest': image.digest}}
                    if manifest:
                        res['result']['manifest'] = image.data
                    res = json.dumps(res)
                else:
                    res = image.digest
                    if manifest:  # add manifest json in std out
                        res += "\n" + json.dumps(image.data)
        except DRegCliException as e:
            res = str(e)
            if json_output:
                res = json.dumps({'error': res})
        print(res)
