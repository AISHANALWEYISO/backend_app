import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Store OTPs temporarily in memory {email: {otp, expires_at}}
otp_store = {}

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # Gmail App Password


def generate_otp(length=6) -> str:
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(email: str) -> dict:
    """
    Generate and send OTP to the given email.
    Returns {success: bool, message: str}
    """
    otp = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=10)  # OTP valid for 10 mins

    # Store OTP
    otp_store[email] = {
        "otp": otp,
        "expires_at": expires_at
    }

    # Build email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your Yucca Agro Password Reset OTP"
    msg["From"] = GMAIL_USER
    msg["To"] = email

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f5f0e8; padding: 20px;">
        <div style="max-width: 480px; margin: auto; background: white; border-radius: 16px; padding: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 24px;">
                <h2 style="color: #366000; margin: 0;">🌱 Yucca Agro</h2>
                <p style="color: #888; font-size: 14px;">Smart Agricultural Solutions</p>
            </div>
            <h3 style="color: #333; text-align: center;">Password Reset OTP</h3>
            <p style="color: #555; text-align: center;">Use the code below to reset your password. It expires in <strong>10 minutes</strong>.</p>
            <div style="text-align: center; margin: 28px 0;">
                <span style="
                    display: inline-block;
                    background: #f0f7e8;
                    border: 2px dashed #366000;
                    border-radius: 12px;
                    padding: 16px 40px;
                    font-size: 36px;
                    font-weight: bold;
                    color: #366000;
                    letter-spacing: 10px;
                ">{otp}</span>
            </div>
            <p style="color: #999; font-size: 12px; text-align: center;">
                If you did not request this, please ignore this email.
            </p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, email, msg.as_string())
        return {"success": True, "message": "OTP sent successfully"}
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return {"success": False, "message": "Failed to send OTP email"}


def verify_otp(email: str, otp: str) -> dict:
    """
    Verify OTP for a given email.
    Returns {success: bool, message: str}
    """
    record = otp_store.get(email)

    if not record:
        return {"success": False, "message": "No OTP found for this email"}

    if datetime.now() > record["expires_at"]:
        del otp_store[email]
        return {"success": False, "message": "OTP has expired. Please request a new one"}

    if record["otp"] != otp:
        return {"success": False, "message": "Invalid OTP. Please try again"}

    # OTP is valid — remove it so it can't be reused
    del otp_store[email]
    return {"success": True, "message": "OTP verified successfully"}