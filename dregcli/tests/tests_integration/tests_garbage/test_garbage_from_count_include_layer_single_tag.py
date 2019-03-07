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


class TestGarbageFromCountIncludeLayerSingleTag:
    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_client',
        'fixture_repository',
        'fixture_garbage_tags',
    )
    def test_from_count_include_layer_single_tag(
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

        # tags by date desc (and their name should match fixtures)
        expected_tags_by_desc_date = [
            tag_data['tag'] for tag_data in repo.get_tags_by_date()
        ]
        assert sorted(expected_tags_by_desc_date) == \
            sorted(fixture_garbage_tags)
