FROM python:3.7-alpine3.8

EXPOSE 8443

RUN apk add --no-cache make libressl libressl-dev gcc musl-dev

RUN mkdir /beacon
COPY requirements.txt /beacon/requirements.txt
RUN pip install -r /beacon/requirements.txt

RUN apk del --no-cache --purge make gcc postgresql-dev musl-dev libressl-dev && \
    rm -rf /var/cache/apk/*

COPY manage.py /beacon/manage.py
COPY logger.yaml /beacon/logger.yaml
COPY egafiles /beacon/beaconui
COPY static /beacon/static
COPY templates /beacon/templates

ENV LOG_YML /beacon/logger.yaml

WORKDIR /beacon
CMD ["aiohttp-wsgi-serve", "beaconui.wsgi:application", "--static", "/static=./static", "--host", "0.0.0.0", "--port", "8443"]

# CMD ["sleep", "100000000000000"]
# aiohttp-wsgi-serve beaconui.wsgi:application --static /static=./static --host 0.0.0.0 --port 8443
