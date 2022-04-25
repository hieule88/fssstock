import pandas as pd
import numpy as np 
from statsmodels.tsa.api import VAR

a = np.random.rand(1000,16)
a= pd.DataFrame(a)
data_train = a[:-25]
data_test = a[-25:]

differenced_data = data_train.diff(1)
differenced_data.dropna(inplace=True)

var_model = VAR(differenced_data)

print("MODEL IS RUNNING")
lag_results = var_model.select_order(5)
selected_lag = lag_results.aic # selected_lag = 13
var_fitresults = var_model.fit(selected_lag)

print("MODEL IS PREDICTING")
predict_data = var_fitresults.forecast(y= differenced_data.values[selected_lag*(-1):], steps=25)
df_forecast=pd.DataFrame(data=predict_data)

print("MODEL IS REVERSING")
df_forecast['PREDICT'] = data_train[0].iloc[-1] + df_forecast[0].cumsum()
print(df_forecast['PREDICT'])
print(data_test[0])
data_test[0].plot(figsize=(12,5),legend=True)
df_forecast['PREDICT'].plot(legend=True)

import time

time.sleep(2.4)