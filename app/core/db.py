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
            conn.execute(text("ALTER TABLE branch ADD COLUMN IF NOT EXISTS code VARCHAR;"))
            
            # Employees
            conn.execute(text("ALTER TABLE employee ADD COLUMN IF NOT EXISTS position VARCHAR;"))
            conn.execute(text("ALTER TABLE employee ADD COLUMN IF NOT EXISTS department VARCHAR;"))
            
            # 1. work_schedule
            # Primero aseguramos que exista
            conn.execute(text("ALTER TABLE employee ADD COLUMN IF NOT EXISTS work_schedule JSON;")) # Intenta crear como JSON directo
            
            # 2. photo_url
            conn.execute(text("ALTER TABLE employee ADD COLUMN IF NOT EXISTS photo_url TEXT;"))
            
            # 3. face_embedding
            conn.execute(text("ALTER TABLE employee ADD COLUMN IF NOT EXISTS face_embedding JSON;"))

            # FIX: Force ALTER columns to ensure correct types (in case they existed as VARCHAR)
            if "postgres" in str(engine.url) or "postgresql" in str(engine.url):
                try:
                    # Enforce photo_url is TEXT (unlimited length) not VARCHAR
                    conn.execute(text("ALTER TABLE employee ALTER COLUMN photo_url TYPE TEXT;"))
                    print("✅ photo_url forced to TEXT")

                    # Enforce work_schedule is JSON. This might fail if data is invalid, so catch it.
                    # 'USING work_schedule::json' is needed if it was text.
                    # If it was already JSON, this is a no-op usually or safe.
                    # If it was empty text '', it fails. Handle that?
                    # Let's try a safe approach:
                    conn.execute(text("ALTER TABLE employee ALTER COLUMN work_schedule TYPE JSON USING work_schedule::json;"))
                    print("✅ work_schedule forced to JSON")

                    # Enforce face_embedding is JSON.
                    conn.execute(text("ALTER TABLE employee ALTER COLUMN face_embedding TYPE JSON USING face_embedding::json;"))
                    print("✅ face_embedding forced to JSON")

                except Exception as e_alter:
                     print(f"⚠️ Column type enforcement warning: {e_alter}")

            conn.commit() 
            print("✅ Schema migrations checked/applied")
        except Exception as e:
            print(f"⚠️ Migration warning: {e}")

def get_session():
    with Session(engine) as session:
        yield session
