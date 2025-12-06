# backend/services/experian.py

import os
import logging
from pathlib import Path
import html
import httpx
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

load_dotenv()
logger = logging.getLogger(__name__)

# -----------------------------
# ENVIRONMENT VARIABLES
# -----------------------------
EXPERIAN_URL = os.getenv("EXPERIAN_URL")
EXPERIAN_USER = os.getenv("EXPERIAN_USER")
EXPERIAN_PASSWORD = os.getenv("EXPERIAN_PASSWORD")

EXPERIAN_ENQUIRY_REASON = os.getenv("EXPERIAN_ENQUIRY_REASON", "13")   # Loan Enquiry
EXPERIAN_FIN_PURPOSE = os.getenv("EXPERIAN_FIN_PURPOSE", "99")         # Personal / Unsecured Loan

# Folder to store XML + PDF
BASE_DIR = Path(__file__).resolve().parent.parent
EXPERIAN_DIR = BASE_DIR / "experian_reports"
EXPERIAN_DIR.mkdir(exist_ok=True)


# -------------------------------------------------------
# 1️⃣ BUILD EXPERIAN CPU2CPU SOAP REQUEST
# -------------------------------------------------------
def _build_experian_soap(
    pan: str,
    full_name: str | None,
    first_name: str | None,
    last_name: str | None,
    dob: str | None,           # format YYYY-MM-DD
    mobile: str | None,
    address: str | None,
    city: str | None,
    state: str | None,
    pincode: str | None,
) -> str:

    """BUILD PRODUCTION SOAP XML REQUEST"""

       # ---- SAFELY HANDLE NAME FIELDS ----
    # full_name fallback
    if not full_name or full_name.strip() == "":
        full_name = f"{first_name or ''} {last_name or ''}".strip()

    # If still empty, set default
    if not full_name or full_name.strip() == "":
        full_name = "_"

    # Safe extract surname (last word)
    name_parts = full_name.split()
    surname = name_parts[-1] if name_parts else "_"

    # Safe extract first name (first word)
    firstname = name_parts[0] if name_parts else "_"


    # Convert DOB YYYY-MM-DD → CCYYMMDD
    dob_xml = ""
    if dob:
        try:
            dob_xml = dob.replace("-", "")  # 1996-10-18 -> 19961018
        except:
            dob_xml = ""

    # ------------------ CBV2 XML Structure ------------------
    xml_body = f"""
<INProfileRequest>
  <Identification>
    <XMLUser>{html.escape(EXPERIAN_USER or "")}</XMLUser>
    <XMLPassword>{html.escape(EXPERIAN_PASSWORD or "")}</XMLPassword>
  </Identification>

  <Application>
    <FTReferenceNumber></FTReferenceNumber>
    <CustomerReferenceID></CustomerReferenceID>
    <EnquiryReason>{EXPERIAN_ENQUIRY_REASON}</EnquiryReason>
    <FinancePurpose>{EXPERIAN_FIN_PURPOSE}</FinancePurpose>
    <AmountFinanced>000000000005000</AmountFinanced>
    <DurationOfAgreement>06</DurationOfAgreement>
    <ScoreFlag>1</ScoreFlag>
    <PSVFlag></PSVFlag>
  </Application>

  <Applicant>
    <Surname>{html.escape(surname)}</Surname>
    <FirstName>{html.escape(firstname)}</FirstName>
    <GenderCode>1</GenderCode>
    <IncomeTaxPAN>{html.escape(pan)}</IncomeTaxPAN>
    <DateOfBirth>{dob_xml}</DateOfBirth>
    <PhoneNumber>{html.escape(mobile or "")}</PhoneNumber>
    <EMailId></EMailId>
  </Applicant>

  <Address>
    <FlatNoPlotNoHouseNo>{html.escape(address or "")}</FlatNoPlotNoHouseNo>
    <City>{html.escape(city or "")}</City>
    <State>{html.escape(state or "")}</State>
    <PinCode>{html.escape(pincode or "")}</PinCode>
  </Address>

  <AdditionalAddressFlag><Flag>N</Flag></AdditionalAddressFlag>
</INProfileRequest>
"""

    # ------------------ SOAP ENVELOPE ---------------------
    soap = f"""
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:cbv2">
  <soapenv:Header/>
  <soapenv:Body>
    <urn:process>
      <urn:in>
        {xml_body}
      </urn:in>
    </urn:process>
  </soapenv:Body>
</soapenv:Envelope>
"""

    return soap.strip()



# -------------------------------------------------------
# 2️⃣ SAVE XML AS PDF
# -------------------------------------------------------
def _xml_to_pdf(xml_str: str, pdf_path: Path):
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    text = c.beginText(40, 800)

    for line in xml_str.splitlines():
        text.textLine(line[:120])  # simple wrap

    c.drawText(text)
    c.showPage()
    c.save()



# -------------------------------------------------------
# 3️⃣ MAIN FUNCTION: FETCH CIBIL SCORE FROM EXPERIAN
# -------------------------------------------------------
def fetch_experian_cibil(
    pan: str,
    full_name: str | None,
    first_name: str | None,
    last_name: str | None,
    dob: str | None,
    mobile: str | None,
    address: str | None,
    city: str | None,
    state: str | None,
    pincode: str | None,
    customer_code: str,
):

    """CALL EXPERIAN CPU2CPU SERVER AND RETURN (score, xml_path, pdf_path)"""

    if not (EXPERIAN_URL and EXPERIAN_USER and EXPERIAN_PASSWORD):
        logger.warning("❌ Experian credentials missing — Skipping bureau call")
        return None, None, None

    # Build SOAP XML
    soap_body = _build_experian_soap(
        pan,
        full_name,
        first_name,
        last_name,
        dob,
        mobile,
        address,
        city,
        state,
        pincode,
    )

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "urn:cbv2/process",
    }

    logger.info(f"📡 Calling Experian CPU2CPU for customer {customer_code}")
    logger.debug("🧾 SOAP Body:\n%s", soap_body)

    try:
        response = httpx.post(
            EXPERIAN_URL,
            data=soap_body,
            headers=headers,
            timeout=60,
        )
    except Exception as e:
        logger.exception("❌ Experian connection failed")
        raise

    logger.info("📥 Experian HTTP Status: %s", response.status_code)
    logger.debug("🔍 Raw XML:\n%s", response.text[:2000])

    response.raise_for_status()
    xml_response = response.text

    # Save XML
    xml_path = EXPERIAN_DIR / f"{customer_code}_experian.xml"
    xml_path.write_text(xml_response, encoding="utf-8")

    # Save as PDF
    pdf_path = EXPERIAN_DIR / f"{customer_code}_experian.pdf"
    _xml_to_pdf(xml_response, pdf_path)

    # ------------------ Extract Bureau Score ------------------
    score = None
    try:
        root = ET.fromstring(xml_response)
        score_el = root.find(".//BureauScore")
        if score_el is not None:
            score = int(score_el.text)
    except Exception:
        logger.exception("⚠️ Could not parse CIBIL score from XML")

    return score, str(xml_path), str(pdf_path)
