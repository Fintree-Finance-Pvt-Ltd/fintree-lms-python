# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# import mysql.connector
# import httpx
# import os
# import xml.etree.ElementTree as ET
# from dotenv import load_dotenv
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4

# load_dotenv()

# router = APIRouter(prefix="/customer/experian", tags=["Experian CIBIL"])

# DB_CONFIG = {
#     "host": os.getenv("DB_HOST"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD"),
#     "database": os.getenv("DB_NAME"),
# }

# EXPERIAN_URL = os.getenv("EXPERIAN_URL")
# EXPERIAN_USER = os.getenv("EXPERIAN_USER")
# EXPERIAN_PASSWORD = os.getenv("EXPERIAN_PASSWORD")
# EXPERIAN_FIN_PURPOSE = os.getenv("EXPERIAN_FIN_PURPOSE")
# EXPERIAN_ENQUIRY_REASON = os.getenv("EXPERIAN_ENQUIRY_REASON")

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# EXPERIAN_DIR = os.path.join(BASE_DIR, "experian_reports")
# os.makedirs(EXPERIAN_DIR, exist_ok=True)


# # -------------------------
# # JSON body model
# # -------------------------
# class ExperianRequest(BaseModel):
#     customerCode: str
#     pan: str


# @router.post("/score")
# async def experian_score(data: ExperianRequest):
#     customerCode = data.customerCode
#     pan = data.pan

#     # Build SOAP Body
#     xml_body = f"""
# <GetScore>
#   <User>{EXPERIAN_USER}</User>
#   <Password>{EXPERIAN_PASSWORD}</Password>
#   <PAN>{pan}</PAN>
# </GetScore>
# """

#     headers = {"Content-Type": "text/xml"}

#     async with httpx.AsyncClient() as client:
#         res = await client.post(EXPERIAN_URL, data=xml_body, headers=headers)

#     if res.status_code != 200:
#         raise HTTPException(status_code=400, detail="Experian API failed")

#     xml_text = res.text

#     # Save XML
#     xml_path = os.path.join(EXPERIAN_DIR, f"{customerCode}.xml")
#     open(xml_path, "w").write(xml_text)

#     # Convert to PDF
#     pdf_path = os.path.join(EXPERIAN_DIR, f"{customerCode}.pdf")
#     c = canvas.Canvas(pdf_path, pagesize=A4)
#     t = c.beginText(40, 800)

#     for line in xml_text.split("\n"):
#         t.textLine(line[:120])
#     c.drawText(t)
#     c.showPage()
#     c.save()

#     # Parse CIBIL Score
#     score = None
#     try:
#         root = ET.fromstring(xml_text)
#         score_el = root.find(".//Score")
#         if score_el is not None:
#             score = int(score_el.text)
#     except:
#         score = None

#     # Update DB
#     conn = mysql.connector.connect(**DB_CONFIG)
#     cursor = conn.cursor()
#     cursor.execute("""
#         UPDATE customers
#         SET experian_xml_path = %s,
#             experian_pdf_path = %s,
#             cibil_score = %s
#         WHERE customer_code = %s
#     """, (xml_path, pdf_path, score, customerCode))
#     conn.commit()

#     cursor.close()
#     conn.close()

#     return {
#         "success": True,
#         "score": score,
#         "xmlPath": xml_path,
#         "pdfPath": pdf_path
#     }


# ///////////////////
# backend/routers/experian_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import mysql.connector
import os
from dotenv import load_dotenv

from services.experian import fetch_experian_cibil   # <-- NEW IMPORTANT IMPORT

load_dotenv()

router = APIRouter(prefix="/customer/experian", tags=["Experian CIBIL"])

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}


# -------------------------
# Request Model
# -------------------------
class ExperianRequest(BaseModel):
    customerCode: str
    pan: str
    fullName: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    dob: str | None = None
    mobile: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None


# -------------------------
# Experian Score API
# -------------------------
@router.post("/score")
async def experian_score(data: ExperianRequest):

    # ---- CALL THE SERVICE FUNCTION ----
    score, xml_path, pdf_path = fetch_experian_cibil(
        pan=data.pan,
        full_name=data.fullName,
        first_name=data.firstName,
        last_name=data.lastName,
        dob=data.dob,
        mobile=data.mobile,
        address=data.address,
        city=data.city,
        state=data.state,
        pincode=data.pincode,
        customer_code=data.customerCode,
    )

    # If bureau skipped due to missing env vars
    if score is None and xml_path is None:
        return {"success": False, "message": "Experian not configured or not reachable"}

    # ---- UPDATE DATABASE ----
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE customers
        SET experian_xml_path = %s,
            experian_pdf_path = %s,
            cibil_score = %s
        WHERE customer_code = %s
    """, (xml_path, pdf_path, score, data.customerCode))

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "success": True,
        "score": score,
        "xmlPath": xml_path,
        "pdfPath": pdf_path,
    }
