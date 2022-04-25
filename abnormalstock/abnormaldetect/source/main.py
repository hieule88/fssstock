from cProfile import label
from io import StringIO
from itertools import count
from numpy import square
import pandas as pd
import os
from pandas.core.algorithms import diff
from tqdm import tqdm
from abnormaldetect.source.model import VarModel, FemModel, RemModel
from abnormaldetect.source.parser import Parser
from abnormaldetect.source.upload_to_db import connect_data
from abnormaldetect.source.features import PreProcessor, FeatureTicker
import argparse
import random
from datetime import datetime
import time
import io
import pickle
import matplotlib
import matplotlib.pyplot as plt 
matplotlib.use('Agg')
random.seed(int(time.time()))

def upload_image(data, typeof, taskid, ref_id, ver, p_ticker):
    try:          
        if typeof == 'sq_error':
            squared_errors = data[0]
            threshold = data[1]
            threshold = [threshold for i in range(len(squared_errors))]
            dates = data[2]
            plt.plot(dates, squared_errors, label = 'Squared Errors',)
            plt.plot(dates, threshold, '--', label = 'Threshold')
            plt.xlabel('Date')
            plt.ylabel('Error')
            plt.title('Error Chart')
        elif typeof == 'residual':
            real_close_cost = data[0]
            resid = data[1]
            dates = data[2]
            estimate_close_cost = [real_close_cost[i] + resid[i][0] for i in range(len(real_close_cost))]
            plt.plot(dates, real_close_cost, label = 'Real Close')
            plt.plot(dates, estimate_close_cost, label = 'Estimate Close')
            plt.xlabel('Date')
            plt.ylabel('Close')
            plt.title('Close Chart')
            
        plt.legend()
        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        buf = io.BytesIO()
        fig.savefig(buf, format='jpeg', dpi= 100)
        buf.seek(0)
        plt.close()
        plt.clf()
        cur, conn = connect_data()
        ref = ref_id.split('\\')[0]

        sql_insert = "INSERT INTO RES_VAR_IMG (REFVERSION, VERSION, ID_MODELLING, TYPE, IMAGE_VAL, MACK) \
                    VALUES (:1,:2,:3,:4,:5,:6) "
        cur.execute(sql_insert, [ref, ver, taskid, typeof, pickle.dumps(buf), p_ticker])
        conn.commit()
        print('UPLOAD IMAGE TO DB SUCCESS')
    except:
        print('UPLOAD IMAGE TO DB FAIL')
        raise
def upload_to_DB(data, typeof, taskid, ref_id , model, ver):
    try:
        cur, conn = connect_data()
        id = random.randint(1, 1000)
        ref, id_labelling, id_preprocessing = ref_id.split('\\')
        id_labelling = int(id_labelling)
        id_preprocessing = int(id_preprocessing)

        if typeof == 'predict':
            for i in range(len(data[2])):
                if data[3][i] > 0:
                    status = 'Y'
                else:
                    status = 'N'
                sql_insert = "INSERT INTO RES_PREDICT_FRAUD_2 (AUTOID, MACK, CDDATE, STATUS, RESIDUALS, SCORE, VERSION, REFVERSION, ID_MODELLING, ID_LABELLING, ID_PREPROCESSING) \
                                                                VALUES ({}, '{}', '{}', '{}', {}, {}, '{}', '{}', {}, {}, {}) "\
                                                                .format(id,data[1],data[2][i] , status , data[3][i], data[4][i], ver, ref, taskid, id_labelling, id_preprocessing)
                cur.execute(sql_insert)

        elif typeof == 'feature':
            day = datetime.now().strftime("%D")
            for i in range(len(data[1])):
                sql_insert = "INSERT INTO RES_VARIABLE_SCORE_2 (AUTOID, MACK, CDDATE, VARIABLE, SCORE, VERSION, REFVERSION, ID_MODELLING, ID_LABELLING, ID_PREPROCESSING) \
                                                                VALUES ({}, '{}', '{}', '{}', {}, '{}', '{}', {}, {}, {}) "\
                                                                .format(id, data[0], day, data[1][i], float(data[2][i]), ver, ref, taskid, id_labelling, id_preprocessing)
                cur.execute(sql_insert)
        conn.commit()
    except:
        raise

