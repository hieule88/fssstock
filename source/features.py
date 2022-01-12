import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
import pandas_ta as ta
from tqdm import tqdm
import os 
from scipy import interpolate

list_features = [
    'adi', 'obv', 'ema', 'sma', 'wma', 'mfi', 'cmf', 'rsi', 'cci', 'roc', 'atr', 
    'fibonacci', 'bollinger', 'wR', 'srsi', 'macd' 
]
default_dict = {
    i: 14 for i in list_features
}

class FeatureTicker():
    def __init__(self, tickerframe, name, hyperparams= {}):
        self.name = name
        tickerframe = tickerframe.sort_values(by=['TXDATE'], ascending=True)
        tkdate = tickerframe['TXDATE'] 
        tickerframe = tickerframe.drop(columns=['TICKER', 'TXDATE'])
        self.tickerframe = tickerframe
        self.close = self.tickerframe["close"]
        self.open = self.tickerframe["open"]
        self.low = self.tickerframe["low"]
        self.high = self.tickerframe["high"]
        self.volume = self.tickerframe["volume"]
        self.hyperparams = default_dict
        self.hyperparams.update(hyperparams)

        self.popular = pd.concat([self.countTA_popular(),tkdate], axis=1)

    def countTA_popular(self):
        TApopular = {}
        try:
            TApopular['adi'] = ta.ad(close=self.close, high=self.high, \
                                    low=self.low, volume=self.volume)

            TApopular['obv'] = ta.obv(close=self.close, volume=self.volume)

            TApopular['ema'] = ta.ema(close=self.close, length=self.hyperparams['ema'])

            TApopular['sma'] = ta.sma(close=self.close, length=self.hyperparams['sma'])
            
            TApopular['wma'] = ta.wma(close=self.close, length=self.hyperparams['wma'])
            
            TApopular['mfi'] = ta.mfi(open=self.open, high=self.high,\
                                    low=self.low, close=self.close, \
                                    volume=self.volume, length=self.hyperparams['mfi'])
            
            TApopular['cmf'] = ta.cmf(open=self.open, high=self.high,\
                                    low=self.low, close=self.close,\
                                    volume=self.volume, length=self.hyperparams['cmf'])
            
            TApopular['rsi'] = ta.rsi(close=self.close, length=self.hyperparams['rsi'])
            
            TApopular['cci'] = ta.cci(close=self.close, high=self.high, \
                                    low=self.low, length=self.hyperparams['cci'])
            
            TApopular['roc'] = ta.roc(close=self.close, length=self.hyperparams['roc'])
            
            TApopular['atr'] = ta.atr(close=self.close, high=self.high, \
                                    low=self.low, length=self.hyperparams['atr'])
            
            TApopular['fibonacci'] = ta.fwma(close=self.close, length=self.hyperparams['fibonacci'])

            bollinger = ta.bbands(close=self.close, length=self.hyperparams['bollinger']) 
            for boll_index in bollinger.keys():
                TApopular[boll_index] = bollinger[boll_index] 
            # TApopular['bollinger_bandsL'] = bollinger['BBL_'+ str(self.hyperparams['bollinger']) +'_2.0']
            # TApopular['bollinger_bandsM'] = bollinger['BBM_'+ str(self.hyperparams['bollinger']) +'_2.0']
            # TApopular['bollinger_bandsU'] = bollinger['BBU_'+ str(self.hyperparams['bollinger']) +'_2.0']
            # TApopular['bollinger_bandsB'] = bollinger['BBB_'+ str(self.hyperparams['bollinger']) +'_2.0']
            # TApopular['bollinger_bandsP'] = bollinger['BBP_'+ str(self.hyperparams['bollinger']) +'_2.0']

            TApopular['wR'] = ta.willr(close=self.close, high=self.high, \
                                        low=self.low, length=self.hyperparams['wR'])
            
            srsi = ta.stochrsi(close=self.close, high=self.high, \
                                    low=self.low, length=self.hyperparams['srsi'])
            for srsi_index in srsi.keys():
                TApopular[srsi_index] = srsi[srsi_index] 

            so = ta.stoch(close=self.close, high=self.high, \
                                    low=self.low)                       
            for so_index in so.keys():
                TApopular[so_index] = so[so_index]

            macd = ta.macd(close=self.close, length=self.hyperparams['macd'])
            for macd_index in macd.keys():
                TApopular[macd_index] = macd[macd_index]
            
            psar = ta.psar(close=self.close, high=self.high, \
                                        low=self.low) 
            TApopular['psarl'] = psar['PSARl_0.02_0.2']
            TApopular['psars'] = psar['PSARs_0.02_0.2']
            TApopular['psaraf'] = psar['PSARaf_0.02_0.2']
            TApopular['psarr'] = psar['PSARr_0.02_0.2']

            ichimoku = ta.ichimoku(close=self.close, high=self.high, \
                                        low=self.low)[0]
            TApopular['ichimokuISA'] = ichimoku['ISA_9']
            TApopular['ichimokuISB'] = ichimoku['ISB_26']
            TApopular['ichimokuITS'] = ichimoku['ITS_9']
            TApopular['ichimokuIKS'] = ichimoku['IKS_26']
            TApopular['ichimokuICS'] = ichimoku['ICS_26']
            
            TApopular['price'] = self.close.div(self.close.max()) if (self.close.max() != 0) else self.close
            
            TApopular['vol'] = self.volume.div(self.volume.max()) if (self.volume.max() != 0) else self.volume

            # TApopular['bw_mfi'] = 0
            # TApopular['vrsi'] = 0
            # TApopular['mi'] = 0 
            TApopular = pd.concat([TApopular[key_index] for key_index in TApopular.keys()], axis=1)
        except Exception as e: 
            print('Found exception at Ticker: ',self.name)
            print(str(e))
            quit()
        return TApopular
    def countFA_popular(self):
        return {}
    def count_popular(self):
        popular = pd.concat([self.countTA_popular(), self.countFA_popular()], axis=1)
        return popular

    def count_volume(self):
        volume = self.popular
        return volume

    def count_volatility(self):
        volatility = self.popular
        return volatility

    def count_trend(self):
        trend = self.popular
        return trend

    def count_momentum(self):
        momentum = self.popular
        return momentum

    def count_addFA(self):
        addFA = self.popular
        return addFA

    def count_full(self):
        datafull = self.popular
        datafull.update(self.count_volatility())
        datafull.update(self.count_volume())
        datafull.update(self.count_trend())
        datafull.update(self.count_momentum())
        datafull.update(self.count_addFA())
        return datafull

    def to_dataframe(self, dict_data):
        return pd.DataFrame.from_dict(dict_data)

