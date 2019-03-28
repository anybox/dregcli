# dregcli

WIP: Docker registry API v2 client, and console tool

dregcli --help for usage

## auth

see -u login:password, --user=login:password option

DISCLAIMER: to get auth token dregcli uses basic auth, you must be in HTTPS !

## docker image

build image:

```
docker build -t anybox/dregcli .
```

use image:

```
docker run --rm -it anybox/dregcli --help
```

## dev virtualenv

```bash
python3 -m venv ~/venvs/dregcli
source ~/venvs/dregcli/bin/activate
git clone https://github.com/anybox/dregcli
cd dregcli
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements.tests.txt
python setup.py develop
```

### unit tests

```bash
py.test --pep8 --cov=dregcli --cov-report=html -v --ignore dregcli/tests/tests_integration/
```

### integration tests

specify virtual env dir in DREGCLI_VENV then run start script

```bash
export DREGCLI_VENV=~/venvs/dregcli
dregcli/tests/tests_integration/start.sh
```

optionally specify host, login, password of any thirdparty docker registry, using:

- DREGCLI_HOST
- DREGCLI_LOGIN
- DREGCLI_PASSWORD (for gitlab integrated docker registry, password could be any 'read_registry' scope user token)

if these are set, a third party registry auth integration test is triggered

```bash
export DREGCLI_VENV=~/venvs/dregcli
export DREGCLI_HOST=https://myhost
export DREGCLI_LOGIN=myuser
export DREGCLI_PASSWORD=mypassword
dregcli/tests/tests_integration/start.sh
```
