import sys
import os
import pandas as pd
import numpy as np
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if sys.platform.startswith('win') and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras import regularizers
from tensorflow.keras.optimizers import Adam
from storage.mongo_db import get_db

mydb = get_db('SOLUSDT')
koleksiyon_adi = "SOLUSDT_5mislemler"
mycollection = mydb[koleksiyon_adi]


veriler = mycollection.find({}, {"_id": 0})

df = pd.DataFrame(list(veriler))
pd.set_option('display.max_columns', None)



df = df.fillna(0)


drop_cols = [
   
    'kapanis_zamani',
    'class',
    'ema9',
    'histogram',
    'alt_banda_yaklasti_decision',
    'ust_banda_yaklasti_decision',
    'ust_banda_yaklasti_satis',
    'alt_banda_yaklasti_10',
    'ust_banda_yaklasti_10',
    'alt_banda_yaklasti_20',
    'ust_banda_yaklasti_20',
    'orta_band'
]
df.drop(drop_cols, axis=1, inplace=True)

df = df.sort_values('zaman_damgasi').set_index('zaman_damgasi')
bool_cols = [
    'dusus','yukselis',
    'ust_banda_degdi','alt_banda_degdi',
    'ust_banda_yaklasti','alt_banda_yaklasti'
]
df[bool_cols] = df[bool_cols].astype(int)

cols = [
    'acilis','yuksek','dusuk','kapanis','hacim',
    '+DI14','-DI14','ADX','DX',
    'ust_band','alt_band','band_genisligi','CCI_14','CCI_SMA14','ema20','ema50','ust_banda_degdi','alt_banda_degdi',
    'CCI_SMA20','dusus','yukselis','band_genisligi','band_genisligi_yuzde_oran','ust_banda_yaklasti','alt_banda_yaklasti',
'sonuc','islemde']


last_n = 4000
df_main = df[cols].iloc[-100000:-last_n].drop_duplicates(keep='last')
df_lastN = df[cols].iloc[-last_n:]


scalers = {}
df_scaled = df_main.copy()
for col in df_main.columns:
    scalers[col] = MinMaxScaler()
    df_scaled[col] = scalers[col].fit_transform(df_main[[col]])


def deger_esitleme(data, target_index, seq_length=60):
    X, y = [], []
    for i in range(len(data)-seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length, target_index])
    return np.array(X), np.array(y)

seq_length = 60
target_index = df_scaled.columns.get_loc('sonuc')
data = df_scaled.values
X, y = deger_esitleme(data, target_index, seq_length)


split = int(0.8 * len(X))
X_train, y_train = X[:split], y[:split]
X_test, y_test = X[split:], y[split:]


model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2]),
         kernel_regularizer=regularizers.l2(1e-4)),
    Dropout(0.3),
    LSTM(32),
    Dropout(0.2),
    Dense(1)
])

early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
model.compile(loss='mae', optimizer=Adam(learning_rate=1e-3))
model.fit(X_train, y_train, epochs=50, batch_size=32,
          validation_data=(X_test, y_test),
          callbacks=[early_stop], verbose=1)


def batch_predict(model, X, batch_size=None):
    if batch_size is None:
        batch_size = max(1, int(1e6 / (X.shape[1]*X.shape[2])))
    y_pred = []
    for i in range(0, X.shape[0], batch_size):
        X_batch = X[i:i+batch_size]
        y_batch_pred = model.predict(X_batch, verbose=0)
        y_pred.append(y_batch_pred)
    return np.vstack(y_pred)


def inverse_kapanis(y_scaled, scaler):
    return scaler.inverse_transform(y_scaled.reshape(-1,1))


y_pred = batch_predict(model, X_test)
y_pred_x_train = batch_predict(model, X_train)

y_test_orig = inverse_kapanis(y_test, scalers['kapanis'])
y_train_orig = inverse_kapanis(y_train, scalers['kapanis'])
y_pred_orig = inverse_kapanis(y_pred, scalers['kapanis'])
y_pred_x_train_orig = inverse_kapanis(y_pred_x_train, scalers['kapanis'])


df_lastN_scaled = df_lastN.copy()
for col in df_lastN_scaled.columns:
    df_lastN_scaled[col] = scalers[col].transform(df_lastN_scaled[[col]])

df_for_lastN = pd.concat([df_scaled.tail(seq_length), df_lastN_scaled])
df_for_lastN = df_for_lastN.reset_index(drop=True)

X_lastN, y_lastN = deger_esitleme(df_for_lastN.values, target_index, seq_length=seq_length)
y_lastN_pred = batch_predict(model, X_lastN)

y_lastN_orig = inverse_kapanis(y_lastN, scalers['kapanis'])
y_lastN_pred_orig = inverse_kapanis(y_lastN_pred, scalers['kapanis'])


print("Saat\tGerçek\tTahmin")
for i, idx in enumerate(df_lastN.index):
    print(f"{idx}\t{y_lastN_orig[i][0]:.4f}\t{y_lastN_pred_orig[i][0]:.4f}")

plt.figure(figsize=(12,5))
plt.plot(df_lastN.index, y_lastN_orig, label="Gerçek", marker='o')
plt.plot(df_lastN.index, y_lastN_pred_orig, label="Tahmin", marker='x')
plt.title(f"Son {last_n} Verinin Tahmini vs Gerçek Kapanış Değerleri")
plt.xlabel("Zaman")
plt.ylabel("Kapanış Fiyatı")
plt.legend()
plt.xticks(rotation=45)
plt.show()


def print_metrics(y_true, y_pred, label="Test"):
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    print(f"{label} MSE  : {mse:.4f}")
    print(f"{label} RMSE : {rmse:.4f}")
    print(f"{label} MAE  : {mae:.4f}")
    print(f"{label} R²   : {r2:.4f}")
    print('-------------------------')

print_metrics(y_test_orig, y_pred_orig, "Test")
print_metrics(y_train_orig, y_pred_x_train_orig, "Train")
