import os
import yfinance as yf
import logging
from smtplib import SMTP

# Email configuration
smtp_server_info = 'smtp.gmail.com'
smtp_port = 587  # Change to 587 for TLS
email_id = 'vincentman1027@gmail.com'  # Change to your email
email_password = 'nkdryjqgpqeugfwh'  # Change to your email password
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


def calculate_macd(ticker, period='1y', fast=12, slow=26, signal=9):
    """Calculate MACD for a given ticker."""
    data = yf.Ticker(ticker).history(period=period, interval='1wk')  # Weekly data
    if len(data) < slow + signal:
        return None  # Not enough data

    close_prices = data['Close']
    exp1 = close_prices.ewm(span=fast, adjust=False).mean()
    exp2 = close_prices.ewm(span=slow, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    macd_histogram = macd_line - signal_line

    return {
        'macd_line': macd_line.iloc[-1],
        'signal_line': signal_line.iloc[-1],
        'histogram': macd_histogram.iloc[-1],
        'is_negative': macd_histogram.iloc[-1] < 0  # True if MACD is negative
    }


def calculate_rsi(ticker, period=14):
    """Calculate RSI for a given ticker."""
    data = yf.Ticker(ticker).history(period='1y')
    if len(data) < period:
        return None  # Not enough data

    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]  # Return the latest RSI value


# Configure logging (unchanged)
logging.basicConfig(filename='stock_price_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# List of tickers (unchanged)
hk_tickers = ["2638.HK", "6823.HK", "1038.HK", "0270.HK", "2388.HK", "0006.HK"]
tickers = ["3416.HK", "0700.HK", "0005.HK", "1299.HK", "0941.HK", "0883.HK", "0949.HK","2638.HK", "6823.HK","03003.HK", "BRK-B", "QQQM", "VOO", "SPY", "UL"]

tickers = list(set(tickers) | set(hk_tickers))

all_messages = []

for ticker in tickers:
    myTicket = yf.Ticker(ticker)
    data = myTicket.history(period='30d')

    if len(data) < 2:
        logging.warning(f"Not enough data for {ticker}. Skipping.")
        continue

    last_day_close = data['Close'].iloc[-2]
    current_price = myTicket.history(period='1d')['Close'].iloc[-1]
    price_change_percent = ((current_price - last_day_close) / last_day_close) * 100

    # Calculate Weekly MACD
    macd_data = calculate_macd(ticker)
    macd_status = "Negative (Bearish)" if macd_data and macd_data['is_negative'] else "Positive (Bullish)"

    # Calculate RSI
    rsi_value = calculate_rsi(ticker)

    message = (f"For The Stock: {ticker}. Current price: {current_price:.2f}<br>"
               f"Last day's closing price: {last_day_close:.2f}<br>"
               f"Price change: {price_change_percent:.2f}%<br>"
               f"Weekly MACD Status: {macd_status}<br>"
               f"Current RSI: {rsi_value:.2f}<br>")

    # Buy suggestion logic (updated)
    if price_change_percent <= -1.5:
        if macd_data and macd_data['is_negative'] and rsi_value < 30:
            message += (
                f"<strong style='color:blue;'>Suggestion: HIGHLY STRONG BUY! (Price drop + Weekly MACD negative + RSI < 30)</strong>")
        elif macd_data and macd_data['is_negative']:
            message += (
                f"<strong style='color:blue;'>Suggestion: STRONG BUY! (Price drop + Weekly MACD negative)</strong>")
        elif rsi_value < 40:
            message += (
                f"<strong style='color:blue; text-decoration: underline;'>Suggestion: MUST BUY! (RSI < 40)</strong>")
        else:
            message += (
                f"<strong style='color:green;'>Suggestion: Consider buying (Price drop but MACD not negative yet)</strong>")
    else:
        message += (
            f"<strong style='color:red;'>Wait to buy {ticker} (No significant drop or MACD not aligned)</strong>")

    all_messages.append(message)

# Send email (unchanged)
final_message = "<br><br>".join(all_messages)
if final_message:
    logging.info("Sending summary email.")
    print(final_message)
    send_email(final_message)
else:
    logging.warning("No data to send in the email.")
