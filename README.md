# Stock Price Prediction using Flask and Linear Regression

## Overview
This project provides a Flask-based UI for stock price prediction using historical stock data. It fetches stock prices for Nifty 50 stocks, performs linear regression for future price prediction, and displays results in an HTML table.

## Features
1. **Flask-based UI**: Allows users to select different stocks for prediction.
2. **Time Series Fetching**: Retrieves historical stock data from Yahoo Finance.
3. **Linear Regression Model**: Uses `sklearn.linear_model.LinearRegression` to predict future stock prices.
4. **Stock Data Storage**: Stores fetched stock data in a MySQL database.
5. **Visualization**: Displays stock time series and predicted values in tabular format.

## Requirements
- Python 3.x
- Flask
- MySQL
- Pandas
- NumPy
- Requests
- Scikit-learn
- Matplotlib
- yFinance

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/stock-prediction.git
   cd stock-prediction
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Configure MySQL database with the following schema:
   ```sql
   CREATE DATABASE stock_data;
   CREATE TABLE stocks (
       stock_id INT AUTO_INCREMENT PRIMARY KEY,
       stock_symbol VARCHAR(10) UNIQUE NOT NULL
   );
   CREATE TABLE daily_prices (
       stock_id INT,
       date DATE,
       open_price FLOAT,
       high_price FLOAT,
       low_price FLOAT,
       close_price FLOAT,
       volume INT,
       PRIMARY KEY (stock_id, date),
       FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
   );
   ```
4. Update database credentials in `DATABASE_CONFIG` inside the Python script.
5. Run the Flask application:
   ```sh
   python app.py
   ```

## Usage
1. Open a browser and visit `http://127.0.0.1:5000/`.
2. Select a stock and choose an option:
   - View historical stock data
   - Predict future stock prices
3. The application fetches data, stores it in MySQL, and displays results in a table.

## Endpoints
- `/` - Main menu with options to fetch stock data and make predictions.
- `/search_a_stock/<stock_symbol>` - Fetches historical stock data from the database.
- `/predict/<stock_symbol>` - Performs linear regression and predicts future prices.

## Future Improvements
- Improve the prediction model using more advanced ML techniques.
- Integrate graphical visualization of stock prices.
- Add user authentication for secure access.

## License
This project is open-source and available under the [MIT License](LICENSE).

