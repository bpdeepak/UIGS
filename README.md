# Unified Identity Graph System (UIGS)

A user-centric identity management platform that represents digital identity as a time-evolving knowledge graph. UIGS ingests fragmented identity data from multiple sources, unifies them, and enables users to reason about, manage, and selectively disclose their identity.

## 🏗️ Project Status

**Current Phase:** Phase 1 - Foundation ✅

| Phase | Name | Status |
|-------|------|--------|
| 1 | Foundation (Infrastructure + Ingestion) | ✅ Implemented |
| 2 | Unification (Graph Engine) | 🔜 Planned |
| 3 | Experience (Frontend Dashboard) | 🔜 Planned |
| 4 | Intelligence (AI/Privacy Features) | 🔜 Planned |

## 🚀 Quick Start

### Prerequisites

- Docker 24.x+
- Docker Compose 2.x+
- Go 1.21+ (for local development)
- Git

### 1. Clone and Configure

```bash
# Clone repository
git clone <repository-url>
cd Digital-Identity-Fragmentation

# Create environment file
cp .env.example .env

# Generate JWT secret
echo "JWT_SECRET=$(openssl rand -hex 32)" >> .env
```

### 2. Start Services

```bash
# Start all services
make up

# Or using docker compose directly
docker compose up -d
```

### 3. Verify Setup

```bash
# Check health
curl http://localhost:8081/health

# Test ingestion
make test-api
```

## 📁 Project Structure

```
.
├── docker-compose.yml          # Container orchestration
├── Makefile                    # Development commands
├── .env.example                # Environment template
│
├── docs/                       # Documentation
│   ├── abstract.txt            # Project abstract
│   ├── introduction.txt        # Detailed introduction
│   ├── literature_survey_extended.txt  # 25-paper survey
│   ├── srs.txt                 # Software Requirements (IEEE 830)
│   ├── architecture_design.txt # System architecture
│   ├── project_phase_plan.txt  # 4-phase roadmap
│   └── implementation_plan.txt # Detailed specs
│
├── services/
│   ├── ingestion/              # Go Ingestion Service ✅
│   │   ├── cmd/server/         # Entry point
│   │   └── internal/           # Core packages
│   ├── graph-engine/           # Python Graph Engine (Phase 2)
│   └── frontend/               # Next.js Dashboard (Phase 3)
│
├── infra/
│   ├── docker/                 # Docker configurations
│   │   ├── postgres/init.sql   # Database schema
│   │   ├── neo4j/              # Neo4j config
│   │   └── rabbitmq/           # RabbitMQ config
│   └── k8s/                    # Kubernetes manifests
│
└── data/
    └── samples/                # Sample VCs for testing
```

## 🔌 API Reference

### Ingestion Service (Port 8081)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/ready` | GET | Readiness check |
| `/api/v1/ingest` | POST | Ingest a credential |
| `/api/v1/events` | GET | List user events |
| `/api/v1/events/:id` | GET | Get event by ID |

### Ingest Credential

```bash
curl -X POST http://localhost:8081/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "VC",
    "payload": {
      "@context": ["https://www.w3.org/2018/credentials/v1"],
      "type": ["VerifiableCredential"],
      "issuer": "did:example:university",
      "issuanceDate": "2024-01-01T00:00:00Z",
      "credentialSubject": {
        "name": "John Doe",
        "degree": "Computer Science"
      }
    }
  }'
```

**Response:**
```json
{
  "event_id": "uuid",
  "status": "accepted",
  "message": "Credential ingested successfully",
  "created_at": "2024-12-31T18:00:00Z"
}
```

## 🛠️ Development

### Local Development

```bash
# Start infrastructure only
make dev

# Run Go service locally
cd services/ingestion
go run cmd/server/main.go
```

### Available Commands

```bash
make help       # Show all commands
make up         # Start all services
make down       # Stop all services
make logs       # View logs
make build      # Build images
make clean      # Remove containers and volumes
make test       # Run tests
make test-api   # Test API with curl
make seed       # Ingest sample credentials
```

## 🏢 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     UIGS Architecture                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  Ingestion  │───▶│  RabbitMQ   │───▶│   Graph     │     │
│  │  (Go)       │    │             │    │   Engine    │     │
│  │  :8081      │    │  :5672      │    │  (Python)   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                                     │             │
│         ▼                                     ▼             │
│  ┌─────────────┐                       ┌─────────────┐     │
│  │  PostgreSQL │                       │   Neo4j     │     │
│  │  (Audit)    │                       │   (Graph)   │     │
│  │  :5432      │                       │  :7474/7687 │     │
│  └─────────────┘                       └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Service Endpoints

| Service | Port | UI |
|---------|------|----|
| Ingestion API | 8081 | - |
| Graph Engine | 8082 | - |
| Frontend | 3000 | http://localhost:3000 |
| Neo4j Browser | 7474 | http://localhost:7474 |
| RabbitMQ Mgmt | 15672 | http://localhost:15672 |
| PostgreSQL | 5432 | - |

## 📚 Documentation

See the `docs/` folder for comprehensive documentation:

- **[Abstract](docs/abstract.txt)** - Executive summary
- **[Introduction](docs/introduction.txt)** - Problem context and solution
- **[Literature Survey](docs/literature_survey_extended.txt)** - 25 papers analyzed
- **[SRS](docs/srs.txt)** - IEEE 830 requirements
- **[Architecture](docs/architecture_design.txt)** - System design
- **[Phase Plan](docs/project_phase_plan.txt)** - Implementation roadmap
- **[Implementation](docs/implementation_plan.txt)** - Detailed specs

## 📄 License

This project is developed for academic purposes.

---

**Phase 1 Acceptance Criteria:**
- [✅] docker-compose up starts all services without errors
- [✅] POST /api/v1/ingest returns 201 with valid JSON payload
- [✅] Payload is visible in PostgreSQL ingestion_events table
- [✅] Message is visible in RabbitMQ queue (via management UI)
