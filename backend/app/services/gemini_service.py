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


def explain_bias(bias_results: dict) -> dict:
    """
    Takes raw Fairlearn numbers and asks Gemini to explain
    them in plain language a non-technical person can act on.

    Returns a dict with 'explanation' and 'remediation' keys.

    Think of Gemini as the translator —
    turns confusing numbers into a clear story.
    """
    fallback = {
        "explanation": "Bias explanation unavailable — GEMINI_API_KEY not set or model failed to initialize.",
        "remediation": [],
    }

    if model is None:
        return fallback

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
3. Uses simple language — no jargon, no ML terms

Keep it under 200 words. Be direct and honest.

Also suggest 3 concrete remediation steps to reduce the detected bias.
Format as:
REMEDIATION:
1. [step one]
2. [step two]
3. [step three]
"""

    try:
        response = model.generate_content(prompt)
        raw = response.text or ""

        explanation = raw
        remediation = []

        if "REMEDIATION:" in raw:
            parts = raw.split("REMEDIATION:", 1)
            explanation = parts[0].strip()
            rem_text = parts[1].strip()
            import re
            steps = re.findall(r"\d+\.\s*(.+)", rem_text)
            remediation = [s.strip() for s in steps if s.strip()]

        return {"explanation": explanation, "remediation": remediation}
    except Exception as e:
        error_text = str(e)
        logger.error(f"Gemini API call failed: {error_text}")

        lowered = error_text.lower()
        if "429" in lowered or "quota" in lowered or "rate" in lowered:
            return {
                "explanation": (
                    "AI explanation is temporarily unavailable because the Gemini API "
                    "quota or rate limit was reached. Bias metrics are still valid. "
                    "Please try again later or use a key with available quota."
                ),
                "remediation": [],
            }

        if "404" in lowered or "not found" in lowered or "model" in lowered:
            return {
                "explanation": (
                    "AI explanation is temporarily unavailable due to a Gemini model "
                    "compatibility issue. Bias metrics are still valid."
                ),
                "remediation": [],
            }

        return {
            "explanation": (
                "AI explanation is temporarily unavailable right now. Bias metrics "
                "are still valid and can be used for the audit."
            ),
            "remediation": [],
        }


def generate_model_card(bias_results: dict, domain: str) -> str:
    """
    Generate a Hugging Face-format model card from audit results.
    """
    import json

    if model is None:
        return "# Model Card\n\nModel card generation unavailable — GEMINI_API_KEY not set."

    prompt = f"""
Generate a Hugging Face model card in markdown format based on these fairness audit results
for a {domain} prediction model.

Audit results: {json.dumps(bias_results, indent=2)}

Include these sections:
- Model description
- Intended use and out-of-scope uses
- Bias and fairness evaluation (with a markdown table of metrics)
- Recommendations
- Ethical considerations

Use proper markdown headings. Be specific and cite the actual metric values.
"""
    try:
        response = model.generate_content(prompt)
        return response.text or "# Model Card\n\nGeneration returned empty content."
    except Exception as e:
        logger.error(f"Model card generation failed: {str(e)}")
        return f"# Model Card\n\nGeneration failed: {str(e)}"
