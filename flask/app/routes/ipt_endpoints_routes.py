import gzip
import sys, json
import traceback
from flask_jsonpify import jsonify
from flask import request, make_response, Response
from app import app ,db , tz
from app.models.inventory_models import IPT_Endpoints_Table, INVENTORY_SCRIPTS_STATUS
from sqlalchemy import func
from datetime import datetime
from app.middleware import token_required
from app.ipt_endpoints.iptendpoints_inv import IPTENDPOINTSPuller
from app.models.inventory_models import FAILED_DEVICES_IPT_ENDPOINTS
import pandas as pd



from app.logger import Logger

iptlogger = Logger('ipt-endpoints').logger

def InsertData(obj):
    iptlogger.debug(f"Inserting Data to DB, Data is {obj}")
    #add data to db
    try:
        #obj.creation_date= datetime.now(tz)
        #obj.modification_date= datetime.now(tz)
        db.session.add(obj)
        db.session.commit()
        iptlogger.debug(f"Successfully Inserted Data to DB, Data is {obj}")
    except Exception as e:
        db.session.rollback()
        iptlogger.exception(f"Failed to Insert Data to DB, Data is {obj}, Error is {e}")
        print(f"Something else went wrong in Database Insertion {e}", file=sys.stderr)

    return True

def UpdateData(obj):
    #add data to db
    #print(obj, file=sys.stderr)
    iptlogger.debug(f"Updating Data to DB, Data is {obj}")
    try:
        #obj.modification_date= datetime.now(tz)
        db.session.merge(obj)
        db.session.commit()
        iptlogger.debug(f"Successfully Update Data to DB, Data is {obj}")
    except Exception as e:
        db.session.rollback()
        iptlogger.exception(f"Failed to Update Data to DB, Data is {obj}, Error is {e}")
        print(f"Something else went wrong in Database Update {e}", file=sys.stderr)
    
    return True


def FormatStringDate(date):
    print(date, file=sys.stderr)
    iptlogger.debug(f"Formatting String Date {date}")
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
        iptlogger.debug(f"Formatting String Date Success, Date was {date}, Result is: {result}")
    except Exception as e:
        result=datetime(2000, 1,1)
        iptlogger.exception(f"Formatting String Date Success, Date was {date}, Error is {e}")
        print("date format exception", file=sys.stderr)

    return result

def add_failed_devices_to_db(host, reason, time):
    iptlogger.info(f"Inserting IPT END Points Failed Device, Host: {host}, Reason: {reason}")
    pmFailedDb = FAILED_DEVICES_IPT_ENDPOINTS()
    
    try:
        pmFailedDb.ip_address = host
        pmFailedDb.device_id = host
        pmFailedDb.reason =reason
        pmFailedDb.date = time
        
        InsertData(pmFailedDb)
        iptlogger.info(f"Successfully Inserted IPT Endpoints Failed Device")
        print('Successfully added Failed device to the Database', file = sys.stderr)
        
    except Exception as e:
        iptlogger.exception(f"Failed to ADD IPT Endpoints Failed Device, Error is {e}")
        db.session.rollback()
        print(f"Error while inserting failed device data into DB {e}", file=sys.stderr)


def FormatDate(date):
    iptlogger.debug(f"Formatting Date {date}")
    if date is not None:
        result = date.strftime('%d-%m-%Y')
        iptlogger.debug(f"Formatting  Date Success, Date was {date}, Result is: {result}")
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)
        iptlogger.debug(f"Formatting Date Success, Date was {date}, Result is: {result}")



@app.route("/fetchIPTEndpoints", methods = ['GET'])
@token_required
def FetchIPTEndpoints(user_data):
    iptlogger.info(f"Fetch IPT Endpoints Started by User {user_data} ")
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        try:
            FetchIPTEndpointsFunc(user_data)
            iptlogger.info(f"Successfully Fetched IPT Endpoints, Started by User {user_data} ")
            return jsonify({'response': "success","code":"200"})
        except Exception as e:
            iptlogger.exception (f"Error Occured in Fetching IPT Endpoints, Started by User {user_data}, Error is {e}")
            print(f"Error Occured while fetching IPT Endpoints {e}", file=sys.stderr)
            traceback.print_exc()
            return jsonify({'failed': "success","code":"500"}) 
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def getEmptyTagsandSerialNumbers():
    tags=""
    iptlogger.info(f"Getting Tag Ids Count")
    query_string = "SELECT COUNT(*) FROM ipt_endpoints_table WHERE LENGTH(TRIM(tag_id)) > 0;"  
    result = db.session.execute(query_string)
    for row in result:
        tags=row[0]
    
    iptlogger.debug(f"Got Tag Ids Count, Count is {tags}")   

    serials=""
    iptlogger.info(f"Getting Serial Numbers Count")
    query_string = "SELECT COUNT(*) FROM ipt_endpoints_table WHERE LENGTH(TRIM(serial_number)) > 0;"  
    result = db.session.execute(query_string)
    for row in result:
        serials=row[0]
    iptlogger.debug(f"Got Serial Numbers Count, Count is {tags}")   
    return int(tags), int(serials)

