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
#from app.dc_capacity_scripts.dc_capacity import DcCapacity
from app.dc_capacity.dc_capacity import DCCAPACITY
from app.dc_capacity.dc_capacity_apic import DCCAPACITYAPIC

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

@app.route("/fetchEdnDcCapacity", methods = ['GET'])
@token_required
def FetchEdnDcCapacity(user_data):  
    if True:
        try:
            FetchEdnDcCapacityFunc(user_data)
            return jsonify("Success"), 200
            
        except Exception as e:
            traceback.print_exc()
            print(f"Exception occured when fetching DcCapacity {e}", file=sys.stderr)
            return jsonify("Failure"), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchEdnDcCapacityFunc(user_data):
    ednDcCapacityList = []

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query_string = "select site_id, device_id,ne_ip_address, sw_type from seed_table where cisco_domain = 'EDN-NET' and (sw_type='IOS' or sw_type='IOS-XE' or sw_type='IOS-XR' or sw_type='NX-OS') and `function` LIKE '%SWITCH%' and site_type='DC' and operation_status='Production';" 
    result = db.session.execute(query_string)
    
    for row in result:
        ednDcCapacityDict = {}
        ednDcCapacityDict['site_id'] = row[0]
        ednDcCapacityDict['device_id'] = row[1]
        ednDcCapacityDict['device_ip'] = row[2]
        ednDcCapacityDict['sw_type'] = row[3]
        ednDcCapacityDict['type'] = 'EDN'
        ednDcCapacityDict['time'] = current_time
        ednDcCapacityDict['user_id'] = user_data['user_id']
        
        ednDcCapacityList.append(ednDcCapacityDict)
    
    query_string = "select ne_ip_address, site_id, device_id from seed_table where cisco_domain = 'EDN-NET' and sw_type = 'APIC' and site_type='DC' and operation_status='Production';" 
    result = db.session.execute(query_string)
    ednACIDict = {}
    try:
        for row in result:
            site_apic= row[2].split('-')
            site_apic= '-'.join(site_apic[:-1])
            if site_apic in ednACIDict:
                ednACIDictEntry = {}
                ednACIDictEntry['ip'] = row[0]
                ednACIDictEntry['time'] = current_time
                ednACIDictEntry['type'] = 'EDN'
                ednACIDictEntry['user_id'] = user_data['user_id']
                ednACIDictEntry['device_id'] =row[2]

                ednACIDict[site_apic].append(ednACIDictEntry)
            else:
                site_apic= row[2].split('-')
                site_apic= '-'.join(site_apic[:-1])
                ednACIDict[site_apic] = []


                ednACIDictEntry = {}
                ednACIDictEntry['ip'] = row[0]
                ednACIDictEntry['time'] = current_time
                ednACIDictEntry['type'] = 'EDN'
                ednACIDictEntry['user_id'] = user_data['user_id']
                ednACIDictEntry['device_id'] =row[2]
            
                ednACIDict[site_apic].append(ednACIDictEntry)
    except Exception as e:
        print("Exception, {e} ", file=sys.stderr)
        traceback.print_exc()

    try:
        dc_capacity= DCCAPACITY()
        dc_capacity_apic= DCCAPACITYAPIC()
    except Exception as e:
        traceback.print_exc()
        print(f"Exception Occured In EDN DcCapacity {e}", file=sys.stderr)
    #Update Script Status
    
    ednDcCapacityStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script=="EDN-Dc-Capacity").first()

    try:
        ednDcCapacityStatus.script = "EDN-Dc-Capacity"
        ednDcCapacityStatus.status = "Running"
        ednDcCapacityStatus.creation_date= current_time
        ednDcCapacityStatus.modification_date= current_time
        
        InsertData(ednDcCapacityStatus)
    
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    try:
        dc_capacity.getDCCapacity(ednDcCapacityList)
        dc_capacity_apic.getDCCapacity(ednACIDict)
    except Exception as e:
        print(e, file=sys.stderr)
   
    try:
        ednDcCapacityStatus.script = "EDN-Dc-Capacity"
        ednDcCapacityStatus.status = "Completed"
        ednDcCapacityStatus.creation_date= current_time
        ednDcCapacityStatus.modification_date= current_time
        db.session.add(ednDcCapacityStatus)
        db.session.commit() 
    
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

