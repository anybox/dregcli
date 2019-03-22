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
    fixture_delete_tags,
    fixture_delete_tags_cotags_mapping,
)
from dregcli.console.delete import DeleteCommandHandler


class TestDeleteAllCotag:
    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_client',
        'fixture_repository',
        'fixture_delete_tags',
        'fixture_delete_tags_cotags_mapping'
    )
    def test_all_cotags(
        self,
        fixture_registry_url,
        fixture_client,
        fixture_repository,
        fixture_delete_tags,
        fixture_delete_tags_cotags_mapping,
        capsys
    ):
        """delete: cotags report in json"""
        # check data set adhoc state
        repo = fixture_client.repositories()[0]
        repo_tags = repo.tags()
        assert sorted(repo_tags) == sorted(fixture_delete_tags)

        handler = DeleteCommandHandler()
        deleted = handler.run(
            fixture_registry_url,
            fixture_repository,
            True,  # json output
            all=True
        )

        output_json = tools.get_output_json(capsys)
        assert 'result' in output_json
        # check mapping: we should match each tag cotags
        for json_result_entry in output_json['result']:
            assert sorted(json_result_entry['cotags']) == sorted(
                fixture_delete_tags_cotags_mapping[json_result_entry['tag']])