def FetchIPTEndpointsFunc(user_data):

    iptlogger.debug(f"Succesfully Started IPT Endpoints Fetch Function, Started by User {user_data} ")
    callManagersList=[]
    
    try:
        iptlogger.info(f"Getting Call Managers")
         
        query_string = "select ne_ip_address, device_id from seed_table where `function` = 'Call Manager' and hostname not LIKE '%-PUB' and hostname not LIKE '%-TFTP'  and operation_status='Production';"  
        #query_string = "select ne_ip_address from seed_table where ne_ip_address = '10.41.158.4';"
        result = db.session.execute(query_string)
        
        time= datetime.now(tz)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        iptlogger.info(f"Loading IPT Endpoints Credential File")
        with open('app/cred.json') as inventory:
            inv = json.loads(inventory.read())
        
        iptlogger.info(f"Creating IPT Endpoints Call Managers dictionary")
        for row in result:
            callManagers = {}
            callManagers['ip'] = row[0]
            callManagers['device_id'] = row[1]
            callManagers['user'] = inv['IPT_ENDPOINT']['user']
            callManagers['pwd']= inv['IPT_ENDPOINT']['pwd']
            callManagers['auth-key']= inv['IPT_ENDPOINT']['auth-key']
            callManagers['time']= current_time
            
            callManagersList.append(callManagers)
        iptlogger.debug(f"IPT Endpoints Call Managers list is {callManagersList}")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #Update Script Status
        iptlogger.info(f"Getting IPT Endpoints Script Status")
        iptEndpointsStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "IPT-Endpoints").first()
        iptlogger.debug(f"IPT Endpoints Script Status is {iptlogger}")
        try:
            iptlogger.info(f"Updating IPT Endpoints Script Status to Running")
            iptEndpointsStatus.script = "IPT-Endpoints"
            iptEndpointsStatus.status = "Running"
            iptEndpointsStatus.creation_date= current_time
            iptEndpointsStatus.modification_date= current_time
            
            db.session.add(iptEndpointsStatus)
            db.session.commit() 
            iptlogger.info(f"Successfully Updated IPT Endpoints Script Status to Running")
        except Exception as e:
            db.session.rollback()
            iptlogger.exception(f"Failed to Update IPT Endpoints Script Status to Running, Error is {e}")
            print(f"Error while updating script status {e}", file=sys.stderr)

        iptlogger.debug(f"Creating IPT Endpoints Class Object")
        ipt_endpoint= IPTENDPOINTSPuller()
        iptlogger.info(f"Getting IPT Endpoints Inventory Data")
        ipt_endpoint_data= ipt_endpoint.get_inventory_data(callManagersList)
        iptlogger.info(f"Successfully Got IPT Endpoints  Inventory Data, Length is {len(ipt_endpoint_data)}")
        
        iptlogger.info(f"Getting  IPT Endpoints Publisher")
        query_string = "select ne_ip_address, device_id from seed_table where `function` = 'Call Manager' and hostname LIKE '%-PUB' and operation_status='Production';"  
        result = db.session.execute(query_string)
        iptlogger.info(f"Successfully Received IPT Endpoints Publisher")
        publisher_ip=""
        device_id=""
        iptlogger.debug(f"Creating IPT Endpoints Publisher Dictionary")
        for row in result:
            publisher_ip = row[0]
            device_id= row[1]
        host={}
        host["ip"]=publisher_ip
        host["device_id"]=device_id
        host["time"]=current_time
        iptlogger.debug(f"IPT Endpoints Publisher Dictionary is {host}")

        iptlogger.info(f"Getting IPT Endpoints Publisher API Data")
        ipt_api_data= ipt_endpoint.get_api_data(publisher_ip, inv['IPT_ENDPOINT_API']['user'], inv['IPT_ENDPOINT_API']['pwd'], ipt_endpoint_data, host)#ipt_endpoint.get_api_data(callManagersList)
        iptlogger.info(f"Received IPT Endpoints Publisher API Data, Length is {ipt_api_data}")
        
        print("Getting IPT Endpoints Phone Lines", file=sys.stderr) 
        iptlogger.info(f"Getting IPT Endpoints Phone Lines Data")
        ipt_api_data= ipt_endpoint.get_lines_data(publisher_ip, inv['IPT_ENDPOINT_API']['user'], inv['IPT_ENDPOINT_API']['pwd'], ipt_api_data, host)   
        iptlogger.info(f"Received IPT Endpoints Phone Lines Data, Length is {len(ipt_api_data)}")

        iptlogger.info(f"Parsing IPT Endpoints Data")
        #for callManager, callManagerData in ipt_endpoint_data.items():   
        for phone in ipt_api_data: 
            iptlogger.debug(f"Phone in IPT Endpoints Data is {phone}")
            iptEndpointObject = IPT_Endpoints_Table()
            phoneHostName = IPT_Endpoints_Table.query.with_entities(IPT_Endpoints_Table).filter_by(hostname=phone.get('hostname')).first()
            iptlogger.debug(f"Search Phone in IPT Endpoints Database, Hoat Name is {phoneHostName}")
            
            tagsBeforeUpdate, serialNumberBeforeUpdate= getEmptyTagsandSerialNumbers()
            if phoneHostName is not None:
                try:
                    iptEndpointObject.hostname = phoneHostName.hostname
                    if phone.get('ip_address', '') !="":
                        iptEndpointObject.ip_address = phone.get('ip_address', '')
                    if phone.get('mac_address', '') !="":
                        iptEndpointObject.mac_address = phone.get('mac_address', '')
                    if phone.get('user', '') !="":
                        iptEndpointObject.user = phone.get('user', '')
                    if phone.get('product_id', '') !="":
                        iptEndpointObject.product_id = phone.get('product_id', '')
                    if  phone.get('description', '') !="":
                        iptEndpointObject.description = phone.get('description', '')
                    if phone.get('firmware', '') !="":
                        iptEndpointObject.firmware = phone.get('firmware', '')
                    if phone.get('protocol', '') !="":
                        iptEndpointObject.protocol = phone.get('protocol', '')
                    if phone.get('calling_search_space', '') !="":
                        iptEndpointObject.calling_search_space = phone.get('calling_search_space', '')
                    if phone.get('device_pool_name', '') !="":
                        iptEndpointObject.device_pool_name = phone.get('device_pool_name', '')
                    if phone.get('location_name', '') !="":
                        iptEndpointObject.location_name = phone.get('location_name', '')
                    if phone.get('resource_list_name', '') !="":
                        iptEndpointObject.resource_list_name = phone.get('resource_list_name', '')
                    if phone.get('extensions', '') !="":
                        iptEndpointObject.extensions = phone.get('extensions', '')
                    if phone.get('status', '') !="":
                        iptEndpointObject.status = phone.get('status', '')  

                    iptEndpointObject.modification_date= time
                    iptEndpointObject.modified_by= user_data["user_id"]
                    print("Updated IPT Endpoints " + phone.get('hostname'), file=sys.stderr)
                    iptlogger.debug("Final Phone DB Object is  {iptEndpointObject}")
                    
                    UpdateData(iptEndpointObject)
                    iptlogger.debug("Updated Ipt Endpoints Phone")
                except Exception as e:
                    iptlogger.exception("Exception occured in Parsing Ipt Endpoints Phone, Error is: {e}")
                    add_failed_devices_to_db( phoneHostName.hostname, f"Error while Updating data into DB {e}", current_time)
            else:
                try:
                    iptEndpointObject.hostname = phone.get('hostname')
                    iptEndpointObject.ip_address = phone.get('ip_address', '')
                    iptEndpointObject.mac_address = phone.get('mac_address', '')
                    iptEndpointObject.user = phone.get('user', '')
                    iptEndpointObject.product_id = phone.get('product_id', '')
                    iptEndpointObject.description = phone.get('description', '')
                    iptEndpointObject.firmware = phone.get('firmware', '')
                    iptEndpointObject.protocol = phone.get('protocol', '')
                    iptEndpointObject.calling_search_space = phone.get('calling_search_space', '')
                    iptEndpointObject.device_pool_name = phone.get('device_pool_name', '')
                    iptEndpointObject.location_name = phone.get('location_name', '')
                    iptEndpointObject.resource_list_name = phone.get('resource_list_name', '')
                    iptEndpointObject.status = phone.get('status', '')
                    iptEndpointObject.extensions = phone.get('extensions', '')
                    iptEndpointObject.creation_date= time
                    iptEndpointObject.modification_date= time
                    iptEndpointObject.modified_by= user_data["user_id"]
                    iptEndpointObject.created_by= user_data["user_id"]
                    iptlogger.debug("Final Phone DB Object is  {iptEndpointObject}")
                    print("Inserted IPT Endpoints " +iptEndpointObject.hostname,file=sys.stderr)
                    InsertData(iptEndpointObject)
                    iptlogger.debug("Inserted Ipt Endpoints Phone")
                except Exception as e:
                    iptlogger.exception("Exception occured in Parsing Ipt Endpoints Phone, Error is: {e}")
                    add_failed_devices_to_db( phone.get('hostname'), f"Error while Inserting data into DB {e}", current_time)
            
            tagsAfterUpdate, serialNumberAfterUpdate= getEmptyTagsandSerialNumbers()
            
            if (tagsBeforeUpdate-tagsAfterUpdate!=0) or (serialNumberBeforeUpdate-serialNumberAfterUpdate!=0):
                iptlogger.info(25, f"IPT Endpoints Change in Static Values Count Detected during Insertion of data, Stats are, TBU: {tagsBeforeUpdate} , TAU {tagsAfterUpdate}, SBU {serialNumberBeforeUpdate}, SAU {serialNumberAfterUpdate}")
            print("IPT data successfully updated", file=sys.stderr)
            iptlogger.info("Finished IPT Endpoints Data Insert/Update in DB")
        
        print("Updating Status of Phones which are not present in current fetch", file=sys.stderr)
        iptlogger.info("Updating IPT Endpoints Data Removed Devices in DB")
        try:
            absentPhones= db.session.execute(f"select hostname, status from ipt_endpoints_table where MODIFICATION_DATE!=(select max(MODIFICATION_DATE) from ipt_endpoints_table);")
            iptlogger.debug(f"Successfully Get IPT Endpoints devices which need to be removed")
            
            for row in absentPhones:
                
                hostname = row[0]
                iptlogger.debug(f"Removing IPT Endpoints Phone {hostname}")
                status = row[1]
                #if status=="Registered":
                absentPhones= db.session.execute(f"update ipt_endpoints_table set status= 'Removed' where hostname='{hostname}'")
                db.session.commit()
                iptlogger.debug(f"Successfully Removed IPT Endpoints Phone {hostname}")

            iptlogger.info(f"Successfully Removed IPT Endpoints Phones which are not Present in Current Fetch ")
            print('Successfully Updated Status of Phones which are not present in current fetch',file=sys.stderr)
        
            tagsAfterRemove, serialNumberAfterRemove= getEmptyTagsandSerialNumbers()
            
            if (tagsAfterUpdate-tagsAfterRemove!=0) or (serialNumberAfterUpdate-serialNumberAfterRemove!=0):
                iptlogger.info(25, f"IPT Endpoints Change in Static Values Count Detected during Insertion of data, Stats are, TAU {tagsAfterUpdate}, TAR {tagsAfterRemove} , SAU {serialNumberAfterUpdate}, SAR {serialNumberAfterRemove}")

        except Exception as e:
            iptlogger.exception(f"Error Occured in Removing IPT Endpoints Phones which are not Present in Current Fetch, Error is {e} ")
            print('Error in Status of Phones which are not present in current fetch',file=sys.stderr)
            add_failed_devices_to_db( "Any", f"Error while Removing Phones {e}", current_time)
        
    except Exception as e:
        traceback.print_exc()
        iptlogger.exception(f"Error In Fetching IPT Endpoints, Error is {e}")
        print(f"Error in Fetching IPT Endpoints {e}", file=sys.stderr)
    
    #Update Script Status
    iptlogger.info(f"Getting IPT Endpoints Script Status")
           
    iptEndpointsStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "IPT-Endpoints").first()
    iptlogger.debug(f"IPT Endpoints Script Status is {iptlogger}")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:

        iptEndpointsStatus.script = "IPT-Endpoints"
        iptEndpointsStatus.status = "Completed"
        iptEndpointsStatus.creation_date= current_time
        iptEndpointsStatus.modification_date= current_time
        iptlogger.info(f"Updating IPT Endpoints Script Status to Completed")
        db.session.add(iptEndpointsStatus)
        db.session.commit() 
        iptlogger.info(f"Successfully Updated IPT Endpoints Script Status to Completed")
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)
        traceback.print_exc()
        iptlogger.exception(f"Failed to Update IPT Endpoints Script Status to Completed, Error is {e}")
    
    iptlogger.info(f"Successfully Completed IPT Endpoints Fetch, Initiated By User {user_data}") 
    print("Finished IPT Endpoints fetch", file=sys.stderr)

