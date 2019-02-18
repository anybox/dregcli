from unittest import mock
import pytest

from .fixtures import (
    fixture_registry_url,
    fixture_repositories,
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
                    user=None,
                    gitlab=False
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
                    user='login:pwd',
                    gitlab=False
                )

        # gitlab
        with mock.patch(
            'sys.argv',
            ['dregcli', '--gitlab', 'reps', fixture_registry_url]
        ):
            with mock.patch(
                'dregcli.console.RepositoriesCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    False,
                    user=None,
                    gitlab=True
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
                    user=None,
                    gitlab=False
                )

    @pytest.mark.usefixtures('fixture_registry_url', 'fixture_repositories')
    def test_tags(self, fixture_registry_url, fixture_repositories):
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'tags',
                fixture_registry_url,
                fixture_repositories["repositories"][0],
            ]
        ):
            with mock.patch(
                'dregcli.console.TagsCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repositories["repositories"][0],
                    False,
                    user=None,
                    gitlab=False
                )

        # json
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'tags',
                fixture_registry_url,
                fixture_repositories["repositories"][0],
                '-j',
            ]
        ):
            with mock.patch(
                'dregcli.console.TagsCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repositories["repositories"][0],
                    True,
                    user=None,
                    gitlab=False
                )

    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repositories',
        'fixture_tags'
    )
    def test_image(
        self,
        fixture_registry_url,
        fixture_repositories,
        fixture_tags
    ):
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repositories["repositories"][0],
                fixture_tags[0],
            ]
        ):
            with mock.patch(
                'dregcli.console.ImageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repositories["repositories"][0],
                    fixture_tags[0],
                    False,
                    False,
                    False,
                    False,
                    user=None,
                    gitlab=False
                )

        # manifest
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repositories["repositories"][0],
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
                    fixture_repositories["repositories"][0],
                    fixture_tags[0],
                    True,
                    False,
                    False,
                    False,
                    user=None,
                    gitlab=False
                )

        # json
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repositories["repositories"][0],
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
                    fixture_repositories["repositories"][0],
                    fixture_tags[0],
                    False,
                    True,
                    False,
                    False,
                    user=None,
                    gitlab=False
                )

        # delete
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repositories["repositories"][0],
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
                    fixture_repositories["repositories"][0],
                    fixture_tags[0],
                    False,
                    False,
                    True,
                    False,
                    user=None,
                    gitlab=False
                )

        # always yes
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repositories["repositories"][0],
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
                    fixture_repositories["repositories"][0],
                    fixture_tags[0],
                    False,
                    False,
                    False,
                    True,
                    user=None,
                    gitlab=False
                )

    @pytest.mark.usefixtures('fixture_registry_url', 'fixture_repositories')
    def test_garbage(
        self,
        fixture_registry_url,
        fixture_repositories
    ):
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'garbage',
                fixture_registry_url,
                fixture_repositories["repositories"][0],
            ]
        ):
            with mock.patch(
                'dregcli.console.GarbageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repositories["repositories"][0],
                    False,
                    False,
                    user=None,
                    gitlab=False
                )

        # null
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'garbage',
                fixture_registry_url,
                fixture_repositories["repositories"][0],
                '-n'
            ]
        ):
            with mock.patch(
                'dregcli.console.GarbageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repositories["repositories"][0],
                    True,
                    False,
                    user=None,
                    gitlab=False
                )

        # json
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'garbage',
                fixture_registry_url,
                fixture_repositories["repositories"][0],
                '-j'
            ]
        ):
            with mock.patch(
                'dregcli.console.GarbageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repositories["repositories"][0],
                    False,
                    True,
                    user=None,
                    gitlab=False
                )
