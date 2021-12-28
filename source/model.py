from os import replace
import pandas as pd
from statsmodels.tsa.stattools import adfuller
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")

def binning(datacolumn):
    max_col = datacolumn.max()
    max_col = float(max_col)
    bin_len = max_col/3
    bins = [i*bin_len for i in range(3)]
    for i in datacolumn.index:
        if datacolumn.at[i, 'Error at Price'] < bins[0]:
            datacolumn.at[i, 'Error at Price'] =0
        elif datacolumn.at[i, 'Error at Price'] >= bins[0] and datacolumn.at[i, 'Error at Price'] < bins[1]:
            datacolumn.at[i, 'Error at Price'] =1
        elif datacolumn.at[i, 'Error at Price'] >= bins[1] and datacolumn.at[i, 'Error at Price'] < bins[2]:
            datacolumn.at[i, 'Error at Price'] =2
        elif datacolumn.at[i, 'Error at Price'] >= bins[2]:
            datacolumn.at[i, 'Error at Price'] =3

    return datacolumn

def test_stationarity(ts_data, column='', signif=0.05, series=False):
    if series:
        adf_test = adfuller(ts_data, autolag='AIC')
    else:
        adf_test = adfuller(ts_data[column], autolag='AIC')
    p_value = adf_test[1]
    if p_value <= signif:
        test_result = "Stationary"
    else:
        test_result = "Non-Stationary"
    return test_result
"""Multivariate Time Series"""
dataset = pd.read_csv('./dataset/Features.csv')
tickers = dataset.name.unique()

count_error =0
for p_ticker in tqdm(tickers, desc= "Var model: ", total= len(tickers)):
    try: 
        ticker_feature = dataset.loc[dataset['name']==p_ticker].drop(columns='name')
        txdate = ticker_feature['TXDATE']
        ticker_feature.drop(columns='TXDATE', inplace=True)
        non_stationary_cols = [col for col in ticker_feature.columns \
                                if test_stationarity(ticker_feature, column=col) == 'Non-Stationary']

        # Bo sung phuong phap bien doi chuoi khong dung thanh dung
        def differencing(data, column, order):
            differenced_data = data[column].diff(order)
            differenced_data.fillna(differenced_data.mean(), inplace=True)
            return differenced_data
        for col in non_stationary_cols:
            ticker_feature[col] = differencing(ticker_feature, col, 1)

        # find selected_lag
        from statsmodels.tsa.api import VAR
        column_to_model = list(ticker_feature.columns)

        while(1):
            try:
                max_lag = 5 # tham so co the dieu chinh
                var_model = VAR(ticker_feature[column_to_model])
                # select the best lag order
                lag_results = var_model.select_order(max_lag)

                selected_lag = lag_results.aic # selected_lag = 13
                def find_anomalies(squared_errors):
                    threshold = np.mean(squared_errors) + np.std(squared_errors)
                    predictions = (squared_errors >= threshold).astype(int)
                    return predictions, threshold

                var = VAR(ticker_feature[column_to_model])
                var_fitresults = var.fit(selected_lag)
                # print(var_fitresults.summary())
                squared_errors = var_fitresults.resid.sum(axis=1)**2
                price_errors = pd.DataFrame(var_fitresults.resid['close'])
                price_errors.rename(columns={'close': 'Error at Price'}, inplace=True)
                # price_errors = binning(price_errors) lua chon co the giai thich binning
                
                predictions, threshold = find_anomalies(squared_errors) 

                data = pd.concat([ticker_feature[column_to_model].iloc[selected_lag:, :], txdate.iloc[selected_lag:],price_errors[selected_lag:] ], axis=1)
                data['Predictions'] = predictions.values

                print('\nLIST ABNORMAL DAYS OF TICKER:', p_ticker)
                print(data[['TXDATE', 'Error at Price']].loc[data['Predictions'] ==1])
                # print('Importance of Features to Price')
                corr = pd.DataFrame(ticker_feature[column_to_model].iloc[selected_lag:, :].corr(method='pearson')['close'])

                coef_dict = dict(zip(corr.index ,corr.values))
                coef_dict = dict(sorted(coef_dict.items(), key= lambda item: item[1], reverse=True)[1:13])
                column = coef_dict.keys()
                coef_dict = np.concatenate(tuple([i] for i in list(coef_dict.values())), axis=0).T

                fig, ax = plt.subplots()
                ax.set_xticks([i for i in range(len(column))])
                ax.set_xticklabels(column)
                im =ax.imshow(coef_dict, cmap='hot', interpolation='nearest')
                cbar = ax.figure.colorbar(im, ax=ax, )
                cbar.ax.set_ylabel('Importance of features', rotation=-90, va="bottom")
                plt.xticks(fontsize=8)
                plt.show()


                # danh sach cac ngay bat thuong cua 1 ma
                # thoi diem error > 0 (them 1 cot dau hieu)

                break
            except Exception as e:
                e = str(e)
                e_index = 0
                for i in range(len(e)):
                    if e[i] == '-':
                        e_index = i
                        break
                if e_index == 0 or e_index > 3:
                    print(e + ' at Ticker: ', p_ticker)
                    count_error = count_error+1
                    break
                e_column = int(e[:e_index])
                column_to_model.remove(column_to_model[e_column-1])
        # ticker_feature = ticker_feature.drop(columns=['BBM_14_2.0','BBU_14_2.0'])
        # print(set(ticker_feature.columns) - set(column_to_model))
    except Exception as e:
        count_error = count_error+1
        print(str(e) + ' at Ticker: ', p_ticker)
    break

# Luu lai ket qua moi cach xu ly
# 