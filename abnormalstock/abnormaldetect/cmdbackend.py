import io
import cx_Oracle, time
import pandas as pd
from sklearn import tree
from abnormalstock import settings
from abnormaldetect import tasks
import pickle
import base64
import matplotlib.pyplot as plt
from abnormaldetect.source.main import RUNALLMODEL
from abnormaldetect.source.upload_to_db import connect_data
from datetime import datetime
from abnormaldetect import admin

#User checking data
def func_modelid_variable(v_modelid):    
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        result = cursor.callfunc('GET_VARIABLE_MODEL_BY_MODELID',str, [v_modelid])
        return result
    except:
        # Re-raise the exception.
        raise  

def func_modelid_variableset(v_modelid):    
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        result = cursor.callfunc('GET_VARIABLE_SET_BY_MODELID',str, [v_modelid])
        return result
    except:
        # Re-raise the exception.
        raise  

#User checking data
def user_taxcode_inquiry(v_taxcode, v_typeofquery):    
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('USER_INQUIRY_TAXCODE', [v_taxcode, v_typeofquery, outcursor])
        results = outcursor.getvalue()
        return results
    except:
        # Re-raise the exception.
        raise  

#Get model information - queryset
def user_model_info(reflinkid, v_typeofquery):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('USER_MODEL_INFO', [reflinkid, v_typeofquery, outcursor])
        results = outcursor.getvalue()
        return results
    except:
        # Re-raise the exception.
        raise

#Get model information - dataframe
def user_model_info_df(reflinkid, v_typeofquery):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        refCursorVar = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('USER_MODEL_INFO', [reflinkid, v_typeofquery, refCursorVar])
        refCursor = refCursorVar.getvalue()
        col_names = []
        for col in refCursor.description:
            col_names.append(col[0])  
        df = pd.DataFrame.from_records(refCursor)
        df.columns=col_names
        return df
    except:
        # Re-raise the exception.
        raise



#Get AUTOID & TYPE of treemodel & supportvectormachine
def user_model_rule_info(modelid):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('USER_MODEL_INFO', [modelid, 'T', outcursor])
        refCursor = outcursor.getvalue()
        col_names = []
        for col in refCursor.description:
            col_names.append(col[0])  
        df = pd.DataFrame.from_records(refCursor)
        if len(df) != 0:
            df.columns = col_names        
            v_refid=df.at[0,'REFID']
            v_reftype=df.at[0,'REFTYPE']
            return GetModel2Show(str(v_refid), v_reftype)
        else:
            return ''
    except:
        # Re-raise the exception.
        raise        

#User checking data
def user_data_check(v_year, v_area):    
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('USER_DATA_CHECKING', [v_year, v_area, outcursor])
        results = outcursor.getvalue()
        return results
    except:
        # Re-raise the exception.
        raise   

#User checking data
def user_data_check_detail(v_year, v_area, v_ruleid):    
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('USER_DATA_CHECKING_DETAIL', [v_year, v_area, v_ruleid, outcursor])
        results = outcursor.getvalue()
        return results
    except:
        # Re-raise the exception.
        raise  

#User checking data
def user_kriset(v_kriset):    
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('USER_KRISET_DICT', [v_kriset, outcursor])
        results = outcursor.getvalue()
        return results
    except:
        # Re-raise the exception.
        raise

 #User prediction
def user_prediction(taskid, v_refversion, v_maxrows):    
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        sql_refversion = "SELECT REFVERSION FROM TASKLOG_V2 WHERE TASKID={}".format(v_refversion)
        cursor.execute(sql_refversion)
        ref = cursor.fetchall()[0][0]
        sql_idpreprocessing = "SELECT REFID FROM TASKLOG_V2 WHERE TASKID={}".format(v_refversion)
        cursor.execute(sql_idpreprocessing)
        id_preprocessing = cursor.fetchall()[0][0]
        ref_id = str(ref) + '/' + str(v_refversion) + '/' + str(id_preprocessing)

        sql_taskdata = "SELECT PARACONTENT FROM TASKLOG_V2 WHERE VERSION='{}'".format(ref)
        cursor.execute(sql_taskdata)
        taskdata = cursor.fetchall()[0][0]
        taskdata = taskdata.split(':')[1].split('-')

        sql_preprocessing = "SELECT PARACONTENT FROM TASKLOG_V2 WHERE TASKID={}".format(id_preprocessing)
        cursor.execute(sql_preprocessing)
        preprocessing = cursor.fetchall()[0][0]
        preprocessing = preprocessing.split(': ')[1].split('/')

        sql_labelling = "SELECT PARACONTENT FROM TASKLOG_V2 WHERE TASKID={}".format(v_refversion)
        cursor.execute(sql_labelling)
        labelling= cursor.fetchall()[0][0]
        labelling = labelling.split(': ')[1].split('/')



        hyperparams = {}
        hyperparams['StationarityTest'] = preprocessing[0].split('[')[1]
        hyperparams['DiffTest'] = preprocessing[1]
        hyperparams['ReplaceNan'] = preprocessing[2]
        hyperparams['MinTradeDay'] = preprocessing[3]
        hyperparams['Method'] = preprocessing[4]
        hyperparams['MaxLag'] = preprocessing[5]
        hyperparams['FeatureImpotance']  = preprocessing[6].split(']')[0]

        hyperparams['FIThreshold'] = labelling[0].split('[')[1]
        hyperparams['TopFeature'] = labelling[1]
        hyperparams['ScoreConvert'] = labelling[2]
        hyperparams['ScoreThreshold'] = labelling[3]
        hyperparams['AbnormThreshold'] = labelling[4].split(']')[0]

        hyperparams['DatasetType'] = taskdata[0]
        hyperparams['MaCK'] = taskdata[1]
        hyperparams['FromDate'] = taskdata[2]
        hyperparams['ToDate'] = taskdata[3]

        return RUNALLMODEL(taskid, ref_id, hyperparams)
    except:
        # Re-raise the exception.
        raise        

#Get frauditem belong to the model
def user_predictversion(reflinkid):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('USER_PREDICT_VERSION', [reflinkid, outcursor])
        results = outcursor.getvalue()
        return results
    except:
        # Re-raise the exception.
        raise   

#Get riskprofile information
def user_riskprofile(masothue, cmdtype):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('USER_RISKPROFILE', [masothue, cmdtype, outcursor])
        results = outcursor.getvalue()
        return results
    except:
        # Re-raise the exception.
        raise   

