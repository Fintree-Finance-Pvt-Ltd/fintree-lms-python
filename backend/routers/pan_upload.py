from fastapi import APIRouter, UploadFile, File, HTTPException
import base64
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

PAN_OCR_URL = "https://aasandbox.finanalyz.com/sandbox/pan/ocr"
PAN_DETAILS_URL = "https://aasandbox.finanalyz.com/eKyc/pan-Details"

# Load keys from .env
PAN_OCR_API_KEY = os.getenv("PAN_OCR_API_KEY")  # MUST BE FILLED
PAN_OCR_API_KEY_HEADER = os.getenv("PAN_OCR_API_KEY_HEADER")  # e.g.: x-api-key

PAN_DETAILS_API_KEY = os.getenv("PAN_DETAILS_API_KEY")  # separate key for PAN Details API

router = APIRouter(prefix="/pan", tags=["PAN"])


@router.post("/upload")
async def upload_pan(file: UploadFile = File(...)):
    # Check OCR key
    if not PAN_OCR_API_KEY:
        raise HTTPException(500, "OCR API Key missing: PAN_OCR_API_KEY not set in .env")

    # Convert file → base64
    file_bytes = await file.read()
    base64_str = base64.b64encode(file_bytes).decode()

    # -------- 1️⃣ OCR API CALL --------
    ocr_headers = {
        PAN_OCR_API_KEY_HEADER: PAN_OCR_API_KEY,
        "Content-Type": "application/json",
        "accept": "*/*"
    }

    print("OCR HEADERS SENT:", ocr_headers)

    async with httpx.AsyncClient(timeout=30) as client:
        ocr_res = await client.post(
            PAN_OCR_URL,
            headers=ocr_headers,
            json={"base64Image": base64_str, "fileUrl": ""}
        )

    print("OCR STATUS:", ocr_res.status_code)
    print("OCR RAW:", ocr_res.text)

    if ocr_res.status_code != 200:
        raise HTTPException(400, f"OCR API Failed → {ocr_res.text}")

    ocr_json = ocr_res.json()

    # PAN extraction
    pan_number = (
    ocr_json.get("fields", {}).get("pan")
    or ocr_json.get("fields", {}).get("panNumber")
    or ocr_json.get("pan")
    or ocr_json.get("data", {}).get("pan")
)


    if not pan_number:
        raise HTTPException(400, "No PAN number found in OCR output")

    # -------- 2️⃣ PAN DETAILS API CALL --------

    if not PAN_DETAILS_API_KEY:
        raise HTTPException(500, "PAN Details API Key missing: PAN_DETAILS_API_KEY not set in .env")

    verify_headers = {
        "XApiKey": PAN_DETAILS_API_KEY,
        "Content-Type": "application/json",
        "accept": "*/*"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        verify_res = await client.post(
            PAN_DETAILS_URL,
            headers=verify_headers,
            json={"panNumber": pan_number}
        )

    print("PAN VERIFY STATUS:", verify_res.status_code)
    print("PAN VERIFY RAW:", verify_res.text)

    if verify_res.status_code != 200:
        raise HTTPException(400, f"PAN Verification Failed → {verify_res.text}")

    pan_details = verify_res.json()["data"]["response"]

    return {
        "success": True,
        "pan": pan_number,
        "ocr": ocr_json,
        "panDetails": pan_details
    }
