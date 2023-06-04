from ast import For
import json, sys, time
from socket import timeout
from app import app,db, tz, phy_engine
from flask import request, make_response, Response
import gzip
from flask_jsonpify import jsonify
import pandas as pd
from datetime import datetime
import time
from app.models.inventory_models import Seed, EDN_IPAM_TABLE, IGW_IPAM_TABLE, SOC_IPAM_TABLE, INVENTORY_SCRIPTS_STATUS
from app.middleware import token_required
from app.ipam_scripts.ipam import IPAM
from app.models.inventory_models import Phy_Table

def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%d-%m-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

def InsertData(obj):
    #add data to db
    db.session.add(obj)
    db.session.commit()
    return True

@app.route("/fetchEdnIpam", methods = ['GET'])
@token_required
def FetchEdnIpam(user_data):  
    if True:
        try:
            FetchEdnIpamFunc(user_data)
            return jsonify("Success"), 200
            
        except Exception as e:
            print(f"Exception occured when fetching Ipam {e}", file=sys.stderr)
            return jsonify("Failure"), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchEdnIpamFunc(user_data):
    ednIpamList = []
    ednIpamList2 = []
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query_string = "select site_id, device_id,ne_ip_address,sw_type,site_type from seed_table where  operation_status='Production' and (cisco_domain = 'EDN-NET' or cisco_domain = 'EDN-SYS') and (sw_type='IOS' or sw_type='IOS-XE' or sw_type='IOS-XR' or sw_type='NX-OS' or sw_type='ACI-LEAF' or sw_type='F5');"
    result = db.session.execute(query_string)
    
    query_string
    for row in result:
        ednIpamDict = {}
        ednIpamDict['site_id'] = row[0]
        
        siteObj = Phy_Table.query.filter_by(site_id=row[0]).first()
        if siteObj:
            ednIpamDict['region']= siteObj.region 
        else:
            ednIpamDict['region']= '' 

        ednIpamDict['device_id'] = row[1]
        ednIpamDict['mgmt_ip'] = row[2]
        ednIpamDict['sw_type'] = row[3]
        ednIpamDict['site_type'] = row[4]
        ednIpamDict['type'] = 'EDN'
        ednIpamDict['time'] = current_time
        ednIpamDict['user_id']= user_data['user_id']
        
        ednIpamList.append(ednIpamDict)
      
    try:
        ipam= IPAM()
    except Exception as e:
        print("Exception Occured In EDN IPAM", file=sys.stderr)
    #Update Script Status
    
    ednIpamStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script=="EDN-IPAM").first()

    try:
        ednIpamStatus.script = "EDN-IPAM"
        ednIpamStatus.status = "Running"
        ednIpamStatus.creation_date= current_time
        ednIpamStatus.modification_date= current_time
        
        InsertData(ednIpamStatus)
    
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    try:
        ipam.getIpam(ednIpamList)
    except Exception as e:
        print(e, file=sys.stderr)
   
    try:
        ednIpamStatus.script = "EDN-IPAM"
        ednIpamStatus.status = "Completed"
        ednIpamStatus.creation_date= current_time
        ednIpamStatus.modification_date= current_time
        db.session.add(ednIpamStatus)
        db.session.commit() 
    
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)


