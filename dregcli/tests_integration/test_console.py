from unittest import mock
import pytest

from dregcli.console import main as console_main


@pytest.fixture(scope="module")
def fixture_registry_url():
    return 'http://localhost:5001'


class TestConsole:
    def test_reps(self, fixture_registry_url, capsys):
        expected_out = [
            'reps',
            'GET http://localhost:5001/v2/_catalog',
            'my-alpine',
            ''
        ]

        with mock.patch(
            'sys.argv',
            ['dregcli', 'reps', fixture_registry_url]
        ):
            console_main()
            captured = capsys.readouterr()
            assert captured.out == "\n".join(expected_out)
