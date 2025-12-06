# from fastapi import APIRouter, HTTPException, Request
# from pydantic import BaseModel
# import httpx
# import os
# import base64
# import mysql.connector
# from datetime import datetime
# from dotenv import load_dotenv

# from services.sms_service import send_sms
# from services.email_service import send_email

# load_dotenv()

# router = APIRouter(prefix="/customer/aadhaar", tags=["Aadhaar KYC"])

# # -------------------- DB CONFIG --------------------
# DB = {
#     "host": os.getenv("DB_HOST"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD"),
#     "database": os.getenv("DB_NAME"),
#     "port": int(os.getenv("DB_PORT", 3306)),
# }

# # -------------------- DIGITAP CONFIG --------------------
# DIGITAP_CLIENT_ID = os.getenv("DIGITAP_CLIENT_ID")
# DIGITAP_CLIENT_SECRET = os.getenv("DIGITAP_CLIENT_SECRET")
# DIGITAP_BASE = os.getenv("DIGITAP_BASE_URL")  # e.g. https://svc.digitap.ai

# AADHAAR_DIR = "aadhaar_docs"
# os.makedirs(AADHAAR_DIR, exist_ok=True)

# FRONTEND_URL = os.getenv("FRONTEND_BASE_URL", "https://fintree.in")

# GENERATE_URL_ENDPOINT = "/kyc-unified/v1/generate-url/"
# DETAILS_ENDPOINT = "/kyc-unified/v1/{txn}/details/"


# # ---------------------- 1️⃣ Request model ----------------------
# class AadhaarGenerateSchema(BaseModel):
#     customerCode: str
#     mobile: str
#     email: str


# # ---------------------- 2️⃣ Generate Aadhaar KYC Link ----------------------
# @router.post("/generate-url")
# async def generate_kyc_link(body: AadhaarGenerateSchema):

#     if not DIGITAP_CLIENT_ID or not DIGITAP_CLIENT_SECRET:
#         raise HTTPException(500, "Digitap credentials missing")

#     # Basic Auth
#     auth_raw = f"{DIGITAP_CLIENT_ID}:{DIGITAP_CLIENT_SECRET}"
#     auth_header = base64.b64encode(auth_raw.encode()).decode()

#     headers = {
#         "Authorization": f"Basic {auth_header}",
#         "Content-Type": "application/json",
#         "accept": "application/json"
#     }

#     # Customer will be returned to this URL (optional)
#     redirect_url = f"{FRONTEND_URL}/aadhaar-status?customerCode={body.customerCode}"

#     payload = {
#         "uniqueId": body.customerCode,
#         "redirectionUrl": redirect_url,
#         "expiryHours": 72
#     }

#     async with httpx.AsyncClient(timeout=30) as client:
#         res = await client.post(
#             f"{DIGITAP_BASE}{GENERATE_URL_ENDPOINT}",
#             json=payload,
#             headers=headers
#         )

#     if res.status_code != 200:
#         raise HTTPException(400, f"Digitap error: {res.text}")

#     model = res.json()["model"]
#     kyc_url = model.get("shortUrl") or model.get("url")
#     unified_transaction_id = model.get("unifiedTransactionId")

#     # ---------------------- SEND SMS ----------------------
#     await send_sms(
#         body.mobile,
#         f"Your Aadhaar KYC link: {kyc_url}. Complete within 72 hours."
#     )

#     # ---------------------- SEND EMAIL ----------------------
#     await send_email(
#         body.email,
#         "Aadhaar Verification Required",
#         f"Dear Customer,\n\nPlease complete your Aadhaar KYC:\n{kyc_url}\n\nRegards,\nFintree Finance"
#     )

#     return {
#         "success": True,
#         "customerCode": body.customerCode,
#         "kycUrl": kyc_url,
#         "unifiedTransactionId": unified_transaction_id
#     }


# # ---------------------- 3️⃣ Digitap Webhook (MOST IMPORTANT) ----------------------
# @router.post("/webhook")
# async def aadhaar_webhook(request: Request):
#     """
#     Digitap sends the full Aadhaar details + pdfLink via webhook.
#     """
#     payload = await request.json()
#     print("📥 Webhook Received:", payload)

#     txn = payload.get("transactionId")
#     status = payload.get("status")
#     data = payload.get("data", {})

#     customerCode = data.get("uniqueId")
#     pdf_url = data.get("pdfLink")

#     if not customerCode:
#         return {"error": "uniqueId missing in webhook"}

#     # ------------- Download Aadhaar PDF -------------
#     pdf_path = None
#     if pdf_url:
#         pdf_path = f"{AADHAAR_DIR}/{customerCode}_aadhaar.pdf"
#         pdf = httpx.get(pdf_url)
#         if pdf.status_code == 200:
#             with open(pdf_path, "wb") as f:
#                 f.write(pdf.content)

#     # ------------- Save JSON & PDF into DB -------------
#     conn = mysql.connector.connect(**DB)
#     cursor = conn.cursor()

