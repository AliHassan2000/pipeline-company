# from crypt import methods
from crypt import methods
from http.client import responses
import json
from sqlalchemy import and_
import mimetypes
from pickle import TRUE
from traceback import print_exc
import traceback
from unittest import result
from urllib import response
from flask import request
from app import app,db, inv_engine
from flask_jsonpify import jsonify
from app.models.inventory_models import EDN_IOS_TRACKER, Device_Table, User_Table, IP_ASSIGNMENT_TRACKER, IP_CLEARANCE_TRACKER, IPT_Endpoints_Table, EDN_DEVICE_POWEROFF_TRACKER, EDN_HANDBACK_TRACKER, EDN_HANDOVER_TRACKER, EDN_PMR_TRACKER, IPT_RMA_TRACKER, Attachments, TableMappings, SNAGS, EDN_CMDB_TRACKER
from app.middleware import token_required
import sys
# from crypt import methods
from datetime import date, datetime
from werkzeug.utils import secure_filename
import uuid
import os
from flask import send_file, send_from_directory, make_response
from os.path import isfile


def FormatDate(date):
    #print(date, addIosTrackerfile=sys.stderr)
    if date is not None:
        result = date.strftime('%d-%m-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

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

def InsertData(obj):
    #add data to db
    try:        
        db.session.add(obj)
        db.session.commit()
        db.session.refresh(obj)
        return obj


    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong in Database Insertion {e}", file=sys.stderr)

    #return id

def UpdateData(obj):
    #add data to db
    try:
        db.session.flush()

        db.session.merge(obj)
        db.session.commit()
        #db.session.refresh(obj)

    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong during Database Update {e}", file=sys.stderr)
    
    return True

@app.route('/', methods=['GET'])
def Hello():
    return jsonify('UNIFIED ROUTES'),200


# EDN IOS TRACKER #

@app.route('/iosTracker', methods=['POST'])
@token_required
def AddTracker(user_data):
    if True:
        try:
            trackerObj = request.get_json()
            trackerList = []
            response = False
            response1 = False
            trck = ''
            for obj in trackerObj:
                try:
                    objDict = {}
                    objDict['device_id'] = obj['device_id']
                    objDict['new_os_version'] = obj['new_os_version']
                    objDict['assignee'] = obj['assignee']
                    # objDict['schedule'] = obj['schedule']
                    objDict['schedule'] = FormatStringDate(obj['schedule'])
                    if "status" in obj:
                        objDict["status"] = obj['status']
                    else:
                        objDict["status"] = ''
                    if "crq" in obj:
                        objDict["crq"] = obj['crq']
                    else:
                        objDict["crq"] = ''
                    if "remarks" in obj:
                        objDict["remarks"] = obj['remarks']
                    else:
                        objDict["remarks"] = ''
                    queryString = f"select ne_ip_address, site_id, pn_code, software_version from device_table where DEVICE_ID='{obj['device_id']}';"
                    result = inv_engine.execute(queryString)

                    for row in result:
                        objDict['ip_address'] = row[0]
                        objDict['site_id'] = row[1]
                        objDict['pid'] = row[2]
                        objDict['current_os_version'] = row[3]

                    queryString2 = f"select region from phy_table where SITE_ID='{objDict['site_id']}';"
                    result2 = inv_engine.execute(queryString2)

                    for row in result2:
                        objDict['region'] = row[0]
                    
                    queryString1 = f"select sw_type from seed_table where DEVICE_ID='{obj['device_id']}';"
                    result1 = inv_engine.execute(queryString1)

                    for row in result1:
                        objDict['os_type'] = row[0]


                    trackerList.append(objDict)

                except Exception as e:
                    traceback.print_exc()
                    print(f"Error Adding Data: {e}", file=sys.stderr)
                
            print(trackerList, file=sys.stderr)

            for objs in trackerList:
                try:
                    tracker = EDN_IOS_TRACKER()
                    tracker.device_id = objs['device_id']
                    tracker.new_os_version = objs.get('new_os_version', "")
                    tracker.assignee = objs.get('assignee', "")
                    tracker.schedule = objs.get('schedule', "")
                    tracker.status = objs.get('status', "")
                    tracker.crq = objs.get('crq', "")
                    tracker.remarks = objs.get('remarks', "")
                    tracker.ip_address = objs.get('ip_address', "")
                    tracker.site_id = objs.get('site_id', "")
                    tracker.pid = objs.get('pid',"")
                    tracker.current_os_version = objs.get('current_os_version', "")
                    tracker.region = objs.get('region', "")
                    tracker.os_type = objs.get('os_type', "")

                    print("IOS Tracker", tracker, file=sys.stderr)

                    if EDN_IOS_TRACKER.query.with_entities(EDN_IOS_TRACKER.device_id).filter_by(device_id=obj['device_id']).first() is not None:
                        tracker.id = EDN_IOS_TRACKER.query.with_entities(EDN_IOS_TRACKER.id).filter_by(device_id=obj['device_id']).first()[0]
                        
                        time = datetime.now()
                        tracker.modified_by= user_data['user_id']
                        tracker.modification_date= time


                        UpdateData(tracker)
                        print("Data Updated For Device ID:"+ ' ' +obj['device_id'], file=sys.stderr)
                        
                        
                        response = True
                        trck = tracker.device_id
                        
                    else:
                        time = datetime.now()
                        tracker.created_by= user_data['user_id']
                        tracker.modified_by= user_data['user_id']
                        tracker.creation_date=time
                        tracker.modification_date= time

                        InsertData(tracker)
                        print("Data Inserted Into DB", file=sys.stderr)
                        response1 = True
                        trck = tracker.device_id

                except Exception as e:
                    print(f"Error Adding Data: {e}", file=sys.stderr)


            if response==True:
                return jsonify({'Response': f"{trck} Successfully Updated"}),200
            if response1==True:
                return jsonify({'Response': f"{trck} Successfully Inserted"}),200

        except Exception as e:
            traceback.print_exc()
            return jsonify({f"Response": f"Failed to Update/Insert {e}"}),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/iosTracker/<int:id>', methods=['PUT'])
def UpdateTracker(id):
    try:
        trackerObj = request.get_json()
        objs = EDN_IOS_TRACKER.query.with_entities(EDN_IOS_TRACKER).filter_by(id= id).first()

        if objs:
            if "device_id" in trackerObj:
                objs.device_id = trackerObj['device_id']
            if "ip_address" in trackerObj:
                objs.ip_address = trackerObj['ip_address']
            if "site_id" in trackerObj:
                objs.site_id = trackerObj['site_id']
            if "region" in trackerObj:
                objs.region = trackerObj['region']
            if "pid" in trackerObj:
                objs.pid = trackerObj['pid']
            if "os_type" in trackerObj:
                objs.os_type = trackerObj['os_type']
            if "current_os_version" in trackerObj:
                objs.current_os_version = trackerObj['current_os_version']
            if "new_os_version" in trackerObj:
                objs.new_os_version = trackerObj['new_os_version']
            if "assignee" in trackerObj:
                objs.assignee = trackerObj['assignee']
            if "schedule" in trackerObj:
                objs.schedule = FormatStringDate(trackerObj['schedule'])
            if "status" in trackerObj:
                objs.status = trackerObj['status']
            if "crq" in trackerObj:
                objs.crq = trackerObj['crq']
            if "remarks" in trackerObj:
                objs.remarks = trackerObj['remarks']

            #INSERT TO DB

            db.session.flush()

            db.session.merge(objs)
            db.session.commit()
            print(f"Data Updated For Device ID: {id}", file=sys.stderr)
            return jsonify({'response': "success","code":"200"})
            
        else:
            print("NO MATCH", file = sys.stderr)
            return "Device Not Found", 404
    except Exception as e:
        print(f"Something else went wrong during Database Update {e.args}", file=sys.stderr)
        return str(e),500

@app.route('/iosTracker', methods=['GET'])
@token_required
def GetAllTrackers(user_data):
    if True:
        try:
            unifiedObjList = []
            unifiedObjs = EDN_IOS_TRACKER.query.all()
            for unifiedObj in unifiedObjs:
                unifiedDataDict = {}
                unifiedDataDict['id'] = unifiedObj.id
                unifiedDataDict['device_id'] = unifiedObj.device_id
                unifiedDataDict['ip_address'] = unifiedObj.ip_address
                unifiedDataDict['site_id'] = unifiedObj.site_id
                unifiedDataDict['region'] = unifiedObj.region
                unifiedDataDict['pid'] = unifiedObj.pid
                unifiedDataDict['os_type'] = unifiedObj.os_type
                unifiedDataDict['current_os_version'] = unifiedObj.current_os_version
                unifiedDataDict['new_os_version'] = unifiedObj.new_os_version
                unifiedDataDict['assignee'] = unifiedObj.assignee
                unifiedDataDict['schedule'] = FormatDate(unifiedObj.schedule)
                unifiedDataDict['status'] = unifiedObj.status
                unifiedDataDict['crq'] = unifiedObj.crq
                unifiedDataDict['remarks'] = unifiedObj.remarks
                if unifiedObj.creation_date:
                    unifiedDataDict['creation_date'] = FormatDate(unifiedObj.creation_date)
                if unifiedObj.modification_date:
                    unifiedDataDict['modification_date'] = FormatDate(unifiedObj.modification_date)
               
                
                if user_data['user_role']=='Admin':
                    unifiedDataDict['created_by'] = unifiedObj.created_by
                    unifiedDataDict['modified_by'] = unifiedObj.modified_by

                unifiedObjList.append(unifiedDataDict)
            print(unifiedObjList,file=sys.stderr)
            return jsonify(unifiedObjList),200
        except Exception as e:
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/iosTracker', methods=['DELETE'])
@token_required
def RemoveIOSTracker(user_data):
    if True:
        try:
            ids = request.get_json()
            for ip in ids['ips']:
                EDN_IOS_TRACKER.query.filter_by(id= ip).delete()

            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/getAssignees', methods=['GET'])
@token_required
def GetAssignees(user_data):
    if True:
        try:
            assigneeList = []
            assigneeObj = User_Table.query.with_entities(User_Table.name, User_Table.user_id).filter_by(team= 'EDN').all()

            for obj in assigneeObj:
                assigneeList.append(str(obj[0]) + "(" + str(obj[1]) + ")")

            return jsonify(assigneeList), 200

        except Exception as e:
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/getDeviceId', methods=['GET'])
@token_required
def GetDeviceID(user_data):
    if True:
        try:
            idList = []
            deviceObj = Device_Table.query.with_entities(Device_Table.device_id).all()

            for obj in deviceObj:
                idList.append(str(obj[0]))

            return jsonify(idList), 200

        except Exception as e:
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/getDismantleDeviceId', methods=['GET'])
@token_required
def GetDismantleDeviceId(user_data):
    if True:
        try:
            idList = []
            deviceObj = Device_Table.query.with_entities(Device_Table.device_id).filter_by(status="Dismantle").all()

            for obj in deviceObj:
                idList.append(str(obj[0]))

            return jsonify(idList), 200

        except Exception as e:
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401


# IP ASSIGNMENT TRACKER #

@app.route('/iptAssignmentTracker', methods=['POST'])
@token_required
def AddIptAssignmentTracker(user_data):
    try:
        response = False
        response1 = False
        trck = ''
        trackerObj = request.get_json()
        # if type(trackerObj[0]) == list:
        #     trackerObj = trackerObj[0]
        for obj in trackerObj:
            try:
                tracker = IP_ASSIGNMENT_TRACKER()
                if 'employee_pf' in obj:
                    tracker.employee_pf = obj['employee_pf']
                else:
                    tracker.employee_pf = ''
                if 'full_name' in obj:
                    tracker.full_name = obj['full_name']
                else:
                    tracker.full_name = ''
                if 'organization' in obj:
                    tracker.organization = obj['organization']
                else:
                    tracker.organization = ''
                if 'position' in obj:
                    tracker.position = obj['position']
                else:
                    tracker.position = ''
                if 'grade' in obj:
                    tracker.grade = obj['grade']
                else:
                    tracker.grade = ''
                if 'email' in obj:
                    tracker.email = obj['email']
                else:
                    tracker.email = ''
                if 'ip_phone_model' in obj:
                    tracker.ip_phone_model = obj['ip_phone_model']
                else:
                    tracker.ip_phone_model = ''
                if 'serial_number' in obj:
                    tracker.serial_no = obj['serial_number']
                else:
                    tracker.serial_no = ''
                if 'mac' in obj:
                    tracker.mac = obj['mac']
                else:
                    tracker.mac = ''
                if 'date_of_device_assignment' in obj:
                    tracker.date_of_device_assignment = FormatStringDate(obj['date_of_device_assignment']) 
                else:
                    tracker.date_of_device_assignment = ''
                if 'region' in obj:
                    tracker.region = obj['region']
                else:
                    tracker.region = ''
                if 'registration_status' in obj:
                    tracker.registration_status = obj['registration_status']
                else:
                    tracker.registration_status = ''
                
                if 'assigned_by' in obj:
                    tracker.assigned_by = obj['assigned_by']
                else:
                    tracker.assigned_by = ''
                
                if 'mobile_number' in obj:
                    tracker.mobile_number = obj['mobile_number']
                else:
                    tracker.mobile_number = ''
                
                if 'serial_number' in obj:

                    if obj['serial_number']:

                        if IP_ASSIGNMENT_TRACKER.query.with_entities(IP_ASSIGNMENT_TRACKER.ip_assignment_tracker_id).filter_by(serial_no=obj['serial_number']).first() is not None:
                            tracker.ip_assignment_tracker_id= IP_ASSIGNMENT_TRACKER.query.with_entities(IP_ASSIGNMENT_TRACKER.ip_assignment_tracker_id).filter_by(serial_no=obj['serial_number']).first()[0]
                            time = datetime.now()
                            tracker.modified_by= user_data['user_id']
                            tracker.modification_date= time
                            UpdateData(tracker)
                            print("Data Updated For Device No:"+ ' ' +str(tracker.ip_assignment_tracker_id), file=sys.stderr)
                            response = True
                            trck = tracker.ip_assignment_tracker_id
                        else:
                            time = datetime.now()
                            tracker.created_by= user_data['user_id']
                            tracker.modified_by= user_data['user_id']
                            tracker.creation_date=time
                            tracker.modification_date= time
                            InsertData(tracker)
                            print("Data Inserted Into DB", file=sys.stderr)
                            response1 = True
                            # trck = obj['ip_assignment_tracker_id']
                    else:
                        time = datetime.now()
                        tracker.created_by= user_data['user_id']
                        tracker.modified_by= user_data['user_id']
                        tracker.creation_date=time
                        tracker.modification_date= time
                        InsertData(tracker)
                        print("Data Inserted Into DB", file=sys.stderr)
                        response1 = True
                        # trck = obj['ip_assignment_tracker_id']

                else:
                    time = datetime.now()
                    tracker.created_by= user_data['user_id']
                    tracker.modified_by= user_data['user_id']
                    tracker.creation_date=time
                    tracker.modification_date= time
                    InsertData(tracker)
                    print("Data Inserted Into DB", file=sys.stderr)
                    response1 = True
                    # trck = obj['ip_assignment_tracker_id']

            except Exception as e:
                traceback.print_exc()
                print(f"Error Adding Data: {e}", file=sys.stderr)
        
        if response==True:
            return jsonify({'Response': f"Tracker {trck} Successfully Updated"}),200
        if response1==True:
            return jsonify({'Response': f"Tracker Successfully Inserted"}),200

    except Exception as e:
        traceback.print_exc()
        return jsonify({f"Response": f"Failed to Update/Insert {e}"}),500

@app.route('/iptAssignmentTracker', methods=['GET'])
@token_required
def GetIptAssignmentTrackers(user_data):
    if True:
        try:
            trackerList = []
            trackerObj = IP_ASSIGNMENT_TRACKER.query.all()
            for obj in trackerObj:
                trackerDict = {}
                trackerDict['ip_assignment_tracker_id'] = obj.ip_assignment_tracker_id
                trackerDict['employee_pf'] = obj.employee_pf
                trackerDict['full_name'] = obj.full_name
                trackerDict['organization'] = obj.organization
                trackerDict['position'] = obj.position
                trackerDict['grade'] = obj.grade
                trackerDict['email'] = obj.email
                trackerDict['ip_phone_model'] = obj.ip_phone_model
                trackerDict['serial_number'] = obj.serial_no
                trackerDict['mac'] = obj.mac
                trackerDict['date_of_device_assignment'] = FormatDate(obj.date_of_device_assignment)
                trackerDict['region'] = obj.region
                trackerDict['registration_status'] = obj.registration_status
                trackerDict['assigned_by'] = obj.assigned_by
                trackerDict['mobile_number'] = obj.mobile_number
                if obj.creation_date:
                    trackerDict['creation_date'] = FormatDate(obj.creation_date)
                if (obj.modification_date):
                    trackerDict['modification_date'] = FormatDate(obj.modification_date)
                if user_data['user_role']=='Admin':
                    trackerDict['created_by'] = obj.created_by
                    trackerDict['modified_by'] = obj.modified_by
                trackerList.append(trackerDict)
            # print(trackerList,file=sys.stderr)
            return jsonify(trackerList),200
        except Exception as e:
            print(e, file=sys.stderr)
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/iptAssignmentTracker', methods=['DELETE'])
@token_required
def RemoveIptAssignmentTracker(user_data):
    if True:
        try:
            ids = request.get_json()
            for ip in ids['ips']:
                IP_ASSIGNMENT_TRACKER.query.filter_by(ip_assignment_tracker_id= ip).delete()

            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

# IP CLEARANCE TRACKER #

@app.route('/ipClearanceTracker', methods=['POST'])
@token_required
def AddIpClearanceTracker(user_data):
    try:
        response = False
        response1 = False
        trck = ''
        trackerObj = request.get_json()
        # if type(trackerObj[0]) == list:
        #     trackerObj = trackerObj[0]
        for obj in trackerObj:
            try:
                tracker = IP_CLEARANCE_TRACKER()
                if 'employee_pf' in obj:
                    tracker.employee_pf = obj['employee_pf']
                else:
                    tracker.employee_pf = ''
                if 'full_name' in obj:
                    tracker.full_name = obj['full_name']
                else:
                    tracker.full_name = ''
                if 'organization' in obj:
                    tracker.organization = obj['organization']
                else:
                    tracker.organization = ''
                if 'position' in obj:
                    tracker.position = obj['position']
                else:
                    tracker.position = ''
                if 'job' in obj:
                    tracker.job = obj['job']
                else:
                    tracker.job = ''
                if 'grade' in obj:
                    tracker.grade = obj['grade']
                else:
                    tracker.grade = ''
                if 'nationality' in obj:
                    tracker.nationality = obj['nationality']
                else:
                    tracker.nationality = ''
                if 'termination_date' in obj:
                    tracker.termination_date = FormatStringDate(obj['termination_date'])
                else:
                    tracker.termination_date = ''
                if 'email' in obj:
                    tracker.email = obj['email']
                else:
                    tracker.email = ''
                if 'ipt_team_assignee' in obj:
                    tracker.ipt_team_assignee = obj['ipt_team_assignee']
                else:
                    tracker.ipt_team_assignee = ''
                if 'ip_phone_model' in obj:
                    tracker.ip_phone_model = obj['ip_phone_model']
                else:
                    tracker.ip_phone_model = ''
                if 'serial_number' in obj:
                    tracker.serial_no = obj['serial_number']
                else:
                    tracker.serial_no = ''
                if 'mac' in obj:
                    tracker.mac = obj['mac']
                else:
                    tracker.mac = ''
                if 'collection_date' in obj:
                    tracker.collection_date = FormatStringDate(obj['collection_date'])
                else:
                    tracker.collection_date = ''
                if 'region' in obj:
                    tracker.region = obj['region']
                else:
                    tracker.region = ''
                if 'status' in obj:
                    tracker.status = obj['status']
                else:
                    tracker.status = ''
                if 'remarks' in obj:
                    tracker.remarks = obj['remarks']
                else:
                    tracker.remarks = ''

                if 'serial_number' in obj:

                    if obj['serial_number']:
                        if IP_CLEARANCE_TRACKER.query.with_entities(IP_CLEARANCE_TRACKER.ip_clearance_tracker_id).filter_by(serial_no=obj['serial_number']).first() is not None:
                            tracker.ip_clearance_tracker_id= IP_CLEARANCE_TRACKER.query.with_entities(IP_CLEARANCE_TRACKER.ip_clearance_tracker_id).filter_by(serial_no=obj['serial_number']).first()[0]
                            time = datetime.now()
                            tracker.modified_by= user_data['user_id']
                            tracker.modification_date= time
                            UpdateData(tracker)
                            print("Data Updated For Device No:"+ ' ' +str(tracker.ip_clearance_tracker_id), file=sys.stderr)
                            response = True
                            trck = tracker.ip_clearance_tracker_id
                        else:
                            time = datetime.now()
                            tracker.created_by= user_data['user_id']
                            tracker.modified_by= user_data['user_id']
                            tracker.creation_date=time
                            tracker.modification_date= time
                            InsertData(tracker)
                            print("Data Inserted Into DB", file=sys.stderr)
                            response1 = True
                            # trck = obj['ip_clearance_tracker_id']
                    else:
                        time = datetime.now()
                        tracker.created_by= user_data['user_id']
                        tracker.modified_by= user_data['user_id']
                        tracker.creation_date=time
                        tracker.modification_date= time
                        InsertData(tracker)
                        print("Data Inserted Into DB", file=sys.stderr)
                        response1 = True
                        # trck = obj['ip_clearance_tracker_id']
                else:
                    time = datetime.now()
                    tracker.created_by= user_data['user_id']
                    tracker.modified_by= user_data['user_id']
                    tracker.creation_date=time
                    tracker.modification_date= time
                    InsertData(tracker)
                    print("Data Inserted Into DB", file=sys.stderr)
                    response1 = True
                    # trck = obj['ip_clearance_tracker_id']

            except Exception as e:
                traceback.print_exc()
                print(f"Error Adding Data: {e}", file=sys.stderr)
        
        if response==True:
            return jsonify({'Response': f"Tracker {trck} Successfully Updated"}),200
        if response1==True:
            return jsonify({'Response': f"Tracker Successfully Inserted"}),200

    except Exception as e:
        traceback.print_exc()
        return jsonify({f"Response": f"Failed to Update/Insert {e}"}),500

@app.route('/ipClearanceTracker', methods=['GET'])
@token_required
def GetIpClearanceTrackers(user_data):
    if True:
        try:
            trackerList = []
            trackerObj = IP_CLEARANCE_TRACKER.query.all()
            for obj in trackerObj:
                trackerDict = {}
                trackerDict['ip_clearance_tracker_id'] = obj.ip_clearance_tracker_id
                trackerDict['employee_pf'] = obj.employee_pf
                trackerDict['full_name'] = obj.full_name
                trackerDict['organization'] = obj.organization
                trackerDict['position'] = obj.position
                trackerDict['job'] = obj.job
                trackerDict['grade'] = obj.grade
                trackerDict['nationality'] = obj.nationality
                trackerDict['termination_date'] = FormatDate(obj.termination_date)
                trackerDict['email'] = obj.email
                trackerDict['ipt_team_assignee'] = obj.ipt_team_assignee
                trackerDict['ip_phone_model'] = obj.ip_phone_model
                trackerDict['serial_number'] = obj.serial_no
                trackerDict['mac'] = obj.mac
                trackerDict['collection_date'] = FormatDate(obj.collection_date)
                trackerDict['region'] = obj.region
                trackerDict['status'] = obj.status
                trackerDict['remarks'] = obj.remarks
                if obj.creation_date:
                    trackerDict['creation_date'] = FormatDate(obj.creation_date)
                if (obj.modification_date):
                    trackerDict['modification_date'] = FormatDate(obj.modification_date)
                if user_data['user_role']=='Admin':
                    trackerDict['created_by'] = obj.created_by
                    trackerDict['modified_by'] = obj.modified_by
                
                trackerList.append(trackerDict)
            # print(trackerList,file=sys.stderr)
            return jsonify(trackerList),200
        except Exception as e:
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/ipClearanceTracker', methods=['DELETE'])
@token_required
def RemoveIpClearanceTracker(user_data):
    if True:
        try:
            ids = request.get_json()
            for ip in ids['ips']:
                IP_CLEARANCE_TRACKER.query.filter_by(ip_clearance_tracker_id= ip).delete()

            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/getAssigneesTracker', methods=['GET'])
@token_required
def GetAssigneesTracker(user_data):
    if True:
        try:
            assigneeList = []
            assigneeObj = User_Table.query.with_entities(User_Table.name, User_Table.user_id).filter_by(team= 'IPT').all()

            for obj in assigneeObj:
                assigneeList.append(str(obj[0]) + "(" + str(obj[1]) + ")")

            return jsonify(assigneeList), 200

        except Exception as e:
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/getIptProductIds', methods=['GET'])
@token_required
def GetProductId(user_data):
    if True:
        try:
            trackerList = []
            trackerObj = IPT_Endpoints_Table.query.with_entities(IPT_Endpoints_Table.product_id).distinct()

            for obj in trackerObj:
                if str(obj[0]):
                    trackerList.append(str(obj[0]))

            return jsonify(trackerList), 200

        except Exception as e:
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

# EDN Device Power OFF Tracker #

@app.route('/ednPowerOffTracker', methods=['POST'])
@token_required
def AddPowerOffTracker(user_data):
    if True:
        try:
            trackerObj = request.get_json()
            trackerList = []
            ipFlag = False
            ipFlag2 = False
            response = False
            response1 = False
            trck = ''
            for obj in trackerObj:
                try:
                    ipFlag = False
                    objDict = {}
                    demoDict = {}
                    
                    if 'crq_no' in obj:
                        objDict['crq_no'] = obj['crq_no']
                    else:
                        raise Exception("Key 'crq_no' is Missing")
                    if 'comments' in obj:
                        objDict['comments'] = obj['comments']
                    else:
                        objDict['comments'] = ''
                    if 'assigned_to' in obj:
                        objDict['assigned_to'] = obj['assigned_to']
                    else:
                        objDict['assigned_to'] = ''
                    if 'associated_circuit_id_details' in obj:
                        objDict['associated_circuit_id_details'] = obj['associated_circuit_id_details']
                    else:
                        objDict['associated_circuit_id_details'] = ''
                    if 'date_of_power_down' in obj:
                        objDict['date_of_power_down'] = FormatStringDate(obj['date_of_power_down'])
                    else:
                        raise Exception("Key 'date_of_power_down' is Missing")
                    if 'date_of_power_on' in obj:
                        objDict['date_of_power_on'] = FormatStringDate(obj['date_of_power_on'])
                    else:
                        objDict['date_of_power_on'] = None
                    if 'device_id' in obj:
                        objDict['device_id'] = obj['device_id']
                    else:
                        raise Exception("Key 'device_id' is Missing")


                    queryString = f"select ne_ip_address, serial_number, `function`, pn_code, tag_id, site_id, rack_id from device_table where DEVICE_ID='{obj['device_id']}';"
                    result = inv_engine.execute(queryString)

                    for row in result:
                        objDict['ip_address'] = row[0]
                        objDict['serial_no'] = row[1]
                        objDict['function'] = row[2]
                        objDict['pn_code'] = row[3]
                        objDict['tag_id'] = row[4]
                        demoDict['site_id'] = row[5]
                        demoDict['rack_id'] = row[6]


                    if objDict.get('device_id'):

                        queryString2 = f"select region, city, site_name from phy_table where SITE_ID='{demoDict['site_id']}';"
                        result2 = inv_engine.execute(queryString2)

                        for row in result2:
                            objDict['region'] = row[0]
                            objDict['city'] = row[1]
                            objDict['site_name'] = row[2]
                        
                        queryString1 = f"select rack_name from rack_table where RACK_ID='{demoDict['rack_id']}';"
                        result1 = inv_engine.execute(queryString1)

                        for row in result1:
                            objDict['rack_name'] = row[0]

                        queryString3 = f"select sw_type from seed_table where DEVICE_ID='{objDict['device_id']}';"
                        result3 = inv_engine.execute(queryString3)

                        for row in result3:
                            objDict['os_type'] = row[0]
                        
                    else:
                        print("Device with this ID Not Found", file=sys.stderr)
                        ipFlag = True
                        ipFlag2 = True
                    

                    if not ipFlag:
                        trackerList.append(objDict)

                except Exception as e:
                    traceback.print_exc()
                    print(f"Error Adding Data: {e}", file=sys.stderr)
                    return jsonify({f"response": f"Failed to Update/Insert: {e}"}),500
                
                    

                finally:
                    
                    print("FLAG", ipFlag, file=sys.stderr)
                    if not ipFlag:
                        print(">>>>>>>>>>>>>>>>>>>", file=sys.stderr)

                        for objs in trackerList:
                            try:
                                tracker = EDN_DEVICE_POWEROFF_TRACKER()
                                tracker.ip_address = objs.get('ip_address', "")
                                tracker.crq_no = objs['crq_no']
                                tracker.device_id = objs['device_id']
                                tracker.serial_no = objs.get('serial_no', "")
                                tracker.function = objs.get('function', "")
                                tracker.pn_code = objs.get('pn_code', "")
                                tracker.comments = objs['comments']
                                tracker.os_type = objs.get('os_type', "")
                                tracker.region = objs.get('region', "")
                                tracker.city = objs.get('city',"")
                                tracker.site_name = objs.get('site_name', "")
                                tracker.rack_name = objs.get('rack_name', "")
                                tracker.tag_id = objs.get('tag_id', "")
                                tracker.date_of_power_down = objs['date_of_power_down']
                                tracker.date_of_power_on = objs['date_of_power_on']
                                tracker.assigned_to = objs['assigned_to']
                                tracker.associated_circuit_id_details = objs['associated_circuit_id_details']

                                print("Poweroff Tracker", tracker, file=sys.stderr)

                                if EDN_DEVICE_POWEROFF_TRACKER.query.with_entities(EDN_DEVICE_POWEROFF_TRACKER.poweroff_tracker_id).filter_by(device_id=obj['device_id']).first() is not None:
                                    tracker.poweroff_tracker_id = EDN_DEVICE_POWEROFF_TRACKER.query.with_entities(EDN_DEVICE_POWEROFF_TRACKER.poweroff_tracker_id).filter_by(device_id=obj['device_id']).first()[0]
                                    
                                    time = datetime.now()
                                    tracker.modified_by= user_data['user_id']
                                    tracker.modification_date= time

                                    UpdateData(tracker)
                                    print("Data Updated For Device ID:"+ ' ' +obj['device_id'], file=sys.stderr)
                                    response = True
                                    trck = tracker.device_id
                                    
                                else:
                                    time = datetime.now()
                                    tracker.created_by= user_data['user_id']
                                    tracker.modified_by= user_data['user_id']
                                    tracker.creation_date=time
                                    tracker.modification_date= time
                                    InsertData(tracker)
                                    print("Data Inserted Into DB", file=sys.stderr)
                                    response1 = True
                                    trck = tracker.device_id

                            except Exception as e:
                                traceback.print_exc()
                                print(f"Error Adding Data: {e}", file=sys.stderr)

            if ipFlag2:                    
                print("Some Devices Not Found", file=sys.stderr)
                return jsonify({'response': "Some Devices Not Found"}),500
            if response==True:
                return jsonify({'response': f"{trck} Successfully Updated"}),200
            if response1==True:
                return jsonify({'response': f"{trck} Successfully Inserted"}),200

        except Exception as e:
            traceback.print_exc()
            return jsonify({f"response": f"Failed to Update/Insert {e}"}),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/ednPowerOffTracker', methods=['GET'])
@token_required
def GetPoweroffTrackers(user_data):
    if True:
        try:
            trackerList = []
            trackerObj = EDN_DEVICE_POWEROFF_TRACKER.query.all()
            for obj in trackerObj:
                trackerDict = {}
                trackerDict['poweroff_tracker_id'] = obj.poweroff_tracker_id
                trackerDict['crq_no'] = obj.crq_no
                trackerDict['ip_address'] = obj.ip_address
                trackerDict['device_id'] = obj.device_id
                trackerDict['tag_id'] = obj.tag_id
                trackerDict['serial_no'] = obj.serial_no
                trackerDict['function'] = obj.function
                trackerDict['pn_code'] = obj.pn_code
                trackerDict['comments'] = obj.comments
                trackerDict['os_type'] = obj.os_type
                trackerDict['region'] = obj.region
                trackerDict['city'] = obj.city
                trackerDict['site_name'] = obj.site_name
                trackerDict['rack_name'] = obj.rack_name
                trackerDict['date_of_power_down'] = FormatDate(obj.date_of_power_down)
                trackerDict['date_of_power_on'] = FormatDate(obj.date_of_power_on)
                trackerDict['assigned_to'] = obj.assigned_to
                trackerDict['associated_circuit_id_details'] = obj.associated_circuit_id_details
                if obj.creation_date:
                    trackerDict['creation_date'] = FormatDate(obj.creation_date)
                if (obj.modification_date):
                    trackerDict['modification_date'] = FormatDate(obj.modification_date)
                if user_data['user_role']=='Admin':
                    trackerDict['created_by'] = obj.created_by
                    trackerDict['modified_by'] = obj.modified_by
                trackerList.append(trackerDict)
            # print(trackerList,file=sys.stderr)
            return jsonify(trackerList),200
        except Exception as e:
            print(f"Exception Occured {e}", file=sys.stderr)
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/ednPowerOffTracker', methods=['DELETE'])
@token_required
def RemoveEdnPoweroffTracker(user_data):
    if True:
        try:
            ids = request.get_json()
            for ip in ids['ips']:
                EDN_DEVICE_POWEROFF_TRACKER.query.filter_by(poweroff_tracker_id= ip).delete()

            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

# EDN Hand-Back Tracker #

@app.route('/ednHandbackTracker', methods=['POST'])
@token_required
def AddHandbackTracker(user_data):
    if True:
        try:
            trackerObj = request.get_json()
            trackerList = []
            ipFlag = False
            ipFlag2 = False
            response = False
            response1 = False
            trck = ''
            for obj in trackerObj:
                try:
                    ipFlag = False
                    objDict = {}
                    demoDict = {}
                    
                    if 'crq_no' in obj:
                        objDict['crq_no'] = obj['crq_no']
                    else:
                        raise Exception("Key 'crq_no' is Missing")
                    if 'handback_status' in obj:
                        objDict['handback_status'] = obj['handback_status']
                    else:
                        raise Exception("Key 'handback_status' is Missing")
                    if 'assigned_to' in obj:
                        objDict['assigned_to'] = obj['assigned_to']
                    else:
                        raise Exception("Key 'assigned_to' is Missing")
                    if 'associated_circuit_id_details' in obj:
                        objDict['associated_circuit_id_details'] = obj['associated_circuit_id_details']
                    else:
                        objDict['associated_circuit_id_details'] = ''
                    if 'ip_decomissioning_crq' in obj:
                        objDict['ip_decomissioning_crq'] = obj['ip_decomissioning_crq']
                    else:
                        objDict['ip_decomissioning_crq'] = ''
                    if 'project_representative' in obj:
                        objDict['project_representative'] = obj['project_representative']
                    else:
                        objDict['project_representative'] = ''
                    if 'po_no' in obj:
                        objDict['po_no'] = obj['po_no']
                    else:
                        objDict['po_no'] = ''
                    if 'configuration_cleanup_status' in obj:
                        objDict['configuration_cleanup_status'] = obj['configuration_cleanup_status']
                    else:
                        raise Exception("Key 'configuration_cleanup_status' is Missing")
                    if 'extra_old_devices' in obj:
                        objDict['extra_old_devices'] = obj['extra_old_devices']
                    else:
                        objDict['extra_old_devices'] = ''
                    if 'handback_submission_date' in obj:
                        objDict['handback_submission_date'] = FormatStringDate(obj['handback_submission_date'])
                    else:
                        raise Exception("Key 'handback_submission_date' is Missing")
                    if 'handback_completion_date' in obj:
                        objDict['handback_completion_date'] = FormatStringDate(obj['handback_completion_date'])
                    else:
                        objDict['handback_completion_date'] = None
                    if 'device_id' in obj:
                        objDict['device_id'] = obj['device_id']
                    else:
                        raise Exception("Key 'device_id' is Missing")


                    queryString = f"select ne_ip_address, serial_number, `function`, pn_code, tag_id, site_type, site_id from device_table where device_id='{obj['device_id']}';"
                    result = inv_engine.execute(queryString)

                    for row in result:
                        objDict['ip_address'] = row[0]
                        objDict['serial_no'] = row[1]
                        objDict['function'] = row[2]
                        objDict['pn_code'] = row[3]
                        objDict['tag_id'] = row[4]
                        objDict['site_type'] = row[5]
                        demoDict['site_id'] = row[6]

                    if objDict.get('device_id'):

                        queryString1 = f"select region from phy_table where SITE_ID='{demoDict['site_id']}';"
                        result1 = inv_engine.execute(queryString1)

                        for row in result1:
                            objDict['region'] = row[0]

                    else:
                        print("Device with this ID Not Found", file=sys.stderr)
                        ipFlag = True
                        ipFlag2 = True

                    

                    if not ipFlag:
                        trackerList.append(objDict)


                except Exception as e:
                    traceback.print_exc()
                    print(f"Error Adding Data: {e}", file=sys.stderr)
                    return jsonify({f"response": f"Failed to Update/Insert: {e}"}),500
                
                finally:

                    if not ipFlag:
                        for objs in trackerList:
                            try:
                                tracker = EDN_HANDBACK_TRACKER()
                                tracker.ip_address = objs.get('ip_address', "")
                                tracker.crq_no = objs['crq_no']
                                tracker.device_id = objs['device_id']
                                tracker.tag_id = objs.get('tag_id', "")
                                tracker.region = objs.get('region', "")
                                tracker.site_type = objs.get('site_type', "")
                                tracker.function = objs.get('function', "")
                                tracker.pn_code = objs.get('pn_code', "")
                                tracker.serial_no = objs.get('serial_no', "")
                                tracker.assigned_to = objs['assigned_to']
                                tracker.handback_status = objs['handback_status']
                                tracker.ip_decomissioning_crq = objs['ip_decomissioning_crq']
                                tracker.project_representative = objs['project_representative']
                                tracker.handback_submission_date = objs['handback_submission_date']
                                tracker.handback_completion_date = objs['handback_completion_date']
                                tracker.po_no = objs['po_no']
                                tracker.configuration_cleanup_status = objs['configuration_cleanup_status']
                                tracker.extra_old_devices = objs['extra_old_devices']
                                tracker.associated_circuit_id_details = objs['associated_circuit_id_details']

                                print("Handback Tracker", tracker, file=sys.stderr)

                                if EDN_HANDBACK_TRACKER.query.with_entities(EDN_HANDBACK_TRACKER.handback_tracker_id).filter_by(device_id=obj['device_id']).first() is not None:
                                    tracker.handback_tracker_id = EDN_HANDBACK_TRACKER.query.with_entities(EDN_HANDBACK_TRACKER.handback_tracker_id).filter_by(device_id=obj['device_id']).first()[0]
                                    time = datetime.now()
                                   
                                    time = datetime.now()
                                    tracker.modified_by= user_data['user_id']
                                    tracker.modification_date= time

                                    UpdateData(tracker)
                                    print("Data Updated For Device ID:"+ ' ' +obj['device_id'], file=sys.stderr)
                                    response = True
                                    trck = tracker.ip_address
                                    
                                else:
                                    time = datetime.now()
                                    tracker.created_by= user_data['user_id']
                                    tracker.modified_by= user_data['user_id']
                                    tracker.creation_date=time
                                    tracker.modification_date= time
                                    InsertData(tracker)
                                    print("Data Inserted Into DB", file=sys.stderr)
                                    response1 = True
                                    trck = tracker.ip_address

                            except Exception as e:
                                traceback.print_exc()
                                print(f"Error Adding Data: {e}", file=sys.stderr)
            if ipFlag2:
                print("Some Devices Not Found", file=sys.stderr)
                return jsonify({'response': "Some Devices Not Found"}),500
            if response==True:
                return jsonify({'response': f"{trck} Successfully Updated"}),200
            if response1==True:
                return jsonify({'response': f"{trck} Successfully Inserted"}),200

        except Exception as e:
            traceback.print_exc()
            return jsonify({f"response": f"Failed to Update/Insert {e}"}),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/ednHandbackTracker', methods=['GET'])
@token_required
def GetHandbackTrackers(user_data):
    if True:
        try:
            trackerList = []
            trackerObj = EDN_HANDBACK_TRACKER.query.all()
            for obj in trackerObj:
                trackerDict = {}
                trackerDict['handback_tracker_id'] = obj.handback_tracker_id
                trackerDict['crq_no'] = obj.crq_no
                trackerDict['ip_address'] = obj.ip_address
                trackerDict['device_id'] = obj.device_id
                trackerDict['tag_id'] = obj.tag_id
                trackerDict['region'] = obj.region
                trackerDict['site_type'] = obj.site_type
                trackerDict['function'] = obj.function
                trackerDict['pn_code'] = obj.pn_code
                trackerDict['serial_no'] = obj.serial_no
                trackerDict['assigned_to'] = obj.assigned_to
                trackerDict['handback_submission_date'] = FormatDate(obj.handback_submission_date)
                trackerDict['handback_completion_date'] = FormatDate(obj.handback_completion_date)
                trackerDict['handback_status'] = obj.handback_status
                trackerDict['ip_decomissioning_crq'] = obj.ip_decomissioning_crq
                trackerDict['project_representative'] = obj.project_representative
                trackerDict['po_no'] = obj.po_no
                trackerDict['configuration_cleanup_status'] = obj.configuration_cleanup_status
                trackerDict['extra_old_devices'] = obj.extra_old_devices
                trackerDict['associated_circuit_id_details'] = obj.associated_circuit_id_details
                if obj.creation_date:
                    trackerDict['creation_date'] = FormatDate(obj.creation_date)
                if (obj.modification_date):
                    trackerDict['modification_date'] = FormatDate(obj.modification_date)
                if user_data['user_role']=='Admin':
                    trackerDict['created_by'] = obj.created_by
                    trackerDict['modified_by'] = obj.modified_by
                trackerList.append(trackerDict)
            # print(trackerList,file=sys.stderr)
            return jsonify(trackerList),200
        except Exception as e:
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/ednHandbackTracker', methods=['DELETE'])
@token_required
def RemoveEdnHandbackTracker(user_data):
    if True:
        try:
            ids = request.get_json()
            for ip in ids['ips']:
                EDN_HANDBACK_TRACKER.query.filter_by(handback_tracker_id= ip).delete()

            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

# EDN Hand-Over Tracker #

@app.route('/ednHandoverTracker', methods=['POST'])
@token_required
def AddHandoverTracker(user_data):
    if True:
        try:
            trackerObj = request.get_json()
            trackerList = []
            ipFlag = False
            ipFlag2 = False
            response = False
            response1 = False
            trck = ''
            i=0
            for obj in trackerObj:
                try:
                    ipFlag = False
                    objDict = {}
                    
                    if 'ip_address' in obj:
                        objDict['ip_address'] = obj['ip_address']
                    else:
                        raise Exception("Key 'ip_address' is Missing")
                    if 'device_id' in obj:
                        objDict['device_id'] = obj['device_id']
                    else:
                        raise Exception("Key 'device_id' is Missing")
                    if 'assigned_to' in obj:
                        objDict['assigned_to'] = obj['assigned_to']
                    else:
                        raise Exception("Key 'assigned_to' is Missing")
                    if 'project_type' in obj:
                        objDict['project_type'] = obj['project_type']
                    else:
                        objDict['project_type']=''
                    if 'asset_type' in obj:
                        objDict['asset_type'] = obj['asset_type']
                    else:
                        objDict['asset_type']=''
                    if 'handover_review_status' in obj:
                        objDict['handover_review_status'] = obj['handover_review_status']
                    else:
                        objDict['handover_review_status'] =''
                    if 'remedy_incident' in obj:
                        objDict['remedy_incident'] = obj['remedy_incident']
                    else:
                        objDict['remedy_incident'] =''
                    if 'serial_number' in obj:
                        objDict['serial_no'] = obj['serial_number']
                    else:
                        objDict['serial_no'] =''
                    if 'pid' in obj:
                        objDict['pn_code'] = obj['pid']
                    else:
                        objDict['pn_code'] =''
                    if 'site_id' in obj:
                        objDict['site_id'] = obj['site_id']
                    else:
                        objDict['site_id'] =''
                    if 'site_type' in obj:
                        objDict['site_type'] = obj['site_type']
                    else:
                        objDict['site_type'] =''
                    if 'region' in obj:
                        objDict['region'] = obj['region']
                    else:
                        objDict['region'] =''
                    if 'handover_submisson_date' in obj:
                        objDict['handover_submisson_date'] = FormatStringDate(obj['handover_submisson_date'])
                    if 'handover_completion_date' in obj:
                        objDict['handover_completion_date'] = FormatStringDate(obj['handover_completion_date'])
                    if 'comment' in obj:
                        objDict['comment'] = obj['comment']
                    if 'history' in obj:
                        objDict['history'] = obj['history']
                    if 'attachments' in obj:
                        objDict['attachments'] = obj['attachments']
                    
                    data = inv_engine.execute(f"Select onboard_status from seed_table where device_id = '{obj['device_id']}'").fetchall()
                    if len(data) > 0:
                        onboardStatus = data[0][0]
                        if 'true' in onboardStatus:
                            objDict['onboard_status'] = 'onboarded'
                        elif 'false' in onboardStatus:
                            objDict['onboard_status'] = 'not onboarded' 
                    else:
                        objDict['onboard_status'] = 'not in seed'              

                    '''
                    queryString = f"select device_id, serial_number, pn_code, site_type, site_id from device_table where NE_IP_ADDRESS='{obj['ip_address']}';"
                    result = inv_engine.execute(queryString)

                    for row in result:
                        objDict['device_id'] = obj['device_id']#row[0]
                        objDict['serial_no'] = row[1]
                        objDict['pn_code'] = row[2]
                        objDict['site_type'] = row[3]
                        demoDict['site_id'] = row[4]
                    
                    if objDict.get('device_id'):
                        queryString1 = f"select region from phy_table where SITE_ID='{demoDict.get('site_id')}';"
                        result1 = inv_engine.execute(queryString1)

                        for row in result1:
                            objDict['region'] = row[0]

                        queryString2 = f"select asset_type from seed_table where ne_ip_address='{obj.get('ip_address')}';"
                        
                        result2 = inv_engine.execute(queryString2)
                        objDict['asset_type']= ""
                        for row in result2:
                            objDict['asset_type'] = row[0]
                      
                    else:
                        print("Device with this IP Not Found", file=sys.stderr)
                        ipFlag = True
                        ipFlag2 = True
                    '''                
                    # if 'ip_address' in obj:
                    #     objDict['ip_address'] = obj['ip_address']
                    # else:
                    #     raise Exception("Key 'ip_address' is Missing")
                    
                    # if 'device_id' in obj:
                    #     objDict['device_id'] = obj['device_id']
                    # else:
                    #     raise Exception("Key 'device_id' is Missing")
                    

                    if not ipFlag:
                        trackerList.append(objDict)


                except Exception as e:
                    traceback.print_exc()
                    print(f"Error Adding Data: {e}", file=sys.stderr)
                    return jsonify({f"response": f"Failed to Update/Insert: {e}"}),500
               
                
            if not ipFlag:
                for objs in trackerList:
                    i+=1
                    try:
                        tracker = EDN_HANDOVER_TRACKER()
                        tracker.ip_address = objs['ip_address']
                        tracker.device_id = objs.get('device_id', "")
                        tracker.project_type = objs.get('project_type', "")
                        tracker.region = objs.get('region', "")
                        tracker.site_type = objs.get('site_type', "")
                        tracker.asset_type = objs.get('asset_type', "")
                        tracker.pn_code = objs.get('pn_code', "")
                        tracker.serial_no = objs.get('serial_no', "")
                        tracker.assigned_to = objs['assigned_to']
                        if "handover_submisson_date" in objs:
                            tracker.handover_submission_date = objs['handover_submisson_date']
                        if "handover_completion_date" in objs:
                            tracker.handover_completion_date = objs['handover_completion_date']
                        tracker.handover_review_status = objs['handover_review_status']
                        tracker.remedy_incident = objs.get('remedy_incident', "")
                        tracker.history = objs.get('comment', "")
                        tracker.onboard_status = objs.get('onboard_status', "")
                        
                        print("Handover Tracker", tracker, file=sys.stderr)

                        if EDN_HANDOVER_TRACKER.query.with_entities(EDN_HANDOVER_TRACKER.handover_tracker_id).filter_by(ip_address=obj['ip_address']).first() is not None:
                            tracker.handover_tracker_id = EDN_HANDOVER_TRACKER.query.with_entities(EDN_HANDOVER_TRACKER.handover_tracker_id).filter_by(ip_address=obj['ip_address']).first()[0]
                            time = datetime.now()
                            tracker.modified_by= user_data['user_id']
                            tracker.modification_date= time
                            comment = inv_engine.execute(f"select history from edn_handover_tracker where ip_address = '{objs['ip_address']}'").fetchall()[0][0]
                            print("@@@@", comment, file=sys.stderr)
                            if comment:
                                commentHistory = inv_engine.execute(f"select comment_history from edn_handover_tracker where ip_address = '{objs['ip_address']}'").fetchall()[0][0]
                                if commentHistory:
                                    history = str(commentHistory) + ',' + str(comment)
                                    tracker.comment_history = history
                                else:
                                    tracker.comment_history = str(comment)

                            UpdateData(tracker)
                            ho_Tracker_id= tracker.handover_tracker_id
                            print("Data Updated For IP:"+ ' ' +obj['ip_address'], file=sys.stderr)
                            response = True
                            trck = tracker.ip_address
                            
                        else:
                            time = datetime.now()
                            tracker.created_by= user_data['user_id']
                            tracker.modified_by= user_data['user_id']
                            tracker.creation_date=time
                            tracker.modification_date= time
                            ho_Tracker_obj= InsertData(tracker)
                            ho_Tracker_id= ho_Tracker_obj.handover_tracker_id


                            trk = EDN_HANDOVER_TRACKER.query.filter(EDN_HANDOVER_TRACKER.handover_tracker_id == ho_Tracker_id).first()
                            if trk:
                                trk.primary_handover_id = ho_Tracker_id
                            UpdateData(trk)
                            print("Data Updated for IP:"+ ' ' + obj['ip_address'], file=sys.stderr)
                            response1 = True
                            trck = tracker.ip_address
                            
                        if 'attachments' in obj:
                            if obj['attachments']:
                                attach=""
                                for attachment in obj['attachments']:
                                    attach+=attachment
                                    attachmentObj = Attachments.query.filter(Attachments.attachment_path == attachment).first()
                                    if attachmentObj:
                                        category= ""
                                        tableId= ""
                                        category = request.args.get('category')
                                        if category:
                                            tableMappingId= TableMappings.query.filter(TableMappings.table_name == category).first()
                                            if tableMappingId:
                                                tableId= tableMappingId.table_id
                                            else:
                                                print("No Table ID Found", file=sys.stderr)
                                        else:
                                                print("No Table ID Found", file=sys.stderr)

                                        if tableId:
                                            attachmentObj.table_id= tableId
                                            attachmentObj.primary_id= ho_Tracker_id
                                            attachmentObj.is_temp=0
                                            time = datetime.now()
                                            attachmentObj.modification_date=time
                                        
                                            UpdateData(attachmentObj)
                                        else:
                                            print("No Attachment Mapping Table Found", file=sys.stderr)
                                    else:
                                        print("No ATtachment Obj Found", file=sys.stderr)


                                        
                                objDict['attachments'] = attach
                        else:
                            objDict['attachments']=''


                    except Exception as e:
                        traceback.print_exc()
                        print(f"Error Adding Data: {e}", file=sys.stderr)
                print(f"COunt is: {i}", file=sys.stderr)
            #if ipFlag2:
            #    print("Some IP Not Found", file=sys.stderr)
            #    return jsonify({'response': "Some IPs Not Found"}),500
            if response==True:
                return jsonify({'response': f"{trck} Successfully Updated"}),200
            if response1==True:
                return jsonify({'response': f"{trck} Successfully Inserted"}),200

        except Exception as e:
            traceback.print_exc()
            return jsonify({f"response": f"Failed to Update/Insert {e}"}),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401
    
@app.route('/addEdnHandoverTracker', methods=['POST'])
@token_required
def AddEdnHandoverTracker(user_data):
    if True:
        try:
            trackerObj = request.get_json()
            trackerList = []
            ipFlag = False
            ipFlag2 = False
            response = False
            response1 = False
            trck = ''
            for obj in trackerObj:
                try:
                    ipFlag = False
                    objDict = {}
                    demoDict = {}
                    
                    if 'ip_address' in obj:
                        objDict['ip_address'] = obj['ip_address']
                    else:
                        raise Exception("Key 'ip_address' is Missing")
                    if 'device_id' in obj:
                        objDict['device_id'] = obj['device_id']
                    else:
                        raise Exception("Key 'device_id' is Missing")
                    if 'assigned_to' in obj:
                        objDict['assigned_to'] = obj['assigned_to']
                    else:
                        raise Exception("Key 'assigned_to' is Missing")
                    if 'project_type' in obj:
                        objDict['project_type'] = obj['project_type']
                    else:
                        objDict['project_type']=''
                    if 'asset_type' in obj:
                        objDict['asset_type'] = obj['asset_type']
                    else:
                        objDict['asset_type']=''
                    if 'handover_review_status' in obj:
                        objDict['handover_review_status'] = obj['handover_review_status']
                    else:
                        objDict['handover_review_status'] =''
                    if 'remedy_incident' in obj:
                        objDict['remedy_incident'] = obj['remedy_incident']
                    else:
                        objDict['remedy_incident'] =''
                    if 'serial_number' in obj:
                        objDict['serial_no'] = obj['serial_number']
                    else:
                        objDict['serial_no'] =''
                    if 'pid' in obj:
                        objDict['pn_code'] = obj['pid']
                    else:
                        objDict['pn_code'] =''
                    if 'site_id' in obj:
                        objDict['site_id'] = obj['site_id']
                    else:
                        objDict['site_id'] =''
                    if 'site_type' in obj:
                        objDict['site_type'] = obj['site_type']
                    else:
                        objDict['site_type'] =''
                    if 'region' in obj:
                        objDict['region'] = obj['region']
                    else:
                        objDict['region'] =''
                    if 'handover_submisson_date' in obj:
                        objDict['handover_submisson_date'] = FormatStringDate(obj['handover_submisson_date'])
                    if 'handover_completion_date' in obj:
                        objDict['handover_completion_date'] = FormatStringDate(obj['handover_completion_date'])
                    if 'comment' in obj:
                        objDict['comment'] = obj['comment']
                    if 'primary_ho_id' in obj:
                        objDict['primary_handover_id'] = obj['primary_ho_id']
                    
                    data = inv_engine.execute(f"Select onboard_status from seed_table where device_id = '{obj['device_id']}'").fetchall()
                    if len(data) > 0:
                        onboardStatus = data[0][0]
                        if 'true' in onboardStatus:
                            objDict['onboard_status'] = 'onboarded'
                        elif 'false' in onboardStatus:
                            objDict['onboard_status'] = 'not onboarded' 
                    else:
                        objDict['onboard_status'] = 'not in seed'

                    if not ipFlag:
                        trackerList.append(objDict)


                except Exception as e:
                    traceback.print_exc()
                    print(f"Error Adding Data: {e}", file=sys.stderr)
                    return jsonify({f"response": f"Failed to Update/Insert: {e}"}),500
                
                finally:

                    if not ipFlag:
                        for objs in trackerList:
                            try:
                                tracker = EDN_HANDOVER_TRACKER()
                                tracker.ip_address = objs['ip_address']
                                tracker.device_id = objs.get('device_id', "")
                                tracker.project_type = objs.get('project_type', "")
                                tracker.region = objs.get('region', "")
                                tracker.site_type = objs.get('site_type', "")
                                tracker.asset_type = objs.get('asset_type', "")
                                tracker.pn_code = objs.get('pn_code', "")
                                tracker.serial_no = objs.get('serial_no', "")
                                tracker.assigned_to = objs['assigned_to']
                                tracker.handover_submission_date = objs['handover_submisson_date']
                                tracker.handover_completion_date = objs['handover_completion_date']
                                tracker.handover_review_status = objs['handover_review_status']
                                tracker.remedy_incident = objs['remedy_incident']
                                tracker.history = objs.get('comment', "")
                                tracker.onboard_status = objs.get('onboard_status', "")
                                tracker.primary_handover_id = objs['primary_handover_id']
                                
                                print("Handover Tracker", tracker, file=sys.stderr)

                                if EDN_HANDOVER_TRACKER.query.with_entities(EDN_HANDOVER_TRACKER.handover_tracker_id).filter_by(ip_address=obj['ip_address']).first() is not None:
                                    tracker.handover_tracker_id = EDN_HANDOVER_TRACKER.query.with_entities(EDN_HANDOVER_TRACKER.handover_tracker_id).filter_by(ip_address=obj['ip_address']).first()[0]
                                    time = datetime.now()
                                    tracker.modified_by= user_data['user_id']
                                    tracker.modification_date= time

                                    UpdateData(tracker)
                                    print("Data Updated For IP:"+ ' ' +obj['ip_address'], file=sys.stderr)
                                    response = True
                                    trck = tracker.ip_address
                                    
                                else:
                                    time = datetime.now()
                                    tracker.created_by= user_data['user_id']
                                    tracker.modified_by= user_data['user_id']
                                    tracker.creation_date=time
                                    tracker.modification_date= time

                                    InsertData(tracker)
                                    print("Data Inserted Into DB", file=sys.stderr)

                                    response1 = True
                                    trck = tracker.ip_address

                            except Exception as e:
                                traceback.print_exc()
                                print(f"Error Adding Data: {e}", file=sys.stderr)
            #if ipFlag2:
            #    print("Some IP Not Found", file=sys.stderr)
            #    return jsonify({'response': "Some IPs Not Found"}),500
            if response==True:
                return jsonify({'response': f"{trck} Successfully Updated"}),200
            if response1==True:
                return jsonify({'response': f"{trck} Successfully Inserted"}),200

        except Exception as e:
            traceback.print_exc()
            return jsonify({f"response": f"Failed to Update/Insert {e}"}),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/ednHandoverTracker', methods=['GET'])
@token_required
def GetHandoverTrackers(user_data):
    if True:
        try:
            trackerList = []
            trackerObj = EDN_HANDOVER_TRACKER.query.all()
            for obj in trackerObj:
                trackerDict = {}
                trackerDict['handover_tracker_id'] = obj.handover_tracker_id
                trackerDict['ip_address'] = obj.ip_address
                trackerDict['device_id'] = obj.device_id
                trackerDict['project_type'] = obj.project_type
                trackerDict['region'] = obj.region
                trackerDict['site_type'] = obj.site_type
                trackerDict['asset_type'] = obj.asset_type
                trackerDict['pid'] = obj.pn_code
                trackerDict['serial_number'] = obj.serial_no
                trackerDict['onboard_status'] = obj.onboard_status
                trackerDict['assigned_to'] = obj.assigned_to
                trackerDict['handover_submisson_date'] = FormatDate(obj.handover_submission_date)
                trackerDict['handover_completion_date'] = FormatDate(obj.handover_completion_date)
                trackerDict['handover_review_status'] = obj.handover_review_status
                trackerDict['remedy_incident'] = obj.remedy_incident
                trackerDict['comment'] = obj.history
                trackerDict['comments_history'] = obj.comment_history
                trackerDict['primary_ho_id'] = obj.primary_handover_id
                if obj.creation_date:
                    trackerDict['creation_date'] = FormatDate(obj.creation_date)
                if (obj.modification_date):
                    trackerDict['modification_date'] = FormatDate(obj.modification_date)
                if user_data['user_role']=='Admin':
                    trackerDict['created_by'] = obj.created_by
                    trackerDict['modified_by'] = obj.modified_by
                trackerList.append(trackerDict)
            # print(trackerList,file=sys.stderr)
            return jsonify(trackerList),200
        except Exception as e:
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/ednHandoverTracker', methods=['DELETE'])
@token_required
def RemoveEdnHandoverTracker(user_data):
    if True:
        try:
            data = request.get_json()
            for id in data['ids']:
                EDN_HANDOVER_TRACKER.query.filter_by(handover_tracker_id= id).delete()

            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401


# EDN PMR Tracker #

@app.route('/ednPMRTracker', methods=['POST'])
@token_required
def AddPMRTracker(user_data):
    if True:
        try:
            trackerObj = request.get_json()
            trackerList = []
            ipFlag = False
            ipFlag2 = False
            response = False
            response1 = False
            trck = ''
            for obj in trackerObj:
                try:
                    ipFlag = False
                    objDict = {}
                    demoDict = {}
                    
                    #if 'ip_address' in obj:
                    #    objDict['ip_address'] = obj['ip_address']
                    #else:
                    #    raise Exception("Key 'ip_address' is Missing")
                    if 'edn_pmr_tracker_id' in obj:
                        objDict['edn_pmr_tracker_id'] = obj['edn_pmr_tracker_id']


                    if 'device_id' in obj:
                        objDict['device_id'] = obj['device_id']
                    else:
                        raise Exception("Key 'device_id' is Missing")

                    if 'device_remarks' in obj:
                        objDict['device_remarks'] = obj['device_remarks']
                    else:
                        objDict['device_remarks']= ''
                        #raise Exception("Key 'assigned_to' is Missing")                    

                    if 'pmr_quarter' in obj:
                        objDict['pmr_quarter'] = obj['pmr_quarter']
                    else:
                        objDict['pmr_quarter']=''

                    if 'pmr_crq' in obj:
                        objDict['pmr_crq'] = obj['pmr_crq']
                    else:
                        objDict['pmr_crq']=''

                    if 'pmr_status' in obj:
                        objDict['pmr_status'] = obj['pmr_status']
                    else:
                        raise Exception("Key 'pmr_status' is Missing")
                        #objDict['pmr_status'] =''
                    
                    if 'pmr_remarks' in obj:
                        objDict['pmr_remarks'] = obj['pmr_remarks']
                    else:
                        #raise Exception("Key 'pmr_remarks' is Missing")
                        objDict['pmr_remarks'] =''
                                        
                    if 'door_locks_status' in obj:
                        objDict['door_locks_status'] = obj['door_locks_status']
                    else:
                        raise Exception("Key 'door_locks_status' is Missing")
                        #objDict['door_locks_status'] =''
                    
                    if 'labels_status' in obj:
                        objDict['labels_status'] = obj['labels_status']
                    else:
                        raise Exception("Key 'labels_status' is Missing")
                        #objDict['labels_status'] =''
                    
                    if 'pmr_corrective_actions' in obj:
                        objDict['pmr_corrective_actions'] = obj['pmr_corrective_actions']
                    else:
                        raise Exception("Key 'pmr_corrective_actions' is Missing")
                        #objDict['pmr_corrective_actions'] =''
                    
                    
                    if "pmr_date" in obj:
                        objDict['pmr_date'] = FormatStringDate(obj['pmr_date'])
                    else:
                        raise Exception("Key 'pmr_date' is Missing")
                    
                    
                    queryString = f"select ne_ip_address, serial_number, manufacturer , criticality, cisco_domain, `virtual`, status, site_id, rack_id, pn_code, site_type from device_table where DEVICE_ID='{obj['device_id']}';"
                    result = inv_engine.execute(queryString)

                    for row in result:
                        objDict['ip_address'] =row[0]
                        objDict['serial_number'] = row[1]
                        objDict['vendor'] = row[2]
                        objDict['criticality'] = row[3]
                        objDict['domain'] = row[4]
                        objDict['virtual'] = row[5]
                        objDict['device_status'] = row[6]
                        objDict['site_id'] = row[7]
                        objDict['rack_id'] = row[8]
                        objDict['model'] = row[9]
                        objDict['site_type'] = row[10]
                       
                    if objDict.get('ip_address'):
                        queryString1 = f"select latitude, longitude, city, region from phy_table where SITE_ID='{objDict.get('site_id')}';"
                        result1 = inv_engine.execute(queryString1)

                        for row in result1:
                            
                            objDict['latitude'] = row[0]
                            objDict['longitude'] = row[1]
                            objDict['city'] = row[2]
                            objDict['region'] = row[3]

                        queryString2 = f"select rack_name from rack_table where rack_id='{objDict.get('rack_id')}';"
                        
                        result2 = inv_engine.execute(queryString2)
                        for row in result2:
                            objDict['rack_name'] = row[0]
                      
                    else:
                        print("Device with this ID Not Found", file=sys.stderr)
                        ipFlag = True
                        ipFlag2 = True
                                    
                    #if 'ip_address' in obj:
                    #    objDict['ip_address'] = obj['ip_address']
                    #else:
                    #    raise Exception("Key 'ip_address' is Missing")
                    
                    if 'device_id' in obj:
                        objDict['device_id'] = obj['device_id']
                    else:
                        raise Exception("Key 'device_id' is Missing")

                    if not ipFlag:
                        trackerList.append(objDict)


                except Exception as e:
                    traceback.print_exc()
                    print(f"Error Adding Data: {e}", file=sys.stderr)
                    return jsonify({f"response": f"Failed to Update/Insert: {e}"}),500
                
                finally:

                    if not ipFlag:
                        for objs in trackerList:
                            try:
                                tracker = EDN_PMR_TRACKER()
                                tracker.ip_address = objs['ip_address']
                                tracker.device_id = objs.get('device_id', "")
                                tracker.serial_number = objs.get('serial_number', "")
                                tracker.vendor = objs.get('vendor', "")
                                tracker.model = objs.get('model', "")
                                tracker.criticality = objs.get('criticality', "")
                                tracker.domain = objs['domain']
                                tracker.virtual = objs['virtual']
                                tracker.device_status = objs['device_status']
                                tracker.device_remarks = objs['device_remarks']
                                tracker.site_id = objs['site_id']
                                tracker.site_type = objs['site_type']
                                tracker.region = objs.get('region', "")
                                tracker.latitude = objs.get('latitude', "")
                                tracker.longitude = objs.get('longitude', "")
                                tracker.city = objs.get('city', "")
                                tracker.region = objs.get('region', "")
                                tracker.rack_name = objs.get('rack_name', "")
                                tracker.rack_id = objs.get('rack_id', "")
                                tracker.pmr_quarter = objs.get('pmr_quarter', "")
                                tracker.pmr_crq = objs.get('pmr_crq', "")
                                tracker.pmr_date = objs.get('pmr_date', "")
                                tracker.pmr_status = objs.get('pmr_status', "")
                                tracker.pmr_remarks = objs.get('pmr_remarks', "")
                                tracker.door_locks_status = objs.get('door_locks_status', "")
                                tracker.labels_status = objs.get('labels_status', "")
                                tracker.pmr_corrective_actions = objs.get('pmr_corrective_actions', "")
                                
                                print("PMR Tracker", tracker, file=sys.stderr)

                                #if EDN_PMR_TRACKER.query.with_entities(EDN_PMR_TRACKER.pmr_tracker_id).filter_by(ip_address=obj['ip_address']).first() is not None:
                                
                                if 'edn_pmr_tracker_id' in objDict:
                                    
                                    if objDict['edn_pmr_tracker_id']:
                                        tracker.edn_pmr_tracker_id = EDN_PMR_TRACKER.query.with_entities(EDN_PMR_TRACKER.edn_pmr_tracker_id).filter_by(edn_pmr_tracker_id=objDict['edn_pmr_tracker_id']).first()[0]
                                        tracker.edn_tracker_id= objDict['edn_pmr_tracker_id']

                                        time = datetime.now()
                                        tracker.modified_by= user_data['user_id']
                                        tracker.modification_date= time

                                        UpdateData(tracker)
                                        print("Data Updated For ID:"+ ' ' +objDict['device_id'], file=sys.stderr)
                                        response = True
                                        trck = tracker.ip_address
                                    else:
                                        time = datetime.now()
                                        tracker.created_by= user_data['user_id']
                                        tracker.modified_by= user_data['user_id']
                                        tracker.creation_date=time
                                        tracker.modification_date= time

                                        InsertData(tracker)
                                        print("Data Inserted Into DB", file=sys.stderr)
                                        response1 = True
                                        trck = tracker.ip_address
                                        
                                else:
                                    time = datetime.now()
                                    tracker.created_by= user_data['user_id']
                                    tracker.modified_by= user_data['user_id']
                                    tracker.creation_date=time
                                    tracker.modification_date= time

                                    InsertData(tracker)
                                    print("Data Inserted Into DB", file=sys.stderr)
                                    response1 = True
                                    trck = tracker.ip_address

                            except Exception as e:
                                traceback.print_exc()
                                print(f"Error Adding Data: {e}", file=sys.stderr)
            if ipFlag2:
                print("Some Device Ids Not Found", file=sys.stderr)
                return jsonify({'response': "Some Device Ids Not  Found"}),500
            if response==True:
                return jsonify({'response': f"{trck} Successfully Updated"}),200
            if response1==True:
                return jsonify({'response': f"{trck} Successfully Inserted"}),200

        except Exception as e:
            traceback.print_exc()
            return jsonify({f"response": f"Failed to Update/Insert {e}"}),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/ednPMRTracker', methods=['GET'])
@token_required
def GetPMRTrackers(user_data):
    if True:
        try:
            trackerList = []
            trackerObj = EDN_PMR_TRACKER.query.all()
            for obj in trackerObj:
                trackerDict = {}
                trackerDict['edn_pmr_tracker_id'] = obj.edn_pmr_tracker_id
                trackerDict['ip_address'] = obj.ip_address
                trackerDict['device_id'] = obj.device_id
                trackerDict['serial_number'] = obj.serial_number
                trackerDict['vendor'] = obj.vendor
                trackerDict['model'] = obj.model
                trackerDict['criticality'] = obj.criticality
                trackerDict['domain'] = obj.domain
                trackerDict['virtual'] = obj.virtual
                trackerDict['device_status'] = obj.device_status
                trackerDict['device_remarks'] = obj.device_remarks
                trackerDict['site_type'] = obj.site_type
                trackerDict['site_id'] = obj.site_id
                trackerDict['latitude'] = obj.latitude

                trackerDict['longitude'] = obj.longitude
                trackerDict['city'] = obj.city
                trackerDict['region'] = obj.region
                trackerDict['rack_id'] = obj.rack_id
                trackerDict['rack_name'] = obj.rack_name
                trackerDict['pmr_quarter'] = obj.pmr_quarter
                trackerDict['pmr_crq'] = obj.pmr_crq
                trackerDict['pmr_date'] = FormatDate(obj.pmr_date)
                trackerDict['pmr_remarks'] = obj.pmr_remarks
                trackerDict['pmr_status'] = obj.pmr_status
                trackerDict['door_locks_status'] = obj.door_locks_status
                trackerDict['labels_status'] = obj.labels_status
                trackerDict['pmr_corrective_actions'] = obj.pmr_corrective_actions
                if obj.creation_date:
                    trackerDict['creation_date'] = FormatDate(obj.creation_date)
                if (obj.modification_date):
                    trackerDict['modification_date'] = FormatDate(obj.modification_date)
                if user_data['user_role']=='Admin':
                    trackerDict['created_by'] = obj.created_by
                    trackerDict['modified_by'] = obj.modified_by

                trackerList.append(trackerDict)
            # print(trackerList,file=sys.stderr)
            return jsonify(trackerList),200
        except Exception as e:
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

@app.route('/ednPMRTracker', methods=['DELETE'])
@token_required
def RemoveEdnPMRTracker(user_data):
    if True:
        try:
            ids = request.get_json()
            for ip in ids['ips']:
                EDN_PMR_TRACKER.query.filter_by(edn_pmr_tracker_id= ip).delete()

            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401


## IPT RMA Tracker 

@app.route('/iptRMATracker', methods=['POST'])
@token_required
def AddRMATracker(user_data):
    if True:
        try:
            trackerObj = request.get_json()
            trackerList = []
            response = False
            for obj in trackerObj:
                try:
                    objDict = {}

                    if 'ipt_rma_tracker_id' in obj:
                        if obj['ipt_rma_tracker_id']:
                            objDict['ipt_rma_tracker_id'] = obj['ipt_rma_tracker_id']
                        else:    
                            objDict['ipt_rma_tracker_id'] ="" 
                    else:
                        objDict['ipt_rma_tracker_id'] = ""

                    if 'rma_order_number' in obj:
                        objDict['rma_order_number'] = obj['rma_order_number']
                    else:
                        raise Exception("Key 'rma_order_number' is Missing")

                    if 'service_request_number' in obj:
                        objDict['service_request_number'] = obj['service_request_number']
                    else:
                        raise Exception("Key 'service_request_number' is Missing")

                    # if 'serial_no' in obj:
                    #     objDict['serial_no'] = obj['serial_no']
                    # else:
                    #     raise Exception("Key 'serial_no' is Missing")

                    if 'mac' in obj:
                        objDict['mac'] = obj['mac']
                    else:
                        objDict['mac'] =''
                        #raise Exception("Key 'mac' is Missing")

                    # if 'user_id' in obj:
                    #     objDict['user_id'] = obj['user_id']
                    # else:
                    #     raise Exception("Key 'user_id' is Missing")

                    if 'user_info_and_device_impacted_details' in obj:
                        objDict['user_info_and_device_impacted_details'] = obj['user_info_and_device_impacted_details']
                    else:
                        raise Exception("Key 'user_info_and_device_impacted_details' is Missing")
                        # objDict['user_info_and_device_impacted_details']= ''

                    if "rma_ordered_date" in obj:
                        objDict['rma_ordered_date'] = FormatStringDate(obj['rma_ordered_date'])
                    else:
                        raise Exception("Key 'rma_ordered_date' is Missing")

                    if 'fe_receiving_the_rma_part_from_dhl' in obj:
                        objDict['fe_receiving_the_rma_part_from_dhl'] = obj['fe_receiving_the_rma_part_from_dhl']
                    else:
                        raise Exception("Key 'fe_receiving_the_rma_part_from_dhl' is Missing")
                        #objDict['fe_receiving_the_rma_part_from_dhl']=''

                    if 'current_status' in obj:
                        objDict['current_status'] = obj['current_status']
                    else:
                        raise Exception("Key 'current_status' is Missing")

                    if "actual_rma_received_date" in obj:
                        objDict['actual_rma_received_date'] = FormatStringDate(obj['actual_rma_received_date'])
                    else:
                        raise Exception("Key 'actual_rma_received_date' is Missing")
                        #objDict['actual_rma_received_date']=''

                    # if 'part_number' in obj:
                    #             objDict['part_number'] = obj['part_number']
                    # else:
                    #     raise Exception("Key 'part_number' is Missing")

                    if 'engineer_handling_the_rma' in obj:
                        objDict['engineer_handling_the_rma'] = obj['engineer_handling_the_rma']
                    else:
                        raise Exception("Key 'engineer_handling_the_rma' is Missing")
                        #objDict['engineer_handling_the_rma']=''

                    if "pickup_date_scheduled_in_airway_bill" in obj:
                        objDict['pickup_date_scheduled_in_airway_bill'] = FormatStringDate(obj['pickup_date_scheduled_in_airway_bill'])
                    else:
                        raise Exception("Key 'pickup_date_scheduled_in_airway_bill")
                        #objDict['pickup_date_scheduled_in_airway_bill']=''

                    if 'fe_delivering_the_device_to_dhl' in obj:
                        objDict['fe_delivering_the_device_to_dhl'] = obj['fe_delivering_the_device_to_dhl']
                    else:
                        objDict['fe_delivering_the_device_to_dhl']=''

                    if 'delivery_location' in obj:
                        objDict['delivery_location'] = obj['delivery_location']
                    else:
                        raise Exception("Key 'delivery_location")
                        #objDict['delivery_location']=''

                    if 'final_status' in obj:
                        objDict['final_status'] = obj['final_status']
                    else:
                        objDict['final_status']=''
                        #raise Exception("Key 'final_status' is Missing")

                    if 'remarks' in obj:
                        objDict['remarks'] = obj['remarks']
                    else:
                        objDict['remarks']=''
                    
                    if objDict['mac']:
                        trackerObj = IPT_Endpoints_Table.query.with_entities(IPT_Endpoints_Table.user, IPT_Endpoints_Table.serial_number, IPT_Endpoints_Table.product_id).filter(IPT_Endpoints_Table.mac_address == objDict['mac']).all()
                        for partNoObj in trackerObj:
                            objDict['serial_no'] = partNoObj[0]
                            objDict['user_id'] = partNoObj[1]
                            objDict['part_number'] = partNoObj[2]
                    
                    is_mac_present=""
                    if objDict['ipt_rma_tracker_id']:
                        is_mac_present = IPT_RMA_TRACKER.query.filter(IPT_RMA_TRACKER.ipt_rma_tracker_id == objDict['ipt_rma_tracker_id']).first()
                
                    ipt_endpoints_id=0
                    if is_mac_present:
                        result = IPT_RMA_TRACKER.query.filter(IPT_RMA_TRACKER.ipt_rma_tracker_id == objDict['ipt_rma_tracker_id']).first()
                        ipt_endpoints_id = result.ipt_rma_tracker_id
                        objDict['ipt_rma_tracker_id']= ipt_endpoints_id
                        tracker = IPT_RMA_TRACKER(**objDict)
                        time = datetime.now()
                        tracker.modified_by= user_data['user_id']
                        tracker.modification_date= time
                        UpdateData(tracker)
                    else:
                        objDict.pop('ipt_rma_tracker_id')
                        tracker = IPT_RMA_TRACKER(**objDict)
                        time = datetime.now()
                        tracker.created_by= user_data['user_id']
                        tracker.modified_by= user_data['user_id']
                        tracker.creation_date=time
                        tracker.modification_date= time
                        ipt_endpoints_obj=InsertData(tracker) 
                        ipt_endpoints_id= ipt_endpoints_obj.ipt_rma_tracker_id
                        # code for handling the existing MAC

                    if 'attachments' in obj:
                        if obj['attachments']:
                            attach=""
                            for attachment in obj['attachments']:
                                attach+=attachment
                                attachmentObj = Attachments.query.filter(Attachments.attachment_path == attachment).first()
                                if attachmentObj:
                                    category= ""
                                    tableId= ""
                                    category = request.args.get('category')
                                    if category:
                                        tableMappingId= TableMappings.query.filter(TableMappings.table_name == category).first()
                                        if tableMappingId:
                                            tableId= tableMappingId.table_id
                                        else:
                                            print("No Table ID Found", file=sys.stderr)
                                    else:
                                            print("No Table ID Found", file=sys.stderr)

                                    if tableId:
                                        attachmentObj.table_id= tableId
                                        attachmentObj.primary_id= ipt_endpoints_id
                                        attachmentObj.is_temp=0
                                        time = datetime.now()
                                        attachmentObj.modification_date=time
                                    
                                        UpdateData(attachmentObj)
                                    else:
                                        print("No Attachment Mapping Table Found", file=sys.stderr)
                                else:
                                    print("No ATtachment Obj Found", file=sys.stderr)


                                    
                            objDict['attachments'] = attach
                    else:
                        objDict['attachments']=''

                    #rma_tracker = IPT_RMA_TRACKER(**objDict)
                    #trackerList.append(rma_tracker)
                    

                except Exception as e:
                    traceback.print_exc()
                    print(f"Exception Occured in Adding IPT RMA, Error is {e}", file=sys.stderr)
                    print(e)
                    response = False

            
            #db.session.add_all(trackerList)
            #db.session.commit()
            response = True

            if response==True:
                return jsonify({'Response': f"Tracker Successfully Updated"}),200
            else:
                return jsonify({f"Response": f"Failed to Update/Insert Some Records {e}"}),500

        except Exception as e:
            print(f"Exception Occured in Adding IPT RMA, Error is {e}", file=sys.stderr)
            response = False
            return jsonify({f"Response": f"Failed to Update/Insert {e}"}),500

        return jsonify(response)


@app.route('/iptRMATracker', methods=['GET'])
@token_required
def GetRMATrackers(user_data):
    if True:
        try:
            trackerList = []
            trackerObj = IPT_RMA_TRACKER.query.all()
            for obj in trackerObj:
                trackerDict = {}
                trackerDict['ipt_rma_tracker_id'] = obj.ipt_rma_tracker_id
                trackerDict['rma_order_number'] = obj.rma_order_number
                trackerDict['service_request_number'] = obj.service_request_number
                trackerDict['serial_number'] =obj.serial_no
                trackerDict['mac'] = obj.mac
                trackerDict['user_id'] = obj.user_id
                trackerDict['user_info_and_device_impacted_details'] = obj.user_info_and_device_impacted_details
                trackerDict['rma_ordered_date'] = FormatDate(obj.rma_ordered_date)
                trackerDict['fe_receiving_the_rma_part_from_dhl'] = obj.fe_receiving_the_rma_part_from_dhl
                trackerDict['current_status'] = obj.current_status
                trackerDict['actual_rma_received_date'] = FormatDate(obj.actual_rma_received_date)
                trackerDict['part_number'] = obj.part_number
                trackerDict['engineer_handling_the_rma'] = obj.engineer_handling_the_rma
                trackerDict['pickup_date_scheduled_in_airway_bill'] = FormatDate(obj.pickup_date_scheduled_in_airway_bill)
                trackerDict['fe_delivering_the_device_to_dhl'] = obj.fe_delivering_the_device_to_dhl
                trackerDict['delivery_location'] = obj.delivery_location
                trackerDict['final_status'] = obj.final_status
                trackerDict['attachments'] = obj.attachments
                trackerDict['remarks'] = obj.remarks
                if obj.creation_date:
                    trackerDict['creation_date'] = FormatDate(obj.creation_date)
                if obj.modification_date:
                    trackerDict['modification_date'] = FormatDate(obj.modification_date)
                if user_data['user_role']=='Admin':
                    trackerDict['created_by'] = obj.created_by
                    trackerDict['modified_by'] = obj.modified_by
                trackerList.append(trackerDict)

            return jsonify(trackerList),200
        except Exception as e:
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Get Data'}), 401

@app.route('/iptRMATracker', methods=['DELETE'])
@token_required
def RemoveIptRMATracker(user_data):
    
    if True:
        try:
            ids = request.get_json()
            for id in ids['ips']:
                IPT_RMA_TRACKER.query.filter_by(ipt_rma_tracker_id=id).delete()

            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Delete Data'}), 401

@app.route('/getMacs', methods=['GET'])
@token_required
def GetMacs(user_data):
    if True:
        try:
            trackerList = []
            trackerObj = IPT_Endpoints_Table.query.with_entities(IPT_Endpoints_Table.mac_address).filter(IPT_Endpoints_Table.hostname.like('%SEP%')).distinct()
            for obj in trackerObj:
                if str(obj[0]):
                    trackerList.append(str(obj[0]))

            return jsonify(trackerList), 200

        except Exception as e:
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

# CMDB Tracker (EDN) #

@app.route('/cmdbTracker', methods=['POST'])
@token_required
def AddEdnCmdbTrackers(user_data):
    try:
        trackerObj = request.get_json()
        trackerList = []
        response = False
        response1 = False
        trck = ''
        for obj in trackerObj:
            try:
                objDict = {}
                if "crq_no" in obj:
                    objDict['crq_no'] = obj['crq_no']
                else:
                    raise Exception("Key 'crq_no' is Missing")
                if "activity_summary" in obj:
                    objDict['activity_summary'] = obj['activity_summary']
                if "activity_type" in obj:
                    objDict['activity_type'] = obj['activity_type']
                if "approval_type" in obj:
                    objDict['approval_type'] = obj['approval_type']
                if "priority" in obj:
                    objDict['priority'] = obj['priority']
                if "implementing_team" in obj:
                    objDict['implementing_team'] = obj['implementing_team']
                if "implementer" in obj:
                    objDict['implementer'] = obj['implementer']
                if "region" in obj:
                    objDict['region'] = obj['region']
                if "site" in obj:
                    objDict['site'] = obj['site']
                if "date" in obj:
                    objDict['date'] = FormatStringDate(obj['date'])
                if "status" in obj:
                    objDict["status"] = obj['status']
                if "service_impact" in obj:
                    objDict["service_impact"] = obj['service_impact']
                if "domain" in obj:
                    objDict["domain"] = obj['domain']
                if "activity_category" in obj:
                    objDict["activity_category"] = obj['activity_category']
                if "ci" in obj:
                    objDict["ci"] = obj['ci']
                if "reason_of_rollback" in obj:
                    objDict["reason_of_rollback"] = obj['reason_of_rollback']

                trackerList.append(objDict)

            except Exception as e:
                traceback.print_exc()
                print(f"Error Adding Data: {e}", file=sys.stderr)
            
        # print(trackerList, file=sys.stderr)

        for objs in trackerList:
            try:
                tracker = EDN_CMDB_TRACKER()
                tracker.crq_no = objs['crq_no']
                tracker.activity_summary = objs.get('activity_summary', "")
                tracker.activity_type = objs.get('activity_type', "")
                tracker.approval_type = objs.get('approval_type', "")
                tracker.priority = objs.get('priority', "")
                tracker.implementing_team = objs.get('implementing_team', "")
                tracker.implementer = objs.get('implementer', "")
                tracker.region = objs.get('region', "")
                tracker.site = objs.get('site', "")
                tracker.date = objs.get('date', "")
                tracker.status = objs.get('status',"")
                tracker.service_impact = objs.get('service_impact', "")
                tracker.domain = objs.get('domain', "")
                tracker.activity_category = objs.get('activity_category', "")
                tracker.ci = objs.get('ci', "")
                tracker.reason_of_rollback = objs.get('reason_of_rollback', "")

                # print("CMDB Tracker", tracker, file=sys.stderr)

                if EDN_CMDB_TRACKER.query.with_entities(EDN_CMDB_TRACKER.crq_no).filter_by(crq_no=obj['crq_no']).first() is not None:
                    tracker.id = EDN_CMDB_TRACKER.query.with_entities(EDN_CMDB_TRACKER.id).filter_by(crq_no=obj['crq_no']).first()[0]
                    
                    time = datetime.now()
                    tracker.modified_by= user_data['user_id']
                    tracker.modification_date= time


                    UpdateData(tracker)
                    print("Data Updated Successfully", file=sys.stderr)
                    
                    
                    response = True
                    trck = tracker.crq_no
                    
                else:
                    time = datetime.now()
                    tracker.created_by= user_data['user_id']
                    tracker.modified_by= user_data['user_id']
                    tracker.creation_date=time
                    tracker.modification_date= time

                    InsertData(tracker)
                    print("Data Inserted Into DB", file=sys.stderr)
                    response1 = True
                    trck = tracker.crq_no

            except Exception as e:
                traceback.print_exc()
                print(f"Error Adding Data: {e}", file=sys.stderr)


        if response==True:
            return jsonify({'response': f"{trck} Successfully Updated"}),200
        if response1==True:
            return jsonify({'response': f"{trck} Successfully Inserted"}),200

    except Exception as e:
        traceback.print_exc()
        return jsonify({f"Response": f"Failed to Update/Insert {e}"}),500

@app.route('/cmdbTracker', methods=['GET'])
@token_required
def GetAllEdnCmdbTrackers(user_data):
    try:
        unifiedObjList = []
        unifiedObjs = EDN_CMDB_TRACKER.query.all()
        for unifiedObj in unifiedObjs:
            unifiedDataDict = {}
            unifiedDataDict['id'] = unifiedObj.id
            unifiedDataDict['crq_no'] = unifiedObj.crq_no
            unifiedDataDict['activity_summary'] = unifiedObj.activity_summary
            unifiedDataDict['activity_type'] = unifiedObj.activity_type
            unifiedDataDict['approval_type'] = unifiedObj.approval_type
            unifiedDataDict['priority'] = unifiedObj.priority
            unifiedDataDict['implementing_team'] = unifiedObj.implementing_team
            unifiedDataDict['implementer'] = unifiedObj.implementer
            unifiedDataDict['region'] = unifiedObj.region
            unifiedDataDict['site'] = unifiedObj.site
            unifiedDataDict['date'] = FormatDate(unifiedObj.date)
            unifiedDataDict['status'] = unifiedObj.status
            unifiedDataDict['service_impact'] = unifiedObj.service_impact
            unifiedDataDict['domain'] = unifiedObj.domain
            unifiedDataDict['activity_category'] = unifiedObj.activity_category
            unifiedDataDict['ci'] = unifiedObj.ci
            unifiedDataDict['reason_of_rollback'] = unifiedObj.reason_of_rollback
            unifiedDataDict['creation_date'] = FormatDate(unifiedObj.creation_date)
            unifiedDataDict['modification_date'] = FormatDate(unifiedObj.modification_date)
            unifiedDataDict['created_by'] = unifiedObj.created_by
            unifiedDataDict['modified_by'] = unifiedObj.modified_by

            unifiedObjList.append(unifiedDataDict)
        # print(unifiedObjList,file=sys.stderr)
        return jsonify(unifiedObjList),200
    except Exception as e:
        traceback.print_exc()
        return str(e),500

@app.route('/cmdbTracker', methods=['DELETE'])
@token_required
def RemoveEdnCmdbTracker(user_data):
    try:
        ids = request.get_json()
        for ip in ids['ips']:
            EDN_CMDB_TRACKER.query.filter_by(id= ip).delete()

        db.session.commit()

        return jsonify({'response': "success", "code": "200"})
        
    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
        return str(e),500

@app.route('/getImplementers', methods=['GET'])
@token_required
def GetImplementers(user_data):
    try:
        objList = []
        objs = User_Table.query.with_entities(User_Table.name, User_Table.user_id).all()

        for obj in objs:
            objList.append(str(obj[0]) + "(" + str(obj[1]) + ")")

        return jsonify(objList), 200

    except Exception as e:
        return str(e),500


# ATTACHMENTS ROUTES #

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'msg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/attachmentFile', methods=['POST'])
def upload():
    files = request.files.getlist("attachment")
    #files = request.files.getlist("attachment")
    filenames = ""
    try:
        for file in files:
            try:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    original_name, file_extension = os.path.splitext(filename)
                    unique_filename = original_name + "_" + str(uuid.uuid4()) + file_extension
                    filenames = unique_filename
                    file.save(os.path.join("attachments/trackers/", unique_filename))
                    attachment= Attachments()
                    attachment.attachment_name= original_name
                    attachment.attachment_path=filenames
                    attachment.file_extension= file_extension.replace(".", "").lower()
                    attachment.table_id=0
                    attachment.primary_id=0
                    time = datetime.now()
                    attachment.creation_date=time
                    attachment.modification_date= time

                    InsertData(attachment)
                    filenames = unique_filename
            except Exception as e:
                traceback.print_exc()
                print(f"Error Occured {e}", file=sys.stderr)
        return jsonify(filenames),200
    
    except Exception as e:
        print(f"Error Occured {e}", file=sys.stderr)
    return filenames, 200

