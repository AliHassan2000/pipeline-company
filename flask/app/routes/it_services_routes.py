
from ipaddress import ip_address
import json, sys, time
from logging import raiseExceptions
from socket import timeout
from app import app,db, tz, phy_engine
from flask import request, make_response, Response
import gzip
from flask_jsonpify import jsonify
from app.models.phy_mapping_models import IT_PHYSICAL_SERVERS_TABLE, IT_APP_TABLE, IT_OS_TABLE, IT_IP_TABLE, IT_MAC_TABLE, IT_OWNER_TABLE, EDN_SERVICE_MAPPING
from app.middleware import token_required
from datetime import datetime
import traceback
########

def FormatStringDate(date):
    #print(date, file=sys.stderr)
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
    try: 
        # print(f"Dataa is : {obj.creation_date}", file=sys.stderr)
        #add data to db
        #obj.creation_date= datetime.now(tz)
        #obj.modification_date= datetime.now(tz)
        db.session.add(obj)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong {e}", file=sys.stderr)

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
    try:
        #obj.modification_date= datetime.now(tz)
        db.session.merge(obj)
        db.session.commit()
        #print(obj.site_name, file=sys.stderr)
    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong {e}", file=sys.stderr)
    
    return True

@app.route('/physicalServersNew', methods=['POST'])
@token_required
def AddPhysicalServerNew(user_data):
    if True:
        response = AddPhysicalServerFunc()
        return response
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

