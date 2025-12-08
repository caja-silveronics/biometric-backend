from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Biometrico API",
    description="API for Biometric Attendance System",
    version="1.0.0"
)

# Configurar CORS (Permitir que el dashboard y la app se conecten)
origins = [
    "*", # Por ahora permitimos todo para facilitar el desarrollo
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Biometrico API is running 🚀", "status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
