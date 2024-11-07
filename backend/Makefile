VENV = .venv
CODE = src app.py scripts

run:
	@$(VENV)/bin/python app.py

lint:
	@$(VENV)/bin/ruff check $(CODE)
	@$(VENV)/bin/mypy --install-types --non-interactive $(CODE)

pretty:
	@$(VENV)/bin/ruff format $(CODE)
	@$(VENV)/bin/ruff check --fix $(CODE)