#     cursor.execute(
#         """
#         UPDATE customers SET
#             aadhaar_pdf_path=%s,
#             aadhaar_json=%s,
#             kyc_status=%s,
#             aadhaar_completed_at=%s
#         WHERE customer_code=%s
#         """,
#         (pdf_path, str(data), status, datetime.now(), customerCode)
#     )

#     conn.commit()
#     cursor.close()
#     conn.close()

#     return {"success": True, "customerCode": customerCode}



# //////////////////////////

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
import os
import base64
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv

# Services
from services.sms_service import send_sms
from services.email_service import send_email

load_dotenv()

router = APIRouter(prefix="/customer/aadhaar", tags=["Aadhaar KYC"])

# -------------------- DB CONFIG --------------------
DB = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306)),
}

# -------------------- DIGITAP CONFIG --------------------
DIGITAP_CLIENT_ID = os.getenv("DIGITAP_CLIENT_ID")
DIGITAP_CLIENT_SECRET = os.getenv("DIGITAP_CLIENT_SECRET")
DIGITAP_BASE = os.getenv("DIGITAP_BASE_URL")  # e.g. https://svc.digitap.ai

GENERATE_URL_ENDPOINT = "/kyc-unified/v1/generate-url/"
DETAILS_ENDPOINT = "/kyc-unified/v1/{txn}/details/"

FRONTEND_URL = os.getenv("FRONTEND_BASE_URL", "https://fintree.in")

# -------------------- Aadhaar Storage --------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AADHAAR_DIR = os.path.join(BASE_DIR, "aadhaar_docs")
os.makedirs(AADHAAR_DIR, exist_ok=True)


# --------------------------------------------------------
# 1️⃣ REQUEST MODEL - Generate Aadhaar KYC Link
# --------------------------------------------------------
class AadhaarGenerateSchema(BaseModel):
    customerCode: str
    mobile: str
    email: str


# --------------------------------------------------------
# 2️⃣ Generate Aadhaar KYC Link API
# --------------------------------------------------------
@router.post("/generate-url")
async def generate_kyc_link(body: AadhaarGenerateSchema):

    if not DIGITAP_CLIENT_ID or not DIGITAP_CLIENT_SECRET:
        raise HTTPException(500, "❌ Digitap credentials missing in .env")

    # ---------------- Basic Auth ----------------
    auth_raw = f"{DIGITAP_CLIENT_ID}:{DIGITAP_CLIENT_SECRET}"
    auth_header = base64.b64encode(auth_raw.encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    # Customer will return here after completing Aadhaar
    redirect_url = f"{FRONTEND_URL}/aadhaar-status?customerCode={body.customerCode}"

    payload = {
        "uniqueId": body.customerCode,
        "redirectionUrl": redirect_url,
        "expiryHours": 72
    }

    # ---------------- Call Digitap API ----------------
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(f"{DIGITAP_BASE}{GENERATE_URL_ENDPOINT}", json=payload, headers=headers)

    if res.status_code != 200:
        raise HTTPException(400, f"Digitap error: {res.text}")

    model = res.json()["model"]

    kyc_url = model.get("shortUrl") or model.get("url")
    unified_transaction_id = model.get("unifiedTransactionId")

    # ---------------- SEND SMS ----------------
    await send_sms(
        body.mobile,
        f"Dear Customer, complete Aadhaar KYC using this secure link:\n{kyc_url}\nValid for 72 hours."
    )

    # ---------------- SEND EMAIL ----------------
    await send_email(
        body.email,
        "Aadhaar Verification - Fintree Finance",
        f"Dear Customer,\n\nPlease complete your Aadhaar KYC:\n{kyc_url}\n\nRegards,\nFintree Finance"
    )

    return {
        "success": True,
        "kycUrl": kyc_url,
        "unifiedTransactionId": unified_transaction_id,
        "customerCode": body.customerCode,
    }


# --------------------------------------------------------
# 3️⃣ Digitap → LMS Webhook (FINAL RESPONSE)
# --------------------------------------------------------
@router.post("/webhook")
async def aadhaar_webhook(request: Request):

    payload = await request.json()
    print("📥 Aadhaar Webhook Received:", payload)

    txn = payload.get("transactionId")
    status = payload.get("status")       # e.g., SUCCESS / FAILED
    data = payload.get("data", {})

    customerCode = data.get("uniqueId")
    pdf_url = data.get("pdfLink")

    if not customerCode:
        return {"error": "uniqueId missing in webhook"}

    # ---------------- Download Aadhaar PDF ----------------
    pdf_path = None
    if pdf_url:
        pdf_path = f"{AADHAAR_DIR}/{customerCode}_aadhaar.pdf"
        pdf_res = httpx.get(pdf_url)

        if pdf_res.status_code == 200:
            with open(pdf_path, "wb") as f:
                f.write(pdf_res.content)
        else:
            pdf_path = None

    # ---------------- Save data into DB ----------------
    conn = mysql.connector.connect(**DB)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE customers SET
            aadhaar_pdf_path=%s,
            aadhaar_json=%s,
            kyc_status=%s,
            aadhaar_completed_at=%s
        WHERE customer_code=%s
        """,
        (pdf_path, str(data), status, datetime.now(), customerCode)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {"success": True, "customerCode": customerCode, "kycStatus": status}