@app.route('/downloadAttachment' , methods=['GET']) 
def DownloadAttachment():
    #trackerObj = request.get_json()
    #payload = request.get_json()#trackerObj.get('attachment_id')
    attachment_id = request.args.get('attachment_id')

    try:
        if attachment_id:
            attachment=   Attachments.query.filter_by(attachment_id= attachment_id).first()
            if attachment:
                file_path = "/app/attachments/trackers/"+attachment.attachment_path
                if not isfile(file_path):
                    return jsonify({"error": "File does not exist"}), 500
                response = make_response(send_file(file_path))
                response.headers["Content-Type"] = "application/octet-stream"
                response.headers["Content-Disposition"] = "attachment; filename=" + attachment.attachment_name
                return response
                
                
                #return send_file(file_path, as_attachment=True), 200
                #return response

        #return send_file(os.path.join("attachments/trackers/", filename), as_attachment=True), 200
       
        #return send_from_directory("/attachments/trackers/", filename, as_attachment=False), 200

    except Exception as e:
        traceback.print_exc()
        print(f"Error Occured in Downloading File {e}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route('/viewAttachment', methods=['GET'])
def viewAttachment():
    attachment_id = request.args.get('attachment_id')
    if attachment_id:
        attachment = Attachments.query.filter_by(attachment_id=attachment_id).first()
        if attachment:
            file_path = "/app/attachments/trackers/" + attachment.attachment_path
            if not os.path.isfile(file_path):
                return jsonify({"error": "File does not exist"}), 500
            try:
                response = send_from_directory("/app/attachments/trackers/", attachment.attachment_path, as_attachment=False)
                #response.headers["Content-Type"] = "application/octet-stream"
                #response.headers["Content-Type"] = "application/pdf"


                return response, 200
            except Exception as e:
                print(f"Error Occured in View Attachment File {e}", file=sys.stderr)
                return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Attachment ID is required"}), 400


@app.route('/deleteAttachments' , methods=['POST']) 
def deleteAttachment():
    #filename= trackerObj.get('file')
    #file_path = "attachments/trackers/" + filename
    deleted=False
    payload= trackerObj = request.get_json()#trackerObj.get('attachment_id')
    try:
        if "ids" in payload and payload['ids']:
            for attachment_id in payload['ids']:
                attachment=   Attachments.query.filter_by(attachment_id=attachment_id).first()
                if attachment:
                    file_path="attachments/trackers/"+attachment.attachment_path
        
                if not isfile(file_path):
                    return jsonify({"error": "File does not exist"}), 500
                try:
                    os.remove(file_path)
                    Attachments.query.filter_by(attachment_id= attachment_id).delete()

                    db.session.commit()
                    deleted=True
                    #return jsonify({"message": "File deleted successfully"}), 200
                except Exception as e:
                    print(f"Error Occured in Deleting File {e}", file=sys.stderr)
                    #return jsonify({"error": str(e)}), 500
        if deleted:
            return jsonify({"message": "File deleted successfully"}), 200
    except Exception as e:
        print(f"Error Occured in Deleting File {e}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "Success"}), 200

@app.route('/getAttachmentsById')
def get_attachments():
    try: 
        tracker_id = request.args.get('trackerId')
        category = request.args.get('category')
                
        if category:
            tableMappingId= TableMappings.query.filter(TableMappings.table_name == category).first()
            
            if tableMappingId:
                tableId= tableMappingId.table_id
                if tableId:
                    attachmentsObj = Attachments.query.filter_by(primary_id=tracker_id, table_id=tableId).all()
                    attachmentsList=[]
                    if attachmentsObj:
                        for atachment in attachmentsObj:
                            attachmentDict = {}
                            attachmentDict['file_name'] = atachment.attachment_name
                            attachmentDict['attachment_id'] = atachment.attachment_id
                            attachmentDict['file_extension'] = atachment.file_extension
                            attachmentsList.append(attachmentDict)

                return jsonify(attachmentsList),200
                
            else:
                print("No Table ID Found", file=sys.stderr)
        return jsonify([]),200
    except Exception as e:
        print(f"Exception Occured {e}", file=sys.stderr)
        return jsonify({"message": "Error"}), 500


# SNAGS #

@app.route("/snags", methods=['POST'])
@token_required
def AddSnags(user_data):
    try:
        snagObj = request.get_json()
        try:
            snag = SNAGS()
            if "ho_ref_id" in snagObj:
                snag.ho_ref_id = snagObj['ho_ref_id']
            if "device_name" in snagObj:
                snag.device_name = snagObj['device_name']
            if "snag_name" in snagObj:
                snag.snag_name = snagObj['snag_name']
            if "snag_status" in snagObj:
                snag.snag_status = snagObj['snag_status']
            if "snag_criticality" in snagObj:
                snag.snag_criticality = snagObj['snag_criticality']
            if "comment" in snagObj:
                snag.history = snagObj['comment']
            if "reported_date" in snagObj:
                snag.reported_date = FormatStringDate(snagObj['reported_date'])
            if "closure_date" in snagObj:
                snag.closure_date = FormatStringDate(snagObj['closure_date'])
            if "snag_closure_date" in snagObj:
                snag.snag_closure_date = FormatStringDate(snagObj['snag_closure_date'])
            
            if snagObj['snag_id']:
                if SNAGS.query.with_entities(SNAGS.snag_id).filter_by(snag_id=snagObj['snag_id']).first() is not None:
                    snag.snag_id = SNAGS.query.with_entities(SNAGS.snag_id).filter_by(snag_id=snagObj['snag_id']).first()[0]
                    time = datetime.now()
                    snag.modification_date= time
                    comment = inv_engine.execute(f"select history from snags where snag_id = '{snagObj['snag_id']}'").fetchall()[0][0]
                    print("@@@@", comment, file=sys.stderr)
                    if comment:
                        commentHistory = inv_engine.execute(f"select comment_history from snags where snag_id = '{snagObj['snag_id']}'").fetchall()[0][0]
                        if commentHistory:
                            history = str(commentHistory) + ',' + str(comment)
                            snag.comment_history = history
                        else:
                            snag.comment_history = str(comment)

                    UpdateData(snag)
                    print(f"Data Updated For SNAG: {snag.snag_id}", file=sys.stderr)
                else:
                    time = datetime.now()
                    snag.creation_date = time
                    snag.modification_date = time
                    snag.created_by= user_data['user_id']
                    snag.modified_by= user_data['user_id']
                    InsertData(snag)
                    print("Data Inserted Into DB", file=sys.stderr)
            else:
                time = datetime.now()
                snag.creation_date = time
                snag.modification_date = time
                snag.created_by= user_data['user_id']
                snag.modified_by= user_data['user_id']
                InsertData(snag)
                print("Data Inserted Into DB", file=sys.stderr)

            return jsonify({'response': "Success", "code": "200"})

        except Exception as e:
            traceback.print_exc()
            print(f"Error Adding Data: {e}", file=sys.stderr)
            return jsonify({f"response": f"Failed to Insert/Update: {e}"}), 500

    except Exception as e:
        traceback.print_exc()
        print(f"Error Adding Data: {e}", file=sys.stderr)
        return jsonify({f"response": f"Failed to Insert/Update: {e}"}), 500
    
@app.route('/snags', methods=['GET'])
@token_required
def GetAllSnags(user_data):
    try:
        snagsList = []
        snagObj = SNAGS.query.all()
        for obj in snagObj:
            snagDict = {}
            snagDict['snag_id'] = obj.snag_id
            snagDict['ho_ref_id'] = obj.ho_ref_id
            snagDict['device_name'] = obj.device_name
            snagDict['snag_name'] = obj.snag_name
            snagDict['snag_status'] = obj.snag_status
            snagDict['snag_criticality'] = obj.snag_criticality
            snagDict['comment'] = obj.history
            snagDict['comments_history'] = obj.comment_history
            snagDict['reported_date'] = FormatDate(obj.reported_date)
            snagDict['closure_date'] = FormatDate(obj.closure_date)
            snagDict['snag_closure_date'] = FormatDate(obj.snag_closure_date)
            snagDict['creation_date'] = FormatDate(obj.creation_date)
            snagDict['modification_date'] = FormatDate(obj.modification_date)
            snagDict['created_by'] = obj.created_by
            snagDict['modified_by'] = obj.modified_by

            snagsList.append(snagDict)

        return jsonify(snagsList),200
    except Exception as e:
        return str(e),500

@app.route('/snags/<int:id>', methods=['GET'])
@token_required
def GetSnags(user_data, id):
    try:
        snagsList = []
        snagObj = SNAGS.query.with_entities(SNAGS).filter_by(ho_ref_id = id).all()
        for obj in snagObj:
            snagDict = {}
            snagDict['snag_id'] = obj.snag_id
            snagDict['ho_ref_id'] = obj.ho_ref_id
            snagDict['device_name'] = obj.device_name
            snagDict['snag_name'] = obj.snag_name
            snagDict['snag_status'] = obj.snag_status
            snagDict['snag_criticality'] = obj.snag_criticality
            snagDict['comment'] = obj.history
            snagDict['comments_history'] = obj.comment_history
            snagDict['reported_date'] = FormatDate(obj.reported_date)
            snagDict['closure_date'] = FormatDate(obj.closure_date)
            snagDict['snag_closure_date'] = FormatDate(obj.snag_closure_date)
            snagDict['creation_date'] = FormatDate(obj.creation_date)
            snagDict['modification_date'] = FormatDate(obj.modification_date)
            snagDict['created_by'] = obj.created_by
            snagDict['modified_by'] = obj.modified_by

            snagsList.append(snagDict)

        return jsonify(snagsList),200
    except Exception as e:
        return str(e),500
    
@app.route('/snags', methods=['DELETE'])
@token_required
def RemoveSnags(user_data):
    if True:
        try:
            data = request.get_json()
            for id in data['ids']:
                SNAGS.query.filter_by(snag_id= id).delete()

            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401
    
@app.route("/getAllSnagsStaticColumns", methods = ['GET'])
@token_required
def GetAllSnagsStaticColumns(user_data): 
    objList=[]
    objList.append({'snag_name':'DOC-High level Design Document', 'snag_criticality':'Low'})
    objList.append({'snag_name':'DOC-LLD Document/IP address & Vlan schemes', 'snag_criticality':'Low'})
    objList.append({'snag_name':'DOC-TXM/Access Media Circuit ID', 'snag_criticality':'Medium'})
    objList.append({'snag_name':'DOC - Physical & Logical Network Diagram', 'snag_criticality':'Medium'})
    objList.append({'snag_name':'NRFU - High Availability redundancy test result - L3 Routing/L2 Bridging', 'snag_criticality':'Major'})
    objList.append({'snag_name':'NRFU-High Availability redundancy test result - Device/LinkLevel', 'snag_criticality':'Major'})
    objList.append({'snag_name':'NRFU-High Availability redundancy test result - Power Level', 'snag_criticality':'Major'})
    objList.append({'snag_name':'NRFU-Services verification & Confirmation from the site Supervisor/Users', 'snag_criticality':'Major'})
    objList.append({'snag_name':'PI- Hardware Environment - Labelling & Arrangement-Device&Cables/Cooling/Racking', 'snag_criticality':'Major'})
    objList.append({'snag_name':'PI-Redundant PSU to the device with redundant power source', 'snag_criticality':'Major'})
    objList.append({'snag_name':'PI-Network Devices are on UPS', 'snag_criticality':'Major'})
    objList.append({'snag_name':'CNTI-Device Configurations as per baseline configuration guide v3.1 IOS/v1.6 NX-OS', 'snag_criticality':'Critical'})
    objList.append({'snag_name':'CNTI-Mobily Security Vulnerability Clearance', 'snag_criticality':'Critical'})
    objList.append({'snag_name':'CNTI-Configuration Compliance Clearance (RED SEAL)', 'snag_criticality':'Critical'})
    objList.append({'snag_name':'CNTI-OSS FM/PM - Device, WAN & MGMT/Infrastructure Interfaces addition & confirmation.', 'snag_criticality':'Critical'})
    objList.append({'snag_name':'CNTI-Applicable Mobily Security Integration tools/feature delpoyments(SIEM/NAC). CRQ Reference on Port opening (ARUBA/Syslog/CSPC/BackupServer)', 'snag_criticality':'Critical'})
    objList.append({'snag_name':'CNTI-Mobily Active Contract Mapping for the hardware/Software TAC Support', 'snag_criticality':'Critical'})
    objList.append({'snag_name':'KT-Technical session with operation team', 'snag_criticality':'Major'})
    objList.append({'snag_name':'KT- Validating the set up as per the project/Approved LLD', 'snag_criticality':'Major'})
    objList.append({'snag_name':'MISC - EOX hardware handed over back to planning/projects Management', 'snag_criticality':'Medium'})
    
    return jsonify(objList), 200
