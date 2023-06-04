import json, sys, time
from platform import mac_ver
from logging import exception
from socket import timeout
from app import app,db, tz, phy_engine
from flask import request, make_response, Response
import gzip
from flask_jsonpify import jsonify
import pandas as pd
from datetime import date, datetime
from app.middleware import token_required
import traceback
from app.models.inventory_models import VULNERABILITY_EDN_ARCHER, VULNERABILITY_EDN_MASTER, Device_Table, Seed, INVENTORY_SCRIPTS_STATUS, VULNERABILITY_EDN_NO_PLAN, VULNERABILITY_EDN_NOT_FOUND, EDN_IPAM_TABLE, VULNERABILITY_IGW_ARCHER, VULNERABILITY_IGW_MASTER, VULNERABILITY_IGW_NO_PLAN, VULNERABILITY_IGW_NOT_FOUND, IGW_IPAM_TABLE, VULNERABILITY_SOC_ARCHER, VULNERABILITY_SOC_MASTER, VULNERABILITY_SOC_NO_PLAN, VULNERABILITY_SOC_NOT_FOUND, SOC_IPAM_TABLE #, VULNERABILITY_INPROGRESS, VULNERABILITY_MANAGEDBY, VULNERABILITY_OPEN, VULNERABILITY_OVERDUE, 
from sqlalchemy import or_


def FormatStringDate(date):
    #print(date, file=sys.stderr)
    try:
        if date is not None:
            if '-' in date:
                result = datetime.strptime(date,'%m-%d-%Y')
            elif '/' in date:
                result = datetime.strptime(date,'%m/%d/%Y')
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
    try:
        #print(f"Data is : {obj.creation_date}", file=sys.stderr)
        #add data to db
        #obj.creation_date= datetime.now(tz)
        #obj.modification_date= datetime.now(tz)
        db.session.add(obj)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Exception in Inserting data {e}", file=sys.stderr)
        db.session.flush()
        db.session.rollback()
        

def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%m-%d-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

def UpdateData(obj):
    #add data to db
    try:
        #obj.modification_date= datetime.now(tz)
        db.session.merge(obj)
        db.session.commit()
        #print(obj.site_name, file=sys.stderr)
    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong {e}", file=sys.stderr)
    
    return True


###
#Vulnerabilities Archer
###

@app.route("/getAllEdnVulnerabilityArcherDates",methods=['GET'])
@token_required
def GetAllEdnVulnerabilityArcherDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_edn_archer  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/addEdnVulnerabilityArcher", methods = ['POST'])
@token_required
def AddEdnVulnerabilityArcher(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()
        time= datetime.now(tz)
        print(postData,file=sys.stderr)

        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "EDN-VULN-ARCHER").first()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            vulnStatus.script = "EDN-VULN-ARCHER"
            vulnStatus.status = "Running"
            vulnStatus.creation_date= current_time
            vulnStatus.modification_date= current_time
            db.session.add(vulnStatus)
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"Error while updating script status {e}", file=sys.stderr)


        for vulnerabilityArcherObj in postData:
            try:
                vulnerabilityArcher = VULNERABILITY_EDN_ARCHER()
                if 'scan_result_id' in vulnerabilityArcherObj:
                    vulnerabilityArcher.scan_result_id = vulnerabilityArcherObj['scan_result_id']
                else:
                    print(f"Error Occured in Adding Vulnerability Archer Scan Result Id Not Found.", file=sys.stderr)
                    continue

                if 'device_ip' in vulnerabilityArcherObj:
                    vulnerabilityArcher.device_ip = vulnerabilityArcherObj['device_ip']
                else:
                    vulnerabilityArcher.device_ip = ''

                if 'device_name' in vulnerabilityArcherObj:
                    vulnerabilityArcher.device_name = vulnerabilityArcherObj['device_name']
                else:
                    vulnerabilityArcher.device_name = ''

                if 'title' in vulnerabilityArcherObj:
                    vulnerabilityArcher.title = vulnerabilityArcherObj['title']
                else:
                    vulnerabilityArcher.title = ''

                if 'due_date' in vulnerabilityArcherObj:
                    if vulnerabilityArcherObj['due_date']:
                        vulnerabilityArcher.due_date = FormatStringDate(vulnerabilityArcherObj['due_date'])
                #else:
                #    vulnerabilityArcher.due_date = ''

                if 'false_positive_date' in vulnerabilityArcherObj:
                    if vulnerabilityArcherObj['false_positive_date']:
                        vulnerabilityArcher.false_positive_date = FormatStringDate(vulnerabilityArcherObj['false_positive_date'])
                #else:
                #    vulnerabilityArcher.false_positive_date = ''

                if 'severity' in vulnerabilityArcherObj:
                    vulnerabilityArcher.severity = vulnerabilityArcherObj['severity']
                else:
                    vulnerabilityArcher.severity = ''

                if 'overall_status' in vulnerabilityArcherObj:
                    vulnerabilityArcher.overall_status = vulnerabilityArcherObj['overall_status']
                else:
                    vulnerabilityArcher.overall_status = ''

                if 'qualys_vuln_status' in vulnerabilityArcherObj:

                    vulnerabilityArcher.qualys_vuln_status =  vulnerabilityArcherObj['qualys_vuln_status']
                else:
                    vulnerabilityArcher.qualys_vuln_status = ''

                if 'last_detected' in vulnerabilityArcherObj:
                    if vulnerabilityArcherObj['last_detected']:
                        vulnerabilityArcher.last_detected = FormatStringDate(vulnerabilityArcherObj['last_detected'])
                #else:
                #    vulnerabilityArcher.last_detected = ''
                    
                if 'technical_contact' in vulnerabilityArcherObj:
                    vulnerabilityArcher.technical_contact = vulnerabilityArcherObj['technical_contact']
                else:
                    vulnerabilityArcher.technical_contact = ''

                if 'exception_requests' in vulnerabilityArcherObj:
                    vulnerabilityArcher.exception_requests = vulnerabilityArcherObj['exception_requests']
                else:
                    vulnerabilityArcher.exception_requests = ''
                
                if 'cve_id' in vulnerabilityArcherObj:
                    vulnerabilityArcher.cve_id = vulnerabilityArcherObj['cve_id']
                else:
                    vulnerabilityArcher.cve_id = ''

                vulnerabilityArcher.creation_date= time
                vulnerabilityArcher.modification_date= time
                vulnerabilityArcher.created_by= user_data['user_id']
                vulnerabilityArcher.modified_by=  user_data['user_id']
            
                
                InsertData(vulnerabilityArcher)
            except Exception as e:
                traceback.print_exc()
                print(f"Error Occured in Adding Vulnerability Archer {vulnerabilityArcherObj['scan_result_id']}", file=sys.stderr)

        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "EDN-VULN-ARCHER").first()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            vulnStatus.script = "EDN-VULN-ARCHER"
            vulnStatus.status = "Completed"
            vulnStatus.creation_date= current_time
            vulnStatus.modification_date= current_time
            db.session.add(vulnStatus)
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"Error while updating script status {e}", file=sys.stderr)
            

        try:
            print(f"Running Automatic Sync of EDN Vulnerability to Master", file=sys.stderr)
            syncEdnVulnerabilityMasterFunc(user_data)

        except Exception as e:
            print(f"Exception Occured in Automatic Sync of EDN Vulnerability to Master {e}", file=sys.stderr)

        try:
            print(f"Running Automatic Sync of EDN Vulnerability to Devices", file=sys.stderr)
            syncEdnVulnerabilityMasterToDevicesFunc(user_data)

        except Exception as e:
           print(f"Exception Occured in Automatic Sync of EDN Vulnerability to Devices {e}", file=sys.stderr)


        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editEdnVulnerabilityArcher", methods = ['POST'])
