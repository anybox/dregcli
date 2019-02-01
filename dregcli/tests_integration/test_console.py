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
    return ['latest', '3.7', '3.8']


class TestConsole:
    def test_reps(self, fixture_registry_url, fixture_repository, capsys):
        expected_out = [
            'reps',
            'GET {url}/v2/_catalog'.format(url=fixture_registry_url),
            fixture_repository,
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
            'GET {url}/v2/{repo}/tags/list'.format(
                url=fixture_registry_url,
                repo=fixture_repository
            ),
            ','.join(fixture_tags),
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
        tag = fixture_tags[0]  # FYI in test_dregcli fixture_tags[2] is deleted

        expected_out = [
            'image',
            'GET {url}/v2/{repo}/manifests/{tag}'.format(
                url=fixture_registry_url,
                repo=fixture_repository,
                tag=tag
            ),
        ]

        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repository,
                tag,
            ]
        ):
            console_main()
            out_lines = tools.get_output_lines(capsys)
            # 3 lines, command, request and digest
            assert len(out_lines) == 3 and \
                out_lines[:2] == expected_out and \
                tools.check_sha256(out_lines[2])

        # with manifest
        expected_out = [
            'image',
            'GET {url}/v2/{repo}/manifests/{tag}'.format(
                url=fixture_registry_url,
                repo=fixture_repository,
                tag=tag
            ),
        ]

        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repository,
                tag,
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
        tag = fixture_tags[0]  # FYI in test_dregcli fixture_tags[2] is deleted

        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repository,
                tag,
                '-j',
            ]
        ):
            console_main()
            out_json = json.loads(tools.get_output_lines(capsys)[0])
            assert out_json and isinstance(out_json, dict) and \
                list(out_json.keys()) == ['result'] and \
                list(out_json['result'].keys()) == ['digest'] and \
                tools.check_sha256(out_json['result']['digest'])

        # with manifest
        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repository,
                tag,
                '-j',
                '-m',
            ]
        ):
            console_main()
            out_json = json.loads(tools.get_output_lines(capsys)[0])
            assert out_json and isinstance(out_json, dict) and \
                list(out_json.keys()) == ['result'] and \
                sorted(list(out_json['result'].keys())) \
                == ['digest', 'manifest'] and \
                tools.check_sha256(out_json['result']['digest'])

    def test_image_delete(
        self,
        fixture_registry_url,
        fixture_repository,
        fixture_tags,
        capsys
    ):
        tag = fixture_tags[0]  # FYI in test_dregcli fixture_tags[2] is deleted

        expected_out = [
            'image',
            'GET {url}/v2/{repo}/manifests/{tag}'.format(
                url=fixture_registry_url,
                repo=fixture_repository,
                tag=tag
            ),

        ]
        expected_delete_prefix = \
            'DELETE {url}/v2/{repo}/manifests/'.format(
                url=fixture_registry_url,
                repo=fixture_repository
            )

        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repository,
                tag,
                '-d',
                '-y'
            ]
        ):
            console_main()
            out_lines = tools.get_output_lines(capsys)
            # 5 lines: command, get image request, delete request,
            #          then digest and 'deleted' message
            delete_digest = out_lines[2][len(expected_delete_prefix):]
            digest = out_lines[3]
            assert len(out_lines) == 5 and \
                out_lines[:2] == expected_out and \
                out_lines[2].startswith(expected_delete_prefix) and \
                tools.check_sha256(delete_digest) and \
                tools.check_sha256(digest) and \
                out_lines[4] == 'deleted'

    def test_image_delete_json(
        self,
        fixture_registry_url,
        fixture_repository,
        fixture_tags,
        capsys
    ):
        tag = fixture_tags[1]  # FYI in test_dregcli fixture_tags[2] is deleted

        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'image',
                fixture_registry_url,
                fixture_repository,
                tag,
                '-d',
                '-y',
                '-j',
            ]
        ):
            console_main()
            out_json = json.loads(tools.get_output_lines(capsys)[0])
            assert out_json and isinstance(out_json, dict) and \
                list(out_json.keys()) == ['result'] and \
                sorted(list(out_json['result'].keys())) == [
                    'digest', 'message'] and \
                tools.check_sha256(out_json['result']['digest']) and \
                out_json['result']['message'] == 'deleted'
