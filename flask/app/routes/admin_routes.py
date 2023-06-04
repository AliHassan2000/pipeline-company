import gzip
import re
import traceback
from unittest import result
from app import app,db, tz
from app.models.inventory_models import Phy_Table, Rack_Table, Device_Table, Board_Table, Subboard_Table, SFP_Table, License_Table, Seed, SNTC_Table, PnCode_SNAP_Table, CDN_Table, POWER_FEEDS_TABLE,Rebd_Table,Pos_Table, FUNCTIONS_TABLE, DOMAINS_TABLE
from flask_jsonpify import jsonify
import pandas as pd
import json, sys, time
from datetime import date, datetime
from flask import request, make_response, Response,session
from app.middleware import token_required
from collections import namedtuple


def UpdateData(obj):
    #add data to db
    #print(obj, file=sys.stderr)
    try:
        # db.session.flush()
        db.session.execute("SET FOREIGN_KEY_CHECKS=0;") 
        db.session.commit()
        db.session.merge(obj)
        db.session.commit()
        db.session.execute("SET FOREIGN_KEY_CHECKS=1;") 
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        db.session.execute("SET FOREIGN_KEY_CHECKS=1;") 
        db.session.commit()
        #print(f"Something else went wrong during Database Update {e}", file=sys.stderr)
        
        return None
    
def UpdateData2(obj):
    try:
        db.session.execute("SET FOREIGN_KEY_CHECKS=0;")
        db.session.commit()

        db.session.merge(obj)
        db.session.commit()

        db.session.execute("SET FOREIGN_KEY_CHECKS=1;")
        db.session.commit()

        return True

    except Exception as e:
        db.session.rollback()
        db.session.execute("SET FOREIGN_KEY_CHECKS=1;")
        db.session.commit()
        return None


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



@app.route("/editDeviceId", methods = ['POST'])
@token_required
def EditDeviceId(user_data): 
    
    
    oldId= newId="" 
    deviceObj = request.get_json()
    if "old_device_id" in deviceObj:
        oldId= deviceObj['old_device_id']
    if "new_device_id" in deviceObj:
        newId= deviceObj['new_device_id']

    if oldId and newId:
        newInSeed= Seed.query.with_entities(Seed.device_id).filter_by(device_id=newId).first()
        newInDevice= Device_Table.query.with_entities(Device_Table.device_id).filter_by(device_id=newId).first()

        if newInSeed and newInDevice:
            print("New Device ID Already Exists in both Seed and Table", file=sys.stderr)
            return jsonify({'response': "New Device ID Already Exists in both Seed and Table"}), 500
            
        
        if newInSeed:
            print("New Device ID Already Exists in Seed", file=sys.stderr)
            #return jsonify({'response': "New Device ID Already Exists in Seed"}), 500
            return jsonify({'response': "New Device ID Already Exists in Seed","code":"500"})
        
        if newInDevice:
            print("New Device ID Already Exists in Device Table", file=sys.stderr)
            #return jsonify({'response': "New Device ID Already Exists in Device"}), 500
            return jsonify({'response': "New Device ID Already Exists in Device Table","code":"500"})
        try:
            message="Device Id successfully updated in"
            #db.session.execute("SET FOREIGN_KEY_CHECKS=0")

            obj = Seed.query.filter(Seed.device_id == oldId).first()

            if(obj):
                try:
                    obj.device_id = newId
                    obj.modified_by= user_data["user_id"]
                  
                    UpdateData(obj)
                    message+= " Seed"
                
                except Exception as e:
                  
                    print(f"Failed to update Device ID in Device Table {e}", file=sys.stderr)

            #db.session.commit()
            
            '''
            try:
                db.session.execute(f"update seed_table set device_id = '{newId}' where device_id='{oldId}';")
                db.session.commit()
                #result= db.session.execute(f"SELECT * FROM seed_table WHERE device_id ='{newId}';")
                seedObjs = Seed.query.with_entities(Seed).filter(Seed.device_id != oldId).all()
                if seedObjs:
                    for obj in result:
                        obj.device_id= newId
                        UpdateData(obj)
                        message+= " Seed"
                        break
            except Exception as e:
                print(f"Failed to update Device ID in Seed {e}", file=sys.stderr)
            '''

            obj = Device_Table.query.filter(Device_Table.device_id == oldId).first()

            if(obj):
                try:
                    obj.device_id = newId
                    obj.modified_by= user_data["user_id"]
                 
                    UpdateData(obj)
                    message+= ", Device Tables"
                
                except Exception as e:
                  
                    print(f"Failed to update Device ID in Device Table {e}", file=sys.stderr)

            '''
            try:
                db.session.execute(f"update device_table set device_id = '{newId}' where device_id='{oldId}';")
                db.session.commit()
                result= db.session.execute(f"SELECT * FROM device_table where device_id='{newId}';")
                
                for row in result:
                    if row[0]:
                        message+= ", Device Tables"
                    break
            except Exception as e:
                print(f"Failed to update Device ID in Device Table {e}", file=sys.stderr)
            '''
            obj = Board_Table.query.filter(Board_Table.device_id == oldId).all()

            if(obj):
                for index, board in enumerate(obj):
                    try:
                        board.device_id = newId
                        board.modified_by= user_data["user_id"]
                        UpdateData(obj)
                        if index==0:
                            message+= ", Boards Tables"
                    
                    except Exception as e:
                    
                        print(f"Failed to update Device ID in Device Table {e}", file=sys.stderr)

            '''
            try:
                db.session.execute(f"update board_table set device_id = '{newId}' where device_id='{oldId}';")
                db.session.commit()
                result= db.session.execute(f"SELECT *  FROM board_table where device_id='{newId}';")
                for row in result:
                    if row[0]:
                        message+= ", Boards Tables"
                    break
            except Exception as e:
                print(f"Failed to update Device ID in Boards Table {e}", file=sys.stderr)
            '''

            obj = Subboard_Table.query.filter(Subboard_Table.device_id == oldId).all()

            if(obj):
                for index, subboard in enumerate(obj):
                    try:
                        subboard.device_id = newId
                        subboard.modified_by= user_data["user_id"]
                    
                        UpdateData(obj)
                        if index==0:
                            message+= ", Subboards Tables"
                    
                    except Exception as e:
                        
                        print(f"Failed to update Device ID in Device Table {e}", file=sys.stderr)


            '''
            try:
                db.session.execute(f"update subboard_table set device_id = '{newId}' where device_id='{oldId}';")
                db.session.commit()
                result= db.session.execute(f"SELECT * FROM subboard_table where device_id='{oldId}';")
                for row in result:
                    if row[0]:
                        message+= ", Subboards Tables"
                    break
                    
            except Exception as e:
                print(f"Failed to update Device ID in Subboard Table {e}", file=sys.stderr)
            '''
            obj = SFP_Table.query.filter(SFP_Table.device_id == oldId).all()

            if(obj):
                for index, sfp in enumerate(obj):
                    try:
                        sfp.device_id = newId
                        sfp.modified_by= user_data["user_id"]
                        #db.session.flush()
                        #db.session.commit()
                        #print("updated in device", file=sys.stderr)
                        UpdateData(sfp)
                        if index==0:
                            message+= ", SFPS Tables"
                    
                    except Exception as e:
                        #db.session.flush()
                        #db.session.execute("SET FOREIGN_KEY_CHECKS=0")
                        print(f"Failed to update Device ID in Device Table {e}", file=sys.stderr)
            '''
            try:
                db.session.execute(f"update sfp_table set device_id = '{newId}' where device_id='{oldId}';")
                db.session.commit()
                result= db.session.execute(f"SELECT * FROM sfp_table where device_id='{newId}';")
                for row in result:
                    if row[0]:
                        message+= ", SFPS Tables"
                    break
            except Exception as e:
                print(f"Failed to update Device ID in SFPS Table {e}", file=sys.stderr)
            '''
            obj = POWER_FEEDS_TABLE.query.filter(POWER_FEEDS_TABLE.device_id == oldId).first()

            if(obj):
                try:
                    obj.device_id = newId
                    #db.session.flush()
                    obj.modified_by= user_data["user_id"]
                    #db.session.commit()
                    #print("updated in device", file=sys.stderr)
                    UpdateData(obj)
                    message+= ", Power Feed Tables"
                
                except Exception as e:
                    #db.session.flush()
                    #db.session.execute("SET FOREIGN_KEY_CHECKS=0")
                    print(f"Failed to update Device ID in Device Table {e}", file=sys.stderr)

            '''
            try:
                db.session.execute(f"update power_feeds_table set device_id = '{newId}' where device_id='{oldId}';")
                db.session.commit()
                result= db.session.execute(f"SELECT * FROM  power_feeds_table where device_id='{newId}';")
                for row in result:
                    if row[0]:
                        message+= ", Power Feeds Tables"
                    break
            except Exception as e:
                print(f"Failed to update Device ID in Power Feeds Table {e}", file=sys.stderr)

            '''
            
            if message== "Device Id successfully updated in":
                print("Device ID not updated in any table", file=sys.stderr)
                #db.session.execute("SET FOREIGN_KEY_CHECKS=ON")
                #return jsonify({'response': "Device ID not updated in any table"}), 500
                #db.session.execute("SET FOREIGN_KEY_CHECKS=1;")
                #db.session.execute("SET FOREIGN_KEY_CHECKS=1;")
                return jsonify({'response': "Device ID not updated in any table","code":"500"})
    
            #db.session.execute("SET FOREIGN_KEY_CHECKS=ON")
            #db.session.execute("SET FOREIGN_KEY_CHECKS=1;")
            print(message, file=sys.stderr)
            #db.session.execute("SET FOREIGN_KEY_CHECKS=1;")
            return jsonify({'response': message,"code":"200"})

        except Exception as e:
            print(f"Error Occured In updating Device ID {e}", file=sys.stderr)
            #db.session.flush()
            #db.session.execute("SET FOREIGN_KEY_CHECKS=1;")
            #db.session.execute("SET FOREIGN_KEY_CHECKS=ON")
            #return jsonify({'response': f"Error Occured In updating Device ID {e}"}), 500
            #db.session.execute("SET FOREIGN_KEY_CHECKS=1;")
            return jsonify({'response': f"Error Occured In updating Device ID {e}","code":"500"})
        
        finally:
            pass
            #db.session.execute("SET FOREIGN_KEY_CHECKS=ON")
            #db.session.execute("SET FOREIGN_KEY_CHECKS=1;")
    
    else:
        print("Old or New Device Not Found", file=sys.stderr)
        #return jsonify({'response': "Old or New Device Not Found"}), 500
        return jsonify({'response': "Old or New Device Not Received","code":"500"})


