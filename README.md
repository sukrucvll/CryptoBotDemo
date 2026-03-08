# CryptoPulse (Demo)

This is a **demo version** of a cryptocurrency analysis and prediction system.

## Description

- Fetches **coin data** via API.
- Calculates a wide range of **technical indicators**, including:
  - RSI, MFI, Bollinger Bands (BB), Williams %R (WILR)
  - Stochastic RSI (STRSI), DMI, ATR, MACD
  - Heiken Ashi (HAYKIN), TRIX, CCI
- Detects **buy/sell signals** based on historical data and indicators.
- Stores all trading actions in **SQL** (e.g., where a buy/sell occurred, prices, positions).
- Aggregates and stores **all computed data** in **MongoDB** for historical tracking and analysis.
- Uses **LSTM neural networks** to predict **future price movements** based on historical patterns.
- Designed as a **demo project**; API keys and production configs are removed.

## Features

- Real-time or historical **coin data streaming**
- **Technical analysis** & candle pattern detection
- **Buy/Sell signal generation**
- **SQL storage** for detailed trade records
- **MongoDB storage** for aggregated data
- **LSTM-based price prediction** for future trend estimation
