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
from app.middleware import token_required
from app.edn_exchange.edn_core_routing import EDNCOREROUTING
from app.models.inventory_models import EDN_CORE_ROUTING, Phy_Table, INVENTORY_SCRIPTS_STATUS

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


@app.route("/fetchEdnCoreRouting", methods = ['GET'])
@token_required
def FetchEdnCoreRouting(user_data):  
    try:
        FetchEdnCoreRoutingFunc(user_data)
        return jsonify("Success"), 200
        
    except Exception as e:
        traceback.print_exc()
        print(f"Exception occured when fetching Core Routing {e}", file=sys.stderr)
        return jsonify("Failure"), 500

def FetchEdnCoreRoutingFunc(user_data):
    ednList = []

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query_string = "select device_id, ne_ip_address, sw_type, site_id from seed_table where ne_ip_address = '10.64.150.151';" 
    result = db.session.execute(query_string)
    
    for row in result:
        ednDict = {}
        print("Software type is:", row[2], file=sys.stderr)

        siteObj = Phy_Table.query.filter_by(site_id=row[3]).first()
        if siteObj:
            ednDict['region']= siteObj.region 
        else:
            ednDict['region']= ''
            
        
        ednDict['device_id'] = row[0]
        ednDict['device_ip'] = row[1]
        if 'IOS' in row[2]:
            ednDict['sw_type'] = 'ios-xr'
        else:
            ednDict['sw_type'] = row[2]
        ednDict['site_id'] = row[3]
        ednDict['user_id'] = user_data['user_id']
        
        ednDict['time']= current_time
        
        ednList.append(ednDict)
    
    try:
        routing= EDNCOREROUTING()
    except Exception as e:
        traceback.print_exc()
        print(f"Exception Occured In EDN Core Routing {e}", file=sys.stderr)

    #Update Script Status
    
    ednStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script=="EDN-CORE-ROUTING").first()

    try:
        ednStatus.script = "EDN-CORE-ROUTING"
        ednStatus.status = "Running"
        ednStatus.creation_date= current_time
        ednStatus.modification_date= current_time
        
        InsertData(ednStatus)
    
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        print(f"Error while updating script status {e}", file=sys.stderr)

    try:
        
        routing.getEdnCoreRouting(ednList)
    except Exception as e:
        print(e, file=sys.stderr)
   
    try:
        ednStatus.script = "EDN-CORE-ROUTING"
        ednStatus.status = "Completed"
        ednStatus.creation_date= current_time
        ednStatus.modification_date= current_time
        db.session.add(ednStatus)
        db.session.commit() 
    
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        print(f"Error while updating script status {e}", file=sys.stderr)

@app.route("/getEdnCoreRoutingScriptStatus", methods = ['GET'])
@token_required
def GetEdnCoreRoutingScriptStatus(user_data):
    ednCoreRouting={}
    
    #Getting status of script
    script_status=""
    script_modifiation_date=""
    ednCoreStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "EDN-CORE-ROUTING").first()
    if ednCoreStatus:
        script_status= ednCoreStatus.status
        script_modifiation_date= str(ednCoreStatus.modification_date)
    ednCoreRouting["fetch_status"] = script_status
    ednCoreRouting["fetch_date"]= script_modifiation_date

    content = gzip.compress(json.dumps(ednCoreRouting).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response

@app.route("/getAllEdnCoreRouting", methods = ['GET'])
@token_required
def GetAllEdnCoreRouting(user_data):
    ObjList=[]
    objs = db.session.execute('SELECT * FROM edn_core_routing WHERE creation_date = (SELECT max(creation_date) FROM edn_core_routing)')
    
    for obj in objs:
        dataDict= {}
        dataDict['edn_core_routing_id']= obj[0]
        dataDict['device_ip'] = obj[1]
        dataDict['device_id'] = obj[2]
        dataDict['subnet'] = obj[3]
        dataDict['route_type'] = obj[4]
        dataDict['next_hop'] = obj[5]
        dataDict['originated_from_ip'] = obj[6]
        dataDict['originator_name'] = obj[7]
        dataDict['route_age'] = obj[8]
        dataDict['process_id'] = obj[9]
        dataDict['cost'] = obj[10]
        dataDict['outgoing_interface'] = obj[11]
        dataDict['creation_date'] = str(obj[12])
        dataDict['modification_date'] = str(obj[13])
        dataDict['region'] = str(obj[14])
        dataDict['site_id'] = str(obj[15])
        dataDict['created_by']=  obj[16]
        dataDict['modified_by']=  obj[17]
        ObjList.append(dataDict)

    content = gzip.compress(json.dumps(ObjList).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response

@app.route('/getAllEdnCoreRoutingDates',methods=['GET'])
@token_required
def GetAllEdnCoreRoutingDates(user_data):

    dates = []
    queryString = "select distinct(creation_date) from edn_core_routing ORDER BY creation_date DESC;"
    
    result = db.session.execute(queryString)
        
    for row in result:                  
        print(row[0],file=sys.stderr)     
        dates.append(row[0])    

    return jsonify(dates), 200

@app.route("/getAllEdnCoreRoutingByDate", methods = ['POST'])
@token_required
def GetAllEdnCoreRoutingByDate(user_data):
        ObjList=[]

        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)

        objs = db.session.execute(f"SELECT * FROM edn_core_routing WHERE creation_date = '{current_time}' ")
        
        for obj in objs:
            dataDict= {}
            dataDict['edn_core_routing_id']= obj[0]
            dataDict['device_ip'] = obj[1]
            dataDict['device_id'] = obj[2]
            dataDict['subnet'] = obj[3]
            dataDict['route_type'] = obj[4]
            dataDict['next_hop'] = obj[5]
            dataDict['originated_from_ip'] = obj[6]
            dataDict['originator_name'] = obj[7]
            dataDict['route_age'] = obj[8]
            dataDict['process_id'] = obj[9]
            dataDict['cost'] = obj[10]
            dataDict['outgoing_interface'] = obj[11]
            dataDict['creation_date'] = str(obj[12])
            dataDict['modification_date'] = str(obj[13])
            dataDict['region'] = str(obj[14])
            dataDict['site_id'] = str(obj[15])
            dataDict['created_by']=  obj[16]
            dataDict['modified_by']=  obj[17]
            ObjList.append(dataDict)

        content = gzip.compress(json.dumps(ObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response

