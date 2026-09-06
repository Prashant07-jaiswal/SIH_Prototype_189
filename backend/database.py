import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite database setup (lightweight and requires no setup for hackathons)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "security_platform.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Add check_same_thread=False for SQLite in FastAPI to prevent multi-threading connection issues
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_utc_now():
    return datetime.now(timezone.utc)

# ---------------------------------------------------------
# Database Schema
# ---------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="investigator")  # e.g., admin, investigator
    created_at = Column(DateTime, default=get_utc_now)


class EvidenceLog(Base):
    """
    Acts as an immutable 'Blockchain Ledger' simulator by storing the SHA-256 hash
    of uploaded evidence to guarantee tamper-proof audit trails for forensic admissibility.
    """
    __tablename__ = "evidence_ledger"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50))  # e.g., 'fir', 'cdr', 'transaction'
    uploader_id = Column(Integer, nullable=False)  # Maps to User.id
    sha256_hash = Column(String(64), nullable=False, index=True)
    timestamp = Column(DateTime, default=get_utc_now)


# Create tables if they do not exist
Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------
# FastAPI DB Session Dependency
# ---------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
