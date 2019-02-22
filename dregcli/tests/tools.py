import json
import re


def get_error_status_message(code):
    return "Status code error {code}".format(code=code)


def get_output_lines(capsys):
    return capsys.readouterr().out.split("\n")[:-1]


def get_output_json(capsys):
    # json always on first line
    output_lines = get_output_lines(capsys)
    return output_lines and json.loads(output_lines[0]) or None


def check_sha256(sha256):
    return re.match("sha256\\:[A-Fa-f0-9]{64}", sha256)
