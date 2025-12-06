# from fastapi import APIRouter, UploadFile, File, Form
# from db import get_conn
# from services.ocr_service import run_ocr
# import uuid
# import os

# router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

# UPLOAD_DIR = "uploads/pan"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# @router.post("/start")
# async def start_onboarding(
#     mobile: str = Form(...),
#     email: str = Form(...),
#     address_line1: str = Form(...),
#     city: str = Form(...),
#     state: str = Form(...),
#     pincode: str = Form(...),
#     pan_image: UploadFile = File(...)
# ):
#     # 1. Save PAN image
#     file_ext = pan_image.filename.split(".")[-1]
#     filename = f"{uuid.uuid4()}.{file_ext}"
#     file_path = f"{UPLOAD_DIR}/{filename}"

#     with open(file_path, "wb") as f:
#         f.write(await pan_image.read())

#     # 2. Run OCR (dummy for now)
#     ocr_data = await run_ocr(file_path)
#     pan_no = ocr_data["pan"]
#     full_name = ocr_data["name"]
#     dob = ocr_data["dob"]

#     # 3. Insert into customers
#     conn = get_conn()
#     cur = conn.cursor()

#     customer_code = f"CUST-{pan_no}"

#     cur.execute("""
#         INSERT INTO customers
#         (customer_code, pan, full_name, dob, mobile, email,
#          address_line1, city, state, pincode, kyc_status)
#         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'IN_PROGRESS')
#     """, (
#         customer_code, pan_no, full_name, dob, mobile, email,
#         address_line1, city, state, pincode
#     ))

#     customer_id = cur.lastrowid

#     # 4. Save document entry
#     cur.execute("""
#         INSERT INTO customer_documents
#         (customer_id, doc_type, file_path, ocr_text)
#         VALUES (%s, 'PAN_FRONT', %s, %s)
#     """, (customer_id, file_path, str(ocr_data["raw"]))
#     )

#     conn.commit()
#     cur.close()
#     conn.close()

#     return {
#         "success": True,
#         "customer_id": customer_id,
#         "pan_details": ocr_data,
#         "message": "Onboarding started successfully"
#     }

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from db import get_conn
from services.ocr_service import run_pan_ocr
import uuid
import os

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

# folder to store PAN images
BASE_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads", "pan")
BASE_UPLOAD_DIR = os.path.abspath(BASE_UPLOAD_DIR)
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)


@router.post("/pan-upload")
async def pan_upload_start(
    mobile: str = Form(...),
    email: str = Form(...),
    address_line1: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    pincode: str = Form(...),
    pan_image: UploadFile = File(...)
):
    # 1. Save uploaded PAN image
    ext = pan_image.filename.split(".")[-1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(BASE_UPLOAD_DIR, filename)

    try:
        with open(file_path, "wb") as f:
            f.write(await pan_image.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save PAN image: {e}")

    # 2. Run OCR on saved file
    ocr_data = await run_pan_ocr(file_path)

    pan = ocr_data.get("pan")
    full_name = ocr_data.get("name")
    dob = ocr_data.get("dob")

    if not pan:
        raise HTTPException(status_code=400, detail="PAN not detected from OCR")

    # 3. Insert / upsert into customers table
    conn = get_conn()
    cur = conn.cursor()

    # Check if customer already exists with same PAN
    cur.execute("SELECT id FROM customers WHERE pan = %s", (pan,))
    existing = cur.fetchone()

    if existing:
        customer_id = existing[0]
        # update basic contact/address
        cur.execute(
            """
            UPDATE customers
            SET full_name=%s, dob=%s, mobile=%s, email=%s,
                address_line1=%s, city=%s, state=%s, pincode=%s,
                kyc_status='IN_PROGRESS'
            WHERE id=%s
            """,
            (full_name, dob, mobile, email,
             address_line1, city, state, pincode, customer_id)
        )
    else:
        customer_code = f"CUST-{pan}"
        cur.execute(
            """
            INSERT INTO customers
            (customer_code, pan, full_name, dob, mobile, email,
             address_line1, city, state, pincode, kyc_status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'IN_PROGRESS')
            """,
            (customer_code, pan, full_name, dob, mobile, email,
             address_line1, city, state, pincode)
        )
        customer_id = cur.lastrowid

    # 4. Insert document record
    cur.execute(
        """
        INSERT INTO customer_documents
        (customer_id, doc_type, file_path, ocr_text)
        VALUES (%s, 'PAN_FRONT', %s, %s)
        """,
        (customer_id, file_path, str(ocr_data))
    )

    conn.commit()
    cur.close()
    conn.close()

    return {
        "success": True,
        "customer_id": customer_id,
        "pan_details": {
            "pan": pan,
            "name": full_name,
            "dob": dob,
        },
        "message": "PAN uploaded and customer onboarding started.",
    }
