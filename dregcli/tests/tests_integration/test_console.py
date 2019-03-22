import os
import sys
from tabulate import tabulate
from unittest import mock
import pytest

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
)
import tools
from fixtures import (
    fixture_registry_url,
    fixture_repository,
    fixture_tags,
    fixture_client,
)
from dregcli.console import main as console_main, CommandHandler
from dregcli.dregcli import DRegCliException, Client, Repository, Image


class TestConsole:
    def get_repo(self, client):
        return client.repositories()[0]

    @pytest.mark.usefixtures('fixture_registry_url', 'fixture_repository')
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

    @pytest.mark.usefixtures('fixture_registry_url', 'fixture_repository')
    def test_reps_user(self, fixture_registry_url, fixture_repository, capsys):
        expected_out = [
            'reps',
            "login as user 'login'",
        ]

        with mock.patch(
            'sys.argv',
            ['dregcli', '-u', 'login:pwd', 'reps', fixture_registry_url]
        ):
            console_main()
            out_lines = tools.get_output_lines(capsys)
            # we should have "registry: as user 'login'" at 2nd line
            assert out_lines[:2] == expected_out

    @pytest.mark.usefixtures('fixture_registry_url', 'fixture_repository')
    def test_reps_json(self, fixture_registry_url, fixture_repository, capsys):
        expected_json = {'result': [fixture_repository]}

        with mock.patch(
            'sys.argv',
            ['dregcli', 'reps', fixture_registry_url, '-j']
        ):
            console_main()
            assert tools.get_output_json(capsys) == expected_json

    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repository',
        'fixture_tags'
    )
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
        expected_tags_lines = tabulate([
            [t, CommandHandler().date2str(repository.image(t).get_date())]
            for t in fixture_tags
        ], headers=['Tag', 'Date']).split("\n")

        with mock.patch(
            'sys.argv',
            ['dregcli', 'tags', fixture_registry_url, fixture_repository]
        ):
            console_main()
            out_lines = tools.get_output_lines(capsys)
            assert out_lines[0] == 'tags'
            # tag lines result: last tags count ouput lines
            output_tags = out_lines[len(expected_tags_lines) * -1:]
            assert all([ot in expected_tags_lines for ot in output_tags])

    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repository',
        'fixture_tags'
    )
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
        expected_json_result = {
            'result': [
                {
                    'tag': t,
                    'date': CommandHandler().date2str(
                        repository.image(t).get_date()
                    ),
                } for t in fixture_tags
            ],
        }

        with mock.patch(
            'sys.argv',
            ['dregcli', 'tags', fixture_registry_url, fixture_repository, '-j']
        ):
            console_main()
            out_json = tools.get_output_json(capsys)
            assert out_json and 'result' in expected_json_result \
                and all(t in expected_json_result['result']
                        for t in out_json['result'])

    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repository',
        'fixture_tags'
    )
    def test_images_json(
            self,
            fixture_registry_url,
            fixture_repository,
            fixture_tags,
            capsys
    ):
        # compute expected json result from expected fixture_tags
        client = Client(fixture_registry_url, verbose=False)
        repository = Repository(client, fixture_repository)

        with mock.patch(
            'sys.argv',
            [
                'dregcli',
                'images',
                fixture_registry_url, fixture_repository,
                '-j'
            ]
        ):
            console_main()
            out_json = tools.get_output_json(capsys)

            # 1388 commit and latest should be in same layer
            # 1385 1386 and 1387 should each on separate layer

            for result_item in out_json['result']:
                tags = result_item['tags']
                tags_count = len(tags)

                assert tags_count in (1, 2)
                for t in tags:
                    pipeline_ref = t.split('-')[-1]
                    if tags_count == 1:
                        assert pipeline_ref in ('1385', '1386', '1387')
                    else:
                        assert pipeline_ref in ('latest', '1388')

    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repository',
        'fixture_tags'
    )
    def test_image(
        self,
        fixture_registry_url,
        fixture_repository,
        fixture_tags,
        capsys
    ):
        tag = 'latest'

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

    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repository',
        'fixture_tags'
    )
    def test_image_json(
        self,
        fixture_registry_url,
        fixture_repository,
        fixture_tags,
        capsys
    ):
        tag = 'latest'

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
            out_json = tools.get_output_json(capsys)
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
            out_json = tools.get_output_json(capsys)
            assert out_json and isinstance(out_json, dict) and \
                list(out_json.keys()) == ['result'] and \
                sorted(list(out_json['result'].keys())) \
                == ['digest', 'manifest'] and \
                tools.check_sha256(out_json['result']['digest'])


class TestConsoleImageDelete:
    # should be processed at last suite in this file

    def get_repo(self, client):
        return client.repositories()[0]

    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repository',
        'fixture_tags',
        'fixture_client'
    )
    def test_image_delete(
        self,
        fixture_registry_url,
        fixture_repository,
        fixture_tags,
        fixture_client,
        capsys
    ):
        tag = 'master-6da64c000cf59c30e4841371e0dac3dd02c31aaa-1385'

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

            fixture_tags.remove(
                'master-6da64c000cf59c30e4841371e0dac3dd02c31aaa-1385')
            repo = self.get_repo(fixture_client)
            assert sorted(repo.tags()) == sorted(fixture_tags)

            # after delete, repo should still be here in catalog
            assert repo.name == fixture_repository

    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repository',
        'fixture_tags',
        'fixture_client'
    )
    def test_image_delete_json(
        self,
        fixture_registry_url,
        fixture_repository,
        fixture_tags,
        fixture_client,
        capsys
    ):
        tag = 'master-b2a7d05ca36cdd3e8eb092f857580b3ed0f7159a-1386'

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
            out_json = tools.get_output_json(capsys)
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
                assert tools.get_output_json(capsys) == expected_json

            # extrapolated tags left
            # deleted in test_image_delete()
            fixture_tags.remove(
                'master-6da64c000cf59c30e4841371e0dac3dd02c31aaa-1385')
            # deleted here
            fixture_tags.remove(
                'master-b2a7d05ca36cdd3e8eb092f857580b3ed0f7159a-1386')
            repo = self.get_repo(fixture_client)
            assert sorted(repo.tags()) == sorted(fixture_tags)

            # after delete, repo should still be here in catalog
            assert repo.name == fixture_repository