#Get frauditem information
def user_frauditem(reflinkid):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('USER_FRAUDITEM', [reflinkid, outcursor])
        results = outcursor.getvalue()
        return results
    except:
        # Re-raise the exception.
        raise  

 #User generic inquiry
def user_inquiry(v_refversion, v_typeofinquiry, v_maxrows):    
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('USER_INQUIRY', [v_refversion, v_typeofinquiry, v_maxrows, outcursor])
        results = outcursor.getvalue()
        return results     
    except:
        # Re-raise the exception.
        raise        


def runtaskall(v_mastertaskid, v_rootversionid, v_refparacontent):
    try:
        #Mp_taskcd: AUTOMODELLING
        v_return = task_runall_parameters(v_mastertaskid, v_rootversionid, v_refparacontent)
        return v_return
    except:
        # Re-raise the exception.
        raise      

#Read image from database
def GetModel2Show(refid, reftype):
    try:
        v_reftype=reftype
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        #model decision tree/random forest sử dụng query
        if reftype=="T":
            v_cmdsql='select autoid, objecttree from res_decision_tree where autoid=:id'
        elif reftype=="R":
            v_cmdsql='select autoid, objectmodel from res_random_forest where autoid=:id'
        else:
            return ''
        #build model
        res_query=cursor.execute(v_cmdsql, id=refid)
        list_=[]
        for result in res_query.fetchall():
            list_.append(result)
        row=list_[0][1]
        imageBlob=row
        blob=imageBlob.read()
        object_model=pickle.loads(blob)
        #build model text and image
        arr_model=[]
        arr_model_text=[]
        arr_model_image=[]
        if v_reftype=="T":
            text_model=tree.export_text(object_model[0]['classifier'], feature_names=object_model[1])
            arr_model_text.append(text_model)
            fig = plt.figure(figsize=(25,20))
            _ = tree.plot_tree(object_model[0]['classifier'],
                    feature_names=object_model[1],
                    class_names=['nofraud','fraud'],
                    filled=True)
            model_filename=reftype + str(refid) +".png"
            model_filename='sonar_tree.png'
            fig.savefig(model_filename)
            with open(model_filename, "rb") as imageFile:
                image_data = base64.b64encode(imageFile.read()).decode()
            arr_model_image.append(image_data)
            model_item = [text_model, image_data]
            arr_model.append(model_item)
        else:
            n_estimator=6
            for i in range(n_estimator):
                text_model = tree.export_text(object_model[0]['classifier'].estimators_[i], feature_names=object_model[1])
                arr_model_text.append(text_model)
                fig = plt.figure(figsize=(25,20))
                _ = tree.plot_tree(object_model[0]['classifier'].estimators_[i],
                        feature_names=object_model[1],
                        class_names=['nofraud','fraud'],
                        filled=True)
                model_filename=reftype + str(refid) + '-' + str(i) +".png"
                model_filename='sonar_tree.png'
                fig.savefig(model_filename)
                with open(model_filename, "rb") as imageFile:
                    image_data = base64.b64encode(imageFile.read()).decode()
                arr_model_image.append(image_data)
                model_item = [text_model, image_data]
                arr_model.append(model_item)
        return arr_model
    except:
        # Re-raise the exception.
        raise        

#Get data for export
def Cursor2DataFrame(refCursor):
    try:
        col_names = []
        for col in refCursor.description:
            col_names.append(col[0])  
        df = pd.DataFrame.from_records(refCursor)
        df.columns=col_names
        return df
    except:
        # Re-raise the exception.
        raise        

#Get data for the chart
def GetChartData(typeofquery, params):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        refCursorVar = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('GET_DATASET_CHART', [typeofquery, params, refCursorVar])
        refCursor = refCursorVar.getvalue()
        col_names = []
        for col in refCursor.description:
            col_names.append(col[0])  
        df = pd.DataFrame.from_records(refCursor)
        df.columns=col_names
        return df
    except:
        # Re-raise the exception.
        raise        

#Execute ETL
def task_ETL_execute(Category, Year):
    try:
        #Implement asynchronous
        #results = tasks.runETL(Category, Year) 
        results = runETL(Category, Year) 
        return results
    except:
        # Re-raise the exception.
        raise        

def runETL(Category, Year):
    try:
        results=''
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('SP_ETL_CHITIEU', [Category, Year, outcursor])
        con.commit()
        results = outcursor.getvalue()
        return results
    except:
        # Re-raise the exception.
        raise        


###

#Execute command
def task_command_exec_main(cmdtype, cmdcontent):
    try:
        results =''
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        if cmdtype=="R":
            #Read
            sqlcommand = cmdcontent
            cursor.execute(sqlcommand)
            results = cursor.fetchall()
        else:
            #Write
            sqlcommand = cmdcontent
            cursor.execute(sqlcommand)
            con.commit()
        return results
    except:
        # Re-raise the exception.
        raise        

#Execute command_typ
import abnormaldetect.tasks
def task_command_exec(cmdtype, cmdcontent):
    try:
        if cmdtype=="W":
            tasks.taskcmdcelery.apply_async(args=[cmdtype,cmdcontent])
        else:
            return task_command_exec_main(cmdtype, cmdcontent)            
    except:
        # Re-raise the exception.
        raise        

#Get colums collection (Meta data)
def task_command_meta(cmdtype, cmdcontent):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        results = ''
        if cmdtype=="R":
            #Read
            sqlcommand = cmdcontent
            cursor.execute(sqlcommand)
            col_names = []
            for i in range(0, len(cursor.description)):
                col_names.append(cursor.description[i][0])        
            results = col_names
        return results
    except:
        # Re-raise the exception.
        raise        

#Get reconcile information
def get_reconcile_result(reflinkid):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('GET_RECONCILE_RESULT', [reflinkid, outcursor])
        results = outcursor.getvalue()
        return results
    except:
        # Re-raise the exception.
        raise

#Get predictversion information
def get_predictversion(reflinkid):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('GET_PREDICT_VERSION', [reflinkid, outcursor])
        results = outcursor.getvalue()
        return results
    except:
        # Re-raise the exception.
        raise        

#Get risk profile
def get_riskprofile(masothue, cmdtype):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('GET_RISKPROFILE', [masothue, cmdtype, outcursor])
        results = outcursor.getvalue()
        return results
    except:
        # Re-raise the exception.
        raise   

#Get frauditem information
def get_frauditem(reflinkid):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('GET_FRAUDITEM', [reflinkid, outcursor])
        results = outcursor.getvalue()
        return results
    except:
        # Re-raise the exception.
        raise        

