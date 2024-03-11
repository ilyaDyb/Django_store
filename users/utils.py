import random
import smtplib
from django.core.cache import cache

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from email.mime.text import MIMEText


def send_email_for_confirmation(email, unique_code):
    sender = "ilyachannel1.0@gmail.com"
    password = "pqtt inbm vjcc psrv"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    try:
        message = f"Your varification code: {unique_code}"
        server.login(sender, password)
        msg = MIMEText(message)
        msg["From"] = "Home Furniture"
        msg["Subject"] = "Verification code"
        server.sendmail(sender, email, msg.as_string())

        return "The message was sent successfully!"
    except Exception as ex:
        return f"{ex}\nCheck your login or password please!"


# Генерация уникального кода (ваш способ)
def generate_unique_code():
    return str(random.randint(100000, 999999))
