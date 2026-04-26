from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import analyze

app = FastAPI(
    title="Veritas API",
    description="Bias detection and fairness auditing for ML datasets",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local dev
        "http://localhost:3000",  # Alternative dev
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://veritas-ai-01.web.app",
        "https://veritas-ai-01.firebaseapp.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(analyze.router, prefix="/api")


@app.get("/")
def root():
    return {"status": "Veritas API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
