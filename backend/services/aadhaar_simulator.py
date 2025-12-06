# backend/services/aadhaar_simulator.py

import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
AADHAAR_DIR = BASE_DIR / "aadhaar_docs"
AADHAAR_DIR.mkdir(exist_ok=True)

def simulate_aadhaar(customerCode: str):
    """
    Returns dummy Aadhaar KYC data + creates a sample PDF.
    Used ONLY in local mode (DIGITAP_MODE=SIMULATE).
    """

    # Create dummy PDF
    pdf_path = AADHAAR_DIR / f"{customerCode}_aadhaar_simulated.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.4 Dummy Aadhaar Simulated PDF File")

    simulated = {
        "aadhaarNumber": "XXXX-XXXX-1234",
        "dob": "1995-01-01",
        "gender": "M",
        "name": "Test Aadhaar User",
        "address": "Dummy Address Line 1",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001",
        "pdfPath": str(pdf_path)
    }

    return simulated
