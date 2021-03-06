import cx_Oracle
import pandas as pd
# from backend import BACKEND_DB
from abnormaldetect.source.backend import BACKEND_DB

class Parser:
    def __init__(self, proc, table, p_ticker, p_start_date, p_end_date):
        self.table = table
        try:
            print('LOADING DATA FROM DATABASE')
            con = cx_Oracle.connect(BACKEND_DB)
            cursor = con.cursor()
            outcursor = cursor.var(cx_Oracle.CURSOR)
            cursor.callproc(proc, [table, p_ticker, p_start_date, p_end_date, outcursor])
            refCursor = outcursor.getvalue()
            col_names = []
            for col in refCursor.description:
                col_names.append(col[0])
            dfticker = pd.DataFrame.from_records(refCursor)
            dfticker.columns=col_names

            if table in ['TVHISTORY1D', 'TVHISTORY1M']: 
                dfticker.rename(columns={"O": "open", "H": "high", "L": "low", "C": "close", "V": "volume"}, inplace= True)
            self.dataframe = dfticker
            print('SUCCESSFUL LOAD FROM DATABASE')

        except Exception as e:
            print('UNSUCCESSFUL LOAD FROM DATABASE')
            print(str(e))
            quit()
            
    def get_ticker_infor(self, ticker):
        v_df_ohlcv = self.dataframe.loc[self.dataframe['TICKER'] == ticker]
        v_df_ohlcv = v_df_ohlcv.sort_values(by=['TXDATE'], ascending=True)
        # v_df_ohlcv = v_df_ohlcv.drop(columns=['TICKER', 'TXDATE'])
        return v_df_ohlcv

    def get_ticker_name(self):
        if self.table in ['TVHISTORY1D', 'TVHISTORY1M']:
            return pd.DataFrame(self.dataframe['TICKER'].unique())
        
        return self.dataframe

if __name__ == '__main__':
    p_start_date='01/01/2019'
    p_end_date='01/01/2021'
    p_ticker = 'FPT'
    parser = Parser('SP_TA_GET_TICKER_RAWDATA', 'TICKERLIST', p_ticker, p_start_date, p_end_date)
    # print(parser.dataframe)