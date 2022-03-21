from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from abnormaldetect.models import LogMessage
from abnormaldetect import cmdbackend, admin
from abnormaldetect.source.upload_to_db import connect_data
from abnormalstock import settings
import cx_Oracle
class UserIndexForm(forms.Form):
    #Query riskprofile of DTNT
    TaxCode = forms.CharField(label = "TaxCode", required = True)

class UserReconcileForm(forms.Form):
    #Query reconcile data
    YearOfData = forms.IntegerField(label = "Year", help_text="Zero means all", required = True, initial=0)
    set_khuvuc = cmdbackend.task_para_list('KHUVUC')                
    ref_khuvuc = [(row[0], row[1]) 
                for row in set_khuvuc]   
    Area = forms.ChoiceField(choices  = ref_khuvuc)    

class UserPredictionForm(forms.Form):
    # Init every time load page
    set_datatype = ['POPULAR', 'VOLUMN', 'VOLATILITY', 'TREND', 'MOMENTUM', 'ADDFA', 'FULL']
    data_types = [(type, type) for i, type in enumerate(set_datatype)]    

    DatasetType = forms.ChoiceField(label = "DATASET TYPE", choices = data_types)     
    MaCK = forms.ChoiceField(label = "MACK", choices  = admin.PARAMS['MACK'], required= True, initial='ALL')
    FromDate = forms.CharField(label = "FROMDATE", required= True)
    ToDate = forms.CharField(label = "TODATE", required= True)

    StationarityTest = forms.ChoiceField(label = "STATIONARITYTEST", choices  = admin.PARAMS['STATIONARITYTEST'], required= True)
    DiffTest = forms.ChoiceField(label = "DIFFTYPE", choices  = admin.PARAMS['DIFFTYPE'], required= True)
    ReplaceNan = forms.ChoiceField(label = "REPLACENAN", choices  = admin.PARAMS['REPLACENAN'], required= True)
    MinTradeDay = forms.IntegerField(label = "MINTRADEDAY", required= True, initial=60)

    Method = forms.ChoiceField(label = "METHOD", choices  = admin.PARAMS['METHOD'], required= True)
    MaxLag = forms.IntegerField(label = "MAXLAG", required= True, initial=5)
    FeatureImpotance = forms.ChoiceField(label = "FEATUREIMPORTANCE", choices  = admin.PARAMS['FEATUREIMPORTANCE'], required= True)

    FIThreshold = forms.ChoiceField(label = "FITHRESHOLD", choices  = admin.PARAMS['FITHRESHOLD'], required= True)
    TopFeature = forms.IntegerField(label = "TOPFEATURE", required= True, initial=15)
    ScoreConvert = forms.ChoiceField(label = "SCORECONVERT", choices  = admin.PARAMS['SCORECONVERT'], required= True)
    ScoreThreshold = forms.ChoiceField(label = "SCORETHRESHOLD", choices  = admin.PARAMS['SCORETHRESHOLD'], required= True)
    AbnormThreshold = forms.IntegerField(label = "ABNORMTHRESHOLD", required= True, initial=14)

    MaxRows = forms.IntegerField(label = "Max rows", required = False, initial=1000)
    
class UserInquiryForm(forms.Form):
    #Init every time load page
    def __init__(self, *args, **kwargs):
        super(UserInquiryForm, self).__init__(*args, **kwargs)
        set_dataversion = cmdbackend.task_para_list('VERROOTDESC')
        ref_dataversion = [(row[0], row[1]) 
                    for row in set_dataversion]            
        self.fields['DataVersion'] = forms.ChoiceField(
            choices=ref_dataversion )  
    TypeofInquiry = forms.ChoiceField(label = "Type", choices  = settings.INQUIRY_CHOICES)
    MaxRows = forms.IntegerField(label = "Max rows", required = False, initial=1000)

class GenerateRandomUserForm(forms.Form):
    total = forms.IntegerField(
        validators=[
            MinValueValidator(50),
            MaxValueValidator(500)
        ]
    )
    
class LogMessageForm(forms.ModelForm):
    class Meta:
        model = LogMessage
        fields = ("message",)   # NOTE: the trailing comma is required

class KRISetForm(forms.Form):
    KRISet = forms.ChoiceField(label = "KRI", choices = settings.KRISET_CHOICES)

class ParameterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ParameterForm, self).__init__(*args, **kwargs)
        queryset = cmdbackend.task_para_list('PARA')
        ref_choices = [(row[0], row[1]) 
                    for row in queryset]    
        self.fields['para_name'] = forms.ChoiceField(
            choices=ref_choices )      
    para_value = forms.CharField(max_length = 100)
    YesNo = forms.ChoiceField(label = "For Auto Run", choices  = settings.YESNO_CHOICES)

