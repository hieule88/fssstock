from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from abnormaldetect.models import LogMessage
from abnormaldetect import cmdbackend, admin

from abnormalstock import settings

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
    #Init every time load page
    def __init__(self, *args, **kwargs):
        super(UserPredictionForm, self).__init__(*args, **kwargs)
        # set_dataversion = cmdbackend.task_para_list('VERROOTDESC')
        # CHANGE TO READ FROM DATABASE
        set_dataversion = ['POPULAR', 'VOLUMN', 'VOLATILITY', 'TREND', 'MOMENTUM', 'ADDFA', 'FULL']
        ref_dataversion = [(type, type) 
                    for i, type in enumerate(set_dataversion)]          
        self.fields['DataVersion'] = forms.ChoiceField(
            choices=ref_dataversion )      
    StationarityTest = forms.ChoiceField(label = "STATIONARITYTEST", choices  = admin.PARAMS['STATIONARITYTEST'])
    DiffTest = forms.ChoiceField(label = "DIFFTYPE", choices  = admin.PARAMS['DIFFTYPE'])
    ReplaceNan = forms.ChoiceField(label = "REPLACENAN", choices  = admin.PARAMS['REPLACENAN'])
    MinTradeDay = forms.ChoiceField(label = "MINTRADEDAY", choices  = admin.PARAMS['MINTRADEDAY'])

    Method = forms.ChoiceField(label = "METHOD", choices  = admin.PARAMS['METHOD'])
    MaxLag = forms.ChoiceField(label = "MAXLAG", choices  = admin.PARAMS['MAXLAG'])
    FeatureImpotance = forms.ChoiceField(label = "FEATUREIMPORTANCE", choices  = admin.PARAMS['FEATUREIMPORTANCE'])

    FIThreshold = forms.ChoiceField(label = "FITHRESHOLD", choices  = admin.PARAMS['FITHRESHOLD'])
    TopFeature = forms.ChoiceField(label = "TOPFEATURE", choices  = admin.PARAMS['TOPFEATURE'])
    ScoreConvert = forms.ChoiceField(label = "SCORECONVERT", choices  = admin.PARAMS['SCORECONVERT'])
    ScoreThreshold = forms.ChoiceField(label = "SCORETHRESHOLD", choices  = admin.PARAMS['SCORETHRESHOLD'])
    AbnormThreshold = forms.ChoiceField(label = "ABNORMTHRESHOLD", choices  = admin.PARAMS['ABNORMTHRESHOLD'])

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
    Age = forms.ChoiceField(choices  = settings.AGE_CHOICES)
    Capital = forms.ChoiceField(choices  = settings.CAPITAL_CHOICES)
    Year = forms.ChoiceField(choices  = settings.YEAR_CHOICES)
    KRISet = forms.ChoiceField(label = "KRI set", choices  = settings.KRISET_CHOICES)
    KRILoss = forms.ChoiceField(label = "KRI for loss prediction", choices  = settings.ESTIMATE_CHOICES)
    set_bobctc = cmdbackend.task_para_list('BOBCTC')
    ref_bobctc = [(row[0], row[1]) 
                for row in set_bobctc]    
    set_nganh = cmdbackend.task_para_list('NGANH')                
    ref_nganh = [(row[0], row[1]) 
                for row in set_nganh]    
    set_khuvuc = cmdbackend.task_para_list('KHUVUC')                
    ref_khuvuc = [(row[0], row[1]) 
                for row in set_khuvuc]    
    Category = forms.ChoiceField(choices  = ref_bobctc)
    Industry = forms.ChoiceField(choices  = ref_nganh)
    Area = forms.ChoiceField(choices  = ref_khuvuc)

class ModellingForm(forms.Form):
    v_group='DEF_MODELLING'
    #Init every time load page
    def __init__(self, *args, **kwargs):
        super(ModellingForm, self).__init__(*args, **kwargs)
        set_dataversion = cmdbackend.task_choosing('CLASSIFICATION')
        ref_dataversion = [(row[0], row[1]) 
                    for row in set_dataversion]            
        self.fields['Data'] = forms.ChoiceField(
            choices=ref_dataversion )  

