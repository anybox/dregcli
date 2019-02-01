from unittest import mock
import pytest

from . import tools
from dregcli.dregcli import DRegCliException, Client, Repository


@pytest.fixture(scope="module")
def fixture_registry_url():
    return 'http://localhost:5001'


@pytest.fixture(scope="module")
def fixture_repo():
    return 'my-alpine'


class TestGarbage:
    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repo',
    )
    def test_garbage(
        self,
        fixture_registry_url,
        fixture_repo,
    ):
        # TODO
        pass
