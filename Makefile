HOST=0.0.0.0
PORT=8000

LOG_YML=logger.yaml

CONTAINER=beacon-frontend
IMG=egarchive/beacon-frontend

.PHONY: server build up down log exec

# ####### Beacon Endpoints
export BEACON_INFO_ENDPOINT=https://testbeacon.ega-archive.org/?limit=0
export BEACON_ACCESS_LEVELS_ENDPOINT=https://testbeacon.ega-archive.org/access_levels
export BEACON_ENDPOINT_query=https://testbeacon.ega-archive.org/query?


server:
	@aiohttp-wsgi-serve beaconui.wsgi:application --static /static=./static --host $(HOST) --port $(PORT)

build:
	docker build --build-arg http_proxy="http://hellgate.local:8080" \
                     --build-arg https_proxy="http://hellgate.local:8080" \
                     -t $(IMG) .

shell:
	@python manage.py shell -i python


MOUNTPOINTS=-v $(shell pwd -P)/logger.yaml/beacon/logger.yaml \
	    -v $(shell pwd -P)/manage.py:/beacon/manage.py    \
	    -v $(shell pwd -P)/beaconui:/beacon/beaconui      \
	    -v $(shell pwd -P)/static:/beacon/static          \
	    -v $(shell pwd -P)/templates:/beacon/templates    \
	    -e LOG_YML=/beacon/logger.yaml                    \
	    -e BEACON_INFO_ENDPOINT="$(BEACON_INFO_ENDPOINT)"                       \
	    -e BEACON_ACCESS_LEVELS_ENDPOINT="$(BEACON_ACCESS_LEVELS_ENDPOINT)"     \
	    -e BEACON_ENDPOINT_query="$(BEACON_ENDPOINT_query)"

up:
	docker run -d                                        \
	           --name crg-$(CONTAINER)                   \
	           --hostname $(CONTAINER).crg.eu            \
	           -p $(PORT):8443                           \
	           $(MOUNTPOINTS)                            \
	 	$(IMG)

down:
	-docker kill crg-$(CONTAINER)
	docker rm crg-$(CONTAINER)

log:
	docker logs -f crg-$(CONTAINER)

exec:
	docker exec -it crg-$(CONTAINER) sh


db:
	rm -rf db.sqlite
	python manage.py migrate

