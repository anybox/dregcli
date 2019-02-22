import hashlib
import json
import os
import sys
from unittest import mock
import pytest

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
)
import tools


class TestTestTools:
    def test_get_error_status_message(self):
        expected_code = 404
        msg = tools.get_error_status_message(expected_code)
        assert msg and isinstance(msg, str) and str(expected_code) in msg

    def test_get_output_lines(self, capsys):
        expected_output = "hello world"
        print(expected_output)
        assert tools.get_output_lines(capsys) == [expected_output]

    def test_get_output_lines_no_output(self, capsys):
        assert tools.get_output_lines(capsys) == []

    def test_get_output_json(self, capsys):
        expected_json = {"message": "hello world"}
        print(json.dumps(expected_json))
        assert tools.get_output_json(capsys) == expected_json

    def test_get_output_json_no_output(self, capsys):
        assert tools.get_output_json(capsys) is None

    def test_check_sha256(self):
        sha = "sha256:{sha}".format(sha=hashlib.sha256().hexdigest())
        assert tools.check_sha256(sha)

        sha = "sha257:{sha}".format(sha=hashlib.sha256().hexdigest())
        assert not tools.check_sha256(sha)

        sha = "sha256:wrong"
        assert not tools.check_sha256(sha)