class PreprocessingForm(forms.Form):
    v_group='DEF_PREPROCESSING'
    #Init every time load page
    def __init__(self, *args, **kwargs):
        super(PreprocessingForm, self).__init__(*args, **kwargs)
        set_dataversion = cmdbackend.task_choosing('INITDATASOURCE')
        ref_dataversion = [(row[0], row[1]) 
                    for row in set_dataversion]            
        self.fields['Data'] = forms.ChoiceField(
            choices=ref_dataversion )    

    #Parameter    
    set_balancedatamethod = cmdbackend.task_para_choice(v_group, 'BALANCEDATAMETHOD')
    ref_balancedatamethod = [(row[0], row[1]) 
                for row in set_balancedatamethod]    
    set_chooseonehotencoder = cmdbackend.task_para_choice(v_group, 'CHOOSEONEHOTENCODER')
    ref_chooseonehotencoder = [(row[0], row[1]) 
                for row in set_chooseonehotencoder]    
    set_n_components = cmdbackend.task_para_choice(v_group, 'N_COMPONENTS')
    ref_n_components = [(row[0], row[1]) 
                for row in set_n_components]    
    set_scaler= cmdbackend.task_para_choice(v_group, 'SCALER')
    ref_scaler = [(row[0], row[1]) 
                for row in set_scaler]    
    set_test_size = cmdbackend.task_para_choice(v_group, 'TEST_SIZE')    
    ref_test_size = [(row[0], row[1]) 
                for row in set_test_size]    
    set_categoricalimputer = cmdbackend.task_para_choice(v_group, 'CATEGORICALIMPUTER')    
    ref_categoricalimputer = [(row[0], row[1]) 
                for row in set_categoricalimputer]         
    set_categoricaloutliers = cmdbackend.task_para_choice(v_group, 'CATEGORICALOUTLIERS')    
    ref_categoricaloutliers = [(row[0], row[1]) 
                for row in set_categoricaloutliers]      
    set_combinecategorical = cmdbackend.task_para_choice(v_group, 'COMBINECATEGORICAL')    
    ref_combinecategorical = [(row[0], row[1]) 
                for row in set_combinecategorical]      
    set_numericimputer = cmdbackend.task_para_choice(v_group, 'NUMERICIMPUTER')    
    ref_numericimputer = [(row[0], row[1]) 
                for row in set_numericimputer]       
    set_numericoutliers = cmdbackend.task_para_choice(v_group, 'NUMERICOUTLIERS')    
    ref_numericoutliers = [(row[0], row[1]) 
                for row in set_numericoutliers]    
    set_numericoutliers = cmdbackend.task_para_choice(v_group, 'NUMERICOUTLIERS')    
    ref_numericoutliers = [(row[0], row[1]) 
                for row in set_numericoutliers]                                                                                
    set_n_folds = cmdbackend.task_para_choice(v_group, 'N_FOLDS')    
    ref_n_folds = [(row[0], row[1]) 
                for row in set_n_folds]  
    set_parameterforbalancedata = cmdbackend.task_para_choice(v_group, 'PARAMETERFORBALANCEDATA')    
    ref_parameterforbalancedata = [(row[0], row[1]) 
                for row in set_parameterforbalancedata]       
    set_pcalabelling = cmdbackend.task_para_choice(v_group, 'PCALABELLING')    
    ref_pcalabelling = [(row[0], row[1]) 
                for row in set_pcalabelling]        
    set_rateholdcol = cmdbackend.task_para_choice(v_group, 'RATEHOLDCOL')    
    ref_rateholdcol = [(row[0], row[1]) 
                for row in set_rateholdcol]      
    set_rateholdrow = cmdbackend.task_para_choice(v_group, 'RATEHOLDROW')    
    ref_rateholdrow = [(row[0], row[1]) 
                for row in set_rateholdrow]     
    set_svd_solver = cmdbackend.task_para_choice(v_group, 'SVD_SOLVER')    
    ref_svd_solver = [(row[0], row[1]) 
                for row in set_svd_solver]         
    set_whis_boxplot = cmdbackend.task_para_choice(v_group, 'WHIS_BOXPLOT')    
    ref_whis_boxplot = [(row[0], row[1]) 
                for row in set_whis_boxplot]                                                                        
    BALANCEDATAMETHOD= forms.ChoiceField(choices  = ref_balancedatamethod)
    CATEGORICALIMPUTER= forms.ChoiceField(choices  = ref_categoricalimputer)
    CATEGORICALOUTLIERS= forms.ChoiceField(choices  = ref_categoricaloutliers)
    CHOOSEONEHOTENCODER= forms.ChoiceField(choices  = ref_chooseonehotencoder)
    COMBINECATEGORICAL= forms.ChoiceField(choices  = ref_combinecategorical)
    NUMERICIMPUTER= forms.ChoiceField(choices  = ref_numericimputer)
    NUMERICOUTLIERS= forms.ChoiceField(choices  = ref_numericoutliers)
    N_COMPONENTS= forms.ChoiceField(choices  = ref_n_components)
    N_FOLDS= forms.ChoiceField(choices  = ref_n_folds)
    PARAMETERFORBALANCEDATA= forms.ChoiceField(choices  = ref_parameterforbalancedata)
    PCALABELLING= forms.ChoiceField(choices  = ref_pcalabelling)
    RATEHOLDCOL= forms.ChoiceField(choices  = ref_rateholdcol)
    RATEHOLDROW= forms.ChoiceField(choices  = ref_rateholdrow)
    SCALER= forms.ChoiceField(choices  = ref_scaler)
    SVD_SOLVER= forms.ChoiceField(choices  = ref_svd_solver)
    TEST_SIZE= forms.ChoiceField(choices  = ref_test_size)
    WHIS_BOXPLOT= forms.ChoiceField(choices  = ref_whis_boxplot)