class QueryForm(forms.Form):
    #Init every time load page
    def __init__(self, *args, **kwargs):
        super(QueryForm, self).__init__(*args, **kwargs)
        set_dataversion = cmdbackend.task_para_list('VERROOTDESC')
        ref_dataversion = [(row[0], row[1]) 
                    for row in set_dataversion]            
        self.fields['Data'] = forms.ChoiceField(
            choices=ref_dataversion )      
    TypeofQuery = forms.ChoiceField(label = "Type", choices  = settings.QUERY_CHOICES)
    TagColor = forms.ChoiceField(label = "Filter", choices  = settings.TAGCOLOR_CHOICES)
    TaxCode = forms.CharField(label = "TaxCode", required = False)
    MaxRows = forms.IntegerField(label = "Max rows", required = False, initial=1000)

class ETLForm(forms.Form):
    set_chitieu = cmdbackend.task_para_list('CHITIEU')
    ref_chitieu = [(row[0], row[1]) 
                for row in set_chitieu]    
    Category = forms.ChoiceField(choices  = ref_chitieu)
    Year = forms.IntegerField(label = "Year", help_text="Zero means all", required = False, initial=2016)

class CommandForm(forms.Form):
    cmdType = forms.ChoiceField(label = "Type", choices  = settings.COMMAND_CHOICES)
    cmdContent = forms.CharField(widget=forms.Textarea(attrs={"rows":6, "cols":60}), label = "Content", required = True, initial="SELECT CDTYPE, CDNAME, CDVAL, CDCONTENT, EN_CDCONTENT FROM ALLCODE WHERE CDUSER='Y' AND EN_CDCONTENT = 'DEF_LABELLING'")

class ActivityForm(forms.Form):
    #Init every time load page
    def __init__(self, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)
        set_dataversion = cmdbackend.task_para_list('VERROOTDESC')
        ref_dataversion = [(row[0], row[1]) 
                    for row in set_dataversion]            
        self.fields['Data'] = forms.ChoiceField(
            choices=ref_dataversion )  

class ChooseDataForm(forms.Form):
    set_datatype = ['POPULAR', 'VOLUMN', 'VOLATILITY', 'TREND', 'MOMENTUM', 'ADDFA', 'FULL']
    data_types = [(type, type) for i, type in enumerate(set_datatype)]    

    DatasetType = forms.ChoiceField(label = "DATASET TYPE", choices = data_types)    
    MaCK = forms.ChoiceField(label = "MACK", choices  = admin.PARAMS['MACK'], required= True, initial='ALL')
    FromDate = forms.CharField(label = "FROMDATE", required= True)
    ToDate = forms.CharField(label = "TODATE", required= True)

class ModellingForm(forms.Form):
    v_group='DEF_MODELLING'
    #Init every time load page
    def __init__(self, *args, **kwargs):
        super(ModellingForm, self).__init__(*args, **kwargs)
        set_dataversion = cmdbackend.task_choosing('LABELLING')
        ref_dataversion = []
        for i, content in enumerate(set_dataversion):
            cont = 'TaskID: {}, RootVersion: {}||{}'.format(content[0], content[1], content[2])
            ref_dataversion.append((content[0], cont))
        self.fields['Data'] = forms.ChoiceField(
            choices=ref_dataversion )  

class PreprocessingForm(forms.Form):
    v_group='DEF_PREPROCESSING'
    #Init every time load page
    def __init__(self, *args, **kwargs):
        super(PreprocessingForm, self).__init__(*args, **kwargs)
        set_dataversion = cmdbackend.task_choosing('TASKDATA')
        ref_dataversion = []
        for i, content in enumerate(set_dataversion):
            cont = 'TaskID: {}, RootVersion: {}||{}'.format(content[0], content[1], content[2])
            ref_dataversion.append((content[0], cont))
        self.fields['Data'] = forms.ChoiceField(
            choices=ref_dataversion )    

    #Parameter    
    StationarityTest = forms.ChoiceField(label = "STATIONARITYTEST", choices  = admin.PARAMS['STATIONARITYTEST'], required= True)
    DiffTest = forms.ChoiceField(label = "DIFFTYPE", choices  = admin.PARAMS['DIFFTYPE'], required= True)
    ReplaceNan = forms.ChoiceField(label = "REPLACENAN", choices  = admin.PARAMS['REPLACENAN'], required= True)
    MinTradeDay = forms.IntegerField(label = "MINTRADEDAY", required= True, initial=60)

    Method = forms.ChoiceField(label = "METHOD", choices  = admin.PARAMS['METHOD'], required= True)
    MaxLag = forms.IntegerField(label = "MAXLAG", required= True, initial=5)
    FeatureImpotance = forms.ChoiceField(label = "FEATUREIMPORTANCE", choices  = admin.PARAMS['FEATUREIMPORTANCE'], required= True)

