from celery import shared_task
from abnormaldetect import cmdbackend
from .admin import *
import os
import pandas as pd 
import matplotlib.pyplot as plt
#get_ipython().run_line_magic('matplotlib', 'inline')
import pandas as pd
import statsmodels.api as sm
import numpy as np
import statsmodels.api as sm 
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 100)
#from luminol.anomaly_detector import AnomalyDetector
#from sklearn.pipeline import Pipeline

#import cv2
import datetime
import PIL, PIL.Image
# install pickle-mixin
from datetime import datetime as dt
from abnormaldetect.admin import *
from abnormaldetect.source.main import RUNALLMODEL
from celery import shared_task, Celery
import celery
from abnormalstock import settings
import django
# IMPORT MODEL TO RUN HERE

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abnormalstock.settings')
django.setup()

@shared_task
def runETL(v_category, v_year):
    #Execute ETL
    v_return = cmdbackend.task_run_etl(v_category, v_year)
    return v_return

@shared_task
def runtask(p_taskid, ref_id, hyperparams):
    #Mp_taskcd: MODELLING or AUTOMODELLING
    try:
        results = RUNALLMODEL(p_taskid, ref_id, hyperparams)
        return results
    except Exception as e:
        raise

@shared_task
def taskcmdcelery(cmdtype, cmdcontent):
   cmdbackend.task_command_exec_main(cmdtype, cmdcontent)

app = Celery(broker='amqp://', backend= 'rpc://')