@app.route("/getAllIPTEndpoints", methods = ['GET'])
@token_required
def GetAllIPTEndpoints(user_data):
    
    iptlogger.info(f"Loading IPT Endpoints by User {user_data} ")

    if True: #request.headers.get('X-Auth-Key') == session.get('token', None):
        try: 
            endpoints=[]

            endpoints= GetAllIPTEndpointsFunc(user_data)
            
            iptlogger.debug(f"Loaded IPT Endpoints by User {user_data}, Count is {len(endpoints)}")
            iptlogger.info(f"Successfully Loaded IPT Endpoints by User {user_data} ")
            return jsonify(endpoints), 200
            
        except Exception as e:
            print(f"Error Occured while getting IPT Endpoints {e}", file=sys.stderr)
            iptlogger.exception(f"Error in Loading IPT Endpoints by User {user_data}, Error is {e}")
            return jsonify([]), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def GetAllIPTEndpointsFunc(user_data):
    
    iptlogger.debug(f"Loading IPT Endpoints by User {user_data} ")
    try: 
        iptEndpointsList=[]
        endpoints = IPT_Endpoints_Table.query.all()

        iptlogger.debug(f"Loading IPT Endpoints from Data base by {user_data}, Length of data is {len(endpoints)} ")
        for endpoint in endpoints:
            try:

                iptEndpointDict= {}
                iptEndpointDict['hostname']=endpoint.hostname
                iptEndpointDict['ip_address'] = endpoint.ip_address
                iptEndpointDict['mac_address'] = endpoint.mac_address
                iptEndpointDict['user'] = endpoint.user
                iptEndpointDict['product_id'] = endpoint.product_id 
                iptEndpointDict['description'] = endpoint.description
                iptEndpointDict['protocol'] = endpoint.protocol
                iptEndpointDict['calling_search_space'] = endpoint.calling_search_space
                iptEndpointDict['device_pool_name'] = endpoint.device_pool_name
                iptEndpointDict['location_name'] = endpoint.location_name
                iptEndpointDict['resource_list_name'] = endpoint.resource_list_name
                iptEndpointDict['firmware'] = endpoint.firmware
                iptEndpointDict['status'] = endpoint.status
                iptEndpointDict['serial_number'] = endpoint.serial_number
                iptEndpointDict['tag_id'] = endpoint.tag_id
                if endpoint.rfs_date != None:
                    iptEndpointDict['rfs_date'] = endpoint.rfs_date

                iptEndpointDict['extensions'] = endpoint.extensions
                iptEndpointDict['creation_date'] = endpoint.creation_date
                iptEndpointDict['modification_date'] = endpoint.modification_date
                iptEndpointDict['created_by'] = endpoint.created_by
                iptEndpointDict['modified_by'] = endpoint.modified_by
                
                iptEndpointsList.append(iptEndpointDict)
            except Exception as e:
                iptlogger.exception(f"Error in Loading IPT Endpoints by User {user_data}, Error is {e}")
                pass
                # print(f"Error Occured while getting IPT Endpoints {e}", file=sys.stderr)

        return iptEndpointsList
        
    except Exception as e:
        print(f"Error Occured while getting IPT Endpoints {e}", file=sys.stderr)
        iptlogger.exception(f"Error in Loading IPT Endpoints by User {user_data}, Error is {e}")
        return []

