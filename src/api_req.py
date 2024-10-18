import requests
import mysql.connector
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import yfinance as yf
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
from flask import Flask,render_template, request , redirect, url_for

# api key = ZHBXASJLVDEZ545C
#SH9HLNNKE9E9QMTU
app = Flask(__name__)
# Replace with your own values
# API_KEY = 'ZHBXASJLVDEZ545C'  #  Alpha Vantage API Key
API_KEY = 'SH9HLNNKE9E9QMTU'  #  Alpha Vantage API Key
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'kedar',
    'password': 'StrongPassword@123',
    'database': 'stock_data'
}

# List of Nifty 50 stock symbols
nifty50_stocks = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
    'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'BHARTIARTL.NS', 'LT.NS',
    'HCLTECH.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'ITC.NS', 'BAJFINANCE.NS',
    'MARUTI.NS', 'TITAN.NS', 'ULTRACEMCO.NS', 'WIPRO.NS', 'TECHM.NS',
    'SUNPHARMA.NS', 'POWERGRID.NS', 'TATASTEEL.NS', 'NESTLEIND.NS', 'JSWSTEEL.NS',
    'NTPC.NS', 'GRASIM.NS', 'COALINDIA.NS', 'ONGC.NS', 'BRITANNIA.NS', 
    'CIPLA.NS', 'ADANIPORTS.NS', 'DRREDDY.NS', 'HDFCLIFE.NS', 'BAJAJ-AUTO.NS', 
    'HEROMOTOCO.NS', 'HINDALCO.NS', 'EICHERMOT.NS', 'DIVISLAB.NS', 'APOLLOHOSP.NS',
    'M&M.NS', 'SHREECEM.NS', 'INDUSINDBK.NS', 'TATAMOTORS.NS', 'SBILIFE.NS',
    'HAVELLS.NS', 'DLF.NS', 'PIDILITIND.NS', 'ICICIPRULI.NS', 'ADANIENT.NS'
]

#------------------------------------------------------------------------------------------------

def fetch_daily_stock_data(stock_symbol, start_date, end_date):
    # Fetch data using yfinance
    stock_data = yf.download(stock_symbol, start=start_date, end=end_date)
    
    # Reset index to get date as a column
    stock_data.reset_index(inplace=True)

    # Format the data for storage
    formatted_data = []
    for index, row in stock_data.iterrows():
        formatted_data.append({
            'date': row['Date'].date(),
            'open': row['Open'],
            'high': row['High'],
            'low': row['Low'],
            'close': row['Close'],
            'volume': int(row['Volume']),
        })

    return formatted_data



def store_stock_data(stock_symbol, stock_data):
    print(f"Inserting data for stock: {stock_symbol}")  # Debugging line
    print(stock_data)  # Print the fetched stock data
    
    conn = mysql.connector.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    for record in stock_data:
        cursor.execute(
            """
            INSERT INTO daily_prices (stock_id, date, open_price, high_price, low_price, close_price, volume)
            VALUES (
                (SELECT stock_id FROM stocks WHERE stock_symbol = %s),
                %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                open_price = VALUES(open_price),
                high_price = VALUES(high_price),
                low_price = VALUES(low_price),
                close_price = VALUES(close_price),
                volume = VALUES(volume);
            """,
            (stock_symbol, record['date'], record['open'], record['high'], record['low'], record['close'], record['volume'])
        )
    
    conn.commit()
    cursor.close()
    conn.close()
#------------------------------------------------------------------------------------------------
def fetch_stock_data_from_mysql(stock_symbol):
    conn = mysql.connector.connect(
        host='localhost',
        user='kedar',
        password='StrongPassword@123',
        database='stock_data'
    )
    query = """
        SELECT d.date, d.close_price
        FROM daily_prices d, stocks s
        WHERE s.stock_symbol = %s
        AND d.stock_id = s.stock_id
        ORDER BY date ASC;
    """
    stock_data = pd.read_sql(query, conn , params = (stock_symbol,))
    conn.close()
    
    # Convert date column to datetime format
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    stock_data.set_index('date', inplace=True)
    prices = stock_data['close_price'].tolist()
    return(prices)
