import os
import base64
from typing import Dict, Any
from datetime import datetime

import httpx
from dotenv import load_dotenv

load_dotenv()  # load .env from backend root

PAN_OCR_URL = os.getenv("PAN_OCR_URL", "https://aasandbox.finanalyz.com/sandbox/pan/ocr")
PAN_OCR_API_KEY = os.getenv("PAN_OCR_API_KEY")
PAN_OCR_API_KEY_HEADER = os.getenv("PAN_OCR_API_KEY_HEADER", "x-api-key")


def _normalise_dob(dob_raw: str | None) -> str | None:
    """
    Try to convert various formats (DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD) -> YYYY-MM-DD.
    If fail, return original or None.
    """
    if not dob_raw:
        return None

    dob_raw = dob_raw.strip()

    # Try a few common patterns
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(dob_raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return dob_raw  # fallback


async def run_pan_ocr(file_path: str) -> Dict[str, Any]:
    """
    Call Finanalyz PAN OCR API with base64 image.
    Returns dict with keys: pan, name, dob.
    """

    if not PAN_OCR_API_KEY:
        raise RuntimeError("PAN_OCR_API_KEY not set in .env")

    # 1. Read image and convert to base64
    with open(file_path, "rb") as f:
        img_bytes = f.read()

    base64_image = base64.b64encode(img_bytes).decode("ascii")

    payload = {
        "base64Image": base64_image,
        "fileUrl": ""  # we are not using fileUrl
    }

    headers = {
        "accept": "*/*",
        "Content-Type": "application/json",
        PAN_OCR_API_KEY_HEADER: PAN_OCR_API_KEY,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(PAN_OCR_URL, json=payload, headers=headers)

    # 2. Handle auth error
    if resp.status_code == 401:
        # This means the API key or header name is wrong
        raise RuntimeError("PAN OCR API unauthorized (401) – check API key and header name")

    if resp.status_code >= 400:
        raise RuntimeError(f"PAN OCR API error {resp.status_code}: {resp.text}")

    data = resp.json()
    # Now we have to map their response to pan/name/dob.
    # This depends on Finanalyz response structure.
    # Examples (adjust these keys if docs say different):
    pan = (
        data.get("pan")
        or data.get("panNumber")
        or data.get("pan_no")
    )
    name = (
        data.get("name")
        or data.get("nameOnCard")
        or data.get("fullName")
    )
    dob_raw = (
        data.get("dob")
        or data.get("dateOfBirth")
        or data.get("dobOnCard")
    )
    dob = _normalise_dob(dob_raw)

    return {
        "raw": data,   # keep full raw response for debugging if needed
        "pan": pan,
        "name": name,
        "dob": dob,
    }