@app.route("/editIPTEndpoints", methods = ['POST'])
@token_required
def EditIPTEndpoints(user_data):


    iptlogger.info(f"Editing IPT Endpoints by User {user_data}")
    
    if True:#session.get('token', None):
        try:
            
            iptEndpointObj = request.get_json()

            iptlogger.debug(f"Editing IPT Endpoints by User {user_data}, Payload is: {iptEndpointObj}")
            
            iptPhoneObj = IPT_Endpoints_Table.query.with_entities(IPT_Endpoints_Table).filter_by(hostname=iptEndpointObj.get("hostname")).first()
            #print(type(iptPhoneObj), file=sys.stderr)
            iptlogger.debug(f"Editing IPT Endpoints by User {user_data}, Database Object is: {iptEndpointObj}")
            
            if iptEndpointObj['serial_number']:
                if str.isspace(iptEndpointObj['serial_number']):
                    iptlogger.log(25, f"Empty Serial Number IPT Endpoints by User {user_data}")

                iptPhoneObj.serial_number = iptEndpointObj['serial_number']

            if iptEndpointObj['tag_id']:
                if str.isspace(iptEndpointObj['tag_id']):
                    iptlogger.log(25, f"Empty Tag Id in IPT Endpoints by User {user_data}")
                iptPhoneObj.tag_id = iptEndpointObj['tag_id']
            
            if iptEndpointObj['rfs_date']:
                if str.isspace(iptEndpointObj['rfs_date']):
                    iptlogger.log(25, f"Empty RFS Date in IPT Endpoints by User {user_data}")

                iptPhoneObj.rfs_date = FormatStringDate(iptEndpointObj['rfs_date'])
            
            iptPhoneObj.modification_date= datetime.now(tz)
            iptPhoneObj.modified_by= user_data["user_id"]
            UpdateData(iptPhoneObj)
            iptlogger.info(f"Successfully Edited IPT Endpoints by User {user_data}")
            
            return jsonify({'response': "success","code":"200"})
        except Exception as e:
            iptlogger.exception(f"Failed to Edit IPT Endpoint by User {user_data} , Error is {e}")
            print(f"Error Occured while editing IPT Endpoints {e}", file=sys.stderr)
            return jsonify({'response': "failed","code":"500"})

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route("/getIptEndpointsFetchStatus", methods = ['GET'])
@token_required
def GetIptEndpointsFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        iptEndpointData={}
        iptlogger.info(f"Getting IPT Endpoints FetchStatus by User {user_data}")
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        iptEndpointStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "IPT-Endpoints").first()
        iptlogger.debug(f"IPT Endpoints Fetch Status by User {user_data}, status is {iptEndpointStatus}")
        if iptEndpointStatus:
            script_status= iptEndpointStatus.status
            script_modifiation_date= str(iptEndpointStatus.modification_date)
        iptEndpointData["fetch_status"] = script_status
        iptEndpointData["fetch_date"]= script_modifiation_date
        content = gzip.compress(json.dumps(iptEndpointData).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        iptlogger.debug(f"Successfully Sent IPT ENdpoints Fetch status to  User {user_data}, status is {iptEndpointData}")
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getIptEndpoints", methods = ['GET'])
@token_required
def GetRegisteredSoftPhones(user_data):
    iptlogger.debug(f"Loading Custom IPT Endpoints data by user  User {user_data}")
    if True:
        try:
            queryString=""
            filter = request.args.get('filter')
            iptlogger.debug(f"Custom IPT Endpoints data Filter is {filter}")
            
            if filter=='soft_phones':

                queryString = f"select * from ipt_endpoints_table where hostname not like '%SEP%' and STATUS='Registered';"
            elif filter== 'registered_phones':
                queryString = f"select * from ipt_endpoints_table where hostname like 'SEP%' and STATUS='Registered';"
            elif filter== 'total_line':
                queryString = f"select * from ipt_endpoints_table where extensions is not null and extensions!='';"
            elif filter== 'registered_ex90':
                queryString = f"select * from ipt_endpoints_table where PRODUCT_ID='Cisco TelePresence EX90' and STATUS='Registered';"
            elif filter== 'registered_dx80':
                queryString = f"select * from ipt_endpoints_table where PRODUCT_ID='Cisco Webex DX80' and STATUS='Registered';"
            elif filter=='registered_deskpro':
                queryString = f"select * from ipt_endpoints_table where PRODUCT_ID='Cisco Webex Desk Pro' and STATUS='Registered';"
            elif filter=='registered_webex':
                queryString = f"select * from ipt_endpoints_table where PRODUCT_ID='Cisco Webex Board 55' or PRODUCT_ID='Cisco Webex Room 70 Single' or PRODUCT_ID='Cisco Webex Board Pro 55'or PRODUCT_ID='Cisco Webex Room 55' and STATUS='Registered';"
            else:
                if queryString=="":
                    print("REQUEST NOT FOUND", file=sys.stderr)
                    iptlogger.debug(f"Custom IPT Endpoints Invalid Request")
                    traceback.print_exc()
                    return "REQUEST NOT FOUND",500
                    
            iptlogger.debug(f"Custom IPT Endpoints Getting DB Data")
            result = db.session.execute(queryString)
            objList = []
            for row in result:
                objDict = {}
                objDict['hostname'] =row[0]
                objDict['ip_address'] =row[1]
                objDict['mac_address'] =row[2]
                objDict['user'] =row[3] 
                objDict['product_id'] =row[4]
                objDict['description'] =row[5]
                objDict['firmware'] =row[6]
                objDict['creation_date'] =row[7]
                objDict['modification_date'] =row[8]
                objDict['serial_number'] =row[9]
                objDict['rfs_date'] =row[10]
                objDict['tag_id'] =row[11]
                objDict['protocol'] =row[12]
                objDict['calling_search_space'] =row[13]
                objDict['device_pool_name'] =row[14]
                objDict['location_name'] =row[15]
                objDict['resource_list_name'] =row[16]
                objDict['status'] =row[17]
                objDict['extensions'] =row[18]
                objDict['created_by'] =row[19]
                objDict['modified_by'] =row[20]
                objList.append(objDict)
            print(objList,file=sys.stderr)
            iptlogger.debug(f"Custom IPT Endpoints Successfully Loaded")
            return jsonify(objList),200
                           
        except Exception as e:
            iptlogger.exception(f"Failed to Load IPT Endpoints Custom Data, Error is {e}")
            print(str(e),file=sys.stderr)
            traceback.print_exc()
            return str(e),500
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


# @app.route("/getRegisteredPhones", methods = ['GET'])
# @token_required
# def GetRegisteredPhones(user_data):
#     if True:
#         try:
#             pass
#         except Exception as e:
#             print(str(e),file=sys.stderr)
#             traceback.print_exc()
#             return str(e),500
#     else: 
#         print("Authentication Failed", file=sys.stderr)
#         return jsonify({'message': 'Authentication Failed'}), 401

# @app.route("/totalNumberOfLines", methods = ['GET'])
# @token_required
# def TotalNumberOfLines(user_data):
#     if True:
#         try:
#             pass
#         except Exception as e:
#             print(str(e),file=sys.stderr)
#             traceback.print_exc()
#             return str(e),500
#     else: 
#         print("Authentication Failed", file=sys.stderr)
#         return jsonify({'message': 'Authentication Failed'}), 401

# @app.route("/registeredEx90", methods = ['GET'])
# @token_required
# def RegisteredEx90(user_data):
#     if True:
#         try:
#             pass
#         except Exception as e:
#             print(str(e),file=sys.stderr)
#             traceback.print_exc()
#             return str(e),500
#     else: 
#         print("Authentication Failed", file=sys.stderr)
#         return jsonify({'message': 'Authentication Failed'}), 401

# @app.route("/registeredDx80", methods = ['GET'])
# @token_required
# def RegisteredDx80(user_data):
#     if True:
#         try:
#             pass
#         except Exception as e:
#             print(str(e),file=sys.stderr)
#             traceback.print_exc()
#             return str(e),500
#     else: 
#         print("Authentication Failed", file=sys.stderr)
#         return jsonify({'message': 'Authentication Failed'}), 401

# @app.route("/registeredDeskpro", methods = ['GET'])
# @token_required
# def RegisteredDeskpro(user_data):
#     if True:
#         try:
#             pass
#         except Exception as e:
#             print(str(e),file=sys.stderr)
#             traceback.print_exc()
#             return str(e),500
#     else: 
#         print("Authentication Failed", file=sys.stderr)
#         return jsonify({'message': 'Authentication Failed'}), 401

# @app.route("/registeredWebex", methods = ['GET'])
# @token_required
# def RegisteredWebex(user_data):
#     if True:
#         try:
#             pass
#         except Exception as e:
#             print(str(e),file=sys.stderr)
#             traceback.print_exc()
#             return str(e),500
#     else: 
#         print("Authentication Failed", file=sys.stderr)
#         return jsonify({'mes

def iptEndPointsExcelBackup():
    iptlogger.info(f"Creating IPT Endpoints Backup ")
    try: 
        iptEndpointsList=[]
        endpoints = IPT_Endpoints_Table.query.all()
        for endpoint in endpoints:
            try:

                iptEndpointDict= {}
                iptEndpointDict['hostname']=endpoint.hostname
                iptEndpointDict['ip_address'] = endpoint.ip_address
                iptEndpointDict['mac_address'] = endpoint.mac_address
                iptEndpointDict['user'] = endpoint.user
                iptEndpointDict['product_id'] = endpoint.product_id 
                iptEndpointDict['description'] = endpoint.description
                iptEndpointDict['protocol'] = endpoint.protocol
                iptEndpointDict['calling_search_space'] = endpoint.calling_search_space
                iptEndpointDict['device_pool_name'] = endpoint.device_pool_name
                iptEndpointDict['location_name'] = endpoint.location_name
                iptEndpointDict['resource_list_name'] = endpoint.resource_list_name
                iptEndpointDict['firmware'] = endpoint.firmware
                iptEndpointDict['status'] = endpoint.status
                iptEndpointDict['serial_number'] = endpoint.serial_number
                iptEndpointDict['tag_id'] = endpoint.tag_id
                if endpoint.rfs_date != None:
                    iptEndpointDict['rfs_date'] = endpoint.rfs_date

                iptEndpointDict['extensions'] = endpoint.extensions
                iptEndpointDict['creation_date'] = endpoint.creation_date
                iptEndpointDict['modification_date'] = endpoint.modification_date
                iptEndpointDict['created_by'] = endpoint.created_by
                iptEndpointDict['modified_by'] = endpoint.modified_by
                
                iptEndpointsList.append(iptEndpointDict)
            except Exception as e:
                pass
                # print(f"Error Occured while getting IPT Endpoints {e}", file=sys.stderr)
        ###
        iptlogger.info(f"Successfully Get Data from DB, Length is {len(iptEndpointsList)}")

        iptlogger.info(f"Generating Excel File")
        #Generating Excel
        df = pd.DataFrame(iptEndpointsList)

        now = datetime.now()

        # Format the date and time to include in the file name
        file_name = "ipt-endpoint-backup" + now.strftime("_%Y-%m-%d_%H-%M-%S") + ".xlsx"

        # Create an Excel file from the DataFrame
        df.to_excel("logs/"+file_name, index=False)

        iptlogger.info(f"Successfully Generated Excel Backup, File Name is: {file_name}")
        
        
    except Exception as e:
        print(f"Error Occured while getting IPT Endpoints {e}", file=sys.stderr)
        iptlogger.exception(f"Error in Generating IPT Endpoints Backup, Error is {e}")
    



@app.route('/testIpt',methods = ['GET'])
def TestIpt():
    queryString = "select distinct (EXTENSIONS) from ipt_endpoints_table where extensions is not null and extensions!='';"
    result = db.session.execute(queryString)
    objList = []
    
    for row1 in result:
        extension = row1[0]
        queryString1 = f"select * from ipt_endpoints_table where extensions='{extension}';"
        result1 = db.session.execute(queryString1)
        count = 0
        for row in result1:
            objDict = {}
            objDict['hostname'] =row[0]
            objDict['ip_address'] =row[1]
            objDict['mac_address'] =row[2]
            objDict['user'] =row[3] 
            objDict['product_id'] =row[4]
            objDict['description'] =row[5]
            objDict['firmware'] =row[6]
            objDict['creation_date'] =row[7]
            objDict['modification_date'] =row[8]
            objDict['serial_number'] =row[9]
            objDict['rfs_date'] =row[10]
            objDict['tag_id'] =row[11]
            objDict['protocol'] =row[12]
            objDict['calling_search_space'] =row[13]
            objDict['device_pool_name'] =row[14]
            objDict['location_name'] =row[15]
            objDict['resource_list_name'] =row[16]
            objDict['status'] =row[17]
            objDict['extensions'] =row[18]
            objDict['created_by'] =row[19]
            objDict['modified_by'] =row[20]
            objList.append(objDict)
    return str(len(objList)),200

