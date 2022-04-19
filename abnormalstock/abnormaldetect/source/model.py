from os import replace
from random import Random
import pandas as pd
from pandas.core.algorithms import diff
from statsmodels.tsa.stattools import adfuller, kpss, zivot_andrews
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from statsmodels.tsa.api import VAR
from dateutil import parser

import warnings
warnings.filterwarnings("ignore")

def binning(scoreconvert, scorethresh, datacolumn):
        max_col = datacolumn.max()
        max_col = float(max_col)
        min_col = datacolumn.min()
        min_col = float(min_col)

        if scoreconvert == '3-binning':
            if max_col <= scorethresh :
                for i in datacolumn.index:
                    datacolumn.at[i, 'Score'] =0
            else: 
                bin_len_max = (max_col - scorethresh )/3
                bins = [i*bin_len_max for i in range(3)]
                for i in datacolumn.index:
                    if datacolumn.at[i, 'Score'] <= bins[0] and datacolumn.at[i, 'Score'] >= 0:
                        datacolumn.at[i, 'Score'] =0
                    elif datacolumn.at[i, 'Score'] > bins[0] and datacolumn.at[i, 'Score'] <= bins[1]:
                        datacolumn.at[i, 'Score'] =1
                    elif datacolumn.at[i, 'Score'] > bins[1] and datacolumn.at[i, 'Score'] <= bins[2]:
                        datacolumn.at[i, 'Score'] =2
                    elif datacolumn.at[i, 'Score'] > bins[2]:
                        datacolumn.at[i, 'Score'] =3

            if min_col >= scorethresh*(-1.0) : 
                for i in datacolumn.index:
                    datacolumn.at[i, 'Score'] =0
            else: 
                bin_len_min = (min_col - scorethresh*(-1.0))/3
                bins = [i*bin_len_min for i in range(3)]
                for i in datacolumn.index:
                    if datacolumn.at[i, 'Score'] >= bins[0] and datacolumn.at[i, 'Score'] <= 0:
                        datacolumn.at[i, 'Score'] =0
                    elif datacolumn.at[i, 'Score'] < bins[0] and datacolumn.at[i, 'Score'] >= bins[1]:
                        datacolumn.at[i, 'Score'] =1
                    elif datacolumn.at[i, 'Score'] < bins[1] and datacolumn.at[i, 'Score'] >= bins[2]:
                        datacolumn.at[i, 'Score'] =2
                    elif datacolumn.at[i, 'Score'] < bins[2]:
                        datacolumn.at[i, 'Score'] =3

        elif scoreconvert == '4-binning':
            if max_col <= scorethresh :
                for i in datacolumn.index:
                    datacolumn.at[i, 'Score'] =0
            else: 
                bin_len_max = (max_col - scorethresh )/4
                bins = [i*bin_len_max for i in range(4)]
                for i in datacolumn.index:
                    if datacolumn.at[i, 'Score'] <= bins[0] and datacolumn.at[i, 'Score'] >= 0:
                        datacolumn.at[i, 'Score'] =0
                    elif datacolumn.at[i, 'Score'] > bins[0] and datacolumn.at[i, 'Score'] <= bins[1]:
                        datacolumn.at[i, 'Score'] =1
                    elif datacolumn.at[i, 'Score'] > bins[1] and datacolumn.at[i, 'Score'] <= bins[2]:
                        datacolumn.at[i, 'Score'] =2
                    elif datacolumn.at[i, 'Score'] > bins[2] and datacolumn.at[i, 'Score'] <= bins[3]:
                        datacolumn.at[i, 'Score'] =3
                    elif datacolumn.at[i, 'Score'] > bins[3]:
                        datacolumn.at[i, 'Score'] =4

            if min_col >= scorethresh*(-1.0) : 
                for i in datacolumn.index:
                    datacolumn.at[i, 'Score'] =0
            else: 
                bin_len_min = (min_col - scorethresh*(-1.0))/4
                bins = [i*bin_len_min for i in range(4)]
                for i in datacolumn.index:
                    if datacolumn.at[i, 'Score'] >= bins[0] and datacolumn.at[i, 'Score'] <= 0:
                        datacolumn.at[i, 'Score'] =0
                    elif datacolumn.at[i, 'Score'] < bins[0] and datacolumn.at[i, 'Score'] >= bins[1]:
                        datacolumn.at[i, 'Score'] =1
                    elif datacolumn.at[i, 'Score'] < bins[1] and datacolumn.at[i, 'Score'] >= bins[2]:
                        datacolumn.at[i, 'Score'] =2
                    elif datacolumn.at[i, 'Score'] < bins[2] and datacolumn.at[i, 'Score'] >= bins[3]:
                        datacolumn.at[i, 'Score'] =3
                    elif datacolumn.at[i, 'Score'] < bins[3]:
                        datacolumn.at[i, 'Score'] =4

        return datacolumn

