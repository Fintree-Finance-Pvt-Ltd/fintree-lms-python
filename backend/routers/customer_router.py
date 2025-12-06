# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# import mysql.connector
# import httpx
# import os
# import base64
# from dotenv import load_dotenv

# load_dotenv()

# router = APIRouter(prefix="/customer", tags=["Customer"])

# # ---------- DB CONFIG ----------
# DB_CONFIG = {
#     "host": "217.21.80.3",
#     "user": "u341672715_python_code",
#     "password": "F!ntree@2026",
#     "database": "u341672715_python_code"
# }

# # ---------- Digitap Aadhaar Config ----------
# DIGITAP_CLIENT_ID = os.getenv("DIGITAP_CLIENT_ID")
# DIGITAP_CLIENT_SECRET = os.getenv("DIGITAP_CLIENT_SECRET")
# DIGITAP_BASE_URL = os.getenv("DIGITAP_BASE_URL", "https://api.digitap.com")

# # /kyc-unified/v1/<unifiedTransactionId>/details/ → from PDF
# AADHAAR_DETAILS_ENDPOINT = "/kyc-unified/v1/{unifiedTransactionId}/details/"

# # ---------- Folder for Aadhaar PDFs ----------
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# AADHAAR_PDF_DIR = os.path.join(BASE_DIR, "aadhaar_docs")
# os.makedirs(AADHAAR_PDF_DIR, exist_ok=True)   # ensure folder exists


# class CustomerSchema(BaseModel):
#     pan: str
#     fullName: str
#     firstName: str
#     middleName: str | None = ""
#     lastName: str | None = ""
#     gender: str
#     dob: str
#     address: str
#     city: str
#     state: str
#     country: str
#     pincode: str
#     maskedAadhaar: str | None = None
#     mobile: str
#     email: str
#     # we will receive unifiedTransactionId after Aadhaar KYC completed on Digitap
#     aadhaarTransactionId: str | None = None


# async def fetch_aadhaar_details_and_pdf(unified_transaction_id: str, customer_id: int):
#     """
#     Call Digitap Unified KYC Aadhaar details API,
#     fetch pdfLink, download PDF, and return parsed model + pdf_path.
#     """
#     if not DIGITAP_CLIENT_ID or not DIGITAP_CLIENT_SECRET:
#         raise HTTPException(500, "Digitap credentials not configured")

#     # Basic auth header for Digitap
#     auth_raw = f"{DIGITAP_CLIENT_ID}:{DIGITAP_CLIENT_SECRET}"
#     auth_header = base64.b64encode(auth_raw.encode()).decode()

#     headers = {
#         "Authorization": f"Basic {auth_header}",
#         "accept": "application/json",
#     }

#     url = f"{DIGITAP_BASE_URL}{AADHAAR_DETAILS_ENDPOINT.format(unifiedTransactionId=unified_transaction_id)}"

#     async with httpx.AsyncClient(timeout=30) as client:
#         res = await client.get(url, headers=headers)

#     if res.status_code != 200:
#         raise HTTPException(400, f"Aadhaar details API failed: {res.text}")

#     data = res.json()
#     model = data.get("model", {})
#     pdf_link = model.get("pdfLink")

#     pdf_path = None
#     if pdf_link:
#         # Download PDF
#         pdf_filename = f"aadhaar_{customer_id}.pdf"
#         pdf_path = os.path.join(AADHAAR_PDF_DIR, pdf_filename)

#         pdf_res = httpx.get(pdf_link, timeout=30)
#         if pdf_res.status_code == 200:
#             with open(pdf_path, "wb") as f:
#                 f.write(pdf_res.content)
#         else:
#             # you can log this, but don't fail whole flow
#             pdf_path = None

#     return model, pdf_path


# @router.post("/save")
# async def save_customer(data: CustomerSchema):
#     """
#     1) Save customer basic data
#     2) If aadhaarTransactionId provided, call Digitap Aadhaar details API,
#        download PDF, and update customer row with aadhaar info & pdf path
#     """
#     conn = None
#     cursor = None
#     try:
#         conn = mysql.connector.connect(**DB_CONFIG)
#         cursor = conn.cursor()

#         insert_sql = """
#         INSERT INTO customers (
#             pan, full_name, first_name, middle_name, last_name,
#             gender, dob, address, city, state, country, pincode,
#             masked_aadhar, mobile, email
#         ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """

#         values = (
#             data.pan,
#             data.fullName,
#             data.firstName,
#             data.middleName,
#             data.lastName,
#             data.gender,
#             data.dob,
#             data.address,
#             data.city,
#             data.state,
#             data.country,
#             data.pincode,
#             data.maskedAadhaar,
#             data.mobile,
#             data.email,
#         )

#         cursor.execute(insert_sql, values)
#         conn.commit()
#         customer_id = cursor.lastrowid

#         aadhaar_model = None
#         aadhaar_pdf_path = None

#         # If Aadhaar KYC transaction ID is available, fetch details & PDF
#         if data.aadhaarTransactionId:
#             aadhaar_model, aadhaar_pdf_path = await fetch_aadhaar_details_and_pdf(
#                 data.aadhaarTransactionId,
#                 customer_id,
#             )

#             update_sql = """
#             UPDATE customers
#             SET aadhar_response = %s,
#                 aadhaar_pdf_path = %s
#             WHERE id = %s
#             """

#             cursor.execute(
#                 update_sql,
#                 (str(aadhaar_model), aadhaar_pdf_path, customer_id)
#             )
#             conn.commit()

#         return {
#             "success": True,
#             "customerId": customer_id,
#             "aadhaar": aadhaar_model,
#             "aadhaarPdfPath": aadhaar_pdf_path,
#         }

#     except Exception as e:
#         raise HTTPException(500, f"Error saving customer: {e}")

#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

# ////////////////////

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os
# import base64

load_dotenv()

router = APIRouter(prefix="/customer", tags=["Customer Basic"])

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306))
}

class CustomerBasicSchema(BaseModel):
    pan: str
    fullName: str
    dob: str
    address: str
    city: str
    state: str
    country: str
    pincode: str
    maskedAadhaar: str | None = None
    mobile: str
    email: str


def generate_customer_code(cursor):
    cursor.execute("SELECT IFNULL(MAX(id),0) FROM customers")
    (max_id,) = cursor.fetchone()
    next_id = max_id + 1
    return f"CUST{next_id:06d}"


@router.post("/save-basic")
async def save_basic_customer(data: CustomerBasicSchema):
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        customer_code = generate_customer_code(cursor)

        aadhaar_last4 = None
        if data.maskedAadhaar:
            aadhaar_last4 = data.maskedAadhaar[-4:]

        dob_sql = None
        try:
            dob_sql = datetime.strptime(data.dob, "%Y-%m-%d").date()
        except:
            pass

        sql = """
        INSERT INTO customers (
            customer_code, pan, aadhaar_last4, full_name, dob,
            mobile, email, address_line1, address_line2,
            city, state, pincode, kyc_status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL, %s, %s, %s, 'IN_PROGRESS')
        """

        cursor.execute(sql, (
            customer_code,
            data.pan,
            aadhaar_last4,
            data.fullName,
            dob_sql,
            data.mobile,
            data.email,
            data.address,
            data.city,
            data.state,
            data.pincode,
        ))

        conn.commit()
        customer_id = cursor.lastrowid

        return {
            "success": True,
            "customerId": customer_id,
            "customerCode": customer_code
        }

    except Exception as e:
        raise HTTPException(500, f"Save Error: {e}")

    finally:
        if cursor: cursor.close()
        if conn: conn.close()
