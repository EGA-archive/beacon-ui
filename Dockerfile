FROM python:3.7-alpine3.9

RUN pip install --upgrade pip

RUN addgroup beacon && \
    adduser -D -G beacon beacon && \
    mkdir /beacon

COPY requirements.txt /beacon/requirements.txt
RUN pip install -r /beacon/requirements.txt

COPY beaconui /beacon/beaconui
COPY static /beacon/static
COPY templates /beacon/templates
COPY logger.yaml /beacon/logger.yaml

ENV LOG_YML /beacon/logger.yaml
ENV BEACON_API_INFO           https://testbeacon.ega-archive.org/?limit=0
ENV BEACON_API_ACCESS_LEVELS  https://testbeacon.ega-archive.org/access_levels
ENV BEACON_API_QUERY          https://testbeacon.ega-archive.org/query?
ENV BEACON_API_GENOMIC_SNP    https://testbeacon.ega-archive.org/query_snp?
ENV BEACON_API_GENOMIC_REGION https://testbeacon.ega-archive.org/query_region?

RUN chown -R beacon:beacon /beacon
WORKDIR /beacon
USER beacon

CMD ["aiohttp-wsgi-serve", "beaconui.wsgi:application", "--static", "/static=./static", "--host", "0.0.0.0", "--port", "8443"]
