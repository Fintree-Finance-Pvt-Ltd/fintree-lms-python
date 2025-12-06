import httpx
import os

SMS_API_URL = os.getenv("SMS_API_URL")  # your SMS gateway
SMS_API_KEY = os.getenv("SMS_API_KEY")

async def send_sms(mobile: str, message: str):
    print(f"📲 Sending SMS → {mobile}: {message}")

    # Actual SMS gateway here
    if SMS_API_URL:
        payload = {
            "apiKey": SMS_API_KEY,
            "mobile": mobile,
            "message": message
        }
        async with httpx.AsyncClient() as client:
            await client.post(SMS_API_URL, json=payload)
