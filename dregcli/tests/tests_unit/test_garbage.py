import json
import os
import sys
from unittest import mock
import pytest

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
)
import tools
from fixtures import fixture_registry_url, fixture_repository
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

        expected_output_lines = [json.dumps({'error': expected_msg})]
        handler.run(fixture_registry_url, fixture_repository, True)
        out_lines = tools.get_output_lines(capsys)
        assert out_lines == expected_output_lines

        expected_output_lines = ['garbage', expected_msg]
        handler.run(fixture_registry_url, fixture_repository, False)
        out_lines = tools.get_output_lines(capsys)
        assert out_lines == expected_output_lines
