# Change the ticker symbol to '03416.HK'
import os
import yfinance as yf
import logging
from smtplib import SMTP

# Email configuration
smtp_server_info = 'smtp.gmail.com'
smtp_port = 587
email_id = 'vincentman1027@gmail.com'  # Change to your email
email_password = 'nkdryjqgpqeugfwh'    # Change to your email password
recipient_emails = ["vincentman1027@yahoo.com.hk", "lambenny947@gmail.com"]  # List of recipient emails

def send_email(content):
    port = 25  # For starttls
    smtp_server = smtp_server_info
    sender_email = email_id
    receiver_emails = recipient_emails
    password = email_password
    subject = "Financial decision!"
    body = content+" \nCompleted."

    message = """\
From: {}
To: {}
Subject: {}

{}
""".format(sender_email, ", ".join(receiver_emails), subject, body)  # Format the message with recipients

    try:
        server = SMTP(smtp_server, port)
        server.starttls()  # Upgrade the connection to secure
        server.login(sender_email, email_password)  # Log in to the email account
        server.sendmail(sender_email, receiver_emails, message)
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.info("Failed to send email: {}".format(e))
        print("Failed to send email: {}".format(e))
    finally:
        server.quit()  # Always quit the server after sending

# Configure logging
logging.basicConfig(filename='stock_price_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

Ticker = "3416.HK"
# Fetch stock data
myTicket = yf.Ticker(Ticker)
# Fetch only the last 30 days of historical data
data = myTicket.history(period='30d')

# Get the last day's closing price
last_day_close = data['Close'].iloc[-2]  # Previous day's closing price
current_price = myTicket.history(period='1d')['Close'].iloc[-1]  # Current price

# Create the alert message
message = (f"For The Stock :{ Ticker}.  Current price: {current_price}\n"
           f"Last day's closing price: {last_day_close}\n"
           f"Price change: {((current_price - last_day_close) / last_day_close) * 100:.2f}%")

# Log the message
logging.info(message)
print(message)  # Optionally print the message to the console
send_email(message)