class PreProcessor():
    def __init__(self, max_params = 14, replace_nan = 'mean'):
        self.max_params = max_params
        self.replace_nan = replace_nan

    def preprocess(self, data: pd.DataFrame):
        data.drop(data.index[[i for i in range(-(self.max_params + 1),0)]], inplace= True)
        # add more fill nan 
        if self.replace_nan == 'mean':
            value = data.mean()
            data.fillna(value= value, inplace= True)
        elif self.replace_nan == 'interpolate':
            data.interpolate(method='linear', order=2, inplace=True)
        data.fillna(value= 0, inplace= True)
        return data

if __name__ =='__main__':
    dataset = pd.DataFrame(pd.read_csv('./dataset/TradingHistory.csv'))
    dataset.drop(columns=['Unnamed: 0'], inplace=True)
    tickers = pd.DataFrame(pd.read_csv('./dataset/Ticker.csv')['TICKER'])
    preprocessor = PreProcessor()

    for row in tqdm(tickers.iterrows(), desc= "Saving Ticker's Feature: ", total= len(tickers.index)):
    # Load ticker infor
        p_ticker = row[1]['TICKER']
        
        ticker_infor = dataset.loc[dataset['TICKER']==p_ticker]
        if len(ticker_infor.index) < 60 : # Bo sung tham so toi thieu ngay giao dich
            continue
        ticker_infor = FeatureTicker(ticker_infor, name = p_ticker)
        ticker_infor.popular.reset_index(inplace=True, drop=True)
        ticker_infor = ticker_infor.popular

        ticker_infor = preprocessor.preprocess(ticker_infor)

        ticker_infor['name'] = [p_ticker for i in range(len(ticker_infor.index))]
        # Save to csv
        filepath = './dataset/Features.csv'
        header = 1 - os.path.exists(filepath)
        ticker_infor.to_csv(filepath, mode='a', header=header, index=False)