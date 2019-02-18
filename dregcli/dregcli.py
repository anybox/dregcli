from path import Path
import datetime
import os
import requests


class DRegCliException(RuntimeError):
    pass


class Client(object):
    class Meta:
        api_version = 'v2'
        remote_type_registry = 'registry'
        remote_type_gitlab = 'gitlab'
        repositories = '_catalog'
        auth_env_login = 'DREGCLI_LOGIN'
        auth_env_password = 'DREGCLI_PWD'
        auth_response_get_token_header = 'Www-Authenticate'
        auth_bearer_pattern = "Bearer {token}"

    def __init__(self, url, verbose=False):
        super().__init__()
        self.url = url
        self.verbose = verbose
        self.request_kwargs = dict()
        self.auth = False

    def set_auth(self, login, password, remote_type=False):
        remote_type = remote_type or self.Meta.remote_type_registry
        self.display("{rt}: as user '{login}'".format(rt=remote_type,
                                                      login=login))
        self.auth = {
            'login': login,
            'password': password,
            'token': '',
            'remote_type': remote_type or self.Meta.remote_type_registry,
        }
        return self.auth

    def reset_auth(self):
        self.auth = False

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

        response = self._request(url, headers={})

        repositories = response.json().get("repositories", [])
        return [Repository(self, repo) for repo in repositories]

    def _request(
        self,
        url,
        headers={},
        method=False,
        verb=False,
        expected_code=200
    ):
        method = method or requests.get
        verb = verb or 'GET'
        self.display(verb, url)

        response = method(url, headers=headers)
        if response.status_code != expected_code:
            if not self.auth:  # raise only if no auth
                msg = "Status code error {code}".format(
                    code=response.status_code
                )
                raise DRegCliException(msg)

        if self._auth_get_token(response):
            # auth: request again with token obtained through previous response
            response2 = requests.get(
                url,
                headers=self._auth_decorate_headers(headers)
            )
            if response2.status_code != expected_code:
                msg = "Status code error {code}".format(
                    code=response2.status_code
                )
                raise DRegCliException(msg)

            return response2
        else:
            return response

    def _auth_get_token(self, response):
        """get token workflow (from current response)"""
        if not self.auth:
            return False

        # < Www-Authenticate: Bearer realm="https://host/v2/token",
        # service="docker-registry.host.fr",
        # scope="registry:catalog:*"
        www_authenticate = response.headers.get(
            self.Meta.auth_response_get_token_header, '')
        if not www_authenticate:
            raise DRegCliException(
                'Auth: response header {header} missing'.format(
                    header=self.Meta.auth_response_get_token_header
                )
            )

        www_authenticate_str = www_authenticate.split('Bearer ')[1]
        www_authenticate_parts = www_authenticate_str.split(',')
        realm = www_authenticate_parts[0].split('=')[1].strip('"')
        service = www_authenticate_parts[1].split('=')[1].strip('"')
        scope = www_authenticate_parts[2].split('=')[1].strip('"')

        get_token_url = "{realm}?service={service}&scope={scope}".format(
            realm=realm,
            service=service,
            scope=scope,
        )
        get_token_response = requests.get(
            get_token_url,
            auth=requests.auth.HTTPBasicAuth(
                self.auth['login'],
                self.auth['password']
            )
        )
        if get_token_response.status_code != 200:
            self.auth['token'] = ''
            msg = "Get token request: status code error {code}".format(
                code=get_token_response.status_code
            )
            raise DRegCliException(msg)

        self.auth['token'] = get_token_response.json().get('token', False)
        if not self.auth['token']:
            msg = "Get token request: no token found in response"
            raise DRegCliException(msg)

        return self.auth['token']

    def _auth_decorate_headers(self, headers):
        """
        decorate headers (auth bearer)
        :return new headers
        :rtype dict
        """
        new_headers = headers.copy()

        if self.auth and self.auth['token']:
            new_headers['Authorization'] = \
                self.Meta.auth_bearer_pattern.format(token=self.auth['token'])

        return new_headers


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

        blobs = 'blobs'

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

        response = self.client._request(url, headers={})
        return response.json().get("tags", [])

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

        headers = self.Meta.manifests_headers  # important: accept header
        response = self.client._request(url, headers=headers)

        # image digest: grap the image digest from the header response
        digest = response.headers.get(
            self.Meta.manifest_response_header_digest,
            False
        )
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
            data=response.json()
        )


class Image(RegistryComponent):
    """
    Image
    digest: manifest digest
            from manifest Meta.manifest_response_header_digest response header
    config_digest: from image config
    """
    def __init__(self, client, name, tag, digest='', data=dict()):
        super().__init__(client, name, digest=digest, data=data)
        self.tag = tag
        self.config_digest = self.data.get('config', {}).get('digest', '')
        self.date = False

    def __str__(self):
        return "{name}:{tag}".format(name=self.name, tag=self.tag)

    @staticmethod
    def _parse_date(created_date_str):
        return datetime.datetime.strptime(
            created_date_str[:-4],
            "%Y-%m-%dT%H:%M:%S.%f"
        )

    def get_date(self):
        """
        get image date from config blob
        """
        url = str(
            Path(self.client.url) /
            Client.Meta.api_version /
            self.name /
            Repository.Meta.blobs /
            self.config_digest
        )

        headers = Repository.Meta.manifests_headers  # important: accept header
        response = self.client._request(
            url,
            headers=headers,
            expected_code=200
        )

        created_date = response.json().get('created', False)
        if not created_date:
            raise DRegCliException("Image date not found")
        self.date = self._parse_date(created_date)
        return self.date

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

        headers = Repository.Meta.manifests_headers  # important: accept header
        response = self.client._request(
            url,
            headers=headers,
            method=requests.delete,
            verb='DELETE',
            expected_code=202
        )
