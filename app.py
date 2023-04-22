from flask import Flask, request,render_template
from dotenv import load_dotenv
from email.message import EmailMessage
import ssl
import smtplib
import yfinance as yf
import threading
import os
from twilio.rest import Client

app = Flask(__name__)
load_dotenv()
sender_email = 'testdebug211@gmail.com'
sender_password =os.environ.get('PASSWORD')

context = ssl.create_default_context()

smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context)
smtp.login(sender_email, sender_password)

check_frequency = {'1 minute': 60, '6 hours': 21600, '12 hours': 43200, '24 hours': 86400}
notification_types = ['email','sms']

# user_data = {}

def check_stock_price(symbol, threshold, frequency, notification_type, email):
    stock_data = yf.Ticker(symbol).history(period='1d')
    last_price = stock_data['Close'].iloc[-1]
    if last_price >= float(threshold):
        if notification_type == 'email':
            em = EmailMessage()
            em['From'] = sender_email
            em['To'] = email
            em['Subject'] = 'Stock price alert'
            em.set_content(f'The stock price for {symbol} is currently {last_price}. This is higher than the threshold price of {threshold}.')
            smtp.send_message(em)
            print('Email sent successfully!')
            
        elif notification_type == 'sms':
            account_sid = os.environ['TWILIO_ACCOUNT_SID']
            auth_token = os.environ['TWILIO_AUTH_TOKEN']
            client = Client(account_sid, auth_token)
            message = client.messages \
            .create(
                body=f'The stock price for {symbol} is currently {last_price}. This is higher than the threshold price of {threshold}.',
                from_=os.environ.get('SENDER'),
                to=os.environ.get('RECEIVER'))
            print(message.sid)

        else:
            print('Invalid notification type')
    threading.Timer(frequency, check_stock_price, [symbol, threshold, frequency, notification_type, email]).start()

@app.route('/', methods=['GET', 'POST'])
def get_page_title():
    if request.method == 'POST':
        notification_type = request.form['notification_type']
        if notification_type not in notification_types:
            return 'Invalid notification type'
        if notification_type=="email":
            receiver_email = request.form['receiver_email']
            stock_symbol = request.form['stock_symbol']
            threshold_price = request.form['threshold_price']
            frequency = request.form['frequency']
            check_stock_price(stock_symbol, threshold_price, check_frequency[frequency], notification_type, receiver_email)
        else:
            stock_symbol = request.form['stock_symbol']
            threshold_price = request.form['threshold_price']
            frequency = request.form['frequency']
            check_stock_price(stock_symbol, threshold_price, check_frequency[frequency], notification_type,'abc@example.asdasd')    
        return render_template('stock_price_alert.html')
    else:
        return render_template('stock_price_alert.html')
if __name__ == '__main__':
    app.run(debug=True)