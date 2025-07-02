SHELL := $(shell echo $$SHELL)

.DEFAULT_GOAL := help

BACKEND_DIR := backend
FRONTEND_DIR := frontend

.PHONY: help install run install-be run-be install-fe run-fe clean

help:
	@echo "--------------------- HELP ---------------------"
	@echo "  install           Install both backend & frontend dependencies"
	@echo "  run               Run backend (Gunicorn) & frontend concurrently"
	@echo ""
	@echo "Backend:"
	@echo "  install-be        Install backend dependencies"
	@echo "  run-be            Run backend server via Gunicorn"
	@echo ""
	@echo "Frontend:"
	@echo "  install-fe        Install frontend dependencies"
	@echo "  run-fe            Start frontend dev server"
	@echo ""
	@echo "  clean             Remove generated files (venv, node_modules)"
	@echo "-------------------------------------------------"

install: install-be install-fe

install-be:
	$(MAKE) --no-print-directory -C $(BACKEND_DIR) install

install-fe:
	$(MAKE) --no-print-directory -C $(FRONTEND_DIR) install

run: 
	@echo "Starting backend and frontend servers..."
	@trap 'kill $(jobs -p)' INT; \
	($(MAKE) run-be 2>&1 | sed 's/^/[BACKEND] /' ) & \
	($(MAKE) run-fe 2>&1 | sed 's/^/[FRONTEND] /' ) & \
	wait

run-be:
	$(MAKE) --no-print-directory -C $(BACKEND_DIR) run

run-fe:
	$(MAKE) --no-print-directory -C $(FRONTEND_DIR) run

clean:
	@echo "Cleaning backend and frontend..."
	$(MAKE) --no-print-directory -C $(BACKEND_DIR) clean
	$(MAKE) --no-print-directory -C $(FRONTEND_DIR) clean
