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
from app.edn_exchange.edn_exchange import EDNEXCHANGE
from app.models.inventory_models import EDN_EXCHANGE, VRF_OWNERS, EXTERNAL_VRF_ANALYSIS, INTRANET_VRF_ANALYSIS
from app.models.inventory_models import Phy_Table
from app.models.inventory_models import VRF_ROUTES


def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%d-%m-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

def UpdateData(obj):
    #add data to db
    #print(obj, file=sys.stderr)
    try:
        # db.session.flush()

        db.session.merge(obj)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong during Database Update {e}", file=sys.stderr)
    
    return True

def InsertData(obj):
    #add data to db
    try:
        db.session.add(obj)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong in Database Insertion {e}", file=sys.stderr)

    return True

def FormatStringDate(date):
    print(date, file=sys.stderr)

    try:
        if date is not None:
            if '-' in date:
                result = datetime.strptime(date,'%d-%m-%Y')
            elif '/' in date:
                result = datetime.strptime(date,'%d/%m/%Y')
            else:
                print("incorrect date format", file=sys.stderr)
                result = datetime(2000, 1, 1)
        else:
            #result = datetime(2000, 1, 1)
            result = datetime(2000, 1, 1)
    except:
        result=datetime(2000, 1,1)
        print("date format exception", file=sys.stderr)

@app.route("/fetchEdnExchange", methods = ['GET'])
@token_required
def FetchEdnExchange(user_data):  
    if True:
        try:
            FetchEdnExchangeFunc(user_data)
            return jsonify("Success"), 200
            
        except Exception as e:
            traceback.print_exc()
            print(f"Exception occured when fetching Exchange {e}", file=sys.stderr)
            return jsonify("Failure"), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchEdnExchangeFunc(user_data):
    ednExchangeList = []

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query_string = "select device_id, ne_ip_address, sw_type, site_id from seed_table where cisco_domain = 'EDN-NET' and `function`='ROUTER' and device_id LIKE '%EXC%' and operation_status='Production';" 
    result = db.session.execute(query_string)
    
    for row in result:
        ednExchangeDict = {}

        siteObj = Phy_Table.query.filter_by(site_id=row[3]).first()
        if siteObj:
            ednExchangeDict['region']= siteObj.region 
        else:
            ednExchangeDict['region']= ''
            
        
        ednExchangeDict['device_id'] = row[0]
        ednExchangeDict['device_ip'] = row[1]
        ednExchangeDict['sw_type'] = row[2]
        ednExchangeDict['site_id'] = row[3]
        ednExchangeDict['user_id'] = user_data['user_id']
        
        ednExchangeDict['time']= current_time
        
        ednExchangeList.append(ednExchangeDict)
    
    try:
        exchange= EDNEXCHANGE()
    except Exception as e:
        traceback.print_exc()
        print(f"Exception Occured In EDN Exchange {e}", file=sys.stderr)
    #Update Script Status
    
    ednExchangeStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script=="EDN-EXCHANGE").first()

    try:
        ednExchangeStatus.script = "EDN-EXCHANGE"
        ednExchangeStatus.status = "Running"
        ednExchangeStatus.creation_date= current_time
        ednExchangeStatus.modification_date= current_time
        
        InsertData(ednExchangeStatus)
    
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        print(f"Error while updating script status {e}", file=sys.stderr)

    try:
        
        exchange.getEdnExchange(ednExchangeList)
    except Exception as e:
        print(e, file=sys.stderr)
    
    try:
        externalVrfAnalysisFunc(user_data)
    except Exception as e:
        traceback.print_exc()
        print(f"Error whilw updating data {e}", file=sys.stderr)
    
    try:
        IntranetVrfAnalysisFunc(user_data)
    except Exception as e:
        traceback.print_exc()
        print(f"Error whilw updating data {e}", file=sys.stderr)
   
    try:
        ednExchangeStatus.script = "EDN-EXCHANGE"
        ednExchangeStatus.status = "Completed"
        ednExchangeStatus.creation_date= current_time
        ednExchangeStatus.modification_date= current_time
        db.session.add(ednExchangeStatus)
        db.session.commit() 
    
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        print(f"Error while updating script status {e}", file=sys.stderr)

