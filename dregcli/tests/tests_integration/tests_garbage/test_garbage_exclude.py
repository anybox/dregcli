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
    fixture_garbage_tags_last,
    fixture_garbage_tags_old,
)
from dregcli.console.garbage import GarbageCommandHandler


class TestGarbageExclude:
    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_client',
        'fixture_repository',
        'fixture_garbage_tags',
        'fixture_garbage_tags_old',
    )
    def test_exclude(
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

        isolated_tag = 'latest'
        handler = GarbageCommandHandler()
        handler.run(
            fixture_registry_url, fixture_repository,
            True,
            exclude=r"^{tag}".format(tag=isolated_tag)
        )

        # check output: others than isolated_tag deleted
        expected_tags_left = fixture_garbage_tags.copy()
        expected_tags_left.remove(isolated_tag)
        json_output = tools.get_output_json(capsys)
        assert json_output and 'result' in json_output \
            and sorted(json_output['result']) == sorted(expected_tags_left)

        # check should have isolated_tag left (by exclusion)
        assert repo.tags() == [isolated_tag]