def RUNALLMODEL(taskid, ref_id, hyperparams):
    abnormdays = []
    dataversion = hyperparams['DatasetType']
    mintradeday = int(hyperparams['MinTradeDay'])
    replacenan = hyperparams['ReplaceNan']
    TA_params = {'tolerance_fault': 14}
    difftest = hyperparams['DiffTest']
    stationtest = hyperparams['StationarityTest']
    topfeature = int(hyperparams['TopFeature'])
    abnormthresh = float(hyperparams['AbnormThreshold'])
    fithresh = float(hyperparams['FIThreshold'])
    featureimportance = hyperparams['FeatureImpotance']
    scoreconvert = hyperparams['ScoreConvert']
    scorethresh = float(hyperparams['ScoreThreshold'])
    method = hyperparams['Method']

    max_params = max(TA_params.values())
    input_start_date=hyperparams['FromDate']
    input_end_date=hyperparams['ToDate']
    input_ticker = hyperparams['MaCK']

    if input_ticker == 'ALL':
        input_ticker = '%'
    parser = Parser('SP_TA_GET_TICKER_RAWDATA', 'TVHISTORY1D', input_ticker, input_start_date, input_end_date)
    dataset = parser.dataframe

    tickers = Parser('SP_TA_GET_TICKER_RAWDATA', 'TICKERLIST', input_ticker, input_start_date, input_end_date).dataframe
    preprocessor = PreProcessor(max_params=max_params, replace_nan=replacenan)
    ver = datetime.now().strftime("%D:%H:%M:%S") + '-' + str(time.time())
    ref = ref_id.split('\\')[0]
    cursor, con = connect_data()
    count_error =0

    # VAR MODEL PROCESS
    if method == 'var':
        print('RUNNING VAR MODEL')
        maxlag = int(hyperparams['MaxLag'])
        var_model = VarModel(maxlag, difftest, stationtest, featureimportance,\
                            topfeature, fithresh, scoreconvert, scorethresh)

        success =0

        for row in tqdm(reversed(list(tickers.iterrows())), desc= "Model Solving: ", total= len(tickers.index)):
        # Load ticker infor
            try:
                p_ticker = row[1]['TICKER']
                ticker_infor = dataset.loc[dataset['TICKER']==p_ticker]
                if len(ticker_infor.index) < mintradeday :
                    raise Exception('Number of trading days is smaller than MinTradeDay')

                ticker_infor = FeatureTicker(ticker_infor, name = p_ticker, hyperparams= TA_params)       
            
                ticker_infor.popular.reset_index(inplace=True, drop=True)
                ticker_infor = ticker_infor.popular

                ticker_infor = preprocessor.preprocess(ticker_infor)

                ticker_infor['name'] = [p_ticker for i in range(len(ticker_infor.index))]

                abnormpredict, top, squared_errors, threshold, tx_date, real_close_cost, resid = var_model.process(ticker_infor, p_ticker, )
                numabnormday = abnormpredict.size / 2
                if numabnormday > abnormthresh:
                    listresult = [numabnormday, p_ticker, abnormpredict['TXDATE'].tolist(), abnormpredict['Residual'].tolist(), abnormpredict['Score'].tolist(), top.keys()]
                    abnormdays.append(listresult)

                    upload_image([squared_errors.tolist(), threshold, list(tx_date)], 'sq_error', taskid, ref_id, ver, p_ticker)
                    upload_image([real_close_cost.tolist(), resid, list(tx_date)], 'residual', taskid, ref_id, ver, p_ticker)
                    upload_to_DB(listresult, typeof= 'predict', taskid= taskid, ref_id= ref_id, model = 'VAR', ver= ver)
                    upload_to_DB([p_ticker, list(top.keys()), list(top.values())], typeof= 'feature', taskid= taskid, ref_id= ref_id, model = 'VAR', ver= ver)
                
                # ticker_feature = ticker_feature.drop(columns=['BBM_14_2.0','BBU_14_2.0'])
                # print(set(ticker_feature.columns) - set(column_to_model))
                    p_logontent = 'Success' + ' at Ticker: ' + p_ticker
                else:
                    p_logontent = 'Success but Numabnormday < Abnormthresh' + ' at Ticker: ' + p_ticker
                p_status = 'S'
                success = success+1
                # if success == 1:
                #     print('Successed !!!')
                #     return 0

            except Exception as e:
                count_error = count_error+1
                print(str(e) + ' at Ticker: ', p_ticker)
                p_status = 'E'
                p_logontent = str(e) + ' at Ticker: ' + p_ticker

            sql_insert = "INSERT INTO RES_LOG_CELERY(ID_MODELLING, REFVERSION, VERSION, STATUS, LOGCONTENT) \
                            VALUES (:1,:2,:3,:4,:5)"
            cursor.execute(sql_insert,[taskid, ref, ver, p_status, p_logontent])
            con.commit()
            # if count_error == 10:
            #     print('Failed !!!')
            #     return 0
            # break
        return abnormdays
    
    # FEM MODEL PROCESS
    elif method == 'fem':
        print('RUNNING FEM MODEL')
        entity_effects = int(hyperparams['EntityEffects'])
        time_effects = int(hyperparams['TimeEffects'])
        other_effects = int(hyperparams['OtherEffects'])
        use_lsdv = int(hyperparams['UseLsdv'])
        use_lsmr = int(hyperparams['UseLsmr'])
        
        low_memory = int(hyperparams['LowMemory'])
        if low_memory == -1:
            low_memory = None

        cov_type = hyperparams['CovType']
        level = hyperparams['Level']
        has_constant = hyperparams['HasConstant']

        fem_model = FemModel(low_memory=low_memory, cov_type=cov_type, level=level, \
                            entity_effects=entity_effects, time_effects=time_effects, \
                            use_lsdv=use_lsdv, use_lsmr=use_lsmr, \
                            difftest=difftest, stationtest=stationtest, featureimportance=featureimportance,\
                            topfeature=topfeature, fithresh=fithresh, scoreconvert=scoreconvert, scorethresh=scorethresh)
        success = 0
        
        # PREPROCESSING
        for row in tqdm(tickers.iterrows(), desc= "PreProcessing Data: ", total= len(tickers.index)):       
            try:
                p_ticker = row[1]['TICKER']
                ticker_infor = dataset.loc[dataset['TICKER']==p_ticker]
                if len(ticker_infor.index) < mintradeday :
                    raise Exception('Number of trading days is smaller than MinTradeDay')

                ticker_infor = FeatureTicker(ticker_infor, name = p_ticker, hyperparams= TA_params)       
            
                ticker_infor.popular.reset_index(inplace=True, drop=True)
                ticker_infor = ticker_infor.popular

                ticker_infor = preprocessor.preprocess(ticker_infor)

                ticker_infor['name'] = [p_ticker for i in range(len(ticker_infor.index))]
                
                if success == 0:
                    data_all_tickers = pd.DataFrame(ticker_infor)
                else:
                    data_all_tickers = pd.concat([data_all_tickers, ticker_infor], axis = 0)
                success = success+1
                # if success == 10:
                #     print('Successed !!!')
                #     break
            except Exception as e:
                count_error = count_error+1
                print(str(e) + ' at Ticker: ', p_ticker)
                p_status = 'E'
                p_logontent = str(e) + ' at Ticker: ' + p_ticker

                sql_insert = "INSERT INTO RES_LOG_CELERY(ID_MODELLING, REFVERSION, VERSION, STATUS, LOGCONTENT) \
                            VALUES (:1,:2,:3,:4,:5)"
                cursor.execute(sql_insert,[taskid, ref, ver, p_status, p_logontent])
                con.commit()
        print('Done Preprocessing')
        try:
            abnormpredict, squared_errors, threshold, tx_date, real_close_cost, resid = fem_model.process(data_all_tickers)
        except Exception as e:
            p_status = 'Model Error'
            p_logontent = str(e)
            sql_insert = "INSERT INTO RES_LOG_CELERY(ID_MODELLING, REFVERSION, VERSION, STATUS, LOGCONTENT) \
                            VALUES (:1,:2,:3,:4,:5)"
            cursor.execute(sql_insert,[taskid, ref, ver, p_status, p_logontent])
            con.commit()
            return
        
        tickers_suc_pre = set(abnormpredict.index.get_level_values(0))
        
        # MODEL RUNNING
        for p_ticker in tqdm(tickers_suc_pre, desc= 'Model Solving: ', total = len(tickers_suc_pre)):
            try:
                numabnormday = 100
                listresult = [numabnormday, p_ticker, abnormpredict['TXDATE'].tolist(), abnormpredict['Residual'].tolist(), abnormpredict['Score'].tolist()]
                abnormdays.append(listresult)

                # upload_image([squared_errors.tolist(), threshold, list(tx_date)], 'sq_error', taskid, ref_id, ver, p_ticker)
                # upload_image([real_close_cost.tolist(), resid, list(tx_date)], 'residual', taskid, ref_id, ver, p_ticker)
                upload_to_DB(listresult, typeof= 'predict', taskid= taskid, ref_id= ref_id, model = 'FEM', ver= ver)
                # upload_to_DB([p_ticker, list(top.keys()), list(top.values())], typeof= 'feature', taskid= taskid, ref_id= ref_id, model = 'VAR', ver= ver)
                p_logontent = 'Success' + ' at Ticker: ' + p_ticker
            except Exception as e:
                count_error = count_error+1
                print(str(e) + ' at Ticker: ', p_ticker)
                p_status = 'E'
                p_logontent = str(e) + ' at Ticker: ' + p_ticker

            sql_insert = "INSERT INTO RES_LOG_CELERY(ID_MODELLING, REFVERSION, VERSION, STATUS, LOGCONTENT) \
                        VALUES (:1,:2,:3,:4,:5)"
            cursor.execute(sql_insert,[taskid, ref, ver, p_status, p_logontent])
            con.commit()
        print('DONE')
    # REM MODEL PROCESS
    elif method == 'rem':
        print('RUNNING REM MODEL')
        fem_model = RemModel(difftest, stationtest, featureimportance,\
                            topfeature, fithresh, scoreconvert, scorethresh)
        success = 0
        for row in tqdm(tickers.iterrows(), desc= "PreProcessing Data: ", total= len(tickers.index)):       
            try:
                p_ticker = row[1]['TICKER']
                ticker_infor = dataset.loc[dataset['TICKER']==p_ticker]
                if len(ticker_infor.index) < mintradeday :
                    raise Exception('Number of trading days is smaller than MinTradeDay')

                ticker_infor = FeatureTicker(ticker_infor, name = p_ticker, hyperparams= TA_params)       
            
                ticker_infor.popular.reset_index(inplace=True, drop=True)
                ticker_infor = ticker_infor.popular

                ticker_infor = preprocessor.preprocess(ticker_infor)

                ticker_infor['name'] = [p_ticker for i in range(len(ticker_infor.index))]
                
                if success == 0:
                    data_all_tickers = pd.DataFrame(ticker_infor)
                else:
                    data_all_tickers = pd.concat([data_all_tickers, ticker_infor], axis = 0)
                success = success+1
                # if success == 3:
                #     print('Successed !!!')
                #     break
            except Exception as e:
                count_error = count_error+1
                print(str(e) + ' at Ticker: ', p_ticker)
                p_status = 'E'
                p_logontent = str(e) + ' at Ticker: ' + p_ticker

                sql_insert = "INSERT INTO RES_LOG_CELERY(ID_MODELLING, REFVERSION, VERSION, STATUS, LOGCONTENT) \
                            VALUES (:1,:2,:3,:4,:5)"
                cursor.execute(sql_insert,[taskid, ref, ver, p_status, p_logontent])
                con.commit()
        abnormpredict, squared_errors, threshold, tx_date, real_close_cost, resid = fem_model.process(data_all_tickers)
        tickers_suc_pre = set(abnormpredict.index.get_level_values(0))
        for p_ticker in tqdm(tickers_suc_pre, desc= 'Model Solving: ', total = len(tickers_suc_pre)):
            try:
                numabnormday = 100
                listresult = [numabnormday, p_ticker, abnormpredict['TXDATE'].tolist(), abnormpredict['Residual'].tolist(), abnormpredict['Score'].tolist()]
                abnormdays.append(listresult)

            # upload_image([squared_errors.tolist(), threshold, list(tx_date)], 'sq_error', taskid, ref_id, ver, p_ticker)
            # upload_image([real_close_cost.tolist(), resid, list(tx_date)], 'residual', taskid, ref_id, ver, p_ticker)
                upload_to_DB(listresult, typeof= 'predict', taskid= taskid, ref_id= ref_id, model = 'FEM', ver= ver)
        # upload_to_DB([p_ticker, list(top.keys()), list(top.values())], typeof= 'feature', taskid= taskid, ref_id= ref_id, model = 'VAR', ver= ver)
                p_logontent = 'Success' + ' at Ticker: ' + p_ticker
            except Exception as e:
                count_error = count_error+1
                print(str(e) + ' at Ticker: ', p_ticker)
                p_status = 'E'
                p_logontent = str(e) + ' at Ticker: ' + p_ticker

            sql_insert = "INSERT INTO RES_LOG_CELERY(ID_MODELLING, REFVERSION, VERSION, STATUS, LOGCONTENT) \
                        VALUES (:1,:2,:3,:4,:5)"
            cursor.execute(sql_insert,[taskid, ref, ver, p_status, p_logontent])
            con.commit()
        print('DONE')