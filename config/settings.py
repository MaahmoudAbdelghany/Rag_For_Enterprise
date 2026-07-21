import os
from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings class parsing configuration from environment variables / .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Company & App Config
    COMPANY_NAME: str = "FinSolve Technologies"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # LLM Config
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = Field(default="", description="Groq API Key")
    GROQ_MODEL: str = "llama-3.1-70b-versatile"

    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = None

    # Qdrant Vector DB
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "enterprise_rag"

    # Embedding Model
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Guardrails & PII
    PII_ANONYMIZATION_ENABLED: bool = True
    PII_ENTITIES: List[str] = [
        "PERSON",
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "US_SSN",
        "CREDIT_CARD",
    ]

    # LangSmith Tracing
    LANGSMITH_TRACING: bool = True
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "enterprise-rag-chatbot"


@lru_cache()
def get_settings() -> Settings:
    """
    Cached accessor function to get application settings singleton.
    """
    return Settings()
