def connect_data(): 
    import cx_Oracle
    from abnormalstock import settings

    dsn_tns = cx_Oracle.makedsn(settings.BACKEND_IP_HOST_DB, settings.BACKEND_PORT_DB, service_name=settings.BACKEND_SERVICE_NAME_USE) # if needed, place an 'r' before any parameter in order to address special characters such as '\'.
    # need input user because ....
    conn = cx_Oracle.connect(user=r'RISK_USER', password=settings.BACKEND_PASS_DB, dsn=dsn_tns) # if needed, place an 'r' before any parameter in order to address special characters such as '\'. For example, if your user name contains '\', you'll need to place 'r' before the user name: user=r'User Name'
    c = conn.cursor()
    #conn.commit()
    return c,conn
## READ ALLCODE
curss,con_obj = connect_data()
sql_query_var = 'select CDNAME,CDVAL from ALLCODE2 where CDUSER=:s'
curss.execute(sql_query_var,{"s":'H'})
data_var = curss.fetchall()
data_var_dict =dict(data_var)
##

# TA:
ta_dict = {}
ta_dict['ema'] = data_var_dict['TA_EMA']
ta_dict['sma'] = data_var_dict['TA_SMA']
ta_dict['wma'] = data_var_dict['TA_WMA']
ta_dict['mfi'] = data_var_dict['TA_MFI']
ta_dict['cmf'] = data_var_dict['TA_CMF']
ta_dict['rsi'] = data_var_dict['TA_RSI']
ta_dict['cci'] = data_var_dict['TA_CCI']
ta_dict['roc'] = data_var_dict['TA_ROC']
ta_dict['atr'] = data_var_dict['TA_ATR']
ta_dict['fibonacci'] = data_var_dict['TA_FIBONACCI']
ta_dict['bollinger'] = data_var_dict['TA_BOLLINGER']
ta_dict['wr'] = data_var_dict['TA_WR']
ta_dict['srsi'] = data_var_dict['TA_SRSI']
ta_dict['macd'] = data_var_dict['TA_MACD']

# PREPROCESS:
stat_test = data_var_dict['STATIONARITYTEST']
diff_type = data_var_dict['DIFFTYPE']
replacenan = data_var_dict['REPLACENAN']
mintradeday = data_var_dict['MINTRADEDAY']

# MODEL:
method = data_var_dict['METHOD']
maxlag = data_var_dict['MAXLAG']
feature_importance = data_var_dict['FEATUREIMPORTANCE']

# LABELLING:
fi_threshold = data_var_dict['FITHRESHOLD']
topfeature = data_var_dict['TOPFEATURE']
score_convert = data_var_dict['SCORECONVERT']
score_threshold = data_var_dict['SCORETHRESHOLD']
abnorm_threshold = data_var_dict['ABNORMTHRESHOLD']
var_predict='Predictions'


