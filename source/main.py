import pandas as pd
import os
from pandas.core.algorithms import diff
from tqdm import tqdm
from model import VarModel
from features import PreProcessor, FeatureTicker
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mintradeday", type=int, default=60)
    parser.add_argument("--replacenan", type=str, default='mean')
    parser.add_argument("--maxlag", type=int, default=5)
    parser.add_argument("--difftype", type=str, default='mean')
    parser.add_argument("--dataset", type=str, default='popular')
    parser.add_argument("--TAparams", type=dict, default={'tolerance_fault': 14})

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = parse_args()
    min_days = args.mintradeday
    max_lag = args.maxlag 
    TA_params = args.TAparams
    diff_type = args.difftype
    replace_nan = args.replacenan
    max_params = max(TA_params.values())

    dataset = pd.DataFrame(pd.read_csv('./dataset/TradingHistory.csv'))
    dataset.drop(columns=['Unnamed: 0'], inplace=True)
    tickers = pd.DataFrame(pd.read_csv('./dataset/Ticker.csv')['TICKER'])
    var_model = VarModel(max_lag=max_lag, diff_type=diff_type)
    preprocessor = PreProcessor(max_params=max_params, replace_nan=replace_nan)

    for row in tqdm(tickers.iterrows(), desc= "Model Solving: ", total= len(tickers.index)):
    # Load ticker infor
        p_ticker = row[1]['TICKER']
        
        ticker_infor = dataset.loc[dataset['TICKER']==p_ticker]
        if len(ticker_infor.index) < min_days :
            continue
        ticker_infor = FeatureTicker(ticker_infor, name = p_ticker, hyperparams= TA_params)
        ticker_infor.popular.reset_index(inplace=True, drop=True)
        ticker_infor = ticker_infor.popular

        ticker_infor = preprocessor.preprocess(ticker_infor)

        ticker_infor['name'] = [p_ticker for i in range(len(ticker_infor.index))]

        count_error =0
        try: 
            var_model.process(ticker_infor, p_ticker)
            # ticker_feature = ticker_feature.drop(columns=['BBM_14_2.0','BBU_14_2.0'])
            # print(set(ticker_feature.columns) - set(column_to_model))
        except Exception as e:
            count_error = count_error+1
            print(str(e) + ' at Ticker: ', p_ticker)
        # break