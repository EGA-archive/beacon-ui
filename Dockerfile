##########################
## Build env
##########################
FROM python:3.7-alpine3.8 as BUILD

RUN apk add --no-cache make libressl libressl-dev gcc musl-dev libffi-dev
RUN pip install --upgrade pip

RUN mkdir /beacon
COPY requirements.txt /beacon/requirements.txt
RUN pip install -r /beacon/requirements.txt

##########################
## Final image
##########################
FROM python:3.7-alpine3.8

EXPOSE 8443

COPY --from=BUILD usr/local/lib/python3.7/ usr/local/lib/python3.7/
COPY --from=BUILD /usr/local/bin/aiohttp-wsgi-serve /usr/local/bin/
#COPY --from=BUILD /usr/local/bin/gunicorn* /usr/local/bin/

COPY logger.yaml /beacon/logger.yaml
COPY manage.py /beacon/manage.py
COPY beaconui /beacon/beaconui
COPY static /beacon/static
COPY templates /beacon/templates

ENV LOG_YML /beacon/logger.yaml

WORKDIR /beacon
CMD ["aiohttp-wsgi-serve", "beaconui.wsgi:application", "--static", "/static=./static", "--host", "0.0.0.0", "--port", "8443"]
