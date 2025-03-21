import os
import yfinance as yf
import logging
import matplotlib.pyplot as plt
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Email configuration
smtp_server_info = 'smtp.gmail.com'
smtp_port = 587
email_id = 'vincentman1027@gmail.com'  # Change to your email
email_password = 'nkdryjqgpqeugfwh'  # Change to your email password
recipient_emails = ["vincentman1027@yahoo.com.hk", "lambenny947@gmail.com"]  # List of recipient emails


def send_email(content, attachment_path=None):
    sender_email = email_id
    receiver_emails = recipient_emails
    subject = "Financial Decision Regarding Stock Prices"

    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = ", ".join(receiver_emails)
    message['Subject'] = subject

    # Attach the email body
    message.attach(MIMEText(content + " \nCompleted.", 'plain'))

    # Attach the histogram if provided
    if attachment_path:
        with open(attachment_path, 'rb') as attachment:
            part = MIMEApplication(attachment.read(), Name=os.path.basename(attachment_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            message.attach(part)

    try:
        server = SMTP(smtp_server_info, smtp_port)
        server.starttls()  # Upgrade the connection to secure
        server.login(sender_email, email_password)  # Log in to the email account
        server.sendmail(sender_email, receiver_emails, message.as_string())

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
# Fetch only the last 10 working days of historical data
data = myTicket.history(period='10d')

# Get the last day's closing price
last_day_close = data['Close'].iloc[-2]  # Previous day's closing price
current_price = myTicket.history(period='1d')['Close'].iloc[-1]  # Current price

# Create the alert message
message = (f"For The Stock: {Ticker}. Current price: {current_price}\n"
           f"Last day's closing price: {last_day_close}\n"
           f"Price change: {((current_price - last_day_close) / last_day_close) * 100:.2f}%")

# Log the message
logging.info(message)
print(message)  # Optionally print the message to the console

# Plot closing prices against dates
plt.figure(figsize=(10, 6))
plt.plot(data.index, data['Close'], marker='o', color='blue', linestyle='-')
plt.xlabel('Date')
plt.ylabel('Closing Price')
plt.title(f'Closing Prices for {Ticker} Over the Last 10 Working Days')
plt.xticks(rotation=45)
plt.grid()

# Save the plot as a PNG file
histogram_path = '3416_HK_closing_prices.jpg'
plt.savefig(histogram_path, bbox_inches='tight')
plt.close()

# Send the email with the message and attach the histogram
send_email(message, histogram_path)

# Logging the completion
logging.info("Line plot generated and email sent.")
