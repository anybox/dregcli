from unittest import mock
import json
import pytest

from . import tools
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
        ]

        with mock.patch(
            'sys.argv',
            ['dregcli', 'reps', fixture_registry_url]
        ):
            console_main()
            out_lines = tools.get_output_lines(capsys)
            assert out_lines == expected_out

    def test_reps_json(self, fixture_registry_url, fixture_repository, capsys):
        expected_json = {'result': [fixture_repository]}

        with mock.patch(
            'sys.argv',
            ['dregcli', 'reps', fixture_registry_url, '-j']
        ):
            console_main()
            out_json = json.loads(tools.get_output_lines(capsys)[0])
            assert out_json == expected_json

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
        ]

        with mock.patch(
            'sys.argv',
            ['dregcli', 'tags', fixture_registry_url, fixture_repository]
        ):
            console_main()
            out_lines = tools.get_output_lines(capsys)
            assert out_lines == expected_out

    def test_tags_json(
            self,
            fixture_registry_url,
            fixture_repository,
            fixture_tags,
            capsys
    ):
        expected_json = {'result': fixture_tags}

        with mock.patch(
            'sys.argv',
            ['dregcli', 'tags', fixture_registry_url, fixture_repository, '-j']
        ):
            console_main()
            out_json = json.loads(tools.get_output_lines(capsys)[0])
            assert out_json == expected_json

    def test_image(
        self,
        fixture_registry_url,
        fixture_repository,
        fixture_tags,
        capsys
    ):
        expected_out = [
            'image',
            'GET http://localhost:5001/v2/{repo}/manifests/{tag}'.format(
                repo=fixture_repository, tag=fixture_tags[0]),
        ]

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
            console_main()
            out_lines = tools.get_output_lines(capsys)
            # 3 lines, command, request and digest
            assert len(out_lines) == 3 and \
                out_lines[:2] == expected_out and \
                tools.check_sha256(out_lines[2])

        expected_out = [
            'image',
            'GET http://localhost:5001/v2/{repo}/manifests/{tag}'.format(
                repo=fixture_repository, tag=fixture_tags[0]),
        ]

        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repository,
                fixture_tags[0],
                '-m'
            ]
        ):
            console_main()
            out_lines = tools.get_output_lines(capsys)
            # as we ask for manifest, we have more than 3 out_lines
            assert len(out_lines) > 3 and \
                out_lines[:2] == expected_out and \
                tools.check_sha256(out_lines[2])

    def test_image_json(
        self,
        fixture_registry_url,
        fixture_repository,
        fixture_tags,
        capsys
    ):
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
            console_main()
            out_json = json.loads(tools.get_output_lines(capsys)[0])
            assert out_json and isinstance(out_json, dict) and \
                list(out_json.keys()) == ['result'] and \
                list(out_json['result'].keys()) == ['digest'] and \
                tools.check_sha256(out_json['result']['digest'])
