run:
	poetry run python -m backend.main

install:
	poetry install

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test:
	poetry run pytest