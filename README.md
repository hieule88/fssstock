# Require:
* Setup cx_Oracle for python like Tax Fraud Detection app  
* Download all stocks dataset from 01/01/2019 to 01/01/2021 via ggdrive link below to reduce loading data time from DB: 
https://drive.google.com/drive/folders/1uAiCKAaxvi0QKL9RjuSOAiAuzqZzqhJQ?usp=sharing
* The file names: TradingHistory.csv
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
# Some changes for the path to TradingHistory.csv:
* In the file abnormalstock/abnormaldetect/source/main.py , line 60 , change the path to the TradingHistory.csv's path
# Now Run
* cd abnormalstock
* python manage.py runserver
