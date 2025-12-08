from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.db import init_db
from app.api.v1.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    yield

app = FastAPI(
    title="Biometrico API",
    description="API for Biometric Attendance System",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS (Permitir que el dashboard y la app se conecten)
origins = [
    "*", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Biometrico API is running 🚀", "status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
