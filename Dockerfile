FROM python:3.6-alpine

ARG VERSION=0.1.0

COPY exporter /opt/hive-exporter

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r /opt/hive-exporter/requirements.txt

# Download prometheus
RUN mkdir -p /etc/hive-exporter && \
    chmod 0755 /opt/hive-exporter/entrypoint.sh /opt/hive-exporter/exporter.py && \
    chown -R nobody:nogroup /etc/hive-exporter

# Expose prometheus port
EXPOSE 3392

ENTRYPOINT [ "/opt/hive-exporter/entrypoint.sh" ]