#Get frauditem information
def get_frauditem_info(masothue, cmdtype):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('GET_FRAUDITEM_INFO', [masothue, cmdtype, outcursor])
        results = outcursor.getvalue()
        return results
    except:
        # Re-raise the exception.
        raise        

#Setup parameter (ADD/DEL)
def task_para_setup(paraname, paraval, yesnotag, actiontag):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        ret_count = cursor.var(int)
        cursor.callproc('SP_ENGINE_PARASETUP', [paraname,paraval,yesnotag,actiontag,ret_count])
        con.commit()
        return ret_count
    except:
        # Re-raise the exception.
        raise        

#Submit Data for the Task
def task_data_submit(p_datatype, p_mack, p_fromdate, p_todate):
    try:
        strt_time = time.ctime()
        ref = datetime.now().strftime("%D:%H:%M:%S") + '-' + str(time.time())
        p_paracontent = 'DATAVERSION-MACK-FROMDATE-TODATE:{}-{}-{}-{}'.format(p_datatype, p_mack, p_fromdate, p_todate)
        cursor, con = connect_data()

        ret_count = cursor.var(int)
        sql_findver = "SELECT MAX(TASKID) FROM TASKLOG_V2"
        cursor.execute(sql_findver)
        max_index = cursor.fetchall()[0][0]
        if max_index == None:
            max_index = -1
        sql_insert = "INSERT INTO TASKLOG_V2 (TASKCD, TASKID, REFID, VERSION, REFVERSION, TASKINIT, TASKSTART, PARACONTENT) \
                        VALUES ('{}', {}, {}, '{}', '{}', '{}', '{}', '{}')"\
                        .format('TASKDATA', max_index+1, 0, ref, ref, strt_time, strt_time, p_paracontent)
        # sql_insert = "INSERT INTO TASKLOG_V2 (TASKCD, TASKID, REFID, VERSION, REFVERSION, TASKINIT, TASKSTART, TASKEND, STATUS, SCHEDULECD, PARACONTENT, LOGCONTENT, CRONJOBID) \
        #                 VALUES ('{}', {}, {}, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"\
        #                 .format('TASKDATA', max_index+1, 0, ref, ref, strt_time, strt_time, 'null', 'null', 'null', p_paracontent, 'null', 'null')
        cursor.execute(sql_insert)                                     
        con.commit()

        return ret_count
    except:
        # Re-raise the exception.
        raise        

def get_result_model(taskid):
    cursor, conn = connect_data()
    # sql_mack = "SELECT DISTINCT MACK FROM RES_PREDICT_FRAUD_2 WHERE ID_MODELLING={}".format(taskid)
    # cursor.execute(sql_mack)
    # mack = cursor.fetchall()[0]

    results = []

    sql_querry_preprocess = "SELECT DISTINCT ID_PREPROCESSING FROM RES_PREDICT_FRAUD_2 WHERE ID_MODELLING={}".format(taskid)
    cursor.execute(sql_querry_preprocess)
    id_preprocess = cursor.fetchall()[0][0]

    sql_query_pram = "SELECT PARACONTENT FROM TASKLOG_V2 WHERE TASKID={}".format(id_preprocess)
    cursor.execute(sql_query_pram)
    param_preprocess = cursor.fetchall()[0][0]

    # GET METHOD NAME
    title_params = param_preprocess.split(': ')[0].split('/')
    model = 0
    for tit in range(len(title_params)):
        if title_params[tit] == 'METHOD':
            model = tit
    method = param_preprocess.split(': ')[1].split('/')[model].upper()

    sql_res_predict = "SELECT MACK, CDDATE, STATUS, RESIDUALS, SCORE, '{}' FROM RES_PREDICT_FRAUD_2 WHERE ID_MODELLING={}".format(method, taskid)
    cursor.execute(sql_res_predict)
    data_predict = cursor.fetchall()

    results.append(data_predict)
    
    sql_res_impfeatures = 'SELECT MACK, VARIABLE, SCORE FROM RES_VARIABLE_SCORE_2 WHERE ID_MODELLING ={}'.format(taskid)
    cursor.execute(sql_res_impfeatures)
    data_impfeatures = cursor.fetchall()
    results.append(data_impfeatures)

    return results

def init_taskid():
    cursor, con = connect_data()
    sql_findver = "SELECT MAX(TASKID) FROM TASKLOG_V2"
    cursor.execute(sql_findver)
    max_index = cursor.fetchall()[0][0]
    return max_index+1
    
def assign_param(p_taskcd, p_taskid, p_reftaskid, ver, ref, strt_time, hyperparams, hyperparams_tomodel,keys, num_params, index_param):
    if index_param == num_params:
        cursor, con = connect_data()
        p_paracontent_prep = "STATIONARITYTEST/DIFFTYPE/REPLACENAN/MINTRADEDAY/METHOD/MAXLAG/FEATUREIMPORTANCE: [{}/{}/{}/{}/{}/{}/{}]"\
                            .format(hyperparams_tomodel["StationarityTest"], hyperparams_tomodel["DiffTest"], \
                                    hyperparams_tomodel["ReplaceNan"], hyperparams_tomodel["MinTradeDay"],\
                                    hyperparams_tomodel["Method"], hyperparams_tomodel["MaxLag"], hyperparams_tomodel["FeatureImpotance"])
        prep_id = init_taskid()
        sql_insert_prep = "INSERT INTO TASKLOG_V2 (TASKCD, TASKID, REFID, VERSION, REFVERSION, TASKINIT, TASKSTART, PARACONTENT) VALUES \
                                    ('{}', {}, {}, '{}', '{}', '{}', '{}', '{}') "\
                                    .format("PREPROCESSING", prep_id, p_reftaskid, ver, ref, strt_time, strt_time, p_paracontent_prep)
        cursor.execute(sql_insert_prep)
        con.commit()

        p_paracontent_label = "FITHRESHOLD/TOPFEATURE/SCORECONVERT/SCORETHRESHOLD/ABNORMTHRESHOLD: [{}/{}/{}/{}/{}]"\
                            .format(hyperparams_tomodel["FIThreshold"], hyperparams_tomodel["TopFeature"], \
                                    hyperparams_tomodel["ScoreConvert"], hyperparams_tomodel["ScoreThreshold"], hyperparams_tomodel["AbnormThreshold"])
        label_id = init_taskid()
        sql_insert_label = "INSERT INTO TASKLOG_V2 (TASKCD, TASKID, REFID, VERSION, REFVERSION, TASKINIT, TASKSTART, PARACONTENT) VALUES \
                                    ('{}', {}, {}, '{}', '{}', '{}', '{}', '{}') "\
                                    .format("LABELLING", label_id, prep_id, ver, ref, strt_time, strt_time, p_paracontent_label)
        cursor.execute(sql_insert_label)
        con.commit()

        p_paracontent_auto = "PREPROCESSINGID/LABELLINGID/MASTERID:{}/{}/{}".format(prep_id, label_id, p_taskid)
        sql_insert_auto = "INSERT INTO TASKLOG_V2 (TASKCD, TASKID, REFID, VERSION, REFVERSION, TASKINIT, TASKSTART, PARACONTENT) VALUES \
                                    ('{}', {}, {}, '{}', '{}', '{}', '{}', '{}') "\
                                    .format(p_taskcd, label_id, p_reftaskid, ver, ref, strt_time, strt_time, p_paracontent_auto)
        con.commit()
        ref_id = ref + '\\' + str(label_id) + '\\' + str(prep_id)

        tasks.runtask.apply_async(args=[p_taskid, ref_id, hyperparams_tomodel])
        cursor.execute(sql_insert_auto)

    else:
        for i in range(len(hyperparams[keys[index_param]])):
            hyperparams_tomodel[keys[index_param]] = hyperparams[keys[index_param]][i]
            assign_param(p_taskcd, p_taskid, p_reftaskid, ver, ref, strt_time, hyperparams, hyperparams_tomodel, keys, num_params, index_param + 1)

