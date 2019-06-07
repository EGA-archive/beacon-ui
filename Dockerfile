##########################
## Build env
##########################
FROM python:3.7-alpine3.9 AS BUILD

RUN apk add gcc musl-dev libressl-dev libffi-dev make
RUN pip install --upgrade pip

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

##########################
## Final image
##########################
FROM python:3.7-alpine3.9

ARG BUILD_DATE
ARG SOURCE_COMMIT

LABEL maintainer "CRG System Developers"
LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.build-date=$BUILD_DATE
LABEL org.label-schema.vcs-url="https://devil.crg.eu/stash/projects/EB/repos/ega_beacon_frontend/"
LABEL org.label-schema.vcs-ref=$SOURCE_COMMIT

RUN apk add --no-cache --update libressl

RUN addgroup beacon && \
    adduser -D -G beacon beacon && \
    mkdir /beacon

COPY beaconui /beacon/beaconui
COPY static /beacon/static
COPY templates /beacon/templates
COPY logger.yaml /beacon/logger.yaml

ENV BEACON_UI_LOG  /beacon/logger.yaml


COPY --from=BUILD usr/local/lib/python3.7/ usr/local/lib/python3.7/
COPY --from=BUILD usr/local/bin/aiohttp-wsgi-serve usr/local/bin/

RUN chown -R beacon:beacon /beacon
WORKDIR /beacon
USER beacon

CMD ["aiohttp-wsgi-serve", "beaconui.wsgi:application", "--static", "/static=./static", "--host", "0.0.0.0", "--port", "8000"]
