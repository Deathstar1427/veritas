import io
import json
import logging

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse, Response
from slowapi import Limiter
from slowapi.util import get_remote_address

from auth_middleware import verify_token
from firebase_admin_init import init_firebase
from app.domain_config import DOMAIN_CONFIG
from app.services.bias_service import detect_bias, detect_proxy_columns
from app.services.gemini_service import explain_bias, generate_model_card
from app.services.pdf_generator import generate_pdf_report

router = APIRouter()
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

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
@limiter.limit("10/minute")
async def analyze_csv(
    request: Request,
    file: UploadFile = File(...),
    domain: str = Form(...),
    uid: str = Depends(verify_token),
):
    """
    Main endpoint.
    Receives a CSV file + domain name.
    Returns bias metrics + Gemini explanation + remediation + proxy columns.
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

    # Detect proxy columns for each protected attribute
    config = DOMAIN_CONFIG[domain]
    proxy_columns = {}
    try:
        available_attrs = [col for col in config["protected_attributes"] if col in df.columns]
        for attr in available_attrs:
            proxies = detect_proxy_columns(
                df, attr, config["outcome_column"], config["protected_attributes"]
            )
            if proxies:
                proxy_columns[attr] = proxies
    except Exception as e:
        logger.warning(f"Proxy column detection failed: {str(e)}")

    bias_results["proxy_columns"] = proxy_columns

    try:
        gemini_result = explain_bias(bias_results)
    except Exception:
        gemini_result = {
            "explanation": "Explanation unavailable — check your GEMINI_API_KEY.",
            "remediation": [],
        }

    return {
        "status": "success",
        "results": bias_results,
        "explanation": gemini_result.get("explanation", ""),
        "remediation": gemini_result.get("remediation", []),
    }


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


@router.post("/model-card")
@limiter.limit("20/minute")
async def create_model_card(
    request: Request,
    data: dict,
    uid: str = Depends(verify_token),
):
    """
    Generate a Hugging Face-format model card from bias audit results.
    Expects: {"bias_results": {...}, "domain": "hiring"}
    Returns markdown text.
    """
    try:
        bias_results = data.get("bias_results")
        domain = data.get("domain", "unknown")

        if not bias_results:
            raise HTTPException(status_code=400, detail="bias_results required")

        card_md = generate_model_card(bias_results, domain)

        return Response(
            content=card_md,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename=model_card_{domain}.md"
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Model card generation failed: {str(e)}"
        )
