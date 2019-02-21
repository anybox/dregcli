import json
import os
import sys
from unittest import mock
import pytest

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
)
import tools
from fixtures import fixture_registry_url, fixture_repository, fixture_tags
from dregcli.console.garbage import GarbageCommandHandler


class TestGarbage:
    @pytest.mark.usefixtures('fixture_registry_url', 'fixture_repository')
    def test_garbage_no_option(
        self,
        fixture_registry_url,
        fixture_repository,
        capsys
    ):
        expected_msg = 'no option selected (criteria). --delete aborted'
        handler = GarbageCommandHandler()

        expected_output_json = {'error': expected_msg}
        handler.run(fixture_registry_url, fixture_repository, True, null=True)
        out_lines = tools.get_output_lines(capsys)
        json_output = json.loads(out_lines[0])
        assert json_output == expected_output_json

        expected_output_lines = ['garbage', expected_msg]
        handler.run(fixture_registry_url, fixture_repository, False, null=True)
        out_lines = tools.get_output_lines(capsys)
        assert out_lines == expected_output_lines
