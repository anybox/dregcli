import json
import os
import sys
import pytest

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        os.pardir + os.sep + os.pardir
    )
)
import tools
from fixtures import (
    fixture_registry_url,
    fixture_client,
    fixture_repository,
    fixture_garbage_tags,
)
from dregcli.console.garbage import GarbageCommandHandler


class TestGarbageAll:
    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_client',
        'fixture_repository',
        'fixture_garbage_tags'
    )
    def test_all(
        self,
        fixture_registry_url,
        fixture_client,
        fixture_repository,
        fixture_garbage_tags,
        capsys
    ):
        # check data set adhoc state
        repo = fixture_client.repositories()[0]
        repo_tags = repo.tags()
        assert sorted(repo_tags) == sorted(fixture_garbage_tags)

        handler = GarbageCommandHandler()
        handler.run(fixture_registry_url, fixture_repository, True, all=True)

        # check output: all tags deleted output
        out_lines = tools.get_output_lines(capsys)
        json_output = json.loads(out_lines[0])
        assert json_output and 'result' in json_output \
            and sorted(json_output['result']) == sorted(fixture_garbage_tags)

        # check should have no tag anymore left for repo
        assert repo.tags() == []
