VENV = .venv
CODE = src scripts app.py

run:
	@$(VENV)/bin/python -m streamlit run app.py


lint:
	ruff check $(CODE)
	# mypy is too strict
	# mypy --install-types --non-interactive $(CODE)


pretty:
	ruff format $(CODE)
	ruff check --fix $(CODE)
