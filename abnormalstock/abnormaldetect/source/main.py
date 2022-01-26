import pandas as pd
import os
from pandas.core.algorithms import diff
from tqdm import tqdm
from abnormaldetect.source.model import VarModel
from abnormaldetect.source.features import PreProcessor, FeatureTicker
import argparse

def RUNVARMODEL(ref, hyperparams):
    abnormdays = []
    dataversion = hyperparams['DataVersion']
    mintradeday = int(hyperparams['MinTradeDay'])
    replacenan = hyperparams['ReplaceNan']
    TA_params = {'tolerance_fault': 14}
    maxlag = int(hyperparams['MaxLag'])
    difftest = hyperparams['DiffTest']
    stationtest = hyperparams['StationarityTest']
    topfeature = int(hyperparams['TopFeature'])
    abnormthresh = float(hyperparams['AbnormThreshold'])
    fithresh = float(hyperparams['FIThreshold'])
    featureimportance = hyperparams['FeatureImpotance']
    scoreconvert = hyperparams['ScoreConvert']
    scorethresh = float(hyperparams['ScoreThreshold'])

    max_params = max(TA_params.values())
    dataset = pd.DataFrame(pd.read_csv('C:/work/FSS_stock/dataset/TradingHistory.csv'))
    dataset.drop(columns=['Unnamed: 0'], inplace=True)
    tickers = pd.DataFrame(pd.read_csv('C:/work/FSS_stock/dataset/Ticker.csv')['TICKER'])

    var_model = VarModel(maxlag, difftest, stationtest, featureimportance,\
                    topfeature, fithresh, scoreconvert, scorethresh)
    
    preprocessor = PreProcessor(max_params=max_params, replace_nan=replacenan)

    for row in tqdm(tickers.iterrows(), desc= "Model Solving: ", total= len(tickers.index)):
    # Load ticker infor
        p_ticker = row[1]['TICKER']
        
        ticker_infor = dataset.loc[dataset['TICKER']==p_ticker]
        if len(ticker_infor.index) < mintradeday :
            continue
        try:
            ticker_infor = FeatureTicker(ticker_infor, name = p_ticker, hyperparams= TA_params)
        except:
            continue
        
        
        ticker_infor.popular.reset_index(inplace=True, drop=True)
        ticker_infor = ticker_infor.popular

        ticker_infor = preprocessor.preprocess(ticker_infor)

        ticker_infor['name'] = [p_ticker for i in range(len(ticker_infor.index))]

        count_error =0
        try: 
            abnormpredict, top = var_model.process(ticker_infor, p_ticker)
            numabnormday = abnormpredict.size / 2
            if numabnormday > abnormthresh:
                abnormdays.append([numabnormday, p_ticker, abnormpredict['TXDATE'].tolist(), abnormpredict['Score'].tolist(), top.keys()])
            # ticker_feature = ticker_feature.drop(columns=['BBM_14_2.0','BBU_14_2.0'])
            # print(set(ticker_feature.columns) - set(column_to_model))
        except Exception as e:
            count_error = count_error+1
            print(str(e) + ' at Ticker: ', p_ticker)
        # break
    return abnormdays