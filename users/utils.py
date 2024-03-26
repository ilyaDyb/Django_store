import os
import random
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from twilio.rest import Client


def send_email_for_confirmation(email, unique_code=None, link_for_confirm=None):
    sender = "ilyachannel1.0@gmail.com"
    password = "pqtt inbm vjcc psrv"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    try:
        server.login(sender, password)

        if unique_code:
            message = f"Your varification code: {unique_code}"
        elif link_for_confirm:
            message = f"Your link for confirm: {link_for_confirm}"

        msg = MIMEText(message)
        msg["From"] = "Home Furniture"
        msg["Subject"] = "Confirm your email"
        server.sendmail(sender, email, msg.as_string())

        return "The message was sent successfully!"
    except Exception as ex:
        return f"{ex}\nCheck your login or password please!"


# Генерация уникального кода (ваш способ)
def generate_unique_code():
    return str(random.randint(100000, 999999))


# def sending_sms(text, receiver):
#     load_dotenv()
#     try:
#         account_sid = os.getenv("ACCOUNT_SID")
#         auth_token = os.getenv("AUTH_TOKEN")
#         client = Client(account_sid, auth_token)
#         message = client.messages.create(
#             body=text,
#             from_="+***********",
#             to=receiver
#         )
#     except Exception as ex:
#         return ex
    
# print(sending_sms(text="Получилось", receiver="+***********"))
