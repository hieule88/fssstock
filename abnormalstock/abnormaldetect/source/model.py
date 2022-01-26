from os import replace
import pandas as pd
from pandas.core.algorithms import diff
from statsmodels.tsa.stattools import adfuller, kpss, zivot_andrews
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from statsmodels.tsa.api import VAR

import warnings
warnings.filterwarnings("ignore")

class VarModel():
    def __init__(self, maxlag=5, difftest= 'mean', stationtest= 'adf', \
                featureimportance= 'corr', topfeature= 12, fithresh= 0.1, \
                scoreconvert= 'binning', scorethresh= 0.1):
        self.count_error = 0
        self.maxlag = maxlag
        self.difftest = difftest
        self.stationtest = stationtest
        self.featureimportance = featureimportance
        self.topfeature = topfeature

        self.fithresh = fithresh
        self.scoreconvert = scoreconvert
        self.scorethresh = scorethresh

    def binning(datacolumn):
        max_col = datacolumn.max()
        max_col = float(max_col)
        bin_len = max_col/3
        bins = [i*bin_len for i in range(3)]
        for i in datacolumn.index:
            if datacolumn.at[i, 'Score'] < bins[0]:
                datacolumn.at[i, 'Score'] =0
            elif datacolumn.at[i, 'Score'] >= bins[0] and datacolumn.at[i, 'Score'] < bins[1]:
                datacolumn.at[i, 'Score'] =1
            elif datacolumn.at[i, 'Score'] >= bins[1] and datacolumn.at[i, 'Score'] < bins[2]:
                datacolumn.at[i, 'Score'] =2
            elif datacolumn.at[i, 'Score'] >= bins[2]:
                datacolumn.at[i, 'Score'] =3

        return datacolumn

    def test_stationarity(self, ts_data, column='', signif=0.05, series=False, type = 'adf'):
        if type == 'adf':
            if series:
                adf_test = adfuller(ts_data, autolag='AIC')
            else:
                adf_test = adfuller(ts_data[column], autolag='AIC')
            p_value = adf_test[1]
            if p_value <= signif:
                test_result = True
            else:
                test_result = False
        elif type == 'kpss':
            if series:
                kpsstest = kpss(ts_data, regression='c', nlags="auto")
            else:
                kpsstest = kpss(ts_data[column], regression='c', nlags="auto")
            p_value = kpsstest[1]
            if p_value < signif:
                test_result = False
            else:
                test_result = True
        elif type == 'adf_kpss':
            if self.test_stationarity(ts_data, column, signif, series, type= 'adf') \
                and self.test_stationarity(ts_data, column, signif, series, type= 'kpss'):
                return True
            else:
                return False
        elif type == 'zivot_andrews':
            if series:
                zatest = zivot_andrews(ts_data, regression='c', nlags="auto")
            else:
                zatest = zivot_andrews(ts_data[column], regression='c', nlags="auto")
            p_value = zatest[1]
            if p_value > signif:
                test_result = False
            else:
                test_result = True
        return test_result

    def differencing(self, data, column, order):
        if self.difftest == 'mean':
            differenced_data = data[column].diff(order)
            differenced_data.fillna(differenced_data.mean(), inplace=True)
            return differenced_data
        elif self.difftest == 'log':
            differenced_data = data[column].apply(np.log)
            differenced_data = np.log(data[column])
            return differenced_data
        elif self.difftest == 'saiphan':
            # ADD SAI PHAN
            return

    def find_anomalies(self, squared_errors):
        threshold = np.mean(squared_errors) + np.std(squared_errors)
        predictions = (squared_errors >= threshold).astype(int)
        return predictions, threshold

    def process(self, dataset, p_ticker):
        ticker_feature = dataset.loc[dataset['name']==p_ticker].drop(columns='name')
        txdate = ticker_feature['TXDATE']
        ticker_feature.drop(columns='TXDATE', inplace=True)
        non_stationary_cols = [col for col in ticker_feature.columns \
                                if not self.test_stationarity(ticker_feature, column=col, type= self.stationtest)]

        for col in non_stationary_cols:
            ticker_feature[col] = self.differencing(ticker_feature, col, 1)

        # find selected_lag
        
        column_to_model = list(ticker_feature.columns)

        while(1):
            try:
                self.maxlag = 5 
                var_model = VAR(ticker_feature[column_to_model])
                # select the best lag order
                lag_results = var_model.select_order(self.maxlag)

                selected_lag = lag_results.aic # selected_lag = 13

                var = VAR(ticker_feature[column_to_model])
                var_fitresults = var.fit(selected_lag)

                squared_errors = var_fitresults.resid.sum(axis=1)**2
                price_errors = pd.DataFrame(var_fitresults.resid['close'])
                price_errors.rename(columns={'close': 'Score'}, inplace=True)
                
                predictions, threshold = self.find_anomalies(squared_errors) 

                data = pd.concat([ticker_feature[column_to_model].iloc[selected_lag:, :], txdate.iloc[selected_lag:],price_errors[selected_lag:] ], axis=1)
                data['Predictions'] = predictions.values

                #add correlation
                top = self.feature_importance(ticker_feature, column_to_model, selected_lag)
                output= data[['TXDATE', 'Score']].loc[data['Predictions'] ==1], top
            except Exception as e:
                e = str(e)
                e_index = 0
                for i in range(len(e)):
                    if e[i] == '-':
                        e_index = i
                        break
                if e_index == 0 or e_index > 3:
                    print(e + ' at Ticker: ', p_ticker)
                    self.count_error = self.count_error + 1
                    break
                e_column = int(e[:e_index])
                column_to_model.remove(column_to_model[e_column-1])
        
        return output

    def feature_importance(self, ticker_feature, column_to_model, selected_lag):
        if self.featureimportance == 'corr' :
            corr = pd.DataFrame(ticker_feature[column_to_model].iloc[selected_lag:, :].corr(method='pearson')['close'])

            coef_dict = dict(zip(corr.index ,corr.values))
            coef_dict = dict(sorted(coef_dict.items(), key= lambda item: item[1], reverse=True)[1 : self.topfeature + 1])
            
            return coef_dict