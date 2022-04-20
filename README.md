# Requirements:
* Setup cx_Oracle for python like Tax Fraud Detection app  
* Create folder for project, example: FSS_stock
# CMD for Setup :
* cd FSS_stock
* git clone https://github.com/hieule88/fssstock.git
* python -m venv stockenv
* cd stockenv/Script
* activate
* cd ../..
* cd fssstock
* pip install -r requirements.txt
# Now Run
* cd abnormalstock
* python manage.py runserver
* Open another CMD
* cd abnormalstock
* celery -A abnormalstock worker --time-limit 259200 --loglevel INFO --pool=solo --without-gossip --max-tasks-per-child=1 -n worker1@stock 
# RELATED TABLE
* ALLCODE2
* RES_LOG_CELERY
* RES_PREDICT_FRAUD_2
* RES_VAR_IMG
* RES_VARIABLE_SCORE_2
* RES_TOP_ABNORM
* TASKLOG_V2