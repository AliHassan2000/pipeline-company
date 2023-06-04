import imp
import json, sys, time
from socket import timeout
import traceback
from app import app,db, tz, phy_engine
from flask import request, make_response, Response
import gzip
from flask_jsonpify import jsonify
import pandas as pd
from datetime import datetime
import time
from app.models.inventory_models import INVENTORY_SCRIPTS_STATUS
from app.middleware import token_required
from app.f5.f5 import F5


def InsertData(obj):
    #add data to db
    try:        
        db.session.rollback()
        db.session.add(obj)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong in Database Insertion {e}", file=sys.stderr)

    return True
    

def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%d-%m-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result
@app.route("/fetchF5", methods = ['GET'])
@token_required
def FetchF5(user_data):  
    if True:
        try:
            FetchF5Func(user_data)
            return jsonify("Success"), 200
            
        except Exception as e:
            traceback.print_exc()
            print(f"Exception occured when fetching F5 {e}", file=sys.stderr)
            return jsonify("Failure"), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchF5Func(user_data):
    f5List = []
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query_string = "select device_id, ne_ip_address, sw_type, site_id from seed_table where sw_type='F5' and (device_id LIKE '%ELTM%' OR device_id LIKE '%EVMP%') and operation_status='Production';" # and ne_ip_address='192.168.30.195'
    result = db.session.execute(query_string)
    
    for row in result:
        f5Dict = {}
 
        f5Dict['device_id'] = row[0]
        f5Dict['ip_address'] = row[1]
        f5Dict['sw_type'] = row[2]
        f5Dict['site_id'] = row[3]
        f5Dict['user_id'] = user_data['user_id']
        
        f5Dict['time']= current_time
        
        f5List.append(f5Dict)
    
    try:
        f5= F5()
    except Exception as e:
        traceback.print_exc()
        print(f"Exception Occured In  F5 {e}", file=sys.stderr)
    #Update Script Status
    
    f5Status = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script=="F5").first()

    try:
        f5Status.script = "F5"
        f5Status.status = "Running"
        f5Status.creation_date= current_time
        f5Status.modification_date= current_time
        
        db.session.add(f5Status)
        db.session.commit() 
        #InsertData(f5Status)
    
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        print(f"Error while updating script status {e}", file=sys.stderr)

    try:
        
        f5.getF5(f5List)
        

    except Exception as e:
        print(e, file=sys.stderr)
   
    try:
        f5Status.script = "F5"
        f5Status.status = "Completed"
        f5Status.creation_date= current_time
        f5Status.modification_date= current_time
        db.session.add(f5Status)
        db.session.commit() 
    
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        print(f"Error while updating script status {e}", file=sys.stderr)

@app.route("/getF5FetchStatus", methods = ['GET'])
@token_required
def GetF5FetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        f5={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        f5Status = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "F5").first()
        if f5Status:
            script_status= f5Status.status
            script_modifiation_date= str(f5Status.modification_date)
        f5["fetch_status"] = script_status
        f5["fetch_date"]= script_modifiation_date

        content = gzip.compress(json.dumps(f5).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllF5", methods = ['GET'])
@token_required
def GetAllF5(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        f5ObjList=[]
        f5Objs = db.session.execute('SELECT * FROM f5 WHERE creation_date = (SELECT max(creation_date) FROM f5)')
        
        for f5Obj in f5Objs:
            f5DataDict= {}
            f5DataDict['f5_id']= f5Obj[0]
            f5DataDict['ip_address'] = f5Obj[1]
            f5DataDict['device_id'] = f5Obj[2]
            f5DataDict['site_id'] = f5Obj[3]
            f5DataDict['vserver_name'] = f5Obj[4]
            f5DataDict['vip'] = f5Obj[5]
            f5DataDict['pool_name'] = f5Obj[6]
            f5DataDict['pool_member'] = f5Obj[7]
            f5DataDict['node'] = f5Obj[8]
            f5DataDict['service_port'] = f5Obj[9]
            f5DataDict['monitor_value'] = f5Obj[10]
            f5DataDict['monitor_status'] = f5Obj[11]
            f5DataDict['lb_method'] = f5Obj[12]
            f5DataDict['ssl_profile'] = f5Obj[13]
            f5DataDict['monitor_name'] = f5Obj[14]
            f5DataDict['creation_date'] = str(f5Obj[15])
            f5DataDict['modification_date'] = str(f5Obj[16])
            f5DataDict['created_by']=  f5Obj[17]
            f5DataDict['modified_by']=  f5Obj[18]
            f5DataDict['description']=  f5Obj[19]
            f5ObjList.append(f5DataDict)

        content = gzip.compress(json.dumps(f5ObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllF5Dates',methods=['GET'])
@token_required
def GetAllF5Dates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from f5 ORDER BY creation_date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getAllF5ByDate", methods = ['POST'])
@token_required
def GetAllF5ByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        f5ObjList=[]

        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)

        f5Objs = db.session.execute(f"SELECT * FROM f5 WHERE creation_date = '{current_time}' ")
        
        for f5Obj in f5Objs:
            f5DataDict= {}
            f5DataDict['f5_id']= f5Obj[0]
            f5DataDict['ip_address'] = f5Obj[1]
            f5DataDict['device_id'] = f5Obj[2]
            f5DataDict['site_id'] = f5Obj[3]
            f5DataDict['vserver_name'] = f5Obj[4]
            f5DataDict['vip'] = f5Obj[5]
            f5DataDict['pool_name'] = f5Obj[6]
            f5DataDict['pool_member'] = f5Obj[7]
            f5DataDict['node'] = f5Obj[8]
            f5DataDict['service_port'] = f5Obj[9]
            f5DataDict['monitor_value'] = f5Obj[10]
            f5DataDict['monitor_status'] = f5Obj[11]
            f5DataDict['lb_method'] = f5Obj[12]
            f5DataDict['ssl_profile'] = f5Obj[13]
            f5DataDict['monitor_name'] = f5Obj[14]
            f5DataDict['creation_date'] = str(f5Obj[15])
            f5DataDict['modification_date'] = str(f5Obj[16])
            f5DataDict['created_by']=  f5Obj[17]
            f5DataDict['modified_by']=  f5Obj[18]
            f5DataDict['description']=  f5Obj[19]
            f5ObjList.append(f5DataDict)

        content = gzip.compress(json.dumps(f5ObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

