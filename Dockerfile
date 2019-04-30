##########################
## Build env
##########################
FROM python:3.7-alpine3.8

RUN apk add --no-cache make libressl libressl-dev gcc musl-dev libffi-dev
RUN pip install --upgrade pip

RUN mkdir /beacon
COPY requirements.txt /beacon/requirements.txt
RUN pip install -r /beacon/requirements.txt

ENV LOG_YML /beacon/logger.yaml

WORKDIR /beacon
CMD ["aiohttp-wsgi-serve", "beaconui.wsgi:application", "--static", "/static=./static", "--host", "0.0.0.0", "--port", "8443"]