def autorun(p_taskid, p_taskcd, p_reftaskid, ver, strt_time):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()

        sql_refversion = "SELECT REFVERSION FROM TASKLOG_V2 WHERE TASKID={}".format(p_reftaskid)
        cursor.execute(sql_refversion)
        ref = cursor.fetchall()[0][0]

        sql_taskdata = "SELECT PARACONTENT FROM TASKLOG_V2 WHERE VERSION='{}'".format(ref)
        cursor.execute(sql_taskdata)
        taskdata = cursor.fetchall()[0][0]

        taskdata = taskdata.split(':')[1].split('-')

        hyperparams = {}
        hyperparams['StationarityTest'] = admin.stat_test
        hyperparams['DiffTest'] = admin.diff_type
        hyperparams['ReplaceNan'] = admin.replacenan
        hyperparams['MinTradeDay'] = admin.mintradeday
        hyperparams['Method'] = admin.method
        hyperparams['MaxLag'] = admin.maxlag
        hyperparams['FeatureImpotance']  = admin.feature_importance

        hyperparams['FIThreshold'] = admin.fi_threshold
        hyperparams['TopFeature'] = admin.topfeature
        hyperparams['ScoreConvert'] = admin.score_convert
        hyperparams['ScoreThreshold'] = admin.score_threshold
        hyperparams['AbnormThreshold'] = admin.abnorm_threshold

        hyperparams_tomodel = {}
        hyperparams_tomodel['DatasetType'] = taskdata[0]
        hyperparams_tomodel['MaCK'] = taskdata[1]
        hyperparams_tomodel['FromDate'] = taskdata[2]
        hyperparams_tomodel['ToDate'] = taskdata[3]

        keys = hyperparams.keys()
        num_params = len(keys)

        assign_param(p_taskcd, p_taskid, p_reftaskid, ver, ref, strt_time, hyperparams, hyperparams_tomodel, list(keys), num_params, 0)

    except:
        raise

def task_pipeline_submit(p_taskcd, p_reftaskid, p_paracontent, p_exttaskid, p_extversion):
    try:
        strt_time = time.ctime()
        ver = datetime.now().strftime("%D:%H:%M:%S") + '-' + str(time.time())
        cur, conn = connect_data()
        
        results = []
        if p_taskcd == 'AUTOMODELLING':
            p_taskid = init_taskid()
            autorun(p_taskid, p_taskcd, p_reftaskid, ver, strt_time)
            results = get_result_model(p_taskid)

        elif p_taskcd == 'MODELLING': 
            sql_findref = "SELECT REFVERSION FROM TASKLOG_V2 WHERE TASKID={}".format(p_reftaskid)
            cur.execute(sql_findref)
            ref_data = cur.fetchall()[0][0]
            task_id = init_taskid()
            p_paracontent = p_paracontent + str(task_id)
            sql_insert = "INSERT INTO TASKLOG_V2 (TASKCD, TASKID, REFID, VERSION, REFVERSION, TASKINIT, TASKSTART, PARACONTENT) VALUES \
                                    ('{}', {}, {}, '{}', '{}', '{}', '{}', '{}') "\
                                    .format(p_taskcd, task_id, p_reftaskid, ver, ref_data, strt_time, strt_time, p_paracontent)
            cur.execute(sql_insert)
            conn.commit()

            sql_refversion = "SELECT REFVERSION FROM TASKLOG_V2 WHERE TASKID={}".format(p_reftaskid)
            cur.execute(sql_refversion)
            ref = cur.fetchall()[0][0]         
            id_preprocessing = p_paracontent.split(':')[1].split('/')[0]

            ref_id = str(ref) + '\\' + str(p_reftaskid) + '\\' + str(id_preprocessing)
            
            sql_taskdata = "SELECT PARACONTENT FROM TASKLOG_V2 WHERE VERSION='{}'".format(ref)
            cur.execute(sql_taskdata)
            taskdata = cur.fetchall()[0][0]
            taskdata = taskdata.split(':')[1].split('-')

            sql_preprocessing = "SELECT PARACONTENT FROM TASKLOG_V2 WHERE TASKID={}".format(id_preprocessing)
            cur.execute(sql_preprocessing)
            preprocessing = cur.fetchall()[0][0]
            preprocessing = preprocessing.split(': ')[1].split('/')

            sql_labelling = "SELECT PARACONTENT FROM TASKLOG_V2 WHERE TASKID={}".format(p_reftaskid)
            cur.execute(sql_labelling)
            labelling= cur.fetchall()[0][0]
            labelling = labelling.split(': ')[1].split('/')

            hyperparams = {}
            hyperparams['StationarityTest'] = preprocessing[0].split('[')[1]
            hyperparams['DiffTest'] = preprocessing[1]
            hyperparams['ReplaceNan'] = preprocessing[2]
            hyperparams['MinTradeDay'] = preprocessing[3]
            hyperparams['Method'] = preprocessing[4]
            hyperparams['MaxLag'] = preprocessing[5]
            hyperparams['FeatureImpotance']  = preprocessing[6]

            hyperparams['EntityEffects']  = preprocessing[7]
            hyperparams['TimeEffects']  = preprocessing[8]
            hyperparams['OtherEffects']  = preprocessing[9]
            hyperparams['UseLsdv']  = preprocessing[10]
            hyperparams['UseLsmr']  = preprocessing[11]
            hyperparams['LowMemory']  = preprocessing[12]
            hyperparams['CovType']  = preprocessing[13]
            hyperparams['Level']  = preprocessing[14]
            hyperparams['HasConstant']  = preprocessing[15].split(']')[0]

            hyperparams['FIThreshold'] = labelling[0].split('[')[1]
            hyperparams['TopFeature'] = labelling[1]
            hyperparams['ScoreConvert'] = labelling[2]
            hyperparams['ScoreThreshold'] = labelling[3]
            hyperparams['AbnormThreshold'] = labelling[4].split(']')[0]

            hyperparams['DatasetType'] = taskdata[0]
            hyperparams['MaCK'] = taskdata[1]
            hyperparams['FromDate'] = taskdata[2]
            hyperparams['ToDate'] = taskdata[3]

            celery_results = tasks.runtask.apply_async(args=[task_id, ref_id, hyperparams])
            while not celery_results.ready():
                pass
            results = get_result_model(task_id)

        else:
            sql_findref = "SELECT REFVERSION FROM TASKLOG_V2 WHERE TASKID={}".format(p_reftaskid)
            cur.execute(sql_findref)
            ref_data = cur.fetchall()[0][0]
            task_id = init_taskid()
            sql_insert = "INSERT INTO TASKLOG_V2 (TASKCD, TASKID, REFID, VERSION, REFVERSION, TASKINIT, TASKSTART, PARACONTENT) VALUES \
                                    ('{}', {}, {}, '{}', '{}', '{}', '{}', '{}') "\
                                    .format(p_taskcd, task_id, p_reftaskid, ver, ref_data, strt_time, strt_time, p_paracontent)
            cur.execute(sql_insert)
            conn.commit()
        return results
    except:
        # Re-raise the exception.
        raise        

