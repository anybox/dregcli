from path import Path
import requests


class DRegCliException(RuntimeError):
    pass


class Client(object):
    class Meta:
        api_version = 'v2'
        repositories = '_catalog'

    def __init__(self, url, verbose=False):
        super().__init__()
        self.url = url
        self.verbose = verbose
        self.request_kwargs = dict()

    def display(self, *args):
        if self.verbose:
            print(*args)

    def repositories(self):
        """
        :return list of Repository instances
        """
        url = str(
            Path(self.url) /
            self.Meta.api_version /
            self.Meta.repositories
        )
        self.display('GET', url)

        r = requests.get(url)
        if r.status_code != 200:
            msg = "Status code error {code}".format(code=r.status_code)
            raise DRegCliException(msg)

        repositories = r.json().get("repositories", [])
        return [Repository(self, repo) for repo in repositories]


class RegistryComponent(object):
    def __init__(self, client, name, digest='', data=dict()):
        super().__init__()
        self.client = client
        self.name = name
        self.digest = digest
        self.data = data

    def __str__(self):
        return self.name or ''


class Repository(RegistryComponent):
    class Meta:
        tags_list = 'tags/list'
        manifests = 'manifests'
        manifests_headers = {
            "Accept": "application/vnd.docker.distribution.manifest.v2+json",
        }
        manifest_response_header_digest = 'Docker-Content-Digest'

    def tags(self):
        """
        :return list of tags (each tag an str)
        """
        url = str(
            Path(self.client.url) /
            Client.Meta.api_version /
            self.name /
            self.Meta.tags_list
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
            Client.Meta.api_version /
            self.name /
            self.Meta.manifests /
            tag
        )
        self.client.display('GET', url)

        r = requests.get(
            url,
            headers=self.Meta.manifests_headers  # important: accept header
        )
        if r.status_code != 200:
            msg = "Status code error {code}".format(code=r.status_code)
            raise DRegCliException(msg)

        # image digest: grap the image digest from the header response
        digest = r.headers.get(self.Meta.manifest_response_header_digest,
                               False)
        if not digest:
            msg = "No image digest in response header {digest_header}".format(
                digest_header=self.Meta.manifest_response_header_digest
            )
            raise DRegCliException(msg)

        return Image(
            self.client,
            self.name,
            tag,
            digest=digest,
            data=r.json()
        )


class Image(RegistryComponent):
    def __init__(self, client, name, tag, digest='', data=dict()):
        super().__init__(client, name, digest=digest, data=data)
        self.tag = tag

    def __str__(self):
        return "{name}:{tag}".format(name=self.name, tag=self.tag)

    def delete(self):
        """
        delete image
        IMPORTANT: all other related tags to image will be removed
        """
        url = str(
            Path(self.client.url) /
            Client.Meta.api_version /
            self.name /
            Repository.Meta.manifests /
            self.digest
        )
        self.client.display('DELETE', url)

        r = requests.delete(
            url,
            # important: accept header
            headers=Repository.Meta.manifests_headers
        )
        if r.status_code != 202:  # for delete 202
            msg = "Status code error {code}".format(code=r.status_code)
            raise DRegCliException(msg)
