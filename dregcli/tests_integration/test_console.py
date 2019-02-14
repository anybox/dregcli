from unittest import mock
import json
import pytest

from . import tools
from dregcli.console import main as console_main
from dregcli.dregcli import DRegCliException, Client, Repository, Image


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

    def test_reps_user(self, fixture_registry_url, fixture_repository, capsys):
        expected_out = [
            'reps',
            "registry: as user 'login'",
        ]

        with mock.patch(
            'sys.argv',
            ['dregcli', '-u', 'login:pwd', 'reps', fixture_registry_url]
        ):
            console_main()
            out_lines = tools.get_output_lines(capsys)
            # we should have "registry: as user 'login'" at 2nd line
            assert out_lines[:2] == expected_out

        # gitlab
        expected_out = [
            'reps',
            "gitlab: as user 'login'",
        ]

        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                '-u', 'login:pwd',
                '--gitlab',
                'reps',
                fixture_registry_url
            ]
        ):
            console_main()
            out_lines = tools.get_output_lines(capsys)
            # we should have "gitlab: as user 'login'" at 2nd line
            assert out_lines[:2] == expected_out

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
        # compute expected console result from expected fixture_tags
        client = Client(fixture_registry_url, verbose=False)
        repository = Repository(client, fixture_repository)
        expected_tags_lines = [
            "{tag}\t\t({dt})".format(
                tag=t,
                dt=repository.image(t).get_date()
            ) for t in fixture_tags
        ]

        with mock.patch(
            'sys.argv',
            ['dregcli', 'tags', fixture_registry_url, fixture_repository]
        ):
            console_main()
            out_lines = tools.get_output_lines(capsys)
            assert out_lines[0] == 'tags' and \
                out_lines[1] == 'GET {url}/v2/{repo}/tags/list'.format(
                    url=fixture_registry_url,
                    repo=fixture_repository
                )
            assert out_lines[len(expected_tags_lines)*-1:] \
                == expected_tags_lines

    def test_tags_json(
            self,
            fixture_registry_url,
            fixture_repository,
            fixture_tags,
            capsys
    ):
        # compute expected json result from expected fixture_tags
        client = Client(fixture_registry_url, verbose=False)
        repository = Repository(client, fixture_repository)
        expected_json = {
            'result': [
                {
                    'tag': t,
                    'date': repository.image(t).get_date()
                } for t in fixture_tags
            ],
        }

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

            # after delete, same image action should 404 (no more manifest)
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
                expected_out_404 = expected_out.copy()
                expected_out_404.append(tools.get_error_status_message(404))

                console_main()
                assert tools.get_output_lines(capsys) == expected_out_404

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

            # after delete, same image action should 404 (no more manifest)
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
                msg404 = tools.get_error_status_message(404)
                expected_json = {'error': msg404}

                console_main()
                out_json = json.loads(tools.get_output_lines(capsys)[0])
                assert out_json == expected_json

    def test_garbage(
        self,
        fixture_registry_url,
        fixture_repository,
        capsys
    ):
        # TODO

        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'garbage',
                fixture_registry_url,
                fixture_repository,
                '-n',
            ]
        ):
            console_main()

    def test_garbage_json(
        self,
        fixture_registry_url,
        fixture_repository,
        capsys
    ):
        # TODO
        expected_json = {}

        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'garbage',
                fixture_registry_url,
                fixture_repository,
                '-n',
            ]
        ):
            console_main()
