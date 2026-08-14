import smtplib
from email.mime.text import MIMEText

from app.config import settings


def send_email(to: str, subject: str, body: str) -> bool:
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = settings.gmail_address
        msg["To"] = to

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(settings.gmail_address, settings.gmail_app_password)
            server.send_message(msg)

        return True
    except Exception:
        return False