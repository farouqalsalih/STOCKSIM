import os
import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = "gogogroceryproject@gmail.com"
EMAIL_PASSWORD = "duybrxsitmrbzhsk"

def sendemailconfirmation(email, message):
    msg = EmailMessage()
    msg["Subject"] = "Order Confirmation"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg.set_content(message)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        smtp.send_message(msg)

#testemail101