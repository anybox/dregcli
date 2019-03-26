import datetime
import json
from tabulate import tabulate

from .handler import CommandHandler
from dregcli.dregcli import DRegCliException, Repository, Tools


class DeleteCommandHandler(CommandHandler):
    class Meta:
        command = "delete"

    def __init__(self):
        super().__init__()
        self.dry_run = False

    @classmethod
    def set_parser(cls, subparsers):
        subparser_delete = subparsers.add_parser(
            cls.Meta.command,
            help="delete image tags\n"
                 "DISCLAIMER: deleting a tag shared with other tags"
                 " delete all tags on same layer"
        )

        subparser_delete.add_argument(
            'url',
            help="Url in the form protocol://host:port\n"
                 "example: http://localhost:5001"
        )
        subparser_delete.add_argument(
            'repo',
            help='Repository, example: library/alpine'
        )
        subparser_delete.add_argument(
            '-y', '--yes',
            action='store_true',
            help="Force yes, no confirmation.\n"
                 "DISCLAIMER: proceed with caution and particulary with --all"
        )
        subparser_delete.add_argument(
            '-n', '--null',
            action='store_true',
            help='Dryrun. '
                 'Do not run actions, just display actions that will be done'
        )
        subparser_delete.add_argument(
            '-j', '--json',
            action='store_true',
            help='Json output'
        )
        subparser_delete.add_argument(
            '-a', '--all',
            action='store_true',
            help='DISCLAIMER: proceed with caution, delete all image'
        )
        subparser_delete.add_argument(
            '--from-count',
            type=int,
            help="delete from count tags\n"
                 "--from-count=11 to keep last 10 tags"
        )
        subparser_delete.add_argument(
            '--from-date',
            type=str,
            help="delete from date\n"
                 "--from-date=2018-06-30 to keep tags from 2018-07-01\n"
                 "--from-date=2018-06-30 13:59:59"
                 " to keep tags from 2018-06-30 14:00:00 (2:00 PM)"
        )
        subparser_delete.add_argument(
            '--include',
            type=str,
            help="delete tags including python regexp\n"
                 '--include="^staging"'
        )
        # exclude desactivated: for layers with multiple tags,
        # deletion of an unexcluded tag could cause deletion of an excluded tag
        # subparser_delete.add_argument(
        #     '--exclude',
        #     type=str,
        #     help="delete tags excluding python regexp\n"
        #          "if regexp does not select anything, exclude does nothing "
        #          "(no implicit --all)\n"
        #          '--exclude="^stable"'
        # )
        subparser_delete.add_argument(
            '--single-tag',
            type=str,
            help="to use in conjonction with another delete option.\n"
                 "delete layers with only a single tag left\n"
                 "that single tag matching a given python regexp.\n"
                 "exemple: delete old previous commit-tags not attached"
                 " to a release tag below 2018-07-01\n"
                 '--from-date=2018-06-30 '
                 '--single-tag="^master-"'
                 "\nexemple: delete old commit-tags not attached"
                 " to a release since 21th\n"
                 '--from-count=21 '
                 '--single-tag="^master-"'
        )

        subparser_delete.set_defaults(
            func=lambda args: DeleteCommandHandler().run(
                args.url, args.repo, args.json,
                user=args.user,
                dry_run=args.null,
                yes=args.yes,
                all=args.all,
                from_count=args.from_count or 0,
                from_date=args.from_date or 0,
                single_tag=args.single_tag or '',
                include=args.include and args.include.strip("\"'") or '',
                # exclude desactivated: for layers with multiple tags,
                # deletion of an unexcluded tag could cause deletion of an
                # excluded tag
                # exclude=args.exclude and args.exclude.strip("\"'") or '',
            )
        )
        return subparser_delete

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
        single_tag='',
        include='',
        exclude=''
    ):
        super().run(url, json_output, user=user)
        self.dry_run = dry_run

        # delete options count, single_tag filter excepted
        options = [
            all,
            bool(from_count),
            bool(from_date),
            bool(include),
            bool(exclude)
        ]
        options_on_count = len([o for o in options if o])

        err_msg = ''
        if options_on_count == 0:
            err_msg = 'no option selected (criteria). delete aborted'
        elif options_on_count > 1:
            err_msg = '--all, --from_count, --from_date, --include, ' \
                '--exclude are exclusives. --delete aborted'

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
            if json_output:
                err_msg = json.dumps({'error': err_msg})
            print(err_msg)
            return

        deleted = []
        try:
            repository = Repository(self.client, repo)

            if all:
                deleted = self._all(repository, single_tag=single_tag)
            elif include:
                deleted = self._include_exclude(
                    repository,
                    include,
                    single_tag=single_tag
                )
            # exclude desactivated: for layers with multiple tags,
            # deletion of an unexcluded tag could cause deletion of an
            # excluded tag
            # elif exclude:
            #     deleted = self._include_exclude(
            #         repository,
            #         exclude,
            #         single_tag=single_tag,
            #         exclude=True
            #     )
            elif from_count:
                    deleted = self._from_count(
                        repository,
                        from_count,
                        single_tag=single_tag
                    )
            elif from_date:
                deleted = self._from_date(
                    repository,
                    from_date,
                    single_tag=single_tag
                )

            # display delete result
            # deleted: [[tag, ['cotag1',], ...], see self._parse_codeleted
            if json_output:
                res = json.dumps({
                    'result': [
                        {'tag': d[0], 'cotags': d[1]} for d in deleted
                    ]
                })
            else:
                res = tabulate(
                    [[d[0], ", ".join(d[1])] for d in deleted],
                    headers=['Tag', 'Cotags (deleted too)']
                )
        except DRegCliException as e:
            res = str(e)
            if json_output:
                res = json.dumps({'error': res})
        print(res)
        return [d[0] for d in deleted]  # return only deleted tags

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

    def _get_tags(self, repository, single_tag):
        """
        :single_tag: single_tag regexp (layer with unique tag to keep on)
        :rtype tuple
        :return tags (tags data by date), filtered_tags (list of filtered tags)
        """
        # group tags: that will add a 'cotags' entry to tags items,
        # see Repository.group_tags
        groups, tags = repository.group_tags()

        if single_tag:
            # grab layers concerned by a single tag
            # and that matches only_layer_single_tag_regexp
            filtered_tags = repository.group_tags_layer_single_tags_filter(
                groups,
                single_tag
            )
        else:
            filtered_tags = False

        return tags, filtered_tags

    def _parse_codeleted(self, deleted, tags):
        """
        deduced cotags deleted by tag deletion (tags on same layer)
        :rtype list
        :return [[tag, ['cotag1',], ...]
        """
        def search_tag_data(tag):
            for tag_data in tags:
                if tag_data['tag'] == tag:
                    return tag_data
            return None

        new_deleted = []

        for deleted_tag in deleted:
            # TODO improve repository.group_tags() could return a dict
            # in its return tuple, tag data dict with tag name key
            tag_data = search_tag_data(deleted_tag)

            cotags = tag_data and tag_data['cotags'] or []
            cotags = [ct for ct in cotags]
            new_deleted.append([deleted_tag, cotags])

        return new_deleted

    def _all(self, repository, single_tag=''):
        tags, filtered_tags, _ = self._get_tags(repository, single_tag)

        deleted = []
        for tag_data in tags:
            if not filtered_tags or tag_data['tag'] in filtered_tags:
                self._delete_image(repository, tag_data['tag'])
                deleted.append(tag_data['tag'])

        return self._parse_codeleted(deleted, tags)

    def _include_exclude(
        self,
        repository,
        regexp_expr,
        single_tag='',
        exclude=False
    ):
        tags, filtered_tags, _ = self._get_tags(repository, single_tag)
        include_excluted_tag_names = Tools.search(
            [tag_data['tag'] for tag_data in tags],
            regexp_expr,
            exclude=exclude
        )

        deleted = []
        for tag_data in tags:
            if not filtered_tags or tag_data['tag'] in filtered_tags:
                if tag_data['tag'] in include_excluted_tag_names:
                    self._delete_image(repository, tag_data['tag'])
                    deleted.append(tag_data['tag'])

        return self._parse_codeleted(deleted, tags)

    def _from_count(
        self,
        repository,
        from_count,
        single_tag=''
    ):
        tags, filtered_tags = self._get_tags(repository, single_tag)

        deleted = []
        if from_count:
            if from_count < len(tags):
                to_delete = tags[from_count - 1:]
                for tag_data in to_delete:
                    if not filtered_tags or tag_data['tag'] in filtered_tags:
                        self._delete_image(repository, tag_data['tag'])
                        deleted.append(tag_data['tag'])

        return self._parse_codeleted(deleted, tags)

    def _from_date(
        self,
        repository,
        from_date,
        single_tag=''
    ):
        tags, filtered_tags = self._get_tags(repository, single_tag)

        deleted = []
        if from_date:
            for tag_data in tags:
                if tag_data['date'] <= from_date:  # from desc order
                    if not filtered_tags or tag_data['tag'] in filtered_tags:
                        self._delete_image(repository, tag_data['tag'])
                        deleted.append(tag_data['tag'])

        return self._parse_codeleted(deleted, tags)
