import gzip
import sys, json
import traceback
from flask_jsonpify import jsonify
from flask import request, make_response, Response
from app import app ,db , tz
from app.models.inventory_models import Access_Points_Table, INVENTORY_SCRIPTS_STATUS
from sqlalchemy import func
from datetime import datetime
from app.middleware import token_required
from app.ap_scripts.ap import ACCESSPOINTSPuller
from app.models.inventory_models import Seed

def InsertData(obj):
    #add data to db
    try:
        #obj.creation_date= datetime.now(tz)
        #obj.modification_date= datetime.now(tz)
        db.session.add(obj)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong in Database Insertion {e}", file=sys.stderr)

    return True

def UpdateData(obj):
    #add data to db
    #print(obj, file=sys.stderr)
    try:
        #obj.modification_date= datetime.now(tz)
        db.session.merge(obj)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong in Database Updation {e}", file=sys.stderr)
    
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

    return result

def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%d-%m-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

@app.route("/fetchAccesspoints", methods = ['GET'])
@token_required
def FetchAccesspoints(user_data):
    
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        try:
            FetchAccesspointsFunc(user_data)
            return jsonify({'response': "success","code":"200"})
        except Exception as e:
            print(f"Error Occured while fetching Accesspoints {e}", file=sys.stderr)
            traceback.print_exc()
            return jsonify({'failed': "success","code":"500"}) 
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchAccesspointsFunc(user_data):
    wlcList=[]
    try:
        print("Called Fetch of Access Points", file=sys.stderr)
        #query_string = "select ne_ip_address from seed_table where `sw_type` = 'WLC';"  
        devices= Seed.query.filter_by(sw_type="WLC").filter_by(operation_status='Production').all()
        #devices= Seed.query.filter_by(ne_ip_address="10.78.104.52").all()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if devices:
            #Update Script Status
            accessPointsStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "ACCCESS-POINTS").first()
            try:
                accessPointsStatus.script = "ACCCESS-POINTS"
                accessPointsStatus.status = "Running"
                accessPointsStatus.creation_date= current_time
                accessPointsStatus.modification_date= current_time
                db.session.add(accessPointsStatus)
                db.session.commit() 
            except Exception as e:
                db.session.rollback()
                print(f"Error while updating script status {e}", file=sys.stderr)

            for device in devices:
                #time= datetime.now(tz)
                
                with open('app/cred.json') as inventory:
                    inv = json.loads(inventory.read())
                        
                wlcDevice = {}
                wlcDevice['ip'] = device.ne_ip_address
                wlcDevice['user'] = inv['WLC']['user']
                wlcDevice['pwd']= inv['WLC']['pwd']
                wlcDevice['device']= device
                wlcDevice['device_id']= device.device_id
                wlcDevice['time']= current_time
                wlcDevice['login_user']= user_data['user_id']
                wlcList.append(wlcDevice)
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                access_points= ACCESSPOINTSPuller()
                access_points_data= access_points.get_inventory_data(wlcList)
        
            except Exception as e:
                print(f"Error in Fetching Accesspoints {e}", file=sys.stderr)

            print("Updating Status of AP's which are not present in current fetch", file=sys.stderr)
            try:
                abseAps= db.session.execute(f"select access_point_id, status from access_points_table where MODIFICATION_DATE!=(select max(MODIFICATION_DATE) from access_points_table);")
                for row in abseAps:
                    ap_id = row[0]
                    status = row[1]
                    absentAps= db.session.execute(f"update access_points_table set status= 'Unregistered' where access_point_id='{ap_id}'")
                    db.session.commit()
                
                print('Successfully Updated Status of Phones which are not present in current fetch',file=sys.stderr)
            except Exception as e:
                print('Error in Status of Phones which are not present in current fetch',file=sys.stderr)
    
                
            #Update Script Status
            accessPointsStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "ACCCESS-POINTS").first()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                accessPointsStatus.script = "ACCCESS-POINTS"
                accessPointsStatus.status = "Completed"
                accessPointsStatus.creation_date= current_time
                accessPointsStatus.modification_date= current_time
                db.session.add(accessPointsStatus)
                db.session.commit() 
            except Exception as e:
                db.session.rollback()
                print(f"Error while updating script status {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error in Fetching Accesspoints {e}", file=sys.stderr)
            
    print("Finished Accesspoints fetch", file=sys.stderr)