class LabellingForm(forms.Form):
    v_group='DEF_LABELLING'
    #Init every time load page
    def __init__(self, *args, **kwargs):
        super(LabellingForm, self).__init__(*args, **kwargs)
        set_dataversion = cmdbackend.task_choosing('PREPROCESSING')
        ref_dataversion = []
        for i, content in enumerate(set_dataversion):
            cont = 'TaskID: {}, RootVersion: {}||{}'.format(content[0], content[1], content[2])
            ref_dataversion.append((content[0], cont))
        self.fields['Data'] = forms.ChoiceField(
            choices=ref_dataversion )     
    #Parameter    
    FIThreshold = forms.ChoiceField(label = "FITHRESHOLD", choices  = admin.PARAMS['FITHRESHOLD'], required= True)
    TopFeature = forms.IntegerField(label = "TOPFEATURE", required= True, initial=15)
    ScoreConvert = forms.ChoiceField(label = "SCORECONVERT", choices  = admin.PARAMS['SCORECONVERT'], required= True)
    ScoreThreshold = forms.ChoiceField(label = "SCORETHRESHOLD", choices  = admin.PARAMS['SCORETHRESHOLD'], required= True)
    AbnormThreshold = forms.IntegerField(label = "ABNORMTHRESHOLD", required= True, initial=14)
    
class ClassificationForm(forms.Form):
    v_group='DEF_CLASSIFICATION'
    #Init every time load page
    def __init__(self, *args, **kwargs):
        super(ClassificationForm, self).__init__(*args, **kwargs)
        set_dataversion = cmdbackend.task_choosing('LABELLING')
        ref_dataversion = [(row[0], row[1]) 
                    for row in set_dataversion]            
        self.fields['Data'] = forms.ChoiceField(
            choices=ref_dataversion )       
    REFTTR = forms.ChoiceField(label = "Using TTR result", choices  = settings.TTR_CHOICES)
    #Parameter    
    set_c= cmdbackend.task_para_choice(v_group, 'C')
    ref_c = [(row[0], row[1]) 
                for row in set_c] 
    set_criterion= cmdbackend.task_para_choice(v_group, 'CRITERION')
    ref_criterion = [(row[0], row[1]) 
                for row in set_criterion] 
    set_max_depth= cmdbackend.task_para_choice(v_group, 'MAX_DEPTH')
    ref_max_depth = [(row[0], row[1]) 
                for row in set_max_depth] 
    set_max_feature= cmdbackend.task_para_choice(v_group, 'MAX_FEATURE')
    ref_max_feature = [(row[0], row[1]) 
                for row in set_max_feature] 
    set_n_estimators= cmdbackend.task_para_choice(v_group, 'N_ESTIMATORS')
    ref_n_estimators = [(row[0], row[1]) 
                for row in set_n_estimators] 
    set_penalty= cmdbackend.task_para_choice(v_group, 'PENALTY')
    ref_penalty = [(row[0], row[1]) 
                for row in set_penalty] 
    set_solver= cmdbackend.task_para_choice(v_group, 'SOLVER')
    ref_solver = [(row[0], row[1]) 
                for row in set_solver] 
    set_score_threshold = cmdbackend.task_para_choice(v_group, 'SCORE_THRESHOLD')
    ref_score_threshold = [(row[0], row[1]) 
                for row in set_score_threshold]  
    set_name_method = cmdbackend.task_para_choice(v_group, 'NAME_METHOD')
    ref_name_method = [(row[0], row[1]) 
                for row in set_name_method]                                 
    C= forms.ChoiceField(choices  = ref_c)
    CRITERION= forms.ChoiceField(choices  = ref_criterion)
    MAX_DEPTH= forms.ChoiceField(choices  = ref_max_depth)
    MAX_FEATURE= forms.ChoiceField(choices  = ref_max_feature)
    N_ESTIMATORS= forms.ChoiceField(choices  = ref_n_estimators)
    PENALTY= forms.ChoiceField(choices  = ref_penalty)
    SOLVER= forms.ChoiceField(choices  = ref_solver)
    SCORE_THRESHOLD= forms.ChoiceField(choices  = ref_score_threshold)    
    NAME_METHOD= forms.ChoiceField(choices  = ref_name_method)    

class AutoRunForm(forms.Form):
    v_group='DEF_AUTOMODELLING'
    #Init every time load page
    def __init__(self, *args, **kwargs):
        super(AutoRunForm, self).__init__(*args, **kwargs)
        set_dataversion = cmdbackend.task_choosing('TASKDATA')
        ref_dataversion = []
        for i, content in enumerate(set_dataversion):
            cont = 'TaskID: {}, RootVersion: {}||{}'.format(content[0], content[1], content[2])
            ref_dataversion.append((content[0], cont))
        self.fields['Data'] = forms.ChoiceField(
            choices=ref_dataversion ) 