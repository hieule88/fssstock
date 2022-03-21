from re import A
import copy

def connect_data(): 
    import cx_Oracle
    from abnormalstock import settings

    dsn_tns = cx_Oracle.makedsn(settings.BACKEND_IP_HOST_DB, settings.BACKEND_PORT_DB, service_name=settings.BACKEND_SERVICE_NAME_USE) # if needed, place an 'r' before any parameter in order to address special characters such as '\'.
    # need input user because ....
    conn = cx_Oracle.connect(user=r'RISK_USER', password=settings.BACKEND_PASS_DB, dsn=dsn_tns) # if needed, place an 'r' before any parameter in order to address special characters such as '\'. For example, if your user name contains '\', you'll need to place 'r' before the user name: user=r'User Name'
    c = conn.cursor()
    #conn.commit()
    return c,conn

## READ ALLCODE2
curss,con_obj = connect_data()
sql_query_var = "select CDNAME,CDVAL from ALLCODE2 WHERE CDUSER= 'A'"
curss.execute(sql_query_var)
data_var = curss.fetchall()

def Convert(tup, di):
    for a, b in tup:
        di.setdefault(a, []).append(b)
    return di
PARAMS = {}
PARAMS = Convert(data_var, PARAMS)
data_var_dict = copy.deepcopy(PARAMS)
for k in PARAMS.keys():
    PARAMS[k] = [(v , v) for i , v in enumerate(PARAMS[k])]

##

# TA:
ta_dict = {}

try:
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
except:
    pass

# PREPROCESS:
try:
    stat_test = data_var_dict['STATIONARITYTEST']
except:
    print('Cant find any {} in allcode2'.format('stat_test'))

try:
    diff_type = data_var_dict['DIFFTYPE']
except:
    print('Cant find any {} in allcode2'.format('diff_type'))
try:
    replacenan = data_var_dict['REPLACENAN']
except:
    print('Cant find any {} in allcode2'.format('replacenan'))
try:
    mintradeday = data_var_dict['MINTRADEDAY']
except:
    print('Cant find any {} in allcode2'.format('mintradeday'))

# MODEL:
try:
    method = data_var_dict['METHOD']
except:
    print('Cant find any {} in allcode2'.format('method'))
try:
    maxlag = data_var_dict['MAXLAG']
except:
    print('Cant find any {} in allcode2'.format('maxlag'))
try:
    feature_importance = data_var_dict['FEATUREIMPORTANCE']
except:
    print('Cant find any {} in allcode2'.format('feature_importance'))

# LABELLING:
try:
    fi_threshold = data_var_dict['FITHRESHOLD']
except:
    print('Cant find any {} in allcode2'.format('fi_threshold'))
try:
    topfeature = data_var_dict['TOPFEATURE']
except:
    print('Cant find any {} in allcode2'.format('topfeature'))
try:
    score_convert = data_var_dict['SCORECONVERT']
except:
    print('Cant find any {} in allcode2'.format('score_convert'))
try:
    score_threshold = data_var_dict['SCORETHRESHOLD']
except:
    print('Cant find any {} in allcode2'.format('score_threshold'))
try:
    abnorm_threshold = data_var_dict['ABNORMTHRESHOLD']
except:
    print('Cant find any {} in allcode2'.format('abnorm_threshold'))

var_predict='Predictions'