@app.route("/getAllAccesspoints", methods = ['GET'])
@token_required
def GetAllAccesspoints(user_Data):
    if True: #request.headers.get('X-Auth-Key') == session.get('token', None):
        try: 
            accessPointsList=[]
            accesspoints = Access_Points_Table.query.all()

            for accesspoint in accesspoints:
                accessPointDict={}
                accessPointDict['device_id'] = accesspoint.device_id
                accessPointDict['site_id'] = accesspoint.site_id
                accessPointDict['wlc_name'] = accesspoint.wlc_name
                accessPointDict['authentication'] = accesspoint.authentication
                #accessPointDict['rack_id'] = accesspoint.rack_id
                accessPointDict['ne_ip_address'] = accesspoint.ne_ip_address
                accessPointDict['device_name'] = accesspoint.device_name
                accessPointDict['software_version'] = accesspoint.software_version
                #accessPointDict['patch_version'] = accesspoint.patch_version
                accessPointDict['creation_date'] = FormatDate(accesspoint.creation_date)
                accessPointDict['modification_date'] = FormatDate(accesspoint.modification_date)
                accessPointDict['status'] = accesspoint.status
                #accessPointDict['device_ru'] = accesspoint.ru
                accessPointDict['department'] = accesspoint.department
                accessPointDict['section'] = accesspoint.section
                accessPointDict['criticality'] = accesspoint.criticality
                accessPointDict['function'] = accesspoint.function
                # accessPointDict['cisco_domain'] = accesspoint.cisco_domain
                accessPointDict['manufacturer'] = accesspoint.manufacturer
                # accessPointDict['hw_eos_date'] = FormatDate(accesspoint.hw_eos_date)
                # accessPointDict['hw_eol_date'] = FormatDate(accesspoint.hw_eol_date)
                # accessPointDict['sw_eos_date'] = FormatDate(accesspoint.sw_eos_date)
                # accessPointDict['sw_eol_date'] = FormatDate(accesspoint.sw_eol_date)
                # accessPointDict['virtual'] = accesspoint.virtual
                accessPointDict['rfs_date'] = FormatDate(accesspoint.rfs_date)
                # accessPointDict['authentication'] = accesspoint.authentication
                accessPointDict['serial_number'] = accesspoint.serial_number
                accessPointDict['pn_code'] = accesspoint.pn_code
                accessPointDict['tag_id'] = accesspoint.tag_id
                # accessPointDict['subrack_id_number'] = accesspoint.subrack_id_number
                accessPointDict['manufactuer_date'] = FormatDate(accesspoint.manufactuer_date)
                accessPointDict['hardware_version'] = accesspoint.hardware_version
                accessPointDict['max_power'] = accesspoint.max_power
                accessPointDict['site_type'] = accesspoint.site_type
                # accessPointDict['source'] = accesspoint.source
                # accessPointDict['stack'] = accesspoint.stack
                accessPointDict['contract_number'] = accesspoint.contract_number
                accessPointDict['contract_expiry'] = FormatDate(accesspoint.contract_expiry)
                accessPointDict['item_code'] = accesspoint.item_code
                accessPointDict['item_desc'] = accesspoint.item_desc
                accessPointDict['clei'] = accesspoint.clei
                # accessPointDict['domain'] = accesspoint.domain
                # accessPointDict['ims_status'] = accesspoint.ims_status
                accessPointDict['created_by'] = accesspoint.created_by
                accessPointDict['modified_by'] = accesspoint.modified_by

                accessPointsList.append(accessPointDict)

            return jsonify(accessPointsList), 200
        except Exception as e:
            print(f"Error Occured while getting Accesspoints {e}", file=sys.stderr)
            return jsonify([]), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editAccesspoints", methods = ['POST'])
@token_required
def EditAccesspoints(user_data):
    if True:#session.get('token', None):
        try:
            accessPointObj = request.get_json()
            iptPhoneObj = Access_Points_Table.query.with_entities(Access_Points_Table).filter_by(serial_number=accessPointObj.get("serial_number")).filter_by(wlc_name=accessPointObj.get("wlc_name")).first()
            print(type(iptPhoneObj), file=sys.stderr)
            if iptPhoneObj:
                #if accessPointObj['serial_number']:
                #    iptPhoneObj.serial_number = accessPointObj['serial_number']
                if accessPointObj['tag_id']:
                    iptPhoneObj.tag_id = accessPointObj['tag_id']
                if accessPointObj['rfs_date']:
                    iptPhoneObj.rfs_date = FormatStringDate(accessPointObj['rfs_date'])
                if accessPointObj['device_id']:
                    iptPhoneObj.device_id = accessPointObj['device_id']
                if accessPointObj['item_code']:
                    iptPhoneObj.item_code = accessPointObj['item_code']
                if accessPointObj['item_desc']:
                    iptPhoneObj.item_desc = accessPointObj['item_desc']
                if accessPointObj['clei']:
                    iptPhoneObj.clei = accessPointObj['clei']
                if accessPointObj['manufactuer_date']:
                    iptPhoneObj.manufactuer_date = FormatStringDate(accessPointObj['manufactuer_date'])
                if accessPointObj['max_power']:
                    iptPhoneObj.max_power = accessPointObj['max_power']
                if accessPointObj['contract_number']:
                    iptPhoneObj.contract_number = accessPointObj['contract_number']
                if accessPointObj['contract_expiry']:
                    iptPhoneObj.contract_expiry =FormatStringDate(accessPointObj['contract_expiry'])

                iptPhoneObj.modification_date= datetime.now(tz)
                iptPhoneObj.modified_by= user_data['user_id']
                UpdateData(iptPhoneObj)
            else:
                print("Access Point not found", file=sys.stderr)
                
            return jsonify({'response': "success","code":"200"})
        except Exception as e:
            print(f"Error Occured while editing Accesspoints {e}", file=sys.stderr)
            return jsonify({'response': "failed","code":"500"})

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/getAccesspointsFetchStatus", methods = ['GET'])
@token_required
def GetAccesspointsFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        accessPointData={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        accessPointStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "ACCCESS-POINTS").first()
        if accessPointStatus:
            script_status= accessPointStatus.status
            script_modifiation_date= str(accessPointStatus.modification_date)
        accessPointData["fetch_status"] = script_status
        accessPointData["fetch_date"]= script_modifiation_date
        content = gzip.compress(json.dumps(accessPointData).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

