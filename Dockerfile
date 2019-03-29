FROM python:3.7-alpine
LABEL company="Anybox SAS"
      maintainer "Vincent GREINER <vgreiner.anybox.fr>"

COPY ./requirements.txt /app/
COPY ./requirements.tests.txt /app/
COPY ./setup.py /app/
COPY ./dregcli /app/dregcli/

RUN python3 -m venv /app/.env
RUN /app/.env/bin/pip install --upgrade pip \
    && /app/.env/bin/pip install -r /app/requirements.txt \
    && /app/.env/bin/pip install -r /app/requirements.tests.txt \
    && cd /app && /app/.env/bin/python setup.py develop

RUN rm /app/requirements.txt && rm /app/requirements.tests.txt && rm /app/setup.py

COPY ./docker_entrypoint.sh /
RUN chmod u+x /docker_entrypoint.sh
ENTRYPOINT ["/docker_entrypoint.sh"]