@app.route("/deleteSeedDevice", methods = ['POST'])
@token_required
def DeleteSeedDevice(user_data):
    deviceObj = request.get_json()
    try:

        if "device_id" in deviceObj:
            deviceId= deviceObj['device_id']


        if deviceId:
            idInSeed= Seed.query.with_entities(Seed.device_id).filter_by(device_id=deviceId).first()
            idInDevice= Device_Table.query.with_entities(Device_Table.device_id).filter_by(device_id=deviceId).first()
            if idInDevice:
                print("Device ALready Exists in Device Table", file=sys.stderr)
                #return jsonify({'response': "New Device IP Already Exists in both Seed and Table"}), 500
                return jsonify({'response': "Device ALready Exists in Device Table","code":"500"})
            
            if not idInSeed:
                print("Device Does Not Exists in Seed Table", file=sys.stderr)
                #return jsonify({'response': "New Device IP Already Exists in both Seed and Table"}), 500
                return jsonify({'response': "Device Does Not Exists in Seed Table","code":"500"})
            else:
                db.session.execute(f"delete from seed_table where device_id = '{deviceId}';")
                db.session.commit()
        else:
            return jsonify({'response': "No Device ID Found","code":"500"})
        
        return jsonify({'response': "Deleted","code":"200"})

    except Exception as e:
        print(f"Error in Deleting Device From Seed {e}", file=sys.stderr)
        return jsonify({'response': "Error Occured ","code":"500"})


@app.route("/editDeviceIp", methods = ['POST'])
@token_required
def EditDeviceIp(user_data):   
    oldIp= newIp="" 
    deviceObj = request.get_json()
    if "old_device_ip" in deviceObj:
        oldIp= deviceObj['old_device_ip']
    if "new_device_ip" in deviceObj:
        newIp= deviceObj['new_device_ip']

    if oldIp and newIp:
        newInSeed= Seed.query.with_entities(Seed.ne_ip_address).filter_by(ne_ip_address=newIp).first()
        newInDevice= Device_Table.query.with_entities(Device_Table.ne_ip_address).filter_by(ne_ip_address=newIp).first()
        if newInSeed and newInDevice:
            print("New Device IP Already Exists in both Seed and Table", file=sys.stderr)
            #return jsonify({'response': "New Device IP Already Exists in both Seed and Table"}), 500
            return jsonify({'response': "New Device IP Already Exists in both Seed and Table","code":"500"})

        if newInSeed:
            print("New Device IP Already Exists in Seed", file=sys.stderr)
            #return jsonify({'response': "New Device IP Already Exists in Seed"}), 500
            return jsonify({'response': "New Device IP Already Exists in Seed","code":"500"})

        
        if newInDevice:
            print("New Device IP Already Exists in Device Table", file=sys.stderr)
            #return jsonify({'response': "New Device IP Already Exists in Device"}), 500
            return jsonify({'response': "New Device IP Already Exists in Device","code":"500"})
        try:
            message="Device Ip successfully updated in"
            #db.session.execute("SET FOREIGN_KEY_CHECKS=OFF;")
            
            #db.session.execute("SET FOREIGN_KEY_CHECKS=0")
            
            obj = Seed.query.filter(Seed.ne_ip_address == oldIp).first()

            if(obj):
                try:
                    obj.ne_ip_address = newIp
                    obj.modified_by= user_data["user_id"]
                    #db.session.flush()
                    db.session.commit()
                    #print("updated in device", file=sys.stderr)
                    message+= " Seed"
                
                except Exception as e:
                    #db.session.flush()
                    #db.session.execute("SET FOREIGN_KEY_CHECKS=0")
                    print(f"Failed to update Device ID in Seed Table {e}", file=sys.stderr)

            '''
            try:
                db.session.execute(f"update seed_table set ne_ip_address = '{newIp}' where ne_ip_address='{oldIp}';")
                db.session.commit()
                result= db.session.execute(f"SELECT * FROM seed_table WHERE ne_ip_address ='{newIp}';")
                for row in result:
                    if row[0]:
                        message+= " Seed"
                    break
            except Exception as e:
                print(f"Failed to update Device IP in Seed {e}", file=sys.stderr)
            '''

            obj = Device_Table.query.filter(Device_Table.ne_ip_address == oldIp).first()

            if(obj):
                try:
                    obj.ne_ip_address = newIp
                    obj.modified_by= user_data["user_id"]
                    #db.session.flush()
                    db.session.commit()
                    #print("updated in device", file=sys.stderr)
                    message+= ", Device Tables"
                
                except Exception as e:
                    #db.session.flush()
                    #db.session.execute("SET FOREIGN_KEY_CHECKS=0")
                    print(f"Failed to update Device ID in Device Table {e}", file=sys.stderr)


            '''
            try:
                db.session.execute(f"update device_table set ne_ip_address = '{newIp}' where ne_ip_address='{oldIp}';")
                db.session.commit()
                result= db.session.execute(f"SELECT * FROM device_table where ne_ip_address='{newIp}';")
                for row in result:
                    if row[0]:
                        message+= ", Device Tables"
                    break
            except Exception as e:
                print(f"Failed to update Device IP in Device Table {e}", file=sys.stderr)
            '''


            if message== "Device Ip successfully updated in":
                print("Device IP not updated in any table", file=sys.stderr)
                #db.session.execute("SET FOREIGN_KEY_CHECKS=ON")
                #db.session.execute("SET FOREIGN_KEY_CHECKS=1")
                #return jsonify({'response': "Device IP not updated in any table"}), 500
                return jsonify({'response': "Device IP not updated in any table","code":"500"})
                
    
            #db.session.execute("SET FOREIGN_KEY_CHECKS=ON")
            #db.session.execute("SET FOREIGN_KEY_CHECKS=1")
            print(message, file=sys.stderr)
            return jsonify({'response': message,"code":"200"})

        except Exception as e:
            print(f"Error Occured In updating Device IP {e}", file=sys.stderr)
            #db.session.flush()
            #db.session.execute("SET FOREIGN_KEY_CHECKS=1")
            #db.session.execute("SET FOREIGN_KEY_CHECKS=ON")
            #return jsonify({'response': f"Error Occured In updating Device IP {e}"}), 500
            return jsonify({'response': f"Error Occured In updating Device IP {e}","code":"500"})
        
        finally:
            pass
            #db.session.execute("SET FOREIGN_KEY_CHECKS=ON")
            #db.session.execute("SET FOREIGN_KEY_CHECKS=1")
    
    else:
        print("Old or New Device Not Found", file=sys.stderr)
        #return jsonify({'response': "Old or New Device Not Found"}), 500
        return jsonify({'response': "Old or New Device Not Found","code":"500"})

