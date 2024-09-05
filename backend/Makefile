VENV = .venv
CODE = . ../scripts

run:
	@$(VENV)/bin/python -m streamlit run old_frontend/app.py --server.enableCORS=true


PYTHONPATH=. python scripts/index_dataset.py \
--data-path 'data/MSRVTT' \
--media-path 'data/MSRVTT/5sec' \
--modality 'audio' \
--device 'cpu'

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

lint:
	ruff check $(CODE)
	# mypy is too strict
	# mypy --install-types --non-interactive $(CODE)


pretty:
	ruff format $(CODE)
	ruff check --fix $(CODE)
