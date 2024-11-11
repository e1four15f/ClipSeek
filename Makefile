export VERSION=0.1

build:
	docker-compose build

push:
	docker-compose push

pull:
	docker-compose pull

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-%:
	docker-compose logs -f $(subst logs-,,$@)

scripts: pull
	docker-compose run --entrypoint /bin/bash backend