def find_anomalies(squared_errors):
    threshold = np.mean(squared_errors) + np.std(squared_errors)
    predictions = (squared_errors >= threshold).astype(int)
    return predictions, threshold

class VarModel():
    def __init__(self, maxlag=5, difftest= 'diffty', stationtest= 'adf', \
                featureimportance= 'corr', topfeature= 12, fithresh= 0.0, \
                scoreconvert= '3-binning', scorethresh= 0.0):
        self.count_error = 0
        self.maxlag = maxlag
        self.difftest = difftest
        self.stationtest = stationtest
        self.featureimportance = featureimportance
        self.topfeature = topfeature

        self.fithresh = fithresh
        self.scoreconvert = scoreconvert
        self.scorethresh = scorethresh

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
        if self.difftest == 'diffty':
            differenced_data = data[column].diff(order)
            differenced_data.fillna(differenced_data.mean(), inplace=True)
            differenced_data.fillna(0, inplace=True)
            return differenced_data
        elif self.difftest == 'log':
            differenced_data = data[column].apply(np.log)
            differenced_data.interpolate(method='ffill', order=2, inplace=True)
            differenced_data.fillna(0, inplace=True)
            return differenced_data
        elif self.difftest == 'cbrt':
            differenced_data = data[column].apply(np.cbrt)
            differenced_data.interpolate(method='ffill', order=2, inplace=True)
            differenced_data.fillna(0, inplace=True)
            return differenced_data
        elif self.difftest == 'log&diffty':
            differenced_data = data[column].apply(np.log)
            differenced_data = differenced_data.diff(order)
            differenced_data.fillna(differenced_data.mean(), inplace=True)
            differenced_data.fillna(0, inplace=True)
            return differenced_data  
        elif self.difftest == 'cbrt&diffty':
            differenced_data = data[column].apply(np.cbrt)
            differenced_data = differenced_data.diff(order)
            differenced_data.fillna(differenced_data.mean(), inplace=True)
            differenced_data.fillna(0, inplace=True)
            return differenced_data            

    def process(self, dataset, p_ticker):
        ticker_feature = dataset.loc[dataset['name']==p_ticker].drop(columns='name')
        txdate = ticker_feature['TXDATE']
        ticker_feature.drop(columns='TXDATE', inplace=True)
        non_stationary_cols = [col for col in ticker_feature.columns \
                                if not self.test_stationarity(ticker_feature, column=col, type= self.stationtest)]

        real_close = ticker_feature['close']

        for col in non_stationary_cols:
            ticker_feature[col] = self.differencing(ticker_feature, col, 1)
        # find selected_lag
        
        column_to_model = list(ticker_feature.columns)

        while(1):
            try:
                var_model = VAR(ticker_feature[column_to_model])
                # select the best lag order
                lag_results = var_model.select_order(self.maxlag)

                selected_lag = lag_results.aic # selected_lag = 13

                var = VAR(ticker_feature[column_to_model])
                var_fitresults = var.fit(selected_lag)
                squared_errors = var_fitresults.resid.sum(axis=1)**2
                price_errors = pd.DataFrame(var_fitresults.resid['close'])
                price_errors.rename(columns={'close': 'Score'}, inplace=True)
                residual = price_errors.copy(deep= True)
                
                price_errors = binning(self.scoreconvert, self.scorethresh, price_errors)

                predictions, threshold = find_anomalies(squared_errors)

                data = pd.concat([ticker_feature[column_to_model].iloc[selected_lag:, :], txdate.iloc[selected_lag:],price_errors[selected_lag:]], axis=1)
                data['Predictions'] = predictions.values
                data['Residual'] = residual.values
                # print(data.head(50))
                # print('\nLIST ABNORMAL DAYS OF TICKER:', p_ticker)
                # print(data[['TXDATE', 'Score', 'Residual']].loc[data['Predictions'] ==1])

                #add correlation
                top = self.feature_importance(ticker_feature, column_to_model, selected_lag)

                # retransform_residual, predict_close_cost = self.retransform(ticker_feature['close'][selected_lag:], residual.values)
                
                # return TXDate, Score Fraud, Residual, Top Features, Squared Error, Threshold, Real Close Cost
                return data[['TXDATE', 'Score', 'Residual']].loc[data['Predictions'] ==1], \
                        top, squared_errors, threshold, txdate.iloc[selected_lag:], \
                        ticker_feature['close'][selected_lag:], residual.values

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

    def feature_importance(self, ticker_feature, column_to_model, selected_lag):
        if self.featureimportance == 'corr' :
            corr = pd.DataFrame(ticker_feature[column_to_model].iloc[selected_lag:, :].corr(method='pearson')['close'])
            coef_dict = dict(zip(corr.index ,corr.values))
            coef_dict = dict(sorted(coef_dict.items(), key= lambda item: item[1], reverse=True)[1 : self.topfeature + 1])
            return coef_dict
            
        elif self.featureimportance == 'varcorr':
            print('CHỨC NĂNG ĐANG PHÁT TRIỂN, HÃY THỬ LẠI THUỘC TÍNH FEATURE IMPORTANCE = CORR')

