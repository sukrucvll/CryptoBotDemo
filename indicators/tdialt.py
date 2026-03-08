import pandas as pd
import numpy as np
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_tdialt(df, rsi_period=14, sma_period=20, std_dev=2, signal_period=7):

    df['RSI'] = calculate_rsi(df['close'], rsi_period)
    

    df['RSI_SMA'] = df['RSI'].rolling(window=sma_period).mean()
    df['RSI_STD'] = df['RSI'].rolling(window=sma_period).std()
    

    df['Upper_Band'] = df['RSI_SMA'] + (std_dev * df['RSI_STD'])
    df['Lower_Band'] = df['RSI_SMA'] - (std_dev * df['RSI_STD'])
    

    df['Signal_Line'] = df['RSI'].rolling(window=signal_period).mean()
    
  
    df['TDIALT_Signal'] = 0
    df.loc[(df['RSI'] > df['Signal_Line']) & (df['RSI'] < df['Upper_Band']), 'TDIALT_Signal'] = 1  # Al sinyali
    df.loc[(df['RSI'] < df['Signal_Line']) & (df['RSI'] > df['Lower_Band']), 'TDIALT_Signal'] = -1  # Sat sinyali
    
    return df[['RSI', 'RSI_SMA', 'Upper_Band', 'Lower_Band', 'Signal_Line', 'TDIALT_Signal']]

