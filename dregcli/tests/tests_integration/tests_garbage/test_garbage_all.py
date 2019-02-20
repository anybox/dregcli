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
    fixture_tags,
)
from dregcli.console.garbage import GarbageCommandHandler


class TestGarbage:
    @pytest.mark.usefixtures('fixture_registry_url', 'fixture_repository')
    def test_all(self, fixture_registry_url, fixture_repository):
        handler = GarbageCommandHandler()
        handler.run(fixture_registry_url, fixture_repository, True)
