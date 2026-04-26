import base64
import json
import os

import firebase_admin
from firebase_admin import credentials


def _load_service_account_from_env() -> dict | None:
    raw_value = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    if not raw_value:
        return None

    compact = "".join(raw_value.split())

    try:
        decoded = base64.b64decode(compact, validate=True).decode("utf-8")
        return json.loads(decoded)
    except Exception:
        return json.loads(raw_value)


def init_firebase() -> None:
    if firebase_admin._apps:
        return

    service_account = _load_service_account_from_env()
    if service_account:
        credential = credentials.Certificate(service_account)
        firebase_admin.initialize_app(credential)
        return

    if os.path.exists("serviceAccountKey.json"):
        credential = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(credential)
        return

    firebase_admin.initialize_app()