@app.route("/getEdnIpamScriptStatus", methods = ['GET'])
@token_required
def GetEdnIpamFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednIpam={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        ednIpamStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "EDN-IPAM").first()
        if ednIpamStatus:
            script_status= ednIpamStatus.status
            script_modifiation_date= str(ednIpamStatus.modification_date)
        ednIpam["fetch_status"] = script_status
        ednIpam["fetch_date"]= script_modifiation_date

        content = gzip.compress(json.dumps(ednIpam).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route("/getAllEdnIpam", methods = ['GET'])
@token_required
def GetAllEdnIpam(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednIpamObjList=[]
        ednIpamObjs = db.session.execute('SELECT * FROM edn_ipam_table WHERE creation_date = (SELECT max(creation_date) FROM edn_ipam_table)')
        
        for ednIpamObj in ednIpamObjs:
            ednIpamDataDict= {}
            ednIpamDataDict['id']= ednIpamObj[0]
            ednIpamDataDict['region'] = ednIpamObj[1]
            ednIpamDataDict['site_id'] = ednIpamObj[2]
            ednIpamDataDict['device_id'] = ednIpamObj[3]
            ednIpamDataDict['ip_address'] = ednIpamObj[4]
            ednIpamDataDict['subnet_mask'] = ednIpamObj[5]
            ednIpamDataDict['subnet'] = ednIpamObj[6]
            ednIpamDataDict['protocol_status'] = ednIpamObj[7]
            ednIpamDataDict['admin_status'] = ednIpamObj[8]
            ednIpamDataDict['vlan'] = ednIpamObj[9]
            ednIpamDataDict['interface_name'] = ednIpamObj[10]
            ednIpamDataDict['vlan_name'] = ednIpamObj[11]
            ednIpamDataDict['virtual_ip'] = ednIpamObj[12]
            ednIpamDataDict['interface_description'] = ednIpamObj[13]
            ednIpamDataDict['creation_date'] = FormatDate(ednIpamObj[14])
            ednIpamDataDict['modification_date'] = FormatDate(ednIpamObj[15])
            ednIpamDataDict['management_ip'] = ednIpamObj[16]
            ednIpamDataDict['site_type'] = ednIpamObj[17]
            ednIpamDataDict['created_by'] = ednIpamObj[18]
            ednIpamDataDict['modified_by'] = ednIpamObj[19]
            ednIpamObjList.append(ednIpamDataDict)

        content = gzip.compress(json.dumps(ednIpamObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllEdnIpamDates',methods=['GET'])
@token_required
def GetAllEdnIpamDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from edn_ipam_table ORDER BY creation_date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getAllEdnIpamByDate", methods = ['POST'])
@token_required
def GetAllEdnIpamByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednIpamObjList=[]

        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)

        ednIpamObjs = db.session.execute(f"SELECT * FROM edn_ipam_table WHERE creation_date = '{current_time}' ")
        
        for ednIpamObj in ednIpamObjs:
            ednIpamDataDict= {}
            ednIpamDataDict['id']= ednIpamObj[0]
            ednIpamDataDict['region'] = ednIpamObj[1]
            ednIpamDataDict['site_id'] = ednIpamObj[2]
            ednIpamDataDict['device_id'] = ednIpamObj[3]
            ednIpamDataDict['ip_address'] = ednIpamObj[4]
            ednIpamDataDict['subnet_mask'] = ednIpamObj[5]
            ednIpamDataDict['subnet'] = ednIpamObj[6]
            ednIpamDataDict['protocol_status'] = ednIpamObj[7]
            ednIpamDataDict['admin_status'] = ednIpamObj[8]
            ednIpamDataDict['vlan'] = ednIpamObj[9]
            ednIpamDataDict['interface_name'] = ednIpamObj[10]
            ednIpamDataDict['vlan_name'] = ednIpamObj[11]
            ednIpamDataDict['virtual_ip'] = ednIpamObj[12]
            ednIpamDataDict['interface_description'] = ednIpamObj[13]
            ednIpamDataDict['creation_date'] = FormatDate(ednIpamObj[14])
            ednIpamDataDict['modification_date'] = FormatDate(ednIpamObj[15])
            ednIpamDataDict['management_ip'] = ednIpamObj[16]
            ednIpamDataDict['site_type'] = ednIpamObj[17]
            ednIpamDataDict['created_by'] = ednIpamObj[18]
            ednIpamDataDict['modified_by'] = ednIpamObj[19]
            ednIpamObjList.append(ednIpamDataDict)
        content = gzip.compress(json.dumps(ednIpamObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

#''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

@app.route("/fetchIgwIpam", methods = ['GET'])
@token_required
def FetchIgwIpam(user_data):  
    if True:
        try:
            FetchIgwIpamFunc(user_data)
            return jsonify("Success"), 200
            
        except Exception as e:
            print(f"Exception Occured for IGW IPAM {e}", file=sys.stderr)
            return jsonify("Failure"), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchIgwIpamFunc(user_data):
    ednIpamList = []
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query_string = "select site_id, device_id, ne_ip_address, sw_type, site_type from seed_table where operation_status='Production' and cisco_domain = 'IGW-NET' and (sw_type='IOS' or sw_type='IOS-XE' or sw_type='IOS-XR' or sw_type='NX-OS' or sw_type='ACI-LEAF');" 
    result = db.session.execute(query_string)
    for row in result:
        igwIpamDict = {}
        igwIpamDict['site_id'] = row[0]
        siteObj = Phy_Table.query.filter_by(site_id=row[0]).first()
        if siteObj:
            igwIpamDict['region']= siteObj.region 
        else:
            igwIpamDict['region']= '' 

        igwIpamDict['device_id'] = row[1]
        igwIpamDict['mgmt_ip'] = row[2]
        igwIpamDict['sw_type'] = row[3]
        igwIpamDict['site_type'] = row[4]
        igwIpamDict['type'] = 'IGW'
        igwIpamDict['time'] = current_time
        igwIpamDict['user_id']= user_data['user_id']
        
        ednIpamList.append(igwIpamDict)
      
    try:
        ipam= IPAM()
    except Exception as e:
        print("Exception Occured In IGW IPAM", file=sys.stderr)
    #Update Script Status
    
    igwIpamStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script=="IGW-IPAM").first()

    try:
        igwIpamStatus.script = "IGW-IPAM"
        igwIpamStatus.status = "Running"
        igwIpamStatus.creation_date= current_time
        igwIpamStatus.modification_date= current_time
        
        InsertData(igwIpamStatus)
    
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    try:
        ipam.getIpam(ednIpamList)
    except Exception as e:
        print(e, file=sys.stderr)
   
    try:
        igwIpamStatus.script = "IGW-IPAM"
        igwIpamStatus.status = "Completed"
        igwIpamStatus.creation_date= current_time
        igwIpamStatus.modification_date= current_time
        db.session.add(igwIpamStatus)
        db.session.commit() 
    
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)


@app.route("/getIgwIpamScriptStatus", methods = ['GET'])
@token_required
def GetIgwIpamFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwIpam={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        igwIpamStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "IGW-IPAM").first()
        if igwIpamStatus:
            script_status= igwIpamStatus.status
            script_modifiation_date= str(igwIpamStatus.modification_date)
        igwIpam["fetch_status"] = script_status
        igwIpam["fetch_date"]= script_modifiation_date

        content = gzip.compress(json.dumps(igwIpam).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllIgwIpamDates',methods=['GET'])
@token_required
def GetAllIgwIpamDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from igw_ipam_table ORDER BY creation_date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)

@app.route("/getAllIgwIpam", methods = ['GET'])
@token_required
def GetAllIgwIpam(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwIpamObjList=[]
        igwIpamObjs = db.session.execute('SELECT * FROM igw_ipam_table WHERE creation_date = (SELECT max(creation_date) FROM igw_ipam_table)')
        
        for igwIpamObj in igwIpamObjs:
            igwIpamDataDict= {}
            igwIpamDataDict['id']= igwIpamObj[0]
            igwIpamDataDict['region'] = igwIpamObj[1]
            igwIpamDataDict['site_id'] = igwIpamObj[2]
            igwIpamDataDict['site_type'] = igwIpamObj[17]
            igwIpamDataDict['device_id'] = igwIpamObj[3]
            igwIpamDataDict['ip_address'] = igwIpamObj[4]
            igwIpamDataDict['subnet_mask'] = igwIpamObj[5]
            igwIpamDataDict['subnet'] = igwIpamObj[6]
            igwIpamDataDict['protocol_status'] = igwIpamObj[7]
            igwIpamDataDict['admin_status'] = igwIpamObj[8]
            igwIpamDataDict['vlan'] = igwIpamObj[9]
            igwIpamDataDict['interface_name'] = igwIpamObj[10]
            igwIpamDataDict['vlan_name'] = igwIpamObj[11]
            igwIpamDataDict['virtual_ip'] = igwIpamObj[12]
            igwIpamDataDict['interface_description'] = igwIpamObj[13]
            igwIpamDataDict['creation_date'] = FormatDate(igwIpamObj[14])
            igwIpamDataDict['modification_date'] = FormatDate(igwIpamObj[15])
            igwIpamDataDict['management_ip'] = igwIpamObj[16]
            igwIpamDataDict['created_by'] = igwIpamObj[18]
            igwIpamDataDict['modified_by'] = igwIpamObj[19]
            igwIpamObjList.append(igwIpamDataDict)

        content = gzip.compress(json.dumps(igwIpamObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllIgwIpamByDate", methods = ['POST'])
@token_required
def GetAllIgwIpamByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwIpamObjList=[]
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")

        igwIpamObjs = db.session.execute(f"SELECT * FROM igw_ipam_table WHERE creation_date = '{current_time}'")
        for igwIpamObj in igwIpamObjs:
            igwIpamDataDict= {}
            igwIpamDataDict['id']= igwIpamObj[0]
            igwIpamDataDict['region'] = igwIpamObj[1]
            igwIpamDataDict['site_id'] = igwIpamObj[2]
            igwIpamDataDict['site_type'] = igwIpamObj[17]
            igwIpamDataDict['device_id'] = igwIpamObj[3]
            igwIpamDataDict['ip_address'] = igwIpamObj[4]
            igwIpamDataDict['subnet_mask'] = igwIpamObj[5]
            igwIpamDataDict['subnet'] = igwIpamObj[6]
            igwIpamDataDict['protocol_status'] = igwIpamObj[7]
            igwIpamDataDict['admin_status'] = igwIpamObj[8]
            igwIpamDataDict['vlan'] = igwIpamObj[9]
            igwIpamDataDict['interface_name'] = igwIpamObj[10]
            igwIpamDataDict['vlan_name'] = igwIpamObj[11]
            igwIpamDataDict['virtual_ip'] = igwIpamObj[12]
            igwIpamDataDict['interface_description'] = igwIpamObj[13]
            igwIpamDataDict['creation_date'] = FormatDate(igwIpamObj[14])
            igwIpamDataDict['modification_date'] = FormatDate(igwIpamObj[15])
            igwIpamDataDict['management_ip'] = igwIpamObj[16]
            igwIpamDataDict['created_by'] = igwIpamObj[18]
            igwIpamDataDict['modified_by'] = igwIpamObj[19]
            igwIpamObjList.append(igwIpamDataDict)

        content = gzip.compress(json.dumps(igwIpamObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

#-----------------------------------------------------------SOC---------------------------------------------------------#

@app.route("/fetchSocIpCollector", methods = ['GET'])
@token_required
def FetchSocIpCollector(user_data):  
    if True:
        try:
            FetchSocIpCollectorFunc(user_data)
            return jsonify("Success"), 200
            
        except Exception as e:
            print(f"Exception occured when fetching IPAM {e}", file=sys.stderr)
            return jsonify("Failure"), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchSocIpCollectorFunc(user_data):
    socIpamList = []
    socIpamList2 = []
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query_string = "select site_id, device_id, ne_ip_address, sw_type, site_type from seed_table where operation_status='Production' and cisco_domain = 'SOC' and (sw_type ='Fortinet-Sec' or sw_type = 'Juniper-Sec' or sw_type = 'ASA-SOC' or sw_type = 'ASA96');"
    result = db.session.execute(query_string)
    
    query_string
    for row in result:
        #print("$$$$$$$$", row, file=sys.stderr)
        socIpamDict = {}
        socIpamDict['site_id'] = row[0]
        
        siteObj = Phy_Table.query.filter_by(site_id=row[0]).first()
        if siteObj:
            socIpamDict['region']= siteObj.region 
        else:
            socIpamDict['region']= '' 

        socIpamDict['device_id'] = row[1]
        socIpamDict['mgmt_ip'] = row[2]
        socIpamDict['sw_type'] = row[3]
        socIpamDict['site_type'] = row[4]
        socIpamDict['type'] = 'SOC'
        socIpamDict['time'] = current_time
        socIpamDict['user_id']= user_data['user_id']
        
        socIpamList.append(socIpamDict)
      
    try:
        #print("@#@#@#@#@#@#@#@#@#@#@#", file=sys.stderr)
        ipam= IPAM()
    except Exception as e:
        print("Exception Occured In SOC IPAM", file=sys.stderr)
    #Update Script Status
    
    socIpamStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script=="SOC-IPAM").first()

    try:
        socIpamStatus.script = "SOC-IPAM"
        socIpamStatus.status = "Running"
        socIpamStatus.creation_date= current_time
        socIpamStatus.modification_date= current_time
        
        InsertData(socIpamStatus)
    
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    try:
        ipam.getIpam(socIpamList)
    except Exception as e:
        print(e, file=sys.stderr)
   
    try:
        socIpamStatus.script = "SOC-IPAM"
        socIpamStatus.status = "Completed"
        socIpamStatus.creation_date= current_time
        socIpamStatus.modification_date= current_time
        db.session.add(socIpamStatus)
        db.session.commit() 
    
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)


@app.route("/getSocIpCollectorScriptStatus", methods = ['GET'])
@token_required
def GetSocIpCollectorFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        socIpam={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        socIpamStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "SOC-IPAM").first()
        if socIpamStatus:
            script_status= socIpamStatus.status
            script_modifiation_date= str(socIpamStatus.modification_date)
        socIpam["fetch_status"] = script_status
        socIpam["fetch_date"]= script_modifiation_date

        content = gzip.compress(json.dumps(socIpam).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route("/getAllSocIpCollector", methods = ['GET'])
@token_required
def GetAllSocIpCollector(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        socIpamObjList=[]
        socIpamObjs = db.session.execute('SELECT * FROM soc_ipam_table WHERE creation_date = (SELECT max(creation_date) FROM soc_ipam_table)')
        
        for socIpamObj in socIpamObjs:
            socIpamDataDict= {}
            socIpamDataDict['id']= socIpamObj[0]
            socIpamDataDict['region'] = socIpamObj[1]
            socIpamDataDict['site_id'] = socIpamObj[2]
            socIpamDataDict['device_id'] = socIpamObj[3]
            socIpamDataDict['ip_address'] = socIpamObj[4]
            socIpamDataDict['subnet_mask'] = socIpamObj[5]
            socIpamDataDict['subnet'] = socIpamObj[6]
            socIpamDataDict['protocol_status'] = socIpamObj[7]
            socIpamDataDict['admin_status'] = socIpamObj[8]
            socIpamDataDict['vlan'] = socIpamObj[9]
            socIpamDataDict['interface_name'] = socIpamObj[10]
            socIpamDataDict['vlan_name'] = socIpamObj[11]
            socIpamDataDict['virtual_ip'] = socIpamObj[12]
            socIpamDataDict['interface_description'] = socIpamObj[13]
            socIpamDataDict['creation_date'] = FormatDate(socIpamObj[14])
            socIpamDataDict['modification_date'] = FormatDate(socIpamObj[15])
            socIpamDataDict['management_ip'] = socIpamObj[16]
            socIpamDataDict['site_type'] = socIpamObj[17]
            socIpamDataDict['created_by'] = socIpamObj[18]
            socIpamDataDict['modified_by'] = socIpamObj[19]
            socIpamObjList.append(socIpamDataDict)

        content = gzip.compress(json.dumps(socIpamObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllSocIpCollectorDates',methods=['GET'])
@token_required
def GetAllSocIpCollectorDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from soc_ipam_table ORDER BY creation_date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getAllSocIpCollectorByDate", methods = ['POST'])
@token_required
def GetAllSocIpCollectorByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        socIpamObjList=[]

        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)

        socIpamObjs = db.session.execute(f"SELECT * FROM soc_ipam_table WHERE creation_date = '{current_time}' ")
        
        for socIpamObj in socIpamObjs:
            socIpamDataDict= {}
            socIpamDataDict['id']= socIpamObj[0]
            socIpamDataDict['region'] = socIpamObj[1]
            socIpamDataDict['site_id'] = socIpamObj[2]
            socIpamDataDict['device_id'] = socIpamObj[3]
            socIpamDataDict['ip_address'] = socIpamObj[4]
            socIpamDataDict['subnet_mask'] = socIpamObj[5]
            socIpamDataDict['subnet'] = socIpamObj[6]
            socIpamDataDict['protocol_status'] = socIpamObj[7]
            socIpamDataDict['admin_status'] = socIpamObj[8]
            socIpamDataDict['vlan'] = socIpamObj[9]
            socIpamDataDict['interface_name'] = socIpamObj[10]
            socIpamDataDict['vlan_name'] = socIpamObj[11]
            socIpamDataDict['virtual_ip'] = socIpamObj[12]
            socIpamDataDict['interface_description'] = socIpamObj[13]
            socIpamDataDict['creation_date'] = FormatDate(socIpamObj[14])
            socIpamDataDict['modification_date'] = FormatDate(socIpamObj[15])
            socIpamDataDict['management_ip'] = socIpamObj[16]
            socIpamDataDict['site_type'] = socIpamObj[17]
            socIpamDataDict['created_by'] = socIpamObj[18]
            socIpamDataDict['modified_by'] = socIpamObj[19]
            socIpamObjList.append(socIpamDataDict)
        content = gzip.compress(json.dumps(socIpamObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
