from sqlmodel import Session, delete
from app.core.db import engine
from app.models.models import Attendance

def clear_attendance():
    print("Clearing all attendance records...")
    try:
        with Session(engine) as session:
            statement = delete(Attendance)
            result = session.exec(statement)
            session.commit()
            print(f"Executed. Rows affected: {result.rowcount if hasattr(result, 'rowcount') else 'Unknown'}")
            
            # Double check
            from sqlmodel import select
            count = len(session.exec(select(Attendance)).all())
            print(f"Remaining records: {count}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clear_attendance()
