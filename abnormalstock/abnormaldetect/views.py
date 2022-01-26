from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.timezone import datetime
from django.http import HttpResponse
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from abnormaldetect.forms import *
from abnormaldetect.models import LogMessage
from abnormaldetect import cmdbackend, chartdata
from abnormalstock import settings
import pandas as pd
import traceback

import os
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime  
# Create user views here.
#-----------------------------------------------------------------------------------------------
@csrf_exempt
def userindex(request):
    try:
        taxcode=''
        queryset = ''
        queryset_rating = ''
        if request.method == "POST":
            form = UserIndexForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_submit' in request.POST:
                    taxcode = cd['TaxCode']
                    queryset =  cmdbackend.user_taxcode_inquiry(taxcode,'P')
                    queryset_rating =  cmdbackend.user_taxcode_inquiry(taxcode,'R')
        else:
            form = UserIndexForm()
            queryset = ''
            taxcode=''

        context = {
            "message_list": queryset,
            "message_list_rating": queryset_rating,
            "taxcode": taxcode,
            "form": form
        }
        #Show result on screen
        return render(request, "abnormaldetect/userindex.html", context)
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
        return render(request, "abnormaldetect/userindex.html", context)

@csrf_exempt
def usermodel(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            queryset = ''
            queryset_scorecard=''
            message_list_tree=''
            queryset_dashboard=''
            arr_variables=[]
        else:
            #pandas_frame for queryset_dashboard
            model_variables = cmdbackend.func_modelid_variableset(reflinkid)
            arr_variables = model_variables.split('/')
            queryset_dashboard = cmdbackend.user_model_info_df(reflinkid, 'D')
            #Bo di cac truong khong lien quan den mo hinh
            colnames = model_variables + "/DIEM/DTTHUAN/MST/NAM/GIANLAN"
            arr_colnames = colnames.split('/')
            #Actual dataframe 
            df_final = []
            for item_name, rec in queryset_dashboard.iterrows():
                data=[]
                for fld in arr_colnames:
                    if fld in queryset_dashboard.columns:
                        data.append(rec[fld])
                df_final.append(data)
            #Actual column
            actual_colnames = ''
            for fld in arr_colnames:
                if fld in queryset_dashboard.columns:
                    if actual_colnames == '':
                        actual_colnames = fld
                    else:
                        actual_colnames = actual_colnames + '/' + fld
            queryset = cmdbackend.user_model_info(reflinkid, 'M')
            queryset_scorecard = cmdbackend.user_model_info(reflinkid, 'S')
            message_list_tree = cmdbackend.user_model_rule_info(reflinkid)
        context = {
            "message_list": queryset,
            "message_list_scorecard": queryset_scorecard,
            "message_list_tree": message_list_tree,
            "queryset_dashboard": df_final,
            "queryset_columns": actual_colnames.split('/'),
            "arr_variables": arr_variables,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/usermodel.html", context)

@csrf_exempt
def userlogisticmodel(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            queryset = ''
            queryset_scorecard=''
        else:
            queryset = cmdbackend.user_model_info(reflinkid, 'L')
            queryset_scorecard = cmdbackend.user_model_info(reflinkid, 'X')
        context = {
            "message_list": queryset,
            "message_list_scorecard": queryset_scorecard,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/usershowlogisticmodel.html", context)

@csrf_exempt
def userdecisiontreemodel(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            queryset = ''
        else:
            queryset = cmdbackend.GetModel2Show(reflinkid, 'T')
        context = {
            "message_list": queryset,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/usershowtreemodel.html", context)

@csrf_exempt
def userrandomforestmodel(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            queryset = ''
        else:
            queryset = cmdbackend.GetModel2Show(reflinkid, 'R')
        context = {
            "message_list": queryset,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/usershowtreemodel.html", context)

@csrf_exempt
def userdatacheck(request):
    try:
        yearofdata=0
        area = ''
        queryset = ''
        if request.method == "POST":
            form = UserReconcileForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_submit' in request.POST: 
                    yearofdata = cd['YearOfData']
                    area = cd['Area']
                    queryset =  cmdbackend.user_data_check(yearofdata, area)
        else:
            form = UserReconcileForm()   
            queryset = ''
        context = {
            "message_list": queryset,
            "year": yearofdata,
            "area": area,
            "form": form
        }    
        #Show result on screen
        return render(request, "abnormaldetect/userdatacheck.html", context)
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
        return render(request, "abnormaldetect/datacheck.html", context)

@csrf_exempt
def userdatacheckdetail(request, refyear='', refarea='', reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            queryset = ''
        else:
            queryset = cmdbackend.user_data_check_detail(refyear, refarea, reflinkid)
        context = {
            "message_list": queryset,
            "refyear": refyear,
            "refarea": refarea,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/userreconcile.html", context)

@csrf_exempt
def userreconcile(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            queryset = ''
        else:
            queryset = cmdbackend.get_reconcile_result(reflinkid)
        context = {
            "message_list": queryset,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/userreconcile.html", context)

def userkriset(request):
    try:
        kriset=''
        queryset = ''
        if request.method == "POST":
            form = KRISetForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_submit' in request.POST: 
                    kriset = cd['KRISet']
                    queryset =  cmdbackend.user_kriset(kriset)
        else:
            form = KRISetForm()   
            queryset = ''
            kriset=''
        context = {
            "message_list": queryset,
            "kriset": kriset,
            "form": form
        }    
        #Show result on screen
        return render(request, "abnormaldetect/userkriset.html", context)
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
        return render(request, "abnormaldetect/userkriset.html", context)

def userprediction(request):
    try:
        queryset = ''
        method = ''
        if request.method == "POST":
            form = UserPredictionForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_submit' in request.POST: 
                    method = cd['Method']
                    
                    # dataversion = cd['DataVersion']
                    # abnormthresh = cd['AbnormThreshold']
                    # difftest = cd['DiffTest']
                    # fithresh = cd['FIThreshold']
                    # featureimportance = cd['FeatureImpotance']
                    # maxlag = cd['MaxLag']
                    # mintradeday = cd['MinTradeDay']
                    # replacenan = cd['ReplaceNan']
                    # scoreconvert = cd['ScoreConvert']
                    # scorethresh = cd['ScoreThreshold']
                    # stationtest = cd['StationarityTest']
                    # topfeature = cd['TopFeature']

                    maxrows = cd['MaxRows']
                    queryset =  cmdbackend.user_prediction(datetime.now().strftime("%D:%H:%M:%S"), cd,maxrows)
                    # queryset = [['None', 'None','None', 'None','None','None']]

        else:
            form = UserPredictionForm()   
            queryset = [['None', 'None','None', 'None','None','None']]
        context = {
            "message_list": queryset,
            "method": method,
            "form": form
        }    
        #Show result on screen
        return render(request, "abnormaldetect/userprediction.html", context)
    except Exception as e:
        print(e)
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
        return render(request, "abnormaldetect/userprediction.html", context)

@csrf_exempt
def userpredictversion(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            queryset = ''
        else:
            queryset = cmdbackend.user_predictversion(reflinkid)
        context = {
            "message_list": queryset,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/userpredictversion.html", context)

@csrf_exempt
def userfrauditem(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            queryset = ''
        else:
            queryset = cmdbackend.user_frauditem(reflinkid)
        context = {
            "message_list": queryset,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/userfrauditem.html", context)

def userinquiry(request):
    try:
        queryset = ''
        typeofinquiry=''
        if request.method == "POST":
            form = UserInquiryForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_submit' in request.POST: 
                    dataversion = cd['DataVersion']
                    typeofinquiry = cd['TypeofInquiry']
                    maxrows = cd['MaxRows']
                    queryset =  cmdbackend.user_inquiry(dataversion,typeofinquiry,maxrows)
        else:
            form = UserInquiryForm()   
            queryset = ''
        context = {
            "message_list": queryset,
            "typeofinquiry": typeofinquiry,
            "form": form
        }    
        #Show result on screen
        return render(request, "abnormaldetect/userinquiry.html", context)
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
        return render(request, "abnormaldetect/userinquiry.html", context)

@csrf_exempt
def userriskprofile(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            querysetKRI = ''
            querysetITEM = ''
            querysetRATING = ''
            querysetPROFILE = ''
            querysetTTR = ''
        else:
            querysetKRI = cmdbackend.user_riskprofile(reflinkid, 'K')
            querysetITEM = cmdbackend.user_riskprofile(reflinkid, 'I')
            querysetRATING = cmdbackend.user_riskprofile(reflinkid, 'R')
            querysetPROFILE = cmdbackend.user_riskprofile(reflinkid, 'P')
            querysetTTR = cmdbackend.user_riskprofile(reflinkid, 'A')
        context = {
            "message_list_kri": querysetKRI,
            "message_list_item": querysetITEM,
            "message_list_rating": querysetRATING,
            "message_list_profile": querysetPROFILE,
            "message_list_ttr": querysetTTR,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/userriskprofile.html", context)

# Create admin views here.
#-----------------------------------------------------------------------------------------------
@csrf_exempt
def home(request):
    context = {'vendor': 'FSS'}
    try:
        queryset =  cmdbackend.task_para_get('DICTKRI')
        context = {
            "message_list": queryset
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/home.html", context)    

@method_decorator(csrf_exempt, name='dispatch')
class HomeListView(ListView):
    """Renders the home page, with a list of all messages."""
    model = LogMessage
    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        return context

@csrf_exempt
def taskparameter(request):
    context = {'vendor': 'FSS'}
    try:
        if request.method == "POST":
            form = ParameterForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_add' in request.POST:        
                    cmdbackend.task_para_setup(cd['para_name'],cd['para_value'],cd['YesNo'],'ADD')
                elif 'para_del' in request.POST:        
                    cmdbackend.task_para_setup(cd['para_name'],cd['para_value'],cd['YesNo'],'DEL')
        else:
            form = ParameterForm()   
        queryset =  cmdbackend.task_para_get('PARA')
        context = {
            "message_list": queryset,
            "form": form
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/taskparameter.html", context)

@csrf_exempt
def logisticmodel(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            queryset = ''
            queryset_scorecard=''
        else:
            queryset = cmdbackend.user_model_info(reflinkid, 'L')
            queryset_scorecard = cmdbackend.user_model_info(reflinkid, 'X')
        context = {
            "message_list": queryset,
            "message_list_scorecard": queryset_scorecard,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/logisticmodel.html", context)

@csrf_exempt
def decisiontreemodel(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            queryset = ''
        else:
            queryset = cmdbackend.GetModel2Show(reflinkid, 'T')
        context = {
            "message_list": queryset,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/showtreemodel.html", context)

@csrf_exempt
def randomforestmodel(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            queryset = ''
        else:
            queryset = cmdbackend.GetModel2Show(reflinkid, 'R')
        context = {
            "message_list": queryset,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/showtreemodel.html", context)

@csrf_exempt
def reconcile(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            queryset = ''
        else:
            queryset = cmdbackend.get_reconcile_result(reflinkid)
        context = {
            "message_list": queryset,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/reconcile.html", context)

@csrf_exempt
def predictversion(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            queryset = ''
        else:
            queryset = cmdbackend.get_predictversion(reflinkid)
        context = {
            "message_list": queryset,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/predictversion.html", context)

@csrf_exempt
def riskprofile(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            querysetKRI = ''
            querysetITEM = ''
            querysetRATING = ''
            querysetPROFILE = ''
            querysetTTR = ''
            querysetSTATISTIC = ''
        else:
            querysetKRI = cmdbackend.get_riskprofile(reflinkid, 'K')
            querysetITEM = cmdbackend.get_riskprofile(reflinkid, 'I')
            querysetRATING = cmdbackend.get_riskprofile(reflinkid, 'R')
            querysetPROFILE = cmdbackend.get_riskprofile(reflinkid, 'P')
            querysetTTR = cmdbackend.get_riskprofile(reflinkid, 'A')
            querysetSTATISTIC = cmdbackend.get_riskprofile(reflinkid, 'S')
        context = {
            "message_list_kri": querysetKRI,
            "message_list_item": querysetITEM,
            "message_list_rating": querysetRATING,
            "message_list_profile": querysetPROFILE,
            "message_list_ttr": querysetTTR,
            "message_list_statistic": querysetSTATISTIC,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/riskprofile.html", context)

@csrf_exempt
def frauditem(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            queryset = ''
        else:
            queryset = cmdbackend.get_frauditem(reflinkid)
        context = {
            "message_list": queryset,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/frauditem.html", context)


@csrf_exempt
def frauditem_full(request, reflinkid=''):
    context = {'vendor': 'FSS'}
    try:
        if reflinkid=='':
            querysetKRI = ''
            querysetITEM = ''
            querysetRATING = ''
            querysetPROFILE = ''
            querysetTTR = ''
            querysetSTATISTIC = ''
        else:
            querysetKRI = cmdbackend.get_frauditem_info(reflinkid, 'K')
            querysetITEM = cmdbackend.get_frauditem_info(reflinkid, 'I')
            querysetRATING = cmdbackend.get_frauditem_info(reflinkid, 'R')
            querysetPROFILE = cmdbackend.get_frauditem_info(reflinkid, 'P')
            querysetTTR = cmdbackend.get_frauditem_info(reflinkid, 'A')
            querysetSTATISTIC = cmdbackend.get_frauditem_info(reflinkid, 'S')
        context = {
            "message_list_kri": querysetKRI,
            "message_list_item": querysetITEM,
            "message_list_rating": querysetRATING,
            "message_list_profile": querysetPROFILE,
            "message_list_ttr": querysetTTR,
            "message_list_statistic": querysetSTATISTIC,
            "linkid": reflinkid
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/frauditem.html", context)

@csrf_exempt
def taskETL(request):
    context = {'vendor': 'FSS'}
    try:
        refCategory =''
        refYear = 'refYear'
        if request.method == "POST":
            form = ETLForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_submit' in request.POST: 
                    refCategory = cd['Category']
                    refYear = cd['Year']
                    queryset =  cmdbackend.task_ETL_execute(refCategory, refYear)                
        else:
            form = ETLForm()   
            queryset = ''
        context = {
            "message_list": queryset,
            "category": refCategory,
            "year": refYear,
            "form": form
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/taskETL.html", context)    

@csrf_exempt
def taskcommand(request):
    context = {'vendor': 'FSS'}
    try:
        exportdata = False
        queryset =''
        metadata =''
        cmdType =''
        if request.method == "POST":
            form = CommandForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_submit' in request.POST  or 'para_export' in request.POST: 
                    cmdType = cd['cmdType']
                    cmdContent = cd['cmdContent']
                    queryset =  cmdbackend.task_command_exec(cmdType, cmdContent)
                    metadata =  cmdbackend.task_command_meta(cmdType, cmdContent)
                    if 'para_export' in request.POST and cmdType=='R':
                        exportdata = True
        else:
            form = CommandForm()   
        context = {
            "message_list": queryset,
            "command_type": cmdType,
            "column_metadata": metadata,
            "form": form
        }    
        if exportdata==True:
            #Export data to csv
            df = pd.DataFrame(queryset)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=filename.csv'
            df.to_csv(path_or_buf=response,sep='\t',float_format='%.2f',index=False,decimal=",", encoding='utf-8')
            return response
        else:
            #Show result on screen
            return render(request, "abnormaldetect/taskcommand.html", context)
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
        return render(request, "abnormaldetect/taskcommand.html", context)

@csrf_exempt
def taskquery(request):
    context = {'vendor': 'FSS'}
    try:
        exportdata = False
        taxcode=''
        typeofquery='D'
        if request.method == "POST":
            form = QueryForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_submit' in request.POST or 'para_export' in request.POST: 
                    if 'para_export' in request.POST:
                        exportdata = True
                    refversion = cd['Data']
                    typeofquery = cd['TypeofQuery']
                    tagcolor = cd['TagColor']
                    taxcode = cd['TaxCode']
                    maxrows = cd['MaxRows']
                    if typeofquery == "X":
                        queryset =  cmdbackend.task_log_activity('', refversion,0)
                    elif typeofquery == "I" or typeofquery == "K" or typeofquery == "R":
                        #Lay ten doanh nghiep
                        #Checking item refversion change to taxcode
                        queryset =  cmdbackend.dataversion_choosing(taxcode, typeofquery, tagcolor, maxrows)
                    else:
                        queryset =  cmdbackend.dataversion_choosing(refversion, typeofquery, tagcolor, maxrows)
        else:
            form = QueryForm()   
            queryset = ''
        context = {
            "message_list": queryset,
            "typeofquery": typeofquery,
            "taxcode": taxcode,
            "form": form
        }    
        if exportdata==True:
            #Export data to csv
            df = cmdbackend.Cursor2DataFrame(queryset)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=filename.csv'
            df.to_csv(path_or_buf=response,sep='\t',float_format='%.2f',index=False,decimal=",", encoding='utf-8')
            return response
        else:
            #Show result on screen
            return render(request, "abnormaldetect/taskquery.html", context)
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
        return render(request, "abnormaldetect/taskquery.html", context)

@csrf_exempt
def taskdata(request):
    context = {'vendor': 'FSS'}
    try:
        if request.method == "POST":
            form = ChooseDataForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_submit' in request.POST: 
                    cmdbackend.task_data_submit(cd['Category'], cd['Industry'], cd['Area'], cd['Age'], cd['Capital'], cd['Year'], cd['KRISet'], cd['KRILoss'])
        else:
            form = ChooseDataForm()   
        queryset =  cmdbackend.task_para_get('TASKDATA')
        context = {
            "message_list": queryset,
            "form": form
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/taskdata.html", context)    

@csrf_exempt
def tasksubmit(request):
    context = {'vendor': 'FSS'}
    try:
        #Run modeling với tất cả các tham số mặc định
        taskcd = 'AUTOMODELLING'
        if request.method == "POST":
            form = AutoRunForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_submit' in request.POST: 
                    reftaskid = cd['Data']
                    para_content = 'AUTOMODELLING/REFTTR: [Y/'
                    para_content = para_content + cd['REFTTR'] + ']'
                    cmdbackend.task_pipeline_submit(taskcd,reftaskid,para_content,0,'')    
        else:
            form = AutoRunForm()   
        querycases = cmdbackend.task_para_get('AUTORUNCASES')
        queryset =  cmdbackend.task_log_activity(taskcd,'',0)
        context = {
            "group_cases": querycases,
            "message_list": queryset,
            "form": form
        }  
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/tasksubmit.html", context)      

@csrf_exempt
def taskmodelling(request):
    context = {'vendor': 'FSS'}
    try:
        taskcd='MODELLING'
        if request.method == "POST":
            form = ModellingForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_submit' in request.POST: 
                    reftaskid = cd['Data']
                    cmdbackend.task_pipeline_submit(taskcd,reftaskid,'MODELLING',0,'')
        else:
            form = ModellingForm()   
        queryset =  cmdbackend.task_log_activity(taskcd,'',0)
        context = {
            "message_list": queryset,
            "form": form
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/taskmodelling.html", context)    

@csrf_exempt
def taskpreprocessing(request):
    context = {'vendor': 'FSS'}
    try:
        taskcd='PREPROCESSING'
        if request.method == "POST":
            form = PreprocessingForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_submit' in request.POST: 
                    reftaskid = cd['Data']
                    para_content = 'BALANCEDATAMETHOD/CATEGORICALIMPUTER/CATEGORICALOUTLIERS/CHOOSEONEHOTENCODER/COMBINECATEGORICAL/NUMERICIMPUTER/NUMERICOUTLIERS/N_COMPONENTS/N_FOLDS/PARAMETERFORBALANCEDATA/PCALABELLING/RATEHOLDCOL/RATEHOLDROW/SCALER/SVD_SOLVER/TEST_SIZE/WHIS_BOXPLOT: ['
                    para_content = para_content + cd['BALANCEDATAMETHOD'] + '/'
                    para_content = para_content + cd['CATEGORICALIMPUTER'] + '/'
                    para_content = para_content + cd['CATEGORICALOUTLIERS'] + '/'
                    para_content = para_content + cd['CHOOSEONEHOTENCODER'] + '/'
                    para_content = para_content + cd['COMBINECATEGORICAL'] + '/'
                    para_content = para_content + cd['NUMERICIMPUTER'] + '/'
                    para_content = para_content + cd['NUMERICOUTLIERS'] + '/'
                    para_content = para_content + cd['N_COMPONENTS'] + '/'
                    para_content = para_content + cd['N_FOLDS'] + '/'
                    para_content = para_content + cd['PARAMETERFORBALANCEDATA'] + '/'
                    para_content = para_content + cd['PCALABELLING'] + '/'
                    para_content = para_content + cd['RATEHOLDCOL'] + '/'
                    para_content = para_content + cd['RATEHOLDROW'] + '/'
                    para_content = para_content + cd['SCALER'] + '/'
                    para_content = para_content + cd['SVD_SOLVER'] + '/'
                    para_content = para_content + cd['TEST_SIZE'] + '/'
                    para_content = para_content + cd['WHIS_BOXPLOT'] + ']'
                    cmdbackend.task_pipeline_submit(taskcd,reftaskid,para_content,0,'')
        else:
            form = PreprocessingForm()   
        queryset =  cmdbackend.task_log_activity(taskcd,'',0)
        context = {
            "message_list": queryset,
            "form": form
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/taskpreprocessing.html", context)    

@csrf_exempt
def tasklabelling(request):
    context = {'vendor': 'FSS'}
    try:
        taskcd='LABELLING'
        if request.method == "POST":
            form = LabellingForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_submit' in request.POST: 
                    reftaskid = cd['Data']
                    para_content = 'BOOTSTRAP/EPS/INIT/MAX_ITER/MAX_SAMPLE/METRIC/MIN_SAMPLES/NAME_METHOD/N_CLUSTERS/N_ESTIMATORS/N_NEIGHBORS/RADIUSTHRESHOLD: ['
                    para_content = para_content + cd['BOOTSTRAP'] + '/'
                    para_content = para_content + cd['EPS'] + '/'
                    para_content = para_content + cd['INIT'] + '/'
                    para_content = para_content + cd['MAX_ITER'] + '/'
                    para_content = para_content + cd['MAX_SAMPLE'] + '/'
                    para_content = para_content + cd['METRIC'] + '/'
                    para_content = para_content + cd['MIN_SAMPLES'] + '/'
                    para_content = para_content + cd['NAME_METHOD'] + '/'
                    para_content = para_content + cd['N_CLUSTERS'] + '/'
                    para_content = para_content + cd['N_ESTIMATORS'] + '/'
                    para_content = para_content + cd['N_NEIGHBORS'] + '/'
                    para_content = para_content + cd['RADIUSTHRESHOLD'] + ']'
                    cmdbackend.task_pipeline_submit(taskcd,reftaskid,para_content,0,'')
        else:
            form = LabellingForm()   
        queryset =  cmdbackend.task_log_activity(taskcd,'',0)
        context = {
            "message_list": queryset,
            "form": form
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/tasklabelling.html", context)        

@csrf_exempt
def taskclassification(request):
    context = {'vendor': 'FSS'}
    try:
        taskcd='CLASSIFICATION'
        if request.method == "POST":
            form = ClassificationForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_submit' in request.POST: 
                    reftaskid = cd['Data']
                    para_content = 'REFTTR/NAME_METHOD/C/CRITERION/MAX_DEPTH/MAX_FEATURE/N_ESTIMATORS/PENALTY/SOLVER/SCORE_THRESHOLD: ['
                    para_content = para_content + cd['REFTTR'] + '/'
                    para_content = para_content + cd['NAME_METHOD'] + '/'
                    para_content = para_content + cd['C'] + '/'
                    para_content = para_content + cd['CRITERION'] + '/'
                    para_content = para_content + cd['MAX_DEPTH'] + '/'
                    para_content = para_content + cd['MAX_FEATURE'] + '/'
                    para_content = para_content + cd['N_ESTIMATORS'] + '/'
                    para_content = para_content + cd['PENALTY'] + '/'
                    para_content = para_content + cd['SOLVER'] + '/'
                    #para_content = para_content + cd['KERNEL'] + '/'
                    #para_content = para_content + cd['GAMMA'] + '/'
                    #para_content = para_content + cd['LEARNING_RATE'] + '/'
                    para_content = para_content + cd['SCORE_THRESHOLD'] + ']'
                    cmdbackend.task_pipeline_submit(taskcd,reftaskid,para_content,0,'')                
        else:
            form = ClassificationForm()   
        queryset =  cmdbackend.task_log_activity(taskcd,'',0)
        context = {
            "message_list": queryset,
            "form": form
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/taskclassification.html", context)      

@csrf_exempt
def tasklog(request):
    context = {'vendor': 'FSS'}
    try:
        refversion =''
        if request.method == "POST":
            form = ActivityForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if 'para_submit' in request.POST: 
                    refversion = cd['Data']
        else:
            form = ActivityForm()   
        queryset =  cmdbackend.task_log_activity('', refversion,0)
        context = {
            "message_list": queryset,
            "form": form
        }    
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, "abnormaldetect/tasklog.html", context)        

def about(request):
    return render(request, "abnormaldetect/about.html")

def help(request):
    return render(request, "abnormaldetect/help.html")

def log_message(request):
    context = {'vendor': 'FSS'}
    form = LogMessageForm(request.POST or None)
    try:
        if request.method == "POST":
            if form.is_valid():
                message = form.save(commit=False)
                message.log_date = datetime.now()
                message.save()
                return redirect("home")
        else:
            return render(request, "abnormaldetect/log_message.html", {"form": form})
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
        return render(request, "abnormaldetect/log_message.html", {"form": form})

#Chart version: Dashboard
#-----------------------------------------------------------------------------------------------
def dashboard(request):
    context = {'vendor': 'FSS'}
    try:
        def __init__( self, *args, **kwargs ): 
            self.list = []
                
        # read default data for dashboard
        df = cmdbackend.GetChartData("M","DEFAULT")

        #Build data series for comparison
        comparison_year, comparison_prev_series, comparison_series = chartdata.comparison_series(df, "THUETNDN", "NGANHKT", "NAM")
        v_active_year = max(comparison_year)

        active_year_df = df.loc[df['NAM'] == v_active_year]
        #Build data series for bubble - current year
        bubble_series=chartdata.bubble_series(active_year_df, "THUETNDN", "NGANHKT", "TINH")
        #Build data series for sunburst - current year
        pie_series, pie_subseries = chartdata.drilldown_series(active_year_df, "THUETNDN", "NGANHKT", "NHOM")
        sunburst_series=chartdata.sunburst_series(active_year_df, "THUETNDN", "NGANHKT", "NHOM")
        
        #Build data series for scatter - current year
        scatter_data=chartdata.scatter_series(active_year_df, "THUETNDN", "NGANHKT")

        #Build data series for heatmap 
        heatmap_x, heatmap_y, heatmap_series=chartdata.heatmap_series(df, 'THUETNDN_GL', "NGANHKT", "NAM")
        
        # Build data series for drill down
        drilldown_series, drilldown_subseries = chartdata.drilldown_series(df, "THUETNDN", "NGANHKT", "NAM")

        #Main
        categories, values=chartdata.main_series(df, "NAM")

        #queryset =  cmdbackend.task_log_activity('', refversion,0)
        #Generic table data
        queryset=''
        table_content = df.to_html(index=None,table_id="sortTable",justify="center",classes="table table-striped table-bordered")
        table_content = table_content.replace("","")
        table_content = table_content.replace('border="1"',"")
        context = {"categories": categories, 
            'values': values, 
            'active_year': v_active_year, 
            'scatter_data': scatter_data, 
            'heatmap_x': heatmap_x, 
            'heatmap_y': heatmap_y, 
            'heatmap_series': heatmap_series, 
            'bubble_series': bubble_series, 
            'sunburst_series': sunburst_series, 
            'comparison_year': comparison_year, 
            'comparison_series': comparison_series, 
            'comparison_prev_series': comparison_prev_series, 
            'drilldown_series': drilldown_series, 
            'drilldown_subseries': drilldown_subseries, 
            'pie_series': pie_series, 
            'pie_subseries': pie_subseries, 
            'table_data':table_content,
            "message_list": queryset}
    except Exception as e:
        just_the_string = traceback.format_exc()
        messages.add_message(request, messages.ERROR, just_the_string)
    return render(request, 'abnormaldetect/dashboard.html', context=context)
#-----------------------------------------------------------------------------------------------