import io
import logging

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from auth_middleware import verify_token
from firebase_admin_init import init_firebase
from app.domain_config import DOMAIN_CONFIG
from app.services.bias_service import detect_bias
from app.services.gemini_service import explain_bias
from app.services.pdf_generator import generate_pdf_report

router = APIRouter()
logger = logging.getLogger(__name__)

init_firebase()


@router.get("/domains")
def get_domains():
    """Returns available domains and their config."""
    return {
        domain: {
            "description": config["description"],
            "protected_attributes": config["protected_attributes"],
            "outcome_column": config["outcome_column"],
        }
        for domain, config in DOMAIN_CONFIG.items()
    }


@router.post("/analyze")
async def analyze_csv(
    file: UploadFile = File(...),
    domain: str = Form(...),
    uid: str = Depends(verify_token),
):
    """
    Main endpoint.
    Receives a CSV file + domain name.
    Returns bias metrics + Gemini explanation.
    """
    MAX_FILE_SIZE = 10 * 1024 * 1024
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is 10MB, received {file.size / 1024 / 1024:.2f}MB",
        )

    filename = (file.filename or "").strip()
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    if domain not in DOMAIN_CONFIG:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid domain. Choose from: {list(DOMAIN_CONFIG.keys())}",
        )

    try:
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 10MB, received {len(contents) / 1024 / 1024:.2f}MB",
            )
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=400, detail="CSV file is empty.")

    try:
        bias_results = detect_bias(df, domain)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bias analysis failed: {str(e)}")

    try:
        explanation = explain_bias(bias_results)
    except Exception:
        explanation = "Explanation unavailable — check your GEMINI_API_KEY."

    return {"status": "success", "results": bias_results, "explanation": explanation}


@router.post("/export")
async def export_pdf(data: dict):
    """
    Generate and download PDF report from bias results.
    Expects: {"bias_results": {...}, "gemini_explanation": "..."}
    """
    try:
        bias_results = data.get("bias_results")
        gemini_explanation = data.get("gemini_explanation", "")

        if not bias_results:
            raise HTTPException(status_code=400, detail="bias_results required")

        pdf_bytes = generate_pdf_report(bias_results, gemini_explanation)

        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=veritas_report.pdf"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
