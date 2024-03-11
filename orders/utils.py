from email.mime.text import MIMEText
import smtplib

from datetime import datetime


def send_email_payment_check(email, price, date):
    sender = "ilyachannel1.0@gmail.com"
    password = "pqtt inbm vjcc psrv"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    formatted_date = datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')

    try:
        with open(r"users\templates\users\email_messsage.html", encoding="utf-8") as file:
            template = file.read()
    except IOError:
        return "The template file doesn't found!"

    try:
        template = template.replace("{{ price }}", str(price))
        template = template.replace("{{ date }}", str(formatted_date))
        server.login(sender, password)
        msg = MIMEText(template, "html")
        msg["From"] = sender
        msg["to"] = email
        msg["Subject"] = "Verification check"
        server.sendmail(sender, email, msg.as_string())

        return "The message was sent successfully!"

    except Exception as ex:
        return ex
