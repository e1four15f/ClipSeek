VENV = .venv
CODE = backend src scripts

run:
	@$(VENV)/bin/python -m streamlit run src/app.py --server.enableCORS=true


lint:
	ruff check $(CODE)
	# mypy is too strict
	# mypy --install-types --non-interactive $(CODE)


pretty:
	ruff format $(CODE)
	ruff check --fix $(CODE)