# SOME SUPPORT FUNCTIONS FOR TOP ABNORMAL
def get_important_features(pticker, pid):
    cursor, conn = connect_data()
    sql_find_if = "SELECT VARIABLE FROM RES_VARIABLE_SCORE_2 WHERE MACK = '{}' AND ID_MODELLING = {}"\
                    .format(pticker, pid)
    cursor.execute(sql_find_if)
    imp_feat = [ind[0] for ind in cursor.fetchall()]
    return str(imp_feat)

def insert_top_abnormal(type_of, cursor, conn, taskid, data, bonus_data):
    try:
        print(data)
        print(bonus_data)
        if type_of == 'CUR':
            sql_insert_prep = "INSERT INTO RES_TOP_ABNORM (TASKID, MACK, SCORE, ID_MODELLING, FEATURES, LASTDATE) VALUES \
                                        ({}, '{}', {}, {}, '{}', '{}') "\
                                        .format(taskid, data[0], data[1], data[2], data[3], data[4])
        elif type_of == 'NEW': 
            sql_insert_prep = "INSERT INTO RES_TOP_ABNORM (TASKID, MACK, SCORE, ID_MODELLING, FEATURES, LASTDATE) VALUES \
                                        ({}, '{}', {}, {}, '{}', '{}') "\
                                        .format(taskid, data[0], data[1], data[2], bonus_data[0], bonus_data[1])
        print('loi o day1')
        
        cursor.execute(sql_insert_prep)
        conn.commit()
        print('loi o day2')
    except Exception as e:
        print(e)
        print('INSERT TOP ABNORMAL FAIL')
# GET TOP ABNORMAL TO SHOW AT HOME 
def update_top_abnormal(top):
    try:
        cursor, conn = connect_data()
        # GET CURRENT TOP
        sql_get_new_id = "SELECT MAX(TASKID) FROM RES_TOP_ABNORM"
        cursor.execute(sql_get_new_id)
        max_index = cursor.fetchall()[0][0]
        new_taskid = max_index + 1 

        sql_get_top = "SELECT MACK, SCORE, ID_MODELLING, FEATURES, LASTDATE \
                        FROM RES_TOP_ABNORM WHERE TASKID ={} ORDER BY SCORE DESC".format(max_index)
        cursor.execute(sql_get_top)
        curr_top = cursor.fetchall()

        # GET TOP OF NEW MODEL
        sql_get_new_id = "SELECT MAX(ID_MODELLING) FROM RES_PREDICT_FRAUD_2"
        cursor.execute(sql_get_new_id)
        max_index = cursor.fetchall()[0][0]

        print('loi o day 12')
        sql_get_scores = "SELECT MACK, AVG(ABS(RESIDUALS)), ID_MODELLING FROM RES_PREDICT_FRAUD_2 \
                        WHERE ID_MODELLING={} GROUP BY MACK, ID_MODELLING \
                        ORDER BY AVG(ABS(RESIDUALS)) DESC FETCH FIRST {} ROWS ONLY".format(max_index, top*2)
        cursor.execute(sql_get_scores)
        new_model_top50 = cursor.fetchall()
        print('loi o day 4')
        # COMPARE TO GET NEW TOP
        # INSERT INTO RES_TOP_ABNORMAL
        new_top50_mack = []
        ind_curr = 0
        ind_newmodel = 0
        ind = 0
        cur_date = str(time.ctime())
        while(ind < top) :
            if ind_curr == len(curr_top):
                while(new_model_top50[ind_newmodel][0] in new_top50_mack):
                    ind_newmodel = ind_newmodel + 1
                imp_feat = get_important_features(new_model_top50[ind_newmodel][0], new_model_top50[ind_newmodel][2])
                insert_top_abnormal('NEW', cursor, conn, new_taskid, new_model_top50[ind_newmodel], [imp_feat, cur_date] )
                new_top50_mack.append(new_model_top50[ind_newmodel][0])
                ind = ind + 1
                continue
            elif ind_newmodel == len(new_model_top50):
                while(curr_top[ind_curr][0] in new_top50_mack):
                    ind_curr = ind_curr + 1
                insert_top_abnormal('CUR', cursor, conn, new_taskid, curr_top[ind_curr],'')
                new_top50_mack.append(curr_top[ind_curr][0])
                ind = ind + 1
                continue
            
            while(curr_top[ind_curr][0] in new_top50_mack):
                ind_curr = ind_curr + 1
            while(new_model_top50[ind_newmodel][0] in new_top50_mack):
                ind_newmodel = ind_newmodel + 1
            if ind_curr == len(curr_top) or ind_newmodel == len(new_model_top50):
                continue

            if curr_top[ind_curr][1] > new_model_top50[ind_newmodel][1]:
                insert_top_abnormal('CUR', cursor, conn, new_taskid, curr_top[ind_curr],'')
                new_top50_mack.append(curr_top[ind_curr][0])
                ind_curr = ind_curr + 1 
            else:
                imp_feat = get_important_features(new_model_top50[ind_newmodel][0], new_model_top50[ind_newmodel][2])
                insert_top_abnormal('NEW', cursor, conn, new_taskid, new_model_top50[ind_newmodel], [imp_feat, cur_date] )
                new_top50_mack.append(new_model_top50[ind_newmodel][0])
                ind_newmodel = ind_newmodel + 1 
            ind = ind + 1
        return 'UPDATE TOP ABNORMAL DONE'
    except Exception as e :
        print(e)
        print('UPDATE TOP ABNORMAL UNSUCCESFUL')