@app.route("/getEdnExchangeScriptStatus", methods = ['GET'])
@token_required
def GetEdnExchangeFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednExchange={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        ednExchangeStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "EDN-EXCHANGE").first()
        if ednExchangeStatus:
            script_status= ednExchangeStatus.status
            script_modifiation_date= str(ednExchangeStatus.modification_date)
        ednExchange["fetch_status"] = script_status
        ednExchange["fetch_date"]= script_modifiation_date

        content = gzip.compress(json.dumps(ednExchange).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnExchange", methods = ['GET'])
@token_required
def GetAllEdnExchange(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednExchangeObjList=[]
        ednExchangeObjs = db.session.execute('SELECT * FROM edn_exchange WHERE creation_date = (SELECT max(creation_date) FROM edn_exchange)')
        
        for ednExchangeObj in ednExchangeObjs:
            ednExchangeDataDict= {}
            ednExchangeDataDict['edn_exchange_id']= ednExchangeObj[0]
            ednExchangeDataDict['device_ip'] = ednExchangeObj[1]
            ednExchangeDataDict['device_id'] = ednExchangeObj[2]
            ednExchangeDataDict['vrf_name'] = ednExchangeObj[3]
            ednExchangeDataDict['rd'] = ednExchangeObj[4]
            ednExchangeDataDict['interfaces'] = ednExchangeObj[5]
            ednExchangeDataDict['ibgp_ip'] = ednExchangeObj[6]
            ednExchangeDataDict['ibgp_as'] = ednExchangeObj[7]
            ednExchangeDataDict['ibgp_up_time'] = ednExchangeObj[8]
            ednExchangeDataDict['ibgp_prefix'] = ednExchangeObj[9]
            ednExchangeDataDict['ebgp_ip'] = ednExchangeObj[10]
            ednExchangeDataDict['ebgp_as'] = ednExchangeObj[11]
            ednExchangeDataDict['ebgp_up_time'] = ednExchangeObj[12]
            ednExchangeDataDict['ebgp_prefix'] = ednExchangeObj[13]
            ednExchangeDataDict['ebgp_advertised_routes'] = ednExchangeObj[14]
            ednExchangeDataDict['owner_name'] = ednExchangeObj[15]
            ednExchangeDataDict['owner_email'] = ednExchangeObj[16]
            ednExchangeDataDict['owner_contact'] = ednExchangeObj[17]
            ednExchangeDataDict['creation_date'] = str(ednExchangeObj[18])
            ednExchangeDataDict['modification_date'] = str(ednExchangeObj[19])
            ednExchangeDataDict['region'] = str(ednExchangeObj[20])
            ednExchangeDataDict['site_id'] = str(ednExchangeObj[21])
            ednExchangeDataDict['created_by']=  ednExchangeObj[22]
            ednExchangeDataDict['modified_by']=  ednExchangeObj[23]
            ednExchangeObjList.append(ednExchangeDataDict)

        content = gzip.compress(json.dumps(ednExchangeObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllEdnExchangeDates',methods=['GET'])
@token_required
def GetAllEdnExchangeDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from edn_exchange ORDER BY creation_date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getAllEdnExchangeByDate", methods = ['POST'])
@token_required
def GetAllEdnExchangeByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednExchangeObjList=[]

        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)

        ednExchangeObjs = db.session.execute(f"SELECT * FROM edn_exchange WHERE creation_date = '{current_time}' ")
        
        for ednExchangeObj in ednExchangeObjs:
            ednExchangeDataDict= {}
            ednExchangeDataDict['edn_exchange_id']= ednExchangeObj[0]
            ednExchangeDataDict['device_ip'] = ednExchangeObj[1]
            ednExchangeDataDict['device_id'] = ednExchangeObj[2]
            ednExchangeDataDict['vrf_name'] = ednExchangeObj[3]
            ednExchangeDataDict['rd'] = ednExchangeObj[4]
            ednExchangeDataDict['interfaces'] = ednExchangeObj[5]
            ednExchangeDataDict['ibgp_ip'] = ednExchangeObj[6]
            ednExchangeDataDict['ibgp_as'] = ednExchangeObj[7]
            ednExchangeDataDict['ibgp_up_time'] = ednExchangeObj[8]
            ednExchangeDataDict['ibgp_prefix'] = ednExchangeObj[9]
            ednExchangeDataDict['ebgp_ip'] = ednExchangeObj[10]
            ednExchangeDataDict['ebgp_as'] = ednExchangeObj[11]
            ednExchangeDataDict['ebgp_up_time'] = ednExchangeObj[12]
            ednExchangeDataDict['ebgp_prefix'] = ednExchangeObj[13]
            ednExchangeDataDict['ebgp_advertised_routes'] = ednExchangeObj[14]
            ednExchangeDataDict['owner_name'] = ednExchangeObj[15]
            ednExchangeDataDict['owner_email'] = ednExchangeObj[16]
            ednExchangeDataDict['owner_contact'] = ednExchangeObj[17]
            ednExchangeDataDict['creation_date'] = str(ednExchangeObj[18])
            ednExchangeDataDict['modification_date'] = str(ednExchangeObj[19])
            ednExchangeDataDict['region'] = str(ednExchangeObj[20])
            ednExchangeDataDict['site_id'] = str(ednExchangeObj[21]) 
            ednExchangeDataDict['created_by']=  ednExchangeObj[22]
            ednExchangeDataDict['modified_by']=  ednExchangeObj[23]
            ednExchangeObjList.append(ednExchangeDataDict)

        content = gzip.compress(json.dumps(ednExchangeObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editEdnExchange", methods = ['POST'])
@token_required
def editEdnExchange(user_data):    
    if True:#session.get('token', None):
        exchangeObj = request.get_json()
        print(exchangeObj,file = sys.stderr)
        exchanges = EDN_EXCHANGE.query.with_entities(EDN_EXCHANGE).filter_by(edn_exchange_id=exchangeObj["edn_exchange_id"]).first()
        if exchanges:
            exchanges.owner_name = exchangeObj['owner_name'] 
            exchanges.owner_email = exchangeObj['owner_email'] 
            exchanges.owner_contact = exchangeObj['owner_contact'] 
            exchanges.modification_date= datetime.now(tz)
            exchanges.modified_by= user_data['user_id']
            UpdateData(exchanges)
            
            return jsonify({'response': "success","code":"200"})
        else:
            return jsonify({'message': 'VRF Not Found'}), 500
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllVrfOwners", methods = ['GET'])
@token_required
def GetAllVrfOwners(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vrf_ownersList= []
        
        vrf_ownersObjs= VRF_OWNERS.query.all()
        for vrf_ownersObj in vrf_ownersObjs:
                
            vrf_ownersDataDict={}
            vrf_ownersDataDict['vrf_owners_id']= vrf_ownersObj.vrf_owners_id
            vrf_ownersDataDict['vrf_name']= vrf_ownersObj.vrf_name
            vrf_ownersDataDict['owner_name']= vrf_ownersObj.owner_name
            vrf_ownersDataDict['owner_email']= vrf_ownersObj.owner_email
            vrf_ownersDataDict['owner_contact']= vrf_ownersObj.owner_contact
            vrf_ownersDataDict['creation_date']=  vrf_ownersObj.creation_date
            vrf_ownersDataDict['modification_date']=  vrf_ownersObj.modification_date
            vrf_ownersDataDict['created_by']=  vrf_ownersObj.created_by
            vrf_ownersDataDict['modified_by']=  vrf_ownersObj.modified_by
            vrf_ownersList.append(vrf_ownersDataDict)
                
        return jsonify(vrf_ownersList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addVrfOwner",methods = ['POST'])
@token_required
def AddVrfOwner(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vrf_ownersObj = request.get_json()

        print(vrf_ownersObj,file=sys.stderr)
        vrf_owners = VRF_OWNERS()
        try:
            if  'vrf_name' in vrf_ownersObj:
                vrf_owners.vrf_name = vrf_ownersObj['vrf_name']
                vrf_owners.owner_name = vrf_ownersObj.get('owner_name')
                vrf_owners.owner_email = vrf_ownersObj.get('owner_email')
                vrf_owners.owner_contact = vrf_ownersObj.get('owner_contact')
                    
                if VRF_OWNERS.query.with_entities(VRF_OWNERS.vrf_owners_id).filter_by(vrf_name=vrf_ownersObj['vrf_name']).first() is not None:
                    vrf_owner= VRF_OWNERS.query.filter_by(vrf_name=vrf_ownersObj['vrf_name']).first()
                    vrf_owners.vrf_owners_id= vrf_owner.vrf_owners_id
                    vrf_owners.modification_date= datetime.now(tz)
                    vrf_owners.modified_by= user_data['user_id']
                    UpdateData(vrf_owners)
                    print("Updated " + vrf_ownersObj['vrf_name'],file=sys.stderr)
                    return jsonify({'response': "success","code":"200"})
                
                else:  
                    vrf_owners.creation_date= datetime.now(tz)
                    vrf_owners.modification_date= datetime.now(tz)
                    vrf_owners.created_by= user_data['user_id']
                    vrf_owners.modified_by= user_data['user_id']
                    InsertData(vrf_owners)
                    print("Inserted " +vrf_ownersObj['vrf_name'],file=sys.stderr)
                    return jsonify({'response': "success","code":"200"})
            else:
                return jsonify({'message': 'Empty Row found'}), 500
        except Exception as e:
            print(f"Exception Occured {e}", file=sys.stderr)
            return jsonify({'message': 'Exception Occures'}), 500
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addVrfOwners", methods = ['POST'])
@token_required
def AddVrfOwnersDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()

        print(postData,file=sys.stderr)
        print(f"VRF Owners Data received is:  {postData}", file=sys.stderr)
        for vrf_ownersObj in postData:
            if 'vrf_name' in vrf_ownersObj:
                vrf_owners = VRF_OWNERS()
                vrf_owners.vrf_name = vrf_ownersObj['vrf_name']
                vrf_owners.owner_name = vrf_ownersObj.get('owner_name')
                vrf_owners.owner_email = vrf_ownersObj.get('owner_email')
                vrf_owners.owner_contact = vrf_ownersObj.get('owner_contact')
                    
                if VRF_OWNERS.query.with_entities(VRF_OWNERS.vrf_owners_id).filter_by(vrf_name=vrf_ownersObj['vrf_name']).first() is not None:
                    vrf_owner= VRF_OWNERS.query.filter_by(vrf_name=vrf_ownersObj['vrf_name']).first()
                    vrf_owners.vrf_owners_id= vrf_owner.vrf_owners_id
                    vrf_owners.modification_date= datetime.now(tz)
                    vrf_owners.created_by= user_data['user_id']
                    UpdateData(vrf_owners)
                    print("Updated " + vrf_ownersObj['vrf_name'],file=sys.stderr)
                else:
                    
                    vrf_owners.creation_date= datetime.now(tz)
                    vrf_owners.modification_date= datetime.now(tz)
                    vrf_owners.created_by= user_data['user_id']
                    vrf_owners.modified_by= user_data['user_id']
                    InsertData(vrf_owners)
                    print("Inserted " +vrf_ownersObj['vrf_name'],file=sys.stderr)

        return jsonify({'response': "success","code":"200"})

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteVrfOwner",methods = ['POST'])
@token_required
def DeleteVrfOwnersDevice(user_data):
    if True:#session.get('token', None):
        vrf_ownersObj = request.get_json()
        print(vrf_ownersObj,file = sys.stderr)
        print(f"VRF Owners  Data received is:  {vrf_ownersObj}", file=sys.stderr)

        for obj in vrf_ownersObj.get("vrf_owners_ids"):
            vrf_ownersID = VRF_OWNERS.query.filter(VRF_OWNERS.vrf_owners_id==obj).first()
            print(vrf_ownersID,file=sys.stderr)
            if obj:
                db.session.delete(vrf_ownersID)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllVRFRoutes", methods = ['GET'])
@token_required
def GetAllVRFRoutes(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        VRFRoutesObjList=[]
        VRFRoutesObjs = db.session.execute('SELECT * FROM vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes)')
        
        for VRFRoutesObj in VRFRoutesObjs:
            VRFRoutesDataDict= {}
            VRFRoutesDataDict['vrf_route_id']= VRFRoutesObj[0]
            VRFRoutesDataDict['device_ip'] = VRFRoutesObj[1]
            VRFRoutesDataDict['device_id'] = VRFRoutesObj[2]
            VRFRoutesDataDict['vrf_name'] = VRFRoutesObj[3]
            VRFRoutesDataDict['route'] = VRFRoutesObj[4]
            VRFRoutesDataDict['next_hop'] = VRFRoutesObj[5]
            VRFRoutesDataDict['as_path'] = VRFRoutesObj[6]
            VRFRoutesDataDict['origin'] = VRFRoutesObj[7]
            VRFRoutesDataDict['creation_date'] = str(VRFRoutesObj[8])
            VRFRoutesDataDict['modification_date'] = str(VRFRoutesObj[9]) 
            VRFRoutesDataDict['created_by']=  VRFRoutesObj[10]
            VRFRoutesDataDict['modified_by']=  VRFRoutesObj[11]
            VRFRoutesObjList.append(VRFRoutesDataDict)

        content = gzip.compress(json.dumps(VRFRoutesObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllVRFRoutesDates',methods=['GET'])
@token_required
def GetAllVRFRoutesDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vrf_routes ORDER BY creation_date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getAllVRFRoutesByDate", methods = ['POST'])
@token_required
def GetAllVRFRoutesByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        VRFRoutesObjList=[]

        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)

        VRFRoutesObjs = db.session.execute(f"SELECT * FROM vrf_routes WHERE creation_date = '{current_time}' ")
        
        for VRFRoutesObj in VRFRoutesObjs:
            VRFRoutesDataDict= {}
            VRFRoutesDataDict['vrf_route_id']= VRFRoutesObj[0]
            VRFRoutesDataDict['device_ip'] = VRFRoutesObj[1]
            VRFRoutesDataDict['device_id'] = VRFRoutesObj[2]
            VRFRoutesDataDict['vrf_name'] = VRFRoutesObj[3]
            VRFRoutesDataDict['route'] = VRFRoutesObj[4]
            VRFRoutesDataDict['next_hop'] = VRFRoutesObj[5]
            VRFRoutesDataDict['as_path'] = VRFRoutesObj[6]
            VRFRoutesDataDict['origin'] = VRFRoutesObj[7]
            VRFRoutesDataDict['creation_date'] = str(VRFRoutesObj[8])
            VRFRoutesDataDict['modification_date'] = str(VRFRoutesObj[9]) 
            VRFRoutesDataDict['created_by']=  VRFRoutesObj[10]
            VRFRoutesDataDict['modified_by']=  VRFRoutesObj[11]
            VRFRoutesObjList.append(VRFRoutesDataDict)

        content = gzip.compress(json.dumps(VRFRoutesObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getEdnRoutesByAS", methods = ['GET'])
@token_required
def GetEdnRoutesByAS(user_data):
    device_id=vrf_name=""
    device_id= request.args.get('device_id')
    vrf_name= request.args.get('vrf_name')

    
    # obj = request.get_json()
    # if "device_id" in obj:
    #     device_id= obj['device_id']

    # if "vrf_name" in obj:
    #   vrf_name= obj['vrf_name']
        
    routesList= []
    if device_id and vrf_name:
        routeObj = db.session.execute(f"SELECT route, next_hop FROM vrf_routes WHERE device_id= '{device_id}' and vrf_name= '{vrf_name}' and creation_date = (SELECT max(creation_date) FROM vrf_routes) ") # creation_date = (SELECT max(creation_date) FROM vrf_routes)
        
        for routeOb in routeObj:
            routeDataDict={}
            routeDataDict['route']= routeOb[0]
            routeDataDict['next_hop']= routeOb[1]
            routesList.append(routeDataDict)
            print(routesList, file=sys.stderr)
        
        return jsonify(routesList), 200
        
        #else: 
        #    print("Site Data not found in DB", file=sys.stderr)
        #    return jsonify({'response': "Site Data not found in DB"}), 500 
    else:
        print("Can not Get Device ID and VRF Name from URL", file=sys.stderr)
        return jsonify({'response': "Can not Get Device ID and VRF Name from URL"}), 500

@app.route('/fetchExternalVrfAnalysis', methods=['POST'])
@token_required
def externalVrfAnalysis(user_data):
    if True:
        response = externalVrfAnalysisFunc(user_data)
        return response
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

def externalVrfAnalysisFunc(user_data):
    try:
        newList = []
        time = datetime.now(tz)
        result = db.session.execute(f"Select distinct(vrf_name), device_id from edn_exchange WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes);")
        for vrf, id in result:
            if vrf in ['DCN', 'WLC', 'Offices', 'Outlets'] or "NEW" in id:
                print(f"Exception in {vrf}, {id}", file=sys.stderr)
            else:
                print("@@@@@@@@@@@@@@@", vrf, id, file=sys.stderr)
                siteID = db.session.execute(f"Select distinct(site_id) from edn_exchange WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = '{vrf}';")
                vrf_analysis = {
                    'vrf': None,
                    'primary_site': None,
                    'secondary_site': [],
                    'no_of_received_routes': None,
                    'missing_routes_in_secondary_site': []
                }
                vrf_analysis['vrf'] = vrf
                for site in siteID:
                    print("############", site, type(site[0]), len(site[0]), file=sys.stderr)
                    if site[0] == 'MLQA':
                        print("Primary Site", site, file=sys.stderr)
                        vrf_analysis['primary_site'] = site[0]
                    else:
                        print("Secondary Site", site, file=sys.stderr)
                        vrf_analysis['secondary_site'].append(site[0])

                vrf_analysis['secondary_site'] = ', '.join(vrf_analysis['secondary_site'])
                routes = db.session.execute(f"select count(route), device_id from vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = '{vrf}' GROUP BY device_id;").fetchall()
                print("Received Routes vrf", vrf, file=sys.stderr)

                if len(routes) >= 2:
                    receivedRoutes = str(routes[0][0]) + '/' + str(routes[1][0])
                    vrf_analysis['no_of_received_routes'] = receivedRoutes
                elif len(routes) == 1:
                    if 'MLQA' in routes[0][1]:
                        vrf_analysis['no_of_received_routes'] = str(routes[0][0]) + '/0'
                    else:
                        vrf_analysis['no_of_received_routes'] = '0/' + str(routes[0][0])
                print("Received Routes", vrf_analysis['no_of_received_routes'], file=sys.stderr)
                missingRoute = db.session.execute(f"SELECT route FROM vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = '{vrf}' GROUP BY route HAVING COUNT(*) = 1;")
                if missingRoute:
                    for route in missingRoute:
                        print("Received Routes", route, file=sys.stderr)
                        vrf_analysis['missing_routes_in_secondary_site'].append(route[0])
                vrf_analysis['missing_routes_in_secondary_site'] = ', '.join(vrf_analysis['missing_routes_in_secondary_site'])
                
                print("$$$$$$$$$$$$$$$", vrf_analysis, file=sys.stderr)
                newList.append(vrf_analysis)
        newList = [dict(t) for t in set([tuple(sorted(d.items())) for d in newList])]
        for objs in newList:
            try:
                vrf_analysis = EXTERNAL_VRF_ANALYSIS()
                vrf_analysis.vrf = objs.get('vrf', "")
                vrf_analysis.primary_site = objs.get('primary_site', "")
                vrf_analysis.secondary_site = objs.get('secondary_site', "")
                vrf_analysis.no_of_received_routes = objs.get('no_of_received_routes', "")
                vrf_analysis.missing_routes_in_secondary_site = objs.get('missing_routes_in_secondary_site', "")

                vrf_analysis.creation_date = time
                vrf_analysis.modification_date = time
                vrf_analysis.created_by = user_data['user_id']
                vrf_analysis.modified_by = user_data['user_id']

                InsertData(vrf_analysis)
                print("Data Inserted Into DB", file=sys.stderr)

            except Exception as e:
                traceback.print_exc()
                print(f"Error Adding Data: {e}", file=sys.stderr)
             
        return jsonify({'Response': "Successfully Inserted"}), 200

    
    except Exception as e:
        traceback.print_exc()
        print(f"Something else went wrong during Database Update {e.args}", file=sys.stderr)
        return str(e), 500
    
@app.route('/getAllExternalVRFAnalysisDates',methods=['GET'])
@token_required
def GetAllExternalVRFAnalysisDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from external_vrf_analysis ORDER BY creation_date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 
    
@app.route("/getAllExternalVRFAnalysisByDate", methods = ['POST'])
@token_required
def GetAllExternalVRFAnalysisByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        VRFObjList=[]

        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)

        VRFAnalysisObjs = db.session.execute(f"SELECT * FROM external_vrf_analysis WHERE creation_date = '{current_time}' ")
        
        for VRFAnalysisObj in VRFAnalysisObjs:
            VRFDataDict= {}
            VRFDataDict['external_vrf_analysis_id']= VRFAnalysisObj[0]
            VRFDataDict['vrf'] = VRFAnalysisObj[1]
            VRFDataDict['primary_site'] = VRFAnalysisObj[2]
            VRFDataDict['secondary_site'] = VRFAnalysisObj[3]
            VRFDataDict['number_of_received_routes'] = VRFAnalysisObj[4]
            VRFDataDict['missing_routes_in_secondary_site'] = VRFAnalysisObj[5]
            VRFDataDict['creation_date'] = str(VRFAnalysisObj[6])
            VRFDataDict['modification_date'] = str(VRFAnalysisObj[7])
            VRFDataDict['created_by'] = str(VRFAnalysisObj[8])
            VRFDataDict['modified_by'] = str(VRFAnalysisObj[9])

            VRFObjList.append(VRFDataDict)

        content = gzip.compress(json.dumps(VRFObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/getAllExternalVRFAnalysis", methods = ['GET'])
@token_required
def GetAllExternalVRFAnalysis(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        VRFObjList=[]
        VRFAnalysisObjs = db.session.execute('SELECT * FROM external_vrf_analysis WHERE creation_date = (SELECT max(creation_date) FROM external_vrf_analysis)')
        
        for VRFAnalysisObj in VRFAnalysisObjs:
            VRFDataDict= {}
            VRFDataDict['external_vrf_analysis_id']= VRFAnalysisObj[0]
            VRFDataDict['vrf'] = VRFAnalysisObj[1]
            VRFDataDict['primary_site'] = VRFAnalysisObj[2]
            VRFDataDict['secondary_site'] = VRFAnalysisObj[3]
            VRFDataDict['number_of_received_routes'] = VRFAnalysisObj[4]
            VRFDataDict['missing_routes_in_secondary_site'] = VRFAnalysisObj[5]
            VRFDataDict['creation_date'] = str(VRFAnalysisObj[6])
            VRFDataDict['modification_date'] = str(VRFAnalysisObj[7])
            VRFDataDict['created_by'] = str(VRFAnalysisObj[8])
            VRFDataDict['modified_by'] = str(VRFAnalysisObj[9])
            VRFObjList.append(VRFDataDict)

        content = gzip.compress(json.dumps(VRFObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/fetchIntranetVrfAnalysis', methods=['POST'])
@token_required
def IntranetVrfAnalysis(user_data):
    try:
        response = IntranetVrfAnalysisFunc(user_data)
        return response
    
    except Exception as e:
        traceback.print_exc()
        return str(e), 500

def IntranetVrfAnalysisFunc(user_data):
    try:
        newList = []
        time = datetime.now(tz)
        result = db.session.execute(f"Select distinct(vrf_name), region from edn_exchange WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND (vrf_name = 'Offices' or vrf_name = 'Outlets' or vrf_name = 'DCN') AND device_id NOT LIKE '%NEW';")
        for vrf in result:
            if vrf[0] in ['DCN', 'Offices', 'Outlets']:
                siteID = db.session.execute(f"Select distinct(site_id) from edn_exchange WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = '{vrf[0]}';")
                vrf_analysis = {
                    'vrf': None,
                    'region': None,
                    'primary_site': None,
                    'secondary_site': None,
                    'no_of_received_routes': None,
                    'missing_routes_in_secondary_site': None,
                    'missing_sites_in_secondary_site': None
                }
                vrf_analysis['vrf'] = vrf[0]
                if 'Offices' in vrf[0] and 'CENTRAL' in vrf[1]:
                    vrf_analysis['region'] = vrf[1]
                    primaryCount = ''
                    secondaryCount = ''
                    for site in siteID:
                        if site[0] == 'MLQA':
                            vrf_analysis['primary_site'] = site[0]
                        elif site[0] == 'SULM':
                            vrf_analysis['secondary_site'] = site[0]
                        data = db.session.execute(f"select count(route) from vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'Offices' AND (device_id LIKE 'MLQA%' OR device_id LIKE 'SULM%') GROUP BY device_id;").fetchall()
                        if data:
                            # print("Primary Object", data, site, file=sys.stderr)
                            primaryCount = data[0][0]
                            secondaryCount = data[1][0]
                            vrf_analysis['no_of_received_routes'] = str(primaryCount) + '/' + str(secondaryCount)
                        # print("!!!!!!!!!!!!!!!!!!!!!!", primaryCount, secondaryCount, file=sys.stderr)
                        missing = db.session.execute(f"SELECT route FROM vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'Offices' AND (device_id LIKE 'MLQA%' OR device_id LIKE 'SULM%') GROUP BY route HAVING COUNT(*) = 1;")
                        if missing:
                            for obj in missing:
                                # print("MISSING ROUTE", obj, file=sys.stderr)
                                if vrf_analysis['missing_routes_in_secondary_site'] and str(obj[0]) not in vrf_analysis['missing_routes_in_secondary_site']:
                                    vrf_analysis['missing_routes_in_secondary_site'] = vrf_analysis.get('missing_routes_in_secondary_site', "") + ', ' + str(obj[0])
                                else:
                                    vrf_analysis['missing_routes_in_secondary_site'] = str(obj[0])
                                subnet = db.session.execute(f"Select device_id from edn_ipam_table where creation_date = (SELECT max(creation_date) FROM edn_ipam_table) AND subnet LIKE '{obj[0]}%%';").fetchall()
                                if subnet:
                                    # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!", type(subnet), subnet, file=sys.stderr)
                                    if vrf_analysis['missing_sites_in_secondary_site'] and str(subnet[0][0]) not in vrf_analysis['missing_sites_in_secondary_site']:
                                        vrf_analysis['missing_sites_in_secondary_site'] = vrf_analysis.get('missing_sites_in_secondary_site', "") + ', ' + str(subnet[0][0])
                                    else:
                                        vrf_analysis['missing_sites_in_secondary_site'] = str(subnet[0][0])
                elif 'Offices' in vrf[0] and 'WESTERN' in vrf[1]:
                    vrf_analysis['region'] = vrf[1]
                    for site in siteID:
                        if site[0] == 'FYHA':
                            vrf_analysis['primary_site'] = site[0]
                        elif site[0] == 'JED1':
                            vrf_analysis['secondary_site'] = site[0]
                        data = db.session.execute(f"select count(route) from vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'Offices' AND (device_id LIKE 'FYHA%' OR device_id LIKE 'JED1%') GROUP BY device_id;").fetchall()
                        if data:
                            # print("Primary Object", data, file=sys.stderr)
                            primaryCount = data[0][0]
                            secondaryCount = data[1][0]
                            vrf_analysis['no_of_received_routes'] = str(primaryCount) + '/' + str(secondaryCount)
                        # print("!!!!!!!!!!!!!!!!!!!!!!", primaryCount, secondaryCount, file=sys.stderr)
                        missing = db.session.execute(f"SELECT route FROM vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'Offices' AND (device_id LIKE 'FYHA%' OR device_id LIKE 'JED1%') GROUP BY route HAVING COUNT(*) = 1;")
                        if missing:
                            for obj in missing:
                                # print("MISSING ROUTE", obj, file=sys.stderr)
                                if vrf_analysis['missing_routes_in_secondary_site'] and str(obj[0]) not in vrf_analysis['missing_routes_in_secondary_site']:
                                    vrf_analysis['missing_routes_in_secondary_site'] = vrf_analysis.get('missing_routes_in_secondary_site', "") + ', ' + str(obj[0])
                                else:
                                    vrf_analysis['missing_routes_in_secondary_site'] = str(obj[0])
                                subnet = db.session.execute(f"Select device_id from edn_ipam_table where creation_date = (SELECT max(creation_date) FROM edn_ipam_table) AND subnet LIKE '{obj[0]}%%';").fetchall()
                                if subnet:
                                    # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!", type(subnet), subnet, file=sys.stderr)
                                    if vrf_analysis['missing_sites_in_secondary_site'] and str(subnet[0][0]) not in vrf_analysis['missing_sites_in_secondary_site']:
                                        vrf_analysis['missing_sites_in_secondary_site'] = vrf_analysis.get('missing_sites_in_secondary_site', "") + ', ' + str(subnet[0][0])
                                    else:
                                        vrf_analysis['missing_sites_in_secondary_site'] = str(subnet[0][0])
                elif 'Offices' in vrf[0] and 'EASTERN' in vrf[1]:
                    vrf_analysis['region'] = vrf[1]
                    for site in siteID:
                        if site[0] == 'ADAM':
                            vrf_analysis['primary_site'] = site[0]
                        elif site[0] == 'RSHD':
                            vrf_analysis['secondary_site'] = site[0]
                        data = db.session.execute(f"select count(route) from vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'Offices' AND (device_id LIKE 'ADAM%' OR device_id LIKE 'RSHD%') GROUP BY device_id;").fetchall()
                        if data:
                            # print("Primary Object", data, file=sys.stderr)
                            primaryCount = data[0][0]
                            secondaryCount = data[1][0]
                            vrf_analysis['no_of_received_routes'] = str(primaryCount) + '/' + str(secondaryCount)
                        # print("!!!!!!!!!!!!!!!!!!!!!!", primaryCount, secondaryCount, file=sys.stderr)
                        missing = db.session.execute(f"SELECT route FROM vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'Offices' AND (device_id LIKE 'ADAM%' OR device_id LIKE 'RSHD%') GROUP BY route HAVING COUNT(*) = 1;")
                        if missing:
                            for obj in missing:
                                # print("MISSING ROUTE", obj, file=sys.stderr)
                                if vrf_analysis['missing_routes_in_secondary_site'] and str(obj[0]) not in vrf_analysis['missing_routes_in_secondary_site']:
                                    vrf_analysis['missing_routes_in_secondary_site'] = vrf_analysis.get('missing_routes_in_secondary_site', "") + ', ' + str(obj[0])
                                else:
                                    vrf_analysis['missing_routes_in_secondary_site'] = str(obj[0])
                                subnet = db.session.execute(f"Select device_id from edn_ipam_table where creation_date = (SELECT max(creation_date) FROM edn_ipam_table) AND subnet LIKE '{obj[0]}%%';").fetchall()
                                if subnet:
                                    # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!", type(subnet), subnet, file=sys.stderr)
                                    if vrf_analysis['missing_sites_in_secondary_site'] and str(subnet[0][0]) not in vrf_analysis['missing_sites_in_secondary_site']:
                                        vrf_analysis['missing_sites_in_secondary_site'] = vrf_analysis.get('missing_sites_in_secondary_site', "") + ', ' + str(subnet[0][0])
                                    else:
                                        vrf_analysis['missing_sites_in_secondary_site'] = str(subnet[0][0])
                elif 'Outlets' in vrf[0] and 'CENTRAL' in vrf[1]:
                    vrf_analysis['region'] = vrf[1]
                    for site in siteID:
                        if site[0] == 'MLQA':
                            vrf_analysis['primary_site'] = site[0]
                        elif site[0] == 'SULM':
                            vrf_analysis['secondary_site'] = site[0]
                        data = db.session.execute(f"select count(route) from vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'Outlets' AND (device_id LIKE 'MLQA%' OR device_id LIKE 'SULM%') GROUP BY device_id;").fetchall()
                        if data:
                            # print("Primary Object", data, file=sys.stderr)
                            primaryCount = data[0][0]
                            secondaryCount = data[1][0]
                            vrf_analysis['no_of_received_routes'] = str(primaryCount) + '/' + str(secondaryCount)
                        # print("!!!!!!!!!!!!!!!!!!!!!!", primaryCount, secondaryCount, file=sys.stderr)
                        missing = db.session.execute(f"SELECT route FROM vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'Outlets' AND (device_id LIKE 'MLQA%' OR device_id LIKE 'SULM%') GROUP BY route HAVING COUNT(*) = 1;")
                        if missing:
                            for obj in missing:
                                # print("MISSING ROUTE", obj, file=sys.stderr)
                                if vrf_analysis['missing_routes_in_secondary_site'] and str(obj[0]) not in vrf_analysis['missing_routes_in_secondary_site']:
                                    vrf_analysis['missing_routes_in_secondary_site'] = vrf_analysis.get('missing_routes_in_secondary_site', "") + ', ' + str(obj[0])
                                else:
                                    vrf_analysis['missing_routes_in_secondary_site'] = str(obj[0])
                                subnet = db.session.execute(f"Select device_id from edn_ipam_table where creation_date = (SELECT max(creation_date) FROM edn_ipam_table) AND subnet LIKE '{obj[0]}%%';").fetchall()
                                if subnet:
                                    # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!", type(subnet), subnet, file=sys.stderr)
                                    if vrf_analysis['missing_sites_in_secondary_site'] and str(subnet[0][0]) not in vrf_analysis['missing_sites_in_secondary_site']:
                                        vrf_analysis['missing_sites_in_secondary_site'] = vrf_analysis.get('missing_sites_in_secondary_site', "") + ', ' + str(subnet[0][0])
                                    else:
                                        vrf_analysis['missing_sites_in_secondary_site'] = str(subnet[0][0])
                elif 'Outlets' in vrf[0] and 'WESTERN' in vrf[1]:
                    vrf_analysis['region'] = vrf[1]
                    for site in siteID:
                        if site[0] == 'FYHA':
                            vrf_analysis['primary_site'] = site[0]
                        elif site[0] == 'JED1':
                            vrf_analysis['secondary_site'] = site[0]
                        data = db.session.execute(f"select count(route) from vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'Outlets' AND (device_id LIKE 'FYHA%' OR device_id LIKE 'JED1%') GROUP BY device_id;").fetchall()
                        if data:
                            # print("Primary Object", data, file=sys.stderr)
                            primaryCount = data[0][0]
                            secondaryCount = data[1][0]
                            vrf_analysis['no_of_received_routes'] = str(primaryCount) + '/' + str(secondaryCount)
                        # print("!!!!!!!!!!!!!!!!!!!!!!", primaryCount, secondaryCount, file=sys.stderr)
                        missing = db.session.execute(f"SELECT route FROM vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'Outlets' AND (device_id LIKE 'FYHA%' OR device_id LIKE 'JED1%') GROUP BY route HAVING COUNT(*) = 1;")
                        if missing:
                            for obj in missing:
                                # print("MISSING ROUTE", obj, file=sys.stderr)
                                if vrf_analysis['missing_routes_in_secondary_site'] and str(obj[0]) not in vrf_analysis['missing_routes_in_secondary_site']:
                                    vrf_analysis['missing_routes_in_secondary_site'] = vrf_analysis.get('missing_routes_in_secondary_site', "") + ', ' + str(obj[0])
                                else:
                                    vrf_analysis['missing_routes_in_secondary_site'] = str(obj[0])
                                subnet = db.session.execute(f"Select device_id from edn_ipam_table where creation_date = (SELECT max(creation_date) FROM edn_ipam_table) AND subnet LIKE '{obj[0]}%%';").fetchall()
                                if subnet:
                                    # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!", type(subnet), subnet, file=sys.stderr)
                                    if vrf_analysis['missing_sites_in_secondary_site'] and str(subnet[0][0]) not in vrf_analysis['missing_sites_in_secondary_site']:
                                        vrf_analysis['missing_sites_in_secondary_site'] = vrf_analysis.get('missing_sites_in_secondary_site', "") + ', ' + str(subnet[0][0])
                                    else:
                                        vrf_analysis['missing_sites_in_secondary_site'] = str(subnet[0][0])
                elif 'Outlets' in vrf[0] and 'EASTERN' in vrf[1]:
                    vrf_analysis['region'] = vrf[1]
                    for site in siteID:
                        if site[0] == 'ADAM':
                            vrf_analysis['primary_site'] = site[0]
                        elif site[0] == 'RSHD':
                            vrf_analysis['secondary_site'] = site[0]
                        data = db.session.execute(f"select count(route) from vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'Outlets' AND (device_id LIKE 'ADAM%' OR device_id LIKE 'RSHD%') GROUP BY device_id;").fetchall()
                        if data:
                            # print("Primary Object", data, file=sys.stderr)
                            primaryCount = data[0][0]
                            secondaryCount = data[1][0]
                            vrf_analysis['no_of_received_routes'] = str(primaryCount) + '/' + str(secondaryCount)
                        # print("!!!!!!!!!!!!!!!!!!!!!!", primaryCount, secondaryCount, file=sys.stderr)
                        missing = db.session.execute(f"SELECT route FROM vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'Outlets' AND (device_id LIKE 'ADAM%' OR device_id LIKE 'RSHD%') GROUP BY route HAVING COUNT(*) = 1;")
                        if missing:
                            for obj in missing:
                                # print("MISSING ROUTE", obj, file=sys.stderr)
                                if vrf_analysis['missing_routes_in_secondary_site'] and str(obj[0]) not in vrf_analysis['missing_routes_in_secondary_site']:
                                    vrf_analysis['missing_routes_in_secondary_site'] = vrf_analysis.get('missing_routes_in_secondary_site', "") + ', ' + str(obj[0])
                                else:
                                    vrf_analysis['missing_routes_in_secondary_site'] = str(obj[0])
                                subnet = db.session.execute(f"Select device_id from edn_ipam_table where creation_date = (SELECT max(creation_date) FROM edn_ipam_table) AND subnet LIKE '{obj[0]}%%';").fetchall()
                                if subnet:
                                    # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!", type(subnet), subnet, file=sys.stderr)
                                    if vrf_analysis['missing_sites_in_secondary_site'] and str(subnet[0][0]) not in vrf_analysis['missing_sites_in_secondary_site']:
                                        vrf_analysis['missing_sites_in_secondary_site'] = vrf_analysis.get('missing_sites_in_secondary_site', "") + ', ' + str(subnet[0][0])
                                    else:
                                        vrf_analysis['missing_sites_in_secondary_site'] = str(subnet[0][0])
                elif 'DCN' in vrf[0] and 'CENTRAL' in vrf[1]:
                    vrf_analysis['region'] = vrf[1]
                    for site in siteID:
                        if site[0] == 'MLQA':
                            vrf_analysis['primary_site'] = site[0]
                        elif site[0] == 'SULM':
                            vrf_analysis['secondary_site'] = site[0]
                        data = db.session.execute(f"select count(route) from vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'DCN' AND (device_id LIKE 'MLQA%' OR device_id LIKE 'SULM%') GROUP BY device_id;").fetchall()
                        if data:
                            # print("Primary Object", data, file=sys.stderr)
                            primaryCount = data[0][0]
                            secondaryCount = data[1][0]
                            vrf_analysis['no_of_received_routes'] = str(primaryCount) + '/' + str(secondaryCount)
                        # print("!!!!!!!!!!!!!!!!!!!!!!", primaryCount, secondaryCount, file=sys.stderr)
                        missing = db.session.execute(f"SELECT route FROM vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'DCN' AND (device_id LIKE 'MLQA%' OR device_id LIKE 'SULM%') GROUP BY route HAVING COUNT(*) = 1;")
                        if missing:
                            for obj in missing:
                                # print("MISSING ROUTE", obj, file=sys.stderr)
                                if vrf_analysis['missing_routes_in_secondary_site'] and str(obj[0]) not in vrf_analysis['missing_routes_in_secondary_site']:
                                    vrf_analysis['missing_routes_in_secondary_site'] = vrf_analysis.get('missing_routes_in_secondary_site', "") + ', ' + str(obj[0])
                                else:
                                    vrf_analysis['missing_routes_in_secondary_site'] = str(obj[0])
                                subnet = db.session.execute(f"Select device_id from edn_ipam_table where creation_date = (SELECT max(creation_date) FROM edn_ipam_table) AND subnet LIKE '{obj[0]}%%';").fetchall()
                                if subnet:
                                    # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!", type(subnet), subnet, file=sys.stderr)
                                    if vrf_analysis['missing_sites_in_secondary_site'] and str(subnet[0][0]) not in vrf_analysis['missing_sites_in_secondary_site']:
                                        vrf_analysis['missing_sites_in_secondary_site'] = vrf_analysis.get('missing_sites_in_secondary_site', "") + ', ' + str(subnet[0][0])
                                    else:
                                        vrf_analysis['missing_sites_in_secondary_site'] = str(subnet[0][0])
                elif 'DCN' in vrf[0] and 'WESTERN' in vrf[1]:
                    vrf_analysis['region'] = vrf[1]
                    for site in siteID:
                        if site[0] == 'FYHA':
                            vrf_analysis['primary_site'] = site[0]
                        elif site[0] == 'JED1':
                            vrf_analysis['secondary_site'] = site[0]
                        data = db.session.execute(f"select count(route) from vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'DCN' AND (device_id LIKE 'FYHA%' OR device_id LIKE 'JED1%') GROUP BY device_id;").fetchall()
                        if data:
                            # print("Primary Object", data, file=sys.stderr)
                            primaryCount = data[0][0]
                            secondaryCount = data[1][0]
                            vrf_analysis['no_of_received_routes'] = str(primaryCount) + '/' + str(secondaryCount)
                        # print("!!!!!!!!!!!!!!!!!!!!!!", primaryCount, secondaryCount, file=sys.stderr)
                        missing = db.session.execute(f"SELECT route FROM vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'DCN' AND (device_id LIKE 'FYHA%' OR device_id LIKE 'JED1%') GROUP BY route HAVING COUNT(*) = 1;")
                        if missing:
                            for obj in missing:
                                # print("MISSING ROUTE", obj, file=sys.stderr)
                                if vrf_analysis['missing_routes_in_secondary_site'] and str(obj[0]) not in vrf_analysis['missing_routes_in_secondary_site']:
                                    vrf_analysis['missing_routes_in_secondary_site'] = vrf_analysis.get('missing_routes_in_secondary_site', "") + ', ' + str(obj[0])
                                else:
                                    vrf_analysis['missing_routes_in_secondary_site'] = str(obj[0])
                                subnet = db.session.execute(f"Select device_id from edn_ipam_table where creation_date = (SELECT max(creation_date) FROM edn_ipam_table) AND subnet LIKE '{obj[0]}%%';").fetchall()
                                if subnet:
                                    # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!", type(subnet), subnet, file=sys.stderr)
                                    if vrf_analysis['missing_sites_in_secondary_site'] and str(subnet[0][0]) not in vrf_analysis['missing_sites_in_secondary_site']:
                                        vrf_analysis['missing_sites_in_secondary_site'] = vrf_analysis.get('missing_sites_in_secondary_site', "") + ', ' + str(subnet[0][0])
                                    else:
                                        vrf_analysis['missing_sites_in_secondary_site'] = str(subnet[0][0])
                elif 'DCN' in vrf[0] and 'EASTERN' in vrf[1]:
                    vrf_analysis['region'] = vrf[1]
                    for site in siteID:
                        if site[0] == 'ADAM':
                            vrf_analysis['primary_site'] = site[0]
                        elif site[0] == 'RSHD':
                            vrf_analysis['secondary_site'] = site[0]
                        data = db.session.execute(f"select count(route) from vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'DCN' AND (device_id LIKE 'ADAM%' OR device_id LIKE 'RSHD%') GROUP BY device_id;").fetchall()
                        if data:
                            # print("Primary Object", data, file=sys.stderr)
                            primaryCount = data[0][0]
                            secondaryCount = data[1][0]
                            vrf_analysis['no_of_received_routes'] = str(primaryCount) + '/' + str(secondaryCount)
                        # print("!!!!!!!!!!!!!!!!!!!!!!", primaryCount, secondaryCount, file=sys.stderr)
                        missing = db.session.execute(f"SELECT route FROM vrf_routes WHERE creation_date = (SELECT max(creation_date) FROM vrf_routes) AND vrf_name = 'DCN' AND (device_id LIKE 'ADAM%' OR device_id LIKE 'RSHD%') GROUP BY route HAVING COUNT(*) = 1;")
                        if missing:
                            for obj in missing:
                                # print("MISSING ROUTE", obj, file=sys.stderr)
                                if vrf_analysis['missing_routes_in_secondary_site'] and str(obj[0]) not in vrf_analysis['missing_routes_in_secondary_site']:
                                    vrf_analysis['missing_routes_in_secondary_site'] = vrf_analysis.get('missing_routes_in_secondary_site', "") + ', ' + str(obj[0])
                                else:
                                    vrf_analysis['missing_routes_in_secondary_site'] = str(obj[0])
                                subnet = db.session.execute(f"Select device_id from edn_ipam_table where creation_date = (SELECT max(creation_date) FROM edn_ipam_table) AND subnet LIKE '{obj[0]}%%';").fetchall()
                                if subnet:
                                    # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!", type(subnet), subnet, file=sys.stderr)
                                    if vrf_analysis['missing_sites_in_secondary_site'] and str(subnet[0][0]) not in vrf_analysis['missing_sites_in_secondary_site']:
                                        vrf_analysis['missing_sites_in_secondary_site'] = vrf_analysis.get('missing_sites_in_secondary_site', "") + ', ' + str(subnet[0][0])
                                    else:
                                        vrf_analysis['missing_sites_in_secondary_site'] = str(subnet[0][0])
                
                print("$$$$$$$$$$$$$$$", vrf_analysis, file=sys.stderr)
                newList.append(vrf_analysis)
        for objs in newList:
            try:
                vrf_analysis = INTRANET_VRF_ANALYSIS()
                vrf_analysis.vrf = objs.get('vrf', "")
                vrf_analysis.region = objs.get('region', "")
                vrf_analysis.primary_site = objs.get('primary_site', "")
                vrf_analysis.secondary_site = objs.get('secondary_site', "")
                vrf_analysis.no_of_received_routes = objs.get('no_of_received_routes', "")
                vrf_analysis.missing_routes_in_secondary_site = objs.get('missing_routes_in_secondary_site', "")
                vrf_analysis.missing_sites_in_secondary_site = objs.get('missing_sites_in_secondary_site', "")

                vrf_analysis.creation_date = time
                vrf_analysis.modification_date = time
                vrf_analysis.created_by = user_data['user_id']
                vrf_analysis.modified_by = user_data['user_id']

                db.session.add(vrf_analysis)
                db.session.commit()
                print("Data Inserted Into DB", file=sys.stderr)

            except Exception as e:
                db.session.rollback()
                traceback.print_exc()
                print(f"Error Adding Data: {e}", file=sys.stderr)
             
        return jsonify({'Response': "Successfully Inserted"}), 200
        # return jsonify(newList), 200

    
    except Exception as e:
        traceback.print_exc()
        print(f"Something else went wrong during Database Update {e.args}", file=sys.stderr)
        return str(e), 500

@app.route('/getAllIntranetVRFAnalysisDates',methods=['GET'])
@token_required
def GetAllIntranetVRFAnalysisDates(user_data):
    try:
        dates = []
        queryString = "select distinct(creation_date) from intranet_vrf_analysis ORDER BY creation_date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    except Exception as e:
        traceback.print_exc()
        return str(e), 500
    
@app.route("/getAllIntranetVRFAnalysisByDate", methods = ['POST'])
@token_required
def GetAllIntranetVRFAnalysisByDate(user_data):
    try:
        VRFObjList=[]

        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)

        VRFAnalysisObjs = db.session.execute(f"SELECT * FROM intranet_vrf_analysis WHERE creation_date = '{current_time}' ")
        
        for VRFAnalysisObj in VRFAnalysisObjs:
            VRFDataDict= {}
            VRFDataDict['intranet_vrf_analysis_id']= VRFAnalysisObj[0]
            VRFDataDict['vrf'] = VRFAnalysisObj[1]
            VRFDataDict['region'] = VRFAnalysisObj[2]
            VRFDataDict['primary_site'] = VRFAnalysisObj[3]
            VRFDataDict['secondary_site'] = VRFAnalysisObj[4]
            VRFDataDict['number_of_received_routes'] = VRFAnalysisObj[5]
            VRFDataDict['missing_routes_in_secondary_site'] = VRFAnalysisObj[6]
            VRFDataDict['missing_sites_in_secondary_site'] = VRFAnalysisObj[7]
            VRFDataDict['creation_date'] = str(VRFAnalysisObj[8])
            VRFDataDict['modification_date'] = str(VRFAnalysisObj[9])
            VRFDataDict['created_by'] = str(VRFAnalysisObj[10])
            VRFDataDict['modified_by'] = str(VRFAnalysisObj[11])

            VRFObjList.append(VRFDataDict)

        content = gzip.compress(json.dumps(VRFObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    
    except Exception as e:
        traceback.print_exc()
        return str(e), 500
    
@app.route("/getAllIntranetVRFAnalysis", methods = ['GET'])
@token_required
def GetAllIntranetVRFAnalysis(user_data):
    try:
        VRFObjList=[]
        VRFAnalysisObjs = db.session.execute('SELECT * FROM intranet_vrf_analysis WHERE creation_date = (SELECT max(creation_date) FROM intranet_vrf_analysis)')
        
        for VRFAnalysisObj in VRFAnalysisObjs:
            VRFDataDict= {}
            VRFDataDict['intranet_vrf_analysis_id']= VRFAnalysisObj[0]
            VRFDataDict['vrf'] = VRFAnalysisObj[1]
            VRFDataDict['region'] = VRFAnalysisObj[2]
            VRFDataDict['primary_site'] = VRFAnalysisObj[3]
            VRFDataDict['secondary_site'] = VRFAnalysisObj[4]
            VRFDataDict['number_of_received_routes'] = VRFAnalysisObj[5]
            VRFDataDict['missing_routes_in_secondary_site'] = VRFAnalysisObj[6]
            VRFDataDict['missing_sites_in_secondary_site'] = VRFAnalysisObj[7]
            VRFDataDict['creation_date'] = str(VRFAnalysisObj[8])
            VRFDataDict['modification_date'] = str(VRFAnalysisObj[9])
            VRFDataDict['created_by'] = str(VRFAnalysisObj[10])
            VRFDataDict['modified_by'] = str(VRFAnalysisObj[11])

            VRFObjList.append(VRFDataDict)

        content = gzip.compress(json.dumps(VRFObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    
    except Exception as e:
        traceback.print_exc()
        return str(e), 500
