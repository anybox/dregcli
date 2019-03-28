FROM python:3.6-alpine
LABEL company="Anybox SAS"
      maintainer "Vincent GREINER <vgreiner.anybox.fr>"

COPY ./requirements.txt /app/requirements.txt
COPY ./requirements.tests.txt /app/requirements.tests.txt
COPY ./setup.py /app/setup.py
COPY ./dregcli /app/dregcli/

WORKDIR /app

# setup
RUN python3 -m venv .env
RUN .env/bin/pip install --upgrade pip \
    && .env/bin/pip install -r requirements.txt \
    && .env/bin/pip install -r requirements.tests.txt \
    && .env/bin/python setup.py develop
RUN rm /app/requirements.txt && rm /app/requirements.tests.txt && rm /app/setup.py

CMD ["sh", "-c", "source .env/bin/activate && dregcli"]
