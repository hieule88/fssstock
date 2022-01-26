import string
from celery import shared_task
from abnormaldetect import cmdbackend
from .admin import *
import traceback
import sys
import os
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
#get_ipython().run_line_magic('matplotlib', 'inline')
import numpy as np
import pandas as pd
import statsmodels.api as sm
import numpy as np
from scipy.stats import rankdata
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm 
from sklearn import metrics
from sklearn.metrics import classification_report
import seaborn as sns
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 100)
#from luminol.anomaly_detector import AnomalyDetector
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.covariance import EllipticEnvelope
#from pyemma import msm # not available on Kaggle Kernel
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.model_selection import GridSearchCV
#from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler
from sklearn.compose import ColumnTransformer
from collections import Counter
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix,precision_recall_fscore_support,accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.cluster import DBSCAN
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import silhouette_score
#import cv2
import datetime
from io import StringIO,BytesIO
import PIL, PIL.Image
# install pickle-mixin
import pickle
import time
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, precision_score, recall_score,f1_score,roc_auc_score,confusion_matrix, classification_report
import cx_Oracle
from abnormaldetect.admin import *

import string
from celery import shared_task
import traceback
import sys

# IMPORT MODEL TO RUN HERE

@shared_task
def runETL(v_category, v_year):
    #Execute ETL
    v_return = cmdbackend.task_run_etl(v_category, v_year)
    return v_return

@shared_task
def runtask(p_taskid, p_taskcd):
    #Mp_taskcd: MODELLING or AUTOMODELLING
    #try:
        code_score_card.RUN_ALL_MODEL(p_taskid)
    #except Exception as e:
     #   p_status='E'
      #  p_logontent=str(e)
       # cmdbackend.task_result_feedback(p_taskid, p_status, p_logontent)
        return p_taskid

@shared_task
def taskcmdcelery(cmdtype, cmdcontent):
   cmdbackend.task_command_exec_main(cmdtype, cmdcontent)