class LabellingForm(forms.Form):
    v_group='DEF_LABELLING'
    #Init every time load page
    def __init__(self, *args, **kwargs):
        super(LabellingForm, self).__init__(*args, **kwargs)
        set_dataversion = cmdbackend.task_choosing('PREPROCESSING')
        ref_dataversion = [(row[0], row[1]) 
                    for row in set_dataversion]            
        self.fields['Data'] = forms.ChoiceField(
            choices=ref_dataversion )      
    #Parameter    
    set_bootstrap= cmdbackend.task_para_choice(v_group, 'BOOTSTRAP')
    ref_bootstrap = [(row[0], row[1]) 
                for row in set_bootstrap]  
    set_eps= cmdbackend.task_para_choice(v_group, 'EPS')
    ref_eps = [(row[0], row[1]) 
                for row in set_eps]  
    set_max_sample= cmdbackend.task_para_choice(v_group, 'MAX_SAMPLE')
    ref_max_sample = [(row[0], row[1]) 
                for row in set_max_sample]  
    set_min_samples= cmdbackend.task_para_choice(v_group, 'MIN_SAMPLES')
    ref_min_samples = [(row[0], row[1]) 
                for row in set_min_samples]  
    set_name_method= cmdbackend.task_para_choice(v_group, 'NAME_METHOD')
    ref_name_method = [(row[0], row[1]) 
                for row in set_name_method]  
    set_n_clusters= cmdbackend.task_para_choice(v_group, 'N_CLUSTERS')
    ref_n_clusters = [(row[0], row[1]) 
                for row in set_n_clusters]  
    set_n_estimators= cmdbackend.task_para_choice(v_group, 'N_ESTIMATORS')
    ref_n_estimators = [(row[0], row[1]) 
                for row in set_n_estimators]  
    set_n_neighbors= cmdbackend.task_para_choice(v_group, 'N_NEIGHBORS')
    ref_n_neighbors = [(row[0], row[1]) 
                for row in set_n_neighbors]  
    set_init= cmdbackend.task_para_choice(v_group, 'INIT')
    ref_init = [(row[0], row[1]) 
                for row in set_init]  
    set_max_iter= cmdbackend.task_para_choice(v_group, 'MAX_ITER')
    ref_max_iter = [(row[0], row[1]) 
                for row in set_max_iter]   
    set_metric= cmdbackend.task_para_choice(v_group, 'METRIC')
    ref_metric = [(row[0], row[1]) 
                for row in set_metric]    
    set_radiusthreshold= cmdbackend.task_para_choice(v_group, 'RADIUSTHRESHOLD')
    ref_radiusthreshold = [(row[0], row[1]) 
                for row in set_radiusthreshold]                                                                
    BOOTSTRAP= forms.ChoiceField(choices  = ref_bootstrap)
    EPS= forms.ChoiceField(choices  = ref_eps)
    INIT= forms.ChoiceField(choices  = ref_init)
    MAX_ITER= forms.ChoiceField(choices  = ref_max_iter)
    MAX_SAMPLE= forms.ChoiceField(choices  = ref_max_sample)
    METRIC= forms.ChoiceField(choices  = ref_metric)
    MIN_SAMPLES= forms.ChoiceField(choices  = ref_min_samples)
    NAME_METHOD= forms.ChoiceField(choices  = ref_name_method)
    N_CLUSTERS= forms.ChoiceField(choices  = ref_n_clusters)
    N_ESTIMATORS= forms.ChoiceField(choices  = ref_n_estimators)
    N_NEIGHBORS= forms.ChoiceField(choices  = ref_n_neighbors)
    RADIUSTHRESHOLD= forms.ChoiceField(choices  = ref_radiusthreshold)
    
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
        set_dataversion = cmdbackend.task_choosing('INITDATASOURCE')
        ref_dataversion = [(row[0], row[1]) 
                    for row in set_dataversion]            
        self.fields['Data'] = forms.ChoiceField(
            choices=ref_dataversion )  
    REFTTR = forms.ChoiceField(label = "Using TTR result", choices  = settings.TTR_CHOICES)