# SHOW WHEN HOME PAGE IS LOADED
def get_top_abnormal():
    try:
        cursor, conn = connect_data()
        # GET CURRENT TOP
        sql_get_new_id = "SELECT MAX(TASKID) FROM RES_TOP_ABNORM"
        cursor.execute(sql_get_new_id)
        max_index = cursor.fetchall()[0][0]

        sql_get_top = "SELECT ID_MODELLING, MACK, SCORE, FEATURES, LASTDATE \
                        FROM RES_TOP_ABNORM WHERE TASKID ={} ORDER BY SCORE DESC".format(max_index)
        cursor.execute(sql_get_top)
        curr_top = cursor.fetchall()

        list_mack = [0]
        for infor_mack in curr_top:
            list_mack.append(infor_mack[1])
        list_mack = list_mack[:16]
        list_score= [[infor_mack[2] for infor_mack in curr_top][:15]]

        fig, ax = plt.subplots()
        ax.set_xticklabels(list_mack)
        ax.set_yticklabels('')
        plt.locator_params(axis='x', nbins=15)
        plt.imshow(list_score, cmap='hot', interpolation='nearest')
        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        heatmap = io.BytesIO()
        fig.savefig(heatmap, format='jpeg', dpi= 100)
        heatmap.seek(0)
        plt.close()
        plt.clf()

        heatmap = base64.b64encode(heatmap.read()).decode('utf-8')

        return heatmap, curr_top
    except Exception as e:
        print(e)
        print('SHOW TOP ABNORMAL FAIL')
        return None, None

def trace_log_modelling(p_reftask):
    cur, conn = connect_data()
    sql_preprocess = "SELECT REFID FROM TASKLOG_V2 WHERE TASKID={}".format(p_reftask)
    cur.execute(sql_preprocess)
    ref_pre = cur.fetchall()[0][0]
    result = "PREPROCESSINGID/LABELLINGID/MASTERID:{}/{}/".format(ref_pre, p_reftask)
    return result

#Feedback task result
def task_result_feedback(p_taskid, p_status, p_logontent):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        ret_count = cursor.var(int)
        cursor.callproc('SP_ENGINE_UPDATE_TASK_RESULT', [p_taskid, p_status, p_logontent, ret_count])
        con.commit()
        return ret_count
    except:
        # Re-raise the exception.
        raise        

#Get dataset
def task_para_get(v_para_typ):
    try:
        # need_debug to get table of datasets
        ###################################
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()

        if v_para_typ != 'DASHBOARD':
            sql_query = "SELECT VERSION, PARACONTENT, TASKID, REFID, TASKSTART FROM TASKLOG_V2 WHERE TASKCD='{}'".format(v_para_typ)
            cursor.execute(sql_query)
            
            results = cursor.fetchall()
            if v_para_typ == 'TASKDATA':
                for res_ind in range(len(results)) :
                    ref, cont, _, __, ___ = results[res_ind]
                    cont = cont.split(':')[1].split('-')
                    cont.append(ref)
                    cont.append(res_ind+1)
                    results[res_ind] = cont
                return results
            elif v_para_typ == 'PREPROCESSING':
                pass
            elif v_para_typ == 'LABELLING':
                pass
            elif v_para_typ == 'MODELLING':
                pass
        # GET 
        else:
            taskids = task_get_distinct('RES_PREDICT_FRAUD_2','ID_MODELLING')
            outputs = []
            for taskid in taskids:
                try:
                    output = []
                    output.append(taskid)
                    
                    sql_query = "SELECT REFID FROM TASKLOG_V2 WHERE TASKID={}".format(taskid)
                    cursor.execute(sql_query)
                    id_labelling = cursor.fetchall()[0][0]
                    sql_query = "SELECT PARACONTENT FROM TASKLOG_V2 WHERE TASKID={}".format(taskid)
                    cursor.execute(sql_query)
                    model_param = cursor.fetchall()[0][0]

                    sql_query = "SELECT PARACONTENT FROM TASKLOG_V2 WHERE TASKID={}".format(id_labelling)
                    cursor.execute(sql_query)
                    label_param = cursor.fetchall()[0][0]


                    sql_query = "SELECT REFID FROM TASKLOG_V2 WHERE TASKID={}".format(id_labelling)
                    cursor.execute(sql_query)
                    id_preprocess = cursor.fetchall()[0][0]

                    sql_query = "SELECT PARACONTENT FROM TASKLOG_V2 WHERE TASKCD='PREPROCESSING' AND TASKID={}".format(id_preprocess)
                    cursor.execute(sql_query)
                    preprocess_param = cursor.fetchall()[0][0]

                    # GET MODEL
                    title_params = preprocess_param.split(': ')[0].split('/')
                    model = 0
                    for tit in range(len(title_params)):
                        if title_params[tit] == 'METHOD':
                            model = tit
                    model_name = preprocess_param.split(': ')[1].split('/')[model]
                    output.append(model_name.upper())

                    # GET PARAM
                    output.append('MODELLING: ' + model_param)
                    output.append('PREPROCESSING: ' + preprocess_param)
                    output.append('LABELLING: ' + label_param)

                    # GET NUM DETECTED
                    sql_query = "SELECT COUNT ( DISTINCT MACK ) FROM RES_PREDICT_FRAUD_2 WHERE ID_MODELLING='{}'".format(taskid)
                    cursor.execute(sql_query)
                    number_mack = cursor.fetchall()[0][0]
                    output.append(number_mack)

                    # GET DATASET
                    sql_query = "SELECT REFID FROM TASKLOG_V2 WHERE TASKID={}".format(id_preprocess)
                    cursor.execute(sql_query)
                    refversion = cursor.fetchall()[0][0]
                    sql_query = "SELECT PARACONTENT FROM TASKLOG_V2 WHERE TASKID={}".format(refversion)
                    cursor.execute(sql_query)
                    refdata = cursor.fetchall()[0][0]
                    output.append('DATASET: ' + refdata)
                    
                    outputs.append(output)
                except: 
                    continue
            return outputs
        ###################################
    except:
        # Re-raise the exception.
        raise        

