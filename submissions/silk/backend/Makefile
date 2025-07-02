SHELL := $(shell echo $$SHELL)

.DEFAULT_GOAL := help

BACKEND_DIR := backend
VENV_DIR := venv

.PHONY: help venv init-sqlite-db install test lint run

help:
	@echo "--------------- HELP ---------------"
	@echo "To install dependencies: make install"
	@echo "To start the backend server: make run"
	@echo "------------------------------------"

install:
	source $(VENV_DIR)/bin/activate && \
	pip install -r requirements.txt
run:
	source $(VENV_DIR)/bin/activate && \
	gunicorn -k gevent -w 1 main:app --bind 0.0.0.0:8000