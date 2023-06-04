import json, sys, time
from socket import timeout
from app import app,db, tz, phy_engine
from flask import request, make_response, Response
import gzip
from flask_jsonpify import jsonify
import pandas as pd
from datetime import datetime
import time
from app.models.inventory_models import FAILED_DEVICES_EDN_IPAM, FAILED_DEVICES_IGW_IPAM
from app.middleware import token_required


def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%d-%m-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

  ## IPAM Started ##

@app.route("/getAllEdnIpamFailedDevices", methods = ['GET'])
@token_required
def GetAllEdnIpamFailedDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednIpamFailedObjList=[]
        ednIpamFailedObjs = db.session.execute('SELECT * FROM failed_devices_edn_ipam WHERE date = (SELECT max(date) FROM failed_devices_edn_ipam)')
        
        for ednIpamFailedObj in ednIpamFailedObjs:
            ednIpamFailedDataDict= {}
            ednIpamFailedDataDict['edn_ipam_failed_id']= ednIpamFailedObj[0]
            ednIpamFailedDataDict['ip_address'] = ednIpamFailedObj[1]
            ednIpamFailedDataDict['device_id'] = ednIpamFailedObj[2]
            ednIpamFailedDataDict['reason'] = ednIpamFailedObj[3]
            ednIpamFailedDataDict['date'] = FormatDate(ednIpamFailedObj[4])
            ednIpamFailedObjList.append(ednIpamFailedDataDict)

        content = gzip.compress(json.dumps(ednIpamFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllEdnIpamFailedDevicesDates',methods=['GET'])
@token_required
def GetAllEdnIpamFailedDevicesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(date) from failed_devices_edn_ipam ORDER BY date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getEdnIpamFailedDevicesByDate", methods = ['POST'])
@token_required
def GetEdnIpamFailedDevicesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednIpamFailedObjList=[]
        
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

        ednIpamFailedObjs = db.session.execute(f"SELECT * FROM failed_devices_edn_ipam WHERE date = '{current_time}' ")
        
        for ednIpamFailedObj in ednIpamFailedObjs:
            ednIpamFailedDataDict= {}
            ednIpamFailedDataDict['edn_ipam_failed_id']= ednIpamFailedObj[0]
            ednIpamFailedDataDict['ip_address'] = ednIpamFailedObj[1]
            ednIpamFailedDataDict['device_id'] = ednIpamFailedObj[2]
            ednIpamFailedDataDict['reason'] = ednIpamFailedObj[3]
            ednIpamFailedDataDict['date'] = FormatDate(ednIpamFailedObj[4])
            ednIpamFailedObjList.append(ednIpamFailedDataDict)

        content = gzip.compress(json.dumps(ednIpamFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllIgwIpamFailedDevices", methods = ['GET'])
@token_required
def GetAllIgwIpamFailedDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwIpamFailedObjList=[]
        igwIpamFailedObjs = db.session.execute('SELECT * FROM failed_devices_igw_ipam WHERE date = (SELECT max(date) FROM failed_devices_igw_ipam)')
        
        for igwIpamFailedObj in igwIpamFailedObjs:
            igwIpamFailedDataDict= {}
            igwIpamFailedDataDict['igw_ipam_failed_id']= igwIpamFailedObj[0]
            igwIpamFailedDataDict['ip_address'] = igwIpamFailedObj[1]
            igwIpamFailedDataDict['device_id'] = igwIpamFailedObj[2]
            igwIpamFailedDataDict['reason'] = igwIpamFailedObj[3]
            igwIpamFailedDataDict['date'] = FormatDate(igwIpamFailedObj[4])
            igwIpamFailedObjList.append(igwIpamFailedDataDict)

        content = gzip.compress(json.dumps(igwIpamFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllIgwIpamFailedDevicesDates',methods=['GET'])
@token_required
def GetAllIgwIpamFailedDevicesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(date) from failed_devices_igw_ipam ORDER BY date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getIgwIpamFailedDevicesByDate", methods = ['POST'])
@token_required
def GetIgwIpamFailedDevicesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwIpamFailedObjList=[]
        
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

        igwIpamFailedObjs = db.session.execute(f"SELECT * FROM failed_devices_igw_ipam WHERE date = '{current_time}' ")
        
        for igwIpamFailedObj in igwIpamFailedObjs:
            igwIpamFailedDataDict= {}
            igwIpamFailedDataDict['igw_ipam_failed_id']= igwIpamFailedObj[0]
            igwIpamFailedDataDict['ip_address'] = igwIpamFailedObj[1]
            igwIpamFailedDataDict['device_id'] = igwIpamFailedObj[2]
            igwIpamFailedDataDict['reason'] = igwIpamFailedObj[3]
            igwIpamFailedDataDict['date'] = FormatDate(igwIpamFailedObj[4])
            igwIpamFailedObjList.append(igwIpamFailedDataDict)

        content = gzip.compress(json.dumps(igwIpamFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


    ## IPAM Finished ##


## DC Capacity Started ##

@app.route("/getAllDcCapacityFailedDevices", methods = ['GET'])
@token_required
def GetAllEdnFailedDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednDcCapacityFailedObjList=[]
        ednDcCapacityFailedObjs = db.session.execute('SELECT * FROM failed_devices_edn_dc_capacity WHERE date = (SELECT max(date) FROM failed_devices_edn_dc_capacity)')
        
        for ednDcCapacityFailedObj in ednDcCapacityFailedObjs:
            ednDcCapacityFailedDataDict= {}
            ednDcCapacityFailedDataDict['edn_dc_capacity_failed_id']= ednDcCapacityFailedObj[0]
            ednDcCapacityFailedDataDict['ip_address'] = ednDcCapacityFailedObj[1]
            ednDcCapacityFailedDataDict['device_id'] = ednDcCapacityFailedObj[2]
            ednDcCapacityFailedDataDict['reason'] = ednDcCapacityFailedObj[3]
            ednDcCapacityFailedDataDict['date'] = FormatDate(ednDcCapacityFailedObj[4])
            ednDcCapacityFailedObjList.append(ednDcCapacityFailedDataDict)

        content = gzip.compress(json.dumps(ednDcCapacityFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllEdnDcCapacityFailedDevicesDates',methods=['GET'])
@token_required
def GetAllEdnFailedDevicesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(date) from failed_devices_edn_dc_capacity ORDER BY date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getEdnDcCapacityFailedDevicesByDate", methods = ['POST'])
@token_required
def GetEdnFailedDevicesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednDcCapacityFailedObjList=[]
        
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

        ednDcCapacityFailedObjs = db.session.execute(f"SELECT * FROM failed_devices_edn_dc_capacity WHERE date = '{current_time}' ")
        
        for ednDcCapacityFailedObj in ednDcCapacityFailedObjs:
            ednDcCapacityFailedDataDict= {}
            ednDcCapacityFailedDataDict['edn_dc_capacity_failed_id']= ednDcCapacityFailedObj[0]
            ednDcCapacityFailedDataDict['ip_address'] = ednDcCapacityFailedObj[1]
            ednDcCapacityFailedDataDict['device_id'] = ednDcCapacityFailedObj[2]
            ednDcCapacityFailedDataDict['reason'] = ednDcCapacityFailedObj[3]
            ednDcCapacityFailedDataDict['date'] = FormatDate(ednDcCapacityFailedObj[4])
            ednDcCapacityFailedObjList.append(ednDcCapacityFailedDataDict)

        content = gzip.compress(json.dumps(ednDcCapacityFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllIgwDcCapacityFailedDevices", methods = ['GET'])
@token_required
def GetAllIgwFailedDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwDcCapacityFailedObjList=[]
        igwDcCapacityFailedObjs = db.session.execute('SELECT * FROM failed_devices_igw_dc_capacity WHERE date = (SELECT max(date) FROM failed_devices_igw_dc_capacity)')
        
        for igwDcCapacityFailedObj in igwDcCapacityFailedObjs:
            igwDcCapacityFailedDataDict= {}
            igwDcCapacityFailedDataDict['igw_dc_capacity_failed_id']= igwDcCapacityFailedObj[0]
            igwDcCapacityFailedDataDict['ip_address'] = igwDcCapacityFailedObj[1]
            igwDcCapacityFailedDataDict['device_id'] = igwDcCapacityFailedObj[2]
            igwDcCapacityFailedDataDict['reason'] = igwDcCapacityFailedObj[3]
            igwDcCapacityFailedDataDict['date'] = FormatDate(igwDcCapacityFailedObj[4])
            igwDcCapacityFailedObjList.append(igwDcCapacityFailedDataDict)

        content = gzip.compress(json.dumps(igwDcCapacityFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllIgwDcCapacityFailedDevicesDates',methods=['GET'])
@token_required
def GetAllIgwFailedDevicesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(date) from failed_devices_igw_dc_capacity ORDER BY date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getIgwDcCapacityFailedDevicesByDate", methods = ['POST'])
@token_required
def GetIgwFailedDevicesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwDcCapacityFailedObjList=[]
        
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

        igwDcCapacityFailedObjs = db.session.execute(f"SELECT * FROM failed_devices_igw_dc_capacity WHERE date = '{current_time}' ")
        
        for igwDcCapacityFailedObj in igwDcCapacityFailedObjs:
            igwDcCapacityFailedDataDict= {}
            igwDcCapacityFailedDataDict['igw_dc_capacity_failed_id']= igwDcCapacityFailedObj[0]
            igwDcCapacityFailedDataDict['ip_address'] = igwDcCapacityFailedObj[1]
            igwDcCapacityFailedDataDict['device_id'] = igwDcCapacityFailedObj[2]
            igwDcCapacityFailedDataDict['reason'] = igwDcCapacityFailedObj[3]
            igwDcCapacityFailedDataDict['date'] = FormatDate(igwDcCapacityFailedObj[4])
            igwDcCapacityFailedObjList.append(igwDcCapacityFailedDataDict)

        content = gzip.compress(json.dumps(igwDcCapacityFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


## DC Capacity Finished ##


## Access Points Started ##

@app.route("/getAllAccessPointsFailedDevices", methods = ['GET'])
@token_required
def GetAllFailedDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        AccessPointsFailedObjList=[]
        AccessPointsFailedObjs = db.session.execute('SELECT * FROM failed_devices_access_points WHERE date = (SELECT max(date) FROM failed_devices_access_points)')
        
        for AccessPointsFailedObj in AccessPointsFailedObjs:
            AccessPointsFailedDataDict= {}
            AccessPointsFailedDataDict['_access_points_failed_id']= AccessPointsFailedObj[0]
            AccessPointsFailedDataDict['ip_address'] = AccessPointsFailedObj[1]
            AccessPointsFailedDataDict['device_id'] = AccessPointsFailedObj[2]
            AccessPointsFailedDataDict['reason'] = AccessPointsFailedObj[3]
            AccessPointsFailedDataDict['date'] = FormatDate(AccessPointsFailedObj[4])
            AccessPointsFailedObjList.append(AccessPointsFailedDataDict)

        content = gzip.compress(json.dumps(AccessPointsFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllAccessPointsFailedDevicesDates',methods=['GET'])
@token_required
def GetAllFailedDevicesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(date) from failed_devices_access_points ORDER BY date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getAccessPointsFailedDevicesByDate", methods = ['POST'])
@token_required
def GetFailedDevicesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        AccessPointsFailedObjList=[]
        
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

        AccessPointsFailedObjs = db.session.execute(f"SELECT * FROM failed_devices_access_points WHERE date = '{current_time}' ")
        
        for AccessPointsFailedObj in AccessPointsFailedObjs:
            AccessPointsFailedDataDict= {}
            AccessPointsFailedDataDict['_access_points_failed_id']= AccessPointsFailedObj[0]
            AccessPointsFailedDataDict['ip_address'] = AccessPointsFailedObj[1]
            AccessPointsFailedDataDict['device_id'] = AccessPointsFailedObj[2]
            AccessPointsFailedDataDict['reason'] = AccessPointsFailedObj[3]
            AccessPointsFailedDataDict['date'] = FormatDate(AccessPointsFailedObj[4])
            AccessPointsFailedObjList.append(AccessPointsFailedDataDict)

        content = gzip.compress(json.dumps(AccessPointsFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

## Access Points Finished ##


## LLDP  Started ##

@app.route("/getAllEdnLLDPFailedDevices", methods = ['GET'])
@token_required
def GetAllEdnLLDPFailedDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        pmFailedObjs = db.session.execute('SELECT * FROM failed_devices_edn_lldp WHERE date = (SELECT max(date) FROM failed_devices_edn_lldp)')
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_edn_lldp_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllEdnLLDPFailedDevicesDates',methods=['GET'])
@token_required
def GetAllEdnLLDPFailedDevicesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(date) from failed_devices_edn_lldp ORDER BY date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getEdnLLDPFailedDevicesByDate", methods = ['POST'])
@token_required
def GetFailedEdnLLDPDevicesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        EdnLldpFailedObjList=[]
        
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

        pmFailedObjs = db.session.execute(f"SELECT * FROM failed_devices_edn_lldp WHERE date = '{current_time}' ")
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_edn_lldp_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            EdnLldpFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(EdnLldpFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

## PM LLDP Finished ##


## IGW LLDP  Started ##

@app.route("/getAllIgwLLDPFailedDevices", methods = ['GET'])
@token_required
def GetAllIgwLLDPFailedDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        pmFailedObjs = db.session.execute('SELECT * FROM failed_devices_igw_lldp WHERE date = (SELECT max(date) FROM failed_devices_igw_lldp)')
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_igw_lldp_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllIgwLLDPFailedDevicesDates',methods=['GET'])
@token_required
def GetAllIgwLLDPFailedDevicesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(date) from failed_devices_igw_lldp ORDER BY date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getIgwLLDPFailedDevicesByDate", methods = ['POST'])
@token_required
def GetFailedIgwLLDPDevicesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        IgwLldpFailedObjList=[]
        
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

        pmFailedObjs = db.session.execute(f"SELECT * FROM failed_devices_igw_lldp WHERE date = '{current_time}' ")
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_igw_lldp_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            IgwLldpFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(IgwLldpFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

## PM LLDP Finished ##



## IGW CDP  Started ##

@app.route("/getAllIgwCDPLegacyFailedDevices", methods = ['GET'])
@token_required
def GetAllIgwCDPFailedDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        pmFailedObjs = db.session.execute('SELECT * FROM failed_devices_igw_cdp WHERE date = (SELECT max(date) FROM failed_devices_igw_cdp)')
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_igw_cdp_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllIgwCDPLegacyFailedDevicesDates',methods=['GET'])
@token_required
def GetAllIgwCDPFailedDevicesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(date) from failed_devices_igw_cdp ORDER BY date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getIgwCDPLegacyFailedDevicesByDate", methods = ['POST'])
@token_required
def GetFailedIgwCDPDevicesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

        pmFailedObjs = db.session.execute(f"SELECT * FROM failed_devices_igw_cdp WHERE date = '{current_time}' ")
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_igw_cdp_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

## PM CDP Finished ##


## EDN CDP  Started ##

@app.route("/getAllEdnCDPLegacyFailedDevices", methods = ['GET'])
@token_required
def GetAllEdnCDPFailedDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        pmFailedObjs = db.session.execute('SELECT * FROM failed_devices_edn_cdp WHERE date = (SELECT max(date) FROM failed_devices_edn_cdp)')
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_edn_cdp_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllEdnCDPLegacyFailedDevicesDates',methods=['GET'])
@token_required
def GetAllEdnCDPFailedDevicesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(date) from failed_devices_edn_cdp ORDER BY date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getEdnCDPLegacyFailedDevicesByDate", methods = ['POST'])
@token_required
def GetFailedEdnCDPDevicesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

        pmFailedObjs = db.session.execute(f"SELECT * FROM failed_devices_edn_cdp WHERE date = '{current_time}' ")
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_edn_cdp_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

## PM CDP Finished ##



## EDN MAC  Started ##

@app.route("/getAllEdnMACFailedDevices", methods = ['GET'])
@token_required
def GetAllEdnMACFailedDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        pmFailedObjs = db.session.execute('SELECT * FROM failed_devices_edn_mac WHERE date = (SELECT max(date) FROM failed_devices_edn_mac)')
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_edn_mac_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllEdnMACFailedDevicesDates',methods=['GET'])
@token_required
def GetAllEdnMACFailedDevicesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(date) from failed_devices_edn_mac ORDER BY date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getEdnMACFailedDevicesByDate", methods = ['POST'])
@token_required
def GetFailedEdnMACDevicesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

        pmFailedObjs = db.session.execute(f"SELECT * FROM failed_devices_edn_mac WHERE date = '{current_time}' ")
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_edn_mac_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

## PM MAC Finished ##

## IGW MAC  Started ##

@app.route("/getAllIgwMacFailedDevices", methods = ['GET'])
@token_required
def GetAllIgwMACFailedDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        pmFailedObjs = db.session.execute('SELECT * FROM failed_devices_igw_mac WHERE date = (SELECT max(date) FROM failed_devices_igw_mac)')
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_igw_mac_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllIgwMacFailedDevicesDates',methods=['GET'])
@token_required
def GetAllIgwMACFailedDevicesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(date) from failed_devices_igw_mac ORDER BY date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getIgwMacFailedDevicesByDate", methods = ['POST'])
@token_required
def GetFailedIgwMACDevicesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

        pmFailedObjs = db.session.execute(f"SELECT * FROM failed_devices_igw_mac WHERE date = '{current_time}' ")
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_igw_mac_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

## PM MAC Finished ##


## EDN FIREWALL ARP  Started ##

@app.route("/getAllEdnFirewallARPFailedDevices", methods = ['GET'])
@token_required
def GetAllEdnFIREWALLARPFailedDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        pmFailedObjs = db.session.execute('SELECT * FROM failed_devices_edn_firewall WHERE date = (SELECT max(date) FROM failed_devices_edn_firewall)')
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_edn_firewall_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllEdnFirewallARPFailedDevicesDates',methods=['GET'])
@token_required
def GetAllEdnFIREWALLARPFailedDevicesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(date) from failed_devices_edn_firewall ORDER BY date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getEdnFirewallARPFailedDevicesByDate", methods = ['POST'])
@token_required
def GetFailedEdnFIREWALLARPDevicesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

        pmFailedObjs = db.session.execute(f"SELECT * FROM failed_devices_edn_firewall WHERE date = '{current_time}' ")
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_edn_firewall_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

## PM FIREWALL ARP Finished ##



## EDN EXCHANGE  Started ##

@app.route("/getAllEdnExchangeFailedDevices", methods = ['GET'])
@token_required
def GetAllEdnExchangeFailedDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        pmFailedObjs = db.session.execute('SELECT * FROM failed_devices_edn_exchange WHERE date = (SELECT max(date) FROM failed_devices_edn_exchange)')
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_edn_exchange_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllEdnExchangeFailedDevicesDates',methods=['GET'])
@token_required
def GetAllEdnExchangeFailedDevicesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(date) from failed_devices_edn_exchange ORDER BY date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getEdnExchangeFailedDevicesByDate", methods = ['POST'])
@token_required
def GetFailedEdnExchangeDevicesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

        pmFailedObjs = db.session.execute(f"SELECT * FROM failed_devices_edn_exchange WHERE date = '{current_time}' ")
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_edn_exchange_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

## PM EXCHANGE Finished ##



## IPT ENDPOINTS  Started ##

@app.route("/getAllIptEndpointsFailedDevices", methods = ['GET'])
@token_required
def GetAllIptEndpointsFailedDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        pmFailedObjs = db.session.execute('SELECT * FROM failed_devices_ipt_endpoints WHERE date = (SELECT max(date) FROM failed_devices_ipt_endpoints)')
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_ipt_endpoints_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getIptEndpointsFailedDevicesDates',methods=['GET'])
@token_required
def GetAllIptEndpointsFailedDevicesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(date) from failed_devices_ipt_endpoints ORDER BY date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getIptEndpointsFailedDevicesByDate", methods = ['POST'])
@token_required
def GetFailedIptEndpointsDevicesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

        pmFailedObjs = db.session.execute(f"SELECT * FROM failed_devices_ipt_endpoints WHERE date = '{current_time}' ")
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_ipt_endpoints_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

## IPT ENDPOINTS Finished ##

## F5   Started ##

@app.route("/getAllF5FailedDevices", methods = ['GET'])
@token_required
def GetAllF5FailedDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        pmFailedObjs = db.session.execute('SELECT * FROM failed_devices_f5 WHERE date = (SELECT max(date) FROM failed_devices_f5)')
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_f5_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllF5FailedDevicesDates',methods=['GET'])
@token_required
def GetAllF5FailedDevicesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(date) from failed_devices_f5 ORDER BY date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getF5FailedDevicesByDate", methods = ['POST'])
@token_required
def FetF5FailedDevicesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        pmFailedObjList=[]
        
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

        pmFailedObjs = db.session.execute(f"SELECT * FROM failed_devices_f5 WHERE date = '{current_time}' ")
        
        for pmFailedObj in pmFailedObjs:
            pmFailedDataDict= {}
            pmFailedDataDict['_f5_failed_id']= pmFailedObj[0]
            pmFailedDataDict['ip_address'] = pmFailedObj[1]
            pmFailedDataDict['device_id'] = pmFailedObj[2]
            pmFailedDataDict['reason'] = pmFailedObj[3]
            pmFailedDataDict['date'] = FormatDate(pmFailedObj[4])
            pmFailedObjList.append(pmFailedDataDict)

        content = gzip.compress(json.dumps(pmFailedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
