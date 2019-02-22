import os
import sys
from unittest import mock
import pytest

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
)
from fixtures import (
    fixture_registry_url,
    fixture_repository,
    fixture_tags
)
from dregcli.console import main as console_main


class TestConsoleCommandLine:
    @pytest.mark.usefixtures('fixture_registry_url')
    def test_reps(self, fixture_registry_url):
        with mock.patch(
            'sys.argv',
            ['dregcli', 'reps', fixture_registry_url]
        ):
            with mock.patch(
                'dregcli.console.RepositoriesCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    False,
                    user=None
                )

        # user
        with mock.patch(
            'sys.argv',
            ['dregcli', '-u', 'login:pwd', 'reps', fixture_registry_url]
        ):
            with mock.patch(
                'dregcli.console.RepositoriesCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    False,
                    user='login:pwd'
                )

        # json
        with mock.patch(
            'sys.argv',
            ['dregcli', 'reps', fixture_registry_url, '-j']
        ):
            with mock.patch(
                'dregcli.console.RepositoriesCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    True,
                    user=None
                )

    @pytest.mark.usefixtures('fixture_registry_url', 'fixture_repository')
    def test_tags(self, fixture_registry_url, fixture_repository):
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'tags',
                fixture_registry_url,
                fixture_repository,
            ]
        ):
            with mock.patch(
                'dregcli.console.TagsCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    False,
                    user=None
                )

        # json
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'tags',
                fixture_registry_url,
                fixture_repository,
                '-j',
            ]
        ):
            with mock.patch(
                'dregcli.console.TagsCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    True,
                    user=None
                )

    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repository',
        'fixture_tags'
    )
    def test_image(
        self,
        fixture_registry_url,
        fixture_repository,
        fixture_tags
    ):
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repository,
                fixture_tags[0],
            ]
        ):
            with mock.patch(
                'dregcli.console.ImageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    fixture_tags[0],
                    False,
                    False,
                    False,
                    False,
                    user=None
                )

        # manifest
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repository,
                fixture_tags[0],
                '-m',
            ]
        ):
            with mock.patch(
                'dregcli.console.ImageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    fixture_tags[0],
                    True,
                    False,
                    False,
                    False,
                    user=None
                )

        # json
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repository,
                fixture_tags[0],
                '-j',
            ]
        ):
            with mock.patch(
                'dregcli.console.ImageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    fixture_tags[0],
                    False,
                    True,
                    False,
                    False,
                    user=None
                )

        # delete
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repository,
                fixture_tags[0],
                '-d',
            ]
        ):
            with mock.patch(
                'dregcli.console.ImageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    fixture_tags[0],
                    False,
                    False,
                    True,
                    False,
                    user=None
                )

        # always yes
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repository,
                fixture_tags[0],
                '-y',
            ]
        ):
            with mock.patch(
                'dregcli.console.ImageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    fixture_tags[0],
                    False,
                    False,
                    False,
                    True,
                    user=None
                )

    @pytest.mark.usefixtures('fixture_registry_url', 'fixture_repository')
    def test_garbage(
        self,
        fixture_registry_url,
        fixture_repository
    ):
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'garbage',
                fixture_registry_url,
                fixture_repository,
            ]
        ):
            with mock.patch(
                'dregcli.console.GarbageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    False,
                    user=None,
                    null=False,
                    yes=False,
                    all=False,
                    from_count=0,
                    from_date=0,
                    include='',
                    exclude=''
                )

        # json
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'garbage',
                fixture_registry_url,
                fixture_repository,
                '-j'
            ]
        ):
            with mock.patch(
                'dregcli.console.GarbageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    True,
                    user=None,
                    null=False,
                    yes=False,
                    all=False,
                    from_count=0,
                    from_date=0,
                    include='',
                    exclude=''
                )

        # null
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'garbage',
                fixture_registry_url,
                fixture_repository,
                '-n'
            ]
        ):
            with mock.patch(
                'dregcli.console.GarbageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    False,
                    user=None,
                    null=True,
                    yes=False,
                    all=False,
                    from_count=0,
                    from_date=0,
                    include='',
                    exclude=''
                )

        # yes
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'garbage',
                fixture_registry_url,
                fixture_repository,
                '-y'
            ]
        ):
            with mock.patch(
                'dregcli.console.GarbageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    False,
                    user=None,
                    null=False,
                    yes=True,
                    all=False,
                    from_count=0,
                    from_date=0,
                    include='',
                    exclude=''
                )

        # all
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'garbage',
                fixture_registry_url,
                fixture_repository,
                '-a'
            ]
        ):
            with mock.patch(
                'dregcli.console.GarbageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    False,
                    user=None,
                    null=False,
                    yes=False,
                    all=True,
                    from_count=0,
                    from_date=0,
                    include='',
                    exclude=''
                )

        # from_count
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'garbage',
                fixture_registry_url,
                fixture_repository,
                '--from-count=10'
            ]
        ):
            with mock.patch(
                'dregcli.console.GarbageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    False,
                    user=None,
                    null=False,
                    yes=False,
                    all=False,
                    from_count=10,
                    from_date=0,
                    include='',
                    exclude=''
                )

        # from_date
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'garbage',
                fixture_registry_url,
                fixture_repository,
                '--from-date=2018-06-30'
            ]
        ):
            with mock.patch(
                'dregcli.console.GarbageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    False,
                    user=None,
                    null=False,
                    yes=False,
                    all=False,
                    from_count=0,
                    from_date='2018-06-30',
                    include='',
                    exclude=''
                )

        # include
        include_option_val = "^staging-[0-9]\{4\}"
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'garbage',
                fixture_registry_url,
                fixture_repository,
                '--include="{include}"'.format(include=include_option_val)
            ]
        ):
            with mock.patch(
                'dregcli.console.GarbageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    False,
                    user=None,
                    null=False,
                    yes=False,
                    all=False,
                    from_count=0,
                    from_date=0,
                    include=include_option_val,
                    exclude=''
                )

        # exclude
        exclude_option_val = "^stable-[0-9]\{4\}"
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'garbage',
                fixture_registry_url,
                fixture_repository,
                '--exclude="{exclude}"'.format(exclude=exclude_option_val)
            ]
        ):
            with mock.patch(
                'dregcli.console.GarbageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    False,
                    user=None,
                    null=False,
                    yes=False,
                    all=False,
                    from_count=0,
                    from_date=0,
                    include='',
                    exclude=exclude_option_val
                )