#------------------------------------------------------------------------------------------------
@app.route('/search_a_stock/<stock_symbol>' , methods = ['GET'])
def fetch_all_attributes_of_stock(stock_symbol):
    # symbol = ""+stock_symbol+""
    conn = mysql.connector.connect(
        host='localhost',
        user='kedar',
        password='StrongPassword@123',
        database='stock_data'
    )
    query = """
        SELECT s.stock_symbol, d.stock_id, d.date, d.open_price, d.high_price, d.low_price, d.close_price, d.volume 
        FROM daily_prices d 
        JOIN stocks s ON s.stock_id = d.stock_id 
        WHERE s.stock_symbol = %s
        ORDER BY d.date ASC;
    """
    
    print(query)
    stock_data = pd.read_sql(query, conn , params=(stock_symbol,))
    conn.close()
    stock_data.set_index('date', inplace=True)
    close_prices = stock_data['close_price'].tolist()
    open_prices = stock_data['open_price'].tolist()
    high_price = stock_data['high_price'].tolist()
    volume = stock_data['volume'].tolist()
    dates = stock_data.index.tolist()

    str1 = '<html> <head>' \
       '<style>' \
       'table { border-collapse: collapse; width: 100%; } ' \
       'th, td { border: 2px solid black; padding: 8px; text-align: left; } ' \
       'th { background-color: #f2f2f2; }' \
       '</style>' \
       '</head>' \
       '<body bgcolor="#90EE90">' \
       '<table>' \
       '<thead>' \
       '<tr>' \
       '<th>Date</th><th>Stock Name</th><th>Opening Prices</th><th>Closing Prices</th><th>VOLUME</th>' \
       '</tr></thead><tbody>'

    
    for i in range (len(dates)):
        str1+=f"<tr> <td>{dates[i]}</td><td>{stock_symbol}</td><td>{open_prices[i]}</td><td>{close_prices[i]}</td><td>{volume[i]}</td></tr>"
    str1 += '</tbody></table></html>'
    return str1
#------------------------------------------------------------------------------------------------
@app.route('/predict/<stock_symbol>' , methods = ['GET'])
def prediction_engine(stock_symbol):
    days_to_predict = 10
    prices_var = fetch_stock_data_from_mysql(stock_symbol)
    prices = np.array(prices_var).reshape(-1,1)
    days = np.arange(len(prices)).reshape(-1, 1)
    model = LinearRegression()
    model.fit(days, prices)
    future_days = np.arange(len(prices), len(prices) + days_to_predict).reshape(-1, 1)
    predicted_prices = model.predict(future_days)
    price_list = predicted_prices.flatten().tolist()
    
    str1 = '<html> <head>' \
       '<style>' \
       'table { border-collapse: collapse; width: 100%; } ' \
       'th, td { border: 2px solid black; padding: 8px; text-align: left; } ' \
       'th { background-color: #f2f2f2; }' \
       '</style>' \
       '</head>' \
       '<body bgcolor="#90EE90">' \
       '<table>' \
       '<thead>' \
       '<tr>' \
       '<th>Future Day</th><th>Predicted Price</th>' \
       '</tr></thead><tbody>'

    for i in range (len(price_list)):
        str1+=f"<tr> <td>Day {i}</td><td>{price_list[i]}</td></tr>"
    str1 += '</tbody></table></html>'
    return str1

#------------------------------------------------------------------------------------------------
def fill_table():
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=200)  # Last 60 days
    for stock in nifty50_stocks:
        stock_data = fetch_daily_stock_data(stock, start_date, end_date)
        store_stock_data(stock, stock_data)

#------------------------------------------------------------------------------------------------
@app.route('/main_menu')
def main_menu(): 
    str1 = '<html> <head>'
    str1 += ' <title>Main Menu</title> </head><body bgcolor="#90EE90">'
    str1 += '<h1>MAIN MENU</h1>'
    str1+= '<p><a href="/daily_time_series">VIEW ALL STOCKS TIME SERIES</a></p>'
    str1+= '<p><a href="/search_a_stock>VIEW A PARTICULAR STOCK DATA</a></p>'
    str1+='<p><a href="/search_a_stock>VIEW A PARTICULAR STOCK DATA</a></p>'
    str1+= '</html>'
    return str1
#----------------------------------------------------------------------------------
@app.route('/inpform', methods=['GET', 'POST'])
def inpform():
    symbol = request.form['stockSymbol']
    if request.form['button'] == 'Predicted Prices':
        if request.method == 'POST':
            return redirect(url_for('prediction_engine', stock_symbol=symbol))
        else:
            return redirect(url_for('prediction_engine', stock_symbol=symbol))
    elif request.form['button'] == 'Time Series For Stock':
        if request.method == 'POST':
            return redirect(url_for('fetch_all_attributes_of_stock', stock_symbol=symbol))
        else:
            return redirect(url_for('fetch_all_attributes_of_stock', stock_symbol=symbol))
#--------------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()


