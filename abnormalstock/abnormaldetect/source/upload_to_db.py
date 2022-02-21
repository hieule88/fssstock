from abnormaldetect.source.backend import *
# from backend import *
import pandas as pd
import cx_Oracle
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

def connect_data(): 
    dsn_tns = cx_Oracle.makedsn(BACKEND_IP_HOST_DB, BACKEND_PORT_DB, service_name=BACKEND_SERVICE_NAME_USE) # if needed, place an 'r' before any parameter in order to address special characters such as '\'.
    # need input user because ....
    conn = cx_Oracle.connect(user=r'RISK_USER', password=BACKEND_PASS_DB, dsn=dsn_tns) # if needed, place an 'r' before any parameter in order to address special characters such as '\'. For example, if your user name contains '\', you'll need to place 'r' before the user name: user=r'User Name'
    c = conn.cursor()
    #conn.commit()
    return c,conn

class Updator():
    def __init__(self, database, table):
        self.database = database
        self.table = table
        self.cur, self.conn= connect_data()
    def upload(self, data):
        pass

    def remove(self):
        pass
    
if __name__ == '__main__':
    cur, conn = connect_data()
    #insert hyperparams
    list_params = 'MACK'
    input_start_date='01/01/2019'
    input_end_date='01/01/2021'
    input_ticker = '%'
    tickers = Parser('SP_TA_GET_TICKER_RAWDATA', 'TICKERLIST', input_ticker, input_start_date, input_end_date).dataframe['TICKER']

    val = tickers.tolist()
    val.append('ALL')

    content = list_params
    en_content = 'DEF_PREPROCESSING'
    order = 1

    for i in range(len(val)):
        # SQL = "INSERT INTO ALLCODE2 (CDUSER, CDTYPE, CDNAME, CDVAL, CDCONTENT, EN_CDCONTENT, LSTODR) VALUES ('H','SP', 'MINTRADEDAY','60' , 'MINTRADEDAY', 'DEF_PREPROCESSING', 1)"
        sql_insert = "INSERT INTO ALLCODE2 (CDUSER, CDTYPE, CDNAME, CDVAL, CDCONTENT, EN_CDCONTENT, LSTODR) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', {}) "\
                    .format('H','SP',list_params ,val[i] , content, en_content, i+2)

        c0 = cur.execute(sql_insert)
    conn.commit()
    print('DONE')


