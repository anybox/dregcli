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
                    False,
                    user=None,
                    all=False
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
                    True,
                    False,
                    user=None,
                    all=False
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
                    False,
                    True,
                    user=None,
                    all=False
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
                    False,
                    user=None,
                    all=True
                )