#Get distinct value from table
def task_get_distinct(table, typeof):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        sql = "SELECT DISTINCT {} FROM {}".format(typeof, table)
        cursor.execute(sql)
        result_sql = cursor.fetchall()
        task_ids = [res[0] for res in result_sql]
        return task_ids
    except:
        raise

#Get chart result from res_var_img
def get_chart_result(taskid, mack):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        sql = "SELECT TYPE, IMAGE_VAL FROM RES_VAR_IMG WHERE ID_MODELLING = {} AND MACK = '{}'".format(taskid, mack)
        cursor.execute(sql)
        result_sql = cursor.fetchall()
        img_pair = []
        for res in result_sql:
            tmp_pair = []
            tmp_pair.append(res[0])
            buf_img = pickle.loads(res[1].read())
            buf_img = base64.b64encode(buf_img.read()).decode('utf-8')
            # buf_img = res[1].read()
            # buf_img = pickle.loads(buf_img)
            # buf_img = base64.b64encode(buf_img).decode('utf-8')
            tmp_pair.append(buf_img)
            img_pair.append(tmp_pair)
        return img_pair
    except: 
        raise

#Get log celery data
def get_log_celery(taskid):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        sql = "SELECT * FROM RES_LOG_CELERY WHERE ID_MODELLING ={}".format(taskid)
        cursor.execute(sql)
        log_data = cursor.fetchall()
        return log_data
    except:
        raise

#Get list of parameter for dropdown list
def task_para_list(v_para_typ):    
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('GET_PARA_CHOOSEITEMS', [v_para_typ, outcursor])
        results = outcursor.getvalue()
        return results    
    except:
        # Re-raise the exception.
        raise        

#Get choices for the parameter
def task_para_choice(v_group, v_para):    
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('GET_PARANAME_CHOICE', [v_group, v_para, outcursor])
        results = outcursor.getvalue()
        return results
    except:
        # Re-raise the exception.
        raise        

#Get tasklog
def task_log_activity(v_taskcd, v_refversion, v_reftaskid):    
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        if v_taskcd == 'TASKDATA':
            sql_query = "SELECT VERSION, PARACONTENT FROM TASKLOG_V2 WHERE TASKCD='{}' \
                                ".format(v_taskcd)
        else:
            sql_query = "SELECT * FROM TASKLOG_V2 WHERE TASKCD='{}'".format(v_taskcd)
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return results    
    except:
        # Re-raise the exception.
        raise        

#Get tasklog
def task_choosing(v_taskcd):    
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        sql = "SELECT TASKID, REFVERSION, PARACONTENT FROM TASKLOG_V2 WHERE TASKCD='{}'".format(v_taskcd)
        cursor.execute(sql)
        results = cursor.fetchall()
        return results   
    except:
        # Re-raise the exception.
        raise        

 #Get data version
def dataversion_choosing(v_refversion, v_typeofquery, v_tagcolor, v_maxrows):    
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('GET_TASK_DATA', [v_refversion, v_typeofquery, v_maxrows, outcursor])
        results = outcursor.getvalue()
        return results     
    except:
        # Re-raise the exception.
        raise        

def datakri_choosing(v_refversion):
    try:
        con = cx_Oracle.connect(settings.BACKEND_DB)
        cursor = con.cursor()
        outcursor = cursor.var(cx_Oracle.CURSOR)
        cursor.callproc('GET_TASK_DATA_KRI', [v_refversion, outcursor])
        results = outcursor.getvalue()
        return results     
    except:
        # Re-raise the exception.
        raise        

#Helper function cho phần xử lý AutoRun: Quét toàn bộ tham số chạy tự động để sinh task
#Build matrix of parameter
def task_para_matrix(v_para_variables, v_para_dict):
    try:
        #v_para_variables: Là chuỗi chưa tên biến
        #v_para_dict: dictionary các giá trị của từng biến
        set_count = 1
        para_count = 0
        para_variables = v_para_variables 
        para_dict = v_para_dict 
        para_tag = '@'
        arr_dict_value_prev = []
        arr_dict_value_curr = []
        for key in para_dict:
            para_count = para_count + 1
            para_name = para_tag + key + para_tag
            #Get paraname
            #s = para_dict.get(key).replace('{','')
            #s = s.replace('}','')
            arr_val = para_dict.get(key).split('/')
            #Lấy danh sách các giá trị của biến
            x = len(arr_val)
            arr_dict_value_curr = []
            if (para_count==1):
                #Nếu là biến đầu tiên thì là mảng một chiều với số phần tử bằng đúng số giá trị
                for i in range(len(arr_val)):
                    arr_dict_value_curr.append(para_variables.replace(para_name, arr_val[i]))
            else:
                #Nếu là biến tiếp theo thì mảng tham số trước sẽ phải nhân thêm x lần giá trị
                for i_para_idx in range(len(arr_val)):
                    for i_prev_idx in range(len(arr_dict_value_prev)):
                        #Quét hết các giá trị trước đó để thêm giá trị tham số mới
                        arr_dict_value_curr.append(arr_dict_value_prev[i_prev_idx].replace(para_name, arr_val[i_para_idx]))
            set_count = set_count*x
            arr_dict_value_prev = arr_dict_value_curr
        return arr_dict_value_prev
    except:
        # Re-raise the exception.
        raise        

