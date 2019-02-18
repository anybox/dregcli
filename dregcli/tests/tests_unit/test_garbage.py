import os
import sys
from unittest import mock
import pytest

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
)
import tools
from fixtures import fixture_registry_url, fixture_repositories


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