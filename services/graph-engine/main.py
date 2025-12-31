"""
UIGS Graph Engine - Main Application

FastAPI application with GraphQL endpoint and RabbitMQ consumer.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.config import get_settings
from app.graph import Neo4jClient
from app.consumer import RabbitMQConsumer
from app.api import create_schema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global instances
settings = get_settings()
neo4j_client: Neo4jClient | None = None
consumer: RabbitMQConsumer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global neo4j_client, consumer
    
    logger.info("Starting UIGS Graph Engine...")
    
    # Initialize Neo4j client
    neo4j_client = Neo4jClient(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
    )
    await neo4j_client.connect()
    
    # Initialize RabbitMQ consumer
    consumer = RabbitMQConsumer(settings, neo4j_client)
    await consumer.connect()
    
    # Create GraphQL schema with dependencies injected
    schema = create_schema(neo4j_client, consumer)
    graphql_app = GraphQLRouter(schema)
    app.include_router(graphql_app, prefix="/graphql")
    
    logger.info(f"Graph Engine started on port {settings.port}")
    logger.info(f"GraphQL endpoint: http://localhost:{settings.port}/graphql")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    await consumer.close()
    await neo4j_client.close()
    logger.info("Graph Engine stopped")


# Create FastAPI app
app = FastAPI(
    title="UIGS Graph Engine",
    description="Graph Reasoning Engine for the Unified Identity Graph System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "graph-engine",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    neo4j_ready = False
    rabbitmq_ready = False
    
    try:
        if neo4j_client and neo4j_client._driver:
            await neo4j_client._driver.verify_connectivity()
            neo4j_ready = True
    except Exception as e:
        logger.error(f"Neo4j not ready: {e}")
    
    try:
        if consumer and consumer.connection and not consumer.connection.is_closed:
            rabbitmq_ready = True
    except Exception as e:
        logger.error(f"RabbitMQ not ready: {e}")
    
    ready = neo4j_ready and rabbitmq_ready
    
    return {
        "ready": ready,
        "neo4j": "ready" if neo4j_ready else "not_ready",
        "rabbitmq": "ready" if rabbitmq_ready else "not_ready",
    }


@app.post("/process")
async def process_events(max_messages: int = 100):
    """Manually trigger processing of pending events."""
    if not consumer:
        return {"error": "Consumer not initialized"}
    
    try:
        processed = await consumer.process_pending(max_messages)
        return {
            "success": True,
            "messages_processed": processed,
        }
    except Exception as e:
        logger.error(f"Error processing events: {e}")
        return {
            "success": False,
            "error": str(e),
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
    )