@token_required
def EditEdnVulnerabilityArcher(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityArcherObj = request.get_json()
        time= datetime.now(tz)
        print(vulnerabilityArcherObj,file=sys.stderr)

        #for vulnerabilityArcherObj in postData:
        try:
            vulnerabilityArcher = VULNERABILITY_EDN_ARCHER()
            if 'scan_result_id' in vulnerabilityArcherObj and 'vulnerability_archer_id' in vulnerabilityArcherObj:
                vulnerabilityArcherId = VULNERABILITY_EDN_ARCHER.query.with_entities(VULNERABILITY_EDN_ARCHER.vulnerability_archer_id).filter_by(vulnerability_archer_id=vulnerabilityArcherObj['vulnerability_archer_id']).first()
                if vulnerabilityArcherId is not None:
                    vulnerabilityArcher.vulnerability_archer_id= vulnerabilityArcherId[0]
                    if 'device_ip' in vulnerabilityArcherObj:
                        vulnerabilityArcher.device_ip = vulnerabilityArcherObj['device_ip']
                    else:
                        vulnerabilityArcher.device_ip = ''

                    if 'device_name' in vulnerabilityArcherObj:
                        vulnerabilityArcher.device_name = vulnerabilityArcherObj['device_name']
                    else:
                        vulnerabilityArcher.device_name = ''

                    if 'title' in vulnerabilityArcherObj:
                        vulnerabilityArcher.title = vulnerabilityArcherObj['title']
                    else:
                        vulnerabilityArcher.title = ''

                        
                    if 'due_date' in vulnerabilityArcherObj:
                        if vulnerabilityArcherObj['due_date']:
                            vulnerabilityArcher.due_date = FormatStringDate(vulnerabilityArcherObj['due_date'])
                    #else:
                    #    vulnerabilityArcher.due_date = ''

                    if 'false_positive_date' in vulnerabilityArcherObj:
                        if vulnerabilityArcherObj['false_positive_date']:
                            vulnerabilityArcher.false_positive_date = FormatStringDate(vulnerabilityArcherObj['false_positive_date'])
                    #else:
                    #    vulnerabilityArcher.false_positive_date = ''

                    if 'severity' in vulnerabilityArcherObj:
                        vulnerabilityArcher.severity = vulnerabilityArcherObj['severity']
                    else:
                        vulnerabilityArcher.severity = ''

                    if 'overall_status' in vulnerabilityArcherObj:
                        vulnerabilityArcher.overall_status = vulnerabilityArcherObj['overall_status']
                    else:
                        vulnerabilityArcher.overall_status = ''

                    if 'qualys_vuln_status' in vulnerabilityArcherObj:

                        vulnerabilityArcher.qualys_vuln_status =  vulnerabilityArcherObj['qualys_vuln_status']
                    else:
                        vulnerabilityArcher.qualys_vuln_status = ''

                    if 'last_detected' in vulnerabilityArcherObj:
                        if vulnerabilityArcherObj['last_detected']:
                            vulnerabilityArcher.last_detected = FormatStringDate(vulnerabilityArcherObj['last_detected'])
                    #else:
                    #    vulnerabilityArcher.last_detected = ''
                            
                    if 'technical_contact' in vulnerabilityArcherObj:
                        vulnerabilityArcher.technical_contact = vulnerabilityArcherObj['technical_contact']
                    else:
                        vulnerabilityArcher.technical_contact = ''

                    if 'exception_requests' in vulnerabilityArcherObj:
                        vulnerabilityArcher.exception_requests = vulnerabilityArcherObj['exception_requests']
                    else:
                        vulnerabilityArcher.exception_requests = ''
                    
                    if 'cve_id' in vulnerabilityArcherObj:
                        vulnerabilityArcher.cve_id = vulnerabilityArcherObj['cve_id']
                    else:
                        vulnerabilityArcher.cve_id = ''

                    #vulnerabilityArcher.creation_date= time
                    vulnerabilityArcher.modification_date= time
                    vulnerabilityArcher.modified_by=  user_data['user_id']
                    
                    UpdateData(vulnerabilityArcher)
                else:
                    return jsonify({'response': "Vulnerability Id can not be found in Table"}), 500  
            return jsonify({'response': "Vulnerability Id Missing"}), 500  
        except Exception as e:
            traceback.print_exc()
            print(f"Error Occured in Adding Vulnerability Archer {vulnerabilityArcherObj['scan_result_id']}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnVulnerabilityArcherByDate", methods = ['POST'])
@token_required
def GetAllEdnVulnerabilityArcherByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityArcherObjList=[]
        #vulnerabilityArcherObjs = VULNERABILITY_EDN_ARCHER.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityArcherObjs =  db.session.execute(f"SELECT * FROM vulnerability_edn_archer WHERE creation_date = '{current_time}'")

        for vulnerabilityArcherObj in vulnerabilityArcherObjs:

            vulnerabilityArcherDataDict= {}
            vulnerabilityArcherDataDict['vulnerability_archer_id']=vulnerabilityArcherObj[0]
            vulnerabilityArcherDataDict['scan_result_id'] = vulnerabilityArcherObj[1]
            vulnerabilityArcherDataDict['device_ip'] = vulnerabilityArcherObj[2]
            vulnerabilityArcherDataDict['device_name'] = vulnerabilityArcherObj[3]
            vulnerabilityArcherDataDict['title'] = vulnerabilityArcherObj[4]
            if vulnerabilityArcherObj[5]:
                vulnerabilityArcherDataDict['due_date'] = FormatDate(vulnerabilityArcherObj[5])
            if vulnerabilityArcherObj[6]:
                vulnerabilityArcherDataDict['false_positive_date'] =FormatDate( vulnerabilityArcherObj[6])
            vulnerabilityArcherDataDict['severity'] = vulnerabilityArcherObj[7]
            vulnerabilityArcherDataDict['overall_status'] = vulnerabilityArcherObj[8]
            vulnerabilityArcherDataDict['qualys_vuln_status'] = vulnerabilityArcherObj[9]
            if vulnerabilityArcherObj[10]:
                vulnerabilityArcherDataDict['last_detected'] = FormatDate(vulnerabilityArcherObj[10])
            vulnerabilityArcherDataDict['technical_contact'] = vulnerabilityArcherObj[11]
            vulnerabilityArcherDataDict['exception_requests'] = vulnerabilityArcherObj[12]
            vulnerabilityArcherDataDict['cve_id'] = vulnerabilityArcherObj[13]
            vulnerabilityArcherDataDict['creation_date'] = FormatDate(vulnerabilityArcherObj[14])
            vulnerabilityArcherDataDict['modification_date'] = FormatDate(vulnerabilityArcherObj[15])
            vulnerabilityArcherDataDict['created_by'] = vulnerabilityArcherObj[16]
            vulnerabilityArcherDataDict['modified_by'] = vulnerabilityArcherObj[17]
            vulnerabilityArcherObjList.append(vulnerabilityArcherDataDict)

       
        content = gzip.compress(json.dumps(vulnerabilityArcherObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnVulnerabilityArcher", methods = ['GET'])
@token_required
def GetAllEdnVulnerabilityArcher(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityArcherObjList=[]
        
        vulnerabilityArcherObjs =  db.session.execute(f'SELECT * FROM vulnerability_edn_archer WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_edn_archer)')

        for vulnerabilityArcherObj in vulnerabilityArcherObjs:

            vulnerabilityArcherDataDict= {}
            vulnerabilityArcherDataDict['vulnerability_archer_id']=vulnerabilityArcherObj[0]
            vulnerabilityArcherDataDict['scan_result_id'] = vulnerabilityArcherObj[1]
            vulnerabilityArcherDataDict['device_ip'] = vulnerabilityArcherObj[2]
            vulnerabilityArcherDataDict['device_name'] = vulnerabilityArcherObj[3]
            vulnerabilityArcherDataDict['title'] = vulnerabilityArcherObj[4]
            if vulnerabilityArcherObj[5]:
                vulnerabilityArcherDataDict['due_date'] = FormatDate(vulnerabilityArcherObj[5])
            if vulnerabilityArcherObj[6]:
                vulnerabilityArcherDataDict['false_positive_date'] =FormatDate( vulnerabilityArcherObj[6])
            vulnerabilityArcherDataDict['severity'] = vulnerabilityArcherObj[7]
            vulnerabilityArcherDataDict['overall_status'] = vulnerabilityArcherObj[8]
            vulnerabilityArcherDataDict['qualys_vuln_status'] = vulnerabilityArcherObj[9]
            if vulnerabilityArcherObj[10]:
                vulnerabilityArcherDataDict['last_detected'] = FormatDate(vulnerabilityArcherObj[10])
            vulnerabilityArcherDataDict['technical_contact'] = vulnerabilityArcherObj[11]
            vulnerabilityArcherDataDict['exception_requests'] = vulnerabilityArcherObj[12]
            vulnerabilityArcherDataDict['cve_id'] = vulnerabilityArcherObj[13]
            vulnerabilityArcherDataDict['creation_date'] = FormatDate(vulnerabilityArcherObj[14])
            vulnerabilityArcherDataDict['modification_date'] = FormatDate(vulnerabilityArcherObj[15])
            vulnerabilityArcherDataDict['created_by'] = vulnerabilityArcherObj[16]
            vulnerabilityArcherDataDict['modified_by'] = vulnerabilityArcherObj[17]
            vulnerabilityArcherObjList.append(vulnerabilityArcherDataDict)

        content = gzip.compress(json.dumps(vulnerabilityArcherObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteEdnVulnerabilityArcher",methods = ['POST'])
@token_required
def DeleteEdnVulnerabilityArcher(user_data):
    if True:#session.get('token', None):
        vulnerabilityArcherObj = request.get_json()
        #vulnerabilityArcherObj= vulnerabilityArcherObj.get("ips")
        #vulnerabilityArcherObj = [9,10,11,12,13]
        print(vulnerabilityArcherObj,file = sys.stderr)
        
        for obj in vulnerabilityArcherObj.get("ips"):
            vulnerabilityArcherId = VULNERABILITY_EDN_ARCHER.query.filter(VULNERABILITY_EDN_ARCHER.vulnerability_archer_id==obj).first()
            print(vulnerabilityArcherId,file=sys.stderr)
            if obj:
                db.session.delete(vulnerabilityArcherId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
       



###
#Vulnerability Managed By
###
'''
@app.route("/addEdnVulnerabilityManagedBy", methods = ['POST'])
@token_required
def AddEdnVulnerabilityManagedby(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()
        time= datetime.now(tz)
        print(postData,file=sys.stderr)

        for vulnerabilityManagedbyObj in postData:
            try:
                vulnerabilityManagedby = VULNERABILITY_MANAGEDBY()
                if 'scan_result_id' in vulnerabilityManagedbyObj:
                    vulnerabilityManagedby.scan_result_id = vulnerabilityManagedbyObj['scan_result_id']
                else:
                    print(f"Error Occured in Adding Vulnerability Managedby Scan Result Id Not Found.", file=sys.stderr)
                    continue

                if 'device_ip' in vulnerabilityManagedbyObj:
                    vulnerabilityManagedby.device_ip = vulnerabilityManagedbyObj['device_ip']
                else:
                    vulnerabilityManagedby.device_ip = ''

                if 'device_name' in vulnerabilityManagedbyObj:
                    vulnerabilityManagedby.device_name = vulnerabilityManagedbyObj['device_name']
                else:
                    vulnerabilityManagedby.device_name = ''

                if 'title' in vulnerabilityManagedbyObj:
                    vulnerabilityManagedby.title = vulnerabilityManagedbyObj['title']
                else:
                    vulnerabilityManagedby.title = ''

                if 'due_date' in vulnerabilityManagedbyObj:
                    if vulnerabilityManagedbyObj['due_date']:
                        vulnerabilityManagedby.due_date = FormatStringDate(vulnerabilityManagedbyObj['due_date'])
                #else:
                #    vulnerabilityManagedby.due_date = ''

                if 'false_positive_status' in vulnerabilityManagedbyObj:
                    vulnerabilityManagedby.false_positive_status = vulnerabilityManagedbyObj['false_positive_status']
                else:
                    vulnerabilityManagedby.false_positive_status = ''

                if 'severity' in vulnerabilityManagedbyObj:
                    vulnerabilityManagedby.severity = vulnerabilityManagedbyObj['severity']
                else:
                    vulnerabilityManagedby.severity = ''    
                if 'technical_contact' in vulnerabilityManagedbyObj:
                    vulnerabilityManagedby.technical_contact = vulnerabilityManagedbyObj['technical_contact']
                else:
                    vulnerabilityManagedby.technical_contact = ''

    
                if 'description' in vulnerabilityManagedbyObj:
                    vulnerabilityManagedby.description = vulnerabilityManagedbyObj['description']
                else:
                    vulnerabilityManagedby.description = ''

                if 'cve_id' in vulnerabilityManagedbyObj:

                    vulnerabilityManagedby.cve_id =  vulnerabilityManagedbyObj['cve_id']
                else:
                    vulnerabilityManagedby.cve_id = ''

                if 'device_vendor' in vulnerabilityManagedbyObj:
                    vulnerabilityManagedby.device_vendor = vulnerabilityManagedbyObj['device_vendor']
                else:
                    vulnerabilityManagedby.device_vendor = ''

                if 'exception_expiry_date' in vulnerabilityManagedbyObj:
                    if vulnerabilityManagedbyObj['exception_expiry_date']:
                        vulnerabilityManagedby.exception_expiry_date = FormatStringDate(vulnerabilityManagedbyObj['exception_expiry_date'])
                #else:
                #    vulnerabilityManagedby.exception_requests = ''


                if 'grc_team_comments' in vulnerabilityManagedbyObj:
                    vulnerabilityManagedby.grc_team_comments = vulnerabilityManagedbyObj['grc_team_comments']
                else:
                    vulnerabilityManagedby.grc_team_comments = ''

                if 'grc_team_validation_response' in vulnerabilityManagedbyObj:

                    vulnerabilityManagedby.grc_team_validation_response =  vulnerabilityManagedbyObj['grc_team_validation_response']
                else:
                    vulnerabilityManagedby.grc_team_validation_response = ''

                if 'remediation_comments' in vulnerabilityManagedbyObj:
                    vulnerabilityManagedby.remediation_comments = vulnerabilityManagedbyObj['remediation_comments']
                else:
                    vulnerabilityManagedby.remediation_comments = ''

                if 'vulnerability_id' in vulnerabilityManagedbyObj:
                    vulnerabilityManagedby.vulnerability_id = vulnerabilityManagedbyObj['vulnerability_id']
                else:
                    vulnerabilityManagedby.vulnerability_id = ''

                if 'vendor_reference' in vulnerabilityManagedbyObj:
                    vulnerabilityManagedby.vendor_reference = vulnerabilityManagedbyObj['vendor_reference']
                else:
                    vulnerabilityManagedby.vendor_reference = ''
                
                if 'vulnerability_details' in vulnerabilityManagedbyObj:
                    vulnerabilityManagedby.vulnerability_details = vulnerabilityManagedbyObj['vulnerability_details']
                else:
                    vulnerabilityManagedby.vulnerability_details = ''


                vulnerabilityManagedby.creation_date= time
                vulnerabilityManagedby.modification_date= time
                vulnerabilityManagedby.created_by= user_data['user_id']
                vulnerabilityManagedby.modified_by= user_data['user_id']
            
                
                InsertData(vulnerabilityManagedby)
            except Exception as e:
                traceback.print_exc()
                print(f"Error Occured in Adding Vulnerability Managedby {vulnerabilityManagedbyObj['scan_result_id']}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editEdnVulnerabilityManagedBy", methods = ['POST'])
@token_required
def EditEdnVulnerabilityManagedby(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityManagedbyObj = request.get_json()
        time= datetime.now(tz)
        #print(postData,file=sys.stderr)

        #for vulnerabilityManagedbyObj in postData:
        try:
            vulnerabilityManagedby = VULNERABILITY_MANAGEDBY()
            if 'scan_result_id' in vulnerabilityManagedbyObj and 'vulnerability_managedby_id' in vulnerabilityManagedbyObj:
                vulnerabilityManagedbyId = VULNERABILITY_MANAGEDBY.query.with_entities(VULNERABILITY_MANAGEDBY.vulnerability_managedby_id).filter_by(vulnerability_managedby_id=vulnerabilityManagedbyObj['vulnerability_managedby_id']).first()
                if vulnerabilityManagedbyId is not None:
                    vulnerabilityManagedby.vulnerability_managedby_id = vulnerabilityManagedbyId[0]
                    if 'device_ip' in vulnerabilityManagedbyObj:
                        vulnerabilityManagedby.device_ip = vulnerabilityManagedbyObj['device_ip']
                    else:
                        vulnerabilityManagedby.device_ip = ''

                    if 'device_name' in vulnerabilityManagedbyObj:
                        vulnerabilityManagedby.device_name = vulnerabilityManagedbyObj['device_name']
                    else:
                        vulnerabilityManagedby.device_name = ''

                    if 'title' in vulnerabilityManagedbyObj:
                        vulnerabilityManagedby.title = vulnerabilityManagedbyObj['title']
                    else:
                        vulnerabilityManagedby.title = ''

                    if 'due_date' in vulnerabilityManagedbyObj:
                        if vulnerabilityManagedbyObj['due_date']:
                            vulnerabilityManagedby.due_date = FormatStringDate(vulnerabilityManagedbyObj['due_date'])
                    #else:
                    #    vulnerabilityManagedby.due_date = ''

                    if 'false_positive_status' in vulnerabilityManagedbyObj:
                        vulnerabilityManagedby.false_positive_status = vulnerabilityManagedbyObj['false_positive_status']
                    else:
                        vulnerabilityManagedby.false_positive_status = ''

                    if 'severity' in vulnerabilityManagedbyObj:
                        vulnerabilityManagedby.severity = vulnerabilityManagedbyObj['severity']
                    else:
                        vulnerabilityManagedby.severity = ''    
                    if 'technical_contact' in vulnerabilityManagedbyObj:
                        vulnerabilityManagedby.technical_contact = vulnerabilityManagedbyObj['technical_contact']
                    else:
                        vulnerabilityManagedby.technical_contact = ''

        
                    if 'description' in vulnerabilityManagedbyObj:
                        vulnerabilityManagedby.description = vulnerabilityManagedbyObj['description']
                    else:
                        vulnerabilityManagedby.description = ''

                    if 'cve_id' in vulnerabilityManagedbyObj:

                        vulnerabilityManagedby.cve_id =  vulnerabilityManagedbyObj['cve_id']
                    else:
                        vulnerabilityManagedby.cve_id = ''

                    if 'device_vendor' in vulnerabilityManagedbyObj:
                        vulnerabilityManagedby.device_vendor = vulnerabilityManagedbyObj['device_vendor']
                    else:
                        vulnerabilityManagedby.device_vendor = ''

                    if 'exception_expiry_date' in vulnerabilityManagedbyObj:
                        if vulnerabilityManagedbyObj['exception_expiry_date']:
                            vulnerabilityManagedby.exception_expiry_date = FormatStringDate(vulnerabilityManagedbyObj['exception_expiry_date'])
                    #else:
                    #    vulnerabilityManagedby.exception_requests = ''


                    if 'grc_team_comments' in vulnerabilityManagedbyObj:
                        vulnerabilityManagedby.grc_team_comments = vulnerabilityManagedbyObj['grc_team_comments']
                    else:
                        vulnerabilityManagedby.grc_team_comments = ''

                    if 'grc_team_validation_response' in vulnerabilityManagedbyObj:

                        vulnerabilityManagedby.grc_team_validation_response =  vulnerabilityManagedbyObj['grc_team_validation_response']
                    else:
                        vulnerabilityManagedby.grc_team_validation_response = ''

                    if 'remediation_comments' in vulnerabilityManagedbyObj:
                        vulnerabilityManagedby.remediation_comments = vulnerabilityManagedbyObj['remediation_comments']
                    else:
                        vulnerabilityManagedby.remediation_comments = ''

                    if 'vulnerability_id' in vulnerabilityManagedbyObj:
                        vulnerabilityManagedby.vulnerability_id = vulnerabilityManagedbyObj['vulnerability_id']
                    else:
                        vulnerabilityManagedby.vulnerability_id = ''

                    if 'vendor_reference' in vulnerabilityManagedbyObj:
                        vulnerabilityManagedby.vendor_reference = vulnerabilityManagedbyObj['vendor_reference']
                    else:
                        vulnerabilityManagedby.vendor_reference = ''
                    
                    if 'vulnerability_details' in vulnerabilityManagedbyObj:
                        vulnerabilityManagedby.vulnerability_details = vulnerabilityManagedbyObj['vulnerability_details']
                    else:
                        vulnerabilityManagedby.vulnerability_details = ''

                        #vulnerabilityManagedby.creation_date= time

                    vulnerabilityManagedby.modification_date= time
                    vulnerabilityManagedby.modified_by= user_data['user_id']
                
                    
                    UpdateData(vulnerabilityManagedby)
                else:
                    return jsonify({'response': "Vulnerability Id can not be found in Table"}), 500  
            else:
                return jsonify({'response': "Vulnerability Id Missing"}), 500  
            return jsonify("Success"), 200
        except Exception as e:
            traceback.print_exc()
            print(f"Error Occured in Adding Vulnerability Managedby {vulnerabilityManagedbyObj['scan_result_id']}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route("/getAllEdnVulnerabilityManagedByDates",methods=['GET'])
@token_required
def GetAllEdnVulnerabilityManagedbyDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_managedby  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   


@app.route("/getAllEdnVulnerabilityManagedbyByDate", methods = ['POST'])
@token_required
def GetAllEdnVulnerabilityManagedbyByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityManagedbyObjList=[]
        #vulnerabilityManagedbyObjs = VULNERABILITY_MANAGEDBY.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityManagedbyObjs =  db.session.execute(f"SELECT * FROM vulnerability_managedby WHERE creation_date = '{current_time}'")

        for vulnerabilityManagedbyObj in vulnerabilityManagedbyObjs:

            vulnerabilityManagedbyDataDict= {}

            vulnerabilityManagedbyDataDict['vulnerability_managedby_id']=vulnerabilityManagedbyObj[0]
            vulnerabilityManagedbyDataDict['scan_result_id'] = vulnerabilityManagedbyObj[1]
            vulnerabilityManagedbyDataDict['device_ip'] = vulnerabilityManagedbyObj[2]
            vulnerabilityManagedbyDataDict['device_name'] = vulnerabilityManagedbyObj[3]
            vulnerabilityManagedbyDataDict['title'] = vulnerabilityManagedbyObj[4]
            if vulnerabilityManagedbyObj[5]:
                vulnerabilityManagedbyDataDict['due_date'] = FormatDate(vulnerabilityManagedbyObj[5])
            vulnerabilityManagedbyDataDict['false_positive_status'] = vulnerabilityManagedbyObj[6]
            vulnerabilityManagedbyDataDict['severity'] = vulnerabilityManagedbyObj[7]
            #vulnerabilityManagedbyDataDict['overall_status'] = vulnerabilityManagedbyObj[8]
            #vulnerabilityManagedbyDataDict['qualys_vuln_status'] = vulnerabilityManagedbyObj[9]
            #vulnerabilityManagedbyDataDict['last_detected'] = FormatDate(vulnerabilityManagedbyObj[10])
            vulnerabilityManagedbyDataDict['technical_contact'] = vulnerabilityManagedbyObj[8]
            #vulnerabilityManagedbyDataDict['exception_requests'] = vulnerabilityManagedbyObj[12]
            vulnerabilityManagedbyDataDict['description']=vulnerabilityManagedbyObj[9]
            vulnerabilityManagedbyDataDict['cve_id'] = vulnerabilityManagedbyObj[10]
            vulnerabilityManagedbyDataDict['device_vendor'] = vulnerabilityManagedbyObj[11]
            if vulnerabilityManagedbyObj[12]:
                vulnerabilityManagedbyDataDict['exception_expiry_date'] = FormatDate(vulnerabilityManagedbyObj[12])
            vulnerabilityManagedbyDataDict['grc_team_comments'] = vulnerabilityManagedbyObj[13]
            vulnerabilityManagedbyDataDict['grc_team_validation_response'] = vulnerabilityManagedbyObj[14]
            vulnerabilityManagedbyDataDict['remediation_comments'] = vulnerabilityManagedbyObj[15]
            vulnerabilityManagedbyDataDict['vulnerability_id'] = vulnerabilityManagedbyObj[16]
            vulnerabilityManagedbyDataDict['vendor_reference'] = vulnerabilityManagedbyObj[17]
            vulnerabilityManagedbyDataDict['vulnerability_details'] = vulnerabilityManagedbyObj[18]
            vulnerabilityManagedbyDataDict['creation_date'] = FormatDate(vulnerabilityManagedbyObj[19])
            vulnerabilityManagedbyDataDict['modification_date'] = FormatDate(vulnerabilityManagedbyObj[20])
            vulnerabilityManagedbyDataDict['created_by'] = vulnerabilityManagedbyObj[21]
            vulnerabilityManagedbyDataDict['modified_by'] = vulnerabilityManagedbyObj[22]
            vulnerabilityManagedbyObjList.append(vulnerabilityManagedbyDataDict)
       
        content = gzip.compress(json.dumps(vulnerabilityManagedbyObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route("/getAllEdnVulnerabilityManagedBy", methods = ['GET'])
@token_required
def GetAllEdnVulnerabilityManagedby(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityManagedbyObjList=[]
        
        vulnerabilityManagedbyObjs =  db.session.execute(f'SELECT * FROM vulnerability_managedby WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_managedby)')

        for vulnerabilityManagedbyObj in vulnerabilityManagedbyObjs:

            vulnerabilityManagedbyDataDict= {}
            vulnerabilityManagedbyDataDict['vulnerability_managedby_id']=vulnerabilityManagedbyObj[0]
            vulnerabilityManagedbyDataDict['scan_result_id'] = vulnerabilityManagedbyObj[1]
            vulnerabilityManagedbyDataDict['device_ip'] = vulnerabilityManagedbyObj[2]
            vulnerabilityManagedbyDataDict['device_name'] = vulnerabilityManagedbyObj[3]
            vulnerabilityManagedbyDataDict['title'] = vulnerabilityManagedbyObj[4]
            if vulnerabilityManagedbyObj[5]:
                vulnerabilityManagedbyDataDict['due_date'] = FormatDate(vulnerabilityManagedbyObj[5])
            vulnerabilityManagedbyDataDict['false_positive_status'] = vulnerabilityManagedbyObj[6]
            vulnerabilityManagedbyDataDict['severity'] = vulnerabilityManagedbyObj[7]
            #vulnerabilityManagedbyDataDict['overall_status'] = vulnerabilityManagedbyObj[8]
            #vulnerabilityManagedbyDataDict['qualys_vuln_status'] = vulnerabilityManagedbyObj[9]
            #vulnerabilityManagedbyDataDict['last_detected'] = FormatDate(vulnerabilityManagedbyObj[10])
            vulnerabilityManagedbyDataDict['technical_contact'] = vulnerabilityManagedbyObj[8]
            #vulnerabilityManagedbyDataDict['exception_requests'] = vulnerabilityManagedbyObj[12]
            vulnerabilityManagedbyDataDict['description']=vulnerabilityManagedbyObj[9]
            vulnerabilityManagedbyDataDict['cve_id'] = vulnerabilityManagedbyObj[10]
            vulnerabilityManagedbyDataDict['device_vendor'] = vulnerabilityManagedbyObj[11]
            if vulnerabilityManagedbyObj[12]:
                vulnerabilityManagedbyDataDict['exception_expiry_date'] = FormatDate(vulnerabilityManagedbyObj[12])
            vulnerabilityManagedbyDataDict['grc_team_comments'] = vulnerabilityManagedbyObj[13]
            vulnerabilityManagedbyDataDict['grc_team_validation_response'] = vulnerabilityManagedbyObj[14]
            vulnerabilityManagedbyDataDict['remediation_comments'] = vulnerabilityManagedbyObj[15]
            vulnerabilityManagedbyDataDict['vulnerability_id'] = vulnerabilityManagedbyObj[16]
            vulnerabilityManagedbyDataDict['vendor_reference'] = vulnerabilityManagedbyObj[17]
            vulnerabilityManagedbyDataDict['vulnerability_details'] = vulnerabilityManagedbyObj[18]
	

            
            vulnerabilityManagedbyDataDict['creation_date'] = FormatDate(vulnerabilityManagedbyObj[19])
            vulnerabilityManagedbyDataDict['modification_date'] = FormatDate(vulnerabilityManagedbyObj[20])
            vulnerabilityManagedbyDataDict['created_by'] = vulnerabilityManagedbyObj[21]
            vulnerabilityManagedbyDataDict['modified_by'] = vulnerabilityManagedbyObj[22]
            
            vulnerabilityManagedbyObjList.append(vulnerabilityManagedbyDataDict)


        content = gzip.compress(json.dumps(vulnerabilityManagedbyObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteEdnVulnerabilityManagedBy",methods = ['POST'])
@token_required
def DeleteEdnVulnerabilityManagedby(user_data):
    if True:#session.get('token', None):
        vulnerabilityManagedbyObj = request.get_json()
        #vulnerabilityManagedbyObj= vulnerabilityManagedbyObj.get("ips")
        #vulnerabilityManagedbyObj = [9,10,11,12,13]
        print(vulnerabilityManagedbyObj,file = sys.stderr)
        
        for obj in vulnerabilityManagedbyObj.get("ips"):
            vulnerabilityManagedbyId = VULNERABILITY_MANAGEDBY.query.filter(VULNERABILITY_MANAGEDBY.vulnerability_managedby_id==obj).first()
            print(vulnerabilityManagedbyId,file=sys.stderr)
            if obj:
                db.session.delete(vulnerabilityManagedbyId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
      


##OPEN ##
###
##

@app.route("/getAllEdnVulnerabilityOpenDates",methods=['GET'])
@token_required
def GetAllEdnVulnerabilityOpenDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_open  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/addEdnVulnerabilityOpen", methods = ['POST'])
@token_required
def AddEdnVulnerabilityOpen(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()
        time= datetime.now(tz)
        print(postData,file=sys.stderr)

        for vulnerabilityOpenObj in postData:
            try:
                vulnerabilityOpen = VULNERABILITY_OPEN()
                if 'scan_result_id' in vulnerabilityOpenObj:
                    vulnerabilityOpen.scan_result_id = vulnerabilityOpenObj['scan_result_id']
                else:
                    print(f"Error Occured in Adding Vulnerability Open Scan Result Id Not Found.", file=sys.stderr)
                    continue

                if 'device_ip' in vulnerabilityOpenObj:
                    vulnerabilityOpen.device_ip = vulnerabilityOpenObj['device_ip']
                else:
                    vulnerabilityOpen.device_ip = ''

                if 'device_name' in vulnerabilityOpenObj:
                    vulnerabilityOpen.device_name = vulnerabilityOpenObj['device_name']
                else:
                    vulnerabilityOpen.device_name = ''

                if 'title' in vulnerabilityOpenObj:
                    vulnerabilityOpen.title = vulnerabilityOpenObj['title']
                else:
                    vulnerabilityOpen.title = ''

                if 'due_date' in vulnerabilityOpenObj:
                    if vulnerabilityOpenObj['due_date']:
                        vulnerabilityOpen.due_date = FormatStringDate(vulnerabilityOpenObj['due_date'])
                #else:
                #    vulnerabilityOpen.due_date = ''

                if 'false_positive_date' in vulnerabilityOpenObj:
                    if vulnerabilityOpenObj['false_positive_date']:
                        vulnerabilityOpen.false_positive_date = FormatStringDate(vulnerabilityOpenObj['false_positive_date'])
                #else:
                #    vulnerabilityOpen.false_positive_date = ''

                if 'severity' in vulnerabilityOpenObj:
                    vulnerabilityOpen.severity = vulnerabilityOpenObj['severity']
                else:
                    vulnerabilityOpen.severity = ''

                if 'overall_status' in vulnerabilityOpenObj:
                    vulnerabilityOpen.overall_status = vulnerabilityOpenObj['overall_status']
                else:
                    vulnerabilityOpen.overall_status = ''

                if 'qualys_vuln_status' in vulnerabilityOpenObj:

                    vulnerabilityOpen.qualys_vuln_status =  vulnerabilityOpenObj['qualys_vuln_status']
                else:
                    vulnerabilityOpen.qualys_vuln_status = ''

                if 'last_detected' in vulnerabilityOpenObj:
                    if vulnerabilityOpenObj['last_detected']:
                        vulnerabilityOpen.last_detected = FormatStringDate(vulnerabilityOpenObj['last_detected'])
                #else:
                #    vulnerabilityOpen.last_detected = ''
                    
                if 'technical_contact' in vulnerabilityOpenObj:
                    vulnerabilityOpen.technical_contact = vulnerabilityOpenObj['technical_contact']
                else:
                    vulnerabilityOpen.technical_contact = ''

                if 'exception_requests' in vulnerabilityOpenObj:
                    vulnerabilityOpen.exception_requests = vulnerabilityOpenObj['exception_requests']
                else:
                    vulnerabilityOpen.exception_requests = ''

                vulnerabilityOpen.creation_date= time
                vulnerabilityOpen.modification_date= time
                vulnerabilityOpen.created_by= user_data['user_id']
                vulnerabilityOpen.modified_by= user_data['user_id']
            
                
                InsertData(vulnerabilityOpen)
            except Exception as e:
                traceback.print_exc()
                print(f"Error Occured in Adding Vulnerability Open {vulnerabilityOpenObj['scan_result_id']}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editEdnVulnerabilityOpen", methods = ['POST'])
@token_required
def EditEdnVulnerabilityOpen(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityOpenObj = request.get_json()
        time= datetime.now(tz)
        #print(postData,file=sys.stderr)

        #for vulnerabilityOpenObj in postData:
        try:
            vulnerabilityOpen = VULNERABILITY_OPEN()
            if 'scan_result_id' in vulnerabilityOpenObj and 'vulnerability_open_id' in vulnerabilityOpenObj:
                vulnerabilityOpenId = VULNERABILITY_OPEN.query.with_entities(VULNERABILITY_OPEN.vulnerability_open_id).filter_by(vulnerability_open_id=vulnerabilityOpenObj['vulnerability_open_id']).first()
                if vulnerabilityOpenId is not None:
                    vulnerabilityOpen.vulnerability_open_id = vulnerabilityOpenId[0]
                    if 'device_ip' in vulnerabilityOpenObj:
                        vulnerabilityOpen.device_ip = vulnerabilityOpenObj['device_ip']
                    else:
                        vulnerabilityOpen.device_ip = ''

                    if 'device_name' in vulnerabilityOpenObj:
                        vulnerabilityOpen.device_name = vulnerabilityOpenObj['device_name']
                    else:
                        vulnerabilityOpen.device_name = ''

                    if 'title' in vulnerabilityOpenObj:
                        vulnerabilityOpen.title = vulnerabilityOpenObj['title']
                    else:
                        vulnerabilityOpen.title = ''

                        
                    if 'due_date' in vulnerabilityOpenObj:
                        if vulnerabilityOpenObj['due_date']:
                            vulnerabilityOpen.due_date = FormatStringDate(vulnerabilityOpenObj['due_date'])
                    #else:
                    #    vulnerabilityOpen.due_date = ''

                    if 'false_positive_date' in vulnerabilityOpenObj:
                        if vulnerabilityOpenObj['false_positive_date']:
                            vulnerabilityOpen.false_positive_date = FormatStringDate(vulnerabilityOpenObj['false_positive_date'])
                    #else:
                    #    vulnerabilityOpen.false_positive_date = ''

                    if 'severity' in vulnerabilityOpenObj:
                        vulnerabilityOpen.severity = vulnerabilityOpenObj['severity']
                    else:
                        vulnerabilityOpen.severity = ''

                    if 'overall_status' in vulnerabilityOpenObj:
                        vulnerabilityOpen.overall_status = vulnerabilityOpenObj['overall_status']
                    else:
                        vulnerabilityOpen.overall_status = ''

                    if 'qualys_vuln_status' in vulnerabilityOpenObj:

                        vulnerabilityOpen.qualys_vuln_status =  vulnerabilityOpenObj['qualys_vuln_status']
                    else:
                        vulnerabilityOpen.qualys_vuln_status = ''

                    if 'last_detected' in vulnerabilityOpenObj:
                        if vulnerabilityOpenObj['last_detected']:
                            vulnerabilityOpen.last_detected = FormatStringDate(vulnerabilityOpenObj['last_detected'])
                    #else:
                    #    vulnerabilityOpen.last_detected = ''
                            
                    if 'technical_contact' in vulnerabilityOpenObj:
                        vulnerabilityOpen.technical_contact = vulnerabilityOpenObj['technical_contact']
                    else:
                        vulnerabilityOpen.technical_contact = ''

                    if 'exception_requests' in vulnerabilityOpenObj:
                        vulnerabilityOpen.exception_requests = vulnerabilityOpenObj['exception_requests']
                    else:
                        vulnerabilityOpen.exception_requests = ''

                    #vulnerabilityOpen.creation_date= time
                    vulnerabilityOpen.modification_date= time
                    vulnerabilityOpen.modified_by= user_data['user_id']
                
                    
                    UpdateData(vulnerabilityOpen)
                else:
                    return jsonify({'response': "Vulnerability Id can not be found in Table"}), 500  
            else:
                return jsonify({'response': "Vulnerability Id Missing"}), 500  
            return jsonify({'response': "success","code":"200"})
        except Exception as e:
            traceback.print_exc()
            print(f"Error Occured in Adding Vulnerability Open {vulnerabilityOpenObj['scan_result_id']}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnVulnerabilityOpenByDate", methods = ['POST'])
@token_required
def GetAllEdnVulnerabilityOpenByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityOpenObjList=[]
        #vulnerabilityOpenObjs = VULNERABILITY_OPEN.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityOpenObjs =  db.session.execute(f"SELECT * FROM vulnerability_open WHERE creation_date = '{current_time}'")

        for vulnerabilityOpenObj in vulnerabilityOpenObjs:

            vulnerabilityOpenDataDict= {}
            vulnerabilityOpenDataDict['vulnerability_open_id']=vulnerabilityOpenObj[0]
            vulnerabilityOpenDataDict['scan_result_id'] = vulnerabilityOpenObj[1]
            vulnerabilityOpenDataDict['device_ip'] = vulnerabilityOpenObj[2]
            vulnerabilityOpenDataDict['device_name'] = vulnerabilityOpenObj[3]
            vulnerabilityOpenDataDict['title'] = vulnerabilityOpenObj[4]
            if vulnerabilityOpenObj[5]:
                vulnerabilityOpenDataDict['due_date'] = FormatDate(vulnerabilityOpenObj[5])
            if vulnerabilityOpenObj[6]:
                vulnerabilityOpenDataDict['false_positive_date'] =FormatDate( vulnerabilityOpenObj[6])
            vulnerabilityOpenDataDict['severity'] = vulnerabilityOpenObj[7]
            vulnerabilityOpenDataDict['overall_status'] = vulnerabilityOpenObj[8]
            vulnerabilityOpenDataDict['qualys_vuln_status'] = vulnerabilityOpenObj[9]
            if vulnerabilityOpenObj[10]:
                vulnerabilityOpenDataDict['last_detected'] = FormatDate(vulnerabilityOpenObj[10])
            vulnerabilityOpenDataDict['technical_contact'] = vulnerabilityOpenObj[11]
            vulnerabilityOpenDataDict['exception_requests'] = vulnerabilityOpenObj[12]
            vulnerabilityOpenDataDict['creation_date'] = FormatDate(vulnerabilityOpenObj[13])
            vulnerabilityOpenDataDict['modification_date'] = FormatDate(vulnerabilityOpenObj[14])
            vulnerabilityOpenDataDict['created_by'] = vulnerabilityOpenObj[15]
            vulnerabilityOpenDataDict['modified_by'] = vulnerabilityOpenObj[16]
            vulnerabilityOpenObjList.append(vulnerabilityOpenDataDict)

       
        content = gzip.compress(json.dumps(vulnerabilityOpenObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnVulnerabilityOpen", methods = ['GET'])
@token_required
def GetAllEdnVulnerabilityOpen(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityOpenObjList=[]
        
        vulnerabilityOpenObjs =  db.session.execute(f'SELECT * FROM vulnerability_open WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_open)')

        for vulnerabilityOpenObj in vulnerabilityOpenObjs:

            vulnerabilityOpenDataDict= {}
            vulnerabilityOpenDataDict['vulnerability_open_id']=vulnerabilityOpenObj[0]
            vulnerabilityOpenDataDict['scan_result_id'] = vulnerabilityOpenObj[1]
            vulnerabilityOpenDataDict['device_ip'] = vulnerabilityOpenObj[2]
            vulnerabilityOpenDataDict['device_name'] = vulnerabilityOpenObj[3]
            vulnerabilityOpenDataDict['title'] = vulnerabilityOpenObj[4]
            if vulnerabilityOpenObj[5]:
                vulnerabilityOpenDataDict['due_date'] = FormatDate(vulnerabilityOpenObj[5])
            if vulnerabilityOpenObj[6]:
                vulnerabilityOpenDataDict['false_positive_date'] =FormatDate( vulnerabilityOpenObj[6])
            vulnerabilityOpenDataDict['severity'] = vulnerabilityOpenObj[7]
            vulnerabilityOpenDataDict['overall_status'] = vulnerabilityOpenObj[8]
            vulnerabilityOpenDataDict['qualys_vuln_status'] = vulnerabilityOpenObj[9]
            if vulnerabilityOpenObj[10]:
                vulnerabilityOpenDataDict['last_detected'] = FormatDate(vulnerabilityOpenObj[10])
            vulnerabilityOpenDataDict['technical_contact'] = vulnerabilityOpenObj[11]
            vulnerabilityOpenDataDict['exception_requests'] = vulnerabilityOpenObj[12]
            vulnerabilityOpenDataDict['creation_date'] = FormatDate(vulnerabilityOpenObj[13])
            vulnerabilityOpenDataDict['modification_date'] = FormatDate(vulnerabilityOpenObj[14])
            vulnerabilityOpenDataDict['created_by'] = vulnerabilityOpenObj[15]
            vulnerabilityOpenDataDict['modified_by'] = vulnerabilityOpenObj[16]
            vulnerabilityOpenObjList.append(vulnerabilityOpenDataDict)

        content = gzip.compress(json.dumps(vulnerabilityOpenObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteEdnVulnerabilityOpen",methods = ['POST'])
@token_required
def DeleteEdnVulnerabilityOpen(user_data):
    if True:#session.get('token', None):
        vulnerabilityOpenObj = request.get_json()
        #vulnerabilityOpenObj= vulnerabilityOpenObj.get("ips")
        #vulnerabilityOpenObj = [9,10,11,12,13]
        print(vulnerabilityOpenObj,file = sys.stderr)
        
        for obj in vulnerabilityOpenObj.get("ips"):
            vulnerabilityOpenId = VULNERABILITY_OPEN.query.filter(VULNERABILITY_OPEN.vulnerability_open_id==obj).first()
            print(vulnerabilityOpenId,file=sys.stderr)
            if obj:
                db.session.delete(vulnerabilityOpenId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
       
###
# Over Due
##


@app.route("/getAllEdnVulnerabilityOverdueDates",methods=['GET'])
@token_required
def GetAllEdnVulnerabilityOverdueDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_overdue  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/addEdnVulnerabilityOverdue", methods = ['POST'])
@token_required
def AddEdnVulnerabilityOverdue(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()
        time= datetime.now(tz)
        print(postData,file=sys.stderr)

        for vulnerabilityOverdueObj in postData:
            try:
                vulnerabilityOverdue = VULNERABILITY_OVERDUE()
                if 'scan_result_id' in vulnerabilityOverdueObj:
                    vulnerabilityOverdue.scan_result_id = vulnerabilityOverdueObj['scan_result_id']
                else:
                    print(f"Error Occured in Adding Vulnerability Overdue Scan Result Id Not Found.", file=sys.stderr)
                    continue

                if 'device_ip' in vulnerabilityOverdueObj:
                    vulnerabilityOverdue.device_ip = vulnerabilityOverdueObj['device_ip']
                else:
                    vulnerabilityOverdue.device_ip = ''

                if 'device_name' in vulnerabilityOverdueObj:
                    vulnerabilityOverdue.device_name = vulnerabilityOverdueObj['device_name']
                else:
                    vulnerabilityOverdue.device_name = ''

                if 'title' in vulnerabilityOverdueObj:
                    vulnerabilityOverdue.title = vulnerabilityOverdueObj['title']
                else:
                    vulnerabilityOverdue.title = ''

                if 'due_date' in vulnerabilityOverdueObj:
                    if vulnerabilityOverdueObj['due_date']:
                        vulnerabilityOverdue.due_date = FormatStringDate(vulnerabilityOverdueObj['due_date'])
                #else:
                #    vulnerabilityOverdue.due_date = ''

                if 'false_positive_date' in vulnerabilityOverdueObj:
                    if vulnerabilityOverdueObj['false_positive_date']:
                        vulnerabilityOverdue.false_positive_date = FormatStringDate(vulnerabilityOverdueObj['false_positive_date'])
                #else:
                #    vulnerabilityOverdue.false_positive_date = ''

                if 'severity' in vulnerabilityOverdueObj:
                    vulnerabilityOverdue.severity = vulnerabilityOverdueObj['severity']
                else:
                    vulnerabilityOverdue.severity = ''

                if 'overall_status' in vulnerabilityOverdueObj:
                    vulnerabilityOverdue.overall_status = vulnerabilityOverdueObj['overall_status']
                else:
                    vulnerabilityOverdue.overall_status = ''

                if 'qualys_vuln_status' in vulnerabilityOverdueObj:

                    vulnerabilityOverdue.qualys_vuln_status =  vulnerabilityOverdueObj['qualys_vuln_status']
                else:
                    vulnerabilityOverdue.qualys_vuln_status = ''

                if 'last_detected' in vulnerabilityOverdueObj:
                    if vulnerabilityOverdueObj['last_detected']:
                        vulnerabilityOverdue.last_detected = FormatStringDate(vulnerabilityOverdueObj['last_detected'])
                #else:
                #    vulnerabilityOverdue.last_detected = ''
                    
                if 'technical_contact' in vulnerabilityOverdueObj:
                    vulnerabilityOverdue.technical_contact = vulnerabilityOverdueObj['technical_contact']
                else:
                    vulnerabilityOverdue.technical_contact = ''

                if 'exception_requests' in vulnerabilityOverdueObj:
                    vulnerabilityOverdue.exception_requests = vulnerabilityOverdueObj['exception_requests']
                else:
                    vulnerabilityOverdue.exception_requests = ''

                vulnerabilityOverdue.creation_date= time
                vulnerabilityOverdue.modification_date= time

                vulnerabilityOverdue.created_by= user_data['user_id']
                vulnerabilityOverdue.modified_by= user_data['user_id']
                
                InsertData(vulnerabilityOverdue)
            except Exception as e:
                traceback.print_exc()
                print(f"Error Occured in Adding Vulnerability Overdue {vulnerabilityOverdueObj['scan_result_id']}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editEdnVulnerabilityOverdue", methods = ['POST'])
@token_required
def EditEdnVulnerabilityOverdue(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityOverdueObj = request.get_json()
        time= datetime.now(tz)
        #print(postData,file=sys.stderr)

        #for vulnerabilityOverdueObj in postData:
        try:
            vulnerabilityOverdue = VULNERABILITY_OVERDUE()
            if 'scan_result_id' in vulnerabilityOverdueObj and 'vulnerability_overdue_id' in vulnerabilityOverdueObj:
                vulnerabilityOverdueId = VULNERABILITY_OVERDUE.query.with_entities(VULNERABILITY_OVERDUE.vulnerability_overdue_id).filter_by(vulnerability_overdue_id=vulnerabilityOverdueObj['vulnerability_overdue_id']).first()
                if vulnerabilityOverdueId is not None:
                    vulnerabilityOverdue.vulnerability_overdue_id= vulnerabilityOverdueId[0]
                    if 'device_ip' in vulnerabilityOverdueObj:
                        vulnerabilityOverdue.device_ip = vulnerabilityOverdueObj['device_ip']
                    else:
                        vulnerabilityOverdue.device_ip = ''

                    if 'device_name' in vulnerabilityOverdueObj:
                        vulnerabilityOverdue.device_name = vulnerabilityOverdueObj['device_name']
                    else:
                        vulnerabilityOverdue.device_name = ''

                    if 'title' in vulnerabilityOverdueObj:
                        vulnerabilityOverdue.title = vulnerabilityOverdueObj['title']
                    else:
                        vulnerabilityOverdue.title = ''

                        
                    if 'due_date' in vulnerabilityOverdueObj:
                        if vulnerabilityOverdueObj['due_date']:
                            vulnerabilityOverdue.due_date = FormatStringDate(vulnerabilityOverdueObj['due_date'])
                    #else:
                    #    vulnerabilityOverdue.due_date = ''

                    if 'false_positive_date' in vulnerabilityOverdueObj:
                        if vulnerabilityOverdueObj['false_positive_date']:
                            vulnerabilityOverdue.false_positive_date = FormatStringDate(vulnerabilityOverdueObj['false_positive_date'])
                    #else:
                    #    vulnerabilityOverdue.false_positive_date = ''

                    if 'severity' in vulnerabilityOverdueObj:
                        vulnerabilityOverdue.severity = vulnerabilityOverdueObj['severity']
                    else:
                        vulnerabilityOverdue.severity = ''

                    if 'overall_status' in vulnerabilityOverdueObj:
                        vulnerabilityOverdue.overall_status = vulnerabilityOverdueObj['overall_status']
                    else:
                        vulnerabilityOverdue.overall_status = ''

                    if 'qualys_vuln_status' in vulnerabilityOverdueObj:

                        vulnerabilityOverdue.qualys_vuln_status =  vulnerabilityOverdueObj['qualys_vuln_status']
                    else:
                        vulnerabilityOverdue.qualys_vuln_status = ''

                    if 'last_detected' in vulnerabilityOverdueObj:
                        if vulnerabilityOverdueObj['last_detected']:
                            vulnerabilityOverdue.last_detected = FormatStringDate(vulnerabilityOverdueObj['last_detected'])
                    #else:
                    #    vulnerabilityOverdue.last_detected = ''
                            
                    if 'technical_contact' in vulnerabilityOverdueObj:
                        vulnerabilityOverdue.technical_contact = vulnerabilityOverdueObj['technical_contact']
                    else:
                        vulnerabilityOverdue.technical_contact = ''

                    if 'exception_requests' in vulnerabilityOverdueObj:
                        vulnerabilityOverdue.exception_requests = vulnerabilityOverdueObj['exception_requests']
                    else:
                        vulnerabilityOverdue.exception_requests = ''

                    #vulnerabilityOverdue.creation_date= time
                    vulnerabilityOverdue.modification_date= time
                    vulnerabilityOverdue.modified_by= user_data['user_id']
                
                    
                    UpdateData(vulnerabilityOverdue)
                else:
                    return jsonify({'response': "Vulnerability Id can not be found in Table"}), 500  
            else:
                return jsonify({'response': "Vulnerability Id Missing"}), 500  
            return jsonify({'response': "success","code":"200"})

        except Exception as e:
            traceback.print_exc()
            print(f"Error Occured in Adding Vulnerability Overdue {vulnerabilityOverdueObj['scan_result_id']}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnVulnerabilityOverdueByDate", methods = ['POST'])
@token_required
def GetAllEdnVulnerabilityOverdueByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityOverdueObjList=[]
        #vulnerabilityOverdueObjs = VULNERABILITY_OVERDUE.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityOverdueObjs =  db.session.execute(f"SELECT * FROM vulnerability_overdue WHERE creation_date = '{current_time}'")

        for vulnerabilityOverdueObj in vulnerabilityOverdueObjs:

            vulnerabilityOverdueDataDict= {}
            vulnerabilityOverdueDataDict['vulnerability_overdue_id']=vulnerabilityOverdueObj[0]
            vulnerabilityOverdueDataDict['scan_result_id'] = vulnerabilityOverdueObj[1]
            vulnerabilityOverdueDataDict['device_ip'] = vulnerabilityOverdueObj[2]
            vulnerabilityOverdueDataDict['device_name'] = vulnerabilityOverdueObj[3]
            vulnerabilityOverdueDataDict['title'] = vulnerabilityOverdueObj[4]
            if vulnerabilityOverdueObj[5]:
                vulnerabilityOverdueDataDict['due_date'] = FormatDate(vulnerabilityOverdueObj[5])
            if vulnerabilityOverdueObj[6]:
                vulnerabilityOverdueDataDict['false_positive_date'] =FormatDate( vulnerabilityOverdueObj[6])
            vulnerabilityOverdueDataDict['severity'] = vulnerabilityOverdueObj[7]
            vulnerabilityOverdueDataDict['overall_status'] = vulnerabilityOverdueObj[8]
            vulnerabilityOverdueDataDict['qualys_vuln_status'] = vulnerabilityOverdueObj[9]
            if vulnerabilityOverdueObj[10]:
                vulnerabilityOverdueDataDict['last_detected'] = FormatDate(vulnerabilityOverdueObj[10])
            vulnerabilityOverdueDataDict['technical_contact'] = vulnerabilityOverdueObj[11]
            vulnerabilityOverdueDataDict['exception_requests'] = vulnerabilityOverdueObj[12]
            vulnerabilityOverdueDataDict['creation_date'] = FormatDate(vulnerabilityOverdueObj[13])
            vulnerabilityOverdueDataDict['modification_date'] = FormatDate(vulnerabilityOverdueObj[14])
            vulnerabilityOverdueDataDict['created_by'] = vulnerabilityOverdueObj[15]
            vulnerabilityOverdueDataDict['modified_by'] = vulnerabilityOverdueObj[16]
            vulnerabilityOverdueObjList.append(vulnerabilityOverdueDataDict)

       
        content = gzip.compress(json.dumps(vulnerabilityOverdueObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnVulnerabilityOverdue", methods = ['GET'])
@token_required
def GetAllEdnVulnerabilityOverdue(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityOverdueObjList=[]
        
        vulnerabilityOverdueObjs =  db.session.execute(f'SELECT * FROM vulnerability_overdue WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_overdue)')

        for vulnerabilityOverdueObj in vulnerabilityOverdueObjs:

            vulnerabilityOverdueDataDict= {}
            vulnerabilityOverdueDataDict['vulnerability_overdue_id']=vulnerabilityOverdueObj[0]
            vulnerabilityOverdueDataDict['scan_result_id'] = vulnerabilityOverdueObj[1]
            vulnerabilityOverdueDataDict['device_ip'] = vulnerabilityOverdueObj[2]
            vulnerabilityOverdueDataDict['device_name'] = vulnerabilityOverdueObj[3]
            vulnerabilityOverdueDataDict['title'] = vulnerabilityOverdueObj[4]
            if vulnerabilityOverdueObj[5]:
                vulnerabilityOverdueDataDict['due_date'] = FormatDate(vulnerabilityOverdueObj[5])
            if vulnerabilityOverdueObj[6]:
                vulnerabilityOverdueDataDict['false_positive_date'] =FormatDate( vulnerabilityOverdueObj[6])
            vulnerabilityOverdueDataDict['severity'] = vulnerabilityOverdueObj[7]
            vulnerabilityOverdueDataDict['overall_status'] = vulnerabilityOverdueObj[8]
            vulnerabilityOverdueDataDict['qualys_vuln_status'] = vulnerabilityOverdueObj[9]
            if vulnerabilityOverdueObj[10]:
                vulnerabilityOverdueDataDict['last_detected'] = FormatDate(vulnerabilityOverdueObj[10])
            vulnerabilityOverdueDataDict['technical_contact'] = vulnerabilityOverdueObj[11]
            vulnerabilityOverdueDataDict['exception_requests'] = vulnerabilityOverdueObj[12]
            vulnerabilityOverdueDataDict['creation_date'] = FormatDate(vulnerabilityOverdueObj[13])
            vulnerabilityOverdueDataDict['modification_date'] = FormatDate(vulnerabilityOverdueObj[14])
            vulnerabilityOverdueDataDict['created_by'] = vulnerabilityOverdueObj[15]
            vulnerabilityOverdueDataDict['modified_by'] = vulnerabilityOverdueObj[16]
            vulnerabilityOverdueObjList.append(vulnerabilityOverdueDataDict)

        content = gzip.compress(json.dumps(vulnerabilityOverdueObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteEdnVulnerabilityOverdue",methods = ['POST'])
@token_required
def DeleteEdnVulnerabilityOverdue(user_data):
    if True:#session.get('token', None):
        vulnerabilityOverdueObj = request.get_json()
        #vulnerabilityOverdueObj= vulnerabilityOverdueObj.get("ips")
        #vulnerabilityOverdueObj = [9,10,11,12,13]
        print(vulnerabilityOverdueObj,file = sys.stderr)
        
        for obj in vulnerabilityOverdueObj.get("ips"):
            vulnerabilityOverdueId = VULNERABILITY_OVERDUE.query.filter(VULNERABILITY_OVERDUE.vulnerability_overdue_id==obj).first()
            print(vulnerabilityOverdueId,file=sys.stderr)
            if obj:
                db.session.delete(vulnerabilityOverdueId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
       

####
# In Progress
###
@app.route("/getAllEdnVulnerabilityInProgressDates",methods=['GET'])
@token_required
def GetAllEdnVulnerabilityInprogressDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_inprogress  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/addEdnVulnerabilityInProgress", methods = ['POST'])
@token_required
def AddEdnVulnerabilityInprogress(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()
        time= datetime.now(tz)
        print(postData,file=sys.stderr)

        for vulnerabilityInprogressObj in postData:
            try:
                vulnerabilityInprogress = VULNERABILITY_INPROGRESS()
                if 'scan_result_id' in vulnerabilityInprogressObj:
                    vulnerabilityInprogress.scan_result_id = vulnerabilityInprogressObj['scan_result_id']
                else:
                    print(f"Error Occured in Adding Vulnerability Inprogress Scan Result Id Not Found.", file=sys.stderr)
                    continue

                if 'device_ip' in vulnerabilityInprogressObj:
                    vulnerabilityInprogress.device_ip = vulnerabilityInprogressObj['device_ip']
                else:
                    vulnerabilityInprogress.device_ip = ''

                if 'device_name' in vulnerabilityInprogressObj:
                    vulnerabilityInprogress.device_name = vulnerabilityInprogressObj['device_name']
                else:
                    vulnerabilityInprogress.device_name = ''

                if 'title' in vulnerabilityInprogressObj:
                    vulnerabilityInprogress.title = vulnerabilityInprogressObj['title']
                else:
                    vulnerabilityInprogress.title = ''

                if 'due_date' in vulnerabilityInprogressObj:
                    if vulnerabilityInprogressObj['due_date']:
                        vulnerabilityInprogress.due_date = FormatStringDate(vulnerabilityInprogressObj['due_date'])
                #else:
                #    vulnerabilityInprogress.due_date = ''

                if 'false_positive_date' in vulnerabilityInprogressObj:
                    if vulnerabilityInprogressObj['false_positive_date']:
                        vulnerabilityInprogress.false_positive_date = FormatStringDate(vulnerabilityInprogressObj['false_positive_date'])
                #else:
                #    vulnerabilityInprogress.false_positive_date = ''

                if 'severity' in vulnerabilityInprogressObj:
                    vulnerabilityInprogress.severity = vulnerabilityInprogressObj['severity']
                else:
                    vulnerabilityInprogress.severity = ''

                if 'overall_status' in vulnerabilityInprogressObj:
                    vulnerabilityInprogress.overall_status = vulnerabilityInprogressObj['overall_status']
                else:
                    vulnerabilityInprogress.overall_status = ''

                if 'qualys_vuln_status' in vulnerabilityInprogressObj:

                    vulnerabilityInprogress.qualys_vuln_status =  vulnerabilityInprogressObj['qualys_vuln_status']
                else:
                    vulnerabilityInprogress.qualys_vuln_status = ''

                if 'last_detected' in vulnerabilityInprogressObj:
                    if vulnerabilityInprogressObj['last_detected']:
                        vulnerabilityInprogress.last_detected = FormatStringDate(vulnerabilityInprogressObj['last_detected'])
                #else:
                #    vulnerabilityInprogress.last_detected = ''
                    
                if 'technical_contact' in vulnerabilityInprogressObj:
                    vulnerabilityInprogress.technical_contact = vulnerabilityInprogressObj['technical_contact']
                else:
                    vulnerabilityInprogress.technical_contact = ''

                if 'exception_requests' in vulnerabilityInprogressObj:
                    vulnerabilityInprogress.exception_requests = vulnerabilityInprogressObj['exception_requests']
                else:
                    vulnerabilityInprogress.exception_requests = ''

                vulnerabilityInprogress.creation_date= time
                vulnerabilityInprogress.modification_date= time

                vulnerabilityInprogress.created_by= user_data['user_id']
                vulnerabilityInprogress.modified_by= user_data['user_id']
            
                
                InsertData(vulnerabilityInprogress)
            except Exception as e:
                traceback.print_exc()
                print(f"Error Occured in Adding Vulnerability Inprogress {vulnerabilityInprogressObj['scan_result_id']}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editEdnVulnerabilityInProgress", methods = ['POST'])
@token_required
def EditEdnVulnerabilityInprogress(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityInprogressObj = request.get_json()
        time= datetime.now(tz)
        #print(postData,file=sys.stderr)

        #for vulnerabilityInprogressObj in postData:
        try:
            vulnerabilityInprogress = VULNERABILITY_INPROGRESS()
            if 'scan_result_id' in vulnerabilityInprogressObj and 'vulnerability_inprogress_id' in vulnerabilityInprogressObj:
                vulnerabilityInprogressId = VULNERABILITY_INPROGRESS.query.with_entities(VULNERABILITY_INPROGRESS.vulnerability_inprogress_id).filter_by(vulnerability_inprogress_id=vulnerabilityInprogressObj['vulnerability_inprogress_id']).first()
                if vulnerabilityInprogressId is not None:
                    vulnerabilityInprogress.vulnerability_inprogress_id= vulnerabilityInprogressId[0]
                    if 'device_ip' in vulnerabilityInprogressObj:
                        vulnerabilityInprogress.device_ip = vulnerabilityInprogressObj['device_ip']
                    else:
                        vulnerabilityInprogress.device_ip = ''

                    if 'device_name' in vulnerabilityInprogressObj:
                        vulnerabilityInprogress.device_name = vulnerabilityInprogressObj['device_name']
                    else:
                        vulnerabilityInprogress.device_name = ''

                    if 'title' in vulnerabilityInprogressObj:
                        vulnerabilityInprogress.title = vulnerabilityInprogressObj['title']
                    else:
                        vulnerabilityInprogress.title = ''

                        
                    if 'due_date' in vulnerabilityInprogressObj:
                        if vulnerabilityInprogressObj['due_date']:
                            vulnerabilityInprogress.due_date = FormatStringDate(vulnerabilityInprogressObj['due_date'])
                    #else:
                    #    vulnerabilityInprogress.due_date = ''

                    if 'false_positive_date' in vulnerabilityInprogressObj:
                        if vulnerabilityInprogressObj['false_positive_date']:
                            vulnerabilityInprogress.false_positive_date = FormatStringDate(vulnerabilityInprogressObj['false_positive_date'])
                    #else:
                    #    vulnerabilityInprogress.false_positive_date = ''

                    if 'severity' in vulnerabilityInprogressObj:
                        vulnerabilityInprogress.severity = vulnerabilityInprogressObj['severity']
                    else:
                        vulnerabilityInprogress.severity = ''

                    if 'overall_status' in vulnerabilityInprogressObj:
                        vulnerabilityInprogress.overall_status = vulnerabilityInprogressObj['overall_status']
                    else:
                        vulnerabilityInprogress.overall_status = ''

                    if 'qualys_vuln_status' in vulnerabilityInprogressObj:

                        vulnerabilityInprogress.qualys_vuln_status =  vulnerabilityInprogressObj['qualys_vuln_status']
                    else:
                        vulnerabilityInprogress.qualys_vuln_status = ''

                    if 'last_detected' in vulnerabilityInprogressObj:
                        if vulnerabilityInprogressObj['last_detected']:
                            vulnerabilityInprogress.last_detected = FormatStringDate(vulnerabilityInprogressObj['last_detected'])
                    #else:
                    #    vulnerabilityInprogress.last_detected = ''
                            
                    if 'technical_contact' in vulnerabilityInprogressObj:
                        vulnerabilityInprogress.technical_contact = vulnerabilityInprogressObj['technical_contact']
                    else:
                        vulnerabilityInprogress.technical_contact = ''

                    if 'exception_requests' in vulnerabilityInprogressObj:
                        vulnerabilityInprogress.exception_requests = vulnerabilityInprogressObj['exception_requests']
                    else:
                        vulnerabilityInprogress.exception_requests = ''

                    #vulnerabilityInprogress.creation_date= time
                    vulnerabilityInprogress.modification_date= time
                    vulnerabilityInprogress.modified_by= user_data['user_id']
                
                    
                    UpdateData(vulnerabilityInprogress)
                else:
                    return jsonify({'response': "Vulnerability Id can not be found in Table"}), 500  
            else:
                return jsonify({'response': "Vulnerability Id Missing"}), 500 

            return jsonify({'response': "success","code":"200"})
        except Exception as e:
            traceback.print_exc()
            print(f"Error Occured in Adding Vulnerability Inprogress {vulnerabilityInprogressObj['scan_result_id']}", file=sys.stderr)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnVulnerabilityInProgressByDate", methods = ['POST'])
@token_required
def GetAllEdnVulnerabilityInprogressByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityInprogressObjList=[]
        #vulnerabilityInprogressObjs = VULNERABILITY_INPROGRESS.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityInprogressObjs =  db.session.execute(f"SELECT * FROM vulnerability_inprogress WHERE creation_date = '{current_time}'")

        for vulnerabilityInprogressObj in vulnerabilityInprogressObjs:

            vulnerabilityInprogressDataDict= {}
            vulnerabilityInprogressDataDict['vulnerability_inprogress_id']=vulnerabilityInprogressObj[0]
            vulnerabilityInprogressDataDict['scan_result_id'] = vulnerabilityInprogressObj[1]
            vulnerabilityInprogressDataDict['device_ip'] = vulnerabilityInprogressObj[2]
            vulnerabilityInprogressDataDict['device_name'] = vulnerabilityInprogressObj[3]
            vulnerabilityInprogressDataDict['title'] = vulnerabilityInprogressObj[4]
            if vulnerabilityInprogressObj[5]:
                vulnerabilityInprogressDataDict['due_date'] = FormatDate(vulnerabilityInprogressObj[5])
            if vulnerabilityInprogressObj[6]:
                vulnerabilityInprogressDataDict['false_positive_date'] =FormatDate( vulnerabilityInprogressObj[6])
            vulnerabilityInprogressDataDict['severity'] = vulnerabilityInprogressObj[7]
            vulnerabilityInprogressDataDict['overall_status'] = vulnerabilityInprogressObj[8]
            vulnerabilityInprogressDataDict['qualys_vuln_status'] = vulnerabilityInprogressObj[9]
            if vulnerabilityInprogressObj[10]:
                vulnerabilityInprogressDataDict['last_detected'] = FormatDate(vulnerabilityInprogressObj[10])
            vulnerabilityInprogressDataDict['technical_contact'] = vulnerabilityInprogressObj[11]
            vulnerabilityInprogressDataDict['exception_requests'] = vulnerabilityInprogressObj[12]
            vulnerabilityInprogressDataDict['creation_date'] = FormatDate(vulnerabilityInprogressObj[13])
            vulnerabilityInprogressDataDict['modification_date'] = FormatDate(vulnerabilityInprogressObj[14])
            vulnerabilityInprogressDataDict['created_by'] = vulnerabilityInprogressObj[15]
            vulnerabilityInprogressDataDict['modified_by'] = vulnerabilityInprogressObj[16]
            vulnerabilityInprogressObjList.append(vulnerabilityInprogressDataDict)

       
        content = gzip.compress(json.dumps(vulnerabilityInprogressObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnVulnerabilityInProgress", methods = ['GET'])
@token_required
def GetAllEdnVulnerabilityInprogress(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityInprogressObjList=[]
        
        vulnerabilityInprogressObjs =  db.session.execute(f'SELECT * FROM vulnerability_inprogress WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_inprogress)')

        for vulnerabilityInprogressObj in vulnerabilityInprogressObjs:

            vulnerabilityInprogressDataDict= {}
            vulnerabilityInprogressDataDict['vulnerability_inprogress_id']=vulnerabilityInprogressObj[0]
            vulnerabilityInprogressDataDict['scan_result_id'] = vulnerabilityInprogressObj[1]
            vulnerabilityInprogressDataDict['device_ip'] = vulnerabilityInprogressObj[2]
            vulnerabilityInprogressDataDict['device_name'] = vulnerabilityInprogressObj[3]
            vulnerabilityInprogressDataDict['title'] = vulnerabilityInprogressObj[4]
            if vulnerabilityInprogressObj[5]:
                vulnerabilityInprogressDataDict['due_date'] = FormatDate(vulnerabilityInprogressObj[5])
            if vulnerabilityInprogressObj[6]:
                vulnerabilityInprogressDataDict['false_positive_date'] =FormatDate( vulnerabilityInprogressObj[6])
            vulnerabilityInprogressDataDict['severity'] = vulnerabilityInprogressObj[7]
            vulnerabilityInprogressDataDict['overall_status'] = vulnerabilityInprogressObj[8]
            vulnerabilityInprogressDataDict['qualys_vuln_status'] = vulnerabilityInprogressObj[9]
            if vulnerabilityInprogressObj[10]:
                vulnerabilityInprogressDataDict['last_detected'] = FormatDate(vulnerabilityInprogressObj[10])
            vulnerabilityInprogressDataDict['technical_contact'] = vulnerabilityInprogressObj[11]
            vulnerabilityInprogressDataDict['exception_requests'] = vulnerabilityInprogressObj[12]
            vulnerabilityInprogressDataDict['creation_date'] = FormatDate(vulnerabilityInprogressObj[13])
            vulnerabilityInprogressDataDict['modification_date'] = FormatDate(vulnerabilityInprogressObj[14])
            vulnerabilityInprogressDataDict['created_by'] = vulnerabilityInprogressObj[15]
            vulnerabilityInprogressDataDict['modified_by'] = vulnerabilityInprogressObj[16]
            vulnerabilityInprogressObjList.append(vulnerabilityInprogressDataDict)

        content = gzip.compress(json.dumps(vulnerabilityInprogressObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteEdnVulnerabilityInProgress",methods = ['POST'])
@token_required
def DeleteEdnVulnerabilityInprogress(user_data):
    if True:#session.get('token', None):
        vulnerabilityInprogressObj = request.get_json()
        #vulnerabilityInprogressObj= vulnerabilityInprogressObj.get("ips")
        #vulnerabilityInprogressObj = [9,10,11,12,13]
        print(vulnerabilityInprogressObj,file = sys.stderr)
        
        for obj in vulnerabilityInprogressObj.get("ips"):
            vulnerabilityInprogressId = VULNERABILITY_INPROGRESS.query.filter(VULNERABILITY_INPROGRESS.vulnerability_inprogress_id==obj).first()
            print(vulnerabilityInprogressId,file=sys.stderr)
            if obj:
                db.session.delete(vulnerabilityInprogressId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
'''       

#### EDN MASTER Vulnerbility ROUTES   ###
@app.route("/syncEdnVulnerabilityMaster", methods = ['GET'])
@token_required
def syncEdnVulnerabilityMaster(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        try:
            syncEdnVulnerabilityMasterFunc(user_data)
        except Exception as e:
            print(f"Error Occured in  Population of Master Table {e}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def syncEdnVulnerabilityMasterFunc(user_data):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "EDN-VULN-TO-MASTER").first()
    try:
        vulnStatus.script = "EDN-VULN-TO-MASTER"
        vulnStatus.status = "Running"
        vulnStatus.creation_date= current_time
        vulnStatus.modification_date= current_time
        db.session.add(vulnStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    for table in range(1):
        
        if table==0:
            print("Populating Archer Vulnerabilities in Master", file=sys.stderr)
            creation_date=""
            creationObj = db.session.execute('SELECT max(creation_date) FROM vulnerability_edn_archer')
            for row in creationObj:
                creation_date=row[0]
            vulnerabilityObjs = VULNERABILITY_EDN_ARCHER.query.filter_by(creation_date=creation_date).all()
        
        '''
        if table==1:
            print("Populating Open Vulnerabilities in Master", file=sys.stderr)
            creation_date=""
            creationObj = db.session.execute('SELECT max(creation_date) FROM vulnerability_open')
            for row in creationObj:
                creation_date=row[0]
            vulnerabilityObjs = VULNERABILITY_OPEN.query.filter_by(creation_date=creation_date).all()
        
        if table==2:
            print("Populating In Progress Vulnerabilities in Master", file=sys.stderr)
            creation_date=""
            creationObj = db.session.execute('SELECT max(creation_date) FROM vulnerability_inprogress')
            for row in creationObj:
                creation_date=row[0]
            vulnerabilityObjs = VULNERABILITY_INPROGRESS.query.filter_by(creation_date=creation_date).all()
        '''
        if vulnerabilityObjs:
        
            for vulnerabilityObj in vulnerabilityObjs:
                noPlanObj= VULNERABILITY_EDN_NO_PLAN()
                notFoundObj= VULNERABILITY_EDN_NOT_FOUND()
                try:
                    masterObj= VULNERABILITY_EDN_MASTER()
                    
                    if  vulnerabilityObj.scan_result_id:
                        masterObj.scan_result_id = vulnerabilityObj.scan_result_id
                    else: 
                        masterObj.scan_result_id= 'NE'
                        
                    if  vulnerabilityObj.device_ip:
                        masterObj.device_ip = vulnerabilityObj.device_ip
                    else: 
                        masterObj.device_ip= 'NE'
                    
                    if  vulnerabilityObj.device_name:
                        masterObj.device_name = vulnerabilityObj.device_name
                    else: 
                        masterObj.device_name= 'NE'
                    
                    if  vulnerabilityObj.severity:
                        masterObj.severity = vulnerabilityObj.severity
                    else: 
                        masterObj.severity= 'NE'

                    
                    if  vulnerabilityObj.due_date:
                        masterObj.due_date = vulnerabilityObj.due_date
                    #else: 
                    #    masterObj.scan_result_id= 'NE'
                    
                    if  vulnerabilityObj.last_detected:
                        masterObj.last_detected = vulnerabilityObj.last_detected
                    else: 
                        masterObj.last_detected= 'NE'
                    
                    if  vulnerabilityObj.overall_status:
                        masterObj.overall_status = vulnerabilityObj.overall_status
                    else: 
                        masterObj.overall_status= 'NE'
                    
                    if  vulnerabilityObj.qualys_vuln_status:
                        masterObj.qualys_vuln_status = vulnerabilityObj.qualys_vuln_status
                    else: 
                        masterObj.qualys_vuln_status= 'NE'

                    if  vulnerabilityObj.exception_requests:
                        masterObj.all_exceptions = vulnerabilityObj.exception_requests
                    else: 
                        masterObj.exception_requests= 'NE'
                    
                    if  vulnerabilityObj.cve_id:
                        masterObj.cve_id = vulnerabilityObj.cve_id
                    else: 
                        masterObj.cve_id= 'NE'
                    
                    if  vulnerabilityObj.technical_contact:
                        masterObj.technical_contact = vulnerabilityObj.technical_contact
                    else: 
                        masterObj.cvetechnical_contact_id= 'NE'


                    masterObj.creation_date= current_time
                    masterObj.modification_date= current_time
                    masterObj.created_by= "Sync"
                    masterObj.modified_by= "Sync"
                    
                    '''
                    cveId = VULNERABILITY_MANAGEDBY.query.with_entities(VULNERABILITY_MANAGEDBY.cve_id).filter_by(scan_result_id=vulnerabilityObj.scan_result_id).first()
                    if cveId:
                        if cveId[0]:
                            masterObj.cve_id= cveId[0]
                        else:
                            masterObj.cve_id= 'NE'

                    else:
                        masterObj.cve_id= 'NE'
                    '''
                    # inProgressExemptions = VULNERABILITY_INPROGRESS.query.with_entities(VULNERABILITY_INPROGRESS.exception_requests).filter_by(scan_result_id=vulnerabilityObj.scan_result_id).first()
                    # if inProgressExemptions:
                    #     if inProgressExemptions[0]:
                    #         masterObj.inprogress_exceptions= inProgressExemptions[0]
                    #     else:
                    #         masterObj.inprogress_exceptions= 'NE'

                    # else:
                    #     masterObj.inprogress_exceptions= 'NE'
                    
                    inProgressDevice = Device_Table.query.with_entities(Device_Table.pn_code, Device_Table.hw_eos_date, Device_Table.vuln_fix_plan_status, Device_Table.vuln_ops_severity).filter_by(device_id=vulnerabilityObj.device_name).first()
                    if inProgressDevice:
                        
                        if inProgressDevice[0]:
                            masterObj.pn_code= inProgressDevice[0]
                        else:
                            masterObj.pn_code= 'NE'
                        
                        if inProgressDevice[1]:
                            masterObj.hw_eos_date= inProgressDevice[1]
                        else:
                            pass
                            #masterObj.hw_eos_date= 'NE'
                        
                        if inProgressDevice[2]:
                            masterObj.vuln_fix_plan_status= inProgressDevice[2]
                        else:
                            masterObj.vuln_fix_plan_status= 'NE'

                        if inProgressDevice[3]:
                            masterObj.vuln_ops_severity= inProgressDevice[3]
                        else:
                            masterObj.vuln_ops_severity= 'NE'
                            
                    else:
                        masterObj.pn_code= 'NE'
                        #masterObj.hw_eos_date= 'NE'
                        masterObj.vuln_fix_plan_status= 'NE'
                        masterObj.vuln_ops_severity= 'NE'

                    InsertData(masterObj)

                   
                    if 'closed' not in masterObj.overall_status.lower() and masterObj.vuln_fix_plan_status=="No Plan":
                        isNoPlanExists = VULNERABILITY_EDN_NO_PLAN.query.with_entities(VULNERABILITY_EDN_NO_PLAN.device_ip).filter_by(device_ip=masterObj.device_ip).filter_by(creation_date=masterObj.creation_date).first()
                        if not isNoPlanExists:
                            noPlanObj.device_name= masterObj.device_name
                            noPlanObj.device_ip= masterObj.device_ip
                            noPlanObj.pn_code= masterObj.pn_code
                            noPlanObj.creation_date= masterObj.creation_date
                            noPlanObj.modification_date= masterObj.modification_date
                            noPlanObj.created_by= masterObj.created_by
                            noPlanObj.modified_by= masterObj.modified_by
                            InsertData(noPlanObj)
                            print("Inserted EDN Vulnerability No Plan Device", file=sys.stderr)

                    if 'closed' not in masterObj.overall_status.lower() and masterObj.pn_code=="NE":
                        isNotFoundExists = VULNERABILITY_EDN_NOT_FOUND.query.with_entities(VULNERABILITY_EDN_NOT_FOUND.device_ip).filter_by(device_ip=masterObj.device_ip).filter_by(creation_date=masterObj.creation_date).first()
                        if not isNotFoundExists:
                            ipamObj = EDN_IPAM_TABLE.query.with_entities(EDN_IPAM_TABLE.device_id).filter_by(ip_address=masterObj.device_ip).first()
                            if ipamObj:
                                notFoundObj.correct_device_id= ipamObj[0]
                            else:
                                notFoundObj.correct_device_id= "Not Found"

                            notFoundObj.device_name= masterObj.device_name
                            notFoundObj.device_ip= masterObj.device_ip
                            
                            notFoundObj.creation_date= masterObj.creation_date
                            notFoundObj.modification_date= masterObj.modification_date
                            notFoundObj.created_by= masterObj.created_by
                            notFoundObj.modified_by= masterObj.modified_by
                            InsertData(notFoundObj)
                            print("Inserted EDN Vulnerability Not Found Device", file=sys.stderr)
                            
                except Exception as e:
                        print(f"Error Occured in  Population of Master Table {e}", file=sys.stderr)
    vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "EDN-VULN-TO-MASTER").first()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        vulnStatus.script = "EDN-VULN-TO-MASTER"
        vulnStatus.status = "Completed"
        vulnStatus.creation_date= current_time
        vulnStatus.modification_date= current_time
        db.session.add(vulnStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)
    
    print("Finished Population of EDN Master", file=sys.stderr)

    return jsonify({'response': "success","code":"200"})


@app.route("/getAllEdnVulnerabilityMasterByDate", methods = ['POST'])
@token_required
def GetAllEdnVulnerabilityMasterByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityMasterObjList=[]
        #vulnerabilityMasterObjs = VULNERABILITY_EDN_MASTER.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityMasterObjs =  db.session.execute(f"SELECT * FROM vulnerability_edn_master WHERE creation_date = '{current_time}'")
        try:
            for vulnerabilityMasterObj in vulnerabilityMasterObjs:

                vulnerabilityMasterDataDict= {}
                vulnerabilityMasterDataDict['vulnerability_master_id']=vulnerabilityMasterObj[0]
                vulnerabilityMasterDataDict['scan_result_id'] = vulnerabilityMasterObj[1]
                vulnerabilityMasterDataDict['device_ip'] = vulnerabilityMasterObj[2]
                vulnerabilityMasterDataDict['device_name'] = vulnerabilityMasterObj[3]
                vulnerabilityMasterDataDict['severity'] = vulnerabilityMasterObj[4]
                vulnerabilityMasterDataDict['cve_id'] = vulnerabilityMasterObj[5]
                
                if vulnerabilityMasterObj[6]:
                    vulnerabilityMasterDataDict['due_date'] = FormatDate(vulnerabilityMasterObj[6])
                if vulnerabilityMasterObj[7]:
                    vulnerabilityMasterDataDict['last_detected'] =FormatDate( vulnerabilityMasterObj[7])
                
                vulnerabilityMasterDataDict['overall_status'] = vulnerabilityMasterObj[8]
                vulnerabilityMasterDataDict['qualys_vuln_status'] = vulnerabilityMasterObj[9]
                
                
                #vulnerabilityMasterDataDict['inprogress_exceptions'] = vulnerabilityMasterObj[10]
                vulnerabilityMasterDataDict['all_exceptions'] = vulnerabilityMasterObj[10]
                
                vulnerabilityMasterDataDict['pn_code'] = vulnerabilityMasterObj[11]
                
                if vulnerabilityMasterObj[12]:
                    vulnerabilityMasterDataDict['hw_eos_date'] = FormatDate(vulnerabilityMasterObj[12])
                
                vulnerabilityMasterDataDict['vuln_fix_plan_status'] = vulnerabilityMasterObj[13]          
                vulnerabilityMasterDataDict['vuln_ops_severity'] = vulnerabilityMasterObj[14]
                vulnerabilityMasterDataDict['technical_contact'] = vulnerabilityMasterObj[15]
                
                
                vulnerabilityMasterDataDict['creation_date'] = FormatDate(vulnerabilityMasterObj[16])
                vulnerabilityMasterDataDict['modification_date'] = FormatDate(vulnerabilityMasterObj[17])
                vulnerabilityMasterDataDict['created_by'] = vulnerabilityMasterObj[18]
                vulnerabilityMasterDataDict['modified_by'] = vulnerabilityMasterObj[19]
                
                vulnerabilityMasterObjList.append(vulnerabilityMasterDataDict)

            #print("%%%"+ vulnerabilityMasterObjList, file=sys.stderr)
            content = gzip.compress(json.dumps(vulnerabilityMasterObjList).encode('utf8'), 5)
            response = make_response(content)
            response.headers['Content-length'] = len(content)
            response.headers['Content-Encoding'] = 'gzip'
            return response
        except Exception as e:
            print(f"Error Occured in Getting Master Vulnerabilities {e}", file=sys.stderr)
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnVulnerabilityMaster", methods = ['GET'])
@token_required
def GetAllEdnVulnerabilityMaster(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityMasterObjList=[]
        
        vulnerabilityMasterObjs =  db.session.execute(f'SELECT * FROM vulnerability_edn_master WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_edn_master)')

        for vulnerabilityMasterObj in vulnerabilityMasterObjs:

            vulnerabilityMasterDataDict= {}
            vulnerabilityMasterDataDict['vulnerability_master_id']=vulnerabilityMasterObj[0]
            vulnerabilityMasterDataDict['scan_result_id'] = vulnerabilityMasterObj[1]
            vulnerabilityMasterDataDict['device_ip'] = vulnerabilityMasterObj[2]
            vulnerabilityMasterDataDict['device_name'] = vulnerabilityMasterObj[3]
            vulnerabilityMasterDataDict['severity'] = vulnerabilityMasterObj[4]
            vulnerabilityMasterDataDict['cve_id'] = vulnerabilityMasterObj[5]
            
            if vulnerabilityMasterObj[6]:
                vulnerabilityMasterDataDict['due_date'] = FormatDate(vulnerabilityMasterObj[6])
            if vulnerabilityMasterObj[7]:
                vulnerabilityMasterDataDict['last_detected'] =FormatDate( vulnerabilityMasterObj[7])
            
            vulnerabilityMasterDataDict['overall_status'] = vulnerabilityMasterObj[8]
            vulnerabilityMasterDataDict['qualys_vuln_status'] = vulnerabilityMasterObj[9]
            

            
            #vulnerabilityMasterDataDict['inprogress_exceptions'] = vulnerabilityMasterObj[10]
            vulnerabilityMasterDataDict['all_exceptions'] = vulnerabilityMasterObj[10]
            
            vulnerabilityMasterDataDict['pn_code'] = vulnerabilityMasterObj[11]
            
            if vulnerabilityMasterObj[12]:
                vulnerabilityMasterDataDict['hw_eos_date'] = FormatDate(vulnerabilityMasterObj[12])
            
            
            
            vulnerabilityMasterDataDict['vuln_fix_plan_status'] = vulnerabilityMasterObj[13]          
            vulnerabilityMasterDataDict['vuln_ops_severity'] = vulnerabilityMasterObj[14]
            vulnerabilityMasterDataDict['technical_contact'] = vulnerabilityMasterObj[15]
            
            
            vulnerabilityMasterDataDict['creation_date'] = FormatDate(vulnerabilityMasterObj[16])
            vulnerabilityMasterDataDict['modification_date'] = FormatDate(vulnerabilityMasterObj[17])
            vulnerabilityMasterDataDict['created_by'] = vulnerabilityMasterObj[18]
            vulnerabilityMasterDataDict['modified_by'] = vulnerabilityMasterObj[19]
            
            
            vulnerabilityMasterObjList.append(vulnerabilityMasterDataDict)

        content = gzip.compress(json.dumps(vulnerabilityMasterObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnVulnerabilityMasterDates",methods=['GET'])
@token_required
def GetAllEdnVulnerabilityMasterDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_edn_master  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/editEdnVulnerabilityMaster", methods = ['POST'])
@token_required
def EditEdnVulnerabilityMaster(user_data):  
    try:
        vulnerabilityMasterObj = request.get_json()
        time= datetime.now(tz)
        vulnerabilityMaster = VULNERABILITY_EDN_MASTER.query.with_entities(VULNERABILITY_EDN_MASTER).filter_by(vulnerability_master_id=vulnerabilityMasterObj['vulnerability_master_id']).first()
        if vulnerabilityMaster:
            if 'pn_code' in vulnerabilityMasterObj:
                if vulnerabilityMasterObj['pn_code']:
                    vulnerabilityMaster.pn_code = vulnerabilityMasterObj['pn_code']

            if 'hw_eos_date' in vulnerabilityMasterObj:
                vulnerabilityMaster.hw_eos_date = FormatStringDate(vulnerabilityMasterObj['hw_eos_date'])

            if 'vuln_fix_plan_status' in vulnerabilityMasterObj:
                if vulnerabilityMasterObj['vuln_fix_plan_status']:
                    vulnerabilityMaster.vuln_fix_plan_status = vulnerabilityMasterObj['vuln_fix_plan_status']

            if 'vuln_ops_severity' in vulnerabilityMasterObj:
                if vulnerabilityMasterObj['vuln_ops_severity']:
                    vulnerabilityMaster.vuln_ops_severity = vulnerabilityMasterObj['vuln_ops_severity']

            vulnerabilityMaster.modification_date= time
            vulnerabilityMaster.modified_by= user_data['user_id']
        
            
            UpdateData(vulnerabilityMaster)
            return jsonify({'response': "success","code":"200"})

        else:
            print("NO MATCH", file = sys.stderr)
            return jsonify({'response': "Vulnerability Id can not be found in Table"}), 500

    except Exception as e:
        traceback.print_exc()
        print(f"Error Occured in Adding Vulnerability Master {e.args}", file=sys.stderr)
        return str(e),500

@app.route("/syncEdnVulnerabilityMasterToDevices", methods = ['GET'])
@token_required
def syncEdnVulnerabilityMasterToDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        try:
            syncEdnVulnerabilityMasterToDevicesFunc(user_data)
        
        except Exception as e:
            print(f"Error Occured in  Population of Devices {e}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401        

def syncEdnVulnerabilityMasterToDevicesFunc(user_data):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "EDN-VULN-TO-DEVICES").first()
    try:
        vulnStatus.script = "EDN-VULN-TO-DEVICES"
        vulnStatus.status = "Running"
        vulnStatus.creation_date= current_time
        vulnStatus.modification_date= current_time
        db.session.add(vulnStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)
    
    try:
        tableObjs=[]
        date=""
        masterDateObj = db.session.execute('SELECT max(creation_date) FROM vulnerability_edn_master')
        for row in masterDateObj:
            date=row[0]

        for table in range(2):

            if table==0:
                print("Populating EDN-NET Vulnerabilities in Seed", file=sys.stderr)
                tableObjs = Seed.query.filter(or_(Seed.cisco_domain=='EDN-NET', Seed.cisco_domain=='EDN-IPT')).all()
            if table==1:
                print("Populating EDN-NET Vulnerabilities in Devices", file=sys.stderr)
                tableObjs = Device_Table.query.filter(or_(Device_Table.cisco_domain=='EDN-NET', Device_Table.cisco_domain=='EDN-IPT')).all()
            
            for obj in tableObjs:
                try:
                    deviceId = obj.device_id
                    severityObjs= VULNERABILITY_EDN_MASTER.query.with_entities(VULNERABILITY_EDN_MASTER.severity).filter_by(device_name=deviceId).filter_by(creation_date=date).filter(VULNERABILITY_EDN_MASTER.overall_status.notlike('Closed%')).all()
                    if severityObjs:
                        uniqueSeverity= set()
                        for master in severityObjs:
                            uniqueSeverity.add(master[0])
                        vulnSeverity=""
                        for severity in uniqueSeverity:
                            if severity.lower()=="medium":
                                vulnSeverity+="SL3,"
                            if severity.lower()=="high":
                                vulnSeverity+="SL4,"
                            if severity.lower()=="critical":
                                vulnSeverity+="SL5," 
                        vulnSeverity= vulnSeverity[:-1]
                        obj.vulnerability_severity= vulnSeverity
                        UpdateData(obj)
                        print(f"Updated Vuln Severity for Device {obj.device_id} {vulnSeverity}", file=sys.stderr)
                    else:
                        obj.vulnerability_severity= ""
                        UpdateData(obj)
                        print(f"Reset Vuln Severity for Device {obj.device_id}", file=sys.stderr)

                except Exception  as e:
                    print(f"Exception Occured in Syncing Vulnerabilities {e}")
        
        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "EDN-VULN-TO-DEVICES").first()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            vulnStatus.script = "EDN-VULN-TO-DEVICES"
            vulnStatus.status = "Completed"
            vulnStatus.creation_date= current_time
            vulnStatus.modification_date= current_time
            db.session.add(vulnStatus)
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"Error while updating script status {e}", file=sys.stderr)

        print("Finished EDN Vulnerability Sync To Device ", file=sys.stderr)
    except Exception  as e:
        print(f"Exception Occured in Syncing Vulnerabilities {e}") 

@app.route("/getednVulnerabilitySyncTOMasterStatus", methods = ['GET'])
@token_required
def GetednVulnerabilitySyncTOMasterStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        f5={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "EDN-VULN-TO-MASTER").first()
        if vulnStatus:
            script_status= vulnStatus.status
            script_modifiation_date= str(vulnStatus.modification_date)
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


@app.route("/getednVulnerabilitySyncToDevicesStatus", methods = ['GET'])
#@token_required
def GetednVulnerabilitySyncTODevicesStatus():
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        f5={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "EDN-VULN-TO-DEVICES").first()
        if vulnStatus:
            script_status= vulnStatus.status
            script_modifiation_date= str(vulnStatus.modification_date)
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


@app.route("/getednVulnerabilityImportStatus", methods = ['GET'])
@token_required
def GetednVulnerabilityImportStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        f5={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "EDN-VULN-ARCHER").first()
        if vulnStatus:
            script_status= vulnStatus.status
            script_modifiation_date= str(vulnStatus.modification_date)
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


### No Plan

@app.route("/getAllEdnVulnerabilityNoPlan", methods = ['GET'])
@token_required
def GetAllEdnVulnerabilityNoPlan(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityNoPlanObjList=[]
        
        vulnerabilityNoPlanObjs =  db.session.execute(f'SELECT * FROM vulnerability_edn_no_plan WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_edn_no_plan)')

        for vulnerabilityNoPlanObj in vulnerabilityNoPlanObjs:

            vulnerabilityNoPlanDataDict= {}
            vulnerabilityNoPlanDataDict['vulnerability_no_plan_id']=vulnerabilityNoPlanObj[0]
            vulnerabilityNoPlanDataDict['device_ip'] = vulnerabilityNoPlanObj[1]
            vulnerabilityNoPlanDataDict['device_name'] = vulnerabilityNoPlanObj[2]
            vulnerabilityNoPlanDataDict['pn_code'] = vulnerabilityNoPlanObj[3]
             
            vulnerabilityNoPlanDataDict['creation_date'] = FormatDate(vulnerabilityNoPlanObj[4])
            vulnerabilityNoPlanDataDict['modification_date'] = FormatDate(vulnerabilityNoPlanObj[5])
            vulnerabilityNoPlanDataDict['created_by'] = vulnerabilityNoPlanObj[6]
            vulnerabilityNoPlanDataDict['modified_by'] = vulnerabilityNoPlanObj[7]
            
            
            vulnerabilityNoPlanObjList.append(vulnerabilityNoPlanDataDict)

        content = gzip.compress(json.dumps(vulnerabilityNoPlanObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnVulnerabilityNoPlanDates",methods=['GET'])
@token_required
def GetAllEdnVulnerabilityNoPlanDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_edn_no_plan  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllEdnVulnerabilityNoPlanByDate", methods = ['POST'])
@token_required
def GetAllEdnVulnerabilityNoPlanByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityNoPlanObjList=[]
        #vulnerabilityNoPlanObjs = VULNERABILITY_EDN_MASTER.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityNoPlanObjs =  db.session.execute(f"SELECT * FROM vulnerability_edn_no_plan WHERE creation_date = '{current_time}'")
        try:
            for vulnerabilityNoPlanObj in vulnerabilityNoPlanObjs:

                vulnerabilityNoPlanDataDict= {}
                vulnerabilityNoPlanDataDict['vulnerability_no_plan_id']=vulnerabilityNoPlanObj[0]
                vulnerabilityNoPlanDataDict['device_ip'] = vulnerabilityNoPlanObj[1]
                vulnerabilityNoPlanDataDict['device_name'] = vulnerabilityNoPlanObj[2]
                vulnerabilityNoPlanDataDict['pn_code'] = vulnerabilityNoPlanObj[3]
                
                vulnerabilityNoPlanDataDict['creation_date'] = FormatDate(vulnerabilityNoPlanObj[4])
                vulnerabilityNoPlanDataDict['modification_date'] = FormatDate(vulnerabilityNoPlanObj[5])
                vulnerabilityNoPlanDataDict['created_by'] = vulnerabilityNoPlanObj[6]
                vulnerabilityNoPlanDataDict['modified_by'] = vulnerabilityNoPlanObj[7]
                
                vulnerabilityNoPlanObjList.append(vulnerabilityNoPlanDataDict)

            #print("%%%"+ vulnerabilityNoPlanObjList, file=sys.stderr)
            content = gzip.compress(json.dumps(vulnerabilityNoPlanObjList).encode('utf8'), 5)
            response = make_response(content)
            response.headers['Content-length'] = len(content)
            response.headers['Content-Encoding'] = 'gzip'
            return response
        except Exception as e:
            print(f"Error Occured in Getting NoPlan Vulnerabilities {e}", file=sys.stderr)
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

#### Not Found

@app.route("/getAllEdnVulnerabilityNotFound", methods = ['GET'])
@token_required
def GetAllEdnVulnerabilityNotFound(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityNotFoundObjList=[]
        
        vulnerabilityNotFoundObjs =  db.session.execute(f'SELECT * FROM vulnerability_edn_not_found WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_edn_not_found)')

        for vulnerabilityNotFoundObj in vulnerabilityNotFoundObjs:

            vulnerabilityNotFoundDataDict= {}
            vulnerabilityNotFoundDataDict['vulnerability_not_found_id']=vulnerabilityNotFoundObj[0]
            vulnerabilityNotFoundDataDict['device_ip'] = vulnerabilityNotFoundObj[1]
            vulnerabilityNotFoundDataDict['device_name'] = vulnerabilityNotFoundObj[2]
            vulnerabilityNotFoundDataDict['correct_device_id'] = vulnerabilityNotFoundObj[3]
             
            vulnerabilityNotFoundDataDict['creation_date'] = FormatDate(vulnerabilityNotFoundObj[4])
            vulnerabilityNotFoundDataDict['modification_date'] = FormatDate(vulnerabilityNotFoundObj[5])
            vulnerabilityNotFoundDataDict['created_by'] = vulnerabilityNotFoundObj[6]
            vulnerabilityNotFoundDataDict['modified_by'] = vulnerabilityNotFoundObj[7]
            
            
            vulnerabilityNotFoundObjList.append(vulnerabilityNotFoundDataDict)

        content = gzip.compress(json.dumps(vulnerabilityNotFoundObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnVulnerabilityNotFoundDates",methods=['GET'])
@token_required
def GetAllEdnVulnerabilityNotFoundDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_edn_not_found  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllEdnVulnerabilityNotFoundByDate", methods = ['POST'])
@token_required
def GetAllEdnVulnerabilityNotFoundByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityNotFoundObjList=[]
        #vulnerabilityNotFoundObjs = VULNERABILITY_EDN_MASTER.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityNotFoundObjs =  db.session.execute(f"SELECT * FROM vulnerability_edn_not_found WHERE creation_date = '{current_time}'")
        try:
            for vulnerabilityNotFoundObj in vulnerabilityNotFoundObjs:

                vulnerabilityNotFoundDataDict= {}
                vulnerabilityNotFoundDataDict['vulnerability_not_found_id']=vulnerabilityNotFoundObj[0]
                vulnerabilityNotFoundDataDict['device_ip'] = vulnerabilityNotFoundObj[1]
                vulnerabilityNotFoundDataDict['device_name'] = vulnerabilityNotFoundObj[2]
                vulnerabilityNotFoundDataDict['correct_device_id'] = vulnerabilityNotFoundObj[3]
            
                vulnerabilityNotFoundDataDict['creation_date'] = FormatDate(vulnerabilityNotFoundObj[4])
                vulnerabilityNotFoundDataDict['modification_date'] = FormatDate(vulnerabilityNotFoundObj[5])
                vulnerabilityNotFoundDataDict['created_by'] = vulnerabilityNotFoundObj[6]
                vulnerabilityNotFoundDataDict['modified_by'] = vulnerabilityNotFoundObj[7]
                
                vulnerabilityNotFoundObjList.append(vulnerabilityNotFoundDataDict)

            #print("%%%"+ vulnerabilityNotFoundObjList, file=sys.stderr)
            content = gzip.compress(json.dumps(vulnerabilityNotFoundObjList).encode('utf8'), 5)
            response = make_response(content)
            response.headers['Content-length'] = len(content)
            response.headers['Content-Encoding'] = 'gzip'
            return response
        except Exception as e:
            print(f"Error Occured in Getting NotFound Vulnerabilities {e}", file=sys.stderr)
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getEdnVulnerabilityTechnicalContact", methods = ['GET'])
@token_required
def GetEdnVulnerabilityTechnicalContact(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnList=[]
        vulnList= GetEdnVulnerabilityTechnicalContactFunc()
        content = gzip.compress(json.dumps(vulnList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def GetEdnVulnerabilityTechnicalContactFunc():
    vulnList=[]
    vulnList.append('All')
    try:
        vulnObj =  db.session.execute(f'SELECT distinct(technical_contact) FROM vulnerability_edn_master WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_edn_master)')

        for vuln in vulnObj:
            if vuln[0] is not None:
                vulnList.append(vuln[0])

        return vulnList
    except Exception as e:
        return vulnList
        print("Error in getting distinct Technical Contact")


@app.route("/getEdnVulnerabilityOverallStatus", methods = ['GET'])
@token_required
def GetEdnVulnerabilityOverallStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnList=[]
        
        vulnList= GetEdnVulnerabilityOverallStatusFunc()
        content = gzip.compress(json.dumps(vulnList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
        
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def GetEdnVulnerabilityOverallStatusFunc():
    vulnList=[]
    vulnList.append('All')
    try:
        vulnObj =  db.session.execute(f"SELECT distinct(overall_status) FROM vulnerability_edn_master WHERE OVERALL_STATUS NOT LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_edn_master)")

        for vuln in vulnObj:
            if vuln[0] is not None:
                vulnList.append(vuln[0])
        return vulnList
    except Exception as e:
            return vulnList
            print("Error in getting distinct Technical Contact")




###################################### IGW Vulnerability ################################################################


def FormatStringDate(date):
    #print(date, file=sys.stderr)
    try:
        if date is not None:
            if '-' in date:
                result = datetime.strptime(date,'%m-%d-%Y')
            elif '/' in date:
                result = datetime.strptime(date,'%m/%d/%Y')
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
    try:
        #print(f"Data is : {obj.creation_date}", file=sys.stderr)
        #add data to db
        #obj.creation_date= datetime.now(tz)
        #obj.modification_date= datetime.now(tz)
        db.session.add(obj)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Exception in Inserting data {e}", file=sys.stderr)
        db.session.flush()
        db.session.rollback()
        

def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%m-%d-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

def UpdateData(obj):
    #add data to db
    try:
        #obj.modification_date= datetime.now(tz)
        db.session.merge(obj)
        db.session.commit()
        #print(obj.site_name, file=sys.stderr)
    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong {e}", file=sys.stderr)
    
    return True


###
#Vulnerabilities Archer
###

@app.route("/getAllIgwVulnerabilityArcherDates",methods=['GET'])
@token_required
def GetAllIgwVulnerabilityArcherDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_igw_archer  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/addIgwVulnerabilityArcher", methods = ['POST'])
@token_required
def AddIgwVulnerabilityArcher(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()
        time= datetime.now(tz)
        print(postData,file=sys.stderr)

        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "IGW-VULN-ARCHER").first()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            vulnStatus.script = "IGW-VULN-ARCHER"
            vulnStatus.status = "Running"
            vulnStatus.creation_date= current_time
            vulnStatus.modification_date= current_time
            db.session.add(vulnStatus)
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"Error while updating script status {e}", file=sys.stderr)


        for vulnerabilityArcherObj in postData:
            try:
                vulnerabilityArcher = VULNERABILITY_IGW_ARCHER()
                if 'scan_result_id' in vulnerabilityArcherObj:
                    vulnerabilityArcher.scan_result_id = vulnerabilityArcherObj['scan_result_id']
                else:
                    print(f"Error Occured in Adding Vulnerability Archer Scan Result Id Not Found.", file=sys.stderr)
                    continue

                if 'device_ip' in vulnerabilityArcherObj:
                    vulnerabilityArcher.device_ip = vulnerabilityArcherObj['device_ip']
                else:
                    vulnerabilityArcher.device_ip = ''

                if 'device_name' in vulnerabilityArcherObj:
                    vulnerabilityArcher.device_name = vulnerabilityArcherObj['device_name']
                else:
                    vulnerabilityArcher.device_name = ''

                if 'title' in vulnerabilityArcherObj:
                    vulnerabilityArcher.title = vulnerabilityArcherObj['title']
                else:
                    vulnerabilityArcher.title = ''

                if 'due_date' in vulnerabilityArcherObj:
                    if vulnerabilityArcherObj['due_date']:
                        vulnerabilityArcher.due_date = FormatStringDate(vulnerabilityArcherObj['due_date'])
                #else:
                #    vulnerabilityArcher.due_date = ''

                if 'false_positive_date' in vulnerabilityArcherObj:
                    if vulnerabilityArcherObj['false_positive_date']:
                        vulnerabilityArcher.false_positive_date = FormatStringDate(vulnerabilityArcherObj['false_positive_date'])
                #else:
                #    vulnerabilityArcher.false_positive_date = ''

                if 'severity' in vulnerabilityArcherObj:
                    vulnerabilityArcher.severity = vulnerabilityArcherObj['severity']
                else:
                    vulnerabilityArcher.severity = ''

                if 'overall_status' in vulnerabilityArcherObj:
                    vulnerabilityArcher.overall_status = vulnerabilityArcherObj['overall_status']
                else:
                    vulnerabilityArcher.overall_status = ''

                if 'qualys_vuln_status' in vulnerabilityArcherObj:

                    vulnerabilityArcher.qualys_vuln_status =  vulnerabilityArcherObj['qualys_vuln_status']
                else:
                    vulnerabilityArcher.qualys_vuln_status = ''

                if 'last_detected' in vulnerabilityArcherObj:
                    if vulnerabilityArcherObj['last_detected']:
                        vulnerabilityArcher.last_detected = FormatStringDate(vulnerabilityArcherObj['last_detected'])
                #else:
                #    vulnerabilityArcher.last_detected = ''
                    
                if 'technical_contact' in vulnerabilityArcherObj:
                    vulnerabilityArcher.technical_contact = vulnerabilityArcherObj['technical_contact']
                else:
                    vulnerabilityArcher.technical_contact = ''

                if 'exception_requests' in vulnerabilityArcherObj:
                    vulnerabilityArcher.exception_requests = vulnerabilityArcherObj['exception_requests']
                else:
                    vulnerabilityArcher.exception_requests = ''
                
                if 'cve_id' in vulnerabilityArcherObj:
                    vulnerabilityArcher.cve_id = vulnerabilityArcherObj['cve_id']
                else:
                    vulnerabilityArcher.cve_id = ''

                vulnerabilityArcher.creation_date= time
                vulnerabilityArcher.modification_date= time
                vulnerabilityArcher.created_by= user_data['user_id']
                vulnerabilityArcher.modified_by=  user_data['user_id']
            
                
                InsertData(vulnerabilityArcher)
            except Exception as e:
                traceback.print_exc()
                print(f"Error Occured in Adding Vulnerability Archer {vulnerabilityArcherObj['scan_result_id']}", file=sys.stderr)

        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "IGW-VULN-ARCHER").first()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            vulnStatus.script = "IGW-VULN-ARCHER"
            vulnStatus.status = "Completed"
            vulnStatus.creation_date= current_time
            vulnStatus.modification_date= current_time
            db.session.add(vulnStatus)
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"Error while updating script status {e}", file=sys.stderr)
            

        try:
            print(f"Running Automatic Sync of IGW Vulnerability to Master", file=sys.stderr)
            syncIgwVulnerabilityMasterFunc(user_data)

        except Exception as e:
            print(f"Exception Occured in Automatic Sync of IGW Vulnerability to Master {e}", file=sys.stderr)

        try:
            print(f"Running Automatic Sync of IGW Vulnerability to Devices", file=sys.stderr)
            syncIgwVulnerabilityMasterToDevicesFunc(user_data)

        except Exception as e:
           print(f"Exception Occured in Automatic Sync of IGW Vulnerability to Devices {e}", file=sys.stderr)


        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editIgwVulnerabilityArcher", methods = ['POST'])
@token_required
def EditIgwVulnerabilityArcher(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityArcherObj = request.get_json()
        time= datetime.now(tz)
        print(vulnerabilityArcherObj,file=sys.stderr)

        #for vulnerabilityArcherObj in postData:
        try:
            vulnerabilityArcher = VULNERABILITY_IGW_ARCHER()
            if 'scan_result_id' in vulnerabilityArcherObj and 'vulnerability_archer_id' in vulnerabilityArcherObj:
                vulnerabilityArcherId = VULNERABILITY_IGW_ARCHER.query.with_entities(VULNERABILITY_IGW_ARCHER.vulnerability_archer_id).filter_by(vulnerability_archer_id=vulnerabilityArcherObj['vulnerability_archer_id']).first()
                if vulnerabilityArcherId is not None:
                    vulnerabilityArcher.vulnerability_archer_id= vulnerabilityArcherId[0]
                    if 'device_ip' in vulnerabilityArcherObj:
                        vulnerabilityArcher.device_ip = vulnerabilityArcherObj['device_ip']
                    else:
                        vulnerabilityArcher.device_ip = ''

                    if 'device_name' in vulnerabilityArcherObj:
                        vulnerabilityArcher.device_name = vulnerabilityArcherObj['device_name']
                    else:
                        vulnerabilityArcher.device_name = ''

                    if 'title' in vulnerabilityArcherObj:
                        vulnerabilityArcher.title = vulnerabilityArcherObj['title']
                    else:
                        vulnerabilityArcher.title = ''

                        
                    if 'due_date' in vulnerabilityArcherObj:
                        if vulnerabilityArcherObj['due_date']:
                            vulnerabilityArcher.due_date = FormatStringDate(vulnerabilityArcherObj['due_date'])
                    #else:
                    #    vulnerabilityArcher.due_date = ''

                    if 'false_positive_date' in vulnerabilityArcherObj:
                        if vulnerabilityArcherObj['false_positive_date']:
                            vulnerabilityArcher.false_positive_date = FormatStringDate(vulnerabilityArcherObj['false_positive_date'])
                    #else:
                    #    vulnerabilityArcher.false_positive_date = ''

                    if 'severity' in vulnerabilityArcherObj:
                        vulnerabilityArcher.severity = vulnerabilityArcherObj['severity']
                    else:
                        vulnerabilityArcher.severity = ''

                    if 'overall_status' in vulnerabilityArcherObj:
                        vulnerabilityArcher.overall_status = vulnerabilityArcherObj['overall_status']
                    else:
                        vulnerabilityArcher.overall_status = ''

                    if 'qualys_vuln_status' in vulnerabilityArcherObj:

                        vulnerabilityArcher.qualys_vuln_status =  vulnerabilityArcherObj['qualys_vuln_status']
                    else:
                        vulnerabilityArcher.qualys_vuln_status = ''

                    if 'last_detected' in vulnerabilityArcherObj:
                        if vulnerabilityArcherObj['last_detected']:
                            vulnerabilityArcher.last_detected = FormatStringDate(vulnerabilityArcherObj['last_detected'])
                    #else:
                    #    vulnerabilityArcher.last_detected = ''
                            
                    if 'technical_contact' in vulnerabilityArcherObj:
                        vulnerabilityArcher.technical_contact = vulnerabilityArcherObj['technical_contact']
                    else:
                        vulnerabilityArcher.technical_contact = ''

                    if 'exception_requests' in vulnerabilityArcherObj:
                        vulnerabilityArcher.exception_requests = vulnerabilityArcherObj['exception_requests']
                    else:
                        vulnerabilityArcher.exception_requests = ''
                    
                    if 'cve_id' in vulnerabilityArcherObj:
                        vulnerabilityArcher.cve_id = vulnerabilityArcherObj['cve_id']
                    else:
                        vulnerabilityArcher.cve_id = ''

                    #vulnerabilityArcher.creation_date= time
                    vulnerabilityArcher.modification_date= time
                    vulnerabilityArcher.modified_by=  user_data['user_id']
                    
                    UpdateData(vulnerabilityArcher)
                else:
                    return jsonify({'response': "Vulnerability Id can not be found in Table"}), 500  
            return jsonify({'response': "Vulnerability Id Missing"}), 500  
        except Exception as e:
            traceback.print_exc()
            print(f"Error Occured in Adding Vulnerability Archer {vulnerabilityArcherObj['scan_result_id']}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllIgwVulnerabilityArcherByDate", methods = ['POST'])
@token_required
def GetAllIgwVulnerabilityArcherByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityArcherObjList=[]
        #vulnerabilityArcherObjs = VULNERABILITY_IGW_ARCHER.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityArcherObjs =  db.session.execute(f"SELECT * FROM vulnerability_igw_archer WHERE creation_date = '{current_time}'")

        for vulnerabilityArcherObj in vulnerabilityArcherObjs:

            vulnerabilityArcherDataDict= {}
            vulnerabilityArcherDataDict['vulnerability_archer_id']=vulnerabilityArcherObj[0]
            vulnerabilityArcherDataDict['scan_result_id'] = vulnerabilityArcherObj[1]
            vulnerabilityArcherDataDict['device_ip'] = vulnerabilityArcherObj[2]
            vulnerabilityArcherDataDict['device_name'] = vulnerabilityArcherObj[3]
            vulnerabilityArcherDataDict['title'] = vulnerabilityArcherObj[4]
            if vulnerabilityArcherObj[5]:
                vulnerabilityArcherDataDict['due_date'] = FormatDate(vulnerabilityArcherObj[5])
            if vulnerabilityArcherObj[6]:
                vulnerabilityArcherDataDict['false_positive_date'] =FormatDate( vulnerabilityArcherObj[6])
            vulnerabilityArcherDataDict['severity'] = vulnerabilityArcherObj[7]
            vulnerabilityArcherDataDict['overall_status'] = vulnerabilityArcherObj[8]
            vulnerabilityArcherDataDict['qualys_vuln_status'] = vulnerabilityArcherObj[9]
            if vulnerabilityArcherObj[10]:
                vulnerabilityArcherDataDict['last_detected'] = FormatDate(vulnerabilityArcherObj[10])
            vulnerabilityArcherDataDict['technical_contact'] = vulnerabilityArcherObj[11]
            vulnerabilityArcherDataDict['exception_requests'] = vulnerabilityArcherObj[12]
            vulnerabilityArcherDataDict['cve_id'] = vulnerabilityArcherObj[13]
            vulnerabilityArcherDataDict['creation_date'] = FormatDate(vulnerabilityArcherObj[14])
            vulnerabilityArcherDataDict['modification_date'] = FormatDate(vulnerabilityArcherObj[15])
            vulnerabilityArcherDataDict['created_by'] = vulnerabilityArcherObj[16]
            vulnerabilityArcherDataDict['modified_by'] = vulnerabilityArcherObj[17]
            vulnerabilityArcherObjList.append(vulnerabilityArcherDataDict)

       
        content = gzip.compress(json.dumps(vulnerabilityArcherObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllIgwVulnerabilityArcher", methods = ['GET'])
@token_required
def GetAllIgwVulnerabilityArcher(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityArcherObjList=[]
        
        vulnerabilityArcherObjs =  db.session.execute(f'SELECT * FROM vulnerability_igw_archer WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_igw_archer)')

        for vulnerabilityArcherObj in vulnerabilityArcherObjs:

            vulnerabilityArcherDataDict= {}
            vulnerabilityArcherDataDict['vulnerability_archer_id']=vulnerabilityArcherObj[0]
            vulnerabilityArcherDataDict['scan_result_id'] = vulnerabilityArcherObj[1]
            vulnerabilityArcherDataDict['device_ip'] = vulnerabilityArcherObj[2]
            vulnerabilityArcherDataDict['device_name'] = vulnerabilityArcherObj[3]
            vulnerabilityArcherDataDict['title'] = vulnerabilityArcherObj[4]
            if vulnerabilityArcherObj[5]:
                vulnerabilityArcherDataDict['due_date'] = FormatDate(vulnerabilityArcherObj[5])
            if vulnerabilityArcherObj[6]:
                vulnerabilityArcherDataDict['false_positive_date'] =FormatDate( vulnerabilityArcherObj[6])
            vulnerabilityArcherDataDict['severity'] = vulnerabilityArcherObj[7]
            vulnerabilityArcherDataDict['overall_status'] = vulnerabilityArcherObj[8]
            vulnerabilityArcherDataDict['qualys_vuln_status'] = vulnerabilityArcherObj[9]
            if vulnerabilityArcherObj[10]:
                vulnerabilityArcherDataDict['last_detected'] = FormatDate(vulnerabilityArcherObj[10])
            vulnerabilityArcherDataDict['technical_contact'] = vulnerabilityArcherObj[11]
            vulnerabilityArcherDataDict['exception_requests'] = vulnerabilityArcherObj[12]
            vulnerabilityArcherDataDict['cve_id'] = vulnerabilityArcherObj[13]
            vulnerabilityArcherDataDict['creation_date'] = FormatDate(vulnerabilityArcherObj[14])
            vulnerabilityArcherDataDict['modification_date'] = FormatDate(vulnerabilityArcherObj[15])
            vulnerabilityArcherDataDict['created_by'] = vulnerabilityArcherObj[16]
            vulnerabilityArcherDataDict['modified_by'] = vulnerabilityArcherObj[17]
            vulnerabilityArcherObjList.append(vulnerabilityArcherDataDict)

        content = gzip.compress(json.dumps(vulnerabilityArcherObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteIgwVulnerabilityArcher",methods = ['POST'])
@token_required
def DeleteIgwVulnerabilityArcher(user_data):
    if True:#session.get('token', None):
        vulnerabilityArcherObj = request.get_json()
        #vulnerabilityArcherObj= vulnerabilityArcherObj.get("ips")
        #vulnerabilityArcherObj = [9,10,11,12,13]
        print(vulnerabilityArcherObj,file = sys.stderr)
        
        for obj in vulnerabilityArcherObj.get("ips"):
            vulnerabilityArcherId = VULNERABILITY_IGW_ARCHER.query.filter(VULNERABILITY_IGW_ARCHER.vulnerability_archer_id==obj).first()
            print(vulnerabilityArcherId,file=sys.stderr)
            if obj:
                db.session.delete(vulnerabilityArcherId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
       
#### IGW MASTER Vulnerbility ROUTES   ###
@app.route("/syncIgwVulnerabilityMaster", methods = ['GET'])
@token_required
def syncIgwVulnerabilityMaster(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        try:
            syncIgwVulnerabilityMasterFunc(user_data)
        except Exception as e:
            print(f"Error Occured in  Population of Master Table {e}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def syncIgwVulnerabilityMasterFunc(user_data):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "IGW-VULN-TO-MASTER").first()
    try:
        vulnStatus.script = "IGW-VULN-TO-MASTER"
        vulnStatus.status = "Running"
        vulnStatus.creation_date= current_time
        vulnStatus.modification_date= current_time
        db.session.add(vulnStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    for table in range(1):
        
        if table==0:
            print("Populating Archer Vulnerabilities in Master", file=sys.stderr)
            creation_date=""
            creationObj = db.session.execute('SELECT max(creation_date) FROM vulnerability_igw_archer')
            for row in creationObj:
                creation_date=row[0]
            vulnerabilityObjs = VULNERABILITY_IGW_ARCHER.query.filter_by(creation_date=creation_date).all()
        

        if vulnerabilityObjs:
        
            for vulnerabilityObj in vulnerabilityObjs:
                noPlanObj= VULNERABILITY_IGW_NO_PLAN()
                notFoundObj= VULNERABILITY_IGW_NOT_FOUND()
                try:
                    masterObj= VULNERABILITY_IGW_MASTER()
                    
                    if  vulnerabilityObj.scan_result_id:
                        masterObj.scan_result_id = vulnerabilityObj.scan_result_id
                    else: 
                        masterObj.scan_result_id= 'NE'
                        
                    if  vulnerabilityObj.device_ip:
                        masterObj.device_ip = vulnerabilityObj.device_ip
                    else: 
                        masterObj.device_ip= 'NE'
                    
                    if  vulnerabilityObj.device_name:
                        masterObj.device_name = vulnerabilityObj.device_name
                    else: 
                        masterObj.device_name= 'NE'
                    
                    if  vulnerabilityObj.severity:
                        masterObj.severity = vulnerabilityObj.severity
                    else: 
                        masterObj.severity= 'NE'

                    
                    if  vulnerabilityObj.due_date:
                        masterObj.due_date = vulnerabilityObj.due_date
                    #else: 
                    #    masterObj.scan_result_id= 'NE'
                    
                    if  vulnerabilityObj.last_detected:
                        masterObj.last_detected = vulnerabilityObj.last_detected
                    else: 
                        masterObj.last_detected= 'NE'
                    
                    if  vulnerabilityObj.overall_status:
                        masterObj.overall_status = vulnerabilityObj.overall_status
                    else: 
                        masterObj.overall_status= 'NE'
                    
                    if  vulnerabilityObj.qualys_vuln_status:
                        masterObj.qualys_vuln_status = vulnerabilityObj.qualys_vuln_status
                    else: 
                        masterObj.qualys_vuln_status= 'NE'

                    if  vulnerabilityObj.exception_requests:
                        masterObj.all_exceptions = vulnerabilityObj.exception_requests
                    else: 
                        masterObj.exception_requests= 'NE'
                    
                    if  vulnerabilityObj.cve_id:
                        masterObj.cve_id = vulnerabilityObj.cve_id
                    else: 
                        masterObj.cve_id= 'NE'
                    
                    if  vulnerabilityObj.technical_contact:
                        masterObj.technical_contact = vulnerabilityObj.technical_contact
                    else: 
                        masterObj.cvetechnical_contact_id= 'NE'


                    masterObj.creation_date= current_time
                    masterObj.modification_date= current_time
                    masterObj.created_by= "Sync"
                    masterObj.modified_by= "Sync"
                    
                    '''
                    cveId = VULNERABILITY_MANAGEDBY.query.with_entities(VULNERABILITY_MANAGEDBY.cve_id).filter_by(scan_result_id=vulnerabilityObj.scan_result_id).first()
                    if cveId:
                        if cveId[0]:
                            masterObj.cve_id= cveId[0]
                        else:
                            masterObj.cve_id= 'NE'

                    else:
                        masterObj.cve_id= 'NE'
                    '''
                    # inProgressExemptions = VULNERABILITY_INPROGRESS.query.with_entities(VULNERABILITY_INPROGRESS.exception_requests).filter_by(scan_result_id=vulnerabilityObj.scan_result_id).first()
                    # if inProgressExemptions:
                    #     if inProgressExemptions[0]:
                    #         masterObj.inprogress_exceptions= inProgressExemptions[0]
                    #     else:
                    #         masterObj.inprogress_exceptions= 'NE'

                    # else:
                    #     masterObj.inprogress_exceptions= 'NE'
                    
                    inProgressDevice = Device_Table.query.with_entities(Device_Table.pn_code, Device_Table.hw_eos_date, Device_Table.vuln_fix_plan_status, Device_Table.vuln_ops_severity).filter_by(device_id=vulnerabilityObj.device_name).first()
                    if inProgressDevice:
                        
                        if inProgressDevice[0]:
                            masterObj.pn_code= inProgressDevice[0]
                        else:
                            masterObj.pn_code= 'NE'
                        
                        if inProgressDevice[1]:
                            masterObj.hw_eos_date= inProgressDevice[1]
                        else:
                            pass
                            #masterObj.hw_eos_date= 'NE'
                        
                        if inProgressDevice[2]:
                            masterObj.vuln_fix_plan_status= inProgressDevice[2]
                        else:
                            masterObj.vuln_fix_plan_status= 'NE'

                        if inProgressDevice[3]:
                            masterObj.vuln_ops_severity= inProgressDevice[3]
                        else:
                            masterObj.vuln_ops_severity= 'NE'
                            
                    else:
                        masterObj.pn_code= 'NE'
                        #masterObj.hw_eos_date= 'NE'
                        masterObj.vuln_fix_plan_status= 'NE'
                        masterObj.vuln_ops_severity= 'NE'

                    InsertData(masterObj)

                   
                    if 'closed' not in masterObj.overall_status.lower() and masterObj.vuln_fix_plan_status=="No Plan":
                        isNoPlanExists = VULNERABILITY_IGW_NO_PLAN.query.with_entities(VULNERABILITY_IGW_NO_PLAN.device_ip).filter_by(device_ip=masterObj.device_ip).filter_by(creation_date=masterObj.creation_date).first()
                        if not isNoPlanExists:
                            noPlanObj.device_name= masterObj.device_name
                            noPlanObj.device_ip= masterObj.device_ip
                            noPlanObj.pn_code= masterObj.pn_code
                            noPlanObj.creation_date= masterObj.creation_date
                            noPlanObj.modification_date= masterObj.modification_date
                            noPlanObj.created_by= masterObj.created_by
                            noPlanObj.modified_by= masterObj.modified_by
                            InsertData(noPlanObj)
                            print("Inserted IGW Vulnerability No Plan Device", file=sys.stderr)

                    if 'closed' not in masterObj.overall_status.lower() and masterObj.pn_code=="NE":
                        isNotFoundExists = VULNERABILITY_IGW_NOT_FOUND.query.with_entities(VULNERABILITY_IGW_NOT_FOUND.device_ip).filter_by(device_ip=masterObj.device_ip).filter_by(creation_date=masterObj.creation_date).first()
                        if not isNotFoundExists:
                            ipamObj = IGW_IPAM_TABLE.query.with_entities(IGW_IPAM_TABLE.device_id).filter_by(ip_address=masterObj.device_ip).first()
                            if ipamObj:
                                notFoundObj.correct_device_id= ipamObj[0]
                            else:
                                notFoundObj.correct_device_id= "Not Found"

                            notFoundObj.device_name= masterObj.device_name
                            notFoundObj.device_ip= masterObj.device_ip
                            
                            notFoundObj.creation_date= masterObj.creation_date
                            notFoundObj.modification_date= masterObj.modification_date
                            notFoundObj.created_by= masterObj.created_by
                            notFoundObj.modified_by= masterObj.modified_by
                            InsertData(notFoundObj)
                            print("Inserted IGW Vulnerability Not Found Device", file=sys.stderr)
                            
                except Exception as e:
                        print(f"Error Occured in  Population of Master Table {e}", file=sys.stderr)
    vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "IGW-VULN-TO-MASTER").first()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        vulnStatus.script = "IGW-VULN-TO-MASTER"
        vulnStatus.status = "Completed"
        vulnStatus.creation_date= current_time
        vulnStatus.modification_date= current_time
        db.session.add(vulnStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)
    
    print("Finished Population of IGW Master", file=sys.stderr)

    return jsonify({'response': "success","code":"200"})


@app.route("/getAllIgwVulnerabilityMasterByDate", methods = ['POST'])
@token_required
def GetAllIgwVulnerabilityMasterByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityMasterObjList=[]
        #vulnerabilityMasterObjs = VULNERABILITY_IGW_MASTER.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityMasterObjs =  db.session.execute(f"SELECT * FROM vulnerability_igw_master WHERE creation_date = '{current_time}'")
        try:
            for vulnerabilityMasterObj in vulnerabilityMasterObjs:

                vulnerabilityMasterDataDict= {}
                vulnerabilityMasterDataDict['vulnerability_master_id']=vulnerabilityMasterObj[0]
                vulnerabilityMasterDataDict['scan_result_id'] = vulnerabilityMasterObj[1]
                vulnerabilityMasterDataDict['device_ip'] = vulnerabilityMasterObj[2]
                vulnerabilityMasterDataDict['device_name'] = vulnerabilityMasterObj[3]
                vulnerabilityMasterDataDict['severity'] = vulnerabilityMasterObj[4]
                vulnerabilityMasterDataDict['cve_id'] = vulnerabilityMasterObj[5]
                
                if vulnerabilityMasterObj[6]:
                    vulnerabilityMasterDataDict['due_date'] = FormatDate(vulnerabilityMasterObj[6])
                if vulnerabilityMasterObj[7]:
                    vulnerabilityMasterDataDict['last_detected'] =FormatDate( vulnerabilityMasterObj[7])
                
                vulnerabilityMasterDataDict['overall_status'] = vulnerabilityMasterObj[8]
                vulnerabilityMasterDataDict['qualys_vuln_status'] = vulnerabilityMasterObj[9]
                
                
                #vulnerabilityMasterDataDict['inprogress_exceptions'] = vulnerabilityMasterObj[10]
                vulnerabilityMasterDataDict['all_exceptions'] = vulnerabilityMasterObj[10]
                
                vulnerabilityMasterDataDict['pn_code'] = vulnerabilityMasterObj[11]
                
                if vulnerabilityMasterObj[12]:
                    vulnerabilityMasterDataDict['hw_eos_date'] = FormatDate(vulnerabilityMasterObj[12])
                
                vulnerabilityMasterDataDict['vuln_fix_plan_status'] = vulnerabilityMasterObj[13]          
                vulnerabilityMasterDataDict['vuln_ops_severity'] = vulnerabilityMasterObj[14]
                vulnerabilityMasterDataDict['technical_contact'] = vulnerabilityMasterObj[15]
                
                
                vulnerabilityMasterDataDict['creation_date'] = FormatDate(vulnerabilityMasterObj[16])
                vulnerabilityMasterDataDict['modification_date'] = FormatDate(vulnerabilityMasterObj[17])
                vulnerabilityMasterDataDict['created_by'] = vulnerabilityMasterObj[18]
                vulnerabilityMasterDataDict['modified_by'] = vulnerabilityMasterObj[19]
                
                vulnerabilityMasterObjList.append(vulnerabilityMasterDataDict)

            #print("%%%"+ vulnerabilityMasterObjList, file=sys.stderr)
            content = gzip.compress(json.dumps(vulnerabilityMasterObjList).encode('utf8'), 5)
            response = make_response(content)
            response.headers['Content-length'] = len(content)
            response.headers['Content-Encoding'] = 'gzip'
            return response
        except Exception as e:
            print(f"Error Occured in Getting Master Vulnerabilities {e}", file=sys.stderr)
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllIgwVulnerabilityMaster", methods = ['GET'])
@token_required
def GetAllIgwVulnerabilityMaster(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityMasterObjList=[]
        
        vulnerabilityMasterObjs =  db.session.execute(f'SELECT * FROM vulnerability_igw_master WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_igw_master)')

        for vulnerabilityMasterObj in vulnerabilityMasterObjs:

            vulnerabilityMasterDataDict= {}
            vulnerabilityMasterDataDict['vulnerability_master_id']=vulnerabilityMasterObj[0]
            vulnerabilityMasterDataDict['scan_result_id'] = vulnerabilityMasterObj[1]
            vulnerabilityMasterDataDict['device_ip'] = vulnerabilityMasterObj[2]
            vulnerabilityMasterDataDict['device_name'] = vulnerabilityMasterObj[3]
            vulnerabilityMasterDataDict['severity'] = vulnerabilityMasterObj[4]
            vulnerabilityMasterDataDict['cve_id'] = vulnerabilityMasterObj[5]
            
            if vulnerabilityMasterObj[6]:
                vulnerabilityMasterDataDict['due_date'] = FormatDate(vulnerabilityMasterObj[6])
            if vulnerabilityMasterObj[7]:
                vulnerabilityMasterDataDict['last_detected'] =FormatDate( vulnerabilityMasterObj[7])
            
            vulnerabilityMasterDataDict['overall_status'] = vulnerabilityMasterObj[8]
            vulnerabilityMasterDataDict['qualys_vuln_status'] = vulnerabilityMasterObj[9]
            

            
            #vulnerabilityMasterDataDict['inprogress_exceptions'] = vulnerabilityMasterObj[10]
            vulnerabilityMasterDataDict['all_exceptions'] = vulnerabilityMasterObj[10]
            
            vulnerabilityMasterDataDict['pn_code'] = vulnerabilityMasterObj[11]
            
            if vulnerabilityMasterObj[12]:
                vulnerabilityMasterDataDict['hw_eos_date'] = FormatDate(vulnerabilityMasterObj[12])
            
            
            
            vulnerabilityMasterDataDict['vuln_fix_plan_status'] = vulnerabilityMasterObj[13]          
            vulnerabilityMasterDataDict['vuln_ops_severity'] = vulnerabilityMasterObj[14]
            vulnerabilityMasterDataDict['technical_contact'] = vulnerabilityMasterObj[15]
            
            
            vulnerabilityMasterDataDict['creation_date'] = FormatDate(vulnerabilityMasterObj[16])
            vulnerabilityMasterDataDict['modification_date'] = FormatDate(vulnerabilityMasterObj[17])
            vulnerabilityMasterDataDict['created_by'] = vulnerabilityMasterObj[18]
            vulnerabilityMasterDataDict['modified_by'] = vulnerabilityMasterObj[19]
            
            
            vulnerabilityMasterObjList.append(vulnerabilityMasterDataDict)

        content = gzip.compress(json.dumps(vulnerabilityMasterObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllIgwVulnerabilityMasterDates",methods=['GET'])
@token_required
def GetAllIgwVulnerabilityMasterDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_igw_master  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/editIgwVulnerabilityMaster", methods = ['POST'])
@token_required
def EditIgwVulnerabilityMaster(user_data):  
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityMasterObj = request.get_json()
        time= datetime.now(tz)
        #print(postData,file=sys.stderr)

        #for vulnerabilityMasterObj in postData:
        try:
            vulnerabilityMaster = VULNERABILITY_IGW_MASTER()
            if 'scan_result_id' in vulnerabilityMasterObj and 'vulnerability_master_id' in vulnerabilityMasterObj:
                vulnerabilityMasterId = VULNERABILITY_IGW_MASTER.query.with_entities(VULNERABILITY_IGW_MASTER.vulnerability_master_id).filter_by(vulnerability_master_id=vulnerabilityMasterObj['vulnerability_master_id']).first()
                
                if vulnerabilityMasterId is not None:
                    vulnerabilityMaster.vulnerability_master_id= vulnerabilityMasterId[0]
                    
                    if 'device_ip' in vulnerabilityMasterObj:
                        vulnerabilityMaster.device_ip = vulnerabilityMasterObj['device_ip']
                    else:
                        vulnerabilityMaster.device_ip = 'NE'

                    if 'device_name' in vulnerabilityMasterObj:
                        vulnerabilityMaster.device_name = vulnerabilityMasterObj['device_name']
                    else:
                        vulnerabilityMaster.device_name = 'NE'

                    if 'severity' in vulnerabilityMasterObj:
                        if  vulnerabilityMasterObj['severity']:
                            vulnerabilityMaster.severity = vulnerabilityMasterObj['severity']
                        else:
                            vulnerabilityMaster.severity = 'NE'

                        
                    if 'due_date' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['due_date']:
                            vulnerabilityMaster.due_date = FormatStringDate(vulnerabilityMasterObj['due_date'])
                    #else:
                    #    vulnerabilityMaster.due_date = ''

                    
                    if 'last_detected' in vulnerabilityMasterObj:
                        vulnerabilityMaster.last_detected = FormatStringDate(vulnerabilityMasterObj['last_detected'])
                    #else:
                    #    vulnerabilityMaster.last_detected = 'NE'

                    if 'overall_status' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['overall_status']:
                            vulnerabilityMaster.overall_status = vulnerabilityMasterObj['overall_status']
                        else:
                            vulnerabilityMaster.overall_status = 'NE'

                    if 'qualys_vuln_status' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['qualys_vuln_status']:
                            vulnerabilityMaster.qualys_vuln_status =  vulnerabilityMasterObj['qualys_vuln_status']
                        else:
                            vulnerabilityMaster.qualys_vuln_status = 'NE'

                    if 'in_progress_exception' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['in_progress_exception']:
                            vulnerabilityMaster.in_progress_exception = vulnerabilityMasterObj['in_progress_exception']
                        else:
                            vulnerabilityMaster.in_progress_exception = 'NE'

                    if 'cve_id' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['cve_id']:
                            vulnerabilityMaster.cve_id = vulnerabilityMasterObj['cve_id']
                        else:
                            vulnerabilityMaster.cve_id = 'NE'


                    if 'all_exceptions' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['all_exceptions']:
                            vulnerabilityMaster.all_exceptions = vulnerabilityMasterObj['all_exceptions']
                        else:
                            vulnerabilityMaster.all_exceptions = 'NE'

                    if 'pn_code' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['pn_code']:
                            vulnerabilityMaster.pn_code = vulnerabilityMasterObj['pn_code']
                        else:
                            vulnerabilityMaster.pn_code = 'NE'
                    
                    if 'technical_contact' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['technical_contact']:
                            vulnerabilityMaster.technical_contact = vulnerabilityMasterObj['technical_contact']
                        else:
                            vulnerabilityMaster.technical_contact = 'NE'

                    if 'hw_eos_date' in vulnerabilityMasterObj:
                        vulnerabilityMaster.hw_eos_date = FormatStringDate(vulnerabilityMasterObj['hw_eos_date'])
                    #else:
                    #    vulnerabilityMaster.hw_eos_date = 'NE'

                    if 'vuln_fix_plan_status' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['vuln_fix_plan_status']:
                            vulnerabilityMaster.vuln_fix_plan_status = vulnerabilityMasterObj['vuln_fix_plan_status']
                        else:
                            vulnerabilityMaster.vuln_fix_plan_status = 'NE'

                    if 'vuln_ops_severity' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['vuln_ops_severity']:
                            vulnerabilityMaster.vuln_ops_severity = vulnerabilityMasterObj['vuln_ops_severity']
                        else:
                            vulnerabilityMaster.vuln_ops_severity = 'NE'

                    #vulnerabilityMaster.creation_date= time
                    vulnerabilityMaster.modification_date= time
                    vulnerabilityMaster.modified_by= user_data['user_id']
                
                    
                    UpdateData(vulnerabilityMaster)
                else:
                    return jsonify({'response': "Vulnerability Id can not be found in Table"}), 500  
            else:
                return jsonify({'response': "Vulnerability Id Missing"}), 500  
            return jsonify({'response': "success","code":"200"})
        except Exception as e:
            traceback.print_exc()
            print(f"Error Occured in Adding Vulnerability Master {vulnerabilityMasterObj['scan_result_id']}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/syncIgwVulnerabilityMasterToDevices", methods = ['GET'])
@token_required
def syncIgwVulnerabilityMasterToDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        try:
            syncIgwVulnerabilityMasterToDevicesFunc(user_data)
        
        except Exception as e:
            print(f"Error Occured in  Population of Devices {e}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401        

def syncIgwVulnerabilityMasterToDevicesFunc(user_data):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "IGW-VULN-TO-DEVICES").first()
    try:
        vulnStatus.script = "IGW-VULN-TO-DEVICES"
        vulnStatus.status = "Running"
        vulnStatus.creation_date= current_time
        vulnStatus.modification_date= current_time
        db.session.add(vulnStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)
    
    try:
        tableObjs=[]
        date=""
        masterDateObj = db.session.execute('SELECT max(creation_date) FROM vulnerability_igw_master')
        for row in masterDateObj:
            date=row[0]

        for table in range(2):

            if table==0:
                print("Populating IGW-NET Vulnerabilities in Seed", file=sys.stderr)
                tableObjs = Seed.query.filter(or_(Seed.cisco_domain=='IGW-NET', Seed.cisco_domain=='IGW-SYS')).all()
            if table==1:
                print("Populating IGW-NET Vulnerabilities in Devices", file=sys.stderr)
                tableObjs = Device_Table.query.filter(or_(Device_Table.cisco_domain=='IGW-NET', Device_Table.cisco_domain=='IGW-SYS')).all()
            
            for obj in tableObjs:
                try:
                    deviceId = obj.device_id
                    severityObjs= VULNERABILITY_IGW_MASTER.query.with_entities(VULNERABILITY_IGW_MASTER.severity).filter_by(device_name=deviceId).filter_by(creation_date=date).filter(VULNERABILITY_IGW_MASTER.overall_status.notlike('Closed%')).all()
                    if severityObjs:
                        uniqueSeverity= set()
                        for master in severityObjs:
                            uniqueSeverity.add(master[0])
                        vulnSeverity=""
                        for severity in uniqueSeverity:
                            if severity.lower()=="medium":
                                vulnSeverity+="SL3,"
                            if severity.lower()=="high":
                                vulnSeverity+="SL4,"
                            if severity.lower()=="critical":
                                vulnSeverity+="SL5," 
                        vulnSeverity= vulnSeverity[:-1]
                        obj.vulnerability_severity= vulnSeverity
                        UpdateData(obj)
                        print(f"Updated Vuln Severity for Device {obj.device_id} {vulnSeverity}", file=sys.stderr)
                    else:
                        obj.vulnerability_severity= ""
                        UpdateData(obj)
                        print(f"Reset Vuln Severity for Device {obj.device_id}", file=sys.stderr)

                except Exception  as e:
                    print(f"Exception Occured in Syncing Vulnerabilities {e}")
        
        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "IGW-VULN-TO-DEVICES").first()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            vulnStatus.script = "IGW-VULN-TO-DEVICES"
            vulnStatus.status = "Completed"
            vulnStatus.creation_date= current_time
            vulnStatus.modification_date= current_time
            db.session.add(vulnStatus)
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"Error while updating script status {e}", file=sys.stderr)

        print("Finished IGW Vulnerability Sync To Device ", file=sys.stderr)
    except Exception  as e:
        print(f"Exception Occured in Syncing Vulnerabilities {e}") 

@app.route("/getigwVulnerabilitySyncTOMasterStatus", methods = ['GET'])
@token_required
def GetigwVulnerabilitySyncTOMasterStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        f5={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "IGW-VULN-TO-MASTER").first()
        if vulnStatus:
            script_status= vulnStatus.status
            script_modifiation_date= str(vulnStatus.modification_date)
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


@app.route("/getigwVulnerabilitySyncToDevicesStatus", methods = ['GET'])
#@token_required
def GetigwVulnerabilitySyncTODevicesStatus():
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        f5={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "IGW-VULN-TO-DEVICES").first()
        if vulnStatus:
            script_status= vulnStatus.status
            script_modifiation_date= str(vulnStatus.modification_date)
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


@app.route("/getIgwVulnerabilityImportStatus", methods = ['GET'])
@token_required
def GetIgwVulnerabilityImportStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        f5={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "IGW-VULN-ARCHER").first()
        if vulnStatus:
            script_status= vulnStatus.status
            script_modifiation_date= str(vulnStatus.modification_date)
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


### No Plan

@app.route("/getAllIgwVulnerabilityNoPlan", methods = ['GET'])
@token_required
def GetAllIgwVulnerabilityNoPlan(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityNoPlanObjList=[]
        
        vulnerabilityNoPlanObjs =  db.session.execute(f'SELECT * FROM vulnerability_igw_no_plan WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_igw_no_plan)')

        for vulnerabilityNoPlanObj in vulnerabilityNoPlanObjs:

            vulnerabilityNoPlanDataDict= {}
            vulnerabilityNoPlanDataDict['vulnerability_no_plan_id']=vulnerabilityNoPlanObj[0]
            vulnerabilityNoPlanDataDict['device_ip'] = vulnerabilityNoPlanObj[1]
            vulnerabilityNoPlanDataDict['device_name'] = vulnerabilityNoPlanObj[2]
            vulnerabilityNoPlanDataDict['pn_code'] = vulnerabilityNoPlanObj[3]
             
            vulnerabilityNoPlanDataDict['creation_date'] = FormatDate(vulnerabilityNoPlanObj[4])
            vulnerabilityNoPlanDataDict['modification_date'] = FormatDate(vulnerabilityNoPlanObj[5])
            vulnerabilityNoPlanDataDict['created_by'] = vulnerabilityNoPlanObj[6]
            vulnerabilityNoPlanDataDict['modified_by'] = vulnerabilityNoPlanObj[7]
            
            
            vulnerabilityNoPlanObjList.append(vulnerabilityNoPlanDataDict)

        content = gzip.compress(json.dumps(vulnerabilityNoPlanObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllIgwVulnerabilityNoPlanDates",methods=['GET'])
@token_required
def GetAllIgwVulnerabilityNoPlanDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_igw_no_plan  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllIgwVulnerabilityNoPlanByDate", methods = ['POST'])
@token_required
def GetAllIgwVulnerabilityNoPlanByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityNoPlanObjList=[]
        #vulnerabilityNoPlanObjs = VULNERABILITY_IGW_MASTER.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityNoPlanObjs =  db.session.execute(f"SELECT * FROM vulnerability_igw_no_plan WHERE creation_date = '{current_time}'")
        try:
            for vulnerabilityNoPlanObj in vulnerabilityNoPlanObjs:

                vulnerabilityNoPlanDataDict= {}
                vulnerabilityNoPlanDataDict['vulnerability_no_plan_id']=vulnerabilityNoPlanObj[0]
                vulnerabilityNoPlanDataDict['device_ip'] = vulnerabilityNoPlanObj[1]
                vulnerabilityNoPlanDataDict['device_name'] = vulnerabilityNoPlanObj[2]
                vulnerabilityNoPlanDataDict['pn_code'] = vulnerabilityNoPlanObj[3]
                
                vulnerabilityNoPlanDataDict['creation_date'] = FormatDate(vulnerabilityNoPlanObj[4])
                vulnerabilityNoPlanDataDict['modification_date'] = FormatDate(vulnerabilityNoPlanObj[5])
                vulnerabilityNoPlanDataDict['created_by'] = vulnerabilityNoPlanObj[6]
                vulnerabilityNoPlanDataDict['modified_by'] = vulnerabilityNoPlanObj[7]
                
                vulnerabilityNoPlanObjList.append(vulnerabilityNoPlanDataDict)

            #print("%%%"+ vulnerabilityNoPlanObjList, file=sys.stderr)
            content = gzip.compress(json.dumps(vulnerabilityNoPlanObjList).encode('utf8'), 5)
            response = make_response(content)
            response.headers['Content-length'] = len(content)
            response.headers['Content-Encoding'] = 'gzip'
            return response
        except Exception as e:
            print(f"Error Occured in Getting NoPlan Vulnerabilities {e}", file=sys.stderr)
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

#### Not Found

@app.route("/getAllIgwVulnerabilityNotFound", methods = ['GET'])
@token_required
def GetAllIgwVulnerabilityNotFound(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityNotFoundObjList=[]
        
        vulnerabilityNotFoundObjs =  db.session.execute(f'SELECT * FROM vulnerability_igw_not_found WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_igw_not_found)')

        for vulnerabilityNotFoundObj in vulnerabilityNotFoundObjs:

            vulnerabilityNotFoundDataDict= {}
            vulnerabilityNotFoundDataDict['vulnerability_not_found_id']=vulnerabilityNotFoundObj[0]
            vulnerabilityNotFoundDataDict['device_ip'] = vulnerabilityNotFoundObj[1]
            vulnerabilityNotFoundDataDict['device_name'] = vulnerabilityNotFoundObj[2]
            vulnerabilityNotFoundDataDict['correct_device_id'] = vulnerabilityNotFoundObj[3]
             
            vulnerabilityNotFoundDataDict['creation_date'] = FormatDate(vulnerabilityNotFoundObj[4])
            vulnerabilityNotFoundDataDict['modification_date'] = FormatDate(vulnerabilityNotFoundObj[5])
            vulnerabilityNotFoundDataDict['created_by'] = vulnerabilityNotFoundObj[6]
            vulnerabilityNotFoundDataDict['modified_by'] = vulnerabilityNotFoundObj[7]
            
            
            vulnerabilityNotFoundObjList.append(vulnerabilityNotFoundDataDict)

        content = gzip.compress(json.dumps(vulnerabilityNotFoundObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllIgwVulnerabilityNotFoundDates",methods=['GET'])
@token_required
def GetAllIgwVulnerabilityNotFoundDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_igw_not_found  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllIgwVulnerabilityNotFoundByDate", methods = ['POST'])
@token_required
def GetAllIgwVulnerabilityNotFoundByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityNotFoundObjList=[]
        #vulnerabilityNotFoundObjs = VULNERABILITY_IGW_MASTER.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityNotFoundObjs =  db.session.execute(f"SELECT * FROM vulnerability_igw_not_found WHERE creation_date = '{current_time}'")
        try:
            for vulnerabilityNotFoundObj in vulnerabilityNotFoundObjs:

                vulnerabilityNotFoundDataDict= {}
                vulnerabilityNotFoundDataDict['vulnerability_not_found_id']=vulnerabilityNotFoundObj[0]
                vulnerabilityNotFoundDataDict['device_ip'] = vulnerabilityNotFoundObj[1]
                vulnerabilityNotFoundDataDict['device_name'] = vulnerabilityNotFoundObj[2]
                vulnerabilityNotFoundDataDict['correct_device_id'] = vulnerabilityNotFoundObj[3]
            
                vulnerabilityNotFoundDataDict['creation_date'] = FormatDate(vulnerabilityNotFoundObj[4])
                vulnerabilityNotFoundDataDict['modification_date'] = FormatDate(vulnerabilityNotFoundObj[5])
                vulnerabilityNotFoundDataDict['created_by'] = vulnerabilityNotFoundObj[6]
                vulnerabilityNotFoundDataDict['modified_by'] = vulnerabilityNotFoundObj[7]
                
                vulnerabilityNotFoundObjList.append(vulnerabilityNotFoundDataDict)

            #print("%%%"+ vulnerabilityNotFoundObjList, file=sys.stderr)
            content = gzip.compress(json.dumps(vulnerabilityNotFoundObjList).encode('utf8'), 5)
            response = make_response(content)
            response.headers['Content-length'] = len(content)
            response.headers['Content-Encoding'] = 'gzip'
            return response
        except Exception as e:
            print(f"Error Occured in Getting NotFound Vulnerabilities {e}", file=sys.stderr)
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getIgwVulnerabilityTechnicalContact", methods = ['GET'])
@token_required
def GetIgwVulnerabilityTechnicalContact(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnList=[]
        vulnList= GetIgwVulnerabilityTechnicalContactFunc()
        content = gzip.compress(json.dumps(vulnList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def GetIgwVulnerabilityTechnicalContactFunc():
    vulnList=[]
    vulnList.append('All')
    try:
        vulnObj =  db.session.execute(f'SELECT distinct(technical_contact) FROM vulnerability_igw_master WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_igw_master)')

        for vuln in vulnObj:
            if vuln[0] is not None:
                vulnList.append(vuln[0])

        return vulnList
    except Exception as e:
        return vulnList
        print("Error in getting distinct Technical Contact")


@app.route("/getIgwVulnerabilityOverallStatus", methods = ['GET'])
@token_required
def GetIgwVulnerabilityOverallStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnList=[]
        
        vulnList= GetIgwVulnerabilityOverallStatusFunc()
        content = gzip.compress(json.dumps(vulnList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
        
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def GetIgwVulnerabilityOverallStatusFunc():
    vulnList=[]
    vulnList.append('All')
    try:
        vulnObj =  db.session.execute(f"SELECT distinct(overall_status) FROM vulnerability_igw_master WHERE OVERALL_STATUS NOT LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_igw_master)")

        for vuln in vulnObj:
            if vuln[0] is not None:
                vulnList.append(vuln[0])
        return vulnList
    except Exception as e:
            return vulnList
            print("Error in getting distinct Technical Contact")


###################################### SOC Vulnerability ################################################################


def FormatStringDate(date):
    #print(date, file=sys.stderr)
    try:
        if date is not None:
            if '-' in date:
                result = datetime.strptime(date,'%m-%d-%Y')
            elif '/' in date:
                result = datetime.strptime(date,'%m/%d/%Y')
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
    try:
        #print(f"Data is : {obj.creation_date}", file=sys.stderr)
        #add data to db
        #obj.creation_date= datetime.now(tz)
        #obj.modification_date= datetime.now(tz)
        db.session.add(obj)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Exception in Inserting data {e}", file=sys.stderr)
        db.session.flush()
        db.session.rollback()
        

def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%m-%d-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

def UpdateData(obj):
    #add data to db
    try:
        #obj.modification_date= datetime.now(tz)
        db.session.merge(obj)
        db.session.commit()
        #print(obj.site_name, file=sys.stderr)
    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong {e}", file=sys.stderr)
    
    return True


###
#SOC Vulnerabilities Archer
###

@app.route("/getAllSocVulnerabilityArcherDates",methods=['GET'])
@token_required
def GetAllSocVulnerabilityArcherDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_soc_archer  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/addSocVulnerabilityArcher", methods = ['POST'])
@token_required
def AddSocVulnerabilityArcher(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()
        time= datetime.now(tz)
        print(postData,file=sys.stderr)

        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "SOC-VULN-ARCHER").first()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            vulnStatus.script = "SOC-VULN-ARCHER"
            vulnStatus.status = "Running"
            vulnStatus.creation_date= current_time
            vulnStatus.modification_date= current_time
            db.session.add(vulnStatus)
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"Error while updating script status {e}", file=sys.stderr)


        for vulnerabilityArcherObj in postData:
            try:
                vulnerabilityArcher = VULNERABILITY_SOC_ARCHER()
                if 'scan_result_id' in vulnerabilityArcherObj:
                    vulnerabilityArcher.scan_result_id = vulnerabilityArcherObj['scan_result_id']
                else:
                    print(f"Error Occured in Adding Vulnerability Archer Scan Result Id Not Found.", file=sys.stderr)
                    continue

                if 'device_ip' in vulnerabilityArcherObj:
                    vulnerabilityArcher.device_ip = vulnerabilityArcherObj['device_ip']
                else:
                    vulnerabilityArcher.device_ip = ''

                if 'device_name' in vulnerabilityArcherObj:
                    vulnerabilityArcher.device_name = vulnerabilityArcherObj['device_name']
                else:
                    vulnerabilityArcher.device_name = ''

                if 'title' in vulnerabilityArcherObj:
                    vulnerabilityArcher.title = vulnerabilityArcherObj['title']
                else:
                    vulnerabilityArcher.title = ''

                if 'due_date' in vulnerabilityArcherObj:
                    if vulnerabilityArcherObj['due_date']:
                        vulnerabilityArcher.due_date = FormatStringDate(vulnerabilityArcherObj['due_date'])
                #else:
                #    vulnerabilityArcher.due_date = ''

                if 'false_positive_date' in vulnerabilityArcherObj:
                    if vulnerabilityArcherObj['false_positive_date']:
                        vulnerabilityArcher.false_positive_date = FormatStringDate(vulnerabilityArcherObj['false_positive_date'])
                #else:
                #    vulnerabilityArcher.false_positive_date = ''

                if 'severity' in vulnerabilityArcherObj:
                    vulnerabilityArcher.severity = vulnerabilityArcherObj['severity']
                else:
                    vulnerabilityArcher.severity = ''

                if 'overall_status' in vulnerabilityArcherObj:
                    vulnerabilityArcher.overall_status = vulnerabilityArcherObj['overall_status']
                else:
                    vulnerabilityArcher.overall_status = ''

                if 'qualys_vuln_status' in vulnerabilityArcherObj:

                    vulnerabilityArcher.qualys_vuln_status =  vulnerabilityArcherObj['qualys_vuln_status']
                else:
                    vulnerabilityArcher.qualys_vuln_status = ''

                if 'last_detected' in vulnerabilityArcherObj:
                    if vulnerabilityArcherObj['last_detected']:
                        vulnerabilityArcher.last_detected = FormatStringDate(vulnerabilityArcherObj['last_detected'])
                #else:
                #    vulnerabilityArcher.last_detected = ''
                    
                if 'technical_contact' in vulnerabilityArcherObj:
                    vulnerabilityArcher.technical_contact = vulnerabilityArcherObj['technical_contact']
                else:
                    vulnerabilityArcher.technical_contact = ''

                if 'exception_requests' in vulnerabilityArcherObj:
                    vulnerabilityArcher.exception_requests = vulnerabilityArcherObj['exception_requests']
                else:
                    vulnerabilityArcher.exception_requests = ''
                
                if 'cve_id' in vulnerabilityArcherObj:
                    vulnerabilityArcher.cve_id = vulnerabilityArcherObj['cve_id']
                else:
                    vulnerabilityArcher.cve_id = ''

                vulnerabilityArcher.creation_date= time
                vulnerabilityArcher.modification_date= time
                vulnerabilityArcher.created_by= user_data['user_id']
                vulnerabilityArcher.modified_by=  user_data['user_id']
            
                
                InsertData(vulnerabilityArcher)
            except Exception as e:
                traceback.print_exc()
                print(f"Error Occured in Adding Vulnerability Archer {vulnerabilityArcherObj['scan_result_id']}", file=sys.stderr)

        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "SOC-VULN-ARCHER").first()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            vulnStatus.script = "SOC-VULN-ARCHER"
            vulnStatus.status = "Completed"
            vulnStatus.creation_date= current_time
            vulnStatus.modification_date= current_time
            db.session.add(vulnStatus)
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"Error while updating script status {e}", file=sys.stderr)
            

        try:
            print(f"Running Automatic Sync of SOC Vulnerability to Master", file=sys.stderr)
            syncSocVulnerabilityMasterFunc(user_data)

        except Exception as e:
            print(f"Exception Occured in Automatic Sync of SOC Vulnerability to Master {e}", file=sys.stderr)

        try:
            print(f"Running Automatic Sync of SOC Vulnerability to Devices", file=sys.stderr)
            syncSocVulnerabilityMasterToDevicesFunc(user_data)

        except Exception as e:
           print(f"Exception Occured in Automatic Sync of SOC Vulnerability to Devices {e}", file=sys.stderr)


        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editSocVulnerabilityArcher", methods = ['POST'])
@token_required
def EditSocVulnerabilityArcher(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityArcherObj = request.get_json()
        time= datetime.now(tz)
        print(vulnerabilityArcherObj,file=sys.stderr)

        #for vulnerabilityArcherObj in postData:
        try:
            vulnerabilityArcher = VULNERABILITY_SOC_ARCHER()
            if 'scan_result_id' in vulnerabilityArcherObj and 'vulnerability_archer_id' in vulnerabilityArcherObj:
                vulnerabilityArcherId = VULNERABILITY_SOC_ARCHER.query.with_entities(VULNERABILITY_SOC_ARCHER.vulnerability_archer_id).filter_by(vulnerability_archer_id=vulnerabilityArcherObj['vulnerability_archer_id']).first()
                if vulnerabilityArcherId is not None:
                    vulnerabilityArcher.vulnerability_archer_id= vulnerabilityArcherId[0]
                    if 'device_ip' in vulnerabilityArcherObj:
                        vulnerabilityArcher.device_ip = vulnerabilityArcherObj['device_ip']
                    else:
                        vulnerabilityArcher.device_ip = ''

                    if 'device_name' in vulnerabilityArcherObj:
                        vulnerabilityArcher.device_name = vulnerabilityArcherObj['device_name']
                    else:
                        vulnerabilityArcher.device_name = ''

                    if 'title' in vulnerabilityArcherObj:
                        vulnerabilityArcher.title = vulnerabilityArcherObj['title']
                    else:
                        vulnerabilityArcher.title = ''

                        
                    if 'due_date' in vulnerabilityArcherObj:
                        if vulnerabilityArcherObj['due_date']:
                            vulnerabilityArcher.due_date = FormatStringDate(vulnerabilityArcherObj['due_date'])
                    #else:
                    #    vulnerabilityArcher.due_date = ''

                    if 'false_positive_date' in vulnerabilityArcherObj:
                        if vulnerabilityArcherObj['false_positive_date']:
                            vulnerabilityArcher.false_positive_date = FormatStringDate(vulnerabilityArcherObj['false_positive_date'])
                    #else:
                    #    vulnerabilityArcher.false_positive_date = ''

                    if 'severity' in vulnerabilityArcherObj:
                        vulnerabilityArcher.severity = vulnerabilityArcherObj['severity']
                    else:
                        vulnerabilityArcher.severity = ''

                    if 'overall_status' in vulnerabilityArcherObj:
                        vulnerabilityArcher.overall_status = vulnerabilityArcherObj['overall_status']
                    else:
                        vulnerabilityArcher.overall_status = ''

                    if 'qualys_vuln_status' in vulnerabilityArcherObj:

                        vulnerabilityArcher.qualys_vuln_status =  vulnerabilityArcherObj['qualys_vuln_status']
                    else:
                        vulnerabilityArcher.qualys_vuln_status = ''

                    if 'last_detected' in vulnerabilityArcherObj:
                        if vulnerabilityArcherObj['last_detected']:
                            vulnerabilityArcher.last_detected = FormatStringDate(vulnerabilityArcherObj['last_detected'])
                    #else:
                    #    vulnerabilityArcher.last_detected = ''
                            
                    if 'technical_contact' in vulnerabilityArcherObj:
                        vulnerabilityArcher.technical_contact = vulnerabilityArcherObj['technical_contact']
                    else:
                        vulnerabilityArcher.technical_contact = ''

                    if 'exception_requests' in vulnerabilityArcherObj:
                        vulnerabilityArcher.exception_requests = vulnerabilityArcherObj['exception_requests']
                    else:
                        vulnerabilityArcher.exception_requests = ''
                    
                    if 'cve_id' in vulnerabilityArcherObj:
                        vulnerabilityArcher.cve_id = vulnerabilityArcherObj['cve_id']
                    else:
                        vulnerabilityArcher.cve_id = ''

                    #vulnerabilityArcher.creation_date= time
                    vulnerabilityArcher.modification_date= time
                    vulnerabilityArcher.modified_by=  user_data['user_id']
                    
                    UpdateData(vulnerabilityArcher)
                else:
                    return jsonify({'response': "Vulnerability Id can not be found in Table"}), 500  
            return jsonify({'response': "Vulnerability Id Missing"}), 500  
        except Exception as e:
            traceback.print_exc()
            print(f"Error Occured in Adding Vulnerability Archer {vulnerabilityArcherObj['scan_result_id']}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllSocVulnerabilityArcherByDate", methods = ['POST'])
@token_required
def GetAllSocVulnerabilityArcherByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityArcherObjList=[]
        #vulnerabilityArcherObjs = VULNERABILITY_SOC_ARCHER.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityArcherObjs =  db.session.execute(f"SELECT * FROM vulnerability_soc_archer WHERE creation_date = '{current_time}'")

        for vulnerabilityArcherObj in vulnerabilityArcherObjs:

            vulnerabilityArcherDataDict= {}
            vulnerabilityArcherDataDict['vulnerability_archer_id']=vulnerabilityArcherObj[0]
            vulnerabilityArcherDataDict['scan_result_id'] = vulnerabilityArcherObj[1]
            vulnerabilityArcherDataDict['device_ip'] = vulnerabilityArcherObj[2]
            vulnerabilityArcherDataDict['device_name'] = vulnerabilityArcherObj[3]
            vulnerabilityArcherDataDict['title'] = vulnerabilityArcherObj[4]
            if vulnerabilityArcherObj[5]:
                vulnerabilityArcherDataDict['due_date'] = FormatDate(vulnerabilityArcherObj[5])
            if vulnerabilityArcherObj[6]:
                vulnerabilityArcherDataDict['false_positive_date'] =FormatDate( vulnerabilityArcherObj[6])
            vulnerabilityArcherDataDict['severity'] = vulnerabilityArcherObj[7]
            vulnerabilityArcherDataDict['overall_status'] = vulnerabilityArcherObj[8]
            vulnerabilityArcherDataDict['qualys_vuln_status'] = vulnerabilityArcherObj[9]
            if vulnerabilityArcherObj[10]:
                vulnerabilityArcherDataDict['last_detected'] = FormatDate(vulnerabilityArcherObj[10])
            vulnerabilityArcherDataDict['technical_contact'] = vulnerabilityArcherObj[11]
            vulnerabilityArcherDataDict['exception_requests'] = vulnerabilityArcherObj[12]
            vulnerabilityArcherDataDict['cve_id'] = vulnerabilityArcherObj[13]
            vulnerabilityArcherDataDict['creation_date'] = FormatDate(vulnerabilityArcherObj[14])
            vulnerabilityArcherDataDict['modification_date'] = FormatDate(vulnerabilityArcherObj[15])
            vulnerabilityArcherDataDict['created_by'] = vulnerabilityArcherObj[16]
            vulnerabilityArcherDataDict['modified_by'] = vulnerabilityArcherObj[17]
            vulnerabilityArcherObjList.append(vulnerabilityArcherDataDict)

       
        content = gzip.compress(json.dumps(vulnerabilityArcherObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllSocVulnerabilityArcher", methods = ['GET'])
@token_required
def GetAllSocVulnerabilityArcher(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityArcherObjList=[]
        
        vulnerabilityArcherObjs =  db.session.execute(f'SELECT * FROM vulnerability_soc_archer WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_soc_archer)')

        for vulnerabilityArcherObj in vulnerabilityArcherObjs:

            vulnerabilityArcherDataDict= {}
            vulnerabilityArcherDataDict['vulnerability_archer_id']=vulnerabilityArcherObj[0]
            vulnerabilityArcherDataDict['scan_result_id'] = vulnerabilityArcherObj[1]
            vulnerabilityArcherDataDict['device_ip'] = vulnerabilityArcherObj[2]
            vulnerabilityArcherDataDict['device_name'] = vulnerabilityArcherObj[3]
            vulnerabilityArcherDataDict['title'] = vulnerabilityArcherObj[4]
            if vulnerabilityArcherObj[5]:
                vulnerabilityArcherDataDict['due_date'] = FormatDate(vulnerabilityArcherObj[5])
            if vulnerabilityArcherObj[6]:
                vulnerabilityArcherDataDict['false_positive_date'] =FormatDate( vulnerabilityArcherObj[6])
            vulnerabilityArcherDataDict['severity'] = vulnerabilityArcherObj[7]
            vulnerabilityArcherDataDict['overall_status'] = vulnerabilityArcherObj[8]
            vulnerabilityArcherDataDict['qualys_vuln_status'] = vulnerabilityArcherObj[9]
            if vulnerabilityArcherObj[10]:
                vulnerabilityArcherDataDict['last_detected'] = FormatDate(vulnerabilityArcherObj[10])
            vulnerabilityArcherDataDict['technical_contact'] = vulnerabilityArcherObj[11]
            vulnerabilityArcherDataDict['exception_requests'] = vulnerabilityArcherObj[12]
            vulnerabilityArcherDataDict['cve_id'] = vulnerabilityArcherObj[13]
            vulnerabilityArcherDataDict['creation_date'] = FormatDate(vulnerabilityArcherObj[14])
            vulnerabilityArcherDataDict['modification_date'] = FormatDate(vulnerabilityArcherObj[15])
            vulnerabilityArcherDataDict['created_by'] = vulnerabilityArcherObj[16]
            vulnerabilityArcherDataDict['modified_by'] = vulnerabilityArcherObj[17]
            vulnerabilityArcherObjList.append(vulnerabilityArcherDataDict)

        content = gzip.compress(json.dumps(vulnerabilityArcherObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteSocVulnerabilityArcher",methods = ['POST'])
@token_required
def DeleteSocVulnerabilityArcher(user_data):
    if True:#session.get('token', None):
        vulnerabilityArcherObj = request.get_json()
        #vulnerabilityArcherObj= vulnerabilityArcherObj.get("ips")
        #vulnerabilityArcherObj = [9,10,11,12,13]
        print(vulnerabilityArcherObj,file = sys.stderr)
        
        for obj in vulnerabilityArcherObj.get("ips"):
            vulnerabilityArcherId = VULNERABILITY_SOC_ARCHER.query.filter(VULNERABILITY_SOC_ARCHER.vulnerability_archer_id==obj).first()
            print(vulnerabilityArcherId,file=sys.stderr)
            if obj:
                db.session.delete(vulnerabilityArcherId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
       
#### SOC MASTER Vulnerbility ROUTES   ###

@app.route("/syncSocVulnerabilityMaster", methods = ['GET'])
@token_required
def syncSocVulnerabilityMaster(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        try:
            syncSocVulnerabilityMasterFunc(user_data)
        except Exception as e:
            print(f"Error Occured in  Population of Master Table {e}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def syncSocVulnerabilityMasterFunc(user_data):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "SOC-VULN-TO-MASTER").first()
    try:
        vulnStatus.script = "SOC-VULN-TO-MASTER"
        vulnStatus.status = "Running"
        vulnStatus.creation_date= current_time
        vulnStatus.modification_date= current_time
        db.session.add(vulnStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    for table in range(1):
        
        if table==0:
            print("Populating Archer Vulnerabilities in Master", file=sys.stderr)
            creation_date=""
            creationObj = db.session.execute('SELECT max(creation_date) FROM vulnerability_soc_archer')
            for row in creationObj:
                creation_date=row[0]
            vulnerabilityObjs = VULNERABILITY_SOC_ARCHER.query.filter_by(creation_date=creation_date).all()
        

        if vulnerabilityObjs:
        
            for vulnerabilityObj in vulnerabilityObjs:
                noPlanObj= VULNERABILITY_SOC_NO_PLAN()
                notFoundObj= VULNERABILITY_SOC_NOT_FOUND()
                try:
                    masterObj= VULNERABILITY_SOC_MASTER()
                    
                    if  vulnerabilityObj.scan_result_id:
                        masterObj.scan_result_id = vulnerabilityObj.scan_result_id
                    else: 
                        masterObj.scan_result_id= 'NE'
                        
                    if  vulnerabilityObj.device_ip:
                        masterObj.device_ip = vulnerabilityObj.device_ip
                    else: 
                        masterObj.device_ip= 'NE'
                    
                    if  vulnerabilityObj.device_name:
                        masterObj.device_name = vulnerabilityObj.device_name
                    else: 
                        masterObj.device_name= 'NE'
                    
                    if  vulnerabilityObj.severity:
                        masterObj.severity = vulnerabilityObj.severity
                    else: 
                        masterObj.severity= 'NE'

                    
                    if  vulnerabilityObj.due_date:
                        masterObj.due_date = vulnerabilityObj.due_date
                    #else: 
                    #    masterObj.scan_result_id= 'NE'
                    
                    if  vulnerabilityObj.last_detected:
                        masterObj.last_detected = vulnerabilityObj.last_detected
                    else: 
                        masterObj.last_detected= 'NE'
                    
                    if  vulnerabilityObj.overall_status:
                        masterObj.overall_status = vulnerabilityObj.overall_status
                    else: 
                        masterObj.overall_status= 'NE'
                    
                    if  vulnerabilityObj.qualys_vuln_status:
                        masterObj.qualys_vuln_status = vulnerabilityObj.qualys_vuln_status
                    else: 
                        masterObj.qualys_vuln_status= 'NE'

                    if  vulnerabilityObj.exception_requests:
                        masterObj.all_exceptions = vulnerabilityObj.exception_requests
                    else: 
                        masterObj.exception_requests= 'NE'
                    
                    if  vulnerabilityObj.cve_id:
                        masterObj.cve_id = vulnerabilityObj.cve_id
                    else: 
                        masterObj.cve_id= 'NE'
                    
                    if  vulnerabilityObj.technical_contact:
                        masterObj.technical_contact = vulnerabilityObj.technical_contact
                    else: 
                        masterObj.cvetechnical_contact_id= 'NE'


                    masterObj.creation_date= current_time
                    masterObj.modification_date= current_time
                    masterObj.created_by= "Sync"
                    masterObj.modified_by= "Sync"
                    
                    '''
                    cveId = VULNERABILITY_MANAGEDBY.query.with_entities(VULNERABILITY_MANAGEDBY.cve_id).filter_by(scan_result_id=vulnerabilityObj.scan_result_id).first()
                    if cveId:
                        if cveId[0]:
                            masterObj.cve_id= cveId[0]
                        else:
                            masterObj.cve_id= 'NE'

                    else:
                        masterObj.cve_id= 'NE'
                    '''
                    # inProgressExemptions = VULNERABILITY_INPROGRESS.query.with_entities(VULNERABILITY_INPROGRESS.exception_requests).filter_by(scan_result_id=vulnerabilityObj.scan_result_id).first()
                    # if inProgressExemptions:
                    #     if inProgressExemptions[0]:
                    #         masterObj.inprogress_exceptions= inProgressExemptions[0]
                    #     else:
                    #         masterObj.inprogress_exceptions= 'NE'

                    # else:
                    #     masterObj.inprogress_exceptions= 'NE'
                    
                    inProgressDevice = Device_Table.query.with_entities(Device_Table.pn_code, Device_Table.hw_eos_date, Device_Table.vuln_fix_plan_status, Device_Table.vuln_ops_severity).filter_by(device_id=vulnerabilityObj.device_name).first()
                    if inProgressDevice:
                        
                        if inProgressDevice[0]:
                            masterObj.pn_code= inProgressDevice[0]
                        else:
                            masterObj.pn_code= 'NE'
                        
                        if inProgressDevice[1]:
                            masterObj.hw_eos_date= inProgressDevice[1]
                        else:
                            pass
                            #masterObj.hw_eos_date= 'NE'
                        
                        if inProgressDevice[2]:
                            masterObj.vuln_fix_plan_status= inProgressDevice[2]
                        else:
                            masterObj.vuln_fix_plan_status= 'NE'

                        if inProgressDevice[3]:
                            masterObj.vuln_ops_severity= inProgressDevice[3]
                        else:
                            masterObj.vuln_ops_severity= 'NE'
                            
                    else:
                        masterObj.pn_code= 'NE'
                        #masterObj.hw_eos_date= 'NE'
                        masterObj.vuln_fix_plan_status= 'NE'
                        masterObj.vuln_ops_severity= 'NE'

                    InsertData(masterObj)

                   
                    if 'closed' not in masterObj.overall_status.lower() and masterObj.vuln_fix_plan_status=="No Plan":
                        isNoPlanExists = VULNERABILITY_SOC_NO_PLAN.query.with_entities(VULNERABILITY_SOC_NO_PLAN.device_ip).filter_by(device_ip=masterObj.device_ip).filter_by(creation_date=masterObj.creation_date).first()
                        if not isNoPlanExists:
                            noPlanObj.device_name= masterObj.device_name
                            noPlanObj.device_ip= masterObj.device_ip
                            noPlanObj.pn_code= masterObj.pn_code
                            noPlanObj.creation_date= masterObj.creation_date
                            noPlanObj.modification_date= masterObj.modification_date
                            noPlanObj.created_by= masterObj.created_by
                            noPlanObj.modified_by= masterObj.modified_by
                            InsertData(noPlanObj)
                            print("Inserted SOC Vulnerability No Plan Device", file=sys.stderr)

                    if 'closed' not in masterObj.overall_status.lower() and masterObj.pn_code=="NE":
                        isNotFoundExists = VULNERABILITY_SOC_NOT_FOUND.query.with_entities(VULNERABILITY_SOC_NOT_FOUND.device_ip).filter_by(device_ip=masterObj.device_ip).filter_by(creation_date=masterObj.creation_date).first()
                        if not isNotFoundExists:
                            ipamObj = SOC_IPAM_TABLE.query.with_entities(SOC_IPAM_TABLE.device_id).filter_by(ip_address=masterObj.device_ip).first()
                            if ipamObj:
                                notFoundObj.correct_device_id= ipamObj[0]
                            else:
                                notFoundObj.correct_device_id= "Not Found"

                            notFoundObj.device_name= masterObj.device_name
                            notFoundObj.device_ip= masterObj.device_ip
                            
                            notFoundObj.creation_date= masterObj.creation_date
                            notFoundObj.modification_date= masterObj.modification_date
                            notFoundObj.created_by= masterObj.created_by
                            notFoundObj.modified_by= masterObj.modified_by
                            InsertData(notFoundObj)
                            print("Inserted SOC Vulnerability Not Found Device", file=sys.stderr)
                            
                except Exception as e:
                        print(f"Error Occured in  Population of Master Table {e}", file=sys.stderr)
    vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "SOC-VULN-TO-MASTER").first()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        vulnStatus.script = "SOC-VULN-TO-MASTER"
        vulnStatus.status = "Completed"
        vulnStatus.creation_date= current_time
        vulnStatus.modification_date= current_time
        db.session.add(vulnStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)
    
    print("Finished Population of SOC Master", file=sys.stderr)

    return jsonify({'response': "success","code":"200"})


@app.route("/getAllSocVulnerabilityMasterByDate", methods = ['POST'])
@token_required
def GetAllSocVulnerabilityMasterByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityMasterObjList=[]
        #vulnerabilityMasterObjs = VULNERABILITY_SOC_MASTER.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityMasterObjs =  db.session.execute(f"SELECT * FROM vulnerability_soc_master WHERE creation_date = '{current_time}'")
        try:
            for vulnerabilityMasterObj in vulnerabilityMasterObjs:

                vulnerabilityMasterDataDict= {}
                vulnerabilityMasterDataDict['vulnerability_master_id']=vulnerabilityMasterObj[0]
                vulnerabilityMasterDataDict['scan_result_id'] = vulnerabilityMasterObj[1]
                vulnerabilityMasterDataDict['device_ip'] = vulnerabilityMasterObj[2]
                vulnerabilityMasterDataDict['device_name'] = vulnerabilityMasterObj[3]
                vulnerabilityMasterDataDict['severity'] = vulnerabilityMasterObj[4]
                vulnerabilityMasterDataDict['cve_id'] = vulnerabilityMasterObj[5]
                
                if vulnerabilityMasterObj[6]:
                    vulnerabilityMasterDataDict['due_date'] = FormatDate(vulnerabilityMasterObj[6])
                if vulnerabilityMasterObj[7]:
                    vulnerabilityMasterDataDict['last_detected'] =FormatDate( vulnerabilityMasterObj[7])
                
                vulnerabilityMasterDataDict['overall_status'] = vulnerabilityMasterObj[8]
                vulnerabilityMasterDataDict['qualys_vuln_status'] = vulnerabilityMasterObj[9]
                
                
                #vulnerabilityMasterDataDict['inprogress_exceptions'] = vulnerabilityMasterObj[10]
                vulnerabilityMasterDataDict['all_exceptions'] = vulnerabilityMasterObj[10]
                
                vulnerabilityMasterDataDict['pn_code'] = vulnerabilityMasterObj[11]
                
                if vulnerabilityMasterObj[12]:
                    vulnerabilityMasterDataDict['hw_eos_date'] = FormatDate(vulnerabilityMasterObj[12])
                
                vulnerabilityMasterDataDict['vuln_fix_plan_status'] = vulnerabilityMasterObj[13]          
                vulnerabilityMasterDataDict['vuln_ops_severity'] = vulnerabilityMasterObj[14]
                vulnerabilityMasterDataDict['technical_contact'] = vulnerabilityMasterObj[15]
                
                
                vulnerabilityMasterDataDict['creation_date'] = FormatDate(vulnerabilityMasterObj[16])
                vulnerabilityMasterDataDict['modification_date'] = FormatDate(vulnerabilityMasterObj[17])
                vulnerabilityMasterDataDict['created_by'] = vulnerabilityMasterObj[18]
                vulnerabilityMasterDataDict['modified_by'] = vulnerabilityMasterObj[19]
                
                vulnerabilityMasterObjList.append(vulnerabilityMasterDataDict)

            #print("%%%"+ vulnerabilityMasterObjList, file=sys.stderr)
            content = gzip.compress(json.dumps(vulnerabilityMasterObjList).encode('utf8'), 5)
            response = make_response(content)
            response.headers['Content-length'] = len(content)
            response.headers['Content-Encoding'] = 'gzip'
            return response
        except Exception as e:
            print(f"Error Occured in Getting Master Vulnerabilities {e}", file=sys.stderr)
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllSocVulnerabilityMaster", methods = ['GET'])
@token_required
def GetAllSocVulnerabilityMaster(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityMasterObjList=[]
        
        vulnerabilityMasterObjs =  db.session.execute(f'SELECT * FROM vulnerability_soc_master WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_soc_master)')

        for vulnerabilityMasterObj in vulnerabilityMasterObjs:

            vulnerabilityMasterDataDict= {}
            vulnerabilityMasterDataDict['vulnerability_master_id']=vulnerabilityMasterObj[0]
            vulnerabilityMasterDataDict['scan_result_id'] = vulnerabilityMasterObj[1]
            vulnerabilityMasterDataDict['device_ip'] = vulnerabilityMasterObj[2]
            vulnerabilityMasterDataDict['device_name'] = vulnerabilityMasterObj[3]
            vulnerabilityMasterDataDict['severity'] = vulnerabilityMasterObj[4]
            vulnerabilityMasterDataDict['cve_id'] = vulnerabilityMasterObj[5]
            
            if vulnerabilityMasterObj[6]:
                vulnerabilityMasterDataDict['due_date'] = FormatDate(vulnerabilityMasterObj[6])
            if vulnerabilityMasterObj[7]:
                vulnerabilityMasterDataDict['last_detected'] =FormatDate( vulnerabilityMasterObj[7])
            
            vulnerabilityMasterDataDict['overall_status'] = vulnerabilityMasterObj[8]
            vulnerabilityMasterDataDict['qualys_vuln_status'] = vulnerabilityMasterObj[9]
            

            
            #vulnerabilityMasterDataDict['inprogress_exceptions'] = vulnerabilityMasterObj[10]
            vulnerabilityMasterDataDict['all_exceptions'] = vulnerabilityMasterObj[10]
            
            vulnerabilityMasterDataDict['pn_code'] = vulnerabilityMasterObj[11]
            
            if vulnerabilityMasterObj[12]:
                vulnerabilityMasterDataDict['hw_eos_date'] = FormatDate(vulnerabilityMasterObj[12])
            
            
            
            vulnerabilityMasterDataDict['vuln_fix_plan_status'] = vulnerabilityMasterObj[13]          
            vulnerabilityMasterDataDict['vuln_ops_severity'] = vulnerabilityMasterObj[14]
            vulnerabilityMasterDataDict['technical_contact'] = vulnerabilityMasterObj[15]
            
            
            vulnerabilityMasterDataDict['creation_date'] = FormatDate(vulnerabilityMasterObj[16])
            vulnerabilityMasterDataDict['modification_date'] = FormatDate(vulnerabilityMasterObj[17])
            vulnerabilityMasterDataDict['created_by'] = vulnerabilityMasterObj[18]
            vulnerabilityMasterDataDict['modified_by'] = vulnerabilityMasterObj[19]
            
            
            vulnerabilityMasterObjList.append(vulnerabilityMasterDataDict)

        content = gzip.compress(json.dumps(vulnerabilityMasterObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllSocVulnerabilityMasterDates",methods=['GET'])
@token_required
def GetAllSocVulnerabilityMasterDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_soc_master  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/editSocVulnerabilityMaster", methods = ['POST'])
@token_required
def EditSocVulnerabilityMaster(user_data):  
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityMasterObj = request.get_json()
        time= datetime.now(tz)
        #print(postData,file=sys.stderr)

        #for vulnerabilityMasterObj in postData:
        try:
            vulnerabilityMaster = VULNERABILITY_SOC_MASTER()
            if 'scan_result_id' in vulnerabilityMasterObj and 'vulnerability_master_id' in vulnerabilityMasterObj:
                vulnerabilityMasterId = VULNERABILITY_SOC_MASTER.query.with_entities(VULNERABILITY_SOC_MASTER.vulnerability_master_id).filter_by(vulnerability_master_id=vulnerabilityMasterObj['vulnerability_master_id']).first()
                
                if vulnerabilityMasterId is not None:
                    vulnerabilityMaster.vulnerability_master_id= vulnerabilityMasterId[0]
                    
                    if 'device_ip' in vulnerabilityMasterObj:
                        vulnerabilityMaster.device_ip = vulnerabilityMasterObj['device_ip']
                    else:
                        vulnerabilityMaster.device_ip = 'NE'

                    if 'device_name' in vulnerabilityMasterObj:
                        vulnerabilityMaster.device_name = vulnerabilityMasterObj['device_name']
                    else:
                        vulnerabilityMaster.device_name = 'NE'

                    if 'severity' in vulnerabilityMasterObj:
                        if  vulnerabilityMasterObj['severity']:
                            vulnerabilityMaster.severity = vulnerabilityMasterObj['severity']
                        else:
                            vulnerabilityMaster.severity = 'NE'

                        
                    if 'due_date' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['due_date']:
                            vulnerabilityMaster.due_date = FormatStringDate(vulnerabilityMasterObj['due_date'])
                    #else:
                    #    vulnerabilityMaster.due_date = ''

                    
                    if 'last_detected' in vulnerabilityMasterObj:
                        vulnerabilityMaster.last_detected = FormatStringDate(vulnerabilityMasterObj['last_detected'])
                    #else:
                    #    vulnerabilityMaster.last_detected = 'NE'

                    if 'overall_status' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['overall_status']:
                            vulnerabilityMaster.overall_status = vulnerabilityMasterObj['overall_status']
                        else:
                            vulnerabilityMaster.overall_status = 'NE'

                    if 'qualys_vuln_status' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['qualys_vuln_status']:
                            vulnerabilityMaster.qualys_vuln_status =  vulnerabilityMasterObj['qualys_vuln_status']
                        else:
                            vulnerabilityMaster.qualys_vuln_status = 'NE'

                    if 'in_progress_exception' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['in_progress_exception']:
                            vulnerabilityMaster.in_progress_exception = vulnerabilityMasterObj['in_progress_exception']
                        else:
                            vulnerabilityMaster.in_progress_exception = 'NE'

                    if 'cve_id' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['cve_id']:
                            vulnerabilityMaster.cve_id = vulnerabilityMasterObj['cve_id']
                        else:
                            vulnerabilityMaster.cve_id = 'NE'


                    if 'all_exceptions' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['all_exceptions']:
                            vulnerabilityMaster.all_exceptions = vulnerabilityMasterObj['all_exceptions']
                        else:
                            vulnerabilityMaster.all_exceptions = 'NE'

                    if 'pn_code' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['pn_code']:
                            vulnerabilityMaster.pn_code = vulnerabilityMasterObj['pn_code']
                        else:
                            vulnerabilityMaster.pn_code = 'NE'
                    
                    if 'technical_contact' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['technical_contact']:
                            vulnerabilityMaster.technical_contact = vulnerabilityMasterObj['technical_contact']
                        else:
                            vulnerabilityMaster.technical_contact = 'NE'

                    if 'hw_eos_date' in vulnerabilityMasterObj:
                        vulnerabilityMaster.hw_eos_date = FormatStringDate(vulnerabilityMasterObj['hw_eos_date'])
                    #else:
                    #    vulnerabilityMaster.hw_eos_date = 'NE'

                    if 'vuln_fix_plan_status' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['vuln_fix_plan_status']:
                            vulnerabilityMaster.vuln_fix_plan_status = vulnerabilityMasterObj['vuln_fix_plan_status']
                        else:
                            vulnerabilityMaster.vuln_fix_plan_status = 'NE'

                    if 'vuln_ops_severity' in vulnerabilityMasterObj:
                        if vulnerabilityMasterObj['vuln_ops_severity']:
                            vulnerabilityMaster.vuln_ops_severity = vulnerabilityMasterObj['vuln_ops_severity']
                        else:
                            vulnerabilityMaster.vuln_ops_severity = 'NE'

                    #vulnerabilityMaster.creation_date= time
                    vulnerabilityMaster.modification_date= time
                    vulnerabilityMaster.modified_by= user_data['user_id']
                
                    
                    UpdateData(vulnerabilityMaster)
                else:
                    return jsonify({'response': "Vulnerability Id can not be found in Table"}), 500  
            else:
                return jsonify({'response': "Vulnerability Id Missing"}), 500  
            return jsonify({'response': "success","code":"200"})
        except Exception as e:
            traceback.print_exc()
            print(f"Error Occured in Adding Vulnerability Master {vulnerabilityMasterObj['scan_result_id']}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/syncSocVulnerabilityMasterToDevices", methods = ['GET'])
@token_required
def syncSocVulnerabilityMasterToDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        try:
            syncSocVulnerabilityMasterToDevicesFunc(user_data)
        
        except Exception as e:
            print(f"Error Occured in  Population of Devices {e}", file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401        

def syncSocVulnerabilityMasterToDevicesFunc(user_data):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "SOC-VULN-TO-DEVICES").first()
    try:
        vulnStatus.script = "SOC-VULN-TO-DEVICES"
        vulnStatus.status = "Running"
        vulnStatus.creation_date= current_time
        vulnStatus.modification_date= current_time
        db.session.add(vulnStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)
    
    try:
        tableObjs=[]
        date=""
        masterDateObj = db.session.execute('SELECT max(creation_date) FROM vulnerability_soc_master')
        for row in masterDateObj:
            date=row[0]

        for table in range(2):

            if table==0:
                print("Populating SOC-NET Vulnerabilities in Seed", file=sys.stderr)
                tableObjs = Seed.query.filter(or_(Seed.cisco_domain=='SOC-NET', Seed.cisco_domain=='SOC-SYS')).all()
            if table==1:
                print("Populating SOC-NET Vulnerabilities in Devices", file=sys.stderr)
                tableObjs = Device_Table.query.filter(or_(Device_Table.cisco_domain=='SOC-NET', Device_Table.cisco_domain=='SOC-SYS')).all()
            
            for obj in tableObjs:
                try:
                    deviceId = obj.device_id
                    severityObjs= VULNERABILITY_SOC_MASTER.query.with_entities(VULNERABILITY_SOC_MASTER.severity).filter_by(device_name=deviceId).filter_by(creation_date=date).filter(VULNERABILITY_SOC_MASTER.overall_status.notlike('Closed%')).all()
                    if severityObjs:
                        uniqueSeverity= set()
                        for master in severityObjs:
                            uniqueSeverity.add(master[0])
                        vulnSeverity=""
                        for severity in uniqueSeverity:
                            if severity.lower()=="medium":
                                vulnSeverity+="SL3,"
                            if severity.lower()=="high":
                                vulnSeverity+="SL4,"
                            if severity.lower()=="critical":
                                vulnSeverity+="SL5," 
                        vulnSeverity= vulnSeverity[:-1]
                        obj.vulnerability_severity= vulnSeverity
                        UpdateData(obj)
                        print(f"Updated Vuln Severity for Device {obj.device_id} {vulnSeverity}", file=sys.stderr)
                    else:
                        obj.vulnerability_severity= ""
                        UpdateData(obj)
                        print(f"Reset Vuln Severity for Device {obj.device_id}", file=sys.stderr)

                except Exception  as e:
                    print(f"Exception Occured in Syncing Vulnerabilities {e}")
        
        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "SOC-VULN-TO-DEVICES").first()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            vulnStatus.script = "SOC-VULN-TO-DEVICES"
            vulnStatus.status = "Completed"
            vulnStatus.creation_date= current_time
            vulnStatus.modification_date= current_time
            db.session.add(vulnStatus)
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"Error while updating script status {e}", file=sys.stderr)

        print("Finished SOC Vulnerability Sync To Device ", file=sys.stderr)
    except Exception  as e:
        print(f"Exception Occured in Syncing Vulnerabilities {e}") 

@app.route("/getSocVulnerabilitySyncTOMasterStatus", methods = ['GET'])
@token_required
def GetSocVulnerabilitySyncTOMasterStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        f5={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "SOC-VULN-TO-MASTER").first()
        if vulnStatus:
            script_status= vulnStatus.status
            script_modifiation_date= str(vulnStatus.modification_date)
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


@app.route("/getSocVulnerabilitySyncToDevicesStatus", methods = ['GET'])
#@token_required
def GetSocVulnerabilitySyncTODevicesStatus():
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        f5={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "SOC-VULN-TO-DEVICES").first()
        if vulnStatus:
            script_status= vulnStatus.status
            script_modifiation_date= str(vulnStatus.modification_date)
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


@app.route("/getSocVulnerabilityImportStatus", methods = ['GET'])
@token_required
def GetSocVulnerabilityImportStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        f5={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        vulnStatus = INVENTORY_SCRIPTS_STATUS.query.filter(INVENTORY_SCRIPTS_STATUS.script== "SOC-VULN-ARCHER").first()
        if vulnStatus:
            script_status= vulnStatus.status
            script_modifiation_date= str(vulnStatus.modification_date)
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


### No Plan

@app.route("/getAllSocVulnerabilityNoPlan", methods = ['GET'])
@token_required
def GetAllSocVulnerabilityNoPlan(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityNoPlanObjList=[]
        
        vulnerabilityNoPlanObjs =  db.session.execute(f'SELECT * FROM vulnerability_soc_no_plan WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_soc_no_plan)')

        for vulnerabilityNoPlanObj in vulnerabilityNoPlanObjs:

            vulnerabilityNoPlanDataDict= {}
            vulnerabilityNoPlanDataDict['vulnerability_no_plan_id']=vulnerabilityNoPlanObj[0]
            vulnerabilityNoPlanDataDict['device_ip'] = vulnerabilityNoPlanObj[1]
            vulnerabilityNoPlanDataDict['device_name'] = vulnerabilityNoPlanObj[2]
            vulnerabilityNoPlanDataDict['pn_code'] = vulnerabilityNoPlanObj[3]
             
            vulnerabilityNoPlanDataDict['creation_date'] = FormatDate(vulnerabilityNoPlanObj[4])
            vulnerabilityNoPlanDataDict['modification_date'] = FormatDate(vulnerabilityNoPlanObj[5])
            vulnerabilityNoPlanDataDict['created_by'] = vulnerabilityNoPlanObj[6]
            vulnerabilityNoPlanDataDict['modified_by'] = vulnerabilityNoPlanObj[7]
            
            
            vulnerabilityNoPlanObjList.append(vulnerabilityNoPlanDataDict)

        content = gzip.compress(json.dumps(vulnerabilityNoPlanObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllSocVulnerabilityNoPlanDates",methods=['GET'])
@token_required
def GetAllSocVulnerabilityNoPlanDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_soc_no_plan  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllSocVulnerabilityNoPlanByDate", methods = ['POST'])
@token_required
def GetAllSocVulnerabilityNoPlanByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityNoPlanObjList=[]
        #vulnerabilityNoPlanObjs = VULNERABILITY_SOC_MASTER.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityNoPlanObjs =  db.session.execute(f"SELECT * FROM vulnerability_soc_no_plan WHERE creation_date = '{current_time}'")
        try:
            for vulnerabilityNoPlanObj in vulnerabilityNoPlanObjs:

                vulnerabilityNoPlanDataDict= {}
                vulnerabilityNoPlanDataDict['vulnerability_no_plan_id']=vulnerabilityNoPlanObj[0]
                vulnerabilityNoPlanDataDict['device_ip'] = vulnerabilityNoPlanObj[1]
                vulnerabilityNoPlanDataDict['device_name'] = vulnerabilityNoPlanObj[2]
                vulnerabilityNoPlanDataDict['pn_code'] = vulnerabilityNoPlanObj[3]
                
                vulnerabilityNoPlanDataDict['creation_date'] = FormatDate(vulnerabilityNoPlanObj[4])
                vulnerabilityNoPlanDataDict['modification_date'] = FormatDate(vulnerabilityNoPlanObj[5])
                vulnerabilityNoPlanDataDict['created_by'] = vulnerabilityNoPlanObj[6]
                vulnerabilityNoPlanDataDict['modified_by'] = vulnerabilityNoPlanObj[7]
                
                vulnerabilityNoPlanObjList.append(vulnerabilityNoPlanDataDict)

            #print("%%%"+ vulnerabilityNoPlanObjList, file=sys.stderr)
            content = gzip.compress(json.dumps(vulnerabilityNoPlanObjList).encode('utf8'), 5)
            response = make_response(content)
            response.headers['Content-length'] = len(content)
            response.headers['Content-Encoding'] = 'gzip'
            return response
        except Exception as e:
            print(f"Error Occured in Getting NoPlan Vulnerabilities {e}", file=sys.stderr)
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

#### Not Found

@app.route("/getAllSocVulnerabilityNotFound", methods = ['GET'])
@token_required
def GetAllSocVulnerabilityNotFound(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityNotFoundObjList=[]
        
        vulnerabilityNotFoundObjs =  db.session.execute(f'SELECT * FROM vulnerability_soc_not_found WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_soc_not_found)')

        for vulnerabilityNotFoundObj in vulnerabilityNotFoundObjs:

            vulnerabilityNotFoundDataDict= {}
            vulnerabilityNotFoundDataDict['vulnerability_not_found_id']=vulnerabilityNotFoundObj[0]
            vulnerabilityNotFoundDataDict['device_ip'] = vulnerabilityNotFoundObj[1]
            vulnerabilityNotFoundDataDict['device_name'] = vulnerabilityNotFoundObj[2]
            vulnerabilityNotFoundDataDict['correct_device_id'] = vulnerabilityNotFoundObj[3]
             
            vulnerabilityNotFoundDataDict['creation_date'] = FormatDate(vulnerabilityNotFoundObj[4])
            vulnerabilityNotFoundDataDict['modification_date'] = FormatDate(vulnerabilityNotFoundObj[5])
            vulnerabilityNotFoundDataDict['created_by'] = vulnerabilityNotFoundObj[6]
            vulnerabilityNotFoundDataDict['modified_by'] = vulnerabilityNotFoundObj[7]
            
            
            vulnerabilityNotFoundObjList.append(vulnerabilityNotFoundDataDict)

        content = gzip.compress(json.dumps(vulnerabilityNotFoundObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllSocVulnerabilityNotFoundDates",methods=['GET'])
@token_required
def GetAllSocVulnerabilityNotFoundDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from vulnerability_soc_not_found  ORDER BY creation_date DESC;"
        
        result =  db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllSocVulnerabilityNotFoundByDate", methods = ['POST'])
@token_required
def GetAllSocVulnerabilityNotFoundByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnerabilityNotFoundObjList=[]
        #vulnerabilityNotFoundObjs = VULNERABILITY_SOC_MASTER.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        vulnerabilityNotFoundObjs =  db.session.execute(f"SELECT * FROM vulnerability_soc_not_found WHERE creation_date = '{current_time}'")
        try:
            for vulnerabilityNotFoundObj in vulnerabilityNotFoundObjs:

                vulnerabilityNotFoundDataDict= {}
                vulnerabilityNotFoundDataDict['vulnerability_not_found_id']=vulnerabilityNotFoundObj[0]
                vulnerabilityNotFoundDataDict['device_ip'] = vulnerabilityNotFoundObj[1]
                vulnerabilityNotFoundDataDict['device_name'] = vulnerabilityNotFoundObj[2]
                vulnerabilityNotFoundDataDict['correct_device_id'] = vulnerabilityNotFoundObj[3]
            
                vulnerabilityNotFoundDataDict['creation_date'] = FormatDate(vulnerabilityNotFoundObj[4])
                vulnerabilityNotFoundDataDict['modification_date'] = FormatDate(vulnerabilityNotFoundObj[5])
                vulnerabilityNotFoundDataDict['created_by'] = vulnerabilityNotFoundObj[6]
                vulnerabilityNotFoundDataDict['modified_by'] = vulnerabilityNotFoundObj[7]
                
                vulnerabilityNotFoundObjList.append(vulnerabilityNotFoundDataDict)

            #print("%%%"+ vulnerabilityNotFoundObjList, file=sys.stderr)
            content = gzip.compress(json.dumps(vulnerabilityNotFoundObjList).encode('utf8'), 5)
            response = make_response(content)
            response.headers['Content-length'] = len(content)
            response.headers['Content-Encoding'] = 'gzip'
            return response
        except Exception as e:
            print(f"Error Occured in Getting NotFound Vulnerabilities {e}", file=sys.stderr)
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getSocVulnerabilityTechnicalContact", methods = ['GET'])
@token_required
def GetSocVulnerabilityTechnicalContact(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnList=[]
        vulnList= GetSocVulnerabilityTechnicalContactFunc()
        content = gzip.compress(json.dumps(vulnList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def GetSocVulnerabilityTechnicalContactFunc():
    vulnList=[]
    vulnList.append('All')
    try:
        vulnObj =  db.session.execute(f'SELECT distinct(technical_contact) FROM vulnerability_soc_master WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_soc_master)')

        for vuln in vulnObj:
            if vuln[0] is not None:
                vulnList.append(vuln[0])

        return vulnList
    except Exception as e:
        return vulnList
        print("Error in getting distinct Technical Contact")


@app.route("/getSocVulnerabilityOverallStatus", methods = ['GET'])
@token_required
def GetSocVulnerabilityOverallStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        vulnList=[]
        
        vulnList= GetSocVulnerabilityOverallStatusFunc()
        content = gzip.compress(json.dumps(vulnList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
        
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def GetSocVulnerabilityOverallStatusFunc():
    vulnList=[]
    vulnList.append('All')
    try:
        vulnObj =  db.session.execute(f"SELECT distinct(overall_status) FROM vulnerability_soc_master WHERE OVERALL_STATUS NOT LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_soc_master)")

        for vuln in vulnObj:
            if vuln[0] is not None:
                vulnList.append(vuln[0])
        return vulnList
    except Exception as e:
            return vulnList
            print("Error in getting distinct Technical Contact")

