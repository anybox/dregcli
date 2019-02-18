import hashlib
import os
import sys
from unittest import mock
import pytest

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
)
import tools


class TestTools:
    def test_get_error_status_message(self):
        expected_code = 404
        msg = tools.get_error_status_message(expected_code)
        assert msg and isinstance(msg, str) and str(expected_code) in msg

        def test_get_output_lines(capsys):
            expected_output = "hello world"
            assert tools.get_output_lines(capsys) == expected_output

        def test_check_sha256(sha256):
            sha = "sha256:{sha}".format(sha=hashlib.sha256().hexdigest())
            assert tools.check_sha256(sha)

            sha = "sha257:{sha}".format(sha=hashlib.sha256().hexdigest())
            assert not tools.check_sha256(sha)

            sha = "sha256:wrong"
            assert not tools.check_sha256(sha)
