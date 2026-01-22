# ============================================================================
# UIGS Makefile - Unified Identity Graph System
# ============================================================================

.PHONY: help up down logs build test clean dev frontend graph-engine

# Default target
help:
	@echo "UIGS - Unified Identity Graph System"
	@echo ""
	@echo "Core Commands:"
	@echo "  make up           - Start all services (docker-compose up -d)"
	@echo "  make down         - Stop all services"
	@echo "  make logs         - View all service logs"
	@echo "  make build        - Build all service images"
	@echo "  make clean        - Remove all containers and volumes"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start infrastructure only (for local dev)"
	@echo "  make test         - Run all tests"
	@echo "  make test-api     - Test API endpoints with curl"
	@echo "  make seed         - Ingest sample credentials"
	@echo ""
	@echo "Service-Specific:"
	@echo "  make logs-ingestion     - View ingestion service logs"
	@echo "  make logs-graph-engine  - View graph engine logs"
	@echo "  make logs-frontend      - View frontend logs"
	@echo "  make test-graphql       - Test GraphQL queries"
	@echo "  make process            - Process pending queue messages"
	@echo ""

# ============================================================================
# Core Commands
# ============================================================================

# Start all services
up:
	docker compose up -d
	@echo ""
	@echo "✅ All services started. Access points:"
	@echo "  - Frontend:       http://localhost:3000"
	@echo "  - Ingestion API:  http://localhost:8081"
	@echo "  - GraphQL API:    http://localhost:8082/graphql"
	@echo "  - Neo4j Browser:  http://localhost:7474"
	@echo "  - RabbitMQ Mgmt:  http://localhost:15672"
	@echo ""

# Stop all services
down:
	docker compose down

# View all logs
logs:
	docker compose logs -f

# Build all images
build:
	docker compose build

# Clean up everything
clean:
	docker compose down -v --rmi local
	@echo "Cleaned up containers, volumes, and local images"

# ============================================================================
# Development
# ============================================================================

# Start infrastructure only (for local development)
dev:
	docker compose up -d postgres neo4j rabbitmq
	@echo ""
	@echo "Infrastructure started. Now run services locally:"
	@echo "  Ingestion:    cd services/ingestion && go run cmd/server/main.go"
	@echo "  Graph Engine: cd services/graph-engine && uvicorn main:app --port 8082"
	@echo "  Frontend:     cd services/frontend && npm run dev"
	@echo ""

# Run all tests
test: test-go test-python
	@echo "All tests completed"

# Run Go tests
test-go:
	@echo "Running Go tests..."
	cd services/ingestion && go test -v ./...

# Run Python tests
test-python:
	@echo "Running Python tests..."
	docker exec uigs-graph-engine python -m pytest tests/ -v

# ============================================================================
# API Testing
# ============================================================================

# Test ingestion API
test-api:
	@echo "Testing ingestion health..."
	@curl -s http://localhost:8081/health | jq .
	@echo ""
	@echo "Testing graph-engine health..."
	@curl -s http://localhost:8082/health | jq .
	@echo ""
	@echo "Testing ingest endpoint..."
	@curl -s -X POST http://localhost:8081/api/v1/ingest \
		-H "Content-Type: application/json" \
		-d '{"source_type": "VC", "payload": {"@context": ["https://www.w3.org/2018/credentials/v1"], "type": ["VerifiableCredential"], "issuer": "did:example:test", "issuanceDate": "2024-01-01T00:00:00Z", "credentialSubject": {"name": "Test User"}}}' | jq .
	@echo ""

# Test GraphQL queries
test-graphql:
	@echo "Testing GraphQL identity graph query..."
	@curl -s -X POST http://localhost:8082/graphql \
		-H "Content-Type: application/json" \
		-d '{"query":"{ identityGraph { nodeCount edgeCount } }"}' | jq .
	@echo ""
	@echo "Testing GraphQL conflicts query..."
	@curl -s -X POST http://localhost:8082/graphql \
		-H "Content-Type: application/json" \
		-d '{"query":"{ conflicts { attribute claimAValue claimBValue } }"}' | jq .
	@echo ""

# Process pending queue messages
process:
	@echo "Processing pending events..."
	@curl -s -X POST http://localhost:8082/process | jq .

# Seed sample data
seed:
	@echo "Ingesting sample credentials..."
	@for file in data/samples/*.json; do \
		echo "Ingesting: $$file"; \
		curl -s -X POST http://localhost:8081/api/v1/ingest \
			-H "Content-Type: application/json" \
			-d "{\"source_type\": \"VC\", \"payload\": $$(cat $$file)}" | jq .; \
	done
	@echo ""
	@echo "Processing events..."
	@curl -s -X POST http://localhost:8082/process | jq .

# ============================================================================
# Service-Specific Logs
# ============================================================================

logs-ingestion:
	docker logs -f uigs-ingestion

logs-graph-engine:
	docker logs -f uigs-graph-engine

logs-frontend:
	docker logs -f uigs-frontend

logs-neo4j:
	docker logs -f uigs-neo4j

logs-rabbitmq:
	docker logs -f uigs-rabbitmq

# ============================================================================
# Neo4j Queries
# ============================================================================

# Show graph stats in Neo4j
neo4j-stats:
	@echo "Node counts:"
	@docker exec uigs-neo4j cypher-shell -u neo4j -p neo4j_password_2024 \
		"MATCH (n) RETURN labels(n)[0] AS Type, count(*) AS Count ORDER BY Count DESC;"
	@echo ""
	@echo "Edge counts:"
	@docker exec uigs-neo4j cypher-shell -u neo4j -p neo4j_password_2024 \
		"MATCH ()-[r]->() RETURN type(r) AS Type, count(*) AS Count ORDER BY Count DESC;"

# Clear all Neo4j data
neo4j-clear:
	@echo "Clearing all Neo4j data..."
	@docker exec uigs-neo4j cypher-shell -u neo4j -p neo4j_password_2024 \
		"MATCH (n) DETACH DELETE n;"
	@echo "Done"

# ============================================================================
# Initialize/Setup
# ============================================================================

# Initialize Go modules
go-init:
	cd services/ingestion && go mod tidy

# Initialize Python environment
py-init:
	cd services/graph-engine && pip install -r requirements.txt

# Initialize Frontend
npm-init:
	cd services/frontend && npm install

# Open frontend in browser
open:
	@xdg-open http://localhost:3000 2>/dev/null || open http://localhost:3000 2>/dev/null || echo "Open http://localhost:3000 in your browser"
