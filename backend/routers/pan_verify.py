from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

PAN_API_URL = "https://aasandbox.finanalyz.com/eKyc/pan-Details"
PAN_API_KEY = os.getenv("PAN_API_KEY")  # store in .env
PAN_API_KEY_HEADER = "XApiKey"

router = APIRouter(prefix="/pan", tags=["PAN Verification"])

class PanRequest(BaseModel):
    panNumber: str


def normalize_dob(dob_raw: str | None):
    """Convert 18/10/1996 → 1996-10-18"""
    if not dob_raw:
        return None
    try:
        return datetime.strptime(dob_raw, "%d/%m/%Y").strftime("%Y-%m-%d")
    except:
        return dob_raw


@router.post("/verify")
async def verify_pan(data: PanRequest):
    if not PAN_API_KEY:
        raise HTTPException(status_code=500, detail="Missing PAN_API_KEY in backend")

    headers = {
        PAN_API_KEY_HEADER: PAN_API_KEY,
        "Content-Type": "application/json",
        "accept": "*/*"
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(PAN_API_URL, headers=headers, json={"panNumber": data.panNumber})

    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="PAN API error: " + response.text)

    result = response.json()
    pan_data = result["data"]["response"]

    formatted_data = {
        "pan": pan_data.get("pan"),
        "name": pan_data.get("name"),
        "firstName": pan_data.get("firstName"),
        "middleName": pan_data.get("middleName"),
        "lastName": pan_data.get("lastName"),
        "gender": pan_data.get("gender"),
        "dob": normalize_dob(pan_data.get("dob")),
        "address": pan_data.get("address"),
        "city": pan_data.get("city"),
        "state": pan_data.get("state"),
        "country": pan_data.get("country"),
        "pincode": pan_data.get("pincode"),
        "maskedAadhaar": pan_data.get("maskedAadhaar"),
        "mobile": pan_data.get("mobile_no"),
        "email": pan_data.get("email"),
        "isValid": pan_data.get("isValid"),
        "rawResponse": result
    }

    return {
        "success": True,
        "data": formatted_data
    }
