# dregcli

WIP: Docker registry API v2 client, and console tool

## dev virtualenv

```bash
$ python3 -m venv ~/venvs/dregcli
$ source ~/venvs/dregcli/bin/activate
$ git clone https://github.com/anybox/dregcli
$ cd dregcli
$ pip install --upgrade pip
$ pip install -r requirements.txt
$ pip install -r requirements.tests.txt
$ python setup.py develop
$ py.test --pep8 --cov=cdreg_py --cov-report=html --lf --nf --ff -v
```
