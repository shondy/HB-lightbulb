
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeTimedSerializer
from flask import render_template, url_for

import os

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "lightbulb.shondy@gmail.com"
password = os.environ['NOTIFICATION_PASSWORD']
salt = os.environ['EMAIL_CONFIRMATION_SALT']


def send_confirmation_email(user_email):
    """"create a email for email confirmation"""
    # secret_key - to sign and verify with, 
    # salt – extra key to combine with secret_key to distinguish signatures in different contexts.
    # serializer – an object that provides dumps and loads methods for serializing data to a string.

    confirm_serializer = URLSafeTimedSerializer(os.environ['APP_SECRET_KEY'])

    # generate absolute url for confirmation
    confirm_url = url_for('confirm_email', token=confirm_serializer.dumps(user_email, salt=salt), _external=True)
    
    text = f"Your account on Lightbulb app was successfully created. Please click the link below to confirm your email address and activate your account: {confirm_url}"
    html = render_template('email_confirmation.html', confirm_url=confirm_url)
    
    send_email(text, html, 'Confirm Your Email Address', user_email)

def send_email(text, html, subject, receiver_email):
    # send an email from sender_email to receiver_email with subject and body equils to text/html

    message = MIMEMultipart("alternative")

    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message, which is the MIMEMultipart("alternative") instance
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

