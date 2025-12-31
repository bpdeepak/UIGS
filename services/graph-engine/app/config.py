"""
UIGS Graph Engine - Configuration Module
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server settings
    port: int = 8082
    debug: bool = False
    
    # Neo4j settings
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j_password_2024"
    
    # RabbitMQ settings
    rabbitmq_url: str = "amqp://uigs_rabbit:rabbit_password_2024@localhost:5672/"
    rabbitmq_queue: str = "graph.engine.queue"
    
    # Default user for testing
    default_user_id: str = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