@app.route("/getAllDeviceStaticColumns", methods = ['GET'])
#@token_required
def GetAllDeviceStaticColumns():   
    objList=[]
    #objList.append({'label':'Device Id', 'value':'device_id'})
    #objList.append({'label':'Ip Address', 'value':'ip_address'})
    objList.append({'label':'Function', 'value':'device_name'})
    objList.append({'label':'Site Id', 'value':'site_id'})
    objList.append({'label':'Rack Id', 'value':'rack_id'})
    objList.append({'label':'Tag Id', 'value':'virtual'})

    objList.append({'label': 'Subrack Id Number', 'value': 'subrack_id_number'})
    objList.append({'label': 'Criticality', 'value': 'criticality'})
    objList.append({'label': 'Function', 'value': 'function'})
    objList.append({'label': 'Cisco Domain', 'value': 'cisco_domain'})
    #objList.append({'label': 'Section', 'value': 'section'})


    objList.append({'label':'Dismantle Date', 'value':'dismantle_date'})
    objList.append({'label':'Tag ID', 'value':'tag_id'})
    objList.append({'label':'Device RU', 'value':'device_ru'})
    #objList.append({'label':'Domain', 'value':'domain'})

    objList.append({'label':'Item Code', 'value':'item_code'})
    objList.append({'label':'Item Description', 'value':'item_desc'})
    objList.append({'label':'CLEI', 'value':'clei'})
    objList.append({'label':'Parent', 'value':'parent'})
    objList.append({'label':'Vuln Fix Plan Status', 'value':'vuln_fix_plan_status'})

    objList.append({'label':'Vuln OPS Severity', 'value':'vuln_ops_severity'})
    objList.append({'label':'Source', 'value':'source'})
    objList.append({'label':'Site Type', 'value':'site_type'})
    objList.append({'label':'Contract Number', 'value':'contract_number'})
    objList.append({'label':'Contract Expiry', 'value':'contract_expiry'})

    
    objList.append({'label':'Vuln Ops Severity', 'value':'vuln_ops_severity'})
    #objList.append({'label':'Status', 'value':'status'})
    objList.append({'label':'Site Type', 'value':'site_type'})
    #objList.append({'label':'IMS Status', 'value':'ims_status'})
    #objList.append({'label':'IMS Function', 'value':'ims_function'})

    objList.append({'label':'Integrated with AAA', 'value':'integrated_with_aaa'})
    objList.append({'label':'Integrated with PAAM', 'value':'integrated_with_paam'})
    objList.append({'label':'Approved MBSS', 'value':'approved_mbss'})
    objList.append({'label':'MBSS Implemented', 'value':'mbss_implemented'})

    objList.append({'label':'Threat Cases', 'value':'threat_cases'})
    objList.append({'label':'Vulnerability Scanning', 'value':'vulnerability_scanning'})
    #objList.append({'label':'Vulnerability Severity', 'value':'vulnerability_severity'})
    objList.append({'label':'SW Type', 'value':'sw_type'})
    objList.append({'label':'Onboard Status', 'value':'onboard_status'})

    objList.append({'label':'Vendor', 'value':'vendor'})
    objList.append({'label':'Asset Type', 'value':'asset_type'})
    objList.append({'label':'Authentication', 'value':'authentication'})


    return jsonify(objList), 200

@app.route("/bulkUpdateDeviceExcel", methods = ['Post'])
@token_required
def BulkUpdateDeviceExcel(user_data):   
    deviceObj = request.get_json()
    print("Bulk Updating Devices", file=sys.stderr)
    try:
        columnsToUpdate= deviceObj.get('columns')
        dataToUpdate= deviceObj.get('data')

        if not columnsToUpdate:
            return jsonify({'response': "No Columns Selected to Update", "code":"500"})
        if not dataToUpdate:
            return jsonify({'response': "No Data to Update", "code":"500"})
        ret= updateDeviceAndSeedTable(columnsToUpdate, dataToUpdate, user_data)
        #print(f"Return is {ret}", file=sys.stderr)
        return ret

    except Exception as e:
        print("Exception Occured in Bulk update from Excel{e}", file=sys.stderr)

    return "", 200

