HOST=0.0.0.0
PORT=8000

LOG_YML=logger.yaml

CONTAINER=beacon-frontend
IMG=egarchive/beacon-frontend

.PHONY: server build up down log exec

server:
	@aiohttp-wsgi-serve beaconui.wsgi:application --static /static=./static --host $(HOST) --port $(PORT)

build:
	docker build --build-arg http_proxy="http://hellgate.local:8080" \
                     --build-arg https_proxy="http://hellgate.local:8080" \
                     -t $(IMG) .

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
