import datetime
import json

from .handler import CommandHandler
from dregcli.dregcli import DRegCliException, Repository, Tools


class GarbageCommandHandler(CommandHandler):
    class Meta:
        command = "garbage"

    def __init__(self):
        super().__init__()
        self.dry_run = False

    @classmethod
    def set_parser(cls, subparsers):
        subparser_garbage = subparsers.add_parser(
            'garbage', help='garbage image tags'
        )

        subparser_garbage.add_argument(
            'url',
            help="Url in the form protocol://host:port\n"
                 "example: http://localhost:5001"
        )
        subparser_garbage.add_argument(
            'repo',
            help='Repository, example: library/alpine'
        )
        subparser_garbage.add_argument(
            '-y', '--yes',
            action='store_true',
            help="Force yes, no confirmation\n"
                 "WARNING: proceed with caution and particulary with --all"
        )
        subparser_garbage.add_argument(
            '-n', '--null',
            action='store_true',
            help='Dryrun. '
                 'Do no run actions and feedbacks actions that will be done'
        )
        subparser_garbage.add_argument(
            '-j', '--json',
            action='store_true',
            help='Json output'
        )
        subparser_garbage.add_argument(
            '-a', '--all',
            action='store_true',
            help='WARNING: delete all image'
        )
        subparser_garbage.add_argument(
            '--from-count',
            type=int,
            help="delete from count tags\n"
                 "--from-count=11 to keep last 10 tags"
        )
        subparser_garbage.add_argument(
            '--from-date',
            type=str,
            help="delete from date\n"
                 "--from-date=2018-06-30 to keep tags from 2018-07-01\n"
                 "--from-date=2018-06-30 13:59:59"
                 " to keep tags from 2018-06-30 14:00:00 (2:00 PM)"
        )
        subparser_garbage.add_argument(
            '--include-layer-single-tag',
            type=str,
            help="to use in conjonction with from-count or from-date.\n"
                 'delete from date/position, '
                 "layers with only a single tag left\n"
                 "that single tag matching a given regexp.\n"
                 "exemple: delete old previous to 2018-07-01 commit-tags\n"
                 '--from-date=2018-06-30 '
                 '--include-layer-single-tag="^master-[0-9a-f]{40}-[0-9]\{4\}"'
                 "\nexemple: delete old commit-tags since 21th\n"
                 '--from-count=21 '
                 '--include-layer-single-tag="^master-[0-9a-f]{40}-[0-9]\{4\}"'
        )
        subparser_garbage.add_argument(
            '--include',
            type=str,
            help="delete tags including python regexp\n"
                 '--include="^staging-[0-9]\{4\}"'
        )
        subparser_garbage.add_argument(
            '--exclude',
            type=str,
            help="delete tags excluding python regexp\n"
                 "if regexp does not select anything, exclude does nothing "
                 "(no implicit --all)\n"
                 '--exclude="^stable-[0-9]\{4\}"'
        )

        subparser_garbage.set_defaults(
            func=lambda args: GarbageCommandHandler().run(
                args.url, args.repo, args.json,
                user=args.user,
                dry_run=args.null,
                yes=args.yes,
                all=args.all,
                from_count=args.from_count or 0,
                from_date=args.from_date or 0,
                include_layer_single_tag=args.include_layer_single_tag or '',
                include=args.include and args.include.strip("\"'") or '',
                exclude=args.exclude and args.exclude.strip("\"'") or '',
            )
        )
        return subparser_garbage

    def run(
        self,
        url,
        repo,
        json_output,
        dry_run=False,
        yes=False,
        user=False,
        all=False,
        from_count=0,
        from_date=0,
        include_layer_single_tag='',
        include='',
        exclude=''
    ):
        super().run(url, json_output, user=user)
        self.dry_run = dry_run

        options_on = [
            all,
            bool(from_count),
            bool(from_date),
            bool(include),
            bool(exclude)
        ]
        options_on_count = 0
        for oo in options_on:
            if oo:
                options_on_count += 1

        err_msg = ''
        if options_on_count == 0:
            err_msg = 'no option selected (criteria). --delete aborted'
        elif options_on_count > 1:
            err_msg = '--all, --from_count, --from_date, --include, ' \
                '--exclude are exclusives. --delete aborted'

        if include_layer_single_tag:
            if not from_count and not from_date:
                err_msg = '--include_layer_single_tag must be used with ' \
                          '--from_count or from_date'

        if not err_msg and from_date:
            if len(from_date) == 26:  # with hms
                from_date = datetime.datetime.strptime(from_date,
                                                       '%Y-%m-%d %H:%M:%S.%f')
            elif len(from_date) == 19:  # with hours
                from_date = datetime.datetime.strptime(from_date,
                                                       '%Y-%m-%d %H:%M:%S')
            elif len(from_date) == 10:  # day only
                from_date = datetime.datetime.strptime(from_date, '%Y-%m-%d')
                from_date = from_date_dt.replace(hour=0, minute=0, second=0)
            else:
                err_msg = '--from-date invalide date format. --delete aborted'

        if err_msg:
            msg = '--from-date invalide date format. --delete aborted'
            if json_output:
                err_msg = json.dumps({'error': err_msg})
            print(err_msg)
            return

        deleted = []
        try:
            repository = Repository(self.client, repo)

            if all:
                deleted = self._all(repository)
            elif include:
                deleted = self._include_exclude(repository, include)
            elif exclude:
                deleted = self._include_exclude(repository, exclude,
                                                exclude=True)
            elif from_count:
                if include_layer_single_tag:
                    deleted = self._from_count_onlylayer_single_tag(
                        repository,
                        from_count,
                        include_layer_single_tag
                    )
                else:
                    deleted = self._from_count(repository, from_count)
            elif from_date:
                deleted = self._from_date(repository, from_date)

            if json_output:
                res = json.dumps({'result': deleted})
            else:
                res = "\n".join(deleted)
        except DRegCliException as e:
            res = str(e)
            if json_output:
                res = json.dumps({'error': res})
        print(res)
        return deleted

    def _delete_image(self, repository, tag):
        if not self.dry_run:
            try:
                repository.image(tag).delete()
            except DRegCliException as e:
                if str(e) != 'Status code error 404':
                    raise e
                # 404 tolerated during image(tag) or delete():
                # tag in common with same commit tag
                # and already deleted by previous tag
                # exemple:
                # master-6da64c000cf59c30e4841371e0dac3dd02c31aaa-1385 old-prod
                # representing same image

    def _all(self, repository):
        tags = repository.tags()

        deleted = []
        for tag in tags:
            self._delete_image(repository, tag)
            deleted.append(tag)

        return deleted

    def _include_exclude(self, repository, regexp_expr, exclude=False):
        tags = Tools.search(repository.tags(), regexp_expr, exclude=exclude)

        deleted = []
        for tag in tags:
            self._delete_image(repository, tag)
            deleted.append(tag)

        return deleted

    def _from_count(self, repository, from_count):
        deleted = []

        if from_count:
            tags = repository.get_tags_by_date()
            if from_count < len(tags):
                to_delete = tags[from_count - 1:]
                for tag_data in to_delete:
                    self._delete_image(repository, tag_data['tag'])
                    deleted.append(tag_data['tag'])

        return deleted

    def _from_count_onlylayer_single_tag(
        self,
        repository,
        from_count,
        only_layer_single_tag_regexp
    ):
        deleted = []

        groups, tags = repository.group_tags()

        # grab layers concerned by a single tag
        # and that matches only_layer_single_tag_regexp
        to_delete_tags = []
        for key in groups:
            if len(groups[key]) == 1:  # concerned by a single tag
                tag = groups[key][0].tag
                if Tools.search([tag], only_layer_single_tag_regexp):
                    to_delete_tags.append(tag)
        to_delete_tags = list(set(to_delete_tags))

        # delete selected by date desc order
        if to_delete_tags:
            for tag_data in tags:
                if tag_data['tag'] in to_delete_tags:
                    self._delete_image(repository, tag_data['tag'])
                    deleted.append(tag_data['tag'])

        return deleted

    def _from_date(self, repository, from_date):
        deleted = []

        if from_date:
            for tag_data in repository.get_tags_by_date():
                if tag_data['date'] <= from_date:  # from desc order
                    self._delete_image(repository, tag_data['tag'])
                    deleted.append(tag_data['tag'])

        return deleted
