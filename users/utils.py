import os
import random
import smtplib
from django.core.cache import cache
import time
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from email.mime.text import MIMEText


def generating_code():
    return "".join(str(random.randint(0, 6)) for _ in range(6))


# def send_code():
#     cache.set("verify_code", generating_code(), timeout=60)
#     cached_value = cache.get("verify_code")
#     if cached_value:
#         return cached_value

#     else:
#         return "Переменная удалена"


def send_email(email, user_id):
    sender = "ilyachannel1.0@gmail.com"
    password = "pqtt inbm vjcc psrv"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    try:
        message = f"http://127.0.0.1:8000/user/verify_email/{user_id}/" #send_code()
        server.login(sender, password)
        msg = MIMEText(message)
        msg["Subject"] = "Verification code"
        server.sendmail(sender, email, msg.as_string())

        # server.sendmail(sender, sender, f"Subject: CLICK ME PLEASE!\n{message}")

        return "The message was sent successfully!"
    except Exception as _ex:
        return f"{_ex}\nCheck your login or password please!"
    