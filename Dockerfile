FROM python:3.6-alpine

ARG VERSION=0.1.0

COPY exporter /opt/json-exporter

RUN apk add --update --no-cache aws-cli && \
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r /opt/json-exporter/requirements.txt

RUN mkdir -p /etc/json-exporter && \
    chmod 0755 /opt/json-exporter/entrypoint.sh /opt/json-exporter/exporter.py && \
    chown -R nobody:nogroup /etc/json-exporter

EXPOSE 3392

ENTRYPOINT [ "/opt/json-exporter/entrypoint.sh" ]
