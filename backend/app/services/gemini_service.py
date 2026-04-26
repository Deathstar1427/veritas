import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
model = None

PREFERRED_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite-preview-06-17",
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
    "gemini-2.0-flash-lite-001",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash",
]


def _normalize_model_name(name: str) -> str:
    return name.replace("models/", "") if name else ""


def _select_model_name() -> str | None:
    try:
        available = []
        for m in genai.list_models():
            methods = set(getattr(m, "supported_generation_methods", []) or [])
            if "generateContent" in methods:
                normalized = _normalize_model_name(getattr(m, "name", ""))
                if normalized:
                    available.append(normalized)

        if not available:
            return None

        for preferred in PREFERRED_MODELS:
            if preferred in available:
                return preferred

        return available[0]
    except Exception as e:
        logger.warning(f"Could not list Gemini models dynamically: {str(e)}")
        return None

# Validate API key at import time
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.warning(
        "GEMINI_API_KEY environment variable is not set. "
        "Bias explanations will not be available."
    )
else:
    try:
        genai.configure(api_key=api_key)

        selected_model = _select_model_name()
        if selected_model is None:
            selected_model = "gemini-1.5-flash-latest"

        model = genai.GenerativeModel(selected_model)
        logger.info(f"Gemini model initialized: {selected_model}")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model: {str(e)}")
        model = None


def explain_bias(bias_results: dict) -> str:
    """
    Takes raw Fairlearn numbers and asks Gemini to explain
    them in plain language a non-technical person can act on.

    Think of Gemini as the translator —
    turns confusing numbers into a clear story.
    """
    if model is None:
        return "Bias explanation unavailable — GEMINI_API_KEY not set or model failed to initialize."

    domain = bias_results["domain"]
    total = bias_results["total_records"]
    metrics = bias_results["bias_metrics"]

    # Build a summary of findings to send to Gemini
    findings = []
    for attr, data in metrics.items():
        rates = data["group_selection_rates"]
        dpd = data["demographic_parity_difference"]
        severity = data["bias_severity"]
        findings.append(
            f"- Attribute: {attr} | Severity: {severity} | "
            f"Demographic Parity Difference: {dpd} | "
            f"Group rates: {rates}"
        )

    findings_text = "\n".join(findings)

    prompt = f"""
You are a fairness auditor explaining bias findings to a non-technical team.

Domain: {domain}
Dataset size: {total} records

Bias findings:
{findings_text}

Write a clear, plain-language report that:
1. Summarizes what bias was found (or not found)
2. Explains what each finding means in real-world terms
3. Gives 2-3 specific, actionable recommendations to fix the bias
4. Uses simple language — no jargon, no ML terms

Keep it under 250 words. Be direct and honest.
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_text = str(e)
        logger.error(f"Gemini API call failed: {error_text}")

        lowered = error_text.lower()
        if "429" in lowered or "quota" in lowered or "rate" in lowered:
            return (
                "AI explanation is temporarily unavailable because the Gemini API "
                "quota or rate limit was reached. Bias metrics are still valid. "
                "Please try again later or use a key with available quota."
            )

        if "404" in lowered or "not found" in lowered or "model" in lowered:
            return (
                "AI explanation is temporarily unavailable due to a Gemini model "
                "compatibility issue. Bias metrics are still valid."
            )

        return (
            "AI explanation is temporarily unavailable right now. Bias metrics "
            "are still valid and can be used for the audit."
        )