def AddPhysicalServerFunc():
    try:
        response = False
        response1 = False
        vm = ''
        serverObj = request.get_json()
        for obj in serverObj:
            
            try:
                physicalServer = IT_PHYSICAL_SERVERS_TABLE()
                if "server_name" in obj:
                    physicalServer.server_name = obj['server_name']
                else:
                    raise Exception("Key 'server_name' is Missing")
                if "vm_name" in obj:
                    physicalServer.vm_name = obj['vm_name']
                else:
                    raise Exception("Key 'vm_name' is Missing")
            
                if IT_PHYSICAL_SERVERS_TABLE.query.with_entities(IT_PHYSICAL_SERVERS_TABLE.server_id).filter_by(vm_name=obj['vm_name']).first() is not None:
                    physicalServer.server_id= IT_PHYSICAL_SERVERS_TABLE.query.with_entities(IT_PHYSICAL_SERVERS_TABLE.server_id).filter_by(vm_name=obj['vm_name']).first()[0]
                    physicalServer.modification_date= datetime.now(tz)
                    UpdateData(physicalServer)
                    print(f"Data Updated For VM: {physicalServer.vm_name}", file=sys.stderr)
                    response = True
                    vm = physicalServer.vm_name
                else:
                    physicalServer.modification_date= datetime.now(tz)
                    physicalServer.creation_date= datetime.now(tz)
                    InsertData(physicalServer)
                    print("Data Inserted Into DB", file=sys.stderr)
                    response1 = True
                    vm = physicalServer.vm_name

            except Exception as e:
                print(f"Error Adding Data: {e}", file=sys.stderr)

        if response==True:
            return jsonify({'Response': f"{vm} Successfully Updated"}),200
        if response1==True:
            return jsonify({'Response': f"{vm} Successfully Inserted"}),200
    except Exception as e:
        print(f"Exception Occured in Adding Physical server Table {e}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({f"Response": f"Failed to Update/Insert {e}"}),500

@app.route('/appTableNew', methods=['POST'])
@token_required
def AppTableNew(user_data):
    if True:
        response = AddAppDataFunc()
        return response
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

def AddAppDataFunc():

    try:
        response = False
        response1 = False
        vm = ''
        appObj = request.get_json()
        for obj in appObj:
            try:
                app = IT_APP_TABLE()
                if "vm_name" in obj:
                    app.vm_name = obj['vm_name']
                else:
                    raise Exception("Key 'vm_name' is Missing")
                if "sw_component" in obj:
                    app.sw_component = obj['sw_component']
                else:
                    raise Exception("Key 'sw_component' is Missing")
            
                if IT_APP_TABLE.query.with_entities(IT_APP_TABLE.app_id).filter_by(sw_component=obj['sw_component']).filter_by(vm_name=obj['vm_name']).first() is not None:
                    app.app_id= IT_APP_TABLE.query.with_entities(IT_APP_TABLE.app_id).filter_by(sw_component=obj['sw_component']).filter_by(vm_name=obj['vm_name']).first()[0]
                    app.modification_date= datetime.now(tz)
                    UpdateData(app)
                    print(f"Data Updated For VM: {app.vm_name}", file=sys.stderr)
                    response = True
                    vm = app.vm_name
                else:
                    app.modification_date= datetime.now(tz)
                    app.creation_date= datetime.now(tz)

                    InsertData(app)
                    print("Data Inserted Into DB", file=sys.stderr)
                    response1 = True
                    vm = app.vm_name

            except Exception as e:
                print(f"Error Adding Data {e}", file=sys.stderr)

        if response==True:
            return jsonify({'Response': f"{vm} Successfully Updated"}),200
        if response1==True:
            return jsonify({'Response': f"{vm} Successfully Inserted"}),200
    except Exception as e:
        print(f"Exception is adding APP Table {e}", file=sys.stderr)
        traceback.print_exc()
        return jsonify({f"Response": f"Failed to Update/Insert {e}"}),500


@app.route('/osTableNew', methods=['POST'])
@token_required
def OsTableNew(user_data):
    if True:
        response = AddOSDataFunc()
        return response
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401

def AddOSDataFunc():

    try:
        response = False
        response1 = False
        vm = ''
        osObj = request.get_json()
        for obj in osObj:
            try:
                os = IT_OS_TABLE()
                if "vm_name" in obj:
                    os.vm_name = obj['vm_name']
                else:
                    raise Exception("Key 'vm_name' is Missing")
                if "operating_system" in obj:
                    os.operating_system = obj['operating_system']
                else:
                    raise Exception("Key 'operating_system' is Missing")
                
                if IT_OS_TABLE.query.with_entities(IT_OS_TABLE.os_id).filter_by(vm_name=obj['vm_name']).first() is not None:
                    os.os_id= IT_OS_TABLE.query.with_entities(IT_OS_TABLE.os_id).filter_by(vm_name=obj['vm_name']).first()[0]
                    os.modification_date= datetime.now(tz)
                    UpdateData(os)
                    print(f"Data Updated For VM: {os.vm_name}", file=sys.stderr)
                    response = True
                    vm = os.vm_name
                else:
                    os.modification_date= datetime.now(tz)
                    os.creation_date= datetime.now(tz)

                    InsertData(os)
                    print("Data Inserted Into DB", file=sys.stderr)
                    response1 = True
                    vm = os.vm_name

            except Exception as e:
                print(f"Error Adding Data: {e}", file=sys.stderr)

        if response==True:
            return jsonify({'Response': f"{vm} Successfully Updated"}),200
        if response1==True:
            return jsonify({'Response': f"{vm} Successfully Inserted"}),200
    except Exception as e:
        traceback.print_exc()
        return jsonify({f"Response": f"Failed to Update/Insert {e}"}),500


@app.route('/macTableNew', methods=['POST'])
@token_required
def MacTableNew(user_data):
    if True:
        response = AddMacDataFunc()
        return response
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401
def AddMacDataFunc():

    try:
        response = False
        response1 = False
        vm = ''
        macObj = request.get_json()
        for obj in macObj:
            try:
                mac = IT_MAC_TABLE()
                if "vm_name" in obj:
                    mac.vm_name = obj['vm_name']
                else:
                    raise Exception("Key 'vm_name' is Missing")
                if "mac_address" in obj:
                    address = obj['mac_address'].replace(':','').replace('.', '')
                    address = [*address]
                    add = ''.join(address[:4])
                    address = address[4:]
                    while address:
                        add += "."+''.join(address[:4])
                        address = address[4:]
                    mac.mac_address = add
                    obj['mac_address'] = add

                else:
                    raise Exception("Key 'mac_address' is Missing")
            
                if IT_MAC_TABLE.query.with_entities(IT_MAC_TABLE.mac_id).filter_by(mac_address=obj['mac_address']).first() is not None:
                    mac.mac_id= IT_MAC_TABLE.query.with_entities(IT_MAC_TABLE.mac_id).filter_by(mac_address=obj['mac_address']).first()[0]
                    mac.modification_date= datetime.now(tz)
                    UpdateData(mac)
                    print(f"Data Updated For VM: {mac.vm_name}", file=sys.stderr)
                    response = True
                    vm = mac.vm_name
                else:
                    mac.modification_date= datetime.now(tz)
                    mac.creation_date= datetime.now(tz)
                    InsertData(mac)
                    print("Data Inserted Into DB", file=sys.stderr)
                    response1 = True
                    vm = mac.vm_name

            except Exception as e:
                print(f"Error Adding Data: {e}", file=sys.stderr)

        if response==True:
            return jsonify({'Response': f"{vm} Successfully Updated"}),200
        if response1==True:
            return jsonify({'Response': f"{vm} Successfully Inserted"}),200
    except Exception as e:
        traceback.print_exc()
        return jsonify({f"Response": f"Failed to Update/Insert {e}"}),500

@app.route('/ipTableNew', methods=['POST'])
@token_required
def IpTableNew(user_data):
    if True:
        response = AddIpDataFunc()
        return response
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401
def AddIpDataFunc():
    try:
        response = False
        response1 = False
        vm = ''
        ipObj = request.get_json()
        for obj in ipObj:
            try:
                ip = IT_IP_TABLE()
                if "vm_name" in obj:
                    ip.vm_name = obj['vm_name']
                else:
                    raise Exception("Key 'vm_name' is Missing")
                if "ip_address" in obj:
                    ip.ip_address = obj['ip_address']
                else:
                    raise Exception("Key 'ip_address' is Missing")

                if IT_IP_TABLE.query.with_entities(IT_IP_TABLE.ip_id).filter_by(ip_address=obj['ip_address']).first() is not None:
                    ip.ip_id= IT_IP_TABLE.query.with_entities(IT_IP_TABLE.ip_id).filter_by(ip_address=obj['ip_address']).first()[0]
                    ip.modification_date= datetime.now(tz)
                    
                    UpdateData(ip)
                    print(f"Data Updated For VM: {ip.vm_name}", file=sys.stderr)
                    response = True
                    vm = ip.vm_name
                else:
                    ip.modification_date= datetime.now(tz)
                    ip.creation_date= datetime.now(tz)
                    InsertData(ip)
                    print("Data Inserted Into DB", file=sys.stderr)
                    response1 = True
                    vm = ip.vm_name

            except Exception as e:
                print(f"Error Adding Data {obj['vm_name']}: {e}", file=sys.stderr)

        if response==True:
            return jsonify({'Response': f"{vm} Successfully Updated"}),200
        if response1==True:
            return jsonify({'Response': f"{vm} Successfully Inserted"}),200
    except Exception as e:
        print("Error While Adding Data In IP Table", file=sys.stderr)
        traceback.print_exc()
        return jsonify({f"Response": f"Failed to Update/Insert {e}"}),500

@app.route('/ownersNew', methods=['POST'])
@token_required
def OwnersNew(user_data):
    if True:
        response = AddOwnersDataFunc()
        return response
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Post Data'}), 401
def AddOwnersDataFunc():
    try:
        response = False
        response1 = False
        vm = ''
        ownersObj = request.get_json()
        for obj in ownersObj:
            try:
                owner = IT_OWNER_TABLE()
                if "vm_name" in obj:
                    owner.vm_name = obj['vm_name']
                else:
                    raise Exception("Key 'vm_name' is Missing")
                if "owner_name" in obj:
                    owner.owner_name = obj.get('owner_name',"")
                else:
                    owner.owner_name = ""
                    # raise Exception("Key 'owner_name' is Missing")
                if "owner_email" in obj:
                    owner.owner_email = obj.get('owner_email', "")
                else:
                    owner.owner_email = ""
                    # raise Exception("Key 'owner_email' is Missing")
                if "owner_contact" in obj:
                    owner.owner_contact = obj.get('owner_contact', "")
                else:
                    owner.owner_contact = ""
                    # raise Exception("Key 'owner_contact' is Missing")
                if "app_name" in obj:
                    owner.app_name = obj.get('app_name', "")
                else:
                    owner.app_name = ""
                    # raise Exception("Key 'app_name' is Missing")
                if "status" in obj:
                    owner.status = obj.get('status', "")
                else:
                    owner.status = ""
                    # raise Exception("Key 'status' is Missing")
                if "instance_id" in obj:
                    owner.instance_id = obj.get('instance_id', "")
                else:
                    owner.instance_id = ""
                    # raise Exception("Key 'instance_id' is Missing")

                if IT_OWNER_TABLE.query.with_entities(IT_OWNER_TABLE.owner_id).filter_by(vm_name=obj['vm_name']).first() is not None:
                # queryString = f"select OWNER_ID,APP_NAME from it_owner_table where APP_NAME='{obj['app_name']}' and VM_NAME='{obj['vm_name']}';"
                # result = phy_engine.execute(queryString)
                # print((int(len(list(result)))),file=sys.stderr)
                # length = int(len(list(result)))
                # print(length,file=sys.stderr)
                # if length>0:
                    owner.owner_id= IT_OWNER_TABLE.query.with_entities(IT_OWNER_TABLE.owner_id).filter_by(vm_name=obj['vm_name']).first()[0]
                    # print(owner.owner_id,file=sys.stderr)
                    owner.modification_date= datetime.now(tz)
                    UpdateData(owner)
                    print(f"Data Updated For VM: {owner.vm_name}", file=sys.stderr) 
                    response = True
                    vm = owner.vm_name
                else:
                    owner.modification_date= datetime.now(tz)
                    owner.creation_date= datetime.now(tz)
                    InsertData(owner)
                    print("Data Inserted Into DB", file=sys.stderr)
                    response1 = True
                    vm = owner.vm_name

            except Exception as e:
                print(f"Error Adding Data: {e}", file=sys.stderr)
            
        if response==True:
            return jsonify({'Response': f"{vm} Successfully Updated"}),200
        if response1==True:
            return jsonify({'Response': f"{vm} Successfully Inserted"}),200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({f"Response": f"Failed to Update/Insert {e}"}),500


@app.route('/physicalServers', methods=['GET'])
@token_required
def GetAllServers(user_data):
    if True:
        try:
            ObjList = []
            Objs = IT_PHYSICAL_SERVERS_TABLE.query.all()
            for obj in Objs:
                dataDict = {}
                dataDict['server_id'] = obj.server_id
                dataDict['server_name'] = obj.server_name
                dataDict['vm_name'] = obj.vm_name
                dataDict['creation_date'] = obj.creation_date
                dataDict['modification_date'] = obj.modification_date
                ObjList.append(dataDict)
            return jsonify(ObjList),200
        except Exception as e:
            return str(e),500

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/physicalServers/<int:id>', methods=['PUT'])
@token_required
def UpdatePhysicalServers(id):
    if True:
        try:
            serverObj = request.get_json()
            objs = IT_PHYSICAL_SERVERS_TABLE.query.with_entities(IT_PHYSICAL_SERVERS_TABLE).filter_by(server_id= id).first()

            if objs:
                if "server_id" in serverObj:
                    objs.server_id = serverObj['server_id']
                if "server_name" in serverObj:
                    objs.server_name = serverObj['server_name']
                if "vm_name" in serverObj:
                    objs.vm_name = serverObj['vm_name']
                if "creation_date" in serverObj:
                    objs.creation_date = serverObj['creation_date']
                if "modification_date" in serverObj:
                    objs.modification_date = serverObj['modification_date']

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
    
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route('/physicalServers', methods=['DELETE'])
@token_required
def removePhysicalServers(user_data):
    if True:
        try:
            ids = request.get_json()
            for ip in ids['ips']:
                IT_PHYSICAL_SERVERS_TABLE.query.filter_by(server_id= ip).delete()

            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return str(e),500

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route('/appTable', methods=['GET'])
@token_required
def GetAllApps(user_data):
    if True:
        try:
            ObjList = []
            Objs = IT_APP_TABLE.query.all()
            for obj in Objs:
                dataDict = {}
                dataDict['app_id'] = obj.app_id
                dataDict['vm_name'] = obj.vm_name
                dataDict['sw_component'] = obj.sw_component
                dataDict['creation_date'] = obj.creation_date
                dataDict['modification_date'] = obj.modification_date
                ObjList.append(dataDict)
            return jsonify(ObjList),200
        except Exception as e:
            return str(e),500

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route('/appTable/<int:id>', methods=['PUT'])
@token_required
def UpdateAppData(id):
    if True:
        try:
            appObj = request.get_json()
            objs = IT_APP_TABLE.query.with_entities(IT_APP_TABLE).filter_by(app_id= id).first()

            if objs:
                if "app_id" in appObj:
                    objs.app_id = appObj['app_id']
                if "sw_component" in appObj:
                    objs.sw_component = appObj['sw_component']
                if "vm_name" in appObj:
                    objs.vm_name = appObj['vm_name']
                if "creation_date" in appObj:
                    objs.creation_date = appObj['creation_date']
                if "modification_date" in appObj:
                    objs.modification_date = appObj['modification_date']

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
    
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/appTable', methods=['DELETE'])
@token_required
def removeAppTableData(user_data):
    if True:
        try:
            ips = request.get_json()
            for ip in ips['ips']:
                IT_APP_TABLE.query.filter_by(app_id= ip).delete()

            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return str(e),500

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/osTable', methods=['GET'])
@token_required
def GetAllOS(user_data):
    if True:
        try:
            ObjList = []
            Objs = IT_OS_TABLE.query.all()
            for obj in Objs:
                dataDict = {}
                dataDict['os_id'] = obj.os_id
                dataDict['vm_name'] = obj.vm_name
                dataDict['operating_system'] = obj.operating_system
                dataDict['creation_date'] = obj.creation_date
                dataDict['modification_date'] = obj.modification_date
                ObjList.append(dataDict)
            return jsonify(ObjList),200
        except Exception as e:
            return str(e),500
    
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route('/osTable/<int:id>', methods=['PUT'])
@token_required
def UpdateOsData(id):
    if True:
        try:
            osObj = request.get_json()
            objs = IT_OS_TABLE.query.with_entities(IT_OS_TABLE).filter_by(os_id= id).first()

            if objs:
                if "os_id" in osObj:
                    objs.os_id = osObj['os_id']
                if "operating_system" in osObj:
                    objs.operating_system = osObj['operating_system']
                if "vm_name" in osObj:
                    objs.vm_name = osObj['vm_name']
                if "creation_date" in osObj:
                    objs.creation_date = osObj['creation_date']
                if "modification_date" in osObj:
                    objs.modification_date = osObj['modification_date']

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

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/osTable', methods=['DELETE'])
@token_required
def removeOsTableData(user_data):
    if True:
        try:
            ips = request.get_json()
            for ip in ips['ips']:
                IT_OS_TABLE.query.filter_by(os_id= ip).delete()

            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return str(e),500

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/macTable', methods=['GET'])
@token_required
def GetAllMAC(user_data):
    if True:
        try:
            ObjList = []
            Objs = IT_MAC_TABLE.query.all()
            for obj in Objs:
                dataDict = {}
                dataDict['mac_id'] = obj.mac_id
                dataDict['vm_name'] = obj.vm_name
                dataDict['mac_address'] = obj.mac_address
                dataDict['creation_date'] = obj.creation_date
                dataDict['modification_date'] = obj.modification_date
                ObjList.append(dataDict)
            return jsonify(ObjList),200
        except Exception as e:
            return str(e),500

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/macTable/<int:id>', methods=['PUT'])
@token_required
def UpdateMacData(id):
    if True:
        try:
            macObj = request.get_json()
            objs = IT_MAC_TABLE.query.with_entities(IT_MAC_TABLE).filter_by(mac_id= id).first()

            if objs:
                if "mac_id" in macObj:
                    objs.mac_id = macObj['mac_id']
                if "mac_address" in macObj:
                    objs.mac_address = macObj['mac_address']
                if "vm_name" in macObj:
                    objs.vm_name = macObj['vm_name']
                if "creation_date" in macObj:
                    objs.creation_date = macObj['creation_date']
                if "modification_date" in macObj:
                    objs.modification_date = macObj['modification_date']

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

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/macTable', methods=['DELETE'])
@token_required
def removeMacTableData(user_data):
    if True:
        try:
            ips = request.get_json()
            for ip in ips['ips']:
                IT_MAC_TABLE.query.filter_by(mac_id= ip).delete()

            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return str(e),500

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/ipTable', methods=['GET'])
@token_required
def GetAllIP(user_data):
    if True:
        try:
            ObjList = []
            Objs = IT_IP_TABLE.query.all()
            for obj in Objs:
                dataDict = {}
                dataDict['ip_id'] = obj.ip_id
                dataDict['vm_name'] = obj.vm_name
                dataDict['ip_address'] = obj.ip_address
                dataDict['creation_date'] = obj.creation_date
                dataDict['modification_date'] = obj.modification_date
                ObjList.append(dataDict)
            return jsonify(ObjList),200
        except Exception as e:
            return str(e),500

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route('/ipTable/<int:id>', methods=['PUT'])
@token_required
def UpdateIpData(id):
    if True:
        try:
            ipObj = request.get_json()
            objs = IT_IP_TABLE.query.with_entities(IT_IP_TABLE).filter_by(ip_id= id).first()

            if objs:
                if "ip_id" in ipObj:
                    objs.ip_id = ipObj['ip_id']
                if "ip_address" in ipObj:
                    objs.ip_address = ipObj['ip_address']
                if "vm_name" in ipObj:
                    objs.vm_name = ipObj['vm_name']
                if "creation_date" in ipObj:
                    objs.creation_date = ipObj['creation_date']
                if "modification_date" in ipObj:
                    objs.modification_date = ipObj['modification_date']

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

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/ipTable', methods=['DELETE'])
@token_required
def removeIpTableData(user_data):
    if True:
        try:
            ips = request.get_json()
            for ip in ips['ips']:
                IT_IP_TABLE.query.filter_by(ip_id= ip).delete()

            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return str(e),500

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/owners', methods=['GET'])
@token_required
def GetAllOwners(user_data):
    if True:
        try:
            ObjList = []
            Objs = IT_OWNER_TABLE.query.all()
            for obj in Objs:
                dataDict = {}
                dataDict['owner_id'] = obj.owner_id
                dataDict['vm_name'] = obj.vm_name
                dataDict['owner_name'] = obj.owner_name
                dataDict['owner_email'] = obj.owner_email
                dataDict['owner_contact'] = obj.owner_contact
                dataDict['app_name'] = obj.app_name
                dataDict['status'] = obj.status
                dataDict['instance_id'] = obj.instance_id
                dataDict['creation_date'] = obj.creation_date
                dataDict['modification_date'] = obj.modification_date
                ObjList.append(dataDict)
            return jsonify(ObjList),200
        except Exception as e:
            print(f"Exception Occured in Loading Owners {e}", file=sys.stderr)
            return str(e),500

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route('/owners/<int:id>', methods=['PUT'])
@token_required
def UpdateOwnersData(id):
    if True:
        try:
            ownerObj = request.get_json()
            objs = IT_OWNER_TABLE.query.with_entities(IT_OWNER_TABLE).filter_by(owner_id= id).first()

            if objs:
                if "owner_id" in ownerObj:
                    objs.owner_id = ownerObj['owner_id']
                if "owner_name" in ownerObj:
                    objs.owner_name = ownerObj['owner_name']
                if "vm_name" in ownerObj:
                    objs.vm_name = ownerObj['vm_name']
                if "email" in ownerObj:
                    objs.email = ownerObj['email']
                if "contact" in ownerObj:
                    objs.contact = ownerObj['contact']
                if "app_name" in ownerObj:
                    objs.app_name = ownerObj['app_name']
                if "status" in ownerObj:
                    objs.status = ownerObj['status']
                if "instance_id" in ownerObj:
                    objs.instance_id = ownerObj['instance_id']
                if "creation_date" in ownerObj:
                    objs.creation_date = ownerObj['creation_date']
                if "modification_date" in ownerObj:
                    objs.modification_date = ownerObj['modification_date']

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

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/owners', methods=['DELETE'])
@token_required
def removeOwnerTableData(user_data):
    if True:
        try:
            ips = request.get_json()
            for ip in ips['ips']:
                vmName = phy_engine.execute(f"SELECT vm_name FROM it_owner_table where owner_id = '{ip}'").fetchall()[0][0]
                IT_OWNER_TABLE.query.filter_by(owner_id= ip).delete()
                EDN_SERVICE_MAPPING.query.filter_by(server_name = vmName).delete()

            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return jsonify({'response': "success", "code": "200"})
            #return str(e),500

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401