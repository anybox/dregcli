import datetime

from dregcli.dregcli import Client

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class CommandHandler(object):
    def __init__(self):
        self.client = None

    def date2str(self, dt):
        return dt.strftime(DATE_FORMAT)

    def run(self, url, json_output, user=False, debug=False):
        if not json_output:
            print(self.Meta.command)
        self.client = Client(url, verbose=not json_output)
        if debug:
            self.client.set_debug(True)
        if user:
            login, password = user.split(':')
            self.client.set_auth(login, password)
