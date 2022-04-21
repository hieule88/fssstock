import pandas as pd
import numpy as np 
from statsmodels.tsa.api import VAR

a = np.random.rand(10,16)
a= pd.DataFrame(a)
var_model = VAR(a)
lag_results = var_model.select_order()
selected_lag = lag_results.aic # selected_lag = 13
var_fitresults = var_model.fit(selected_lag)

predict_val = var_fitresults.forecast(y= a.values[-8:], steps=25)