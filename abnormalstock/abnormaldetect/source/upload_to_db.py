from backend import *
import cx_Oracle

def connect_data(): 
    dsn_tns = cx_Oracle.makedsn(BACKEND_IP_HOST_DB, BACKEND_PORT_DB, service_name=BACKEND_SERVICE_NAME_USE) # if needed, place an 'r' before any parameter in order to address special characters such as '\'.
    # need input user because ....
    conn = cx_Oracle.connect(user=r'RISK_USER', password=BACKEND_PASS_DB, dsn=dsn_tns) # if needed, place an 'r' before any parameter in order to address special characters such as '\'. For example, if your user name contains '\', you'll need to place 'r' before the user name: user=r'User Name'
    c = conn.cursor()
    #conn.commit()
    return c,conn

class Updator():
    def __init__(self, database, table):
        self.database = database
        self.table = table
        self.cur, self.conn= connect_data()
    def upload(self, data):
        pass

    def remove(self):
        pass
    
if __name__ == '__main__':
    cur, conn = connect_data()
    #insert hyperparams
    list_params = ['FITHRESHOLD', 'TOPFEATURE']
    val = ['0.1', '15']
    content = list_params
    en_content = 'LABELLING'
    order = 1

    for i in range(len(list_params)):
        # SQL = "INSERT INTO ALLCODE2 (CDUSER, CDTYPE, CDNAME, CDVAL, CDCONTENT, EN_CDCONTENT, LSTODR) VALUES ('H','SP', 'MINTRADEDAY','60' , 'MINTRADEDAY', 'DEF_PREPROCESSING', 1)"
        sql_insert = "INSERT INTO ALLCODE2 (CDUSER, CDTYPE, CDNAME, CDVAL, CDCONTENT, EN_CDCONTENT, LSTODR) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', {}) "\
                    .format('H','SP',list_params[i] ,val[i] , content[i], en_content, order)

        c0 = cur.execute(sql_insert)
    conn.commit()
    print('DONE')


