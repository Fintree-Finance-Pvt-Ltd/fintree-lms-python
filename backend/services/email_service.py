import smtplib
from email.mime.text import MIMEText
import os

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")  # Fintree-LMS@fintreefinance.com
SMTP_PASS = os.getenv("SMTP_PASS")

EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)  # Default fallback

async def send_email(to, subject, body):
    print(f"📧 Sending Email → {to}: {subject}")

    if not SMTP_HOST:
        print("⚠️ SMTP not configured — email not sent.")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = to

    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASS)
    server.sendmail(EMAIL_FROM, to, msg.as_string())
    server.quit()
