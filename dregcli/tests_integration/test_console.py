from unittest import mock
import json
import pytest

from dregcli.console import main as console_main


@pytest.fixture(scope="module")
def fixture_registry_url():
    return 'http://localhost:5001'


@pytest.fixture(scope="module")
def fixture_repository():
    return 'my-alpine'


@pytest.fixture(scope="module")
def fixture_tags():
    return ['3.8']


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

    def test_reps_json(self, fixture_registry_url, fixture_repository, capsys):
        expected_out = [
            json.dumps({'result': [fixture_repository]}),
            '',
        ]

        with mock.patch(
            'sys.argv',
            ['dregcli', 'reps', fixture_registry_url, '-j']
        ):
            console_main()
            captured = capsys.readouterr()
            assert captured.out == "\n".join(expected_out)

    def test_tags(
        self,
        fixture_registry_url,
        fixture_repository,
        fixture_tags,
        capsys
    ):
        expected_out = [
            'tags',
            'GET http://localhost:5001/v2/{repo}/tags/list'.format(
                repo=fixture_repository),
            '3.8',
            ''
        ]

        with mock.patch(
            'sys.argv',
            ['dregcli', 'tags', fixture_registry_url, fixture_repository]
        ):
            console_main()
            captured = capsys.readouterr()
            assert captured.out == "\n".join(expected_out)

    def test_tags_json(
            self,
            fixture_registry_url,
            fixture_repository,
            fixture_tags,
            capsys
    ):
        expected_out = [
            json.dumps({'result': fixture_tags}),
            ''
        ]

        with mock.patch(
            'sys.argv',
            ['dregcli', 'tags', fixture_registry_url, fixture_repository, '-j']
        ):
            console_main()
            captured = capsys.readouterr()
            assert captured.out == "\n".join(expected_out)
