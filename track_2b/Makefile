.PHONY: run test eval clean build lint

# Primary Hack Apertus Track 2B launch target
run:
	@echo "Starting RelayZero in container..."
	docker compose up --build

test:
	@echo "Running RelayZero test suite with air-gap egress zero assertions..."
	pytest src/backend/tests -v -o asyncio_mode=auto --cov=src/backend

eval:
	@echo "Running reproducible 48-incident evaluation benchmark..."
	python src/backend/evaluation_runner.py

build:
	@echo "Building frontend and generating report PDF..."
	cd src/frontend && npm install && npm run build
	python generate_pdf.py

clean:
	@echo "Cleaning temporary build artifacts..."
	rm -rf src/frontend/dist src/frontend/node_modules .pytest_cache