from linearmodels.panel import PanelOLS
class FemModel():
    def __init__(self, low_memory: str, cov_type: str, level: int, has_constant= True, \
                entity_effects=True, time_effects=True, other_effects=None, \
                use_lsdv=False, use_lsmr=False, \
                difftest= 'diffty', stationtest= 'adf', \
                featureimportance= 'corr', topfeature= 12, fithresh= 0.0, \
                scoreconvert= '3-binning', scorethresh= 0.0):
        self.count_error = 0
        
        # FEM'S PARAMETERS
        self.entity_effects = entity_effects
        self.time_effects = time_effects
        self.other_effects = other_effects
        self.use_lsdv = use_lsdv
        self.use_lsmr = use_lsmr
        
        self.low_memory = low_memory
        self.cov_type = cov_type
        self.level = level
        self.has_constant = has_constant

        # FOR STATIONARITY TEST AND TRANSFORM
        self.difftest = difftest
        self.stationtest = stationtest
        self.featureimportance = featureimportance
        self.topfeature = topfeature

        # FOR LABELLING
        self.fithresh = fithresh
        self.scoreconvert = scoreconvert
        self.scorethresh = scorethresh
    
    def process(self, data):
        name = pd.Categorical(data.name)
        # data['TXDATE'] = data['TXDATE'].apply(parser.parse)
        data["name"] = name
        txdate = pd.Categorical(data.TXDATE)
        data = data.set_index(["name", "TXDATE"])
        data["TXDATE"] = txdate
        dependent = 'close'
        exog = list(data.columns)
        exog.remove(dependent)
        print('Model is running')
        model = PanelOLS(data[dependent], data[exog], check_rank = False, entity_effects= self.entity_effects, \
                        time_effects= self.time_effects)
                        
        print('Call model DONE')
        res = model.fit()
        # res = model.fit(use_lsdv = self.use_lsdv, use_lsmr = self.use_lsmr, \
        #                 low_memory = self.low_memory, cov_type = self.cov_type)
        print('Fit model DONE')
        quit()
        resid = res.resids
        price_errors = pd.DataFrame(resid)
        price_errors.rename(columns={'residual': 'Score'}, inplace=True)
        residual = price_errors.copy(deep= True)
        
        price_errors = binning(self.scoreconvert, self.scorethresh, price_errors)
        squared_errors = np.square(resid)
        
        predictions, threshold = find_anomalies(squared_errors) 
        
        results = pd.concat([data['close'], price_errors], axis=1)
        results['Predictions'] = predictions.values
        results['Residual'] = residual.values
        results['TXDATE'] = results.index.get_level_values('TXDATE')
        results = results.droplevel('TXDATE')
        # top = self.feature_importance(data[exog])

        # return TXDate, Score Fraud, Residual, Top Features, Squared Error, Threshold, Real Close Cost
        return results[['TXDATE', 'Score', 'Residual']].loc[results['Predictions'] ==1], \
                        squared_errors, threshold, txdate, \
                        data['close'], residual.values
        # return results[['TXDATE', 'Score', 'Residual']].loc[results['Predictions'] ==1], \
        #                 top, squared_errors, threshold, txdate, \
        #                 data['close'], residual.values

    def feature_importance(self, ticker_feature):
        if self.featureimportance == 'corr' :
            corr = pd.DataFrame(ticker_feature.corr(method='pearson')['close'])
            coef_dict = dict(zip(corr.index ,corr.values))
            coef_dict = dict(sorted(coef_dict.items(), key= lambda item: item[1], reverse=True)[1 : self.topfeature + 1])
            return coef_dict
            
        elif self.featureimportance == 'another_corr':
            print('CHỨC NĂNG ĐANG PHÁT TRIỂN, HÃY THỬ LẠI THUỘC TÍNH FEATURE IMPORTANCE = CORR')

