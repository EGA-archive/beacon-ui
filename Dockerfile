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

ENV LOG_YML          /beacon/logger.yaml

RUN chown -R beacon:beacon /beacon
WORKDIR /beacon
USER beacon

CMD ["aiohttp-wsgi-serve", "beaconui.wsgi:application", "--static", "/static=./static", "--host", "0.0.0.0", "--port", "8443"]
