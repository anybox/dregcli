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
                res = ",".join(repositories)
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
                res = json.dumps({'result': tags})
            else:
                res = ",".join(tags)
        except DRegCliException as e:
            res = str(e)
            if json_output:
                res = json.dumps({'error': res})
        print(res)


class ImageCommandHandler(CommandHandler):
    class Meta:
        command = "image"

    def run(self, url, repo, tag, manifest, json_output, delete, yes):
        super().run(url, json_output)

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


class GarbageCommandHandler(CommandHandler):
    class Meta:
        command = "garbage"

    def run(self, url, repo, null, json_output):
        super().run(url, json_output)

        try:
            repository = Repository(self.client, repo)
            # TODO
            if json_output:
                res = json.dumps({'result': True})
            else:
                res = ''
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
        help='Url in the form protocol://host:port, '
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
        func=lambda args: TagsCommandHandler().run(
            args.url, args.repo, args.json)
    )

    subparser_image = subparsers.add_parser(
        'image', help='get image digest/manifest, delete image'
    )
    subparser_image.add_argument(
        'url',
        help='Url in the form protocol://host:port, '
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
        func=lambda args: ImageCommandHandler().run(
            args.url, args.repo, args.tag, args.manifest, args.json,
            args.delete, args.yes
        )
    )

    subparser_garbage = subparsers.add_parser(
        'garbage', help='garbage image tags'
    )
    subparser_garbage.add_argument(
        'url',
        help='Url in the form protocol://host:port, '
             'example: http://localhost:5001'
    )
    subparser_garbage.add_argument(
        'repo',
        help='Repository, example: library/alpine'
    )
    subparser_garbage.add_argument(
        '-n', '--null',
        action='store_true',
        help='Do no run actions and feedbacks actions that will be done'
    )
    subparser_garbage.add_argument(
        '-j', '--json',
        action='store_true',
        help='Json output'
    )
    subparser_garbage.set_defaults(
        func=lambda args: GarbageCommandHandler().run(
            args.url, args.repo, args.null, args.json
        )
    )

    arguments = parser.parse_args()
    if hasattr(arguments, 'func'):
        arguments.func(arguments)
    else:
        parser.print_help()
