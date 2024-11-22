build:
	docker compose build

pull:
	docker compose pull

up:
	docker compose up -d

logs:
	docker compose logs -f frontend backend attu

scripts:
	docker compose run --entrypoint /bin/bash backend
