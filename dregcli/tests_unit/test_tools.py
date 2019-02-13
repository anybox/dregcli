from unittest import mock
import pytest

from . import tools


class TestTools:
    def test_get_error_status_message(self):
        expected_code = 404
        msg = tools.get_error_status_message(expected_code)
        assert msg and isinstance(msg, str) and str(expected_code) in msg
