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
    fixture_garbage_tags_new,
)
from dregcli.console.garbage import GarbageCommandHandler


class TestGarbageInclude:
    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_client',
        'fixture_repository',
        'fixture_garbage_tags',
        'fixture_garbage_tags_new',
    )
    def test_include(
        self,
        fixture_registry_url,
        fixture_client,
        fixture_repository,
        fixture_garbage_tags,
        fixture_garbage_tags_new,
        capsys
    ):
        # check data set adhoc state
        repo = fixture_client.repositories()[0]
        repo_tags = repo.tags()
        assert sorted(repo_tags) == sorted(fixture_garbage_tags)

        include = r"^old"
        handler = GarbageCommandHandler()
        deleted = handler.run(fixture_registry_url, fixture_repository, False,
                              include=include)

        # check output: 'old' deleted
        assert sorted(deleted) == ['old-prod', 'old-staging']

        # check should have not 'old' left
        assert sorted(repo.tags()) == sorted(fixture_garbage_tags_new)
