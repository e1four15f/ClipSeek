build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-%:
	docker-compose logs -f $(subst logs-,,$@)

scripts:
	docker-compose run --entrypoint /bin/bash backend
