# Pricy Price Tracker - Makefile
# Cross-platform commands for development workflow

.PHONY: install dev test lint docker clean help

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Pricy Price Tracker - Available Commands"
	@echo "========================================"
	@echo ""
	@echo "  make install    Install backend and frontend dependencies"
	@echo "  make dev        Start backend and frontend in development mode"
	@echo "  make test       Run backend and frontend tests"
	@echo "  make lint       Lint backend and frontend code"
	@echo "  make docker     Start services with Docker Compose"
	@echo "  make clean      Clean up generated files and caches"
	@echo ""

install: ## Install all dependencies
	@echo "Installing backend dependencies..."
	python -m pip install -r backend/requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Done. Run 'make dev' to start development servers."

dev: ## Start backend and frontend development servers
	@echo "Starting development servers..."
	@echo "Backend will be available at http://localhost:8000"
	@echo "Frontend will be available at http://localhost:5173"
	start start-backend.bat
	start start-frontend.bat

test: ## Run all tests
	@echo "Running backend tests..."
	python -m pytest backend/tests -v
	@echo "Running frontend checks..."
	cd frontend && npm run lint

lint: ## Lint all code
	@echo "Linting backend with ruff..."
	ruff check backend/ src/ || echo "Install ruff: pip install ruff"
	@echo "Linting frontend..."
	cd frontend && npm run lint

docker: ## Start services with Docker Compose
	@echo "Starting services with Docker Compose..."
	docker-compose up --build

clean: ## Clean up generated files and caches
	@echo "Cleaning up..."
	rm -rf backend/__pycache__
	rm -rf backend/app/__pycache__
	rm -rf backend/tests/__pycache__
	rm -rf src/__pycache__
	rm -rf .pytest_cache
	rm -rf frontend/node_modules/.cache
	@echo "Cleanup complete."
