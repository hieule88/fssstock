import cx_Oracle
import os
import numpy as np
from matplotlib import pyplot as plt
from finta import TA
import pandas as pd
import pandas_ta as ta
BACKEND_DB = 'RISK_USER/RISK_USER@192.168.1.30:1521/orcl.fss.com.vn'
con = cx_Oracle.connect(BACKEND_DB)
cursor = con.cursor()

p_start_date='01/01/2019'
p_end_date='01/01/2021'
p_ticker='%'
#Danh sach ticker
outcursor = cursor.var(cx_Oracle.CURSOR)
cursor.callproc('SP_TA_GET_TICKER_RAWDATA', ['TICKERLIST', p_ticker, p_start_date, p_end_date, outcursor])
refCursor = outcursor.getvalue()

col_names = []
for col in refCursor.description:
    col_names.append(col[0])
dfticker = pd.DataFrame.from_records(refCursor)
dfticker.columns=col_names #dataframe of colname
print(type(dfticker))
#Lich su giao dich cua ticker
outcursorraw = cursor.var(cx_Oracle.CURSOR)
cursor.callproc('SP_TA_GET_TICKER_RAWDATA', ['TVHISTORY1D', p_ticker, p_start_date, p_end_date, outcursorraw])
refCursorRaw = outcursorraw.getvalue()

# --Lấy full lỗi!!!
col_raw_names = []
for col in refCursorRaw.description:
    col_raw_names.append(col[0])

df = pd.DataFrame.from_records(refCursorRaw)
df.columns=col_raw_names
df_ohlcv = df.rename(columns={"O": "open", "H": "high", "L": "low", "C": "close", "V": "volume"})

#Duyệt lấy thông tin từng mã chứng khoán trong danh sách
for row in dfticker.iterrows():
    p_ticker = row[1]['TICKER']
    v_df_ohlcv = df_ohlcv.loc[df_ohlcv['TICKER'] == p_ticker]
    v_df_ohlcv = v_df_ohlcv.sort_values(by=['TXDATE'], ascending=True)
    v_df_ohlcv = v_df_ohlcv.drop(columns=['TICKER', 'TXDATE'])

    print(p_ticker)

p_ticker = 'FPT'
v_df_ohlcv = df_ohlcv.loc[df_ohlcv['TICKER'] == p_ticker]
v_df_ohlcv = v_df_ohlcv.sort_values(by=['TXDATE'], ascending=True)
v_df_ohlcv = v_df_ohlcv.drop(columns=['TICKER', 'TXDATE'])

#Ví dụ Lấy dữ liệu
p_ticker='FPT'
outcursorraw = cursor.var(cx_Oracle.CURSOR)
cursor.callproc('SP_TA_GET_TICKER_RAWDATA', ['TVHISTORY1D', p_ticker, p_start_date, p_end_date, outcursorraw])
refCursorRaw = outcursorraw.getvalue()

col_raw_names = []
for col in refCursorRaw.description:
    col_raw_names.append(col[0])
df = pd.DataFrame.from_records(refCursorRaw)
df.columns=col_raw_names
df_ohlcv = df.rename(columns={"O": "open", "H": "high", "L": "low", "C": "close", "V": "volume"})

v_df_ohlcv = df.rename(columns={"O": "open", "H": "high", "L": "low", "C": "close", "V": "volume"})
v_df_ohlcv = v_df_ohlcv.loc[v_df_ohlcv['TICKER'] == p_ticker]
v_df_ohlcv = v_df_ohlcv.sort_values(by=['TXDATE'], ascending=True)
v_df_ohlcv = v_df_ohlcv.drop(columns=['TICKER', 'TXDATE'])


#Tính các chỉ báo TA hàng ngày từ bảng TICKER_TVHISTORY1D
r_ta_adx = ta.sma(close=v_df_ohlcv["close"], high=v_df_ohlcv["high"], low=v_df_ohlcv["low"])
r_ta_rsi=ta.rsi(close=v_df_ohlcv["close"], length=14)
r_ta_sma = ta.sma(close=v_df_ohlcv["close"], length=14)
r_ta_ema=ta.ema(close=v_df_ohlcv["close"], length=14)
r_ta_macd=ta.macd(close=v_df_ohlcv["close"], length=14)

r_ta_ad = ta.ad(open=v_df_ohlcv["open"], high=v_df_ohlcv["high"],\
                low=v_df_ohlcv["low"], close=v_df_ohlcv["close"],\
                volume=v_df_ohlcv["volume"], length=14)
r_ta_obv = ta.obv(open=v_df_ohlcv["open"], high=v_df_ohlcv["high"], \
                  low=v_df_ohlcv["low"], close=v_df_ohlcv["close"], \
                  volume=v_df_ohlcv["volume"], length=14)
r_ta_mfi = ta.mfi(open=v_df_ohlcv["open"], high=v_df_ohlcv["high"],\
                  low=v_df_ohlcv["low"], close=v_df_ohlcv["close"], \
                  volume=v_df_ohlcv["volume"], length=14)
r_ta_cmf = ta.cmf(open=v_df_ohlcv["open"], high=v_df_ohlcv["high"],\
                  low=v_df_ohlcv["low"], close=v_df_ohlcv["close"],\
                   volume=v_df_ohlcv["volume"], length=14)
r_ta_adosc = ta.adosc(open=v_df_ohlcv["open"], high=v_df_ohlcv["high"],\
                      low=v_df_ohlcv["low"], close=v_df_ohlcv["close"], \
                      volume=v_df_ohlcv["volume"], length=14)