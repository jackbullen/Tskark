#!/usr/bin/env python3

import datetime as dt
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from cache import lookup_in_cache, store_in_cache

def date_to_utc_timestamp(date_str):
    '''
        Convert date string to UNIX timestamp.
    '''
    local_date = dt.datetime.strptime(date_str, '%Y-%m-%d')
    utc_date = local_date.replace(tzinfo=dt.timezone.utc)
    return int(utc_date.timestamp())

def get_stock(stock_name, start_date, end_date):
    '''
        Return a Pandas DataFrame containing the historical stock data from Yahoo Finance.
    '''

    query = f"{stock_name}_{start_date}_{end_date}"

    df, dividend_df = lookup_in_cache(query)
    if df is not None and not df.empty:
        print("Loading stock data from cache...")
        return df, dividend_df

    if start_date > end_date:
        print('Error: Start date is later than end date.')
        return None
    
    period1 = date_to_utc_timestamp(start_date)
    period2 = date_to_utc_timestamp(end_date)

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    
    url = f'https://ca.finance.yahoo.com/quote/{stock_name}/history?period1={period1}&period2={period2}&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true'
    driver.get(url)

    rows = driver.find_elements(By.XPATH, '//table[@data-test="historical-prices"]//tbody/tr')
    
    data = []
    dividend_data = []
    for row in rows:
        row_data = [cell.text for cell in row.find_elements(By.XPATH, './td')]
        if row_data:
            if 'Dividend' in row_data[1]:
                dividend_data.append(row_data)
            else:
                data.append(row_data)

    driver.close()

    columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    df = pd.DataFrame(data, columns=columns)

    dividend_df = pd.DataFrame(dividend_data, columns=['Date', 'Info'])

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.drop_duplicates(subset='Date', keep='first')
    df.set_index('Date', inplace=True)

    cols_to_convert = ['Open', 'High', 'Low', 'Close']
    for col in cols_to_convert:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['Volume'] = df['Volume'].fillna('0').str.replace(',', '').astype(int)

    store_in_cache(query, df, dividend_df)

    return df, dividend_df