def updateDeviceAndSeedTable(columns, data, user_data):
    try:
        #seedMessage="Seed: "
        #deviceMessage="Device: "
        seedCount=0
        deviceCount=0

        for record in data:
            seebObj= None
            deviceObj= None
            
            #print(record, file=sys.stderr)
            try:
                if not 'ip_address' in record:
                    #return jsonify({'response': "No Columns Selected to Update"}), 500
                    pass

                if not 'device_id' in record:
                    pass
                    print("In device checking", file=sys.stderr)
                    #return jsonify({'response': "No Device ID Selected to Update"}), 500
                    
                else:
                    seebObj= Seed.query.filter_by(device_id=record['device_id']).first()
                    deviceObj= Device_Table.query.filter_by(device_id= record['device_id']).first()
                    
                if seebObj is None or deviceObj is None:
                    print(f"Device or Seed Not Found for {record['device_id']}", file=sys.stderr)
                    continue
                    #pass
                if 'device_name' in record and 'device_name' in columns:
                    ##seed Hostname
                    seebObj.hostname= record['device_name']
                    deviceObj.device_name= record['device_name']
                    

                if 'rack_id' in record and 'rack_id' in columns:
                    seebObj.rack_id= record['rack_id']
                    deviceObj.rack_id= record['rack_id']

                    
                if 'device_name' in record and 'device_name' in columns:
                    ##seed Hostname
                    seebObj.hostname = record['device_name']
                    deviceObj.device_name = record['device_name']

                if 'rack_id' in record and 'rack_id' in columns:
                    seebObj.rack_id = record['rack_id']
                    deviceObj.rack_id = record['rack_id']

                if 'site_id' in record and 'site_id' in columns:
                    seebObj.site_id = record['site_id']
                    deviceObj.site_id = record['site_id']

                if 'virtual' in record and 'virtual' in columns:
                    seebObj.virtual = record['virtual']
                    deviceObj.virtual = record['virtual']

                if 'subrack_id_number' in record and 'subrack_id_number' in columns:
                    seebObj.subrack_id_number = record['subrack_id_number']
                    deviceObj.subrack_id_number = record['subrack_id_number']

                if 'criticality' in record and 'criticality' in columns:
                    seebObj.criticality = record['criticality']
                    deviceObj.criticality = record['criticality']

                if 'function' in record and 'function' in columns:
                    seebObj.function = record['function']
                    deviceObj.function = record['function']

                if 'cisco_domain' in record and 'cisco_domain' in columns:
                    seebObj.cisco_domain = record['cisco_domain']
                    deviceObj.cisco_domain = record['cisco_domain']

                    if "EDN" in str(deviceObj.cisco_domain):
                        deviceObj.domain = "ENT"
                    if "IGW" in str(deviceObj.cisco_domain):
                        deviceObj.domain = "IGW"
                    if "SOC" in str(deviceObj.cisco_domain):
                        deviceObj.domain = "Security"

                # if 'section' in record:
                #     seebObj.section= record['section']
                #     deviceObj.section= record['section']
                
                # if 'department' in record:
                #     seebObj.department= record['department']
                #     deviceObj.department= record['department']

                if 'dismantle_date' in record and 'dismantle_date' in columns:
                    #device only
                    deviceObj.dismantle_date= FormatStringDate(record['dismantle_date'])
                    #pass

                if 'tag_id' in record and 'tag_id' in columns:
                    seebObj.tag_id= record['tag_id']
                    deviceObj.tag_id= record['tag_id']

                if 'device_ru' in record and 'device_ru' in columns:
                    seebObj.device_ru= record['device_ru']
                    deviceObj.ru= record['device_ru']
                    
                # if 'domain' in record:
                #     #device only
                #     deviceObj.domain= record['domain']
                    

                if 'item_code' in record and 'item_code' in columns:
                    #device only
                    deviceObj.item_code= record['item_code']

                if 'item_desc' in record and 'item_desc' in columns:
                    #device only
                    deviceObj.item_desc= record['item_desc']

                if 'clei' in record and 'clei' in columns:
                    seebObj.clei= record['clei']
                    deviceObj.clei= record['clei']

                if 'parent' in record and 'parent' in columns:
                    seebObj.parent= record['parent']
                    deviceObj.parent= record['parent']
                                    
                if 'vuln_fix_plan_status' in record  and 'vuln_fix_plan_status' in columns:
                    seebObj.vuln_fix_plan_status= record['vuln_fix_plan_status']
                    deviceObj.vuln_fix_plan_status= record['vuln_fix_plan_status']

                if 'vuln_ops_severity' in record and 'vuln_ops_severity' in columns:
                    seebObj.vuln_ops_severity= record['vuln_ops_severity']
                    deviceObj.vuln_ops_severity= record['vuln_ops_severity']

                if 'source' in record and 'source' in columns:
                    #device only
                    deviceObj.source= record['source']

                if 'site_type' in record and 'site_type' in columns:
                    seebObj.site_type= record['site_type']
                    deviceObj.site_type= record['site_type']

                if 'contract_number' in record and 'contract_number' in columns:
                    seebObj.contract_number= record['contract_number']
                    deviceObj.contract_number= record['contract_number']

                if 'contract_expiry' in record and 'contract_expiry' in columns:
                    seebObj.contract_expiry= FormatStringDate(record['contract_expiry'])
                    deviceObj.contract_expiry= FormatStringDate(record['contract_expiry'])

                # if 'status' in record:
                #     #operation_status in seed
                #     seebObj.operation_status= record['status']
                #     deviceObj.status= record['status']

                # if 'ims_status' in record:
                #     #device only
                #     deviceObj.ims_status= record['ims_status']

                # if 'ims_function' in record:
                #     #device only
                #     deviceObj.ims_function= record['ims_function']

                if 'integrated_with_aaa' in record and 'integrated_with_aaa' in columns:
                    seebObj.integrated_with_aaa= record['integrated_with_aaa']
                    deviceObj.integrated_with_aaa= record['integrated_with_aaa']

                if 'integrated_with_paam' in record and 'integrated_with_paam' in columns:
                    seebObj.integrated_with_paam= record['integrated_with_paam']
                    deviceObj.integrated_with_paam= record['integrated_with_paam']
                
                if 'integrated_with_siem' in record and 'integrated_with_siem' in columns:
                    seebObj.integrated_with_siem= record['integrated_with_siem']
                    deviceObj.integrated_with_siem= record['integrated_with_siem']

                if 'approved_mbss' in record and 'approved_mbss' in columns:
                    seebObj.approved_mbss= record['approved_mbss']
                    deviceObj.approved_mbss= record['approved_mbss']

                if 'mbss_implemented' in record and 'mbss_implemented' in columns:
                    seebObj.mbss_implemented= record['mbss_implemented']
                    deviceObj.mbss_implemented= record['mbss_implemented']

                if 'mbss_implemented' in record and 'mbss_implemented' in columns:
                    seebObj.mbss_integration_check= record['mbss_integration_check']
                    deviceObj.mbss_integration_check= record['mbss_integration_check']

                if 'threat_cases' in record and 'threat_cases' in columns:
                    seebObj.threat_cases= record['threat_cases']
                    deviceObj.threat_cases= record['threat_cases']

                if 'vulnerability_scanning' in record and 'vulnerability_scanning' in columns:
                    seebObj.vulnerability_scanning= record['vulnerability_scanning']
                    deviceObj.vulnerability_scanning= record['vulnerability_scanning'] 

                if 'authentication' in record and 'authentication' in columns:
                    seebObj.authentication= record['authentication']
                    deviceObj.authentication= record['authentication']  
                    

                # if 'vulnerability_severity' in record:
                #     seebObj.vulnerability_severity= record['vulnerability_severity']
                #     deviceObj.vulnerability_severity= record['vulnerability_severity']

                if 'sw_type' in record and 'sw_type' in columns:
                    ##seed Only
                    seebObj.sw_type= record['sw_type']

                if 'onboard_status' in record and 'onboard_status' in columns:
                    ##seed Only
                    seebObj.onboard_status= record['onboard_status']

                if 'vendor' in record and 'vendor' in columns:
                    ##seed Only
                    seebObj.vendor= record['vendor']

                if 'asset_type' in record and 'asset_type' in columns:
                    ##seed Only
                    seebObj.asset_type= record['asset_type']
                

                
                if seebObj is None:
                    print(f"Nothing to update in seed table ", file=sys.stderr)
                else:
                    try:
                        seebObj.modified_by= user_data['user_id']
                        #seebObj.modification_date= datetime.now(tz)

                        status2 = UpdateData2(seebObj)
                        #print(f"Status2 is {status2}", file=sys.stderr)
                        if status2:
                            seedCount += 1
                            print(f"Updated Seed {seebObj.device_id}", file=sys.stderr)
                        else:
                             print(f"Not Updated Seed {seebObj.device_id}", file=sys.stderr)
                    except Exception as e:
                        traceback.print_exc()
                        #db.session.rollback()
                        print(f"Error updating seed: {e}", file=sys.stderr)
                        #print(f"Not Updated Seed {seebObj.device_id}", file=sys.stderr)

                if deviceObj is None:
                    print(f"Nothing to update in device table ", file=sys.stderr)
                else:
                    try:
                        deviceObj.modified_by= user_data['user_id']
                        deviceObj.modification_date= datetime.now(tz)
                        status = UpdateData2(deviceObj)
                        if status:
                            print(f"Status is {status}", file=sys.stderr)
                            deviceCount += 1
                            print(f"Updated Device {deviceObj.device_id}", file=sys.stderr)
                        else:
                            print(f"Not Updated Device {deviceObj.device_id}", file=sys.stderr)
                    except Exception as e:
                        #db.session.rollback()
                        print(f"Error updating device: {e}", file=sys.stderr)
                        #print(f"Not Updated Device {deviceObj.device_id}", file=sys.stderr)



            except Exception as e:
                print(f"Error Occured in Single Update Data {e}", file=sys.stderr)
        print("Finished Bulk Update", file=sys.stderr)
        return jsonify({'response': f"Seed Table: {seedCount}/{len(data)} \n Device Table: {deviceCount}/{len(data)}  ","code":"200"})
    
    except Exception as e:
      print(f"Error Occured in Updating Device and Seed Tables {e}", file=sys.stderr)


