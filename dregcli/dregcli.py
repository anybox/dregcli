from operator import itemgetter
from path import Path
import datetime
import functools
import os
import re
import requests


class DRegCliException(RuntimeError):
    pass


class Client(object):
    class Meta:
        api_version = 'v2'
        repositories = '_catalog'
        auth_env_login = 'DREGCLI_LOGIN'
        auth_env_password = 'DREGCLI_PWD'
        auth_response_get_token_header = 'Www-Authenticate'
        auth_bearer_pattern = "Bearer {token}"

    def __init__(self, url, verbose=False):
        super().__init__()

        assert isinstance(url, str)
        assert isinstance(verbose, bool)

        self.url = url
        self.verbose = verbose
        self.request_kwargs = dict()
        self.auth = False

    def set_auth(self, login, password):
        assert isinstance(login, str)
        assert isinstance(password, str)

        self.display("login as user '{login}'".format(login=login))
        self.auth = {
            'login': login,
            'password': password,
            'token': '',
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
        assert isinstance(url, str)
        assert not headers or isinstance(headers, dict)
        assert not verb or isinstance(verb, str)

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
        assert isinstance(headers, dict)
        new_headers = headers.copy()

        if self.auth and self.auth['token']:
            new_headers['Authorization'] = \
                self.Meta.auth_bearer_pattern.format(token=self.auth['token'])

        return new_headers


class RegistryComponent(object):
    def __init__(self, client, name, digest='', data=dict()):
        super().__init__()

        assert isinstance(name, str)
        assert isinstance(digest, str)
        assert isinstance(data, dict)

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
        return response.json().get("tags", []) or []

    def get_tags_by_date(self):
        """
        get and sort image by descending date
        :return [{'date': datetime, 'tag': '', 'image': Image}]
        """
        def cmp_by_date_desc(x, y):
            # descending order
            date_x = x['date']
            date_y = y['date']
            return 1 if date_x < date_y else -1

        images = []
        for tag in self.tags():
            image = self.image(tag)
            images.append({
                'tag': tag,
                'image': image,
                'date': image.get_date(),
            })

        return sorted(images, key=functools.cmp_to_key(cmp_by_date_desc))

    def group_tags(self):
        """
        group tags and return them per common layer(s)
        cotags is a list of tags that share the same layer of current item tag
        :rtype tuple (
            dict (key: layers digests compose key),
            [{'date': datetime, 'tag': '', 'image': Image,
             'cotags': ['lastest']}]
        )
            (for tags_by_date see get_tags_by_date() return)
        """
        def get_layers_digests_compose_key(layers):
            digests = []
            for layer in layers:
                digests.append(layer['digest'])
            return '/'.join(sorted(digests))

        groups = {}
        tags_by_date = self.get_tags_by_date()

        # group by common layer
        for tag_data in tags_by_date:
            group_key = get_layers_digests_compose_key(
                tag_data['image'].data['layers'])
            groups.setdefault(group_key, []).append(tag_data['image'])

        # per tag dispatch co-tags (in common layer)
        tag_cotags = {}
        for key in groups:
            for image in groups[key]:
                tag_cotags[image.tag] = [
                    ci.tag for ci in groups[key] if ci.tag != image.tag
                ]
        tags_by_date_new = []
        for tag_data in tags_by_date:
            tags_data_new = tag_data.copy()
            tags_data_new['cotags'] = list(set(tag_cotags[tag_data['tag']]))
            tags_by_date_new.append(tags_data_new)

        return groups, tags_by_date_new

    def group_images_date_desc(self, groups, result_tag=False):
        """
        regroup images by layer in desc order
        :param result_tag: True to store only tag name instead of Image
            in result
        :return [[[image(Image),], date], ...] \
            or [[[tag(str),], date], ...] if result_tag
        """
        tags_date = []

        for key in groups:
            tags_date.append([
                [result_tag and img.tag or img for img in groups[key]],
                groups[key][0].get_date()
            ])

        return sorted(tags_date, key=itemgetter(1), reverse=True)

    def group_tags_layer_single_tags_filter(
        self,
        groups,
        only_layer_single_tag_regexp_filter='',
    ):
        """
        from layer groups, return tags that are single on layer
        (example a commit tag with no release tag)
        optionaly filter them with only_layer_single_tag_regexp_filter
        """
        filtered_tags = []

        for key in groups:
            if len(groups[key]) == 1:  # concerned by a single tag
                tag = groups[key][0].tag
                if only_layer_single_tag_regexp_filter:
                    if Tools.search([tag],
                                    only_layer_single_tag_regexp_filter):
                        filtered_tags.append(tag)
                else:
                    filtered_tags.append(tag)
                filtered_tags = list(set(filtered_tags))

        return filtered_tags

    def image(self, tag):
        """
        get image data from tag
        :rtype Image
        """
        assert isinstance(tag, str)

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

        assert isinstance(tag, str) and tag
        self.tag = tag
        self.config_digest = self.data.get('config', {}).get('digest', '')
        self.date = False

    def __str__(self):
        return "{name}:{tag}".format(name=self.name, tag=self.tag)

    @staticmethod
    def _parse_date(created_date_str):
        assert isinstance(created_date_str, str)
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


class Tools(object):
    @staticmethod
    def search(items, regexp_expr, exclude=False):
        """
        search by regexp in items
        :param items: items to search if __name__ == '__main__':
        :type items: list of str
        :param regexp_expr: regexp expression
        :type regexp_expr: str
        :param exclude: True to search by exclusion (not in)
                        by security method returns [] if no item selection
                        no implicit --all
        :type exclude: bool
        """
        assert isinstance(items, list) \
            and all([isinstance(item, str) for item in items])
        assert isinstance(regexp_expr, str)
        assert isinstance(exclude, bool)

        if not items or not regexp_expr:
            return []

        regexp = re.compile(regexp_expr)
        res = [item for item in items if regexp.search(item)]

        if exclude:
            if not res:
                # by security method returns [] if no item selection
                # no implicit --all
                return res
            # exclusion logic for result
            res = [item for item in items if item not in res]
        return res
