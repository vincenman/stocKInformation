import os
import yfinance as yf
import logging
from smtplib import SMTP

# Email configuration
smtp_server_info = 'smtp.gmail.com'
smtp_port = 587  # Change to 587 for TLS
email_id = 'vincentman1027@gmail.com'  # Change to your email
email_password = 'nkdryjqgpqeugfwh'    # Change to your email password
recipient_emails = ["vincentman1027@yahoo.com.hk", "lambenny947@gmail.com"]  # List of recipient emails

def send_email(content):
    port = smtp_port  # Use the correct port
    smtp_server = smtp_server_info
    sender_email = email_id
    receiver_emails = recipient_emails
    subject = "Financial Summary"
    body = content + " \nCompleted."

    message = """\
From: {}
To: {}
Subject: {}
Content-Type: text/html

{}
""".format(sender_email, ", ".join(receiver_emails), subject, body)  # Format the message with recipients

    server = None  # Initialize server variable
    try:
        server = SMTP(smtp_server, port)
        server.starttls()  # Upgrade the connection to secure
        server.login(sender_email, email_password)  # Log in to the email account
        server.sendmail(sender_email, receiver_emails, message)  # Send the email
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error("Failed to send email: {}".format(e))  # Log the error
        print("Failed to send email: {}".format(e))  # Print the error
    finally:
        if server is not None:
            server.quit()  # Always quit the server after sending

# Configure logging
logging.basicConfig(filename='stock_price_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# List of tickers
tickers = ["03416.HK", "UL", "VOO", "SPY"]

# Accumulate messages for all tickets
all_messages = []

for ticker in tickers:
    # Fetch stock data
    myTicket = yf.Ticker(ticker)
    # Fetch only the last 30 days of historical data
    data = myTicket.history(period='30d')

    # Check if there are enough data points
    if len(data) < 2:
        logging.warning(f"Not enough data for {ticker}. Skipping.")
        print(f"Not enough data for {ticker}. Skipping.")
        continue

    # Get the last day's closing price
    last_day_close = data['Close'].iloc[-2]  # Previous day's closing price
    current_price = myTicket.history(period='1d')['Close'].iloc[-1]  # Current price

    # Calculate price change percentage
    price_change_percent = ((current_price - last_day_close) / last_day_close) * 100
    message = (f"For The Stock: {ticker}. Current price: {current_price:.2f}<br>"
               f"Last day's closing price: {last_day_close:.2f}<br>"
               f"Price change: {price_change_percent:.2f}%<br>")

    # Check for drop of 2% or more
    if price_change_percent <= -1.5:
        message += (f"<strong style='color:blue;'>Suggestion: Consider buying {ticker}!</strong>")
    else:
        message += (f"<strong style='color:red;'>Please wait to buy {ticker}!</strong>")

    # Append the message to the list
    all_messages.append(message)

# Create the final message
final_message = "<br><br>".join(all_messages)  # Join all messages with double line breaks

# Log and send the email with all ticket information
if final_message:
    logging.info("Sending summary email.")
    print(final_message)  # Optionally print the final message to the console
    send_email(final_message)
else:
    logging.warning("No data to send in the email.")
    print("No data to send in the email.")
