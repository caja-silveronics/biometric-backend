from sqlmodel import create_engine, SQLModel, Session
import os

# Get DB URL from env or use sqlite for local dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./biometric.db")

# Fix for postgres protocol if needed (some providers use postgres:// instead of postgresql://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=True)

from sqlalchemy import text

def run_migrations():
    results = []
    
    # Run cleanup in its own transaction first
    try:
        with engine.connect() as conn:
            if "postgres" in str(engine.url) or "postgresql" in str(engine.url):
                try:
                    # Fix: Cast to TEXT before using LIKE operator since work_schedule might be JSON or UNKNOWN
                    conn.execute(text("UPDATE employee SET work_schedule = NULL WHERE work_schedule::text NOT LIKE '{%' AND work_schedule::text NOT LIKE '[%';"))
                    conn.commit()
                    results.append("🧹 Cleaned up invalid work_schedule data (set to NULL)")
                except Exception as e_clean:
                    results.append(f"⚠️ Cleanup warning: {e_clean}")
    except Exception as e:
        results.append(f"⚠️ Cleanup Connection error: {e}")

    # Run remaining migrations in a new connection/transaction
    try:
        with engine.connect() as conn:
            # Branches
            try:
                conn.execute(text("ALTER TABLE branch ADD COLUMN IF NOT EXISTS phone VARCHAR;"))
                conn.commit()
                results.append("✅ Added phone to branch")
            except Exception as e: 
                results.append(f"⚠️ phone error: {e}")
                # Don't abort entire block, continue

            try:
                conn.execute(text("ALTER TABLE branch ADD COLUMN IF NOT EXISTS city VARCHAR;"))
                conn.commit()
                results.append("✅ Added city to branch")
            except Exception as e: results.append(f"⚠️ city error: {e}")

            try:
                conn.execute(text("ALTER TABLE branch ADD COLUMN IF NOT EXISTS code VARCHAR;"))
                conn.commit()
                results.append("✅ Added code to branch")
            except Exception as e: results.append(f"⚠️ code error: {e}")
            
            # Employees
            try:
                conn.execute(text("ALTER TABLE employee ADD COLUMN IF NOT EXISTS position VARCHAR;"))
                conn.commit()
                results.append("✅ Added position to employee")
            except Exception as e: results.append(f"⚠️ position error: {e}")

            try:
                conn.execute(text("ALTER TABLE employee ADD COLUMN IF NOT EXISTS department VARCHAR;"))
                conn.commit()
                results.append("✅ Added department to employee")
            except Exception as e: results.append(f"⚠️ department error: {e}")

            try:
                # 1. work_schedule
                conn.execute(text("ALTER TABLE employee ADD COLUMN IF NOT EXISTS work_schedule JSON;"))
                conn.commit()
                results.append("✅ Added work_schedule (JSON) to employee")
            except Exception as e: results.append(f"⚠️ work_schedule error: {e}")

            try:
                # 2. photo_url
                conn.execute(text("ALTER TABLE employee ADD COLUMN IF NOT EXISTS photo_url TEXT;"))
                conn.commit()
                results.append("✅ Added photo_url (TEXT) to employee")
            except Exception as e: results.append(f"⚠️ photo_url error: {e}")

            try:
                # 3. face_embedding
                conn.execute(text("ALTER TABLE employee ADD COLUMN IF NOT EXISTS face_embedding JSON;"))
                conn.commit()
                results.append("✅ Added face_embedding (JSON) to employee")
            except Exception as e: results.append(f"⚠️ face_embedding error: {e}")

            # FIX: Force ALTER columns
            if "postgres" in str(engine.url) or "postgresql" in str(engine.url):
                try:
                    conn.execute(text("ALTER TABLE employee ALTER COLUMN photo_url TYPE TEXT;"))
                    conn.commit()
                    results.append("✅ photo_url forced to TEXT")
                except Exception as e: results.append(f"⚠️ photo_url type error: {e}")

                try:
                    conn.execute(text("ALTER TABLE employee ALTER COLUMN work_schedule TYPE JSON USING work_schedule::json;"))
                    conn.commit()
                    results.append("✅ work_schedule forced to JSON")
                except Exception as e: results.append(f"⚠️ work_schedule type error: {e}")
                
                try:
                    conn.execute(text("ALTER TABLE employee ALTER COLUMN face_embedding TYPE JSON USING face_embedding::json;"))
                    conn.commit()
                    results.append("✅ face_embedding forced to JSON")
                except Exception as e: results.append(f"⚠️ face_embedding type error: {e}")

            results.append("🏁 Migration run complete")
    except Exception as e:
        results.append(f"❌ Critical migration error: {e}")
    
    return results

def init_db():
    SQLModel.metadata.create_all(engine)
    logs = run_migrations()
    for log in logs:
        print(log)

def get_session():
    with Session(engine) as session:
        yield session
