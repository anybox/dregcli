# dregcli

WIP: Docker registry API v2 client, and console tool

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
py.test --pep8 --cov=dregcli --cov-report=html -v --ignore dregcli/tests_integration/
```

### integration tests

specify virtual env dir in DREGCLI_VENV then run start script

```bash
export DREGCLI_VENV=~/venvs/dregcli
dregcli/tests_integration/start.sh
```
