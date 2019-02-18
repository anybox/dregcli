from unittest import mock
import pytest

from . import tools
from .fixtures import fixture_registry_url, fixture_repositories


class TestGarbage:
    @pytest.mark.usefixtures(
        'fixture_registry_url',
        'fixture_repositories',
    )
    def test_garbage(
        self,
        fixture_registry_url,
        fixture_repositories,
    ):
        # TODO
        pass
