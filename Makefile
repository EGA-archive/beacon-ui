HOST=0.0.0.0
PORT=8000

LOG_YML=logger.yaml

CONTAINER=beacon-frontend
IMG=egarchive/beacon-frontend

.PHONY: server build up down log exec

export BEACON_INFO_ENDPOINT=http://localhost:10000/elixirbeacon/v1/beacon/?limit=0
export BEACON_QUERY_ENDPOINT=http://localhost:10000/elixirbeacon/v1/beacon/query?
export BEACON_ACCESS_LEVELS_ENDPOINT=http://localhost:10000/elixirbeacon/v1/beacon/access_levels

# export BEACON_INFO_ENDPOINT=http://dev.clinbioinfosspa.es:9076/elixirbeacon/v1/beacon/
# export BEACON_QUERY_ENDPOINT=http://dev.clinbioinfosspa.es:9076/elixirbeacon/v1/beacon/query?
# export BEACON_ACCESS_LEVELS_ENDPOINT=http://dev.clinbioinfosspa.es:9076/elixirbeacon/v1/beacon/access_levels

# export BEACON_INFO_ENDPOINT=https://egatest.crg.eu/csvs_beacon/
# export BEACON_QUERY_ENDPOINT=https://egatest.crg.eu/csvs_beacon/genomic_region?
# export BEACON_ACCESS_LEVELS_ENDPOINT=https://egatest.crg.eu/csvs_beacon/access_levels

server:
	@aiohttp-wsgi-serve beaconui.wsgi:application --static /static=./static --host $(HOST) --port $(PORT)

build:
	docker build --build-arg http_proxy="http://hellgate.local:8080" \
                     --build-arg https_proxy="http://hellgate.local:8080" \
                     -t $(IMG) .

shell:
	@python manage.py shell -i python

up:
	docker run -d                                        \
	           --name crg-$(CONTAINER)                   \
	           --hostname $(CONTAINER).crg.eu            \
	           -p 9221:8443                              \
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

