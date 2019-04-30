HOST=0.0.0.0
PORT=8000

LOG_YML=logger.yaml

CONTAINER=beacon-frontend
IMG=egarchive/beacon-frontend

.PHONY: server build up down log exec

# # # ####### EGA Beacon @ local-path
# export BEACON_BASE=http://localhost:10000/elixirbeacon/v1/beacon/?limit=0
# export BEACON_INFO_ENDPOINT=$(BEACON_BASE)/?limit=0
# export BEACON_QUERY_ENDPOINT=$(BEACON_BASE)/query?
# export BEACON_GENOMIC_REGION_ENDPOINT=$(BEACON_BASE)/genomic_region?
# export BEACON_GENOMIC_SNP_ENDPOINT=$(BEACON_BASE)/genomic_snp?
# export BEACON_ACCESS_LEVELS_ENDPOINT=$(BEACON_BASE)/access_levels

# # ####### EGA Beacon
# export BEACON_BASE=https://testbeacon.ega-archive.org
# export BEACON_INFO_ENDPOINT=$(BEACON_BASE)/?limit=0
# export BEACON_QUERY_ENDPOINT=$(BEACON_BASE)/query?
# export BEACON_GENOMIC_REGION_ENDPOINT=$(BEACON_BASE)/genomic_region?
# export BEACON_GENOMIC_SNP_ENDPOINT=$(BEACON_BASE)/genomic_snp?
# export BEACON_ACCESS_LEVELS_ENDPOINT=$(BEACON_BASE)/access_levels

# ####### OpenCGA @ Sevilla
# export BEACON_BASE=http://dev.clinbioinfosspa.es:9075/elixirbeacon/v1/beacon
# export BEACON_INFO_ENDPOINT=$(BEACON_BASE)/?limit=0
# export BEACON_QUERY_ENDPOINT=$(BEACON_BASE)/query?
# export BEACON_GENOMIC_REGION_ENDPOINT=$(BEACON_BASE)/genomic_region?
# export BEACON_GENOMIC_SNP_ENDPOINT=$(BEACON_BASE)/genomic_snp?
# export BEACON_ACCESS_LEVELS_ENDPOINT=$(BEACON_BASE)/access_levels

####### CSVS @ CRG
export BEACON_BASE=https://egatest.crg.eu/csvs_beacon
export BEACON_INFO_ENDPOINT=$(BEACON_BASE)/?limit=0
export BEACON_QUERY_ENDPOINT=$(BEACON_BASE)/query?
export BEACON_GENOMIC_REGION_ENDPOINT=$(BEACON_BASE)/genomic_region?
export BEACON_GENOMIC_SNP_ENDPOINT=$(BEACON_BASE)/genomic_snp?
export BEACON_ACCESS_LEVELS_ENDPOINT=$(BEACON_BASE)/access_levels

# ####### CSVS @ Sevilla
# export BEACON_BASE=http://dev.clinbioinfosspa.es:9076/elixirbeacon/v1/beacon
# export BEACON_INFO_ENDPOINT=$(BEACON_BASE)/?limit=0
# export BEACON_QUERY_ENDPOINT=$(BEACON_BASE)/query?
# export BEACON_GENOMIC_REGION_ENDPOINT=$(BEACON_BASE)/genomic_region?
# export BEACON_GENOMIC_SNP_ENDPOINT=$(BEACON_BASE)/genomic_snp?
# export BEACON_ACCESS_LEVELS_ENDPOINT=$(BEACON_BASE)/access_levels

# ####### Cafe Variome
# export BEACON_BASE=https://beacondev.cafevariome.org/
# export BEACON_INFO_ENDPOINT=$(BEACON_BASE)/?limit=0
# export BEACON_QUERY_ENDPOINT=$(BEACON_BASE)/query?
# export BEACON_GENOMIC_REGION_ENDPOINT=$(BEACON_BASE)/genomic_region?
# export BEACON_GENOMIC_SNP_ENDPOINT=$(BEACON_BASE)/genomic_snp?
# export BEACON_ACCESS_LEVELS_ENDPOINT=$(BEACON_BASE)/access_levels


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

