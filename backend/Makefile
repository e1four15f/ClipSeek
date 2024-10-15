VENV = .venv
CODE = src app.py
# scripts
run:
	@$(VENV)/bin/python app.py

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

lint:
	ruff check $(CODE)
	mypy --install-types --non-interactive $(CODE)

pretty:
	ruff format $(CODE)
	ruff check --fix $(CODE)
