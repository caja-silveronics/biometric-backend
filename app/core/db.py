from sqlmodel import create_engine, SQLModel, Session
import os

# Get DB URL from env or use sqlite for local dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./biometric.db")

# Fix for postgres protocol if needed (some providers use postgres:// instead of postgresql://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
