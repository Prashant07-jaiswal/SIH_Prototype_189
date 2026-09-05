"""
Criminal Network Analysis System - FastAPI Backend
Core configuration and settings
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # FastAPI
    app_name: str = "Criminal Network Analysis API"
    app_version: str = "0.1.0"
    debug: bool = True

    # LLM Configuration (Groq)
    groq_api_key: str = ""  # Load from .env
    groq_model: str = "llama-3.3-70b-versatile"

    # Data paths
    data_dir: Path = Path(__file__).parent.parent / "synthetic_data"
    fir_folder: Path = data_dir / "FIRs"
    cdr_file: Path = data_dir / "call_detail_records.csv"
    transaction_file: Path = data_dir / "financial_transactions.csv"
    metadata_file: Path = data_dir / "metadata.json"

    # Processing
    max_upload_size: int = 100 * 1024 * 1024  # 100 MB
    extraction_batch_size: int = 10
    entity_similarity_threshold: float = 0.88

    # Neo4j (for future use)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
