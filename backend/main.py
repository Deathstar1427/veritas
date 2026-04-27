import os
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.routes import analyze

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Veritas API",
    description="Bias detection and fairness auditing for ML datasets",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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


@app.get("/api/sample/{domain}")
@limiter.limit("30/minute")
async def get_sample_dataset(request: Request, domain: str):
    """
    Serve a pre-built sample CSV for a given domain.
    Enables one-click demo without user needing their own data.
    """
    sample_dir = os.path.join(os.path.dirname(__file__), "sample_datasets")
    filepath = os.path.join(sample_dir, f"{domain}_sample.csv")

    if not os.path.isfile(filepath):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"No sample dataset for domain: {domain}")

    return FileResponse(
        filepath,
        media_type="text/csv",
        filename=f"{domain}_sample.csv",
    )
