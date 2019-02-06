from unittest import mock
import pytest

from dregcli.console import main as console_main


@pytest.fixture(scope="module")
def fixture_registry_url():
    return 'http://localhost:5001'


@pytest.fixture(scope="module")
def fixture_repository():
    return 'my-alpine'


@pytest.fixture(scope="module")
def fixture_tag():
    return '3.8'


class TestConsoleCommandLine:
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

    def test_tags(self, fixture_registry_url, fixture_repository):
        with mock.patch(
            'sys.argv',
            ['dregcli', 'tags', fixture_registry_url, fixture_repository]
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
            ['dregcli', 'tags', fixture_registry_url, fixture_repository, '-j']
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

    def test_image(
        self,
        fixture_registry_url,
        fixture_repository,
        fixture_tag
    ):
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repository,
                fixture_tag,
            ]
        ):
            with mock.patch(
                'dregcli.console.ImageCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(
                    fixture_registry_url,
                    fixture_repository,
                    fixture_tag,
                    False,
                    False,
                    False,
                    False,
                    user=None,
                )

        # manifest
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repository,
                fixture_tag,
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
                    fixture_tag,
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
                fixture_tag,
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
                    fixture_tag,
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
                fixture_tag,
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
                    fixture_tag,
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
                fixture_tag,
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
                    fixture_tag,
                    False,
                    False,
                    False,
                    True,
                    user=None
                )

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
                    user=None
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
                    user=None
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
                    user=None
                )