from linearmodels.panel import RandomEffects
class RemModel():
    def __init__(self, cov_type: str, level: int, has_constant: False, small_sample= False, \
                maxlag=5, difftest= 'diffty', stationtest= 'adf', \
                featureimportance= 'corr', topfeature= 12, fithresh= 0.0, \
                scoreconvert= '3-binning', scorethresh= 0.0):
        self.count_error = 0

        # REM'S PARAMETERS
        self.cov_type = cov_type
        self.level = level
        self.has_constant = has_constant
        self.small_sample = small_sample

        # FOR STATIONARITY TEST AND TRANSFORM
        self.maxlag = maxlag
        self.difftest = difftest
        self.stationtest = stationtest
        self.featureimportance = featureimportance
        self.topfeature = topfeature

        # FOR LABELLING
        self.fithresh = fithresh
        self.scoreconvert = scoreconvert
        self.scorethresh = scorethresh
    
    def process(self, data):
        txdate_ogn = data['TXDATE']
        name = pd.Categorical(data.name)
        data['TXDATE'] = data['TXDATE'].apply(parser.parse)
        data["name"] = name
        txdate = pd.Categorical(data.TXDATE)
        data = data.set_index(["name", "TXDATE"])
        data["TXDATE"] = txdate
        dependent = 'close'
        exog = list(data.columns)
        exog.remove(dependent)

        model = RandomEffects(data[dependent], data[exog], check_rank = False)
        res = model.fit()
        resid = res.resids
        price_errors = pd.DataFrame(resid)
        price_errors.rename(columns={'residual': 'Score'}, inplace=True)
        residual = price_errors.copy(deep= True)
        
        price_errors = binning(self.scoreconvert, self.scorethresh, price_errors)
        squared_errors = np.square(resid)
        
        predictions, threshold = find_anomalies(squared_errors) 
        
        results = pd.concat([data['close'], price_errors], axis=1)
        results['Predictions'] = predictions.values
        results['Residual'] = residual.values
        results['TXDATE'] = results.index.get_level_values('TXDATE')
        results = results.droplevel('TXDATE')
        # top = self.feature_importance(data)

        # return TXDate, Score Fraud, Residual, Top Features, Squared Error, Threshold, Real Close Cost
        return results[['TXDATE', 'Score', 'Residual']].loc[results['Predictions'] ==1], \
                        squared_errors, threshold, txdate, \
                        data['close'], residual.values
        # return results[['TXDATE', 'Score', 'Residual']].loc[results['Predictions'] ==1], \
        #                 top, squared_errors, threshold, txdate, \
        #                 data['close'], residual.values

    def feature_importance(self, ticker_feature):
        if self.featureimportance == 'corr' :
            corr = pd.DataFrame(ticker_feature.corr(method='pearson')['close'])
            coef_dict = dict(zip(corr.index ,corr.values))
            coef_dict = dict(sorted(coef_dict.items(), key= lambda item: item[1], reverse=True)[1 : self.topfeature + 1])
            return coef_dict
            
        elif self.featureimportance == 'varcorr':
            print('CHỨC NĂNG ĐANG PHÁT TRIỂN, HÃY THỬ LẠI THUỘC TÍNH FEATURE IMPORTANCE = CORR')