def task_runall_parameters(v_mastertaskid, v_rootversionid, v_refparacontent):
    try:
        #Mp_taskcd: MODELLING or AUTOMODELLING
        ret_count_modelling = 0
        if 1==1:
            #Get parameter setting
            ref_preprocessing_variables=''
            ref_labelling_variables=''
            ref_classification_variables=''
            arr_name_preprocessing = []
            arr_value_preprocessing = []
            arr_name_labelling = []
            arr_value_labelling = []
            arr_name_classification = []
            arr_value_classification = []
            ret = task_para_get('PARADATA')
            para_tag = '@'
            for row in ret:
                para_group=row[0]
                para_name=row[1]
                para_val=row[2]
                if (para_group=='DEF_CLASSIFICATION'):
                    arr_name_classification.append(para_name)
                    arr_value_classification.append(para_val)
                    if (len(ref_classification_variables)==0):
                        ref_classification_variables = para_tag + para_name + para_tag
                    else:
                        ref_classification_variables = ref_classification_variables + '/' + para_tag + para_name + para_tag
                elif (para_group=='DEF_LABELLING'):
                    arr_name_labelling.append(para_name)
                    arr_value_labelling.append(para_val)
                    if (len(ref_labelling_variables)==0):
                        ref_labelling_variables = para_tag + para_name + para_tag
                    else:
                        ref_labelling_variables = ref_labelling_variables + '/' + para_tag + para_name + para_tag
                elif (para_group=='DEF_PREPROCESSING'):
                    arr_name_preprocessing.append(para_name)
                    arr_value_preprocessing.append(para_val)
                    if (len(ref_preprocessing_variables)==0):
                        ref_preprocessing_variables = para_tag + para_name + para_tag
                    else:
                        ref_preprocessing_variables = ref_preprocessing_variables + '/' + para_tag + para_name + para_tag
            para_preprocessing_dict = dict(zip(arr_name_preprocessing, arr_value_preprocessing))
            para_labelling_dict = dict(zip(arr_name_labelling, arr_value_labelling))
            para_classification_dict = dict(zip(arr_name_classification, arr_value_classification))

            #Lấy tập giá trị: PREPROCESSING, LABELLING, CLASSIFICATION 
            ref_preprocessing_values=task_para_matrix(ref_preprocessing_variables, para_preprocessing_dict)
            ref_classification_values=task_para_matrix(ref_classification_variables, para_classification_dict)
            ref_labelling_values=task_para_matrix(ref_labelling_variables, para_labelling_dict)

            #Build tham số modeling: Run all là tổ hợp của các giá trị PREPROCESSING, LABELLING, CLASSIFICATION 
            arr_modelling_values=[]
            p_para_values = ref_preprocessing_values
            p_n_preprocessing=ref_preprocessing_variables.replace(para_tag,'') 
            p_n_labelling=ref_labelling_variables.replace(para_tag,'') 
            #REFTTR cách sử dụng nhãn xử lý
            p_n_classification= 'REFTTR/' + ref_classification_variables.replace(para_tag,'') 

            con = cx_Oracle.connect(settings.BACKEND_DB)
            cursor = con.cursor()
            ret_count = cursor.var(int)
            para_modelling_mask='PREPROCESSINGID/LABELLINGID/CLASSIFICATIONID/MASTERID: ID_PREPROCESSING/ID_LABELLING/ID_CLASSIFICATION/ID_MASTER'
            para_refttr='D' #Mặc định chỉ sử dụng nhãn do labelling xác định
            #Giá trị thứ 2 của chuỗi AUTOMODELLING chỉ ra lựa chọn sử dụng nhãn do labelling xác định
            v_ref_automodelling_para = v_refparacontent.split(':')[1]
            para_refttr = v_ref_automodelling_para.split('/')[1]
            para_refttr = para_refttr.replace(']', '')
            p_paracontent=''
            p_reftaskid = 0
            id_preprocessing=0
            id_labelling=0
            id_classification=0
            id_modelling=0
            for p_v_preprocessing in ref_preprocessing_values:
                #Quét mảng tham số preprocessing
                item_val = p_v_preprocessing.replace('{','')
                item_val = item_val.replace('}','')
                item_preprocessing=p_n_preprocessing + ': [' + item_val + ']'
                #Ghi nhận bản ghi tham số preprocessing
                p_paracontent = item_preprocessing
                p_reftaskid = v_rootversionid
                cursor.callproc('SP_ENGINE_PROCESS_TASK_REQUEST', [p_reftaskid, p_paracontent, 0, '', ret_count])
                con.commit()
                id_preprocessing = ret_count.getvalue()
                for p_v_labelling in ref_labelling_values:
                    #Quét mảng tham số labelling
                    item_val = p_v_labelling.replace('{','')
                    item_val = item_val.replace('}','')
                    item_labelling=p_n_labelling + ': [' + item_val + ']'
                    #Ghi nhận bản ghi tham số labelling
                    p_paracontent = item_labelling
                    p_reftaskid = id_preprocessing
                    cursor.callproc('SP_ENGINE_PROCESS_TASK_REQUEST', [p_reftaskid, p_paracontent, 0, '', ret_count])
                    con.commit()
                    id_labelling = ret_count.getvalue()
                    for p_v_classification in ref_classification_values:
                        #try:
                            #Quét mảng tham số classification
                            item_val = p_v_classification.replace('{','')
                            item_val = item_val.replace('}','')
                            item_classification=p_n_classification + ': [' + para_refttr + '/'+ item_val + ']'
                            #Xử lý tham số REFTTR ở đây
                            #Ghi nhận bản ghi tham số classification
                            p_paracontent = item_classification
                            p_reftaskid = id_labelling
                            cursor.callproc('SP_ENGINE_PROCESS_TASK_REQUEST', [p_reftaskid, p_paracontent, 0, '', ret_count])
                            con.commit()
                            id_classification = ret_count.getvalue()
                            #Nội dụng bộ tham số (sử dụng logging nếu cần)
                            item_modelling = item_preprocessing + '###' + item_labelling + '###' + item_classification
                            #Tạo bản ghi Modelling và submit task xử ký: 
                            #Ghi nhận vào PARACONTENT MASTERID để link đến ID AUTOMODELLING v_mastertaskid
                            p_paracontent =  para_modelling_mask
                            p_paracontent =  p_paracontent.replace('ID_PREPROCESSING', str(id_preprocessing))
                            p_paracontent =  p_paracontent.replace('ID_LABELLING', str(id_labelling))
                            p_paracontent =  p_paracontent.replace('ID_CLASSIFICATION', str(id_classification))
                            p_paracontent =  p_paracontent.replace('ID_MASTER', str(v_mastertaskid))
                            p_reftaskid = id_classification
                            cursor.callproc('SP_ENGINE_PROCESS_TASK_REQUEST', [p_reftaskid, p_paracontent, 0, '', ret_count])
                            con.commit()
                            id_modelling = ret_count.getvalue()
                            ret_count_modelling = ret_count_modelling + 1
                            #Submit single task to celery for processing
                            tasks.runtask.apply_async(args=[id_modelling,'MODELLING']) 
                            p_ret_status='S'
                            p_ret_logontent='OK'
                        #except Exception as e:
                        #   p_status='E'
                        #  p_logontent=str(e)
                            #continue

        return ret_count_modelling    
    except:
        # Re-raise the exception.
        raise        
