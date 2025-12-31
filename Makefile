# ============================================================================
# UIGS Makefile
# ============================================================================

.PHONY: help up down logs build test clean dev

# Default target
help:
	@echo "UIGS - Unified Identity Graph System"
	@echo ""
	@echo "Available commands:"
	@echo "  make up        - Start all services (docker-compose up -d)"
	@echo "  make down      - Stop all services (docker-compose down)"
	@echo "  make logs      - View service logs (docker-compose logs -f)"
	@echo "  make build     - Build all service images"
	@echo "  make clean     - Remove all containers and volumes"
	@echo "  make dev       - Start infrastructure only (for local dev)"
	@echo "  make test      - Run all tests"
	@echo "  make test-api  - Test API endpoints with curl"
	@echo ""

# Start all services
up:
	docker compose up -d
	@echo ""
	@echo "Services started. Access points:"
	@echo "  - Ingestion API: http://localhost:8081"
	@echo "  - Neo4j Browser: http://localhost:7474"
	@echo "  - RabbitMQ Mgmt: http://localhost:15672"
	@echo ""

# Stop all services
down:
	docker compose down

# View logs
logs:
	docker compose logs -f

# Build images
build:
	docker compose build

# Clean up everything
clean:
	docker compose down -v --rmi local
	@echo "Cleaned up containers, volumes, and local images"

# Start infrastructure only (for local development)
dev:
	docker compose up -d postgres neo4j rabbitmq
	@echo ""
	@echo "Infrastructure started. Now run the Go service locally:"
	@echo "  cd services/ingestion && go run cmd/server/main.go"
	@echo ""

# Run tests
test:
	@echo "Running Go tests..."
	cd services/ingestion && go test -v ./...

# Test API endpoints
test-api:
	@echo "Testing health endpoint..."
	curl -s http://localhost:8081/health | jq .
	@echo ""
	@echo "Testing ingest endpoint..."
	curl -s -X POST http://localhost:8081/api/v1/ingest \
		-H "Content-Type: application/json" \
		-d '{"source_type": "VC", "payload": {"@context": ["https://www.w3.org/2018/credentials/v1"], "type": ["VerifiableCredential"], "issuer": "did:example:test", "issuanceDate": "2024-01-01T00:00:00Z", "credentialSubject": {"name": "Test User"}}}' | jq .
	@echo ""

# Initialize Go modules
go-init:
	cd services/ingestion && go mod tidy

# Seed sample data
seed:
	@echo "Ingesting sample credentials..."
	@for file in data/samples/*.json; do \
		echo "Ingesting: $$file"; \
		curl -s -X POST http://localhost:8081/api/v1/ingest \
			-H "Content-Type: application/json" \
			-d "{\"source_type\": \"VC\", \"payload\": $$(cat $$file)}" | jq .; \
	done
