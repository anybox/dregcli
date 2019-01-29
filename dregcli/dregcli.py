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
        """
        :return list of Repository instances
        """
        url = str(
            Path(self.url) /
            self._api_version /
            self._catalog
        )
        self.display('GET', url)

        r = requests.get(url)
        if r.status_code != 200:
            msg = "Status code error {code}".format(code=r.status_code)
            raise DRegCliException(msg)

        repositories = r.json().get("repositories", [])
        return [Repository(self, repo) for repo in repositories]


class RegistryComponent(object):
    def __init__(self, client, name):
        super().__init__()
        self.client = client
        self.name = name
        self.data = dict()

    def __str__(self):
        return self.name or ''


class Repository(RegistryComponent):
    _tags_list = 'tags/list'
    _manifests = 'manifests'
    _manifests_headers = {
        "Accept": "application/vnd.docker.distribution.manifest.v2+json",
    }

    def tags(self):
        """
        :return list of tags (each tag an str)
        """
        url = str(
            Path(self.client.url) /
            self.client._api_version /
            self.name /
            self._tags_list
        )
        self.client.display('GET', url)

        r = requests.get(url)
        if r.status_code != 200:
            msg = "Status code error {code}".format(code=r.status_code)
            raise DRegCliException(msg)

        return r.json().get("tags", [])

    def image(self, tag):
        """
        get image data from tag
        """
        url = str(
            Path(self.client.url) /
            self.client._api_version /
            self.name /
            self._manifests /
            tag
        )
        self.client.display('GET', url)

        r = requests.get(url, headers=self._manifests_headers)
        if r.status_code != 200:
            msg = "Status code error {code}".format(code=r.status_code)
            raise DRegCliException(msg)

        return r.json()