@app.route("/getEdnDcCapacityFetchStatus", methods = ['GET'])
@token_required
def GetEdnDcCapacityFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednDcCapacity={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        ednDcCapacityStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "EDN-DC-CAPACITY").first()
        if ednDcCapacityStatus:
            script_status= ednDcCapacityStatus.status
            script_modifiation_date= str(ednDcCapacityStatus.modification_date)
        ednDcCapacity["fetch_status"] = script_status
        ednDcCapacity["fetch_date"]= script_modifiation_date

        content = gzip.compress(json.dumps(ednDcCapacity).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnDcCapacity", methods = ['GET'])
@token_required
def GetAllEdnDcCapacity(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednDcCapacityObjList=[]
        ednDcCapacityObjs = db.session.execute('SELECT * FROM edn_dc_capacity WHERE creation_date = (SELECT max(creation_date) FROM edn_dc_capacity)')
        
        for ednDcCapacityObj in ednDcCapacityObjs:
            ednDcCapacityDataDict= {}
            ednDcCapacityDataDict['edn_dc_capacity_id']= ednDcCapacityObj[0]
            ednDcCapacityDataDict['device_ip'] = ednDcCapacityObj[1]
            ednDcCapacityDataDict['site_id'] = ednDcCapacityObj[2]
            ednDcCapacityDataDict['device_id'] = ednDcCapacityObj[3]
            ednDcCapacityDataDict['os_version'] = ednDcCapacityObj[4]
            ednDcCapacityDataDict['total_1g_ports'] = ednDcCapacityObj[5]
            ednDcCapacityDataDict['total_10g_ports'] = ednDcCapacityObj[6]
            ednDcCapacityDataDict['total_25g_ports'] = ednDcCapacityObj[7]
            ednDcCapacityDataDict['total_40g_ports'] = ednDcCapacityObj[8]
            ednDcCapacityDataDict['total_100g_ports'] = ednDcCapacityObj[9]
            ednDcCapacityDataDict['total_fast_ethernet_ports'] = ednDcCapacityObj[10]
            ednDcCapacityDataDict['connected_1g'] = ednDcCapacityObj[11]
            ednDcCapacityDataDict['connected_10g'] = ednDcCapacityObj[12]
            ednDcCapacityDataDict['connected_25g'] = ednDcCapacityObj[13]
            ednDcCapacityDataDict['connected_40g'] = ednDcCapacityObj[14]
            ednDcCapacityDataDict['connected_100g'] = ednDcCapacityObj[15]
            ednDcCapacityDataDict['connected_fast_ethernet'] = ednDcCapacityObj[16]
            ednDcCapacityDataDict['not_connected_1g'] = ednDcCapacityObj[17]
            ednDcCapacityDataDict['not_connected_10g'] = ednDcCapacityObj[18]
            ednDcCapacityDataDict['not_connected_25g'] = ednDcCapacityObj[19]
            ednDcCapacityDataDict['not_connected_40g'] = ednDcCapacityObj[20]
            ednDcCapacityDataDict['not_connected_100g'] = ednDcCapacityObj[21]
            ednDcCapacityDataDict['not_fast_ethernet_10g'] = ednDcCapacityObj[22]
            ednDcCapacityDataDict['unused_sfps_1g'] = ednDcCapacityObj[23]
            ednDcCapacityDataDict['unused_sfps_10g'] = ednDcCapacityObj[24]
            ednDcCapacityDataDict['unused_sfps_25g'] = ednDcCapacityObj[25]
            ednDcCapacityDataDict['unused_sfps_40g'] = ednDcCapacityObj[26]
            ednDcCapacityDataDict['unused_sfps_100g'] = ednDcCapacityObj[27]
            
            ednDcCapacityDataDict['creation_date'] = str(ednDcCapacityObj[28])
            ednDcCapacityDataDict['modification_date'] = str(ednDcCapacityObj[29]) 
            ednDcCapacityDataDict['created_by'] = str(ednDcCapacityObj[30]) 
            ednDcCapacityDataDict['modified_by'] = str(ednDcCapacityObj[31]) 
            ednDcCapacityObjList.append(ednDcCapacityDataDict)

        content = gzip.compress(json.dumps(ednDcCapacityObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllEdnDcCapacityDates',methods=['GET'])
@token_required
def GetAllEdnDcCapacityDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from edn_dc_capacity ORDER BY creation_date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getAllEdnDcCapacityByDate", methods = ['POST'])
@token_required
def GetAllEdnDcCapacityByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednDcCapacityObjList=[]

        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)

        ednDcCapacityObjs = db.session.execute(f"SELECT * FROM edn_dc_capacity WHERE creation_date = '{current_time}' ")
        
        for ednDcCapacityObj in ednDcCapacityObjs:
            ednDcCapacityDataDict= {}
            ednDcCapacityDataDict['edn_dc_capacity_id']= ednDcCapacityObj[0]
            ednDcCapacityDataDict['device_ip'] = ednDcCapacityObj[1]
            ednDcCapacityDataDict['site_id'] = ednDcCapacityObj[2]
            ednDcCapacityDataDict['device_id'] = ednDcCapacityObj[3]
            ednDcCapacityDataDict['os_version'] = ednDcCapacityObj[4]
            ednDcCapacityDataDict['total_1g_ports'] = ednDcCapacityObj[5]
            ednDcCapacityDataDict['total_10g_ports'] = ednDcCapacityObj[6]
            ednDcCapacityDataDict['total_25g_ports'] = ednDcCapacityObj[7]
            ednDcCapacityDataDict['total_40g_ports'] = ednDcCapacityObj[8]
            ednDcCapacityDataDict['total_100g_ports'] = ednDcCapacityObj[9]
            ednDcCapacityDataDict['total_fast_ethernet_ports'] = ednDcCapacityObj[10]
            ednDcCapacityDataDict['connected_1g'] = ednDcCapacityObj[11]
            ednDcCapacityDataDict['connected_10g'] = ednDcCapacityObj[12]
            ednDcCapacityDataDict['connected_25g'] = ednDcCapacityObj[13]
            ednDcCapacityDataDict['connected_40g'] = ednDcCapacityObj[14]
            ednDcCapacityDataDict['connected_100g'] = ednDcCapacityObj[15]
            ednDcCapacityDataDict['connected_fast_ethernet'] = ednDcCapacityObj[16]
            ednDcCapacityDataDict['not_connected_1g'] = ednDcCapacityObj[17]
            ednDcCapacityDataDict['not_connected_10g'] = ednDcCapacityObj[18]
            ednDcCapacityDataDict['not_connected_25g'] = ednDcCapacityObj[19]
            ednDcCapacityDataDict['not_connected_40g'] = ednDcCapacityObj[20]
            ednDcCapacityDataDict['not_connected_100g'] = ednDcCapacityObj[21]
            ednDcCapacityDataDict['not_fast_ethernet_10g'] = ednDcCapacityObj[22]
            ednDcCapacityDataDict['unused_sfps_1g'] = ednDcCapacityObj[23]
            ednDcCapacityDataDict['unused_sfps_10g'] = ednDcCapacityObj[24]
            ednDcCapacityDataDict['unused_sfps_25g'] = ednDcCapacityObj[25]
            ednDcCapacityDataDict['unused_sfps_40g'] = ednDcCapacityObj[26]
            ednDcCapacityDataDict['unused_sfps_100g'] = ednDcCapacityObj[27]
            
            ednDcCapacityDataDict['creation_date'] = str(ednDcCapacityObj[28])
            ednDcCapacityDataDict['modification_date'] = str(ednDcCapacityObj[29]) 
            ednDcCapacityDataDict['created_by'] = str(ednDcCapacityObj[30]) 
            ednDcCapacityDataDict['modified_by'] = str(ednDcCapacityObj[31]) 
            ednDcCapacityObjList.append(ednDcCapacityDataDict)

        content = gzip.compress(json.dumps(ednDcCapacityObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

#''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

@app.route("/fetchIgwDcCapacity", methods = ['GET'])
@token_required
def FetchIgwDcCapacity(user_data):  
    if True:
        try:
            FetchIgwDcCapacityFunc(user_data)
            return jsonify("Success"), 200
            
        except Exception as e:
            print(f"Exception occured when fetching DcCapacity {e}", file=sys.stderr)
            return jsonify("Failure"), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchIgwDcCapacityFunc(user_data):
    igwDcCapacityList = []
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query_string = "select site_id, device_id, ne_ip_address, sw_type from seed_table where cisco_domain = 'IGW-NET' and (sw_type='IOS' or sw_type='IOS-XE' or sw_type='IOS-XR' or sw_type='NX-OS') and `function` LIKE '%SWITCH%'  and site_type='DC' and operation_status='Production';" 
    result = db.session.execute(query_string)
    
    
    for row in result:
        igwDcCapacityDict = {}
        igwDcCapacityDict['site_id'] = row[0]
        igwDcCapacityDict['device_id'] = row[1]
        igwDcCapacityDict['device_ip'] = row[2]
        igwDcCapacityDict['sw_type'] = row[3]
        igwDcCapacityDict['type'] = 'IGW'
        igwDcCapacityDict['time'] = current_time
        igwDcCapacityDict['user_id'] = user_data['user_id']
        
        igwDcCapacityList.append(igwDcCapacityDict)

    query_string = "select ne_ip_address, site_id, device_id from seed_table where cisco_domain = 'IGW-NET' and sw_type = 'APIC' and site_type='DC' and operation_status='Production';" 
    result = db.session.execute(query_string)
    igwACIDict = {}
    try:
        for row in result:
            site_apic= row[2].split('-')
            site_apic= '-'.join(site_apic[:-1])
            if site_apic in igwACIDict:
                igwACIDictEntry = {}
                igwACIDictEntry['ip'] = row[0]
                igwACIDictEntry['time'] = current_time
                igwACIDictEntry['type'] = 'IGW'
                igwACIDictEntry['user_id'] = user_data['user_id']
                igwACIDictEntry['device_id'] =row[2]

                igwACIDict[site_apic].append(igwACIDictEntry)
            else:
                site_apic= row[2].split('-')
                site_apic= '-'.join(site_apic[:-1])
                igwACIDict[site_apic] = []


                igwACIDictEntry = {}
                igwACIDictEntry['ip'] = row[0]
                igwACIDictEntry['time'] = current_time
                igwACIDictEntry['type'] = 'IGW'
                igwACIDictEntry['user_id'] = user_data['user_id']
                igwACIDictEntry['device_id'] =row[2]
            
                igwACIDict[site_apic].append(igwACIDictEntry)
    except Exception as e:
        print("Exception, {e} ", file=sys.stderr)
        traceback.print_exc()

    
      
    try:
        dc_capacity= DCCAPACITY()
        dc_capacity_apic= DCCAPACITYAPIC()
    except Exception as e:
        print("Exception Occured In IGW DcCapacity", file=sys.stderr)
    #Update Script Status
    
    igwDcCapacityStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script=="IGW-Dc-Capacity").first()

    try:
        igwDcCapacityStatus.script = "IGW-Dc-Capacity"
        igwDcCapacityStatus.status = "Running"
        igwDcCapacityStatus.creation_date= current_time
        igwDcCapacityStatus.modification_date= current_time
        
        InsertData(igwDcCapacityStatus)
    
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    try:
        dc_capacity.getDCCapacity(igwDcCapacityList)
        dc_capacity_apic.getDCCapacity(igwACIDict)
    except Exception as e:
        print(e, file=sys.stderr)
   
    try:
        igwDcCapacityStatus.script = "IGW-Dc-Capacity"
        igwDcCapacityStatus.status = "Completed"
        igwDcCapacityStatus.creation_date= current_time
        igwDcCapacityStatus.modification_date= current_time
        db.session.add(igwDcCapacityStatus)
        db.session.commit() 
    
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

@app.route("/getIgwDcCapacityFetchStatus", methods = ['GET'])
@token_required
def GetIgwDcCapacityFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwDcCapacity={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        igwDcCapacityStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "IGW-DC-CAPACITY").first()
        if igwDcCapacityStatus:
            script_status= igwDcCapacityStatus.status
            script_modifiation_date= str(igwDcCapacityStatus.modification_date)
        igwDcCapacity["fetch_status"] = script_status
        igwDcCapacity["fetch_date"]= script_modifiation_date

        content = gzip.compress(json.dumps(igwDcCapacity).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllIgwDcCapacityDates',methods=['GET'])
@token_required
def GetAllIgwDcCapacityDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from igw_dc_capacity ORDER BY creation_date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 


@app.route("/getAllIgwDcCapacity", methods = ['GET'])
@token_required
def GetAllIgwDcCapacity(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwDcCapacityObjList=[]
        igwDcCapacityObjs = db.session.execute('SELECT * FROM igw_dc_capacity WHERE creation_date = (SELECT max(creation_date) FROM igw_dc_capacity)')
        
        for igwDcCapacityObj in igwDcCapacityObjs:
            igwDcCapacityDataDict= {}
            igwDcCapacityDataDict['igw_dc_capacity_id']= igwDcCapacityObj[0]
            igwDcCapacityDataDict['device_ip'] = igwDcCapacityObj[1]
            igwDcCapacityDataDict['site_id'] = igwDcCapacityObj[2]
            igwDcCapacityDataDict['device_id'] = igwDcCapacityObj[3]
            igwDcCapacityDataDict['os_version'] = igwDcCapacityObj[4]
            igwDcCapacityDataDict['total_1g_ports'] = igwDcCapacityObj[5]
            igwDcCapacityDataDict['total_10g_ports'] = igwDcCapacityObj[6]
            igwDcCapacityDataDict['total_25g_ports'] = igwDcCapacityObj[7]
            igwDcCapacityDataDict['total_40g_ports'] = igwDcCapacityObj[8]
            igwDcCapacityDataDict['total_100g_ports'] = igwDcCapacityObj[9]
            igwDcCapacityDataDict['total_fast_ethernet_ports'] = igwDcCapacityObj[10]
            igwDcCapacityDataDict['connected_1g'] = igwDcCapacityObj[11]
            igwDcCapacityDataDict['connected_10g'] = igwDcCapacityObj[12]
            igwDcCapacityDataDict['connected_25g'] = igwDcCapacityObj[13]
            igwDcCapacityDataDict['connected_40g'] = igwDcCapacityObj[14]
            igwDcCapacityDataDict['connected_100g'] = igwDcCapacityObj[15]
            igwDcCapacityDataDict['connected_fast_ethernet'] = igwDcCapacityObj[16]
            igwDcCapacityDataDict['not_connected_1g'] = igwDcCapacityObj[17]
            igwDcCapacityDataDict['not_connected_10g'] = igwDcCapacityObj[18]
            igwDcCapacityDataDict['not_connected_25g'] = igwDcCapacityObj[19]
            igwDcCapacityDataDict['not_connected_40g'] = igwDcCapacityObj[20]
            igwDcCapacityDataDict['not_connected_100g'] = igwDcCapacityObj[21]
            igwDcCapacityDataDict['not_fast_ethernet_10g'] = igwDcCapacityObj[22]
            igwDcCapacityDataDict['unused_sfps_1g'] = igwDcCapacityObj[23]
            igwDcCapacityDataDict['unused_sfps_10g'] = igwDcCapacityObj[24]
            igwDcCapacityDataDict['unused_sfps_25g'] = igwDcCapacityObj[25]
            igwDcCapacityDataDict['unused_sfps_40g'] = igwDcCapacityObj[26]
            igwDcCapacityDataDict['unused_sfps_100g'] = igwDcCapacityObj[27]
            
            igwDcCapacityDataDict['creation_date'] = str(igwDcCapacityObj[28])
            igwDcCapacityDataDict['modification_date'] = str(igwDcCapacityObj[29]) 
            igwDcCapacityDataDict['created_by'] = str(igwDcCapacityObj[30]) 
            igwDcCapacityDataDict['modified_by'] = str(igwDcCapacityObj[31]) 
            igwDcCapacityObjList.append(igwDcCapacityDataDict)

        content = gzip.compress(json.dumps(igwDcCapacityObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401



@app.route("/getAllIgwDcCapacityByDate", methods = ['POST'])
@token_required
def GetAllIgwDcCapacityByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwDcCapacityObjList=[]

        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)

        igwDcCapacityObjs = db.session.execute(f"SELECT * FROM igw_dc_capacity WHERE creation_date = '{current_time}' ")
        
        for igwDcCapacityObj in igwDcCapacityObjs:
            igwDcCapacityDataDict= {}
            igwDcCapacityDataDict['igw_dc_capacity_id']= igwDcCapacityObj[0]
            igwDcCapacityDataDict['device_ip'] = igwDcCapacityObj[1]
            igwDcCapacityDataDict['site_id'] = igwDcCapacityObj[2]
            igwDcCapacityDataDict['device_id'] = igwDcCapacityObj[3]
            igwDcCapacityDataDict['os_version'] = igwDcCapacityObj[4]
            igwDcCapacityDataDict['total_1g_ports'] = igwDcCapacityObj[5]
            igwDcCapacityDataDict['total_10g_ports'] = igwDcCapacityObj[6]
            igwDcCapacityDataDict['total_25g_ports'] = igwDcCapacityObj[7]
            igwDcCapacityDataDict['total_40g_ports'] = igwDcCapacityObj[8]
            igwDcCapacityDataDict['total_100g_ports'] = igwDcCapacityObj[9]
            igwDcCapacityDataDict['total_fast_ethernet_ports'] = igwDcCapacityObj[10]
            igwDcCapacityDataDict['connected_1g'] = igwDcCapacityObj[11]
            igwDcCapacityDataDict['connected_10g'] = igwDcCapacityObj[12]
            igwDcCapacityDataDict['connected_25g'] = igwDcCapacityObj[13]
            igwDcCapacityDataDict['connected_40g'] = igwDcCapacityObj[14]
            igwDcCapacityDataDict['connected_100g'] = igwDcCapacityObj[15]
            igwDcCapacityDataDict['connected_fast_ethernet'] = igwDcCapacityObj[16]
            igwDcCapacityDataDict['not_connected_1g'] = igwDcCapacityObj[17]
            igwDcCapacityDataDict['not_connected_10g'] = igwDcCapacityObj[18]
            igwDcCapacityDataDict['not_connected_25g'] = igwDcCapacityObj[19]
            igwDcCapacityDataDict['not_connected_40g'] = igwDcCapacityObj[20]
            igwDcCapacityDataDict['not_connected_100g'] = igwDcCapacityObj[21]
            igwDcCapacityDataDict['not_fast_ethernet_10g'] = igwDcCapacityObj[22]
            igwDcCapacityDataDict['unused_sfps_1g'] = igwDcCapacityObj[23]
            igwDcCapacityDataDict['unused_sfps_10g'] = igwDcCapacityObj[24]
            igwDcCapacityDataDict['unused_sfps_25g'] = igwDcCapacityObj[25]
            igwDcCapacityDataDict['unused_sfps_40g'] = igwDcCapacityObj[26]
            igwDcCapacityDataDict['unused_sfps_100g'] = igwDcCapacityObj[27]
            
            igwDcCapacityDataDict['creation_date'] = str(igwDcCapacityObj[28])
            igwDcCapacityDataDict['modification_date'] = str(igwDcCapacityObj[29]) 
            igwDcCapacityDataDict['created_by'] = str(igwDcCapacityObj[30]) 
            igwDcCapacityDataDict['modified_by'] = str(igwDcCapacityObj[31]) 
            igwDcCapacityObjList.append(igwDcCapacityDataDict)

        content = gzip.compress(json.dumps(igwDcCapacityObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
