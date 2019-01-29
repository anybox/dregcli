from path import Path
import requests


class DRegCliException(RuntimeError):
    pass


class Client(object):
    _api_version = 'v2'
    _catalog = '_catalog'

    def __init__(self, url, verbose=False):
        super().__init__()
        self.url = url
        self.verbose = verbose
        self.request_kwargs = dict()

    def display(self, *args):
        if self.verbose:
            print(*args)

    def catalog(self):
        url = Path(self.url) / self._api_version / self._catalog
        self.display('GET', url)

        r = requests.get(url)
        if r.status_code != 200:
            msg = "Status code error {code}".format(code=r.status_code)
            raise DRegCliException(msg)
