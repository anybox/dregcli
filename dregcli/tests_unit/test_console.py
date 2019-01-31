from unittest import mock
import pytest

from dregcli.console import main as console_main


@pytest.fixture(scope="module")
def fixture_registry_url():
    return 'http://localhost:5001'


class TestConsoleCommandLine:
    def test_reps(self, fixture_registry_url, capsys):
        with mock.patch(
            'sys.argv',
            ['dregcli', 'reps', fixture_registry_url]
        ):
            with mock.patch(
                'dregcli.console.RepositoriesCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(fixture_registry_url, False)

    def test_reps_json(self, fixture_registry_url, capsys):
        with mock.patch(
            'sys.argv',
            ['dregcli', 'reps', fixture_registry_url, '-j']
        ):
            with mock.patch(
                'dregcli.console.RepositoriesCommandHandler.run'
            ) as mo:
                console_main()
                mo.assert_called_once_with(fixture_registry_url, True)