def createDeviceQuery(dateObj, limit, offset):
    try:
        print(dateObj, file=sys.stderr)
        query=""
        count_query=""
        search_query=""
        export_query=""
        count_query = "SELECT COUNT(*) as total_count FROM device_table WHERE 1=1"
        search_query = "SELECT * FROM device_table WHERE 1=1"
        if 'ip_address' in dateObj and dateObj['ip_address']:
            query += f" AND ne_ip_Address LIKE '%%{dateObj['ip_address']}%%'"

        if 'device_id' in dateObj and dateObj['device_id']:
            query += f" AND device_id LIKE '%%{dateObj['device_id']}%%'"

        if 'function' in dateObj and dateObj['function']:
            query += f" AND `function` LIKE '%%{dateObj['function']}%%'"
            
            #fetch_date = datetime.strptime(dateObj['fetch_date'], '%d-%m-%Y')
        if query:
            count_query+= query+";"
            export_query+=search_query+query+";"
            search_query += f" {query} LIMIT {limit} OFFSET {offset};"

        else:
        # If query is empty, return empty strings for all queries
            count_query = ""
            search_query = ""
            export_query = ""
        return search_query, count_query, export_query
    except Exception as e:
        return ""

def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%d-%m-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result


@app.route("/getDevicesBySearchFilters", methods = ['POST'])
@token_required
def GetDevicesBySearchFilters(user_data):
    if True:
        deviceObjList=[]

        limit = request.args.get("limit")
        offset = request.args.get("offset")
        dateObj = request.get_json()
        
        query, count_query, export_query = createDeviceQuery(dateObj, limit, offset)
        deviceObjs = db.session.execute(query)

        rows = deviceObjs.fetchall()

        count=0
        count = db.session.execute(count_query).scalar()
        
        for row in rows:
            # columns = row.keys()
            # #print(columns, file=sys.stderr)
            # rowObj = dict(zip(columns, row))

            # #print(rowObj, file=sys.stderr)
            # Device = namedtuple('Device', columns)
            # deviceObj = Device(*rowObj.values())
            # print(deviceObj, file=sys.stderr)
            row_dict = {k.lower(): v for k, v in row.items()}
            deviceObj = namedtuple('Device', row_dict.keys())(*row_dict.values())

            deviceDataDict= {}
            deviceDataDict['device_id'] = deviceObj.device_id
            deviceDataDict['site_id'] = deviceObj.site_id
            deviceDataDict['rack_id'] = deviceObj.rack_id
            deviceDataDict['ne_ip_address'] = deviceObj.ne_ip_address
            deviceDataDict['device_name'] = deviceObj.device_name
            deviceDataDict['software_version'] = deviceObj.software_version
            deviceDataDict['patch_version'] = deviceObj.patch_version
            
            deviceDataDict['creation_date'] = FormatDate(deviceObj.creation_date)
            deviceDataDict['modification_date'] = FormatDate(deviceObj.modification_date)
            deviceDataDict['status'] = deviceObj.status
            deviceDataDict['device_ru'] = deviceObj.ru
            deviceDataDict['department'] = deviceObj.department
            deviceDataDict['section'] = deviceObj.section
            deviceDataDict['criticality'] = deviceObj.criticality
            deviceDataDict['function'] = deviceObj.function
            deviceDataDict['cisco_domain'] = deviceObj.cisco_domain
            deviceDataDict['manufacturer'] = deviceObj.manufacturer
            deviceDataDict['hw_eos_date'] = FormatDate(deviceObj.hw_eos_date)
            deviceDataDict['hw_eol_date'] = FormatDate(deviceObj.hw_eol_date)
            deviceDataDict['sw_eos_date'] = FormatDate(deviceObj.sw_eos_date)
            deviceDataDict['sw_eol_date'] = FormatDate(deviceObj.sw_eol_date)
            deviceDataDict['virtual'] = deviceObj.virtual
            deviceDataDict['rfs_date'] = FormatDate(deviceObj.rfs_date)
            deviceDataDict['authentication'] = deviceObj.authentication
            deviceDataDict['serial_number'] = deviceObj.serial_number
            deviceDataDict['pn_code'] = deviceObj.pn_code
            deviceDataDict['tag_id'] = deviceObj.tag_id
            deviceDataDict['subrack_id_number'] = deviceObj.subrack_id_number
            deviceDataDict['manufactuer_date'] = FormatDate(deviceObj.manufactuer_date)
            deviceDataDict['hardware_version'] = deviceObj.hardware_version
            deviceDataDict['max_power'] = deviceObj.max_power
            deviceDataDict['site_type'] = deviceObj.site_type
            deviceDataDict['source'] = deviceObj.source
            deviceDataDict['stack'] = deviceObj.stack
            deviceDataDict['contract_number'] = deviceObj.contract_number
            deviceDataDict['contract_expiry'] = FormatDate(deviceObj.contract_expiry)
            deviceDataDict['item_code'] = deviceObj.item_code
            deviceDataDict['item_desc'] = deviceObj.item_desc
            deviceDataDict['clei'] = deviceObj.clei
            deviceDataDict['domain'] = deviceObj.domain
            deviceDataDict['ims_status'] = deviceObj.ims_status
            deviceDataDict['ims_function'] = deviceObj.ims_function
            deviceDataDict['parent'] = deviceObj.parent
            deviceDataDict['vuln_fix_plan_status'] = deviceObj.vuln_fix_plan_status
            deviceDataDict['vuln_ops_severity'] = deviceObj.vuln_ops_severity
            deviceDataDict['integrated_with_aaa'] = deviceObj.integrated_with_aaa
            deviceDataDict['integrated_with_paam'] = deviceObj.integrated_with_paam
            deviceDataDict['approved_mbss'] = deviceObj.approved_mbss
            deviceDataDict['mbss_implemented'] = deviceObj.mbss_implemented
            deviceDataDict['mbss_integration_check'] = deviceObj.mbss_integration_check
            deviceDataDict['integrated_with_siem'] = deviceObj.integrated_with_siem
            deviceDataDict['threat_cases'] = deviceObj.threat_cases
            deviceDataDict['vulnerability_scanning'] = deviceObj.vulnerability_scanning
            deviceDataDict['vulnerability_severity'] = deviceObj.vulnerability_severity
            deviceDataDict['created_by'] = deviceObj.created_by
            deviceDataDict['modified_by'] = deviceObj.modified_by
            if deviceObj.dismantle_date:
                deviceDataDict['dismantle_date'] = FormatDate(deviceObj.dismantle_date)
            #deviceDataDict['site_name'] = Phy_Table.query.with_entities(Phy_Table.site_name).filter_by(site_id=deviceObj.site_id).first()[0]
            #deviceDataDict['rack_name'] = Rack_Table.query.with_entities(Rack_Table.rack_name).filter_by(rack_id=deviceObj.rack_id).first()[0]
            
            
            deviceObjList.append(deviceDataDict)

        content = gzip.compress(json.dumps({'total':count, 'data': deviceObjList}).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response

@app.route("/getDevicesBySearchFiltersNonPaginated", methods = ['POST'])
@token_required
def GetDevicesBySearchFiltersNonPaginated(user_data):
    if True:
        deviceObjList=[]
        dateObj = request.get_json()
        
        query, count_query, export_query = createBulkQuery(dateObj)
        deviceObjs = db.session.execute(query)

        rows = deviceObjs.fetchall()

        # count=0
        # count = db.session.execute(count_query).scalar()
        devices = []
        for row in rows:
            row_dict = {k.lower(): v for k, v in row.items()}
            deviceObj = namedtuple('Device', row_dict.keys())(*row_dict.values())
            #Get Device ID List
            devices.append(str(deviceObj.device_id))
            deviceDataDict= {}
            deviceDataDict['device_id'] = deviceObj.device_id
            deviceDataDict['site_id'] = deviceObj.site_id
            deviceDataDict['rack_id'] = deviceObj.rack_id
            deviceDataDict['ne_ip_address'] = deviceObj.ne_ip_address
            deviceDataDict['device_name'] = deviceObj.device_name
            deviceDataDict['software_version'] = deviceObj.software_version
            deviceDataDict['patch_version'] = deviceObj.patch_version
            deviceDataDict['creation_date'] = FormatDate(deviceObj.creation_date)
            deviceDataDict['modification_date'] = FormatDate(deviceObj.modification_date)
            deviceDataDict['status'] = deviceObj.status
            deviceDataDict['device_ru'] = deviceObj.ru
            deviceDataDict['department'] = deviceObj.department
            deviceDataDict['section'] = deviceObj.section
            deviceDataDict['criticality'] = deviceObj.criticality
            deviceDataDict['function'] = deviceObj.function
            deviceDataDict['cisco_domain'] = deviceObj.cisco_domain
            deviceDataDict['manufacturer'] = deviceObj.manufacturer
            deviceDataDict['hw_eos_date'] = FormatDate(deviceObj.hw_eos_date)
            deviceDataDict['hw_eol_date'] = FormatDate(deviceObj.hw_eol_date)
            deviceDataDict['sw_eos_date'] = FormatDate(deviceObj.sw_eos_date)
            deviceDataDict['sw_eol_date'] = FormatDate(deviceObj.sw_eol_date)
            deviceDataDict['virtual'] = deviceObj.virtual
            deviceDataDict['rfs_date'] = FormatDate(deviceObj.rfs_date)
            deviceDataDict['authentication'] = deviceObj.authentication
            deviceDataDict['serial_number'] = deviceObj.serial_number
            deviceDataDict['pn_code'] = deviceObj.pn_code
            deviceDataDict['tag_id'] = deviceObj.tag_id
            deviceDataDict['subrack_id_number'] = deviceObj.subrack_id_number
            deviceDataDict['manufactuer_date'] = FormatDate(deviceObj.manufactuer_date)
            deviceDataDict['hardware_version'] = deviceObj.hardware_version
            deviceDataDict['max_power'] = deviceObj.max_power
            deviceDataDict['site_type'] = deviceObj.site_type
            deviceDataDict['source'] = deviceObj.source
            deviceDataDict['stack'] = deviceObj.stack
            deviceDataDict['contract_number'] = deviceObj.contract_number
            deviceDataDict['contract_expiry'] = FormatDate(deviceObj.contract_expiry)
            deviceDataDict['item_code'] = deviceObj.item_code
            deviceDataDict['item_desc'] = deviceObj.item_desc
            deviceDataDict['clei'] = deviceObj.clei
            deviceDataDict['domain'] = deviceObj.domain
            deviceDataDict['ims_status'] = deviceObj.ims_status
            deviceDataDict['ims_function'] = deviceObj.ims_function
            deviceDataDict['parent'] = deviceObj.parent
            deviceDataDict['vuln_fix_plan_status'] = deviceObj.vuln_fix_plan_status
            deviceDataDict['vuln_ops_severity'] = deviceObj.vuln_ops_severity
            deviceDataDict['integrated_with_aaa'] = deviceObj.integrated_with_aaa
            deviceDataDict['integrated_with_paam'] = deviceObj.integrated_with_paam
            deviceDataDict['approved_mbss'] = deviceObj.approved_mbss
            deviceDataDict['mbss_implemented'] = deviceObj.mbss_implemented
            deviceDataDict['mbss_integration_check'] = deviceObj.mbss_integration_check
            deviceDataDict['integrated_with_siem'] = deviceObj.integrated_with_siem
            deviceDataDict['threat_cases'] = deviceObj.threat_cases
            deviceDataDict['vulnerability_scanning'] = deviceObj.vulnerability_scanning
            deviceDataDict['vulnerability_severity'] = deviceObj.vulnerability_severity
            deviceDataDict['created_by'] = deviceObj.created_by
            deviceDataDict['modified_by'] = deviceObj.modified_by
            if deviceObj.dismantle_date:
                deviceDataDict['dismantle_date'] = FormatDate(deviceObj.dismantle_date)
            #deviceDataDict['site_name'] = Phy_Table.query.with_entities(Phy_Table.site_name).filter_by(site_id=deviceObj.site_id).first()[0]
            #deviceDataDict['rack_name'] = Rack_Table.query.with_entities(Rack_Table.rack_name).filter_by(rack_id=deviceObj.rack_id).first()[0]
            
            
            deviceObjList.append(deviceDataDict)

        content = gzip.compress(json.dumps({'device_ids':devices, 'data': deviceObjList}).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response

def createBulkQuery(dateObj):
    try:
        print(dateObj, file=sys.stderr)
        query=""
        count_query=""
        search_query=""
        export_query=""
        count_query = "SELECT COUNT(*) as total_count FROM device_table WHERE 1=1"
        search_query = "SELECT * FROM device_table WHERE 1=1"
        if 'domain' in dateObj and dateObj['domain']:
            query += f" AND cisco_domain LIKE '%%{dateObj['domain']}%%'"

        if 'pn_code' in dateObj and dateObj['pn_code']:
            query += f" AND pn_code LIKE '%%{dateObj['pn_code']}%%'"

        if 'function' in dateObj and dateObj['function']:
            query += f" AND `function` LIKE '%%{dateObj['function']}%%'"

        if 'device_id' in dateObj and dateObj['device_id']:
            query += f" AND device_id LIKE '%%{dateObj['device_id']}%%'"
            
            #fetch_date = datetime.strptime(dateObj['fetch_date'], '%d-%m-%Y')
        if query:
            count_query+= query+";"
            export_query+=search_query+query+";"
            search_query += f" {query};"

        else:
        # If query is empty, return empty strings for all queries
            count_query = ""
            search_query = ""
            export_query = ""
        return search_query, count_query, export_query
    except Exception as e:
        return ""

@app.route("/bulkUpdateDeviceColumn", methods = ['Post'])
@token_required
def BulkUpdateDeviceColumn(user_data):   
    deviceObj = request.get_json()
    print("Bulk Updating Devices", file=sys.stderr)
    try:
        columnsToUpdate= deviceObj.get('column')
        valueToUpdate= deviceObj.get('value')
        searchFilters= deviceObj.get('filters')


        if not columnsToUpdate:
            return jsonify({'response': "No Columns Selected to Update", "code":"500"})
        if not valueToUpdate:
            return jsonify({'response': "No Value Selected to Update", "code":"500"})
        if not searchFilters:
            return jsonify({'response': "No Filters Selected to Update", "code":"500"})
        
        deviceObjList=[]

        limit = 50#request.args.get("limit")
        offset =0# request.args.get("offset")
        dateObj = request.get_json()
        
        query, count_query, export_query = createDeviceQuery(dateObj['filters'], limit, offset)
        deviceObjs = db.session.execute(export_query)

        rows = deviceObjs.fetchall()

        count=0
        count = db.session.execute(count_query).scalar()
        
        for row in rows:
            # columns = row.keys()
            # #print(columns, file=sys.stderr)
            # rowObj = dict(zip(columns, row))

            # #print(rowObj, file=sys.stderr)
            # Device = namedtuple('Device', columns)
            # deviceObj = Device(*rowObj.values())
            # print(deviceObj, file=sys.stderr)
            row_dict = {k.lower(): v for k, v in row.items()}
            deviceObj = namedtuple('Device', row_dict.keys())(*row_dict.values())

            deviceDataDict= {}
            deviceDataDict['device_id'] = deviceObj.device_id
            
            deviceObjList.append(deviceDataDict)
        print(len(deviceObjList), file=sys.stderr)
        print(export_query, file=sys.stderr)
        seedCount=0
        deviceCount=0
        for device in deviceObjList:
            seebObj= None
            deviceObj= None
            
            #print(record, file=sys.stderr)
            try:
                
                seebObj= Seed.query.filter_by(device_id=device['device_id']).first()
                deviceObj= Device_Table.query.filter_by(device_id= device['device_id']).first()
                    
                if seebObj is None or deviceObj is None:
                    print(f"Device or Seed Not Found for ", file=sys.stderr)
                    continue
                    #pass
                if 'device_name' in columnsToUpdate:
                    ##seed Hostname
                    seebObj.hostname= valueToUpdate
                    deviceObj.device_name= valueToUpdate
                
                if 'rack_id' in columnsToUpdate:
                    seebObj.rack_id = valueToUpdate
                    deviceObj.rack_id =valueToUpdate

                if 'site_id' in columnsToUpdate:
                    seebObj.site_id =valueToUpdate
                    deviceObj.site_id = valueToUpdate

                if 'virtual' in columnsToUpdate:
                    seebObj.virtual =valueToUpdate
                    deviceObj.virtual = valueToUpdate
                
                if 'subrack_id_number' in columnsToUpdate:
                    seebObj.subrack_id_number = valueToUpdate
                    deviceObj.subrack_id_number = valueToUpdate

                if 'criticality' in columnsToUpdate:
                    seebObj.criticality =valueToUpdate
                    deviceObj.criticality = valueToUpdate

                if 'function' in columnsToUpdate:
                    seebObj.function =valueToUpdate
                    deviceObj.function = valueToUpdate

                if 'cisco_domain' in columnsToUpdate:
                    seebObj.cisco_domain = valueToUpdate
                    deviceObj.cisco_domain = valueToUpdate

                    if "EDN" in str(deviceObj.cisco_domain):
                        deviceObj.domain = "ENT"
                    if "IGW" in str(deviceObj.cisco_domain):
                        deviceObj.domain = "IGW"
                    if "SOC" in str(deviceObj.cisco_domain):
                        deviceObj.domain = "Security"

                # if 'section' in record:
                #     seebObj.section= record['section']
                #     deviceObj.section= record['section']
                
                # if 'department' in record:
                #     seebObj.department= record['department']
                #     deviceObj.department= record['department']

                if 'dismantle_date' in columnsToUpdate:
                    #device only
                    deviceObj.dismantle_date= FormatStringDate(valueToUpdate)
                    #pass

                if 'tag_id' in columnsToUpdate:
                    seebObj.tag_id=valueToUpdate
                    deviceObj.tag_id= valueToUpdate

                if 'device_ru' in columnsToUpdate:
                    seebObj.device_ru= valueToUpdate
                    deviceObj.ru=valueToUpdate
                    
                # if 'domain' in record:
                #     #device only
                #     deviceObj.domain= record['domain']
                    

                if 'item_code' in columnsToUpdate:
                    #device only
                    deviceObj.item_code= valueToUpdate

                if 'item_desc' in columnsToUpdate:
                    #device only
                    deviceObj.item_desc= valueToUpdate

                if 'clei' in columnsToUpdate:
                    seebObj.clei= valueToUpdate
                    deviceObj.clei= valueToUpdate

                if 'parent' in columnsToUpdate:
                    seebObj.parent= valueToUpdate
                    deviceObj.parent= valueToUpdate
                                    
                if 'vuln_fix_plan_status' in columnsToUpdate:
                    seebObj.vuln_fix_plan_status= valueToUpdate
                    deviceObj.vuln_fix_plan_status= valueToUpdate

                if 'vuln_ops_severity' in columnsToUpdate:
                    seebObj.vuln_ops_severity= valueToUpdate
                    deviceObj.vuln_ops_severity= valueToUpdate

                if 'source' in columnsToUpdate:
                    #device only
                    deviceObj.source= valueToUpdate

                if 'site_type' in columnsToUpdate:
                    seebObj.site_type= valueToUpdate
                    deviceObj.site_type= valueToUpdate

                if 'contract_number' in columnsToUpdate:
                    seebObj.contract_number= valueToUpdate
                    deviceObj.contract_number= valueToUpdate

                if 'contract_expiry' in columnsToUpdate:
                    seebObj.contract_expiry= FormatStringDate(valueToUpdate)
                    deviceObj.contract_expiry= FormatStringDate(valueToUpdate)

                # if 'status' in record:
                #     #operation_status in seed
                #     seebObj.operation_status= record['status']
                #     deviceObj.status= record['status']

                # if 'ims_status' in record:
                #     #device only
                #     deviceObj.ims_status= record['ims_status']

                # if 'ims_function' in record:
                #     #device only
                #     deviceObj.ims_function= record['ims_function']

                if 'integrated_with_aaa' in columnsToUpdate:
                    seebObj.integrated_with_aaa= valueToUpdate
                    deviceObj.integrated_with_aaa= valueToUpdate

                if 'integrated_with_paam' in columnsToUpdate:
                    seebObj.integrated_with_paam= valueToUpdate
                    deviceObj.integrated_with_paam= valueToUpdate
                
                if 'integrated_with_siem' in columnsToUpdate:
                    seebObj.integrated_with_siem= valueToUpdate
                    deviceObj.integrated_with_siem= valueToUpdate
                if 'approved_mbss' in columnsToUpdate:
                    seebObj.approved_mbss= valueToUpdate
                    deviceObj.approved_mbss= valueToUpdate

                if 'mbss_implemented' in columnsToUpdate:
                    seebObj.mbss_implemented= valueToUpdate
                    deviceObj.mbss_implemented= valueToUpdate

                if 'mbss_implemented' in columnsToUpdate:
                    seebObj.mbss_integration_check= valueToUpdate
                    deviceObj.mbss_integration_check= valueToUpdate

                if 'threat_cases' in columnsToUpdate:
                    seebObj.threat_cases= valueToUpdate
                    deviceObj.threat_cases= valueToUpdate

                if 'vulnerability_scanning' in columnsToUpdate:
                    seebObj.vulnerability_scanning= valueToUpdate
                    deviceObj.vulnerability_scanning= valueToUpdate

                if 'authentication' in columnsToUpdate:
                    seebObj.authentication= valueToUpdate
                    deviceObj.authentication= valueToUpdate
                    

                # if 'vulnerability_severity' in record:
                #     seebObj.vulnerability_severity= record['vulnerability_severity']
                #     deviceObj.vulnerability_severity= record['vulnerability_severity']

                if 'sw_type' in columnsToUpdate:
                    ##seed Only
                    seebObj.sw_type= valueToUpdate

                if 'onboard_status' in columnsToUpdate:
                    ##seed Only
                    seebObj.onboard_status= valueToUpdate

                if 'vendor' in columnsToUpdate:
                    ##seed Only
                    seebObj.vendor= valueToUpdate

                if 'asset_type' in columnsToUpdate:
                    ##seed Only
                    seebObj.asset_type= valueToUpdate
                

                if seebObj is None:
                    print(f"Nothing to update in seed table ", file=sys.stderr)
                else:
                    try:
                        seebObj.modified_by= user_data['user_id']
                        #seebObj.modification_date= datetime.now(tz)

                        status2 = UpdateData2(seebObj)
                        #print(f"Status2 is {status2}", file=sys.stderr)
                        if status2:
                            seedCount += 1
                            print(f"Updated Seed {seebObj.device_id}", file=sys.stderr)
                        else:
                             print(f"Not Updated Seed {seebObj.device_id}", file=sys.stderr)
                    except Exception as e:
                        traceback.print_exc()
                        #db.session.rollback()
                        print(f"Error updating seed: {e}", file=sys.stderr)
                        #print(f"Not Updated Seed {seebObj.device_id}", file=sys.stderr)

                if deviceObj is None:
                    print(f"Nothing to update in device table ", file=sys.stderr)
                else:
                    try:
                        deviceObj.modified_by= user_data['user_id']
                        deviceObj.modification_date= datetime.now(tz)
                        status = UpdateData2(deviceObj)
                        if status:
                            print(f"Status is {status}", file=sys.stderr)
                            deviceCount += 1
                            print(f"Updated Device {deviceObj.device_id}", file=sys.stderr)
                        else:
                            print(f"Not Updated Device {deviceObj.device_id}", file=sys.stderr)
                    except Exception as e:
                        #db.session.rollback()
                        print(f"Error updating device: {e}", file=sys.stderr)
                        #print(f"Not Updated Device {deviceObj.device_id}", file=sys.stderr)

            except Exception as e:
                print(f"Error Occured in Single Update Data {e}", file=sys.stderr)



        return ""#ret

    except Exception as e:
        print(f"Exception Occured in Bulk update {e}", file=sys.stderr)

    return "", 200

@app.route("/bulkUpdateDeviceColumns", methods = ['Post'])
@token_required
def BulkUpdateDeviceColumns(user_data):
    deviceObj = request.get_json()
    print("Bulk Updating Devices", file=sys.stderr)
    try:
        valueToUpdate= deviceObj.get('values')
        searchFilters= deviceObj.get('device_ids')
        # print("$$$$$$$$", valueToUpdate, searchFilters, file=sys.stderr)
        if not valueToUpdate:
            return jsonify({'response': "No Values Selected to Update", "code":"500"})
        if not searchFilters:
            return jsonify({'response': "No Filters Selected to Update", "code":"500"})
        
        for obj in searchFilters:
            try:
                print("Device ID:", obj, file=sys.stderr)
                device = Device_Table.query.filter(Device_Table.device_id.like(f"%{obj}%")).first()
                seed = Seed.query.filter(Seed.device_id.like(f"%{obj}%")).first()
                # print("Values of Device and Seed From Table: ", device, seed, file=sys.stderr)
                
                if device is None:
                    print(f"Nothing to update in device table ", file=sys.stderr)
                else:
                    if "paam_integrations" in valueToUpdate and valueToUpdate['paam_integrations']:
                        print("PAAM", file=sys.stderr)
                        device.integrated_with_paam = valueToUpdate["paam_integrations"]
                    if "aaa_integrations" in valueToUpdate and valueToUpdate['aaa_integrations']:
                        print("AAA", file=sys.stderr)
                        device.integrated_with_aaa = valueToUpdate["aaa_integrations"]
                    if "mbss_approved" in valueToUpdate and valueToUpdate['mbss_approved']:
                        print("MBSS APPROVED", file=sys.stderr)
                        device.approved_mbss = valueToUpdate["mbss_approved"]
                    if "mbss_compliance" in valueToUpdate and valueToUpdate['mbss_compliance']:
                        print("MBSS Compliance", file=sys.stderr)
                        device.mbss_integration_check = valueToUpdate["mbss_compliance"]

                    device.modified_by= user_data['user_id']
                    device.modification_date= datetime.now(tz)
                    status = UpdateData2(device)
                    # print("Fianl Dictionary of Device is: ", device, file=sys.stderr)
                    if status:
                        print(f"Status is {status}", file=sys.stderr)
                        print(f"Updated Device {obj} in Device", file=sys.stderr)
                    else:
                        print(f"Not Updated Device {obj}", file=sys.stderr)
                
                if seed is None:
                    print(f"Nothing to update in seed table ", file=sys.stderr)
                else:
                    if "paam_integrations" in valueToUpdate and valueToUpdate['paam_integrations']:
                        seed.integrated_with_paam = valueToUpdate["paam_integrations"]
                    if "aaa_integrations" in valueToUpdate and valueToUpdate['aaa_integrations']:
                        seed.integrated_with_aaa = valueToUpdate["aaa_integrations"]
                    if "mbss_approved" in valueToUpdate and valueToUpdate['mbss_approved']:
                        seed.approved_mbss = valueToUpdate["mbss_approved"]
                    if "mbss_compliance" in valueToUpdate and valueToUpdate['mbss_compliance']:
                        seed.mbss_integration_check = valueToUpdate["mbss_compliance"]

                    seed.modified_by= user_data['user_id']
                    seed.modification_date= datetime.now(tz)
                    status = UpdateData2(seed)
                    # print("Fianl Dictionary of Seed is: ", seed, file=sys.stderr)
                    if status:
                        print(f"Status is {status}", file=sys.stderr)
                        print(f"Updated Device {obj} in Seed", file=sys.stderr)
                    else:
                        print(f"Not Updated Device {obj}", file=sys.stderr)

            except Exception as e:
                print(f"Error updating device: {e}", file=sys.stderr)
                traceback.print_exc()

        return ""

    except Exception as e:
        print(f"Exception Occured in Bulk update {e}", file=sys.stderr)
        traceback.print_exc()

    return "", 200

@app.route('/getDomains', methods=['GET'])
@token_required
def GetDomains(user_data):
    try:
        objList = []
        objs = Device_Table.query.with_entities(Device_Table.cisco_domain.distinct()).all()
        for obj in objs:
            objList.append(str(obj[0]))

        return jsonify(objList),200
    except Exception as e:
        print(f"Exception Occured in Loading Owners {e}", file=sys.stderr)
        return str(e),500
