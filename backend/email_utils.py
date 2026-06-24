# email_utils.py - handles OTP generation and sending verification emails
# We use Gmail SMTP with an App Password (not the regular Gmail password).
# The OTP is a random 6-digit number sent as a styled HTML email.

import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Gmail credentials for sending OTPs
GMAIL_ADDRESS      = "hamim00753@gmail.com"
GMAIL_APP_PASSWORD = "tsub ujuq ngwo kqrb"   # 16-character Google App Password


def generate_otp():
    """Generates a random 6-digit code like '482917'."""
    return str(random.randint(100000, 999999))


def send_otp_email(recipient_email, otp):
    """Sends an HTML email containing the OTP to the user.
    Returns True if sent successfully, False if something went wrong."""

    subject = "Sobkaj - Your Verification Code"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #4A90D9;">Welcome to Sobkaj!</h2>
        <p>Your verification code is:</p>
        <h1 style="letter-spacing: 8px; color: #333; background: #f0f0f0;
                    display: inline-block; padding: 10px 20px; border-radius: 8px;">
            {otp}
        </h1>
        <p style="color: #888;">This code expires when you close the registration page.</p>
        <br>
        <p>- The Sobkaj Team</p>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = recipient_email
    msg.attach(MIMEText(body, "html"))

    try:
        # connect to Gmail SMTP on port 587 with TLS encryption
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, recipient_email, msg.as_string())
        print(f"[EMAIL] OTP sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False
