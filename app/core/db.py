from sqlmodel import create_engine, SQLModel, Session
import os

# Get DB URL from env or use sqlite for local dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./biometric.db")

# Fix for postgres protocol if needed (some providers use postgres:// instead of postgresql://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=True)

from sqlalchemy import text

def init_db():
    SQLModel.metadata.create_all(engine)
    # Manual migration for new columns
    with engine.connect() as conn:
        try:
            # Branches
            conn.execute(text("ALTER TABLE branch ADD COLUMN IF NOT EXISTS phone VARCHAR;"))
            conn.execute(text("ALTER TABLE branch ADD COLUMN IF NOT EXISTS city VARCHAR;"))
            
            # Employees
            conn.execute(text("ALTER TABLE employee ADD COLUMN IF NOT EXISTS position VARCHAR;"))
            conn.execute(text("ALTER TABLE employee ADD COLUMN IF NOT EXISTS department VARCHAR;"))
            conn.execute(text("ALTER TABLE employee ADD COLUMN IF NOT EXISTS work_schedule VARCHAR;"))
            conn.execute(text("ALTER TABLE employee ADD COLUMN IF NOT EXISTS photo_url TEXT;")) # Use TEXT for base64
            
            conn.commit() 
            print("✅ Schema migrations checked/applied")
        except Exception as e:
            print(f"⚠️ Migration warning: {e}")

def get_session():
    with Session(engine) as session:
        yield session
