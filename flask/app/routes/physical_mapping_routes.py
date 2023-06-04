import collections
import imp
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
import pytz
from app.models.phy_mapping_models import EDN_CDP_LEGACY,EDN_MAC_LEGACY,EDN_LLDP_ACI,EDN_FIREWALL_ARP,IGW_LLDP_ACI,IGW_CDP_LEGACY, EDN_MPLS, IGW_SYSTEM, EDN_SYSTEM, EDN_SECURITY, SCRIPT_STATUS, EDN_IPT, EDN_EXEC_VIDEO_EPS, EDN_LLDP_LEGACY, IGW_LLDP_LEGACY, EDN_SERVICE_MAPPING, IGW_SERVICE_MAPPING, IT_PHYSICAL_SERVERS_TABLE
from app.models.inventory_models import Seed, EDN_NET_Seed, EDN_SEC_Seed
from app.physical_mapping_scripts.cdp import CDPLegacy
from app.physical_mapping_scripts.arp import EdnMacLegacy
from app.physical_mapping_scripts.aci_lldp import LLDPPuller
from app.physical_mapping_scripts.arp_table import Arp
from app.physical_mapping_scripts.addFWIP import AddFwIP
from app.middleware import token_required
from app.physical_mapping_scripts.lldp import LLDPLegacy
import traceback
from app.physical_mapping_scripts.addSericeMapping import AddServiceMapping

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
    print(f"Dataa is : {obj.creation_date}", file=sys.stderr)
    #add data to db
    #obj.creation_date= datetime.now(tz)
    #obj.modification_date= datetime.now(tz)
    db.session.add(obj)
    db.session.commit()
    return True
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

@app.route("/addEdnMplsDevice",methods = ['POST'])
@token_required
def AddEdnMplsDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednMplsObj = request.get_json()

        print(ednMplsObj,file=sys.stderr)
        ednMpls = EDN_MPLS()
        ednMpls.device_a_ip = ednMplsObj['device_a_ip']
        if ednMplsObj['device_a_name']:
            ednMpls.device_a_name = ednMplsObj['device_a_name']
        if ednMplsObj['device_a_interface']:
            ednMpls.device_a_interface = ednMplsObj['device_a_interface']    
        if ednMplsObj['device_a_trunk_name']:
            ednMpls.device_a_trunk_name = ednMplsObj['device_a_trunk_name']
        if ednMplsObj['device_a_ip']:
            ednMpls.device_a_ip = ednMplsObj['device_a_ip']
        if ednMplsObj['device_b_system_name']:
            ednMpls.device_b_system_name= ednMplsObj['device_b_system_name']
        if ednMplsObj['device_b_interface']:
            ednMpls.device_b_interface = ednMplsObj['device_b_interface']
        if ednMplsObj['device_b_ip']:
            ednMpls.device_b_ip= ednMplsObj['device_b_ip']
        if ednMplsObj['device_b_type']:
            ednMpls.device_b_type= ednMplsObj['device_b_type']
        if ednMplsObj['device_b_port_desc']:
            portDesc = ednMplsObj['device_b_port_desc']
            portDesc.replace('<',"")
            portDesc.replace('>',"")
            portDesc.replace('|'," , ")
            ednMpls.device_b_port_desc= portDesc
            #ednMpls.device_b_port_desc= ednMplsObj['device_b_port_desc']
        if ednMplsObj['device_a_mac']:
            ednMpls.device_a_mac= ednMplsObj['device_a_mac']
        if ednMplsObj['device_b_mac']:
            ednMpls.device_b_mac= ednMplsObj['device_b_mac']
        if ednMplsObj['device_a_port_desc']:
            portDesc = ednMplsObj['device_a_port_desc']
            portDesc.replace('<',"")
            portDesc.replace('>',"")
            portDesc.replace('|'," , ")
            ednMpls.device_a_port_desc= portDesc
            #ednMpls.device_a_port_desc= ednMplsObj['device_a_port_desc']
        if ednMplsObj['device_a_vlan']:
            ednMpls.device_a_vlan= ednMplsObj['device_a_vlan']
        if 'service_vendor' in ednMplsObj:
                ednMpls.service_vendor = ednMplsObj['service_vendor']
        else:
            ednMpls.service_vendor = 'N/A'

        #print(device.sw_eol_date,file=sys.stderr)
        
        if EDN_MPLS.query.with_entities(EDN_MPLS.edn_mpls_id).filter_by(edn_mpls_id=ednMplsObj['edn_mpls_id']).first() is not None:
            ednMpls.edn_mpls_id = EDN_MPLS.query.with_entities(EDN_MPLS.edn_mpls_id).filter_by(edn_mpls_id=ednMplsObj['edn_mpls_id']).first()[0]
            print(f"Updated {ednMplsObj['edn_mpls_id']}",file=sys.stderr)
            ednMpls.modification_date= datetime.now(tz)
            UpdateData(ednMpls)
            
        else:
            ednMpls.creation_date= datetime.now(tz)
            ednMpls.modification_date= datetime.now(tz)
            print("Inserted Record",file=sys.stderr)
            InsertData(ednMpls)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnMplsDates",methods=['GET'])
@token_required
def GetAllEdnMplsDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from edn_mpls  ORDER BY creation_date DESC;"
        
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllEdnMplsByDate", methods = ['POST'])
@token_required
def GetAllEdnMplsByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednMplsObjList=[]
        #ednMplsObjs = EDN_MPLS.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        ednMplsObjs = phy_engine.execute(f"SELECT * FROM edn_mpls WHERE creation_date = '{current_time}'")

        for ednMplsObj in ednMplsObjs:

            ednMplsDataDict= {}
            ednMplsDataDict['edn_mpls_id']=ednMplsObj['EDN_MPLS_ID']
            ednMplsDataDict['device_a_name'] = ednMplsObj['DEVICE_A_NAME']
            ednMplsDataDict['device_a_interface'] = ednMplsObj['DEVICE_A_INTERFACE']
            ednMplsDataDict['device_a_trunk_name'] = ednMplsObj['DEVICE_A_TRUNK_NAME']
            ednMplsDataDict['device_a_ip'] = ednMplsObj['DEVICE_A_IP']
            ednMplsDataDict['device_b_system_name'] = ednMplsObj['DEVICE_B_SYSTEM_NAME']
            ednMplsDataDict['device_b_interface'] = ednMplsObj['DEVICE_B_INTERFACE']
            ednMplsDataDict['device_b_ip'] = ednMplsObj['DEVICE_B_IP']
            ednMplsDataDict['device_b_type'] = ednMplsObj['DEVICE_B_TYPE']
            ednMplsDataDict['device_b_port_desc'] = ednMplsObj['DEVICE_B_PORT_DESC']
            ednMplsDataDict['device_a_mac'] = ednMplsObj['DEVICE_A_MAC']
            ednMplsDataDict['device_b_mac'] = ednMplsObj['DEVICE_B_MAC']
            ednMplsDataDict['device_a_port_desc'] = ednMplsObj['DEVICE_A_PORT_DESC']
            ednMplsDataDict['device_a_vlan'] = ednMplsObj['DEVICE_A_VLAN']
            ednMplsDataDict['service_vendor'] = ednMplsObj['SERVICE_VENDOR']
            ednMplsDataDict['creation_date'] = FormatDate(ednMplsObj['CREATION_DATE'])
            ednMplsDataDict['modification_date'] = FormatDate(ednMplsObj['MODIFICATION_DATE'])
            ednMplsObjList.append(ednMplsDataDict)
       
        content = gzip.compress(json.dumps(ednMplsObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteEdnMplsDevice",methods = ['POST'])
@token_required
def DeleteEdnMplsDevice(user_data):
    if True:#session.get('token', None):
        ednMplsObj = request.get_json()
        #ednMplsObj= ednMplsObj.get("ips")
        #ednMplsObj = [9,10,11,12,13]
        print(ednMplsObj,file = sys.stderr)
        
        for obj in ednMplsObj.get("ips"):
            ednMplsId = EDN_MPLS.query.filter(EDN_MPLS.edn_mpls_id==obj).first()
            print(ednMplsId,file=sys.stderr)
            if obj:
                db.session.delete(ednMplsId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
        
@app.route("/addEdnMplsDevices", methods = ['POST'])
@token_required
def AddEdnMplsDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()
        time= datetime.now(tz)
        print(postData,file=sys.stderr)

        for ednMplsObj in postData:
            ednMpls = EDN_MPLS()
            if 'device_a_name' in ednMplsObj:
                ednMpls.device_a_name = ednMplsObj['device_a_name']
            else:
                ednMpls.device_a_name = 'N/A'
            if 'device_a_interface' in ednMplsObj:
                ednMpls.device_a_interface = ednMplsObj['device_a_interface']
            else:
                ednMpls.device_a_interface = 'N/A'
            if 'device_a_trunk_name' in ednMplsObj:
                ednMpls.device_a_trunk_name = ednMplsObj['device_a_trunk_name']
            else:
                ednMpls.device_a_trunk_name = 'N/A'
            if 'device_a_ip' in ednMplsObj:
                ednMpls.device_a_ip = ednMplsObj['device_a_ip']
            else:
                ednMpls.device_a_ip = 'N/A'
            if 'device_b_system_name' in ednMplsObj:
                ednMpls.device_b_system_name = ednMplsObj['device_b_system_name']
            else:
                ednMpls.device_b_system_name = 'N/A'
            if 'device_b_interface' in ednMplsObj:
                ednMpls.device_b_interface = ednMplsObj['device_b_interface']
            else:
                ednMpls.device_b_interface = 'N/A'
            if 'device_b_ip' in ednMplsObj:
                ednMpls.device_b_ip = ednMplsObj['device_b_ip']
            else:
                ednMpls.device_b_ip = 'N/A'
            if 'device_b_type' in ednMplsObj:
                ednMpls.device_b_type = ednMplsObj['device_b_type']
            else:
                ednMpls.device_b_type = 'N/A'
            if 'device_b_port_desc' in ednMplsObj:
                portDesc = ednMplsObj['device_b_port_desc']
                portDesc.replace('<',"")
                portDesc.replace('>',"")
                portDesc.replace('|'," , ")
                ednMpls.device_b_port_desc = portDesc
            else:
                ednMpls.device_b_port_desc = 'N/A'
            if 'device_a_mac' in ednMplsObj:
                ednMpls.device_a_mac = ednMplsObj['device_a_mac']
            else:
                ednMpls.device_a_mac = 'N/A'
            if 'device_b_mac' in ednMplsObj:
                ednMpls.device_b_mac = ednMplsObj['device_b_mac']
            else:
                ednMpls.device_b_mac = 'N/A'
            if 'device_a_port_desc' in ednMplsObj:
                portDesc = ednMplsObj['device_a_port_desc']
                portDesc.replace('<',"")
                portDesc.replace('>',"")
                portDesc.replace('|'," , ")
                ednMpls.device_a_port_desc = portDesc
            else:
                ednMpls.device_a_port_desc = 'N/A'
            if 'device_a_vlan' in ednMplsObj:
                ednMpls.device_a_vlan = ednMplsObj['device_a_vlan']
            else:
                ednMpls.device_a_vlan = 'N/A'
            if 'service_vendor' in ednMplsObj:
                ednMpls.service_vendor = ednMplsObj['service_vendor']
            else:
                ednMpls.service_vendor = 'N/A'
            ednMpls.creation_date= time
            ednMpls.modification_date = time
         
            # if Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first() is not None:
            #     seed.seed_id = Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first()[0]
            #     print("Updated " + seedObj['ne_ip_address'],file=sys.stderr)
            #     UpdateData(seed)
            # else:
            #     print("Inserted " +seedObj['ne_ip_address'],file=sys.stderr)
            #     seed.onboard_status = 'false'
            InsertData(ednMpls)
       
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnMpls", methods = ['GET'])
@token_required
def GetAllEdnMpls(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednMplsObjList=[]
        
        ednMplsObjs = phy_engine.execute(f'SELECT * FROM edn_mpls WHERE creation_date = (SELECT max(creation_date) FROM edn_mpls)')

        for ednMplsObj in ednMplsObjs:

            ednMplsDataDict= {}
            ednMplsDataDict['edn_mpls_id']=ednMplsObj['EDN_MPLS_ID']
            ednMplsDataDict['device_a_name'] = ednMplsObj['DEVICE_A_NAME']
            ednMplsDataDict['device_a_interface'] = ednMplsObj['DEVICE_A_INTERFACE']
            ednMplsDataDict['device_a_trunk_name'] = ednMplsObj['DEVICE_A_TRUNK_NAME']
            ednMplsDataDict['device_a_ip'] = ednMplsObj['DEVICE_A_IP']
            ednMplsDataDict['device_b_system_name'] = ednMplsObj['DEVICE_B_SYSTEM_NAME']
            ednMplsDataDict['device_b_interface'] = ednMplsObj['DEVICE_B_INTERFACE']
            ednMplsDataDict['device_b_ip'] = ednMplsObj['DEVICE_B_IP']
            ednMplsDataDict['device_b_type'] = ednMplsObj['DEVICE_B_TYPE']
            ednMplsDataDict['device_b_port_desc'] = ednMplsObj['DEVICE_B_PORT_DESC']
            ednMplsDataDict['device_a_mac'] = ednMplsObj['DEVICE_A_MAC']
            ednMplsDataDict['device_b_mac'] = ednMplsObj['DEVICE_B_MAC']
            ednMplsDataDict['device_a_port_desc'] = ednMplsObj['DEVICE_A_PORT_DESC']
            ednMplsDataDict['device_a_vlan'] = ednMplsObj['DEVICE_A_VLAN']
            ednMplsDataDict['service_vendor'] = ednMplsObj['SERVICE_VENDOR']
            ednMplsDataDict['creation_date'] = FormatDate(ednMplsObj['CREATION_DATE'])
            ednMplsDataDict['modification_date'] = FormatDate(ednMplsObj['MODIFICATION_DATE'])
            ednMplsObjList.append(ednMplsDataDict)

        content = gzip.compress(json.dumps(ednMplsObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/exportEdnMpls", methods = ['GET'])
@token_required
def ExportEdnMpls(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednMplsObjList=[]
        ednMplsObjs = EDN_MPLS.query.all()

        for ednMplsObj in ednMplsObjs:

            ednMplsDataDict= {}
            ednMplsDataDict['edn_mpls_id']=ednMplsObjs.edn_mpls_id
            ednMplsDataDict['device_a_name'] = ednMplsObj.device_a_name
            ednMplsDataDict['device_a_interface'] = ednMplsObj.device_a_interface
            ednMplsDataDict['device_a_trunk_name'] = ednMplsObj.device_a_trunk_name
            ednMplsDataDict['device_a_ip'] = ednMplsObj.device_a_ip
            ednMplsDataDict['device_b_system_name'] = ednMplsObj.device_b_system_name
            ednMplsDataDict['device_b_interface'] = ednMplsObj.device_b_interface
            ednMplsDataDict['device_b_ip'] = ednMplsObj.device_b_ip
            ednMplsDataDict['device_b_type'] = ednMplsObj.device_b_type
            ednMplsDataDict['device_b_port_desc'] = ednMplsObj.device_b_port_desc
            ednMplsDataDict['device_a_mac'] = ednMplsObj.device_a_mac
            ednMplsDataDict['device_b_mac'] = ednMplsObj.device_b_mac
            ednMplsDataDict['device_a_port_desc'] = ednMplsObj.device_a_port_desc
            ednMplsDataDict['device_a_vlan'] = ednMplsObj.device_a_vlan
            ednMplsDataDict['creation_date'] = FormatDate(ednMplsObj.creation_date)
            ednMplsDataDict['modification_date'] = FormatDate(ednMplsObj.modification_date)
            
            ednMplsObjList.append(ednMplsDataDict)

        return jsonify(ednMplsObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/deleteIgwSystemDevice",methods = ['POST'])
@token_required
def DeleteIgwSystemDevice(user_data):
    if True:#session.get('token', None):
        igwSystemObj = request.get_json()
        print(igwSystemObj,file = sys.stderr)
        
        for obj in igwSystemObj.get("ips"):
            igwSystemId = IGW_SYSTEM.query.filter(IGW_SYSTEM.igw_system_id==obj).first()
            if obj:
                db.session.delete(igwSystemId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addIgwSystemDevice",methods = ['POST'])
@token_required
def AddIgwSystemDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwSystemObj = request.get_json()

        print(igwSystemObj,file=sys.stderr)

        
        igwSystem = IGW_SYSTEM()
        igwSystem.device_a_ip = igwSystemObj['device_a_ip']
        if igwSystemObj['device_a_name']:
            igwSystem.device_a_name = igwSystemObj['device_a_name']
        if igwSystemObj['device_a_interface']:
            igwSystem.device_a_interface = igwSystemObj['device_a_interface']    
        if igwSystemObj['device_a_trunk_name']:
            igwSystem.device_a_trunk_name = igwSystemObj['device_a_trunk_name']
        if igwSystemObj['device_a_ip']:
            igwSystem.device_a_ip = igwSystemObj['device_a_ip']
        if igwSystemObj['device_b_system_name']:
            igwSystem.device_b_system_name= igwSystemObj['device_b_system_name']
        if igwSystemObj['device_b_interface']:
            igwSystem.device_b_interface = igwSystemObj['device_b_interface']
        if igwSystemObj['device_b_ip']:
            igwSystem.device_b_ip= igwSystemObj['device_b_ip']
        if igwSystemObj['device_b_type']:
            igwSystem.device_b_type= igwSystemObj['device_b_type']
        if igwSystemObj['device_b_port_desc']:
            portDesc = igwSystemObj['device_b_port_desc']
            portDesc.replace('<',"")
            portDesc.replace('>',"")
            portDesc.replace('|'," , ")
            igwSystem.device_b_port_desc= portDesc
            #igwSystem.device_b_port_desc= igwSystemObj['device_b_port_desc']
        if igwSystemObj['device_a_mac']:
            igwSystem.device_a_mac= igwSystemObj['device_a_mac']
        if igwSystemObj['device_b_mac']:
            igwSystem.device_b_mac= igwSystemObj['device_b_mac']
        if igwSystemObj['device_a_port_desc']:
            portDesc = igwSystemObj['device_a_port_desc']
            portDesc.replace('<',"")
            portDesc.replace('>',"")
            portDesc.replace('|'," , ")
            igwSystem.device_a_port_desc= portDesc
            #igwSystem.device_a_port_desc= igwSystemObj['device_a_port_desc']
        if igwSystemObj['device_a_vlan']:
            igwSystem.device_a_vlan= igwSystemObj['device_a_vlan']
     

        #print(device.sw_eol_date,file=sys.stderr)
        
        if IGW_SYSTEM.query.with_entities(IGW_SYSTEM.igw_system_id).filter_by(igw_system_id=igwSystemObj['igw_system_id']).first() is not None:
             igwSystem.igw_system_id = IGW_SYSTEM.query.with_entities(IGW_SYSTEM.igw_system_id).filter_by(igw_system_id=igwSystemObj['igw_system_id']).first()[0]
             print("Updated IGW System ID " + str(igwSystemObj['igw_system_id']),file=sys.stderr)
             igwSystem.modification_date= datetime.now(tz)
             UpdateData(igwSystem)
            
        else:
            print("Inserted Record",file=sys.stderr)
            igwSystem.creation_date= datetime.now(tz)
            igwSystem.modification_date= datetime.now(tz)
            InsertData(igwSystem)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllIgwSystemDates",methods=['GET'])
@token_required
def GetAllIgwSystemDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct CREATION_DATE from igw_system ORDER by CREATION_DATE desc;"
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllIgwSystemByDate", methods = ['POST'])
@token_required
def GetAllIgwSystemByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwSystemObjList=[]
        #igwSystemObjs = IGW_SYSTEM.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        igwSystemObjs = phy_engine.execute(f"SELECT * FROM igw_system WHERE creation_date = '{current_time}'")

        for igwSystemObj in igwSystemObjs:

            igwSystemDataDict= {}
            igwSystemDataDict['igw_system_id']=igwSystemObj['IGW_SYSTEM_ID']
            igwSystemDataDict['device_a_name'] = igwSystemObj['DEVICE_A_NAME']
            igwSystemDataDict['device_a_interface'] = igwSystemObj['DEVICE_A_INTERFACE']
            igwSystemDataDict['device_a_trunk_name'] = igwSystemObj['DEVICE_A_TRUNK_NAME']
            igwSystemDataDict['device_a_ip'] = igwSystemObj['DEVICE_A_IP']
            igwSystemDataDict['device_b_system_name'] = igwSystemObj['DEVICE_B_SYSTEM_NAME']
            igwSystemDataDict['device_b_interface'] = igwSystemObj['DEVICE_B_INTERFACE']
            igwSystemDataDict['device_b_ip'] = igwSystemObj['DEVICE_B_IP']
            igwSystemDataDict['device_b_type'] = igwSystemObj['DEVICE_B_TYPE']
            igwSystemDataDict['device_b_port_desc'] = igwSystemObj['DEVICE_B_PORT_DESC']
            igwSystemDataDict['device_a_mac'] = igwSystemObj['DEVICE_A_MAC']
            igwSystemDataDict['device_b_mac'] = igwSystemObj['DEVICE_B_MAC']
            igwSystemDataDict['device_a_port_desc'] = igwSystemObj['DEVICE_A_PORT_DESC']
            igwSystemDataDict['device_a_vlan'] = igwSystemObj['DEVICE_A_VLAN']
            igwSystemDataDict['creation_date'] = FormatDate(igwSystemObj['CREATION_DATE'])
            igwSystemDataDict['modification_date'] = FormatDate(igwSystemObj['MODIFICATION_DATE'])
            igwSystemObjList.append(igwSystemDataDict)
       
        content = gzip.compress(json.dumps(igwSystemObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addIgwSystemDevices", methods = ['POST'])
@token_required
def AddIgwSystemDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()

        print(postData,file=sys.stderr)
        time= datetime.now(tz)
        for igwSystemObj in postData:

            igwSystem = IGW_SYSTEM()
            if 'device_a_name' in igwSystemObj:
                igwSystem.device_a_name = igwSystemObj['device_a_name']
            else:
                igwSystem.device_a_name = 'N/A'
            if 'device_a_interface' in igwSystemObj:
                igwSystem.device_a_interface = igwSystemObj['device_a_interface']
            else:
                igwSystem.device_a_interface = 'N/A'
            if 'device_a_trunk_name' in igwSystemObj:
                igwSystem.device_a_trunk_name = igwSystemObj['device_a_trunk_name']
            else:
                igwSystem.device_a_trunk_name = 'N/A'
            if 'device_a_ip' in igwSystemObj:
                igwSystem.device_a_ip = igwSystemObj['device_a_ip']
            else:
                igwSystem.device_a_ip = 'N/A'
            if 'device_b_system_name' in igwSystemObj:
                igwSystem.device_b_system_name = igwSystemObj['device_b_system_name']
            else:
                igwSystem.device_b_system_name = 'N/A'
            if 'device_b_interface' in igwSystemObj:
                igwSystem.device_b_interface = igwSystemObj['device_b_interface']
            else:
                igwSystem.device_b_interface = 'N/A'
            if 'device_b_ip' in igwSystemObj:
                igwSystem.device_b_ip = igwSystemObj['device_b_ip']
            else:
                igwSystem.igw_system_id = 'N/A'
            if 'device_b_type' in igwSystemObj:
                igwSystem.device_b_type = igwSystemObj['device_b_type']
            else:
                igwSystem.device_b_type = 'N/A'
            if 'device_b_port_desc' in igwSystemObj:
                portDesc = igwSystemObj['device_b_port_desc']
                portDesc.replace('<',"")
                portDesc.replace('>',"")
                portDesc.replace('|'," , ")
                igwSystem.device_b_port_desc= portDesc
                #igwSystem.device_b_port_desc = igwSystemObj['device_b_port_desc']
            else:
                igwSystem.device_b_port_desc = 'N/A'
            if 'device_a_mac' in igwSystemObj:
                igwSystem.device_a_mac = igwSystemObj['device_a_mac']
            else:
                igwSystem.device_a_mac = 'N/A'
            if 'device_b_mac' in igwSystemObj:
                igwSystem.device_b_mac = igwSystemObj['device_b_mac']
            else:
                igwSystem.device_b_mac = 'N/A'
            if 'device_a_port_desc' in igwSystemObj:
                portDesc = igwSystemObj['device_a_port_desc']
                portDesc.replace('<',"")
                portDesc.replace('>',"")
                portDesc.replace('|'," , ")
                igwSystem.device_a_port_desc= portDesc
                #igwSystem.device_a_port_desc = igwSystemObj['device_a_port_desc']
            else:
                igwSystem.device_a_port_desc = 'N/A'
            if 'device_a_vlan' in igwSystemObj:
                igwSystem.device_a_vlan = igwSystemObj['device_a_vlan']
            else:
                igwSystem.device_a_vlan = 'N/A'

            igwSystem.creation_date= time
            igwSystem.modification_date = time
            # if Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first() is not None:
            #     seed.seed_id = Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first()[0]
            #     print("Updated " + seedObj['ne_ip_address'],file=sys.stderr)
            #     UpdateData(seed)
            # else:
            #     print("Inserted " +seedObj['ne_ip_address'],file=sys.stderr)
            #     seed.onboard_status = 'false'
            InsertData(igwSystem)
       
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/getAllIgwSystems", methods = ['GET'])
@token_required
def GetAllIgwSystem(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwSystemObjList=[]
        igwSystemObjs = phy_engine.execute(f"SELECT * FROM igw_system WHERE creation_date = (SELECT max(creation_date) FROM igw_system)")

        for igwSystemObj in igwSystemObjs:

            igwSystemDataDict= {}
            igwSystemDataDict['igw_system_id']=igwSystemObj['IGW_SYSTEM_ID']
            igwSystemDataDict['device_a_name'] = igwSystemObj['DEVICE_A_NAME']
            igwSystemDataDict['device_a_interface'] = igwSystemObj['DEVICE_A_INTERFACE']
            igwSystemDataDict['device_a_trunk_name'] = igwSystemObj['DEVICE_A_TRUNK_NAME']
            igwSystemDataDict['device_a_ip'] = igwSystemObj['DEVICE_A_IP']
            igwSystemDataDict['device_b_system_name'] = igwSystemObj['DEVICE_B_SYSTEM_NAME']
            igwSystemDataDict['device_b_interface'] = igwSystemObj['DEVICE_B_INTERFACE']
            igwSystemDataDict['device_b_ip'] = igwSystemObj['DEVICE_B_IP']
            igwSystemDataDict['device_b_type'] = igwSystemObj['DEVICE_B_TYPE']
            igwSystemDataDict['device_b_port_desc'] = igwSystemObj['DEVICE_B_PORT_DESC']
            igwSystemDataDict['device_a_mac'] = igwSystemObj['DEVICE_A_MAC']
            igwSystemDataDict['device_b_mac'] = igwSystemObj['DEVICE_B_MAC']
            igwSystemDataDict['device_a_port_desc'] = igwSystemObj['DEVICE_A_PORT_DESC']
            igwSystemDataDict['device_a_vlan'] = igwSystemObj['DEVICE_A_VLAN']
            igwSystemDataDict['creation_date'] = FormatDate(igwSystemObj['CREATION_DATE'])
            igwSystemDataDict['modification_date'] = FormatDate(igwSystemObj['MODIFICATION_DATE'])
            igwSystemObjList.append(igwSystemDataDict)
        content = gzip.compress(json.dumps(igwSystemObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/exportIgwSystem", methods = ['GET'])
@token_required
def ExportIgwSystem(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwSystemObjList=[]
        igwSystemObjs = IGW_SYSTEM.query.all()

        for igwSystemObj in igwSystemObjs:

            igwSystemDataDict= {}
            igwSystemDataDict['igw_system_id']=igwSystemObj.igw_system_id
            igwSystemDataDict['device_a_name'] = igwSystemObj.device_a_name
            igwSystemDataDict['device_a_interface'] = igwSystemObj.device_a_interface
            igwSystemDataDict['device_a_trunk_name'] = igwSystemObj.device_a_trunk_name
            igwSystemDataDict['device_a_ip'] = igwSystemObj.device_a_ip
            igwSystemDataDict['device_b_system_name'] = igwSystemObj.device_b_system_name
            igwSystemDataDict['device_b_interface'] = igwSystemObj.device_b_interface
            igwSystemDataDict['device_b_ip'] = igwSystemObj.device_b_ip
            igwSystemDataDict['device_b_type'] = igwSystemObj.device_b_type
            igwSystemDataDict['device_b_port_desc'] = igwSystemObj.device_b_port_desc
            igwSystemDataDict['device_a_mac'] = igwSystemObj.device_a_mac
            igwSystemDataDict['device_b_mac'] = igwSystemObj.device_b_mac
            igwSystemDataDict['device_a_port_desc'] = igwSystemObj.device_a_port_desc
            igwSystemDataDict['device_a_vlan'] = igwSystemObj.device_a_vlan
            igwSystemDataDict['creation_date'] = FormatDate(igwSystemObj.creation_date)
            igwSystemDataDict['modification_date'] = igwSystemObj.modification_date
            igwSystemObjList.append(igwSystemDataDict)

        return jsonify(igwSystemObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/addEdnSystemDevice",methods = ['POST'])
@token_required
def AddEdnSystemDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednSystemObj = request.get_json()

        print(ednSystemObj,file=sys.stderr)

        ednSystem = EDN_SYSTEM()
        ednSystem.device_a_ip = ednSystemObj['device_a_ip']
        if ednSystemObj['device_a_name']:
            ednSystem.device_a_name = ednSystemObj['device_a_name']
        if ednSystemObj['device_a_interface']:
            ednSystem.device_a_interface = ednSystemObj['device_a_interface']    
        if ednSystemObj['device_a_trunk_name']:
            ednSystem.device_a_trunk_name = ednSystemObj['device_a_trunk_name']
        if ednSystemObj['device_a_ip']:
            ednSystem.device_a_ip = ednSystemObj['device_a_ip']
        if ednSystemObj['device_b_system_name']:
            ednSystem.device_b_system_name= ednSystemObj['device_b_system_name']
        if ednSystemObj['device_b_interface']:
            ednSystem.device_b_interface = ednSystemObj['device_b_interface']
        if ednSystemObj['device_b_ip']:
            ednSystem.device_b_ip= ednSystemObj['device_b_ip']
        if ednSystemObj['device_b_type']:
            ednSystem.device_b_type= ednSystemObj['device_b_type']
        if ednSystemObj['device_b_port_desc']:
            portDesc = ednSystemObj['device_b_port_desc']
            portDesc.replace('<',"")
            portDesc.replace('>',"")
            portDesc.replace('|'," , ")
            ednSystem.device_b_port_desc= portDesc
            #ednSystem.device_b_port_desc= ednSystemObj['device_b_port_desc']
        if ednSystemObj['device_a_mac']:
            ednSystem.device_a_mac= ednSystemObj['device_a_mac']
        if ednSystemObj['device_b_mac']:
            ednSystem.device_b_mac= ednSystemObj['device_b_mac']
        if ednSystemObj['device_a_port_desc']:
            portDesc = ednSystemObj['device_a_port_desc']
            portDesc.replace('<',"")
            portDesc.replace('>',"")
            portDesc.replace('|'," , ")
            ednSystem.device_a_port_desc= portDesc
            #ednSystem.device_a_port_desc= ednSystemObj['device_a_port_desc']
        if ednSystemObj['device_a_vlan']:
            ednSystem.device_a_vlan= ednSystemObj['device_a_vlan']
        if 'service_vendor' in ednSystemObj:
                ednSystem.service_vendor = ednSystemObj['service_vendor']
        else:
            ednSystem.service_vendor = 'N/A'
     
        #print(device.sw_eol_date,file=sys.stderr)
        
        if EDN_SYSTEM.query.with_entities(EDN_SYSTEM.edn_system_id).filter_by(edn_system_id=ednSystemObj['edn_system_id']).first() is not None:
            ednSystem.edn_system_id = EDN_SYSTEM.query.with_entities(EDN_SYSTEM.edn_system_id).filter_by(edn_system_id=ednSystemObj['edn_system_id']).first()[0]
            print(f"Updated  {ednSystemObj['edn_system_id']}", file=sys.stderr)
            ednSystem.modification_date= datetime.now(tz)
            UpdateData(ednSystem)
            
        else:
            print("Inserted Record", file=sys.stderr)
            ednSystem.creation_date= datetime.now(tz)
            ednSystem.modification_date= datetime.now(tz)
            InsertData(ednSystem)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnSystemDates",methods=['GET'])
@token_required
def GetAllEdnSystemDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct CREATION_DATE from edn_system ORDER by CREATION_DATE desc;"
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllEdnSystemByDate", methods = ['POST'])
@token_required
def GetAllEdnSystemByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednSystemObjList=[]
        #ednSystemObjs = EDN_SYSTEM.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        ednSystemObjs = phy_engine.execute(f"SELECT * FROM edn_system WHERE creation_date = '{current_time}'")

        for ednSystemObj in ednSystemObjs:

            ednSystemDataDict= {}
            ednSystemDataDict['edn_system_id']=ednSystemObj['EDN_SYSTEM_ID']
            ednSystemDataDict['device_a_name'] = ednSystemObj['DEVICE_A_NAME']
            ednSystemDataDict['device_a_interface'] = ednSystemObj['DEVICE_A_INTERFACE']
            ednSystemDataDict['device_a_trunk_name'] = ednSystemObj['DEVICE_A_TRUNK_NAME']
            ednSystemDataDict['device_a_ip'] = ednSystemObj['DEVICE_A_IP']
            ednSystemDataDict['device_b_system_name'] = ednSystemObj['DEVICE_B_SYSTEM_NAME']
            ednSystemDataDict['device_b_interface'] = ednSystemObj['DEVICE_B_INTERFACE']
            ednSystemDataDict['device_b_ip'] = ednSystemObj['DEVICE_B_IP']
            ednSystemDataDict['device_b_type'] = ednSystemObj['DEVICE_B_TYPE']
            ednSystemDataDict['device_b_port_desc'] = ednSystemObj['DEVICE_B_PORT_DESC']
            ednSystemDataDict['device_a_mac'] = ednSystemObj['DEVICE_A_MAC']
            ednSystemDataDict['device_b_mac'] = ednSystemObj['DEVICE_B_MAC']
            ednSystemDataDict['device_a_port_desc'] = ednSystemObj['DEVICE_A_PORT_DESC']
            ednSystemDataDict['device_a_vlan'] = ednSystemObj['DEVICE_A_VLAN']
            ednSystemDataDict['service_vendor'] = ednSystemObj['SERVICE_VENDOR']
            ednSystemDataDict['creation_date'] = FormatDate(ednSystemObj['CREATION_DATE'])
            ednSystemDataDict['modification_date'] = FormatDate(ednSystemObj['MODIFICATION_DATE'])
            ednSystemObjList.append(ednSystemDataDict)
       
        content = gzip.compress(json.dumps(ednSystemObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteEdnSystemDevice",methods = ['POST'])
@token_required
def DeleteEdnSystemDevice(user_data):
    if True:#session.get('token', None):
        ednSystemObj = request.get_json()
        print(ednSystemObj,file = sys.stderr)
        
        for obj in ednSystemObj.get("ips"):
            ednSystemId = EDN_SYSTEM.query.filter(EDN_SYSTEM.edn_system_id==obj).first()
            if obj:
                db.session.delete(ednSystemId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addEdnSystemDevices", methods = ['POST'])
@token_required
def AddEdnSystemDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()

        print(postData,file=sys.stderr)
        time= datetime.now(tz)
        for ednSystemObj in postData:

            ednSystem = EDN_SYSTEM()
            if 'device_a_name' in ednSystemObj:
                ednSystem.device_a_name = ednSystemObj['device_a_name']
            else:
                ednSystem.device_a_name = 'N/A'
            if 'device_a_interface' in ednSystemObj:
                ednSystem.device_a_interface = ednSystemObj['device_a_interface']
            else:
                ednSystem.device_a_interface = 'N/A'
            if 'device_a_trunk_name' in ednSystemObj:
                ednSystem.device_a_trunk_name = ednSystemObj['device_a_trunk_name']
            else:
                ednSystem.device_a_trunk_name = 'N/A'
            if 'device_a_ip' in ednSystemObj:
                ednSystem.device_a_ip = ednSystemObj['device_a_ip']
            else:
                ednSystem.device_a_ip = 'N/A'
            if 'device_b_system_name' in ednSystemObj:
                ednSystem.device_b_system_name = ednSystemObj['device_b_system_name']
            else:
                ednSystem.device_b_system_name = 'N/A'
            if 'device_b_interface' in ednSystemObj:
                ednSystem.device_b_interface = ednSystemObj['device_b_interface']
            else:
                ednSystem.device_b_interface = 'N/A'
            if 'device_b_ip' in ednSystemObj:
                ednSystem.device_b_ip = ednSystemObj['device_b_ip']
            else:
                ednSystem.device_b_ip = 'N/A'
            if 'device_b_type' in ednSystemObj:
                ednSystem.device_b_type = ednSystemObj['device_b_type']
            else:
                ednSystem.device_b_type = 'N/A'
            if 'device_b_port_desc' in ednSystemObj:
                portDesc = ednSystemObj['device_b_port_desc']
                portDesc.replace('<',"")
                portDesc.replace('>',"")
                portDesc.replace('|'," , ")
                ednSystem.device_b_port_desc= portDesc
                #ednSystem.device_b_port_desc = ednSystemObj['device_b_port_desc']
            else:
                ednSystem.device_b_port_desc = 'N/A'
            if 'device_a_mac' in ednSystemObj:
                ednSystem.device_a_mac = ednSystemObj['device_a_mac']
            else:
                ednSystem.device_a_mac = 'N/A'
            if 'device_b_mac' in ednSystemObj:
                ednSystem.device_b_mac = ednSystemObj['device_b_mac']
            else:
                ednSystem.device_b_mac = 'N/A'
            if 'device_a_port_desc' in ednSystemObj:
                portDesc = ednSystemObj['device_a_port_desc']
                portDesc.replace('<',"")
                portDesc.replace('>',"")
                portDesc.replace('|'," , ")
                ednSystem.device_a_port_desc= portDesc
                #ednSystem.device_a_port_desc = ednSystemObj['device_a_port_desc']
            else:
                ednSystem.device_a_port_desc = 'N/A'
            if 'device_a_vlan' in ednSystemObj:
                ednSystem.device_a_vlan = ednSystemObj['device_a_vlan']
            else:
                ednSystem.device_a_vlan = 'N/A'
            if 'service_vendor' in ednSystemObj:
                ednSystem.service_vendor = ednSystemObj['service_vendor']
            else:
                ednSystem.service_vendor = 'N/A'
            ednSystem.creation_date= time
            ednSystem.modification_date= time
            # if Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first() is not None:
            #     seed.seed_id = Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first()[0]
            #     print("Updated " + seedObj['ne_ip_address'],file=sys.stderr)
            #     UpdateData(seed)
            # else:
            #     print("Inserted " +seedObj['ne_ip_address'],file=sys.stderr)
            #     seed.onboard_status = 'false'
            InsertData(ednSystem)
       
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnMappings", methods = ['GET'])   
@token_required 
def GetAllEdnMappings(user_data):
    """
        Get all EDN Mappings endpoint
        ---
        description: Get all EDN Mappings
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true

        responses:
            200:
                description: All Datacenters to be returned from inventory DB
                schema:
                    type: array
                    items:
                        type: object
                        properties:
                            device_a_name:
                                type: string
                            device_a_interface:
                                type: string
                            device_a_trunk_name:
                                type: string
                            device_a_ip:
                                type: string
                            device_b_system_name:
                                type: string

                            device_b_interface:
                                type: string
                            device_b_ip:
                                type: string
                            device_b_type:
                                type: string
                            device_b_port_desc:
                                type: string
                            device_a_mac:
                                type: string
                            device_b_mac:
                                type: string
                            device_a_port_desc:
                                type: string
                            device_a_vlan:
                                type: string
                            server_name:
                                type: string
                            owner_name:
                                type: string
                            owner_email:
                                type: string
                            owner_contact:
                                type: string            
                            creation_date:
                                type: date
                                example: "2019-05-17 12:12:12"
                            modification_date:
                                type: date
                                example: "2019-05-17 12:12:12"
                            
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednMappingObjList=[]
        ednMappingObjList= GetAllEdnMappingsFunc(user_data)
        content = gzip.compress(json.dumps(ednMappingObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def GetAllEdnMappingsFunc(user_data):

    ednMappingObjList=[]
    
    #ednCdpLegacyObjs = EDN_CDP_LEGACY.query.all()
    ednCdpLegacyObjs = phy_engine.execute('SELECT * FROM edn_cdp_legacy WHERE creation_date = (SELECT max(creation_date) FROM edn_cdp_legacy)')

    #ednLldpAciObjs = EDN_LLDP_ACI.query.all()
    #ednLldpAciObjs = phy_engine.execute('SELECT * FROM edn_lldp_aci WHERE creation_date = (SELECT max(creation_date) FROM edn_lldp_aci)')

    #ednMacLegacyObjs = EDN_MAC_LEGACY.query.all()  
    ednMacLegacyObjs = phy_engine.execute('SELECT * FROM edn_mac_legacy WHERE creation_date = (SELECT max(creation_date) FROM edn_mac_legacy)')
    
    #ednMplsObjs = EDN_MPLS.query.all()
    ednMplsObjs = phy_engine.execute(f'SELECT * FROM edn_mpls WHERE creation_date = (SELECT max(creation_date) FROM edn_mpls)')

    #ednSecurityObjs = EDN_SECURITY.query.all()
    ednSecurityObjs = phy_engine.execute(f"SELECT * FROM edn_security WHERE creation_date = (SELECT max(creation_date) FROM edn_security)")

    #ednSystemObjs = EDN_SYSTEM.query.all()
    ednSystemObjs = phy_engine.execute(f"SELECT * FROM edn_system WHERE creation_date = (SELECT max(creation_date) FROM edn_system)")
    
    #ednIptObjs = EDN_IPT.query.all()
    ednIptObjs = phy_engine.execute(f"SELECT * FROM edn_ipt WHERE creation_date = (SELECT max(creation_date) FROM edn_ipt)")
    
    #ednExecVideoEpsObjs = EDN_EXEC_VIDEO_EPS.query.all()
    ednExecVideoEPsObjs = phy_engine.execute(f"SELECT * FROM edn_exec_video_eps WHERE creation_date = (SELECT max(creation_date) FROM edn_exec_video_eps)")

    #ednLldpLegacyObjs = EDN_LLDP_LEGACY.query.all()
    ednLldpLegacyObjs = phy_engine.execute('SELECT * FROM edn_lldp_legacy WHERE creation_date = (SELECT max(creation_date) FROM edn_lldp_legacy)')

    for ednCdpLegacyObj in ednCdpLegacyObjs:
            ednCdpLegacyDataDict= {}
            ednCdpLegacyDataDict['edn_cdp_legacy_id']=ednCdpLegacyObj['EDN_CDP_LEGACY_ID']
            ednCdpLegacyDataDict['device_a_name'] = ednCdpLegacyObj['DEVICE_A_NAME']
            ednCdpLegacyDataDict['device_a_interface'] = ednCdpLegacyObj['DEVICE_A_INTERFACE']
            ednCdpLegacyDataDict['device_a_trunk_name'] = ednCdpLegacyObj['DEVICE_A_TRUNK_NAME']
            ednCdpLegacyDataDict['device_a_ip'] = ednCdpLegacyObj['DEVICE_A_IP']
            ednCdpLegacyDataDict['device_b_system_name'] = ednCdpLegacyObj['DEVICE_B_SYSTEM_NAME']
            ednCdpLegacyDataDict['device_b_interface'] = ednCdpLegacyObj['DEVICE_B_INTERFACE']
            ednCdpLegacyDataDict['device_b_ip'] = ednCdpLegacyObj['DEVICE_B_IP']
            ednCdpLegacyDataDict['device_b_type'] = ednCdpLegacyObj['DEVICE_B_TYPE']
            ednCdpLegacyDataDict['device_b_port_desc'] = ednCdpLegacyObj['DEVICE_B_PORT_DESC']
            ednCdpLegacyDataDict['device_a_mac'] = ednCdpLegacyObj['DEVICE_A_MAC']
            ednCdpLegacyDataDict['device_b_mac'] = ednCdpLegacyObj['DEVICE_B_MAC']
            ednCdpLegacyDataDict['device_a_port_desc'] = ednCdpLegacyObj['DEVICE_A_PORT_DESC']
            ednCdpLegacyDataDict['device_a_vlan'] = ednCdpLegacyObj['DEVICE_A_VLAN']
            ednCdpLegacyDataDict['server_name'] = ednCdpLegacyObj['SERVER_NAME']
            ednCdpLegacyDataDict['server_os'] = ednCdpLegacyObj['SERVER_OS']
            ednCdpLegacyDataDict['app_name'] = ednCdpLegacyObj['APP_NAME']
            ednCdpLegacyDataDict['owner_name'] = ednCdpLegacyObj['OWNER_NAME']
            ednCdpLegacyDataDict['owner_email'] = ednCdpLegacyObj['OWNER_EMAIL']
            ednCdpLegacyDataDict['owner_contact'] = ednCdpLegacyObj['OWNER_CONTACT']
            ednCdpLegacyDataDict['creation_date'] = FormatDate(ednCdpLegacyObj['CREATION_DATE'])
            ednCdpLegacyDataDict['modification_date'] = FormatDate(ednCdpLegacyObj['MODIFICATION_DATE'])
            ednCdpLegacyDataDict['device_b_mac_vendor'] = ednCdpLegacyObj["DEVICE_B_MAC_VENDOR"]
            ednCdpLegacyDataDict['service_vendor'] = ednCdpLegacyObj["SERVICE_VENDOR"]

            ednMappingObjList.append(ednCdpLegacyDataDict)
    '''
    for ednLldpAciObj in ednLldpAciObjs:
        ednLldpAciDataDict= {}
        ednLldpAciDataDict['edn_lldp_aci_id']=ednLldpAciObj['EDN_LLDP_ACI_ID']
        ednLldpAciDataDict['device_a_name'] = ednLldpAciObj['DEVICE_A_NAME']
        ednLldpAciDataDict['device_a_interface'] = ednLldpAciObj['DEVICE_A_INTERFACE']
        ednLldpAciDataDict['device_a_trunk_name'] = ednLldpAciObj['DEVICE_A_TRUNK_NAME']
        ednLldpAciDataDict['device_a_ip'] = ednLldpAciObj['DEVICE_A_IP']
        ednLldpAciDataDict['device_b_system_name'] = ednLldpAciObj['DEVICE_B_SYSTEM_NAME']
        ednLldpAciDataDict['device_b_interface'] = ednLldpAciObj['DEVICE_B_INTERFACE']
        ednLldpAciDataDict['device_b_ip'] = ednLldpAciObj['DEVICE_B_IP']
        ednLldpAciDataDict['device_b_type'] = ednLldpAciObj['DEVICE_B_TYPE']
        ednLldpAciDataDict['device_b_port_desc'] = ednLldpAciObj['DEVICE_B_PORT_DESC']
        ednLldpAciDataDict['device_a_mac'] = ednLldpAciObj['DEVICE_A_MAC']
        ednLldpAciDataDict['device_b_mac'] = ednLldpAciObj['DEVICE_B_MAC']
        ednLldpAciDataDict['device_a_port_desc'] = ednLldpAciObj['DEVICE_A_PORT_DESC']
        ednLldpAciDataDict['device_a_vlan'] = ednLldpAciObj['DEVICE_A_VLAN']
        ednLldpAciDataDict['device_a_vlan_name'] = ednLldpAciObj["DEVICE_A_VLAN_NAME"]
        ednLldpAciDataDict['server_name'] = ednLldpAciObj['SERVER_NAME']
        ednLldpAciDataDict['server_os'] = ednLldpAciObj['SERVER_OS']
        ednLldpAciDataDict['app_name'] = ednLldpAciObj['APP_NAME']
        ednLldpAciDataDict['owner_name'] = ednLldpAciObj['OWNER_NAME']
        ednLldpAciDataDict['owner_email'] = ednLldpAciObj['OWNER_EMAIL']
        ednLldpAciDataDict['owner_contact'] = ednLldpAciObj['OWNER_CONTACT']
        ednLldpAciDataDict['creation_date'] = FormatDate(ednLldpAciObj['CREATION_DATE'])
        ednLldpAciDataDict['modification_date'] = FormatDate(ednLldpAciObj['MODIFICATION_DATE'])
        ednMappingObjList.append(ednLldpAciDataDict)
    '''
    
    for ednMacLegacyObj in ednMacLegacyObjs:
        ednMacLegacyDataDict= {}
        ednMacLegacyDataDict['edn_mac_legacy_id']=ednMacLegacyObj["EDN_MAC_LEGACY_ID"]
        ednMacLegacyDataDict['device_a_name'] = ednMacLegacyObj["DEVICE_A_NAME"]
        ednMacLegacyDataDict['device_a_interface'] = ednMacLegacyObj["DEVICE_A_INTERFACE"]
        ednMacLegacyDataDict['device_a_trunk_name'] = ednMacLegacyObj["DEVICE_A_TRUNK_NAME"]
        ednMacLegacyDataDict['device_a_ip'] = ednMacLegacyObj["DEVICE_A_IP"]
        ednMacLegacyDataDict['device_b_system_name'] = ednMacLegacyObj["DEVICE_B_SYSTEM_NAME"]
        ednMacLegacyDataDict['device_b_interface'] = ednMacLegacyObj["DEVICE_B_INTERFACE"]
        ednMacLegacyDataDict['device_b_ip'] = ednMacLegacyObj["DEVICE_B_IP"]
        ednMacLegacyDataDict['device_b_type'] = ednMacLegacyObj["DEVICE_B_TYPE"]
        ednMacLegacyDataDict['device_b_port_desc'] = ednMacLegacyObj["DEVICE_B_PORT_DESC"]
        ednMacLegacyDataDict['device_a_mac'] = ednMacLegacyObj["DEVICE_A_MAC"]
        ednMacLegacyDataDict['device_b_mac'] = ednMacLegacyObj["DEVICE_B_MAC"]
        ednMacLegacyDataDict['device_a_port_desc'] = ednMacLegacyObj["DEVICE_A_PORT_DESC"]
        ednMacLegacyDataDict['device_a_vlan'] = ednMacLegacyObj["DEVICE_A_VLAN"]
        ednMacLegacyDataDict['arp_source_name'] = ednMacLegacyObj["ARP_SOURCE_NAME"]
        ednMacLegacyDataDict['arp_source_type'] = ednMacLegacyObj["ARP_SOURCE_TYPE"]
        ednMacLegacyDataDict['service_vendor'] = ednMacLegacyObj["SERVICE_VENDOR"]
        ednMacLegacyDataDict['device_b_mac_vendor'] = ednMacLegacyObj["DEVICE_B_MAC_VENDOR"]
        ednMacLegacyDataDict['server_name'] = ednMacLegacyObj["SERVER_NAME"]
        ednMacLegacyDataDict['server_os'] = ednMacLegacyObj["SERVER_OS"]
        ednMacLegacyDataDict['app_name'] = ednMacLegacyObj["APP_NAME"]
        ednMacLegacyDataDict['owner_name'] = ednMacLegacyObj["OWNER_NAME"]
        ednMacLegacyDataDict['owner_email'] = ednMacLegacyObj["OWNER_EMAIL"]
        ednMacLegacyDataDict['owner_contact'] = ednMacLegacyObj["OWNER_CONTACT"]
        ednMacLegacyDataDict['service_matched_by'] = ednMacLegacyObj["SERVICE_MATCHED_BY"]
        ednMacLegacyDataDict['modified_by'] = ednMacLegacyObj["MODIFIED_BY"]
        ednMacLegacyDataDict['device_a_rx'] = ednMacLegacyObj["DEVICE_A_RX"]
        ednMacLegacyDataDict['device_a_tx'] = ednMacLegacyObj["DEVICE_A_TX"]
        ednMacLegacyDataDict['f5_lb'] = ednMacLegacyObj["F5_LB"]
        ednMacLegacyDataDict['f5_vip'] = ednMacLegacyObj["F5_VIP"]
        ednMacLegacyDataDict['f5_node_status'] = ednMacLegacyObj["F5_NODE_STATUS"]
        ednMacLegacyDataDict['creation_date'] = FormatDate(ednMacLegacyObj["CREATION_DATE"])
        ednMacLegacyDataDict['modification_date'] = FormatDate(ednMacLegacyObj["MODIFICATION_DATE"])
        if ednMacLegacyObj["DEVICE_B_SYSTEM_NAME"] and ednMacLegacyObj["DEVICE_B_SYSTEM_NAME"]!='':
            ednMappingObjList.append(ednMacLegacyDataDict) 

    for ednMplsObj in ednMplsObjs:
        ednMplsDataDict= {}
        ednMplsDataDict['edn_mpls_id']=ednMplsObj['EDN_MPLS_ID']
        ednMplsDataDict['device_a_name'] = ednMplsObj['DEVICE_A_NAME']
        ednMplsDataDict['device_a_interface'] = ednMplsObj['DEVICE_A_INTERFACE']
        ednMplsDataDict['device_a_trunk_name'] = ednMplsObj['DEVICE_A_TRUNK_NAME']
        ednMplsDataDict['device_a_ip'] = ednMplsObj['DEVICE_A_IP']
        ednMplsDataDict['device_b_system_name'] = ednMplsObj['DEVICE_B_SYSTEM_NAME']
        ednMplsDataDict['device_b_interface'] = ednMplsObj['DEVICE_B_INTERFACE']
        ednMplsDataDict['device_b_ip'] = ednMplsObj['DEVICE_B_IP']
        ednMplsDataDict['device_b_type'] = ednMplsObj['DEVICE_B_TYPE']
        ednMplsDataDict['device_b_port_desc'] = ednMplsObj['DEVICE_B_PORT_DESC']
        ednMplsDataDict['device_a_mac'] = ednMplsObj['DEVICE_A_MAC']
        ednMplsDataDict['device_b_mac'] = ednMplsObj['DEVICE_B_MAC']
        ednMplsDataDict['device_a_port_desc'] = ednMplsObj['DEVICE_A_PORT_DESC']
        ednMplsDataDict['device_a_vlan'] = ednMplsObj['DEVICE_A_VLAN']
        ednMplsDataDict['service_vendor'] = ednMplsObj['SERVICE_VENDOR']
        ednMplsDataDict['creation_date'] = FormatDate(ednMplsObj['CREATION_DATE'])
        ednMplsDataDict['modification_date'] = FormatDate(ednMplsObj['MODIFICATION_DATE'])
        ednMappingObjList.append(ednMplsDataDict)

    for ednSecurityObj in ednSecurityObjs:
        ednSecurityDataDict= {}
        ednSecurityDataDict['edn_security_id']=ednSecurityObj['EDN_SECURITY_ID']
        ednSecurityDataDict['device_a_name'] = ednSecurityObj['DEVICE_A_NAME']
        ednSecurityDataDict['device_a_interface'] = ednSecurityObj['DEVICE_A_INTERFACE']
        ednSecurityDataDict['device_a_trunk_name'] = ednSecurityObj['DEVICE_A_TRUNK_NAME']
        ednSecurityDataDict['device_a_ip'] = ednSecurityObj['DEVICE_A_IP']
        ednSecurityDataDict['device_b_system_name'] = ednSecurityObj['DEVICE_B_SYSTEM_NAME']
        ednSecurityDataDict['device_b_interface'] = ednSecurityObj['DEVICE_B_INTERFACE']
        ednSecurityDataDict['device_b_ip'] = ednSecurityObj['DEVICE_B_IP']
        ednSecurityDataDict['device_b_type'] = ednSecurityObj['DEVICE_B_TYPE']
        ednSecurityDataDict['device_b_port_desc'] = ednSecurityObj['DEVICE_B_PORT_DESC']
        ednSecurityDataDict['device_a_mac'] = ednSecurityObj['DEVICE_A_MAC']
        ednSecurityDataDict['device_b_mac'] = ednSecurityObj['DEVICE_B_MAC']
        ednSecurityDataDict['device_a_port_desc'] = ednSecurityObj['DEVICE_A_PORT_DESC']
        ednSecurityDataDict['device_a_vlan'] = ednSecurityObj['DEVICE_A_VLAN']
        ednSecurityDataDict['service_vendor'] = ednSecurityObj['SERVICE_VENDOR']
        ednSecurityDataDict['creation_date'] = FormatDate(ednSecurityObj['CREATION_DATE'])
        ednSecurityDataDict['modification_date'] = FormatDate(ednSecurityObj['MODIFICATION_DATE'])
        ednMappingObjList.append(ednSecurityDataDict)  
    
    for ednSystemObj in ednSystemObjs:

        ednSystemDataDict= {}
        ednSystemDataDict['edn_system_id']=ednSystemObj['EDN_SYSTEM_ID']
        ednSystemDataDict['device_a_name'] = ednSystemObj['DEVICE_A_NAME']
        ednSystemDataDict['device_a_interface'] = ednSystemObj['DEVICE_A_INTERFACE']
        ednSystemDataDict['device_a_trunk_name'] = ednSystemObj['DEVICE_A_TRUNK_NAME']
        ednSystemDataDict['device_a_ip'] = ednSystemObj['DEVICE_A_IP']
        ednSystemDataDict['device_b_system_name'] = ednSystemObj['DEVICE_B_SYSTEM_NAME']
        ednSystemDataDict['device_b_interface'] = ednSystemObj['DEVICE_B_INTERFACE']
        ednSystemDataDict['device_b_ip'] = ednSystemObj['DEVICE_B_IP']
        ednSystemDataDict['device_b_type'] = ednSystemObj['DEVICE_B_TYPE']
        ednSystemDataDict['device_b_port_desc'] = ednSystemObj['DEVICE_B_PORT_DESC']
        ednSystemDataDict['device_a_mac'] = ednSystemObj['DEVICE_A_MAC']
        ednSystemDataDict['device_b_mac'] = ednSystemObj['DEVICE_B_MAC']
        ednSystemDataDict['device_a_port_desc'] = ednSystemObj['DEVICE_A_PORT_DESC']
        ednSystemDataDict['device_a_vlan'] = ednSystemObj['DEVICE_A_VLAN']
        ednSystemDataDict['service_vendor'] = ednSystemObj['SERVICE_VENDOR']
        ednSystemDataDict['creation_date'] = FormatDate(ednSystemObj['CREATION_DATE'])
        ednSystemDataDict['modification_date'] = FormatDate(ednSystemObj['MODIFICATION_DATE'])
        ednMappingObjList.append(ednSystemDataDict)

    for ednIptObj in ednIptObjs:

        ednIptDataDict= {}
        ednIptDataDict['edn_ipt_id']=ednIptObj['EDN_IPT_ID']
        ednIptDataDict['device_a_name'] = ednIptObj['DEVICE_A_NAME']
        ednIptDataDict['device_a_interface'] = ednIptObj['DEVICE_A_INTERFACE']
        ednIptDataDict['device_a_trunk_name'] = ednIptObj['DEVICE_A_TRUNK_NAME']
        ednIptDataDict['device_a_ip'] = ednIptObj['DEVICE_A_IP']
        ednIptDataDict['device_b_system_name'] = ednIptObj['DEVICE_B_SYSTEM_NAME']
        ednIptDataDict['device_b_interface'] = ednIptObj['DEVICE_B_INTERFACE']
        ednIptDataDict['device_b_ip'] = ednIptObj['DEVICE_B_IP']
        ednIptDataDict['device_b_type'] = ednIptObj['DEVICE_B_TYPE']
        ednIptDataDict['device_b_port_desc'] = ednIptObj['DEVICE_B_PORT_DESC']
        ednIptDataDict['device_a_mac'] = ednIptObj['DEVICE_A_MAC']
        ednIptDataDict['device_b_mac'] = ednIptObj['DEVICE_B_MAC']
        ednIptDataDict['device_a_port_desc'] = ednIptObj['DEVICE_A_PORT_DESC']
        ednIptDataDict['device_a_vlan'] = ednIptObj['DEVICE_A_VLAN']
        ednIptDataDict['service_vendor'] = ednIptObj['SERVICE_VENDOR']
        ednIptDataDict['creation_date'] = FormatDate(ednIptObj['CREATION_DATE'])
        ednIptDataDict['modification_date'] = FormatDate(ednIptObj['MODIFICATION_DATE'])
        ednMappingObjList.append(ednIptDataDict)

    for ednExecVideoEPsObj in ednExecVideoEPsObjs:

        ednExecVideoEPsDataDict= {}
        ednExecVideoEPsDataDict['ipt_exec_video_eps_id']=ednExecVideoEPsObj['IPT_EXEC_VIDEO_EPS_ID']
        ednExecVideoEPsDataDict['device_a_name'] = ednExecVideoEPsObj['DEVICE_A_NAME']
        ednExecVideoEPsDataDict['device_a_interface'] = ednExecVideoEPsObj['DEVICE_A_INTERFACE']
        ednExecVideoEPsDataDict['device_a_trunk_name'] = ednExecVideoEPsObj['DEVICE_A_TRUNK_NAME']
        ednExecVideoEPsDataDict['device_a_ip'] = ednExecVideoEPsObj['DEVICE_A_IP']
        ednExecVideoEPsDataDict['device_b_system_name'] = ednExecVideoEPsObj['DEVICE_B_SYSTEM_NAME']
        ednExecVideoEPsDataDict['device_b_interface'] = ednExecVideoEPsObj['DEVICE_B_INTERFACE']
        ednExecVideoEPsDataDict['device_b_ip'] = ednExecVideoEPsObj['DEVICE_B_IP']
        ednExecVideoEPsDataDict['device_b_type'] = ednExecVideoEPsObj['DEVICE_B_TYPE']
        ednExecVideoEPsDataDict['device_b_port_desc'] = ednExecVideoEPsObj['DEVICE_B_PORT_DESC']
        ednExecVideoEPsDataDict['device_a_mac'] = ednExecVideoEPsObj['DEVICE_A_MAC']
        ednExecVideoEPsDataDict['device_b_mac'] = ednExecVideoEPsObj['DEVICE_B_MAC']
        ednExecVideoEPsDataDict['device_a_port_desc'] = ednExecVideoEPsObj['DEVICE_A_PORT_DESC']
        ednExecVideoEPsDataDict['device_a_vlan'] = ednExecVideoEPsObj['DEVICE_A_VLAN']
        ednExecVideoEPsDataDict['service_vendor'] = ednExecVideoEPsObj['SERVICE_VENDOR']
        ednExecVideoEPsDataDict['creation_date'] = FormatDate(ednExecVideoEPsObj['CREATION_DATE'])
        ednExecVideoEPsDataDict['modification_date'] = FormatDate(ednExecVideoEPsObj['MODIFICATION_DATE'])
        ednMappingObjList.append(ednExecVideoEPsDataDict)

    for ednLldpLegacyObj in ednLldpLegacyObjs:

        ednLldpLegacyDataDict= {}
        ednLldpLegacyDataDict['edn_lldp_legacy_id']=ednLldpLegacyObj['EDN_LLDP_LEGACY_ID']
        ednLldpLegacyDataDict['device_a_name'] = ednLldpLegacyObj['DEVICE_A_NAME']
        ednLldpLegacyDataDict['device_a_interface'] = ednLldpLegacyObj['DEVICE_A_INTERFACE']
        ednLldpLegacyDataDict['device_a_trunk_name'] = ednLldpLegacyObj['DEVICE_A_TRUNK_NAME']
        ednLldpLegacyDataDict['device_a_ip'] = ednLldpLegacyObj['DEVICE_A_IP']
        ednLldpLegacyDataDict['device_b_system_name'] = ednLldpLegacyObj['DEVICE_B_SYSTEM_NAME']
        ednLldpLegacyDataDict['device_b_interface'] = ednLldpLegacyObj['DEVICE_B_INTERFACE']
        ednLldpLegacyDataDict['device_b_ip'] = ednLldpLegacyObj['DEVICE_B_IP']
        ednLldpLegacyDataDict['device_b_type'] = ednLldpLegacyObj['DEVICE_B_TYPE']
        ednLldpLegacyDataDict['device_b_port_desc'] = ednLldpLegacyObj['DEVICE_B_PORT_DESC']
        ednLldpLegacyDataDict['device_a_mac'] = ednLldpLegacyObj['DEVICE_A_MAC']
        ednLldpLegacyDataDict['device_b_mac'] = ednLldpLegacyObj['DEVICE_B_MAC']
        ednLldpLegacyDataDict['device_a_port_desc'] = ednLldpLegacyObj['DEVICE_A_PORT_DESC']
        ednLldpLegacyDataDict['device_a_vlan'] = ednLldpLegacyObj['DEVICE_A_VLAN']
        ednLldpLegacyDataDict['server_name'] = ednLldpLegacyObj['SERVER_NAME']
        ednLldpLegacyDataDict['server_os'] = ednLldpLegacyObj['SERVER_OS']
        ednLldpLegacyDataDict['app_name'] = ednLldpLegacyObj['APP_NAME']
        ednLldpLegacyDataDict['owner_name'] = ednLldpLegacyObj['OWNER_NAME']
        ednLldpLegacyDataDict['owner_email'] = ednLldpLegacyObj['OWNER_EMAIL']
        ednLldpLegacyDataDict['owner_contact'] = ednLldpLegacyObj['OWNER_CONTACT']
        ednLldpLegacyDataDict['service_vendor'] = ednLldpLegacyObj['SERVICE_VENDOR']
        ednLldpLegacyDataDict['creation_date'] = FormatDate(ednLldpLegacyObj['CREATION_DATE'])
        ednLldpLegacyDataDict['modification_date'] = FormatDate(ednLldpLegacyObj['MODIFICATION_DATE'])
        ednLldpLegacyDataDict['device_b_mac_vendor'] = ednLldpLegacyObj["DEVICE_B_MAC_VENDOR"]
        ednMappingObjList.append(ednLldpLegacyDataDict)


    

    return ednMappingObjList

@app.route("/getAllIgwMappings", methods = ['GET']) 
@token_required   
def getAllIgwMappings(user_data):
    """
        Get all EDN Mappings endpoint
        ---
        description: Get all EDN Mappings
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true

        responses:
            200:
                description: All Datacenters to be returned from inventory DB
                schema:
                    type: array
                    items:
                        type: object
                        properties:
                            device_a_name:
                                type: string
                            device_a_interface:
                                type: string
                            device_a_trunk_name:
                                type: string
                            device_a_ip:
                                type: string
                            device_b_system_name:
                                type: string

                            device_b_interface:
                                type: string
                            device_b_ip:
                                type: string
                            device_b_type:
                                type: string
                            device_b_port_desc:
                                type: string
                            device_a_mac:
                                type: string
                            device_b_mac:
                                type: string
                            device_a_port_desc:
                                type: string
                            device_a_vlan:
                                type: string
                            server_name:
                                type: string
                            owner_name:
                                type: string
                            owner_email:
                                type: string
                            owner_contact:
                                type: string            
                            creation_date:
                                type: date
                                example: "2019-05-17 12:12:12"
                            modification_date:
                                type: date
                                example: "2019-05-17 12:12:12"
                            
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):        
        igwMappingObjList=[]
        igwMappingObjList= getAllIgwMappingsFunc(user_data)
        content = gzip.compress(json.dumps(igwMappingObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def getAllIgwMappingsFunc(user_data):
    
    igwMappingObjList=[]

    #igwCdpObjs = IGW_CDP_LEGACY.query.all()
    igwCdpObjs = phy_engine.execute('SELECT * FROM igw_cdp_legacy WHERE creation_date = (SELECT max(creation_date) FROM igw_cdp_legacy)')

    #igwLldpAciObjs = IGW_LLDP_ACI.query.all()
    #igwLldpAciObjs = phy_engine.execute('SELECT * FROM igw_lldp_aci WHERE creation_date = (SELECT max(creation_date) FROM igw_lldp_aci)')

    #igwSystemObjs = IGW_SYSTEM.query.all()
    igwSystemObjs = phy_engine.execute(f"SELECT * FROM igw_system WHERE creation_date = (SELECT max(creation_date) FROM igw_system)")

    igwLldpLegacyObjs = phy_engine.execute('SELECT * FROM igw_lldp_legacy WHERE creation_date = (SELECT max(creation_date) FROM igw_lldp_legacy)')

    igwMacLegacyObjs = phy_engine.execute('SELECT * FROM igw_mac_legacy WHERE creation_date = (SELECT max(creation_date) FROM igw_mac_legacy)')


    for igwCdpLegacyObj in igwCdpObjs:

        igwCdpLegacyDataDict= {}
        igwCdpLegacyDataDict['igw_cdp_legacy_id']=igwCdpLegacyObj['IGW_CDP_LEGACY_ID']
        igwCdpLegacyDataDict['device_a_name'] = igwCdpLegacyObj['DEVICE_A_NAME']
        igwCdpLegacyDataDict['device_a_interface'] = igwCdpLegacyObj['DEVICE_A_INTERFACE']
        igwCdpLegacyDataDict['device_a_trunk_name'] = igwCdpLegacyObj['DEVICE_A_TRUNK_NAME']
        igwCdpLegacyDataDict['device_a_ip'] = igwCdpLegacyObj['DEVICE_A_IP']
        igwCdpLegacyDataDict['device_b_system_name'] = igwCdpLegacyObj['DEVICE_B_SYSTEM_NAME']
        igwCdpLegacyDataDict['device_b_interface'] = igwCdpLegacyObj['DEVICE_B_INTERFACE']
        igwCdpLegacyDataDict['device_b_ip'] = igwCdpLegacyObj['DEVICE_B_IP']
        igwCdpLegacyDataDict['device_b_type'] = igwCdpLegacyObj['DEVICE_B_TYPE']
        igwCdpLegacyDataDict['device_b_port_desc'] = igwCdpLegacyObj['DEVICE_B_PORT_DESC']
        igwCdpLegacyDataDict['device_a_mac'] = igwCdpLegacyObj['DEVICE_A_MAC']
        igwCdpLegacyDataDict['device_b_mac'] = igwCdpLegacyObj['DEVICE_B_MAC']
        igwCdpLegacyDataDict['device_a_port_desc'] = igwCdpLegacyObj['DEVICE_A_PORT_DESC']
        igwCdpLegacyDataDict['device_a_vlan'] = igwCdpLegacyObj['DEVICE_A_VLAN']
        igwCdpLegacyDataDict['server_name'] = igwCdpLegacyObj['SERVER_NAME']
        igwCdpLegacyDataDict['server_os'] = igwCdpLegacyObj['SERVER_OS']
        igwCdpLegacyDataDict['app_name'] = igwCdpLegacyObj['APP_NAME']
        igwCdpLegacyDataDict['owner_name'] = igwCdpLegacyObj['OWNER_NAME']
        igwCdpLegacyDataDict['owner_email'] = igwCdpLegacyObj['OWNER_EMAIL']
        igwCdpLegacyDataDict['owner_contact'] = igwCdpLegacyObj['OWNER_CONTACT']
        igwCdpLegacyDataDict['creation_date'] = FormatDate(igwCdpLegacyObj['CREATION_DATE'])
        igwCdpLegacyDataDict['modification_date'] = FormatDate(igwCdpLegacyObj['MODIFICATION_DATE'])
        igwCdpLegacyDataDict['device_b_mac_vendor'] = igwCdpLegacyObj["DEVICE_B_MAC_VENDOR"]
        igwCdpLegacyDataDict['service_vendor'] = igwCdpLegacyObj["SERVICE_VENDOR"]
        igwMappingObjList.append(igwCdpLegacyDataDict)
    '''
    for IgwLldpAciObj in igwLldpAciObjs:

        IgwLldpAciDataDict= {}
        IgwLldpAciDataDict['igw_lldp_aci_id']=IgwLldpAciObj['IGW_LLDP_ACI_ID']
        IgwLldpAciDataDict['device_a_name'] = IgwLldpAciObj['DEVICE_A_NAME']
        IgwLldpAciDataDict['device_a_interface'] = IgwLldpAciObj['DEVICE_A_INTERFACE']
        IgwLldpAciDataDict['device_a_trunk_name'] = IgwLldpAciObj['DEVICE_A_TRUNK_NAME']
        IgwLldpAciDataDict['device_a_ip'] = IgwLldpAciObj['DEVICE_A_IP']
        IgwLldpAciDataDict['device_b_system_name'] = IgwLldpAciObj['DEVICE_B_SYSTEM_NAME']
        IgwLldpAciDataDict['device_b_interface'] = IgwLldpAciObj['DEVICE_B_INTERFACE']
        IgwLldpAciDataDict['device_b_ip'] = IgwLldpAciObj['DEVICE_B_IP']
        IgwLldpAciDataDict['device_b_type'] = IgwLldpAciObj['DEVICE_B_TYPE']
        IgwLldpAciDataDict['device_b_port_desc'] = IgwLldpAciObj['DEVICE_B_PORT_DESC']
        IgwLldpAciDataDict['device_a_mac'] = IgwLldpAciObj['DEVICE_A_MAC']
        IgwLldpAciDataDict['device_b_mac'] = IgwLldpAciObj['DEVICE_B_MAC']
        IgwLldpAciDataDict['device_a_port_desc'] = IgwLldpAciObj['DEVICE_A_PORT_DESC']
        IgwLldpAciDataDict['device_a_vlan'] = IgwLldpAciObj['DEVICE_A_VLAN']
        IgwLldpAciDataDict['device_a_vlan_name'] = IgwLldpAciObj["DEVICE_A_VLAN_NAME"]
        IgwLldpAciDataDict['server_name'] = IgwLldpAciObj['SERVER_NAME']
        IgwLldpAciDataDict['server_os'] = IgwLldpAciObj['SERVER_OS']
        IgwLldpAciDataDict['app_name'] = IgwLldpAciObj['APP_NAME']
        IgwLldpAciDataDict['owner_name'] = IgwLldpAciObj['OWNER_NAME']
        IgwLldpAciDataDict['owner_email'] = IgwLldpAciObj['OWNER_EMAIL']
        IgwLldpAciDataDict['owner_contact'] = IgwLldpAciObj['OWNER_CONTACT']
        IgwLldpAciDataDict['creation_date'] = FormatDate(IgwLldpAciObj['CREATION_DATE'])
        IgwLldpAciDataDict['modification_date'] = FormatDate(IgwLldpAciObj['MODIFICATION_DATE'])
    
        igwMappingObjList.append(IgwLldpAciDataDict)
    '''
    for igwSystemObj in igwSystemObjs:
        igwSystemDataDict= {}
        igwSystemDataDict['igw_system_id']=igwSystemObj['IGW_SYSTEM_ID']
        igwSystemDataDict['device_a_name'] = igwSystemObj['DEVICE_A_NAME']
        igwSystemDataDict['device_a_interface'] = igwSystemObj['DEVICE_A_INTERFACE']
        igwSystemDataDict['device_a_trunk_name'] = igwSystemObj['DEVICE_A_TRUNK_NAME']
        igwSystemDataDict['device_a_ip'] = igwSystemObj['DEVICE_A_IP']
        igwSystemDataDict['device_b_system_name'] = igwSystemObj['DEVICE_B_SYSTEM_NAME']
        igwSystemDataDict['device_b_interface'] = igwSystemObj['DEVICE_B_INTERFACE']
        igwSystemDataDict['device_b_ip'] = igwSystemObj['DEVICE_B_IP']
        igwSystemDataDict['device_b_type'] = igwSystemObj['DEVICE_B_TYPE']
        igwSystemDataDict['device_b_port_desc'] = igwSystemObj['DEVICE_B_PORT_DESC']
        igwSystemDataDict['device_a_mac'] = igwSystemObj['DEVICE_A_MAC']
        igwSystemDataDict['device_b_mac'] = igwSystemObj['DEVICE_B_MAC']
        igwSystemDataDict['device_a_port_desc'] = igwSystemObj['DEVICE_A_PORT_DESC']
        igwSystemDataDict['device_a_vlan'] = igwSystemObj['DEVICE_A_VLAN']
        igwSystemDataDict['creation_date'] = FormatDate(igwSystemObj['CREATION_DATE'])
        igwSystemDataDict['modification_date'] = FormatDate(igwSystemObj['MODIFICATION_DATE'])
        igwMappingObjList.append(igwSystemDataDict)
        
    for igwLldpLegacyObj in igwLldpLegacyObjs:

        igwLldpLegacyDataDict= {}
        igwLldpLegacyDataDict['igw_lldp_legacy_id']=igwLldpLegacyObj['IGW_LLDP_LEGACY_ID']
        igwLldpLegacyDataDict['device_a_name'] = igwLldpLegacyObj['DEVICE_A_NAME']
        igwLldpLegacyDataDict['device_a_interface'] = igwLldpLegacyObj['DEVICE_A_INTERFACE']
        igwLldpLegacyDataDict['device_a_trunk_name'] = igwLldpLegacyObj['DEVICE_A_TRUNK_NAME']
        igwLldpLegacyDataDict['device_a_ip'] = igwLldpLegacyObj['DEVICE_A_IP']
        igwLldpLegacyDataDict['device_b_system_name'] = igwLldpLegacyObj['DEVICE_B_SYSTEM_NAME']
        igwLldpLegacyDataDict['device_b_interface'] = igwLldpLegacyObj['DEVICE_B_INTERFACE']
        igwLldpLegacyDataDict['device_b_ip'] = igwLldpLegacyObj['DEVICE_B_IP']
        igwLldpLegacyDataDict['device_b_type'] = igwLldpLegacyObj['DEVICE_B_TYPE']
        igwLldpLegacyDataDict['device_b_port_desc'] = igwLldpLegacyObj['DEVICE_B_PORT_DESC']
        igwLldpLegacyDataDict['device_a_mac'] = igwLldpLegacyObj['DEVICE_A_MAC']
        igwLldpLegacyDataDict['device_b_mac'] = igwLldpLegacyObj['DEVICE_B_MAC']
        igwLldpLegacyDataDict['device_a_port_desc'] = igwLldpLegacyObj['DEVICE_A_PORT_DESC']
        igwLldpLegacyDataDict['device_a_vlan'] = igwLldpLegacyObj['DEVICE_A_VLAN']
        igwLldpLegacyDataDict['server_name'] = igwLldpLegacyObj['SERVER_NAME']
        igwLldpLegacyDataDict['server_os'] = igwLldpLegacyObj['SERVER_OS']
        igwLldpLegacyDataDict['app_name'] = igwLldpLegacyObj['APP_NAME']
        igwLldpLegacyDataDict['owner_name'] = igwLldpLegacyObj['OWNER_NAME']
        igwLldpLegacyDataDict['owner_email'] = igwLldpLegacyObj['OWNER_EMAIL']
        igwLldpLegacyDataDict['owner_contact'] = igwLldpLegacyObj['OWNER_CONTACT']
        igwLldpLegacyDataDict['creation_date'] = FormatDate(igwLldpLegacyObj['CREATION_DATE'])
        igwLldpLegacyDataDict['modification_date'] = FormatDate(igwLldpLegacyObj['MODIFICATION_DATE'])
        igwLldpLegacyDataDict['device_b_mac_vendor'] = igwLldpLegacyObj["DEVICE_B_MAC_VENDOR"]
        igwLldpLegacyDataDict['service_vendor'] = igwLldpLegacyObj["SERVICE_VENDOR"]
        igwMappingObjList.append(igwLldpLegacyDataDict)

    for igwMacLegacyObj in igwMacLegacyObjs:
        igwMacLegacyDataDict= {}
        igwMacLegacyDataDict= {}
        igwMacLegacyDataDict['igw_mac_legacy_id']=igwMacLegacyObj["IGW_MAC_LEGACY_ID"]
        igwMacLegacyDataDict['device_a_name'] = igwMacLegacyObj["DEVICE_A_NAME"]
        igwMacLegacyDataDict['device_a_interface'] = igwMacLegacyObj["DEVICE_A_INTERFACE"]
        igwMacLegacyDataDict['device_a_trunk_name'] = igwMacLegacyObj["DEVICE_A_TRUNK_NAME"]
        igwMacLegacyDataDict['device_a_ip'] = igwMacLegacyObj["DEVICE_A_IP"]
        igwMacLegacyDataDict['device_b_system_name'] = igwMacLegacyObj["DEVICE_B_SYSTEM_NAME"]
        igwMacLegacyDataDict['device_b_interface'] = igwMacLegacyObj["DEVICE_B_INTERFACE"]
        igwMacLegacyDataDict['device_b_ip'] = igwMacLegacyObj["DEVICE_B_IP"]
        igwMacLegacyDataDict['device_b_type'] = igwMacLegacyObj["DEVICE_B_TYPE"]
        igwMacLegacyDataDict['device_b_port_desc'] = igwMacLegacyObj["DEVICE_B_PORT_DESC"]
        igwMacLegacyDataDict['device_a_mac'] = igwMacLegacyObj["DEVICE_A_MAC"]
        igwMacLegacyDataDict['device_b_mac'] = igwMacLegacyObj["DEVICE_B_MAC"]
        igwMacLegacyDataDict['device_a_port_desc'] = igwMacLegacyObj["DEVICE_A_PORT_DESC"]
        igwMacLegacyDataDict['device_a_vlan'] = igwMacLegacyObj["DEVICE_A_VLAN"]
        igwMacLegacyDataDict['device_a_vlan_name'] = igwMacLegacyObj["DEVICE_A_VLAN_NAME"]
        igwMacLegacyDataDict['server_name'] = igwMacLegacyObj["SERVER_NAME"]
        igwMacLegacyDataDict['server_os'] = igwMacLegacyObj['SERVER_OS']
        igwMacLegacyDataDict['app_name'] = igwMacLegacyObj['APP_NAME']
        igwMacLegacyDataDict['owner_name'] = igwMacLegacyObj["OWNER_NAME"]
        igwMacLegacyDataDict['owner_email'] = igwMacLegacyObj["OWNER_EMAIL"]
        igwMacLegacyDataDict['owner_contact'] = igwMacLegacyObj["OWNER_CONTACT"]
        igwMacLegacyDataDict['creation_date'] = FormatDate(igwMacLegacyObj["CREATION_DATE"])
        igwMacLegacyDataDict['modification_date'] = FormatDate(igwMacLegacyObj["MODIFICATION_DATE"])
        igwMacLegacyDataDict['device_b_mac_vendor'] = igwMacLegacyObj["DEVICE_B_MAC_VENDOR"]
        igwMappingObjList.append(igwMacLegacyDataDict) 

    return igwMappingObjList

@app.route("/getAllEdnSystems", methods = ['GET'])
@token_required
def GetAllEdnSystem(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednSystemObjList=[]
        ednSystemObjs = phy_engine.execute(f"SELECT * FROM edn_system WHERE creation_date = (SELECT max(creation_date) FROM edn_system)")

        for ednSystemObj in ednSystemObjs:

            ednSystemDataDict= {}
            ednSystemDataDict['edn_system_id']=ednSystemObj['EDN_SYSTEM_ID']
            ednSystemDataDict['device_a_name'] = ednSystemObj['DEVICE_A_NAME']
            ednSystemDataDict['device_a_interface'] = ednSystemObj['DEVICE_A_INTERFACE']
            ednSystemDataDict['device_a_trunk_name'] = ednSystemObj['DEVICE_A_TRUNK_NAME']
            ednSystemDataDict['device_a_ip'] = ednSystemObj['DEVICE_A_IP']
            ednSystemDataDict['device_b_system_name'] = ednSystemObj['DEVICE_B_SYSTEM_NAME']
            ednSystemDataDict['device_b_interface'] = ednSystemObj['DEVICE_B_INTERFACE']
            ednSystemDataDict['device_b_ip'] = ednSystemObj['DEVICE_B_IP']
            ednSystemDataDict['device_b_type'] = ednSystemObj['DEVICE_B_TYPE']
            ednSystemDataDict['device_b_port_desc'] = ednSystemObj['DEVICE_B_PORT_DESC']
            ednSystemDataDict['device_a_mac'] = ednSystemObj['DEVICE_A_MAC']
            ednSystemDataDict['device_b_mac'] = ednSystemObj['DEVICE_B_MAC']
            ednSystemDataDict['device_a_port_desc'] = ednSystemObj['DEVICE_A_PORT_DESC']
            ednSystemDataDict['device_a_vlan'] = ednSystemObj['DEVICE_A_VLAN']
            ednSystemDataDict['service_vendor'] = ednSystemObj['SERVICE_VENDOR']
            ednSystemDataDict['creation_date'] = FormatDate(ednSystemObj['CREATION_DATE'])
            ednSystemDataDict['modification_date'] = FormatDate(ednSystemObj['MODIFICATION_DATE'])
            ednSystemObjList.append(ednSystemDataDict)

        content = gzip.compress(json.dumps(ednSystemObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/exportEdnSystem", methods = ['GET'])
@token_required
def ExportEdnSystem(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednSystemObjList=[]
        ednSystemObjs = EDN_SYSTEM.query.all()

        for ednSystemObj in ednSystemObjs:

            ednSystemDataDict= {}
            ednSystemDataDict['edn_system_id']=ednSystemObj.edn_system_id
            ednSystemDataDict['device_a_name'] = ednSystemObj.device_a_name
            ednSystemDataDict['device_a_interface'] = ednSystemObj.device_a_interface
            ednSystemDataDict['device_b_trunk_name'] = ednSystemObj.device_b_trunk_name
            ednSystemDataDict['device_a_ip'] = ednSystemObj.device_a_ip
            ednSystemDataDict['device_a_system_name'] = ednSystemObj.device_a_system_name
            ednSystemDataDict['device_b_interface'] = ednSystemObj.device_b_interface
            ednSystemDataDict['device_b_ip'] = ednSystemObj.device_b_ip
            ednSystemDataDict['device_b_type'] = ednSystemObj.device_b_type
            ednSystemDataDict['device_b_port_desc'] = ednSystemObj.device_b_port_desc
            ednSystemDataDict['device_a_mac'] = ednSystemObj.device_a_mac
            ednSystemDataDict['device_b_mac'] = ednSystemObj.device_b_mac
            ednSystemDataDict['device_a_port_desc'] = ednSystemObj.device_a_port_desc
            ednSystemDataDict['device_a_vlan'] = ednSystemObj.device_a_vlan
            ednSystemDataDict['creation_date'] = ednSystemObj.creation_date
            ednSystemDataDict['modification_date'] = FormatDate(ednSystemObj.modification_date)
            
            ednSystemObjList.append(ednSystemDataDict)

        return jsonify(ednSystemObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/addEdnSecurityDevice",methods = ['POST'])
@token_required
def AddEdnSecurityDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednSecurityObj = request.get_json()

        print(ednSecurityObj,file=sys.stderr)
        ednSecurity = EDN_SECURITY()
        ednSecurity.device_a_ip = ednSecurityObj['device_a_ip']
        
        if ednSecurityObj['device_a_name']:
            ednSecurity.device_a_name = ednSecurityObj['device_a_name']
        if ednSecurityObj['device_a_interface']:
            ednSecurity.device_a_interface = ednSecurityObj['device_a_interface']    
        if ednSecurityObj['device_a_trunk_name']:
            ednSecurity.device_a_trunk_name = ednSecurityObj['device_a_trunk_name']
        if ednSecurityObj['device_a_ip']:
            ednSecurity.device_a_ip = ednSecurityObj['device_a_ip']
        if ednSecurityObj['device_b_system_name']:
            ednSecurity.device_b_system_name= ednSecurityObj['device_b_system_name']
        if ednSecurityObj['device_b_interface']:
            ednSecurity.device_b_interface = ednSecurityObj['device_b_interface']
        if ednSecurityObj['device_b_ip']:
            ednSecurity.device_b_ip= ednSecurityObj['device_b_ip']
        if ednSecurityObj['device_b_type']:
            ednSecurity.device_b_type= ednSecurityObj['device_b_type']
        if ednSecurityObj['device_b_port_desc']:
            portDesc = ednSecurityObj['device_b_port_desc']
            portDesc.replace('<',"")
            portDesc.replace('>',"")
            portDesc.replace('|'," , ")
            ednSecurity.device_b_port_desc= portDesc
            #ednSecurity.device_b_port_desc= ednSecurityObj['device_b_port_desc']
        if ednSecurityObj['device_a_mac']:
            ednSecurity.device_a_mac= ednSecurityObj['device_a_mac']
        if ednSecurityObj['device_b_mac']:
            ednSecurity.device_b_mac= ednSecurityObj['device_b_mac']
        if ednSecurityObj['device_a_port_desc']:
            portDesc = ednSecurityObj['device_a_port_desc']
            portDesc.replace('<',"")
            portDesc.replace('>',"")
            portDesc.replace('|'," , ")
            ednSecurity.device_a_port_desc= portDesc
            #ednSecurity.device_a_port_desc= ednSecurityObj['device_a_port_desc']
        if ednSecurityObj['device_a_vlan']:
            ednSecurity.device_a_vlan= ednSecurityObj['device_a_vlan']
        if 'service_vendor' in ednSecurityObj:
                ednSecurity.service_vendor = ednSecurityObj['service_vendor']
        else:
            ednSecurity.service_vendor = 'N/A'
    

        #print(device.sw_eol_date,file=sys.stderr)
        
        if EDN_SECURITY.query.with_entities(EDN_SECURITY.edn_security_id).filter_by(edn_security_id=ednSecurityObj['edn_security_id']).first() is not None:
            ednSecurity.edn_security_id = EDN_SECURITY.query.with_entities(EDN_SECURITY.edn_security_id).filter_by(edn_security_id=ednSecurityObj['edn_security_id']).first()[0]
            print(f"Updated {ednSecurityObj['edn_security_id']}",file=sys.stderr)
            ednSecurity.modification_date= datetime.now(tz)
            UpdateData(ednSecurity)
            
        else:
            print("Inserted Record",file=sys.stderr)
            ednSecurity.creation_date= datetime.now(tz)
            ednSecurity.modification_date= datetime.now(tz)
            InsertData(ednSecurity)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnSecurityDates",methods=['GET'])
@token_required
def GetAllEdnSecurityDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct CREATION_DATE from edn_security ORDER by CREATION_DATE desc;"
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllEdnSecurityByDate", methods = ['POST'])
@token_required
def GetAllEdnSecurityByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednSecurityObjList=[]
        #ednSecurityObjs = EDN_SECURITY.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        ednSecurityObjs = phy_engine.execute(f"SELECT * FROM edn_security WHERE creation_date = '{current_time}'")

        for ednSecurityObj in ednSecurityObjs:

            ednSecurityDataDict= {}
            ednSecurityDataDict['edn_security_id']=ednSecurityObj['EDN_SECURITY_ID']
            ednSecurityDataDict['device_a_name'] = ednSecurityObj['DEVICE_A_NAME']
            ednSecurityDataDict['device_a_interface'] = ednSecurityObj['DEVICE_A_INTERFACE']
            ednSecurityDataDict['device_a_trunk_name'] = ednSecurityObj['DEVICE_A_TRUNK_NAME']
            ednSecurityDataDict['device_a_ip'] = ednSecurityObj['DEVICE_A_IP']
            ednSecurityDataDict['device_b_system_name'] = ednSecurityObj['DEVICE_B_SYSTEM_NAME']
            ednSecurityDataDict['device_b_interface'] = ednSecurityObj['DEVICE_B_INTERFACE']
            ednSecurityDataDict['device_b_ip'] = ednSecurityObj['DEVICE_B_IP']
            ednSecurityDataDict['device_b_type'] = ednSecurityObj['DEVICE_B_TYPE']
            ednSecurityDataDict['device_b_port_desc'] = ednSecurityObj['DEVICE_B_PORT_DESC']
            ednSecurityDataDict['device_a_mac'] = ednSecurityObj['DEVICE_A_MAC']
            ednSecurityDataDict['device_b_mac'] = ednSecurityObj['DEVICE_B_MAC']
            ednSecurityDataDict['device_a_port_desc'] = ednSecurityObj['DEVICE_A_PORT_DESC']
            ednSecurityDataDict['device_a_vlan'] = ednSecurityObj['DEVICE_A_VLAN']
            ednSecurityDataDict['service_vendor'] = ednSecurityObj['SERVICE_VENDOR']
            ednSecurityDataDict['creation_date'] = FormatDate(ednSecurityObj['CREATION_DATE'])
            ednSecurityDataDict['modification_date'] = FormatDate(ednSecurityObj['MODIFICATION_DATE'])
            ednSecurityObjList.append(ednSecurityDataDict)
       
        content = gzip.compress(json.dumps(ednSecurityObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteEdnSecurityDevice",methods = ['POST'])
@token_required
def DeleteEdnSecurityDevice(user_data):
    if True:#session.get('token', None):
        ednSecurityObj = request.get_json()
        #ednSecurityObj = [1,2,3,4,5,6,7,8]
        print(ednSecurityObj,file = sys.stderr)
        for id in ednSecurityObj.get("ips"):
            ednSecurityId = EDN_SECURITY.query.filter(EDN_SECURITY.edn_security_id==id).first()
            if id:
                db.session.delete(ednSecurityId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addEdnSecurityDevices", methods = ['POST'])
@token_required
def AddEdnSecurityDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()

        print(postData,file=sys.stderr)
        time= datetime.now(tz)

        for ednSecurityObj in postData:

            ednSecurity = EDN_SECURITY()
            if 'device_a_name' in ednSecurityObj:
                ednSecurity.device_a_name = ednSecurityObj['device_a_name']
            else:
                ednSecurity.device_a_name = 'N/A'
            if 'device_a_interface' in ednSecurityObj:
                ednSecurity.device_a_interface = ednSecurityObj['device_a_interface']
            else:
                ednSecurity.device_a_interface = 'N/A'
            if 'device_a_trunk_name' in ednSecurityObj:
                ednSecurity.device_a_trunk_name = ednSecurityObj['device_a_trunk_name']
            else:
                ednSecurity.device_a_trunk_name = 'N/A'
            if 'device_a_ip' in ednSecurityObj:
                ednSecurity.device_a_ip = ednSecurityObj['device_a_ip']
            else:
                ednSecurity.device_a_ip = 'N/A'
            if 'device_b_system_name' in ednSecurityObj:
                ednSecurity.device_b_system_name = ednSecurityObj['device_b_system_name']
            else:
                ednSecurity.device_b_system_name = 'N/A'
            if 'device_b_interface' in ednSecurityObj:
                ednSecurity.device_b_interface = ednSecurityObj['device_b_interface']
            else:
                ednSecurity.device_b_interface = 'N/A'
            if 'device_b_ip' in ednSecurityObj:
                ednSecurity.device_b_ip = ednSecurityObj['device_b_ip']
            else:
                ednSecurity.device_b_ip = 'N/A'
            if 'device_b_type' in ednSecurityObj:
                ednSecurity.device_b_type = ednSecurityObj['device_b_type']
            else:
                ednSecurity.device_b_type = 'N/A'
            if 'device_b_port_desc' in ednSecurityObj:
                portDesc = ednSecurityObj['device_b_port_desc']
                portDesc.replace('<',"")
                portDesc.replace('>',"")
                portDesc.replace('|'," , ")
                ednSecurity.device_b_port_desc= portDesc
                #ednSecurity.device_b_port_desc = ednSecurityObj['device_b_port_desc']
            else:
                ednSecurity.device_b_port_desc = 'N/A'
            if 'device_a_mac' in ednSecurityObj:
                ednSecurity.device_a_mac = ednSecurityObj['device_a_mac']
            else:
                ednSecurity.device_a_mac = 'N/A'
            if 'device_b_mac' in ednSecurityObj:
                ednSecurity.device_b_mac = ednSecurityObj['device_b_mac']
            else:
                ednSecurity.device_b_mac = 'N/A'
            if 'device_a_port_desc' in ednSecurityObj:
                portDesc = ednSecurityObj['device_a_port_desc']
                portDesc.replace('<',"")
                portDesc.replace('>',"")
                portDesc.replace('|'," , ")
                ednSecurity.device_a_port_desc= portDesc
                #ednSecurity.device_a_port_desc = ednSecurityObj['device_a_port_desc']
            else:
                ednSecurity.device_a_port_desc = 'N/A'
            if 'device_a_vlan' in ednSecurityObj:
                ednSecurity.device_a_vlan = ednSecurityObj['device_a_vlan']
            else:
                ednSecurity.device_a_vlan = 'N/A'
            if 'service_vendor' in ednSecurityObj:
                ednSecurity.service_vendor = ednSecurityObj['service_vendor']
            else:
                ednSecurity.service_vendor = 'N/A'
            
            ednSecurity.creation_date= time
            ednSecurity.modification_date= time
       
            # if Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first() is not None:
            #     seed.seed_id = Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first()[0]
            #     print("Updated " + seedObj['ne_ip_address'],file=sys.stderr)
            #     UpdateData(seed)
            # else:
            #     print("Inserted " +seedObj['ne_ip_address'],file=sys.stderr)
            #     seed.onboard_status = 'false'
            InsertData(ednSecurity)
       
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/getAllEdnSecurities", methods = ['GET'])
@token_required
def GetAllEdnSecurity(user_data):
    
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednSecurityObjList=[]
        ednSecurityObjs = phy_engine.execute(f"SELECT * FROM edn_security WHERE creation_date = (SELECT max(creation_date) FROM edn_security)")

        for ednSecurityObj in ednSecurityObjs:

            ednSecurityDataDict= {}
            ednSecurityDataDict['edn_security_id']=ednSecurityObj['EDN_SECURITY_ID']
            ednSecurityDataDict['device_a_name'] = ednSecurityObj['DEVICE_A_NAME']
            ednSecurityDataDict['device_a_interface'] = ednSecurityObj['DEVICE_A_INTERFACE']
            ednSecurityDataDict['device_a_trunk_name'] = ednSecurityObj['DEVICE_A_TRUNK_NAME']
            ednSecurityDataDict['device_a_ip'] = ednSecurityObj['DEVICE_A_IP']
            ednSecurityDataDict['device_b_system_name'] = ednSecurityObj['DEVICE_B_SYSTEM_NAME']
            ednSecurityDataDict['device_b_interface'] = ednSecurityObj['DEVICE_B_INTERFACE']
            ednSecurityDataDict['device_b_ip'] = ednSecurityObj['DEVICE_B_IP']
            ednSecurityDataDict['device_b_type'] = ednSecurityObj['DEVICE_B_TYPE']
            ednSecurityDataDict['device_b_port_desc'] = ednSecurityObj['DEVICE_B_PORT_DESC']
            ednSecurityDataDict['device_a_mac'] = ednSecurityObj['DEVICE_A_MAC']
            ednSecurityDataDict['device_b_mac'] = ednSecurityObj['DEVICE_B_MAC']
            ednSecurityDataDict['device_a_port_desc'] = ednSecurityObj['DEVICE_A_PORT_DESC']
            ednSecurityDataDict['device_a_vlan'] = ednSecurityObj['DEVICE_A_VLAN']
            ednSecurityDataDict['service_vendor'] = ednSecurityObj['SERVICE_VENDOR']
            ednSecurityDataDict['creation_date'] = FormatDate(ednSecurityObj['CREATION_DATE'])
            ednSecurityDataDict['modification_date'] = FormatDate(ednSecurityObj['MODIFICATION_DATE'])
            ednSecurityObjList.append(ednSecurityDataDict)
        content = gzip.compress(json.dumps(ednSecurityObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/exportEdnSecurity", methods = ['GET'])
@token_required
def ExportEdnSecurity(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednSecurityObjList=[]
        ednSecurityObjs = EDN_SECURITY.query.all()

        for ednSecurityObj in ednSecurityObjs:

            ednSecurityDataDict= {}
            ednSecurityDataDict['edn_security_id']=ednSecurityObj.edn_security_id
            ednSecurityDataDict['device_a_name'] = ednSecurityObj.device_a_name
            ednSecurityDataDict['device_a_interface'] = ednSecurityObj.device_a_interface
            ednSecurityDataDict['device_a_trunk_name'] = ednSecurityObj.device_a_trunk_name
            ednSecurityDataDict['device_a_ip'] = ednSecurityObj.device_a_ip
            ednSecurityDataDict['device_b_system_name'] = ednSecurityObj.device_b_system_name
            ednSecurityDataDict['device_b_interface'] = ednSecurityObj.device_b_interface
            ednSecurityDataDict['device_b_ip'] = ednSecurityObj.device_b_ip
            ednSecurityDataDict['device_b_type'] = ednSecurityObj.device_b_type
            ednSecurityDataDict['device_b_port_desc'] = ednSecurityObj.device_b_port_desc
            ednSecurityDataDict['device_a_mac'] = ednSecurityObj.device_a_mac
            ednSecurityDataDict['device_b_mac'] = ednSecurityObj.device_b_mac
            ednSecurityDataDict['device_a_port_desc'] = ednSecurityObj.device_a_port_desc
            ednSecurityDataDict['device_a_vlan'] = ednSecurityObj.device_a_vlan
            ednSecurityDataDict['creation_date'] = FormatDate(ednSecurityObj.creation_date)
            ednSecurityDataDict['modification_date'] = FormatDate(ednSecurityObj.modification_date)
            
            ednSecurityObjList.append(ednSecurityDataDict)

        return jsonify(ednSecurityObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnCdpLegacy", methods = ['GET'])
@token_required
def GetAllEdnCdpLegacy(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednCdpLegacyObjList=[]
        #ednCdpLegacyObjs = EDN_CDP_LEGACY.query.all()
        ednCdpLegacyObjs = phy_engine.execute('SELECT * FROM edn_cdp_legacy WHERE creation_date = (SELECT max(creation_date) FROM edn_cdp_legacy)')

        for ednCdpLegacyObj in ednCdpLegacyObjs:

            ednCdpLegacyDataDict= {}
            ednCdpLegacyDataDict['edn_cdp_legacy_id']=ednCdpLegacyObj['EDN_CDP_LEGACY_ID']
            ednCdpLegacyDataDict['device_a_name'] = ednCdpLegacyObj['DEVICE_A_NAME']
            ednCdpLegacyDataDict['device_a_interface'] = ednCdpLegacyObj['DEVICE_A_INTERFACE']
            ednCdpLegacyDataDict['device_a_trunk_name'] = ednCdpLegacyObj['DEVICE_A_TRUNK_NAME']
            ednCdpLegacyDataDict['device_a_ip'] = ednCdpLegacyObj['DEVICE_A_IP']
            ednCdpLegacyDataDict['device_b_system_name'] = ednCdpLegacyObj['DEVICE_B_SYSTEM_NAME']
            ednCdpLegacyDataDict['device_b_interface'] = ednCdpLegacyObj['DEVICE_B_INTERFACE']
            ednCdpLegacyDataDict['device_b_ip'] = ednCdpLegacyObj['DEVICE_B_IP']
            ednCdpLegacyDataDict['device_b_type'] = ednCdpLegacyObj['DEVICE_B_TYPE']
            ednCdpLegacyDataDict['device_b_port_desc'] = ednCdpLegacyObj['DEVICE_B_PORT_DESC']
            ednCdpLegacyDataDict['device_a_mac'] = ednCdpLegacyObj['DEVICE_A_MAC']
            ednCdpLegacyDataDict['device_b_mac'] = ednCdpLegacyObj['DEVICE_B_MAC']
            ednCdpLegacyDataDict['device_a_port_desc'] = ednCdpLegacyObj['DEVICE_A_PORT_DESC']
            ednCdpLegacyDataDict['device_a_vlan'] = ednCdpLegacyObj['DEVICE_A_VLAN']
            ednCdpLegacyDataDict['server_name'] = ednCdpLegacyObj['SERVER_NAME']
            ednCdpLegacyDataDict['server_os'] = ednCdpLegacyObj['SERVER_OS']
            ednCdpLegacyDataDict['app_name'] = ednCdpLegacyObj['APP_NAME']
            ednCdpLegacyDataDict['owner_name'] = ednCdpLegacyObj['OWNER_NAME']
            ednCdpLegacyDataDict['owner_email'] = ednCdpLegacyObj['OWNER_EMAIL']
            ednCdpLegacyDataDict['owner_contact'] = ednCdpLegacyObj['OWNER_CONTACT']
            ednCdpLegacyDataDict['creation_date'] = FormatDate(ednCdpLegacyObj['CREATION_DATE'])
            ednCdpLegacyDataDict['modification_date'] = FormatDate(ednCdpLegacyObj['MODIFICATION_DATE'])
            ednCdpLegacyDataDict['device_b_mac_vendor'] = ednCdpLegacyObj["DEVICE_B_MAC_VENDOR"]
            ednCdpLegacyDataDict['service_vendor'] = ednCdpLegacyObj['SERVICE_VENDOR']

            ednCdpLegacyObjList.append(ednCdpLegacyDataDict)
       
        content = gzip.compress(json.dumps(ednCdpLegacyObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllEdnCdpLegacyDates',methods=['GET'])
@token_required
def GetAllEdnCdpLegacyDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from edn_cdp_legacy  ORDER BY creation_date DESC;"
        
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllEdnCdpLegacyByDate", methods = ['POST'])
@token_required
def GetAllEdnCdpLegacyByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednCdpLegacyObjList=[]
        #ednCdpLegacyObjs = EDN_CDP_LEGACY.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        ednCdpLegacyObjs = phy_engine.execute(f"SELECT * FROM edn_cdp_legacy WHERE creation_date = '{current_time}'")

        for ednCdpLegacyObj in ednCdpLegacyObjs:

            ednCdpLegacyDataDict= {}
            ednCdpLegacyDataDict['edn_cdp_legacy_id']=ednCdpLegacyObj['EDN_CDP_LEGACY_ID']
            ednCdpLegacyDataDict['device_a_name'] = ednCdpLegacyObj['DEVICE_A_NAME']
            ednCdpLegacyDataDict['device_a_interface'] = ednCdpLegacyObj['DEVICE_A_INTERFACE']
            ednCdpLegacyDataDict['device_a_trunk_name'] = ednCdpLegacyObj['DEVICE_A_TRUNK_NAME']
            ednCdpLegacyDataDict['device_a_ip'] = ednCdpLegacyObj['DEVICE_A_IP']
            ednCdpLegacyDataDict['device_b_system_name'] = ednCdpLegacyObj['DEVICE_B_SYSTEM_NAME']
            ednCdpLegacyDataDict['device_b_interface'] = ednCdpLegacyObj['DEVICE_B_INTERFACE']
            ednCdpLegacyDataDict['device_b_ip'] = ednCdpLegacyObj['DEVICE_B_IP']
            ednCdpLegacyDataDict['device_b_type'] = ednCdpLegacyObj['DEVICE_B_TYPE']
            ednCdpLegacyDataDict['device_b_port_desc'] = ednCdpLegacyObj['DEVICE_B_PORT_DESC']
            ednCdpLegacyDataDict['device_a_mac'] = ednCdpLegacyObj['DEVICE_A_MAC']
            ednCdpLegacyDataDict['device_b_mac'] = ednCdpLegacyObj['DEVICE_B_MAC']
            ednCdpLegacyDataDict['device_a_port_desc'] = ednCdpLegacyObj['DEVICE_A_PORT_DESC']
            ednCdpLegacyDataDict['device_a_vlan'] = ednCdpLegacyObj['DEVICE_A_VLAN']
            ednCdpLegacyDataDict['server_name'] = ednCdpLegacyObj['SERVER_NAME']
            ednCdpLegacyDataDict['server_os'] = ednCdpLegacyObj['SERVER_OS']
            ednCdpLegacyDataDict['app_name'] = ednCdpLegacyObj['APP_NAME']
            ednCdpLegacyDataDict['owner_name'] = ednCdpLegacyObj['OWNER_NAME']
            ednCdpLegacyDataDict['owner_email'] = ednCdpLegacyObj['OWNER_EMAIL']
            ednCdpLegacyDataDict['owner_contact'] = ednCdpLegacyObj['OWNER_CONTACT']
            ednCdpLegacyDataDict['creation_date'] = FormatDate(ednCdpLegacyObj['CREATION_DATE'])
            ednCdpLegacyDataDict['modification_date'] = FormatDate(ednCdpLegacyObj['MODIFICATION_DATE'])
            ednCdpLegacyDataDict['device_b_mac_vendor'] = ednCdpLegacyObj["DEVICE_B_MAC_VENDOR"]
            ednCdpLegacyDataDict['service_vendor'] = ednCdpLegacyObj["SERVICE_VENDOR"]
            ednCdpLegacyObjList.append(ednCdpLegacyDataDict)
       
        content = gzip.compress(json.dumps(ednCdpLegacyObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/exportEdnCdpLegacy", methods = ['GET'])
@token_required
def ExportEdnCdpLegacy(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednCdpLegacyObjList=[]
        #ednCdpLegacyObjs = EDN_CDP_LEGACY.query.all()
        ednCdpLegacyObjs = phy_engine.execute('SELECT * FROM edn_cdp_legacy WHERE creation_date = (SELECT max(creation_date) FROM edn_cdp_legacy)')

        for ednCdpLegacyObj in ednCdpLegacyObjs:

            ednCdpLegacyDataDict= {}
            ednCdpLegacyDataDict['edn_cdp_legacy_id']=ednCdpLegacyObj['EDN_CDP_LEGACY_ID']
            ednCdpLegacyDataDict['device_a_name'] = ednCdpLegacyObj['DEVICE_A_NAME']
            ednCdpLegacyDataDict['device_a_interface'] = ednCdpLegacyObj['DEVICE_A_INTERFACE']
            ednCdpLegacyDataDict['device_a_trunk_name'] = ednCdpLegacyObj['DEVICE_A_TRUNK_NAME']
            ednCdpLegacyDataDict['device_a_ip'] = ednCdpLegacyObj['DEVICE_A_IP']
            ednCdpLegacyDataDict['device_b_system_name'] = ednCdpLegacyObj['DEVICE_B_SYSTEM_NAME']
            ednCdpLegacyDataDict['device_b_interface'] = ednCdpLegacyObj['DEVICE_B_INTERFACE']
            ednCdpLegacyDataDict['device_b_ip'] = ednCdpLegacyObj['DEVICE_B_IP']
            ednCdpLegacyDataDict['device_b_type'] = ednCdpLegacyObj['DEVICE_B_TYPE']
            ednCdpLegacyDataDict['device_b_port_desc'] = ednCdpLegacyObj['DEVICE_B_PORT_DESC']
            ednCdpLegacyDataDict['device_a_mac'] = ednCdpLegacyObj['DEVICE_A_MAC']
            ednCdpLegacyDataDict['device_b_mac'] = ednCdpLegacyObj['DEVICE_B_MAC']
            ednCdpLegacyDataDict['device_a_port_desc'] = ednCdpLegacyObj['DEVICE_A_PORT_DESC']
            ednCdpLegacyDataDict['device_a_vlan'] = ednCdpLegacyObj['DEVICE_A_VLAN']
            ednCdpLegacyDataDict['server_name'] = ednCdpLegacyObj['SERVER_NAME']
            ednCdpLegacyDataDict['server_os'] = ednCdpLegacyObj['SERVER_OS']
            ednCdpLegacyDataDict['app_name'] = ednCdpLegacyObj['APP_NAME']
            ednCdpLegacyDataDict['owner_name'] = ednCdpLegacyObj['OWNER_NAME']
            ednCdpLegacyDataDict['owner_email'] = ednCdpLegacyObj['OWNER_EMAIL']
            ednCdpLegacyDataDict['owner_contact'] = ednCdpLegacyObj['OWNER_CONTACT']
            ednCdpLegacyDataDict['creation_date'] = FormatDate(ednCdpLegacyObj['CREATION_DATE'])
            ednCdpLegacyDataDict['modification_date'] = FormatDate(ednCdpLegacyObj['MODIFICATION_DATE'])

            
            ednCdpLegacyObjList.append(ednCdpLegacyDataDict)

        return jsonify(ednCdpLegacyObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editEdnMacLegacy",methods = ['POST'])
@token_required
def EditMacLegacy(user_data):
    #if request.headers.get('X-Auth-Key') ==authsession.get('token', None):
    if True:#session.get('token', None):
        ednMacLegacyObj = request.get_json()
        print(ednMacLegacyObj,file = sys.stderr)
        ednMacLegacy = EDN_MAC_LEGACY.query.with_entities(EDN_MAC_LEGACY).filter_by(edn_mac_legacy_id=ednMacLegacyObj["edn_mac_legacy_id"]).first()
        #if ednMacLegacyObj['device_a_name']:
        #    ednMacLegacy.device_a_name = ednMacLegacyObj['device_a_name']          
        #if ednMacLegacyObj['device_a_interface']:
        #    ednMacLegacy.device_a_interface = ednMacLegacyObj['device_a_interface']
        #if ednMacLegacyObj['device_a_trunk_name']:
        #    ednMacLegacy.device_a_trunk_name = ednMacLegacyObj['device_a_trunk_name']
        #if ednMacLegacyObj['device_a_ip']:
        #    ednMacLegacy.device_a_ip = ednMacLegacyObj['device_a_ip']
        if ednMacLegacyObj['device_b_system_name']:
            ednMacLegacy.device_b_system_name = ednMacLegacyObj['device_b_system_name']
        if ednMacLegacyObj['device_b_interface']:
            ednMacLegacy.device_b_interface = ednMacLegacyObj['device_b_interface']
        #if ednMacLegacyObj['device_b_ip']:
        #    ednMacLegacy.device_b_ip = ednMacLegacyObj['device_b_ip']
        if ednMacLegacyObj['device_b_type']:
            ednMacLegacy.device_b_type = ednMacLegacyObj['device_b_type']
        if ednMacLegacyObj['device_b_port_desc']:
            ednMacLegacy.device_b_port_desc = ednMacLegacyObj['device_b_port_desc']
        #if ednMacLegacyObj['device_a_mac']:
        #    ednMacLegacy.device_a_mac = ednMacLegacyObj['device_a_mac']
        #if ednMacLegacyObj['device_b_mac']:
        #    ednMacLegacy.device_b_mac = ednMacLegacyObj['device_b_mac']
        #if ednMacLegacyObj['device_a_port_desc']:
        #    ednMacLegacy.device_a_port_desc = ednMacLegacyObj['device_a_port_desc']
        #if ednMacLegacyObj['device_a_vlan']:
        #    ednMacLegacy.device_a_vlan = ednMacLegacyObj['device_a_vlan']
        if ednMacLegacyObj['server_name']:
            ednMacLegacy.server_name = ednMacLegacyObj['server_name']
        if ednMacLegacyObj['server_os']:
            ednMacLegacy.server_os = ednMacLegacyObj['server_os']
        if ednMacLegacyObj['app_name']:
            ednMacLegacy.app_name = ednMacLegacyObj['app_name']
        if ednMacLegacyObj['owner_name']:
            ednMacLegacy.owner_name = ednMacLegacyObj['owner_name']
        if ednMacLegacyObj['owner_email']:
            ednMacLegacy.owner_email = ednMacLegacyObj['owner_email']
        if ednMacLegacyObj['owner_contact']:
            ednMacLegacy.owner_contact = ednMacLegacyObj['owner_contact']
        UpdateData(ednMacLegacy)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnMacLegacy", methods = ['GET'])
@token_required
def GetAllEdnMacLegacy(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednMacLegacyObjList=[]
        #ednMacLegacyObjs = EDN_MAC_LEGACY.query.all()
        ednMacLegacyObjs = phy_engine.execute('SELECT * FROM edn_mac_legacy WHERE creation_date = (SELECT max(creation_date) FROM edn_mac_legacy)')
        
        for ednMacLegacyObj in ednMacLegacyObjs:

            ednMacLegacyDataDict= {}
            ednMacLegacyDataDict['edn_mac_legacy_id']=ednMacLegacyObj["EDN_MAC_LEGACY_ID"]
            ednMacLegacyDataDict['device_a_name'] = ednMacLegacyObj["DEVICE_A_NAME"]
            ednMacLegacyDataDict['device_a_interface'] = ednMacLegacyObj["DEVICE_A_INTERFACE"]
            ednMacLegacyDataDict['device_a_trunk_name'] = ednMacLegacyObj["DEVICE_A_TRUNK_NAME"]
            ednMacLegacyDataDict['device_a_ip'] = ednMacLegacyObj["DEVICE_A_IP"]
            ednMacLegacyDataDict['device_b_system_name'] = ednMacLegacyObj["DEVICE_B_SYSTEM_NAME"]
            ednMacLegacyDataDict['device_b_interface'] = ednMacLegacyObj["DEVICE_B_INTERFACE"]
            ednMacLegacyDataDict['device_b_ip'] = ednMacLegacyObj["DEVICE_B_IP"]
            ednMacLegacyDataDict['device_b_type'] = ednMacLegacyObj["DEVICE_B_TYPE"]
            ednMacLegacyDataDict['device_b_port_desc'] = ednMacLegacyObj["DEVICE_B_PORT_DESC"]
            ednMacLegacyDataDict['device_a_mac'] = ednMacLegacyObj["DEVICE_A_MAC"]
            ednMacLegacyDataDict['device_b_mac'] = ednMacLegacyObj["DEVICE_B_MAC"]
            ednMacLegacyDataDict['device_a_port_desc'] = ednMacLegacyObj["DEVICE_A_PORT_DESC"]
            ednMacLegacyDataDict['device_a_vlan'] = ednMacLegacyObj["DEVICE_A_VLAN"]
            ednMacLegacyDataDict['device_a_vlan_name'] = ednMacLegacyObj["DEVICE_A_VLAN_NAME"]
            ednMacLegacyDataDict['arp_source_name'] = ednMacLegacyObj["ARP_SOURCE_NAME"]
            ednMacLegacyDataDict['arp_source_type'] = ednMacLegacyObj["ARP_SOURCE_TYPE"]
            ednMacLegacyDataDict['service_vendor'] = ednMacLegacyObj["SERVICE_VENDOR"]
            ednMacLegacyDataDict['device_b_mac_vendor'] = ednMacLegacyObj["DEVICE_B_MAC_VENDOR"]
            ednMacLegacyDataDict['server_name'] = ednMacLegacyObj["SERVER_NAME"]
            ednMacLegacyDataDict['server_os'] = ednMacLegacyObj["SERVER_OS"]
            ednMacLegacyDataDict['app_name'] = ednMacLegacyObj["APP_NAME"]
            ednMacLegacyDataDict['owner_name'] = ednMacLegacyObj["OWNER_NAME"]
            ednMacLegacyDataDict['owner_email'] = ednMacLegacyObj["OWNER_EMAIL"]
            ednMacLegacyDataDict['owner_contact'] = ednMacLegacyObj["OWNER_CONTACT"]
            ednMacLegacyDataDict['service_matched_by'] = ednMacLegacyObj["SERVICE_MATCHED_BY"]
            ednMacLegacyDataDict['modified_by'] = ednMacLegacyObj["MODIFIED_BY"]
            ednMacLegacyDataDict['device_a_rx'] = ednMacLegacyObj["DEVICE_A_RX"]
            ednMacLegacyDataDict['device_a_tx'] = ednMacLegacyObj["DEVICE_A_TX"]
            ednMacLegacyDataDict['f5_lb'] = ednMacLegacyObj["F5_LB"]
            ednMacLegacyDataDict['f5_vip'] = ednMacLegacyObj["F5_VIP"]
            ednMacLegacyDataDict['f5_node_status'] = ednMacLegacyObj["F5_NODE_STATUS"]
            ednMacLegacyDataDict['creation_date'] = FormatDate(ednMacLegacyObj["CREATION_DATE"])
            ednMacLegacyDataDict['modification_date'] = FormatDate(ednMacLegacyObj["MODIFICATION_DATE"])
            ednMacLegacyObjList.append(ednMacLegacyDataDict)

        content = gzip.compress(json.dumps(ednMacLegacyObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/getEdnMacLegacy", methods = ['GET'])
@token_required
def GetEdnMacLegacy(user_data):
    try:
        queryString=""
        filter = request.args.get('filter')
        
        if filter=='learned_mac_address':
            queryString = f"SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY device_b_mac ORDER BY creation_date DESC) AS rn FROM edn_mac_legacy WHERE creation_date = (SELECT MAX(creation_date) FROM edn_mac_legacy)) AS t WHERE rn = 1;"
        elif filter== 'learned_ip_address':
            queryString = f"SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY device_b_ip ORDER BY creation_date DESC) AS rn FROM edn_mac_legacy WHERE creation_date = (SELECT MAX(creation_date) FROM edn_mac_legacy)) AS t WHERE rn = 1;"
        elif filter== 'mapped_it_services':
            queryString = f"SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY device_b_mac ORDER BY creation_date DESC) AS rn FROM edn_mac_legacy WHERE creation_date = (SELECT MAX(creation_date) FROM edn_mac_legacy) AND modified_by = 'IT SYNC') AS t WHERE rn = 1;"
        elif filter== 'mapped_tech_op_services':
            queryString = f"SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY device_b_mac ORDER BY creation_date DESC) AS rn FROM edn_mac_legacy WHERE creation_date = (SELECT MAX(creation_date) FROM edn_mac_legacy) AND (service_vendor <> 'IT' AND service_vendor IS NOT NULL)) AS t WHERE rn = 1;"
        elif filter== 'matched_nodes_behind_f5':
            queryString = f"SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY device_b_mac ORDER BY creation_date DESC) AS rn FROM edn_mac_legacy WHERE creation_date = (SELECT MAX(creation_date) FROM edn_mac_legacy) AND f5_lb IS NOT NULL) AS t WHERE rn = 1;"
        else:
            if queryString=="":
                print("REQUEST NOT FOUND", file=sys.stderr)
                traceback.print_exc()
                return "REQUEST NOT FOUND",500
                
        result = phy_engine.execute(queryString)
        ednMacLegacyObjList = []
        for ednMacLegacyObj in result:
            ednMacLegacyDataDict = {}
            ednMacLegacyDataDict['edn_mac_legacy_id']=ednMacLegacyObj["EDN_MAC_LEGACY_ID"]
            ednMacLegacyDataDict['device_a_name'] = ednMacLegacyObj["DEVICE_A_NAME"]
            ednMacLegacyDataDict['device_a_interface'] = ednMacLegacyObj["DEVICE_A_INTERFACE"]
            ednMacLegacyDataDict['device_a_trunk_name'] = ednMacLegacyObj["DEVICE_A_TRUNK_NAME"]
            ednMacLegacyDataDict['device_a_ip'] = ednMacLegacyObj["DEVICE_A_IP"]
            ednMacLegacyDataDict['device_b_system_name'] = ednMacLegacyObj["DEVICE_B_SYSTEM_NAME"]
            ednMacLegacyDataDict['device_b_interface'] = ednMacLegacyObj["DEVICE_B_INTERFACE"]
            ednMacLegacyDataDict['device_b_ip'] = ednMacLegacyObj["DEVICE_B_IP"]
            ednMacLegacyDataDict['device_b_type'] = ednMacLegacyObj["DEVICE_B_TYPE"]
            ednMacLegacyDataDict['device_b_port_desc'] = ednMacLegacyObj["DEVICE_B_PORT_DESC"]
            ednMacLegacyDataDict['device_a_mac'] = ednMacLegacyObj["DEVICE_A_MAC"]
            ednMacLegacyDataDict['device_b_mac'] = ednMacLegacyObj["DEVICE_B_MAC"]
            ednMacLegacyDataDict['device_a_port_desc'] = ednMacLegacyObj["DEVICE_A_PORT_DESC"]
            ednMacLegacyDataDict['device_a_vlan'] = ednMacLegacyObj["DEVICE_A_VLAN"]
            ednMacLegacyDataDict['device_a_vlan_name'] = ednMacLegacyObj["DEVICE_A_VLAN_NAME"]
            ednMacLegacyDataDict['arp_source_name'] = ednMacLegacyObj["ARP_SOURCE_NAME"]
            ednMacLegacyDataDict['arp_source_type'] = ednMacLegacyObj["ARP_SOURCE_TYPE"]
            ednMacLegacyDataDict['service_vendor'] = ednMacLegacyObj["SERVICE_VENDOR"]
            ednMacLegacyDataDict['device_b_mac_vendor'] = ednMacLegacyObj["DEVICE_B_MAC_VENDOR"]
            ednMacLegacyDataDict['server_name'] = ednMacLegacyObj["SERVER_NAME"]
            ednMacLegacyDataDict['server_os'] = ednMacLegacyObj["SERVER_OS"]
            ednMacLegacyDataDict['app_name'] = ednMacLegacyObj["APP_NAME"]
            ednMacLegacyDataDict['owner_name'] = ednMacLegacyObj["OWNER_NAME"]
            ednMacLegacyDataDict['owner_email'] = ednMacLegacyObj["OWNER_EMAIL"]
            ednMacLegacyDataDict['owner_contact'] = ednMacLegacyObj["OWNER_CONTACT"]
            ednMacLegacyDataDict['service_matched_by'] = ednMacLegacyObj["SERVICE_MATCHED_BY"]
            ednMacLegacyDataDict['modified_by'] = ednMacLegacyObj["MODIFIED_BY"]
            ednMacLegacyDataDict['device_a_rx'] = ednMacLegacyObj["DEVICE_A_RX"]
            ednMacLegacyDataDict['device_a_tx'] = ednMacLegacyObj["DEVICE_A_TX"]
            ednMacLegacyDataDict['f5_lb'] = ednMacLegacyObj["F5_LB"]
            ednMacLegacyDataDict['f5_vip'] = ednMacLegacyObj["F5_VIP"]
            ednMacLegacyDataDict['f5_node_status'] = ednMacLegacyObj["F5_NODE_STATUS"]
            ednMacLegacyDataDict['creation_date'] = FormatDate(ednMacLegacyObj["CREATION_DATE"])
            ednMacLegacyDataDict['modification_date'] = FormatDate(ednMacLegacyObj["MODIFICATION_DATE"])
            ednMacLegacyObjList.append(ednMacLegacyDataDict)

        return jsonify(ednMacLegacyObjList),200
                           
    except Exception as e:
        print(str(e),file=sys.stderr)
        traceback.print_exc()
        return str(e),500

@app.route('/getAllEdnMacLegacyDates',methods=['GET'])
@token_required
def GetAllEdnMacLegacyDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from edn_mac_legacy ORDER BY creation_date DESC;"
        
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getAllEdnMacLegacyByDate", methods = ['POST'])
@token_required
def GetAllEdnMacLegacyByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednMacLegacyObjList=[]
        #ednMacLegacyObjs = EDN_MAC_LEGACY.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)

        ednMacLegacyObjs = phy_engine.execute(f"SELECT * FROM edn_mac_legacy WHERE creation_date = '{current_time}'")
        
        for ednMacLegacyObj in ednMacLegacyObjs:

            ednMacLegacyDataDict= {}
            ednMacLegacyDataDict['edn_mac_legacy_id']=ednMacLegacyObj["EDN_MAC_LEGACY_ID"]
            ednMacLegacyDataDict['device_a_name'] = ednMacLegacyObj["DEVICE_A_NAME"]
            ednMacLegacyDataDict['device_a_interface'] = ednMacLegacyObj["DEVICE_A_INTERFACE"]
            ednMacLegacyDataDict['device_a_trunk_name'] = ednMacLegacyObj["DEVICE_A_TRUNK_NAME"]
            ednMacLegacyDataDict['device_a_ip'] = ednMacLegacyObj["DEVICE_A_IP"]
            ednMacLegacyDataDict['device_b_system_name'] = ednMacLegacyObj["DEVICE_B_SYSTEM_NAME"]
            ednMacLegacyDataDict['device_b_interface'] = ednMacLegacyObj["DEVICE_B_INTERFACE"]
            ednMacLegacyDataDict['device_b_ip'] = ednMacLegacyObj["DEVICE_B_IP"]
            ednMacLegacyDataDict['device_b_type'] = ednMacLegacyObj["DEVICE_B_TYPE"]
            ednMacLegacyDataDict['device_b_port_desc'] = ednMacLegacyObj["DEVICE_B_PORT_DESC"]
            ednMacLegacyDataDict['device_a_mac'] = ednMacLegacyObj["DEVICE_A_MAC"]
            ednMacLegacyDataDict['device_b_mac'] = ednMacLegacyObj["DEVICE_B_MAC"]
            ednMacLegacyDataDict['device_a_port_desc'] = ednMacLegacyObj["DEVICE_A_PORT_DESC"]
            ednMacLegacyDataDict['device_a_vlan'] = ednMacLegacyObj["DEVICE_A_VLAN"]
            ednMacLegacyDataDict['device_a_vlan_name'] = ednMacLegacyObj["DEVICE_A_VLAN_NAME"]
            ednMacLegacyDataDict['server_name'] = ednMacLegacyObj["SERVER_NAME"]
            ednMacLegacyDataDict['owner_name'] = ednMacLegacyObj["OWNER_NAME"]
            ednMacLegacyDataDict['server_os'] = ednMacLegacyObj["SERVER_OS"]
            ednMacLegacyDataDict['app_name'] = ednMacLegacyObj["APP_NAME"]
            ednMacLegacyDataDict['owner_email'] = ednMacLegacyObj["OWNER_EMAIL"]
            ednMacLegacyDataDict['owner_contact'] = ednMacLegacyObj["OWNER_CONTACT"]
            ednMacLegacyDataDict['modified_by'] = ednMacLegacyObj["MODIFIED_BY"]
            ednMacLegacyDataDict['creation_date'] = FormatDate(ednMacLegacyObj["CREATION_DATE"])
            ednMacLegacyDataDict['modification_date'] = FormatDate(ednMacLegacyObj["MODIFICATION_DATE"])
            ednMacLegacyDataDict['arp_source_name'] = ednMacLegacyObj["ARP_SOURCE_NAME"]
            ednMacLegacyDataDict['arp_source_type'] = ednMacLegacyObj["ARP_SOURCE_TYPE"]
            ednMacLegacyDataDict['service_vendor'] = ednMacLegacyObj["SERVICE_VENDOR"]
            ednMacLegacyDataDict['device_b_mac_vendor'] = ednMacLegacyObj["DEVICE_B_MAC_VENDOR"]
            ednMacLegacyDataDict['device_a_rx'] = ednMacLegacyObj["DEVICE_A_RX"]
            ednMacLegacyDataDict['device_a_tx'] = ednMacLegacyObj["DEVICE_A_TX"]
            ednMacLegacyDataDict['f5_lb'] = ednMacLegacyObj["F5_LB"]
            ednMacLegacyDataDict['f5_vip'] = ednMacLegacyObj["F5_VIP"]
            ednMacLegacyDataDict['f5_node_status'] = ednMacLegacyObj["F5_NODE_STATUS"]
            ednMacLegacyObjList.append(ednMacLegacyDataDict)

        content = gzip.compress(json.dumps(ednMacLegacyObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def createEdnMacLegacyQuery(dateObj, limit, offset):
    try:
        query=""
        count_query=""
        search_query=""
        export_query=""
        count_query = "SELECT COUNT(*) as total_count FROM edn_mac_legacy WHERE 1=1"
        search_query = "SELECT * FROM edn_mac_legacy WHERE 1=1"
        if 'device_a_name' in dateObj and dateObj['device_a_name']:
            query += f" AND device_a_name LIKE '%%{dateObj['device_a_name']}%%'"
        if 'device_a_ip' in dateObj and dateObj['device_a_ip']:
            query += f" AND device_a_ip = '{dateObj['device_a_ip']}'"
        if 'device_b_ip' in dateObj and dateObj['device_b_ip']:
            query += f" AND device_b_ip = '{dateObj['device_b_ip']}'"
        if 'device_b_system_name' in dateObj and dateObj['device_b_system_name']:
            query += f" AND device_b_system_name  LIKE '%%{dateObj['device_b_system_name']}%%'"
        if 'device_b_mac' in dateObj and dateObj['device_b_mac']:
            query += f" AND device_b_mac = '{dateObj['device_b_mac']}'"
        if 'device_a_vlan' in dateObj and dateObj['device_a_vlan']:
            query += f" AND device_a_vlan  LIKE '%%{dateObj['device_a_vlan']}%%'"
        if 'app_name' in dateObj and dateObj['app_name']:
            query += f" AND app_name  LIKE '%%{dateObj['app_name']}%%'"
        if 'server_name' in dateObj and dateObj['server_name']:
            query += f" AND server_name  LIKE '%%{dateObj['server_name']}%%'"
        if 'service_vendor' in dateObj and dateObj['service_vendor']:
            query += f" AND service_vendor  LIKE '%%{dateObj['service_vendor']}%%'"
        if 'f5_lb' in dateObj and dateObj['f5_lb']:
            query += f" AND f5_lb LIKE '%%{dateObj['f5_lb']}%%'"
        if 'arp_source_name' in dateObj and dateObj['arp_source_name']:
            query += f" AND arp_source_name LIKE '%%{dateObj['arp_source_name']}%%'"
        if 'fetch_date' in dateObj and dateObj['fetch_date']:
            utc = datetime.strptime(dateObj['fetch_date'], '%a, %d %b %Y %H:%M:%S GMT')
            fetch_date = utc.strftime("%Y-%m-%d %H:%M:%S")
            
            #fetch_date = datetime.strptime(dateObj['fetch_date'], '%d-%m-%Y')
            query += f" AND creation_date = '{fetch_date}'"
        count_query+= query+";"
        export_query+=search_query+query+";"
        search_query += f" {query} LIMIT {limit} OFFSET {offset};"
        return search_query, count_query, export_query
    except Exception as e:
        return ""


# @app.route("/getEdnMacLegacyBySearchFiltersCount", methods = ['POST'])
# @token_required
# def getEdnMacLegacyBySearchFiltersCount(user_data):
#     if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
#         ednMacLegacyObjList=[]
#         #ednMacLegacyObjs = EDN_MAC_LEGACY.query.all()
#         limit = request.args.get("limit")
#         offset = request.args.get("offset")
#         dateObj = request.get_json()
#         #print(type(dateObj['date']),file=sys.stderr)  

#         #utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
#         #print(utc,file=sys.stderr)
#         #current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
#         #print(current_time,file=sys.stderr)

#             # Build the query
        
#         query= createEdnMacLegacyQuery(dateObj, limit, offset)
#         ednMacLegacyObjs = phy_engine.execute(query)
#         count= len(ednMacLegacyObjs)
        
#         content = gzip.compress(json.dumps(count).encode('utf8'), 5)
#         response = make_response(content)
#         response.headers['Content-length'] = len(content)
#         response.headers['Content-Encoding'] = 'gzip'
#         return response
#     else: 
#         print("Authentication Failed", file=sys.stderr)
#         return jsonify({'message': 'Authentication Failed'}), 401


@app.route("/getEdnMacLegacyBySearchFilters", methods = ['POST'])
@token_required
def GetEdnMacLegacyBySearchFilters(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednMacLegacyObjList=[]
        #ednMacLegacyObjs = EDN_MAC_LEGACY.query.all()
        limit = request.args.get("limit")
        offset = request.args.get("offset")
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        #utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        #current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

            # Build the query
        query, count_query, export_query = createEdnMacLegacyQuery(dateObj, limit, offset)
        ednMacLegacyObjs = phy_engine.execute(query)
        count=0
        count = phy_engine.execute(count_query).scalar()
        
        for ednMacLegacyObj in ednMacLegacyObjs:

            ednMacLegacyDataDict= {}
            ednMacLegacyDataDict['edn_mac_legacy_id']=ednMacLegacyObj["EDN_MAC_LEGACY_ID"]
            ednMacLegacyDataDict['device_a_name'] = ednMacLegacyObj["DEVICE_A_NAME"]
            ednMacLegacyDataDict['device_a_interface'] = ednMacLegacyObj["DEVICE_A_INTERFACE"]
            ednMacLegacyDataDict['device_a_trunk_name'] = ednMacLegacyObj["DEVICE_A_TRUNK_NAME"]
            ednMacLegacyDataDict['device_a_ip'] = ednMacLegacyObj["DEVICE_A_IP"]
            ednMacLegacyDataDict['device_b_system_name'] = ednMacLegacyObj["DEVICE_B_SYSTEM_NAME"]
            ednMacLegacyDataDict['device_b_interface'] = ednMacLegacyObj["DEVICE_B_INTERFACE"]
            ednMacLegacyDataDict['device_b_ip'] = ednMacLegacyObj["DEVICE_B_IP"]
            ednMacLegacyDataDict['device_b_type'] = ednMacLegacyObj["DEVICE_B_TYPE"]
            ednMacLegacyDataDict['device_b_port_desc'] = ednMacLegacyObj["DEVICE_B_PORT_DESC"]
            ednMacLegacyDataDict['device_a_mac'] = ednMacLegacyObj["DEVICE_A_MAC"]
            ednMacLegacyDataDict['device_b_mac'] = ednMacLegacyObj["DEVICE_B_MAC"]
            ednMacLegacyDataDict['device_a_port_desc'] = ednMacLegacyObj["DEVICE_A_PORT_DESC"]
            ednMacLegacyDataDict['device_a_vlan'] = ednMacLegacyObj["DEVICE_A_VLAN"]
            ednMacLegacyDataDict['device_a_vlan_name'] = ednMacLegacyObj["DEVICE_A_VLAN_NAME"]
            ednMacLegacyDataDict['server_name'] = ednMacLegacyObj["SERVER_NAME"]
            ednMacLegacyDataDict['owner_name'] = ednMacLegacyObj["OWNER_NAME"]
            ednMacLegacyDataDict['server_os'] = ednMacLegacyObj["SERVER_OS"]
            ednMacLegacyDataDict['app_name'] = ednMacLegacyObj["APP_NAME"]
            ednMacLegacyDataDict['owner_email'] = ednMacLegacyObj["OWNER_EMAIL"]
            ednMacLegacyDataDict['owner_contact'] = ednMacLegacyObj["OWNER_CONTACT"]
            ednMacLegacyDataDict['modified_by'] = ednMacLegacyObj["MODIFIED_BY"]
            ednMacLegacyDataDict['creation_date'] = FormatDate(ednMacLegacyObj["CREATION_DATE"])
            ednMacLegacyDataDict['modification_date'] = FormatDate(ednMacLegacyObj["MODIFICATION_DATE"])
            ednMacLegacyDataDict['arp_source_name'] = ednMacLegacyObj["ARP_SOURCE_NAME"]
            ednMacLegacyDataDict['arp_source_type'] = ednMacLegacyObj["ARP_SOURCE_TYPE"]
            ednMacLegacyDataDict['service_vendor'] = ednMacLegacyObj["SERVICE_VENDOR"]
            ednMacLegacyDataDict['device_b_mac_vendor'] = ednMacLegacyObj["DEVICE_B_MAC_VENDOR"]
            ednMacLegacyDataDict['device_a_rx'] = ednMacLegacyObj["DEVICE_A_RX"]
            ednMacLegacyDataDict['device_a_tx'] = ednMacLegacyObj["DEVICE_A_TX"]
            ednMacLegacyDataDict['f5_lb'] = ednMacLegacyObj["F5_LB"]
            ednMacLegacyDataDict['f5_vip'] = ednMacLegacyObj["F5_VIP"]
            ednMacLegacyDataDict['f5_node_status'] = ednMacLegacyObj["F5_NODE_STATUS"]
            ednMacLegacyObjList.append(ednMacLegacyDataDict)

        content = gzip.compress(json.dumps({'total':count, 'data': ednMacLegacyObjList}).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/exportEdnMacLegacySearched", methods = ['POST'])
@token_required
def ExportEdnMacLegacySearched(user_data):
    if True:#
        ednMacLegacyObjList=[]
        #ednMacLegacyObjs = EDN_MAC_LEGACY.query.all()
        limit = request.args.get("limit")
        offset = request.args.get("offset")
        dateObj = request.get_json()
        #print(type(dateObj['date']),file=sys.stderr)  

        #utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        #print(utc,file=sys.stderr)
        #current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        #print(current_time,file=sys.stderr)

            # Build the query
        query, count_query, export_query = createEdnMacLegacyQuery(dateObj, limit, offset)
        ednMacLegacyObjs = phy_engine.execute(export_query)
        #count=0
        #count = phy_engine.execute(count_query).scalar()
        
        for ednMacLegacyObj in ednMacLegacyObjs:

            ednMacLegacyDataDict= {}
            ednMacLegacyDataDict['edn_mac_legacy_id']=ednMacLegacyObj["EDN_MAC_LEGACY_ID"]
            ednMacLegacyDataDict['device_a_name'] = ednMacLegacyObj["DEVICE_A_NAME"]
            ednMacLegacyDataDict['device_a_interface'] = ednMacLegacyObj["DEVICE_A_INTERFACE"]
            ednMacLegacyDataDict['device_a_trunk_name'] = ednMacLegacyObj["DEVICE_A_TRUNK_NAME"]
            ednMacLegacyDataDict['device_a_ip'] = ednMacLegacyObj["DEVICE_A_IP"]
            ednMacLegacyDataDict['device_b_system_name'] = ednMacLegacyObj["DEVICE_B_SYSTEM_NAME"]
            ednMacLegacyDataDict['device_b_interface'] = ednMacLegacyObj["DEVICE_B_INTERFACE"]
            ednMacLegacyDataDict['device_b_ip'] = ednMacLegacyObj["DEVICE_B_IP"]
            ednMacLegacyDataDict['device_b_type'] = ednMacLegacyObj["DEVICE_B_TYPE"]
            ednMacLegacyDataDict['device_b_port_desc'] = ednMacLegacyObj["DEVICE_B_PORT_DESC"]
            ednMacLegacyDataDict['device_a_mac'] = ednMacLegacyObj["DEVICE_A_MAC"]
            ednMacLegacyDataDict['device_b_mac'] = ednMacLegacyObj["DEVICE_B_MAC"]
            ednMacLegacyDataDict['device_a_port_desc'] = ednMacLegacyObj["DEVICE_A_PORT_DESC"]
            ednMacLegacyDataDict['device_a_vlan'] = ednMacLegacyObj["DEVICE_A_VLAN"]
            ednMacLegacyDataDict['device_a_vlan_name'] = ednMacLegacyObj["DEVICE_A_VLAN_NAME"]
            ednMacLegacyDataDict['server_name'] = ednMacLegacyObj["SERVER_NAME"]
            ednMacLegacyDataDict['owner_name'] = ednMacLegacyObj["OWNER_NAME"]
            ednMacLegacyDataDict['server_os'] = ednMacLegacyObj["SERVER_OS"]
            ednMacLegacyDataDict['app_name'] = ednMacLegacyObj["APP_NAME"]
            ednMacLegacyDataDict['owner_email'] = ednMacLegacyObj["OWNER_EMAIL"]
            ednMacLegacyDataDict['owner_contact'] = ednMacLegacyObj["OWNER_CONTACT"]
            ednMacLegacyDataDict['modified_by'] = ednMacLegacyObj["MODIFIED_BY"]
            ednMacLegacyDataDict['creation_date'] = FormatDate(ednMacLegacyObj["CREATION_DATE"])
            ednMacLegacyDataDict['modification_date'] = FormatDate(ednMacLegacyObj["MODIFICATION_DATE"])
            ednMacLegacyDataDict['arp_source_name'] = ednMacLegacyObj["ARP_SOURCE_NAME"]
            ednMacLegacyDataDict['arp_source_type'] = ednMacLegacyObj["ARP_SOURCE_TYPE"]
            ednMacLegacyDataDict['service_vendor'] = ednMacLegacyObj["SERVICE_VENDOR"]
            ednMacLegacyDataDict['device_b_mac_vendor'] = ednMacLegacyObj["DEVICE_B_MAC_VENDOR"]
            ednMacLegacyDataDict['device_a_rx'] = ednMacLegacyObj["DEVICE_A_RX"]
            ednMacLegacyDataDict['device_a_tx'] = ednMacLegacyObj["DEVICE_A_TX"]
            ednMacLegacyDataDict['f5_lb'] = ednMacLegacyObj["F5_LB"]
            ednMacLegacyDataDict['f5_vip'] = ednMacLegacyObj["F5_VIP"]
            ednMacLegacyDataDict['f5_node_status'] = ednMacLegacyObj["F5_NODE_STATUS"]
            ednMacLegacyObjList.append(ednMacLegacyDataDict)

        content = gzip.compress(json.dumps(ednMacLegacyObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401



@app.route("/exportEdnMacLegacy", methods = ['GET'])
@token_required
def ExportEdnMacLegacy(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednMacLegacyObjList=[]
        #ednMacLegacyObjs = EDN_MAC_LEGACY.query.all()
        ednMacLegacyObjs = phy_engine.execute('SELECT * FROM edn_mac_legacy WHERE creation_date = (SELECT max(creation_date) FROM edn_mac_legacy)')
        
        for ednMacLegacyObj in ednMacLegacyObjs:

            ednMacLegacyDataDict= {}
            ednMacLegacyDataDict['edn_mac_legacy_id']=ednMacLegacyObj["EDN_MAC_LEGACY_ID"]
            ednMacLegacyDataDict['device_a_name'] = ednMacLegacyObj["DEVICE_A_NAME"]
            ednMacLegacyDataDict['device_a_interface'] = ednMacLegacyObj["DEVICE_A_INTERFACE"]
            ednMacLegacyDataDict['device_a_trunk_name'] = ednMacLegacyObj["DEVICE_A_TRUNK_NAME"]
            ednMacLegacyDataDict['device_a_ip'] = ednMacLegacyObj["DEVICE_A_IP"]
            ednMacLegacyDataDict['device_b_system_name'] = ednMacLegacyObj["DEVICE_B_SYSTEM_NAME"]
            ednMacLegacyDataDict['device_b_interface'] = ednMacLegacyObj["DEVICE_B_INTERFACE"]
            ednMacLegacyDataDict['device_b_ip'] = ednMacLegacyObj["DEVICE_B_IP"]
            ednMacLegacyDataDict['device_b_type'] = ednMacLegacyObj["DEVICE_B_TYPE"]
            ednMacLegacyDataDict['device_b_port_desc'] = ednMacLegacyObj["DEVICE_B_PORT_DESC"]
            ednMacLegacyDataDict['device_a_mac'] = ednMacLegacyObj["DEVICE_A_MAC"]
            ednMacLegacyDataDict['device_b_mac'] = ednMacLegacyObj["DEVICE_B_MAC"]
            ednMacLegacyDataDict['device_a_port_desc'] = ednMacLegacyObj["DEVICE_A_PORT_DESC"]
            ednMacLegacyDataDict['device_a_vlan'] = ednMacLegacyObj["DEVICE_A_VLAN"]
            ednMacLegacyDataDict['server_name'] = ednMacLegacyObj["SERVER_NAME"]
            ednMacLegacyDataDict['owner_name'] = ednMacLegacyObj["OWNER_NAME"]
            ednMacLegacyDataDict['owner_email'] = ednMacLegacyObj["OWNER_EMAIL"]
            ednMacLegacyDataDict['owner_contact'] = ednMacLegacyObj["OWNER_CONTACT"]
            ednMacLegacyDataDict['creation_date'] = FormatDate(ednMacLegacyObj["CREATION_DATE"])
            ednMacLegacyDataDict['modification_date'] = FormatDate(ednMacLegacyObj["MODIFICATION_DATE"])
            
            ednMacLegacyObjList.append(ednMacLegacyDataDict)

        return jsonify(ednMacLegacyObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnLldpAci", methods = ['GET'])
@token_required
def GetAllEdnLldpAci(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednLldpAciObjList=[]

        #ednLldpAciObjs = EDN_LLDP_ACI.query.all()
        
        ednLldpAciObjs = phy_engine.execute('SELECT * FROM edn_lldp_aci WHERE creation_date = (SELECT max(creation_date) FROM edn_lldp_aci)')
        
        for ednLldpAciObj in ednLldpAciObjs:
            ednLldpAciDataDict= {}
            ednLldpAciDataDict['edn_lldp_aci_id']=ednLldpAciObj['EDN_LLDP_ACI_ID']
            ednLldpAciDataDict['device_a_name'] = ednLldpAciObj['DEVICE_A_NAME']
            ednLldpAciDataDict['device_a_interface'] = ednLldpAciObj['DEVICE_A_INTERFACE']
            ednLldpAciDataDict['device_a_trunk_name'] = ednLldpAciObj['DEVICE_A_TRUNK_NAME']
            ednLldpAciDataDict['device_a_ip'] = ednLldpAciObj['DEVICE_A_IP']
            ednLldpAciDataDict['device_b_system_name'] = ednLldpAciObj['DEVICE_B_SYSTEM_NAME']
            ednLldpAciDataDict['device_b_interface'] = ednLldpAciObj['DEVICE_B_INTERFACE']
            ednLldpAciDataDict['device_b_ip'] = ednLldpAciObj['DEVICE_B_IP']
            ednLldpAciDataDict['device_b_type'] = ednLldpAciObj['DEVICE_B_TYPE']
            ednLldpAciDataDict['device_b_port_desc'] = ednLldpAciObj['DEVICE_B_PORT_DESC']
            ednLldpAciDataDict['device_a_mac'] = ednLldpAciObj['DEVICE_A_MAC']
            ednLldpAciDataDict['device_b_mac'] = ednLldpAciObj['DEVICE_B_MAC']
            ednLldpAciDataDict['device_a_port_desc'] = ednLldpAciObj['DEVICE_A_PORT_DESC']
            ednLldpAciDataDict['device_a_vlan'] = ednLldpAciObj['DEVICE_A_VLAN']
            ednLldpAciDataDict['device_a_vlan_name'] = ednLldpAciObj["DEVICE_A_VLAN_NAME"]
            ednLldpAciDataDict['server_os'] = ednLldpAciObj['SERVER_OS']
            ednLldpAciDataDict['app_name'] = ednLldpAciObj['APP_NAME']
            ednLldpAciDataDict['server_name'] = ednLldpAciObj['SERVER_NAME']
            ednLldpAciDataDict['owner_name'] = ednLldpAciObj['OWNER_NAME']
            ednLldpAciDataDict['owner_email'] = ednLldpAciObj['OWNER_EMAIL']
            ednLldpAciDataDict['owner_contact'] = ednLldpAciObj['OWNER_CONTACT']
            ednLldpAciDataDict['creation_date'] = FormatDate(ednLldpAciObj['CREATION_DATE'])
            ednLldpAciDataDict['modification_date'] = FormatDate(ednLldpAciObj['MODIFICATION_DATE'])
            
            ednLldpAciObjList.append(ednLldpAciDataDict)

        content = gzip.compress(json.dumps(ednLldpAciObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllEdnLldpAciDates',methods=['GET'])
@token_required
def GetAllEdnLldpAciDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from edn_lldp_aci ORDER BY creation_date DESC;"
        
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getAllEdnLldpAciByDate", methods = ['POST'])
@token_required
def GetAllEdnLldpAciByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednLldpAciObjList=[]

        #ednLldpAciObjs = EDN_LLDP_ACI.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        ednLldpAciObjs = phy_engine.execute(f"SELECT * FROM edn_lldp_aci WHERE creation_date = '{current_time})'")
        
        for ednLldpAciObj in ednLldpAciObjs:
            ednLldpAciDataDict= {}
            ednLldpAciDataDict['edn_lldp_aci_id']=ednLldpAciObj['EDN_LLDP_ACI_ID']
            ednLldpAciDataDict['device_a_name'] = ednLldpAciObj['DEVICE_A_NAME']
            ednLldpAciDataDict['device_a_interface'] = ednLldpAciObj['DEVICE_A_INTERFACE']
            ednLldpAciDataDict['device_a_trunk_name'] = ednLldpAciObj['DEVICE_A_TRUNK_NAME']
            ednLldpAciDataDict['device_a_ip'] = ednLldpAciObj['DEVICE_A_IP']
            ednLldpAciDataDict['device_b_system_name'] = ednLldpAciObj['DEVICE_B_SYSTEM_NAME']
            ednLldpAciDataDict['device_b_interface'] = ednLldpAciObj['DEVICE_B_INTERFACE']
            ednLldpAciDataDict['device_b_ip'] = ednLldpAciObj['DEVICE_B_IP']
            ednLldpAciDataDict['device_b_type'] = ednLldpAciObj['DEVICE_B_TYPE']
            ednLldpAciDataDict['device_b_port_desc'] = ednLldpAciObj['DEVICE_B_PORT_DESC']
            ednLldpAciDataDict['device_a_mac'] = ednLldpAciObj['DEVICE_A_MAC']
            ednLldpAciDataDict['device_b_mac'] = ednLldpAciObj['DEVICE_B_MAC']
            ednLldpAciDataDict['device_a_port_desc'] = ednLldpAciObj['DEVICE_A_PORT_DESC']
            ednLldpAciDataDict['device_a_vlan'] = ednLldpAciObj['DEVICE_A_VLAN']
            ednLldpAciDataDict['server_name'] = ednLldpAciObj['SERVER_NAME']
            ednLldpAciDataDict['server_os'] = ednLldpAciObj['SERVER_OS']
            ednLldpAciDataDict['app_name'] = ednLldpAciObj['APP_NAME']
            ednLldpAciDataDict['owner_name'] = ednLldpAciObj['OWNER_NAME']
            ednLldpAciDataDict['owner_email'] = ednLldpAciObj['OWNER_EMAIL']
            ednLldpAciDataDict['owner_contact'] = ednLldpAciObj['OWNER_CONTACT']
            ednLldpAciDataDict['creation_date'] = FormatDate(ednLldpAciObj['CREATION_DATE'])
            ednLldpAciDataDict['modification_date'] = FormatDate(ednLldpAciObj['MODIFICATION_DATE'])
            ednLldpAciDataDict['device_b_mac_vendor'] = ednLldpAciObj["DEVICE_B_MAC_VENDOR"]
            ednLldpAciObjList.append(ednLldpAciDataDict)

        content = gzip.compress(json.dumps(ednLldpAciObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/exportEdnLldpAci", methods = ['GET'])
@token_required
def ExportEdnLldpAci(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednLldpAciObjList=[]
        #ednLldpAciObjs = EDN_LLDP_ACI.query.all()
        ednLldpAciObjs = phy_engine.execute('SELECT * FROM edn_lldp_aci WHERE creation_date = (SELECT max(creation_date) FROM edn_lldp_aci)')
        
        for ednLldpAciObj in ednLldpAciObjs:

            ednLldpAciDataDict= {}
            ednLldpAciDataDict['edn_lldp_aci_id']=ednLldpAciObj['EDN_LLDP_ACI_ID']
            ednLldpAciDataDict['device_a_name'] = ednLldpAciObj['DEVICE_A_NAME']
            ednLldpAciDataDict['device_a_interface'] = ednLldpAciObj['DEVICE_A_INTERFACE']
            ednLldpAciDataDict['device_a_trunk_name'] = ednLldpAciObj['DEVICE_A_TRUNK_NAME']
            ednLldpAciDataDict['device_a_ip'] = ednLldpAciObj['DEVICE_A_IP']
            ednLldpAciDataDict['device_b_system_name'] = ednLldpAciObj['DEVICE_B_SYSTEM_NAME']
            ednLldpAciDataDict['device_b_interface'] = ednLldpAciObj['DEVICE_B_INTERFACE']
            ednLldpAciDataDict['device_b_ip'] = ednLldpAciObj['DEVICE_B_IP']
            ednLldpAciDataDict['device_b_type'] = ednLldpAciObj['DEVICE_B_TYPE']
            ednLldpAciDataDict['device_b_port_desc'] = ednLldpAciObj['DEVICE_B_PORT_DESC']
            ednLldpAciDataDict['device_a_mac'] = ednLldpAciObj['DEVICE_A_MAC']
            ednLldpAciDataDict['device_b_mac'] = ednLldpAciObj['DEVICE_B_MAC']
            ednLldpAciDataDict['device_a_port_desc'] = ednLldpAciObj['DEVICE_A_PORT_DESC']
            ednLldpAciDataDict['device_a_vlan'] = ednLldpAciObj['DEVICE_A_VLAN']
            ednLldpAciDataDict['server_name'] = ednLldpAciObj['SERVER_NAME']
            ednLldpAciDataDict['owner_name'] = ednLldpAciObj['OWNER_NAME']
            ednLldpAciDataDict['owner_email'] = ednLldpAciObj['OWNER_EMAIL']
            ednLldpAciDataDict['owner_contact'] = ednLldpAciObj['OWNER_CONTACT']
            ednLldpAciDataDict['creation_date'] = FormatDate(ednLldpAciObj['CREATION_DATE'])
            ednLldpAciDataDict['modification_date'] = FormatDate(ednLldpAciObj['MODIFICATION_DATE'])
            
            ednLldpAciObjList.append(ednLldpAciDataDict)

        return jsonify(ednLldpAciObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/getAllIgwLldpAci", methods = ['GET'])
@token_required
def GetAllIgwLldpAci(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        IgwLldpAciObjList=[]
        
        #IgwLldpAciObjs = IGW_LLDP_ACI.query.all()
        IgwLldpAciObjs = phy_engine.execute('SELECT * FROM igw_lldp_aci WHERE creation_date = (SELECT max(creation_date) FROM igw_lldp_aci)')
        
        for IgwLldpAciObj in IgwLldpAciObjs:

            IgwLldpAciDataDict= {}
            IgwLldpAciDataDict['igw_lldp_aci_id']=IgwLldpAciObj['IGW_LLDP_ACI_ID']
            IgwLldpAciDataDict['device_a_name'] = IgwLldpAciObj['DEVICE_A_NAME']
            IgwLldpAciDataDict['device_a_interface'] = IgwLldpAciObj['DEVICE_A_INTERFACE']
            IgwLldpAciDataDict['device_a_trunk_name'] = IgwLldpAciObj['DEVICE_A_TRUNK_NAME']
            IgwLldpAciDataDict['device_a_ip'] = IgwLldpAciObj['DEVICE_A_IP']
            IgwLldpAciDataDict['device_b_system_name'] = IgwLldpAciObj['DEVICE_B_SYSTEM_NAME']
            IgwLldpAciDataDict['device_b_interface'] = IgwLldpAciObj['DEVICE_B_INTERFACE']
            IgwLldpAciDataDict['device_b_ip'] = IgwLldpAciObj['DEVICE_B_IP']
            IgwLldpAciDataDict['device_b_type'] = IgwLldpAciObj['DEVICE_B_TYPE']
            IgwLldpAciDataDict['device_b_port_desc'] = IgwLldpAciObj['DEVICE_B_PORT_DESC']
            IgwLldpAciDataDict['device_a_mac'] = IgwLldpAciObj['DEVICE_A_MAC']
            IgwLldpAciDataDict['device_b_mac'] = IgwLldpAciObj['DEVICE_B_MAC']
            IgwLldpAciDataDict['device_a_port_desc'] = IgwLldpAciObj['DEVICE_A_PORT_DESC']
            IgwLldpAciDataDict['device_a_vlan'] = IgwLldpAciObj['DEVICE_A_VLAN']
            IgwLldpAciDataDict['device_a_vlan_name'] = IgwLldpAciObj["DEVICE_A_VLAN_NAME"]
            IgwLldpAciDataDict['server_name'] = IgwLldpAciObj['SERVER_NAME']
            IgwLldpAciDataDict['server_os'] = IgwLldpAciObj['SERVER_OS']
            IgwLldpAciDataDict['app_name'] = IgwLldpAciObj['APP_NAME']
            IgwLldpAciDataDict['owner_name'] = IgwLldpAciObj['OWNER_NAME']
            IgwLldpAciDataDict['owner_email'] = IgwLldpAciObj['OWNER_EMAIL']
            IgwLldpAciDataDict['owner_contact'] = IgwLldpAciObj['OWNER_CONTACT']
            IgwLldpAciDataDict['creation_date'] = FormatDate(IgwLldpAciObj['CREATION_DATE'])
            IgwLldpAciDataDict['modification_date'] = FormatDate(IgwLldpAciObj['MODIFICATION_DATE'])
            IgwLldpAciObjList.append(IgwLldpAciDataDict)
        
        content = gzip.compress(json.dumps(IgwLldpAciObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllIgwLldpAciDates',methods=['GET'])
@token_required
def GetAllIgwLldpAciDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from igw_lldp_aci ORDER BY creation_date DESC;"
        
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllIgwLldpAciByDate", methods = ['POST'])
@token_required
def GetAllIgwLldpAciByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        IgwLldpAciObjList=[]
        
        #IgwLldpAciObjs = IGW_LLDP_ACI.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)

        IgwLldpAciObjs = phy_engine.execute(f"SELECT * FROM igw_lldp_aci WHERE creation_date = '{current_time}'")
        
        for IgwLldpAciObj in IgwLldpAciObjs:

            IgwLldpAciDataDict= {}
            IgwLldpAciDataDict['igw_lldp_aci_id']=IgwLldpAciObj['IGW_LLDP_ACI_ID']
            IgwLldpAciDataDict['device_a_name'] = IgwLldpAciObj['DEVICE_A_NAME']
            IgwLldpAciDataDict['device_a_interface'] = IgwLldpAciObj['DEVICE_A_INTERFACE']
            IgwLldpAciDataDict['device_a_trunk_name'] = IgwLldpAciObj['DEVICE_A_TRUNK_NAME']
            IgwLldpAciDataDict['device_a_ip'] = IgwLldpAciObj['DEVICE_A_IP']
            IgwLldpAciDataDict['device_b_system_name'] = IgwLldpAciObj['DEVICE_B_SYSTEM_NAME']
            IgwLldpAciDataDict['device_b_interface'] = IgwLldpAciObj['DEVICE_B_INTERFACE']
            IgwLldpAciDataDict['device_b_ip'] = IgwLldpAciObj['DEVICE_B_IP']
            IgwLldpAciDataDict['device_b_type'] = IgwLldpAciObj['DEVICE_B_TYPE']
            IgwLldpAciDataDict['device_b_port_desc'] = IgwLldpAciObj['DEVICE_B_PORT_DESC']
            IgwLldpAciDataDict['device_a_mac'] = IgwLldpAciObj['DEVICE_A_MAC']
            IgwLldpAciDataDict['device_b_mac'] = IgwLldpAciObj['DEVICE_B_MAC']
            IgwLldpAciDataDict['device_a_port_desc'] = IgwLldpAciObj['DEVICE_A_PORT_DESC']
            IgwLldpAciDataDict['device_a_vlan'] = IgwLldpAciObj['DEVICE_A_VLAN']
            IgwLldpAciDataDict['device_a_vlan_name'] = IgwLldpAciObj["DEVICE_A_VLAN_NAME"]
            IgwLldpAciDataDict['server_name'] = IgwLldpAciObj['SERVER_NAME']
            IgwLldpAciDataDict['server_os'] = IgwLldpAciObj['SERVER_OS']
            IgwLldpAciDataDict['app_name'] = IgwLldpAciObj['APP_NAME']
            IgwLldpAciDataDict['owner_name'] = IgwLldpAciObj['OWNER_NAME']
            IgwLldpAciDataDict['owner_email'] = IgwLldpAciObj['OWNER_EMAIL']
            IgwLldpAciDataDict['owner_contact'] = IgwLldpAciObj['OWNER_CONTACT']
            IgwLldpAciDataDict['creation_date'] = FormatDate(IgwLldpAciObj['CREATION_DATE'])
            IgwLldpAciDataDict['modification_date'] = FormatDate(IgwLldpAciObj['MODIFICATION_DATE'])
            IgwLldpAciObjList.append(IgwLldpAciDataDict)
        
        content = gzip.compress(json.dumps(IgwLldpAciObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/exportIgwLldpAci", methods = ['GET'])
@token_required
def ExportIgwLldpAci(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwLldpAciObjList=[]
        #igwLldpAciObjs = IGW_LLDP_ACI.query.all()
        igwLldpAciObjs = phy_engine.execute('SELECT * FROM igw_lldp_aci WHERE creation_date = (SELECT max(creation_date) FROM igw_lldp_aci)')
        
        for IgwLldpAciObj in igwLldpAciObjs:
            IgwLldpAciDataDict= {}
            IgwLldpAciDataDict['igw_lldp_aci_id']=IgwLldpAciObj['IGW_LLDP_ACI_ID']
            IgwLldpAciDataDict['device_a_name'] = IgwLldpAciObj['DEVICE_A_NAME']
            IgwLldpAciDataDict['device_a_interface'] = IgwLldpAciObj['DEVICE_A_INTERFACE']
            IgwLldpAciDataDict['device_a_trunk_name'] = IgwLldpAciObj['DEVICE_A_TRUNK_NAME']
            IgwLldpAciDataDict['device_a_ip'] = IgwLldpAciObj['DEVICE_A_IP']
            IgwLldpAciDataDict['device_b_system_name'] = IgwLldpAciObj['DEVICE_B_SYSTEM_NAME']
            IgwLldpAciDataDict['device_b_interface'] = IgwLldpAciObj['DEVICE_B_INTERFACE']
            IgwLldpAciDataDict['device_b_ip'] = IgwLldpAciObj['DEVICE_B_IP']
            IgwLldpAciDataDict['device_b_type'] = IgwLldpAciObj['DEVICE_B_TYPE']
            IgwLldpAciDataDict['device_b_port_desc'] = IgwLldpAciObj['DEVICE_B_PORT_DESC']
            IgwLldpAciDataDict['device_a_mac'] = IgwLldpAciObj['DEVICE_A_MAC']
            IgwLldpAciDataDict['device_b_mac'] = IgwLldpAciObj['DEVICE_B_MAC']
            IgwLldpAciDataDict['device_a_port_desc'] = IgwLldpAciObj['DEVICE_A_PORT_DESC']
            IgwLldpAciDataDict['device_a_vlan'] = IgwLldpAciObj['DEVICE_A_VLAN']
            IgwLldpAciDataDict['server_name'] = IgwLldpAciObj['SERVER_NAME']
            IgwLldpAciDataDict['owner_name'] = IgwLldpAciObj['OWNER_NAME']
            IgwLldpAciDataDict['owner_email'] = IgwLldpAciObj['OWNER_EMAIL']
            IgwLldpAciDataDict['owner_contact'] = IgwLldpAciObj['OWNER_CONTACT']
            IgwLldpAciDataDict['creation_date'] = FormatDate(IgwLldpAciObj['CREATION_DATE'])
            IgwLldpAciDataDict['modification_date'] = FormatDate(IgwLldpAciObj['MODIFICATION_DATE'])
        
            igwLldpAciObjList.append(IgwLldpAciDataDict)



        return jsonify(igwLldpAciObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/getAllIgwCdpLegacy", methods = ['GET'])
@token_required
def GetAllIgwCdpLegacy(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwCdpLegacyObjList=[]
        
        #igwCdpLegacyObjs = IGW_CDP_LEGACY.query.all()
        igwCdpLegacyObjs = phy_engine.execute('SELECT * FROM igw_cdp_legacy WHERE creation_date = (SELECT max(creation_date) FROM igw_cdp_legacy)')
        
        for igwCdpLegacyObj in igwCdpLegacyObjs:

            igwCdpLegacyDataDict= {}
            igwCdpLegacyDataDict['igw_cdp_legacy_id']=igwCdpLegacyObj['IGW_CDP_LEGACY_ID']
            igwCdpLegacyDataDict['device_a_name'] = igwCdpLegacyObj['DEVICE_A_NAME']
            igwCdpLegacyDataDict['device_a_interface'] = igwCdpLegacyObj['DEVICE_A_INTERFACE']
            igwCdpLegacyDataDict['device_a_trunk_name'] = igwCdpLegacyObj['DEVICE_A_TRUNK_NAME']
            igwCdpLegacyDataDict['device_a_ip'] = igwCdpLegacyObj['DEVICE_A_IP']
            igwCdpLegacyDataDict['device_b_system_name'] = igwCdpLegacyObj['DEVICE_B_SYSTEM_NAME']
            igwCdpLegacyDataDict['device_b_interface'] = igwCdpLegacyObj['DEVICE_B_INTERFACE']
            igwCdpLegacyDataDict['device_b_ip'] = igwCdpLegacyObj['DEVICE_B_IP']
            igwCdpLegacyDataDict['device_b_type'] = igwCdpLegacyObj['DEVICE_B_TYPE']
            igwCdpLegacyDataDict['device_b_port_desc'] = igwCdpLegacyObj['DEVICE_B_PORT_DESC']
            igwCdpLegacyDataDict['device_a_mac'] = igwCdpLegacyObj['DEVICE_A_MAC']
            igwCdpLegacyDataDict['device_b_mac'] = igwCdpLegacyObj['DEVICE_B_MAC']
            igwCdpLegacyDataDict['device_a_port_desc'] = igwCdpLegacyObj['DEVICE_A_PORT_DESC']
            igwCdpLegacyDataDict['device_a_vlan'] = igwCdpLegacyObj['DEVICE_A_VLAN']
            igwCdpLegacyDataDict['server_name'] = igwCdpLegacyObj['SERVER_NAME']
            igwCdpLegacyDataDict['server_os'] = igwCdpLegacyObj['SERVER_OS']
            igwCdpLegacyDataDict['app_name'] = igwCdpLegacyObj['APP_NAME']
            igwCdpLegacyDataDict['owner_name'] = igwCdpLegacyObj['OWNER_NAME']
            igwCdpLegacyDataDict['owner_email'] = igwCdpLegacyObj['OWNER_EMAIL']
            igwCdpLegacyDataDict['owner_contact'] = igwCdpLegacyObj['OWNER_CONTACT']
            igwCdpLegacyDataDict['creation_date'] = FormatDate(igwCdpLegacyObj['CREATION_DATE'])
            igwCdpLegacyDataDict['modification_date'] = FormatDate(igwCdpLegacyObj['MODIFICATION_DATE'])
            igwCdpLegacyDataDict['device_b_mac_vendor'] = igwCdpLegacyObj["DEVICE_B_MAC_VENDOR"]
            igwCdpLegacyDataDict['service_vendor'] = igwCdpLegacyObj["SERVICE_VENDOR"]
            igwCdpLegacyObjList.append(igwCdpLegacyDataDict)

        content = gzip.compress(json.dumps(igwCdpLegacyObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllIgwCdpLegacyDates',methods=['GET'])
@token_required
def GetAllIgwCdpLegacyDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from igw_cdp_legacy ORDER BY creation_date DESC;"
        
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllIgwCdpLegacyByDate", methods = ['POST'])
@token_required
def GetAllIgwCdpLegacyByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwCdpLegacyObjList=[]
        
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        #igwCdpLegacyObjs = IGW_CDP_LEGACY.query.all()
        igwCdpLegacyObjs = phy_engine.execute(f"SELECT * FROM igw_cdp_legacy WHERE creation_date = '{current_time}'")
        
        for igwCdpLegacyObj in igwCdpLegacyObjs:

            igwCdpLegacyDataDict= {}
            igwCdpLegacyDataDict['igw_cdp_legacy_id']=igwCdpLegacyObj['IGW_CDP_LEGACY_ID']
            igwCdpLegacyDataDict['device_a_name'] = igwCdpLegacyObj['DEVICE_A_NAME']
            igwCdpLegacyDataDict['device_a_interface'] = igwCdpLegacyObj['DEVICE_A_INTERFACE']
            igwCdpLegacyDataDict['device_a_trunk_name'] = igwCdpLegacyObj['DEVICE_A_TRUNK_NAME']
            igwCdpLegacyDataDict['device_a_ip'] = igwCdpLegacyObj['DEVICE_A_IP']
            igwCdpLegacyDataDict['device_b_system_name'] = igwCdpLegacyObj['DEVICE_B_SYSTEM_NAME']
            igwCdpLegacyDataDict['device_b_interface'] = igwCdpLegacyObj['DEVICE_B_INTERFACE']
            igwCdpLegacyDataDict['device_b_ip'] = igwCdpLegacyObj['DEVICE_B_IP']
            igwCdpLegacyDataDict['device_b_type'] = igwCdpLegacyObj['DEVICE_B_TYPE']
            igwCdpLegacyDataDict['device_b_port_desc'] = igwCdpLegacyObj['DEVICE_B_PORT_DESC']
            igwCdpLegacyDataDict['device_a_mac'] = igwCdpLegacyObj['DEVICE_A_MAC']
            igwCdpLegacyDataDict['device_b_mac'] = igwCdpLegacyObj['DEVICE_B_MAC']
            igwCdpLegacyDataDict['device_a_port_desc'] = igwCdpLegacyObj['DEVICE_A_PORT_DESC']
            igwCdpLegacyDataDict['device_a_vlan'] = igwCdpLegacyObj['DEVICE_A_VLAN']
            igwCdpLegacyDataDict['server_name'] = igwCdpLegacyObj['SERVER_NAME']
            igwCdpLegacyDataDict['server_os'] = igwCdpLegacyObj['SERVER_OS']
            igwCdpLegacyDataDict['app_name'] = igwCdpLegacyObj['APP_NAME']
            igwCdpLegacyDataDict['owner_name'] = igwCdpLegacyObj['OWNER_NAME']
            igwCdpLegacyDataDict['owner_email'] = igwCdpLegacyObj['OWNER_EMAIL']
            igwCdpLegacyDataDict['owner_contact'] = igwCdpLegacyObj['OWNER_CONTACT']
            igwCdpLegacyDataDict['creation_date'] = FormatDate(igwCdpLegacyObj['CREATION_DATE'])
            igwCdpLegacyDataDict['modification_date'] = FormatDate(igwCdpLegacyObj['MODIFICATION_DATE'])
            igwCdpLegacyDataDict['device_b_mac_vendor'] = igwCdpLegacyObj["DEVICE_B_MAC_VENDOR"]
            igwCdpLegacyDataDict['service_vendor'] = igwCdpLegacyObj["SERVICE_VENDOR"]

            igwCdpLegacyObjList.append(igwCdpLegacyDataDict)

        content = gzip.compress(json.dumps(igwCdpLegacyObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/exportIgwCdpLegacy", methods = ['GET'])
@token_required
def ExportIgwCdpLegacy(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwCdpLegacyObjList=[]
        
        #igwCdpLegacyObjs = IGW_CDP_LEGACY.query.all()
        igwCdpLegacyObjs = phy_engine.execute('SELECT * FROM igw_cdp_legacy WHERE creation_date = (SELECT max(creation_date) FROM igw_cdp_legacy)')
        
        for igwCdpLegacyObj in igwCdpLegacyObjs:

            igwCdpLegacyDataDict= {}
            igwCdpLegacyDataDict['igw_cdp_legacy_id']=igwCdpLegacyObj['IGW_CDP_LEGACY_ID']
            igwCdpLegacyDataDict['device_a_name'] = igwCdpLegacyObj['DEVICE_A_NAME']
            igwCdpLegacyDataDict['device_a_interface'] = igwCdpLegacyObj['DEVICE_A_INTERFACE']
            igwCdpLegacyDataDict['device_a_trunk_name'] = igwCdpLegacyObj['DEVICE_A_TRUNK_NAME']
            igwCdpLegacyDataDict['device_a_ip'] = igwCdpLegacyObj['DEVICE_A_IP']
            igwCdpLegacyDataDict['device_b_system_name'] = igwCdpLegacyObj['DEVICE_B_SYSTEM_NAME']
            igwCdpLegacyDataDict['device_b_interface'] = igwCdpLegacyObj['DEVICE_B_INTERFACE']
            igwCdpLegacyDataDict['device_b_ip'] = igwCdpLegacyObj['DEVICE_B_IP']
            igwCdpLegacyDataDict['device_b_type'] = igwCdpLegacyObj['DEVICE_B_TYPE']
            igwCdpLegacyDataDict['device_b_port_desc'] = igwCdpLegacyObj['DEVICE_B_PORT_DESC']
            igwCdpLegacyDataDict['device_a_mac'] = igwCdpLegacyObj['DEVICE_A_MAC']
            igwCdpLegacyDataDict['device_b_mac'] = igwCdpLegacyObj['DEVICE_B_MAC']
            igwCdpLegacyDataDict['device_a_port_desc'] = igwCdpLegacyObj['DEVICE_A_PORT_DESC']
            igwCdpLegacyDataDict['device_a_vlan'] = igwCdpLegacyObj['DEVICE_A_VLAN']
            igwCdpLegacyDataDict['server_name'] = igwCdpLegacyObj['SERVER_NAME']
            igwCdpLegacyDataDict['owner_name'] = igwCdpLegacyObj['OWNER_NAME']
            igwCdpLegacyDataDict['owner_email'] = igwCdpLegacyObj['OWNER_EMAIL']
            igwCdpLegacyDataDict['owner_contact'] = igwCdpLegacyObj['OWNER_CONTACT']
            igwCdpLegacyDataDict['creation_date'] = FormatDate(igwCdpLegacyObj['CREATION_DATE'])
            igwCdpLegacyDataDict['modification_date'] = FormatDate(igwCdpLegacyObj['MODIFICATION_DATE'])
            
            igwCdpLegacyObjList.append(igwCdpLegacyDataDict)

        return jsonify(igwCdpLegacyObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/getAllEdnFirewallArp", methods = ['GET'])
@token_required
def GetAllEdnFirewallArp(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednFirewallArpObjList=[]

        #ednFirewallArpObjs = EDN_FIREWALL_ARP.query.all()
        ednFirewallArpObjs = phy_engine.execute('SELECT * FROM edn_firewall_arp WHERE creation_date = (SELECT max(creation_date) FROM edn_firewall_arp)')
        
        
        for ednFirewallArpObj in ednFirewallArpObjs:
            ednFirewallArpDataDict= {}
            ednFirewallArpDataDict['edn_firewall_arp_id']=ednFirewallArpObj['EDN_FIREWALL_ARP_ID']
            ednFirewallArpDataDict['firewall_id'] = ednFirewallArpObj['FIREWALL_ID']
            ednFirewallArpDataDict['mac'] = ednFirewallArpObj['MAC']
            ednFirewallArpDataDict['ip'] = ednFirewallArpObj['IP']
            ednFirewallArpDataDict['creation_date'] = FormatDate(ednFirewallArpObj['CREATION_DATE'])
            ednFirewallArpDataDict['modification_date'] = FormatDate(ednFirewallArpObj['MODIFICATION_DATE'])
            ednFirewallArpObjList.append(ednFirewallArpDataDict)


        content = gzip.compress(json.dumps(ednFirewallArpObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllEdnFirewallArpDates',methods=['GET'])
@token_required
def GetAllEdnFirewallArpDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from edn_firewall_arp ORDER BY creation_date DESC;"
        
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getAllEdnFirewallArpByDate", methods = ['POST'])
@token_required
def GetAllEdnFirewallArpByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednFirewallArpObjList=[]

        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)

        #ednFirewallArpObjs = EDN_FIREWALL_ARP.query.all()
        ednFirewallArpObjs = phy_engine.execute(f"SELECT * FROM edn_firewall_arp WHERE creation_date = '{current_time}'")
        
        
        for ednFirewallArpObj in ednFirewallArpObjs:
            ednFirewallArpDataDict= {}
            ednFirewallArpDataDict['edn_firewall_arp_id']=ednFirewallArpObj['EDN_FIREWALL_ARP_ID']
            ednFirewallArpDataDict['firewall_id'] = ednFirewallArpObj['FIREWALL_ID']
            ednFirewallArpDataDict['mac'] = ednFirewallArpObj['MAC']
            ednFirewallArpDataDict['ip'] = ednFirewallArpObj['IP']
            ednFirewallArpDataDict['creation_date'] = FormatDate(ednFirewallArpObj['CREATION_DATE'])
            ednFirewallArpDataDict['modification_date'] = FormatDate(ednFirewallArpObj['MODIFICATION_DATE'])
            ednFirewallArpObjList.append(ednFirewallArpDataDict)


        content = gzip.compress(json.dumps(ednFirewallArpObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/exportEdnFirewallArp", methods = ['GET'])
@token_required
def ExportEdnFirewallArp(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednFirewallArpObjList=[]
        
        #ednFirewallArpObjs = EDN_FIREWALL_ARP.query.all()
        ednFirewallArpObjs = phy_engine.execute('SELECT * FROM edn_firewall_arp WHERE creation_date = (SELECT max(creation_date) FROM edn_firewall_arp)')
        
        for ednFirewallArpObj in ednFirewallArpObjs:
            ednFirewallArpDataDict= {}
            ednFirewallArpDataDict['edn_firewall_arp_id']=ednFirewallArpObj['EDN_FIREWALL_ARP_ID']
            ednFirewallArpDataDict['firewall_id'] = ednFirewallArpObj['FIREWALL_ID']
            ednFirewallArpDataDict['mac'] = ednFirewallArpObj['MAC']
            ednFirewallArpDataDict['ip'] = ednFirewallArpObj['IP']
            ednFirewallArpDataDict['creation_date'] = FormatDate(ednFirewallArpObj['CREATION_DATE'])
            ednFirewallArpDataDict['modification_date'] = FormatDate(ednFirewallArpObj['MODIFICATION_DATE'])
            
            ednFirewallArpObjList.append(ednFirewallArpDataDict)

        return jsonify(ednFirewallArpObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editEdnCdpLegacy",methods = ['POST'])
@token_required
def EditEdnCdpLegacy(user_data):
    #if request.headers.get('X-Auth-Key') ==session.get('token', None):
    if True:#session.get('token', None):
        ednCdpLegacyObj = request.get_json()
        print(ednCdpLegacyObj,file = sys.stderr)
        ednCdpLegacy = EDN_CDP_LEGACY.query.with_entities(EDN_CDP_LEGACY).filter_by(edn_cdp_legacy_id=ednCdpLegacyObj["edn_cdp_legacy_id"]).first()
        '''
        if ednCdpLegacyObj['device_a_name']:
            ednCdpLegacy.device_a_name = ednCdpLegacyObj['device_a_name']          
        if ednCdpLegacyObj['device_a_interface']:
            ednCdpLegacy.device_a_interface = ednCdpLegacyObj['device_a_interface']
        if ednCdpLegacyObj['device_a_trunk_name']:
            ednCdpLegacy.device_a_trunk_name = ednCdpLegacyObj['device_a_trunk_name']
        
        if ednCdpLegacyObj['device_a_ip']:
            ednCdpLegacy.device_a_ip = ednCdpLegacyObj['device_a_ip']
        '''
        if ednCdpLegacyObj['device_b_system_name']:
            ednCdpLegacy.device_b_system_name = ednCdpLegacyObj['device_b_system_name']
        
        if ednCdpLegacyObj['device_b_interface']:
            ednCdpLegacy.device_b_interface = ednCdpLegacyObj['device_b_interface']
        #if ednCdpLegacyObj['device_b_ip']:
        #    ednCdpLegacy.device_b_ip = ednCdpLegacyObj['device_b_ip']
        if ednCdpLegacyObj['device_b_type']:
            ednCdpLegacy.device_b_type = ednCdpLegacyObj['device_b_type']
        if ednCdpLegacyObj['device_b_port_desc']:
            ednCdpLegacy.device_b_port_desc = ednCdpLegacyObj['device_b_port_desc']
        '''
        if ednCdpLegacyObj['device_a_mac']:
            ednCdpLegacy.device_a_mac = ednCdpLegacyObj['device_a_mac']
        if ednCdpLegacyObj['device_b_mac']:
            ednCdpLegacy.device_b_mac = ednCdpLegacyObj['device_b_mac']
        if ednCdpLegacyObj['device_a_port_desc']:
            ednCdpLegacy.device_a_port_desc = ednCdpLegacyObj['device_a_port_desc']
        if ednCdpLegacyObj['device_a_vlan']:
            ednCdpLegacy.device_a_vlan = ednCdpLegacyObj['device_a_vlan']
        '''
        if ednCdpLegacyObj['server_name']:
            ednCdpLegacy.server_name = ednCdpLegacyObj['server_name']
        if ednCdpLegacyObj['server_os']:
            ednCdpLegacy.server_os = ednCdpLegacyObj['server_os']
        if ednCdpLegacyObj['app_name']:
            ednCdpLegacy.app_name = ednCdpLegacyObj['app_name']
        if ednCdpLegacyObj['owner_name']:
            ednCdpLegacy.owner_name = ednCdpLegacyObj['owner_name']
        if ednCdpLegacyObj['owner_email']:
            ednCdpLegacy.owner_email = ednCdpLegacyObj['owner_email']
        if ednCdpLegacyObj['owner_contact']:
            ednCdpLegacy.owner_contact = ednCdpLegacyObj['owner_contact']
        
        UpdateData(ednCdpLegacy)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/fetchEdnCdpLegacy", methods = ['GET'])
@token_required
def FetchEdnCdpLegacy(user_data):  
    if True:
        try:
            FetchEdnCdpLegacyFunc(user_data)
            return jsonify("Success"), 200
            
        except Exception as e:
            return jsonify("Failure"), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchEdnCdpLegacyFunc(user_data):
    ednCDPLegacyList = []
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query_string = "select ne_ip_address, device_id, sw_type from seed_table where cisco_domain = 'EDN-NET' and (sw_type = 'IOS-XE' or sw_type = 'NX-OS' or sw_type = 'IOS' or sw_type = 'IOS-XR') and operation_status='Production';" 
    result = db.session.execute(query_string)
    for row in result:
        #print(row[0], row[1], row[2], file=sys.stderr)
        ednCDPLegacyDict = {}
        ednCDPLegacyDict['ip'] = row[0]
        ednCDPLegacyDict['hostname'] = row[1]
        ednCDPLegacyDict['sw_type'] = row[2]
        ednCDPLegacyDict['time'] = current_time
        ednCDPLegacyDict['type'] = 'EDN'

        ednCDPLegacyList.append(ednCDPLegacyDict)

    print(ednCDPLegacyList, file=sys.stderr)

    cdpLegacy= CDPLegacy()
    
    
    #Update Script Status
    cdpLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-CDP-Legacy").first()
    try:
        cdpLegacyStatus.script = "EDN-CDP-Legacy"
        cdpLegacyStatus.status = "Running"
        cdpLegacyStatus.creation_date= current_time
        cdpLegacyStatus.modification_date= current_time
        db.session.add(cdpLegacyStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    try:
        cdpLegacy.getPhysicalMapping(ednCDPLegacyList)
    except Exception as e:
        print(e, file=sys.stderr)

    #temp=[{'ip': '10.73.0.1', 'hostname': 'RYD-MLGII-ENT-COR-SW1', 'sw_type': 'NX-OS', 'time': '2022-02-11 18:05:10', 'type': 'EDN'}, {'ip': '10.27.78.108', 'hostname': 'JED-BHN-ENT-EDG-CO-SW108', 'sw_type': 'IOS', 'time': '2022-02-11 18:11:08', 'type': 'EDN'}]
    #cdpLegacy.getPhysicalMapping(temp)
    
    #Update Script Status
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cdpLegacyStatus.script = "EDN-CDP-Legacy"
        cdpLegacyStatus.status = "Completed"
        cdpLegacyStatus.creation_date= current_time
        cdpLegacyStatus.modification_date= current_time
        db.session.add(cdpLegacyStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)
    
@app.route("/fetchEdnMacLegacy", methods = ['GET'])
@token_required
def FetchEdnMacLegacy(user_data):
    if True:
        try:
            FetchEdnMacLegacyFunc(user_data)
            return jsonify("Success"), 200
            
        except Exception as e:
            print(f"Exception Occured {e}", file=sys.stderr)
            return jsonify("Failure"), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchEdnMacLegacyFunc(user_data):
    
    ednMacLegacyList = []
    switchObjs = EDN_NET_Seed.query.all()
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for switchObj in switchObjs:

        ednMacLegacyDict = {}
        ednMacLegacyDict['ip'] = switchObj.switch_ip_address
        ednMacLegacyDict['hostname'] = switchObj.switch_id
        ednMacLegacyDict['sw_type'] = switchObj.os_type
        ednMacLegacyDict['time'] = current_time

        ednMacLegacyList.append(ednMacLegacyDict)
    
    print(ednMacLegacyList, file=sys.stderr)
    

    '''
    MAC ACI
    '''

    ednLLDPACIDict = {}
    query_string = "select ne_ip_address, device_id, sw_type, site_id from seed_table where cisco_domain = 'EDN-NET' and sw_type = 'APIC' and operation_status='Production';" 
    result = db.session.execute(query_string)
    for row in result:
        #print(row[0], row[1], row[2], file=sys.stderr)
        site_apic= row[1].split('-')
        site_apic= '-'.join(site_apic[:-1])
        if site_apic in ednLLDPACIDict:
            ednLLDPACIDictEntry = {}
            ednLLDPACIDictEntry['ip'] = row[0]
            ednLLDPACIDictEntry['hostname'] = row[1]
            ednLLDPACIDictEntry['sw_type'] = row[2]
            ednLLDPACIDictEntry['time'] = current_time
            ednLLDPACIDictEntry['type'] = 'EDN-MAC'
    
            ednLLDPACIDict[site_apic].append(ednLLDPACIDictEntry)
        else:
            site_apic= row[1].split('-')
            site_apic= '-'.join(site_apic[:-1])
            ednLLDPACIDict[site_apic] = []

            ednLLDPACIDictEntry = {}
            ednLLDPACIDictEntry['ip'] = row[0]
            ednLLDPACIDictEntry['hostname'] = row[1]
            ednLLDPACIDictEntry['sw_type'] = row[2]
            ednLLDPACIDictEntry['time'] = current_time
            ednLLDPACIDictEntry['type'] = 'EDN-MAC'
            ednLLDPACIDict[site_apic].append(ednLLDPACIDictEntry)
    


    '''
    MAC ACI ENDS
    '''

    try:
       
        ednLLDP= LLDPPuller()
    except Exception as e:
        print("Error Occured", file=sys.stderr)
    
    try:    
        
        ednMacLegacy= EdnMacLegacy()
    except Exception as e:
        print("Error Occured", file=sys.stderr)

    #Update Script Status
    ednMacLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-MAC-Legacy").first()
    try:
        ednMacLegacyStatus.script = "EDN-MAC-Legacy"
        ednMacLegacyStatus.status = "Running"
        ednMacLegacyStatus.creation_date= current_time
        ednMacLegacyStatus.modification_date= current_time
        db.session.add(ednMacLegacyStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)
    
    
    try:
        print("Starting ACI Part", file=sys.stderr)
        ednLLDP.getPhysicalMapping(ednLLDPACIDict, "EDN-MAC")
    except Exception as e:
        print(e, file=sys.stderr)

    try:
        print("Starting MAC Part", file=sys.stderr)
        ednMacLegacy.getPhysicalMapping(ednMacLegacyList)
    except Exception as e:
        print(e, file=sys.stderr)


    #Update Script Status
    finish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        ednMacLegacyStatus.script = "EDN-MAC-Legacy"
        ednMacLegacyStatus.status = "Completed"
        ednMacLegacyStatus.creation_date= finish_time
        ednMacLegacyStatus.modification_date= finish_time
        db.session.add(ednMacLegacyStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    try: 
        print("Populating Firewall IP's in Edn Mac Legacy", file=sys.stderr)
        fwIp= AddFwIP()
        newTime= datetime.now(tz)
        fwIp.addFWIPToEdnMacLegacy(current_time, newTime)
    except Exception as e:
        print("Failed To Sync Firewall IP's In EDN MAC")

    try:  
        print("Populating Service Mapping to Edn Mac Legacy", file=sys.stderr)
        newTime= datetime.now(tz)
        serviceMapping= AddServiceMapping()
        serviceMapping.addEdnMacLegacyServiceMapping(current_time, newTime)

        print("EDN MAC Legacy Completed", file=sys.stderr)   
    except Exception as e:
        print("Failed To Sync EDN Services to EDN MAC")

@app.route("/editEdnLldpAci",methods = ['POST'])
@token_required
def EditEdnLldpAciDevice(user_data):
    #if request.headers.get('X-Auth-Key') ==session.get('token', None):
    if True:#session.get('token', None):
        ednEdnAciObj = request.get_json()
        print(ednEdnAciObj,file = sys.stderr)

        ednAci = EDN_LLDP_ACI.query.with_entities(EDN_LLDP_ACI).filter_by(edn_lldp_aci_id=ednEdnAciObj["edn_lldp_aci_id"]).first()
        '''
        if ednEdnAciObj['device_a_name']:
            ednAci.device_a_name = ednEdnAciObj['device_a_name']          
        if ednEdnAciObj['device_a_interface']:
            ednAci.device_a_interface = ednEdnAciObj['device_a_interface']
        if ednEdnAciObj['device_a_trunk_name']:
            ednAci.device_a_trunk_name = ednEdnAciObj['device_a_trunk_name']
        if ednEdnAciObj['device_a_ip']:
            ednAci.device_a_ip = ednEdnAciObj['device_a_ip']
        '''
        if ednEdnAciObj['device_b_system_name']:
            ednAci.device_b_system_name = ednEdnAciObj['device_b_system_name']
        if ednEdnAciObj['device_b_interface']:
            ednAci.device_b_interface = ednEdnAciObj['device_b_interface']
        #if ednEdnAciObj['device_b_ip']:
        #    ednAci.device_b_ip = ednEdnAciObj['device_b_ip']
        if ednEdnAciObj['device_b_type']:
            ednAci.device_b_type = ednEdnAciObj['device_b_type']
        if ednEdnAciObj['device_b_port_desc']:
            ednAci.device_b_port_desc = ednEdnAciObj['device_b_port_desc']
        
        #if ednEdnAciObj['device_a_mac']:
        #    ednAci.device_a_mac = ednEdnAciObj['device_a_mac']
        #if ednEdnAciObj['device_b_mac']:
        #    ednAci.device_b_mac = ednEdnAciObj['device_b_mac']
        '''
        if ednEdnAciObj['device_a_port_desc']:
            ednAci.device_a_port_desc = ednEdnAciObj['device_a_port_desc']
        if ednEdnAciObj['device_a_vlan']:
            ednAci.device_a_vlan = ednEdnAciObj['device_a_vlan']
        '''
        if ednEdnAciObj['server_name']:
            ednAci.server_name = ednEdnAciObj['server_name']
        if ednEdnAciObj['server_os']:
            ednAci.server_os = ednEdnAciObj['server_os']
        if ednEdnAciObj['app_name']:
            ednAci.app_name = ednEdnAciObj['app_name']
        if ednEdnAciObj['owner_name']:
            ednAci.owner_name = ednEdnAciObj['owner_name']
        if ednEdnAciObj['owner_email']:
            ednAci.owner_email = ednEdnAciObj['owner_email']
        if ednEdnAciObj['owner_contact']:
            ednAci.owner_contact = ednEdnAciObj['owner_contact']
        UpdateData(ednAci)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/fetchEdnLldpAci", methods = ['GET'])
@token_required
def FetchEdnLLDPACI(user_data):
    if True:
        try:
            FetchEdnLLDPACIFunc(user_data)
            return jsonify("Success"), 200
            
        except Exception as e:
            return jsonify("Failure"), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchEdnLLDPACIFunc(user_data):
    ednLLDPACIDict = {}

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query_string = "select ne_ip_address, device_id, sw_type, site_id from seed_table where cisco_domain = 'EDN-NET' and sw_type = 'APIC' and operation_status='Production';" 
    result = db.session.execute(query_string)
    for row in result:
        #print(row[0], row[1], row[2], file=sys.stderr)
        site_apic= row[1].split('-')
        site_apic= '-'.join(site_apic[:-1])
        if site_apic in ednLLDPACIDict:
            ednLLDPACIDictEntry = {}
            ednLLDPACIDictEntry['ip'] = row[0]
            ednLLDPACIDictEntry['hostname'] = row[1]
            ednLLDPACIDictEntry['sw_type'] = row[2]
            ednLLDPACIDictEntry['time'] = current_time
            ednLLDPACIDictEntry['type'] = 'EDN'
    
            ednLLDPACIDict[site_apic].append(ednLLDPACIDictEntry)
        else:
            site_apic= row[1].split('-')
            site_apic= '-'.join(site_apic[:-1])
            ednLLDPACIDict[site_apic] = []

            ednLLDPACIDictEntry = {}
            ednLLDPACIDictEntry['ip'] = row[0]
            ednLLDPACIDictEntry['hostname'] = row[1]
            ednLLDPACIDictEntry['sw_type'] = row[2]
            ednLLDPACIDictEntry['time'] = current_time
            ednLLDPACIDictEntry['type'] = 'EDN'
        

            ednLLDPACIDict[site_apic].append(ednLLDPACIDictEntry)
    
    print(ednLLDPACIDict, file=sys.stderr)


    
    ednLLDP= LLDPPuller()
    
    #Update Script Status
    ednLLDPStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-LLDP").first()
    try:
        ednLLDPStatus.script = "EDN-LLDP"
        ednLLDPStatus.status = "Running"
        ednLLDPStatus.creation_date= current_time
        ednLLDPStatus.modification_date= current_time
        db.session.add(ednLLDPStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    try:
        ednLLDP.getPhysicalMapping(ednLLDPACIDict, "EDN")
    except Exception as e:
        print(e, file=sys.stderr)
    #Update Script Status
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        ednLLDPStatus.script = "EDN-LLDP"
        ednLLDPStatus.status = "Completed"
        ednLLDPStatus.creation_date= current_time
        ednLLDPStatus.modification_date= current_time
        db.session.add(ednLLDPStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

@app.route("/editIgwLldpAci",methods = ['POST'])
@token_required
def EditIgwLldpAci(user_data):
    #if request.headers.get('X-Auth-Key') ==session.get('token', None):
    if True:#session.get('token', None):
        igwAciObj = request.get_json()
        print(igwAciObj,file = sys.stderr)
        igwAci = IGW_LLDP_ACI.query.with_entities(IGW_LLDP_ACI).filter_by(igw_lldp_aci_id=igwAciObj["igw_lldp_aci_id"]).first()
        '''
        if igwAciObj['device_a_name']:
            igwAci.device_a_name = igwAciObj['device_a_name']          
        if igwAciObj['device_a_interface']:
            igwAci.device_a_interface = igwAciObj['device_a_interface']
        if igwAciObj['device_a_trunk_name']:
            igwAci.device_a_trunk_name = igwAciObj['device_a_trunk_name']
        if igwAciObj['device_a_ip']:
            igwAci.device_a_ip = igwAciObj['device_a_ip']
        '''
        if igwAciObj['device_b_system_name']:
            igwAci.device_b_system_name = igwAciObj['device_b_system_name']
        if igwAciObj['device_b_interface']:
            igwAci.device_b_interface = igwAciObj['device_b_interface']
        #if igwAciObj['device_b_ip']:
        #    igwAci.device_b_ip = igwAciObj['device_b_ip']
        if igwAciObj['device_b_type']:
            igwAci.device_b_type = igwAciObj['device_b_type']
        if igwAciObj['device_b_port_desc']:
            igwAci.device_b_port_desc = igwAciObj['device_b_port_desc']
        #if igwAciObj['device_a_mac']:
        #    igwAci.device_a_mac = igwAciObj['device_a_mac']
        #if igwAciObj['device_b_mac']:
        #    igwAci.device_b_mac = igwAciObj['device_b_mac']
        '''
        if igwAciObj['device_a_port_desc']:
            igwAci.device_a_port_desc = igwAciObj['device_a_port_desc']
        if igwAciObj['device_a_vlan']:
            igwAci.device_a_vlan = igwAciObj['device_a_vlan']
        '''
        if igwAciObj['server_name']:
            igwAci.server_name = igwAciObj['server_name']
        if igwAciObj['server_os']:
            igwAci.server_os = igwAciObj['server_os']
        if igwAciObj['app_name']:
            igwAci.app_name = igwAciObj['app_name']
        if igwAciObj['owner_name']:
            igwAci.owner_name = igwAciObj['owner_name']
        if igwAciObj['owner_email']:
            igwAci.owner_email = igwAciObj['owner_email']
        if igwAciObj['owner_contact']:
            igwAci.owner_contact = igwAciObj['owner_contact']
        UpdateData(igwAci)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
@app.route("/editIgwLldpLegacy",methods = ['POST'])
@token_required
def EditIgwLldpLegacy(user_data):
    #if request.headers.get('X-Auth-Key') ==session.get('token', None):
    if True:#session.get('token', None):
        igwLegacyObj = request.get_json()
        print(igwLegacyObj,file = sys.stderr)
        igwLegacy = IGW_LLDP_LEGACY.query.with_entities(IGW_LLDP_LEGACY).filter_by(igw_lldp_legacy_id=igwLegacyObj["igw_lldp_legacy_id"]).first()
        '''
        if igwLegacyObj['device_a_name']:
            igwLegacy.device_a_name = igwLegacyObj['device_a_name']          
        if igwLegacyObj['device_a_interface']:
            igwLegacy.device_a_interface = igwLegacyObj['device_a_interface']
        if igwLegacyObj['device_a_trunk_name']:
            igwLegacy.device_a_trunk_name = igwLegacyObj['device_a_trunk_name']
        if igwLegacyObj['device_a_ip']:
            igwLegacy.device_a_ip = igwLegacyObj['device_a_ip']
        '''
        if igwLegacyObj['device_b_system_name']:
            igwLegacy.device_b_system_name = igwLegacyObj['device_b_system_name']
        if igwLegacyObj['device_b_interface']:
            igwLegacy.device_b_interface = igwLegacyObj['device_b_interface']
        #if igwLegacyObj['device_b_ip']:
        #    igwLegacy.device_b_ip = igwLegacyObj['device_b_ip']
        if igwLegacyObj['device_b_type']:
            igwLegacy.device_b_type = igwLegacyObj['device_b_type']
        if igwLegacyObj['device_b_port_desc']:
            igwLegacy.device_b_port_desc = igwLegacyObj['device_b_port_desc']
        #if igwLegacyObj['device_a_mac']:
        #    igwLegacy.device_a_mac = igwLegacyObj['device_a_mac']
        #if igwLegacyObj['device_b_mac']:
        #    igwLegacy.device_b_mac = igwLegacyObj['device_b_mac']
        '''
        if igwLegacyObj['device_a_port_desc']:
            igwLegacy.device_a_port_desc = igwLegacyObj['device_a_port_desc']
        if igwLegacyObj['device_a_vlan']:
            igwLegacy.device_a_vlan = igwLegacyObj['device_a_vlan']
        '''
        if igwLegacyObj['server_name']:
            igwLegacy.server_name = igwLegacyObj['server_name']
        if igwLegacyObj['server_os']:
            igwLegacy.server_os = igwLegacyObj['server_os']
        if igwLegacyObj['app_name']:
            igwLegacy.app_name = igwLegacyObj['app_name']
        if igwLegacyObj['owner_name']:
            igwLegacy.owner_name = igwLegacyObj['owner_name']
        if igwLegacyObj['owner_email']:
            igwLegacy.owner_email = igwLegacyObj['owner_email']
        if igwLegacyObj['owner_contact']:
            igwLegacy.owner_contact = igwLegacyObj['owner_contact']
        UpdateData(igwLegacy)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route("/fetchIgwLldpACI", methods = ['GET'])
@token_required
def FetchIGWLLDPACI(user_data):
    if True:
        try:
            FetchIGWLLDPACIFunc(user_data)
            return jsonify("Success"), 200

        except Exception as e:
            return jsonify("Failure"), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
def FetchIGWLLDPACIFunc(user_data):
   

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    igwLLDPACIDict = {}
    query_string = "select ne_ip_address, device_id, sw_type, site_id from seed_table where cisco_domain = 'IGW-NET' and sw_type = 'APIC' and operation_status='Production';" 
    result = db.session.execute(query_string)
    for row in result:
        #print(row[0], row[1], row[2], file=sys.stderr)
        site_apic= row[1].split('-')
        site_apic= '-'.join(site_apic[:-1])
        if site_apic in igwLLDPACIDict:
            igwLLDPACIDictEntry = {}
            igwLLDPACIDictEntry['ip'] = row[0]
            igwLLDPACIDictEntry['hostname'] = row[1]
            igwLLDPACIDictEntry['sw_type'] = row[2]
            igwLLDPACIDictEntry['time'] = current_time
            igwLLDPACIDictEntry['type'] = 'IGW'
    
            igwLLDPACIDict[site_apic].append(igwLLDPACIDictEntry)
        else:
            site_apic= row[1].split('-')
            site_apic= '-'.join(site_apic[:-1])
            igwLLDPACIDict[site_apic] = []

            igwLLDPACIDictEntry = {}
            igwLLDPACIDictEntry['ip'] = row[0]
            igwLLDPACIDictEntry['hostname'] = row[1]
            igwLLDPACIDictEntry['sw_type'] = row[2]
            igwLLDPACIDictEntry['time'] = current_time
            igwLLDPACIDictEntry['type'] = 'IGW'
        

            igwLLDPACIDict[site_apic].append(igwLLDPACIDictEntry)

    print(igwLLDPACIDict, file=sys.stderr)

    igwLLDP= LLDPPuller()

    #Update Script Status
    igwLLDPStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "IGW-LLDP").first()
    try:
        igwLLDPStatus.script = "IGW-LLDP"
        igwLLDPStatus.status = "Running"
        igwLLDPStatus.creation_date= current_time
        igwLLDPStatus.modification_date= current_time
        db.session.add(igwLLDPStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    try:
        igwLLDP.getPhysicalMapping(igwLLDPACIDict, "IGW")
    except Exception as e:
        print(e, file=sys.stderr)


    #Update Script Status
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        igwLLDPStatus.script = "IGW-LLDP"
        igwLLDPStatus.status = "Completed"
        igwLLDPStatus.creation_date= current_time
        igwLLDPStatus.modification_date= current_time
        db.session.add(igwLLDPStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

@app.route("/editIgwCdpLegacy",methods = ['POST'])
@token_required
def EditIgwCdpLegacy(user_data):
    #if request.headers.get('X-Auth-Key') ==session.get('token', None):
    if True:#session.get('token', None):
        igwCdpObj = request.get_json()
        print(igwCdpObj,file = sys.stderr)

        igwCdp = IGW_CDP_LEGACY.query.with_entities(IGW_CDP_LEGACY).filter_by(igw_cdp_legacy_id=igwCdpObj["igw_cdp_legacy_id"]).first()
        '''
        if igwCdpObj['device_a_name']:
            igwCdp.device_a_name = igwCdpObj['device_a_name']          
        if igwCdpObj['device_a_interface']:
            igwCdp.device_a_interface = igwCdpObj['device_a_interface']
        if igwCdpObj['device_a_trunk_name']:
            igwCdp.device_a_trunk_name = igwCdpObj['device_a_trunk_name']
        if igwCdpObj['device_a_ip']:
            igwCdp.device_a_ip = igwCdpObj['device_a_ip']
        '''
        if igwCdpObj['device_b_system_name']:
            igwCdp.device_b_system_name = igwCdpObj['device_b_system_name']
        if igwCdpObj['device_b_interface']:
            igwCdp.device_b_interface = igwCdpObj['device_b_interface']
        #if igwCdpObj['device_b_ip']:
        #    igwCdp.device_b_ip = igwCdpObj['device_b_ip']
        if igwCdpObj['device_b_type']:
            igwCdp.device_b_type = igwCdpObj['device_b_type']
        if igwCdpObj['device_b_port_desc']:
            igwCdp.device_b_port_desc = igwCdpObj['device_b_port_desc']
        #if igwCdpObj['device_a_mac']:
        #    igwCdp.device_a_mac = igwCdpObj['device_a_mac']
        #if igwCdpObj['device_b_mac']:
        #    igwCdp.device_b_mac = igwCdpObj['device_b_mac']
        '''
        if igwCdpObj['device_a_port_desc']:
            igwCdp.device_a_port_desc = igwCdpObj['device_a_port_desc']
        if igwCdpObj['device_a_vlan']:
            igwCdp.device_a_vlan = igwCdpObj['device_a_vlan']
        '''
        if igwCdpObj['server_name']:
            igwCdp.server_name = igwCdpObj['server_name']
        if igwCdpObj['server_os']:
            igwCdp.server_os = igwCdpObj['server_os']
        if igwCdpObj['app_name']:
            igwCdp.app_name = igwCdpObj['app_name']
        if igwCdpObj['owner_name']:
            igwCdp.owner_name = igwCdpObj['owner_name']
        if igwCdpObj['owner_email']:
            igwCdp.owner_email = igwCdpObj['owner_email']
        if igwCdpObj['owner_contact']:
            igwCdp.owner_contact = igwCdpObj['owner_contact']
        UpdateData(igwCdp)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/fetchIgwCdpLegacy", methods = ['GET'])
@token_required
def FetchIGWCdpLegacy(user_data):
    
    if True:
        try:
            FetchIGWCdpLegacyFunc(user_data)
            return jsonify("Success"), 200
            
        except Exception as e:
            return jsonify("Failure"), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchIGWCdpLegacyFunc(user_data):    
    igwCDPLegacyList = []

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query_string = "select ne_ip_address, device_id, sw_type from seed_table where cisco_domain = 'IGW-NET' and (sw_type = 'IOS-XE' or sw_type = 'NX-OS' or sw_type = 'IOS' or sw_type = 'IOS-XR') and operation_status='Production';" 
    result = db.session.execute(query_string)
    for row in result:
        #print(row[0], row[1], row[2], file=sys.stderr)
        igwCDPLegacyDict = {}
        igwCDPLegacyDict['ip'] = row[0]
        igwCDPLegacyDict['hostname'] = row[1]
        igwCDPLegacyDict['sw_type'] = row[2]
        igwCDPLegacyDict['time'] = current_time
        igwCDPLegacyDict['type'] = 'IGW'

        igwCDPLegacyList.append(igwCDPLegacyDict)

    print(igwCDPLegacyList, file=sys.stderr)
    cdpLegacy= CDPLegacy()

    #Update Script Status
    igwCdpStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "IGW-CDP-Legacy").first()
    try:
        
        igwCdpStatus.script = "IGW-CDP-Legacy"
        igwCdpStatus.status = "Running"
        igwCdpStatus.creation_date= current_time
        igwCdpStatus.modification_date= current_time
        db.session.add(igwCdpStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    
    try:
        cdpLegacy.getPhysicalMapping(igwCDPLegacyList)
    except Exception as e:
        print(e, file=sys.stderr)

    #Update Script Status
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        
        igwCdpStatus.script = "IGW-CDP-Legacy"
        igwCdpStatus.status = "Completed"
        igwCdpStatus.creation_date= current_time
        igwCdpStatus.modification_date= current_time
        db.session.add(igwCdpStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

@app.route("/fetchEdnArp", methods = ['GET'])
@token_required
def FetchEdnArp(user_data):
    if True:
        try:
            FetchEdnArpFunc(user_data)
            return jsonify("Success"), 200
            
        except Exception as e:
            return jsonify("Failure"), 500
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchEdnArpFunc(user_data):
    ednArpList = []
    fwObjs = EDN_SEC_Seed.query.all()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for fwObj in fwObjs:

        ednArpDict = {}
        ednArpDict['ip'] = fwObj.fw_ip_address
        ednArpDict['hostname'] = fwObj.fw_id
        ednArpDict['sw_type'] = fwObj.os_type
        ednArpDict['time'] = current_time

        ednArpList.append(ednArpDict)
    
    print(ednArpList, file=sys.stderr)
    #temp=[{'ip': '10.64.252.4', 'hostname': 'RYD-MLG-ENT-GSM-VS1', 'sw_type': 'FOS', 'time': current_time}, {'ip': '10.6.0.133', 'hostname': 'RYD-MLG-ENT-DND-VS1', 'sw_type': 'NX-OS', 'time':current_time}]
    ednArp= Arp()

    #Update Script Status
    ednArpStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-Firewall-ARP").first()
    try:
        
        ednArpStatus.script = "EDN-Firewall-ARP"
        ednArpStatus.status = "Running"
        ednArpStatus.creation_date= current_time
        ednArpStatus.modification_date= current_time
        db.session.add(ednArpStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    try:
        ednArp.getPhysicalMapping(ednArpList)
    except Exception as e:
        print(e, file=sys.stderr)

    #Update Script Status
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        ednArpStatus.script = "EDN-Firewall-ARP"
        ednArpStatus.status = "Completed"
        ednArpStatus.creation_date= current_time
        ednArpStatus.modification_date= current_time
        db.session.add(ednArpStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

@app.route("/getEdnCdpLegacyFetchStatus", methods = ['GET'])
@token_required
def GetAllEdnCdpLegacyFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        
        ednCdpLegacyData={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        ednCdpLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-CDP-Legacy").first()
        if ednCdpLegacyStatus:
            script_status= ednCdpLegacyStatus.status
            script_modifiation_date= str(ednCdpLegacyStatus.modification_date)
        ednCdpLegacyData["fetch_status"] = script_status
        ednCdpLegacyData["fetch_date"]= script_modifiation_date
        content = gzip.compress(json.dumps(ednCdpLegacyData).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addEdnIptDevice",methods = ['POST'])
@token_required
def AddEdnIptDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednIptObj = request.get_json()

        print(ednIptObj,file=sys.stderr)
        ednIpt = EDN_IPT()
        ednIpt.device_a_ip = ednIptObj['device_a_ip']
        if ednIptObj['device_a_name']:
            ednIpt.device_a_name = ednIptObj['device_a_name']
        if ednIptObj['device_a_interface']:
            ednIpt.device_a_interface = ednIptObj['device_a_interface']    
        if ednIptObj['device_a_trunk_name']:
            ednIpt.device_a_trunk_name = ednIptObj['device_a_trunk_name']
        if ednIptObj['device_a_ip']:
            ednIpt.device_a_ip = ednIptObj['device_a_ip']
        if ednIptObj['device_b_system_name']:
            ednIpt.device_b_system_name= ednIptObj['device_b_system_name']
        if ednIptObj['device_b_interface']:
            ednIpt.device_b_interface = ednIptObj['device_b_interface']
        if ednIptObj['device_b_ip']:
            ednIpt.device_b_ip= ednIptObj['device_b_ip']
        if ednIptObj['device_b_type']:
            ednIpt.device_b_type= ednIptObj['device_b_type']
        if ednIptObj['device_b_port_desc']:
            portDesc = ednIptObj['device_b_port_desc']
            portDesc.replace('<',"")
            portDesc.replace('>',"")
            portDesc.replace('|'," , ")
            ednIpt.device_b_port_desc= portDesc
            #ednIpt.device_b_port_desc= ednIptObj['device_b_port_desc']
        if ednIptObj['device_a_mac']:
            ednIpt.device_a_mac= ednIptObj['device_a_mac']
        if ednIptObj['device_b_mac']:
            ednIpt.device_b_mac= ednIptObj['device_b_mac']
        if ednIptObj['device_a_port_desc']:
            portDesc = ednIptObj['device_a_port_desc']
            portDesc.replace('<',"")
            portDesc.replace('>',"")
            portDesc.replace('|'," , ")
            ednIpt.device_a_port_desc= portDesc
            #ednIpt.device_a_port_desc= ednIptObj['device_a_port_desc']
        if ednIptObj['device_a_vlan']:
            ednIpt.device_a_vlan= ednIptObj['device_a_vlan']
        if 'service_vendor' in ednIptObj:
                ednIpt.service_vendor = ednIptObj['service_vendor']
        else:
            ednIpt.service_vendor = 'N/A'
        #print(device.sw_eol_date,file=sys.stderr)
        
        if EDN_IPT.query.with_entities(EDN_IPT.edn_ipt_id).filter_by(edn_ipt_id=ednIptObj['edn_ipt_id']).first() is not None:
            ednIpt.edn_ipt_id = EDN_IPT.query.with_entities(EDN_IPT.edn_ipt_id).filter_by(edn_ipt_id=ednIptObj['edn_ipt_id']).first()[0]
            print(f"Updated {ednIptObj['edn_ipt_id']}",file=sys.stderr)
            ednIpt.modification_date= datetime.now(tz)
            UpdateData(ednIpt)
            
        else:
            print("Inserted Record",file=sys.stderr)
            ednIpt.creation_date= datetime.now(tz)
            ednIpt.modification_date= datetime.now(tz)
            InsertData(ednIpt)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
@app.route("/getAllEdnIptDates",methods=['GET'])
@token_required
def GetAllEdnIptDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct CREATION_DATE from edn_ipt ORDER by CREATION_DATE desc;"
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllEdnIptByDate", methods = ['POST'])
@token_required
def GetAllEdnIptByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednIptObjList=[]
        #ednIptObjs = EDN_IPT.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        ednIptObjs = phy_engine.execute(f"SELECT * FROM edn_ipt WHERE creation_date = '{current_time}'")

        for ednIptObj in ednIptObjs:

            ednIptDataDict= {}
            ednIptDataDict['edn_ipt_id']=ednIptObj['EDN_IPT_ID']
            ednIptDataDict['device_a_name'] = ednIptObj['DEVICE_A_NAME']
            ednIptDataDict['device_a_interface'] = ednIptObj['DEVICE_A_INTERFACE']
            ednIptDataDict['device_a_trunk_name'] = ednIptObj['DEVICE_A_TRUNK_NAME']
            ednIptDataDict['device_a_ip'] = ednIptObj['DEVICE_A_IP']
            ednIptDataDict['device_b_system_name'] = ednIptObj['DEVICE_B_SYSTEM_NAME']
            ednIptDataDict['device_b_interface'] = ednIptObj['DEVICE_B_INTERFACE']
            ednIptDataDict['device_b_ip'] = ednIptObj['DEVICE_B_IP']
            ednIptDataDict['device_b_type'] = ednIptObj['DEVICE_B_TYPE']
            ednIptDataDict['device_b_port_desc'] = ednIptObj['DEVICE_B_PORT_DESC']
            ednIptDataDict['device_a_mac'] = ednIptObj['DEVICE_A_MAC']
            ednIptDataDict['device_b_mac'] = ednIptObj['DEVICE_B_MAC']
            ednIptDataDict['device_a_port_desc'] = ednIptObj['DEVICE_A_PORT_DESC']
            ednIptDataDict['device_a_vlan'] = ednIptObj['DEVICE_A_VLAN']
            ednIptDataDict['service_vendor'] = ednIptObj['SERVICE_VENDOR']
            ednIptDataDict['creation_date'] = FormatDate(ednIptObj['CREATION_DATE'])
            ednIptDataDict['modification_date'] = FormatDate(ednIptObj['MODIFICATION_DATE'])
            ednIptObjList.append(ednIptDataDict)
       
        content = gzip.compress(json.dumps(ednIptObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteEdnIptDevice",methods = ['POST'])
@token_required
def DeleteEdnIptDevice(user_data):
    if True:#session.get('token', None):
        ednIptObj = request.get_json()
        #ednIptObj= ednIptObj.get("ips")
        #ednIptObj = [9,10,11,12,13]
        print(ednIptObj,file = sys.stderr)
        
        for obj in ednIptObj.get("ips"):
            ednIptId = EDN_IPT.query.filter(EDN_IPT.edn_ipt_id==obj).first()
            print(ednIptId,file=sys.stderr)
            if obj:
                db.session.delete(ednIptId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
        
@app.route("/addEdnIptDevices", methods = ['POST'])
@token_required
def AddEdnIptDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()

        print(postData,file=sys.stderr)
        
        time= datetime.now(tz)
        for ednIptObj in postData:
            ednIpt = EDN_IPT()
            if 'device_a_name' in ednIptObj:
                ednIpt.device_a_name = ednIptObj['device_a_name']
            else:
                ednIpt.device_a_name = 'N/A'
            if 'device_a_interface' in ednIptObj:
                ednIpt.device_a_interface = ednIptObj['device_a_interface']
            else:
                ednIpt.device_a_interface = 'N/A'
            if 'device_a_trunk_name' in ednIptObj:
                ednIpt.device_a_trunk_name = ednIptObj['device_a_trunk_name']
            else:
                ednIpt.device_a_trunk_name = 'N/A'
            if 'device_a_ip' in ednIptObj:
                ednIpt.device_a_ip = ednIptObj['device_a_ip']
            else:
                ednIpt.device_a_ip = 'N/A'
            if 'device_b_system_name' in ednIptObj:
                ednIpt.device_b_system_name = ednIptObj['device_b_system_name']
            else:
                ednIpt.device_b_system_name = 'N/A'
            if 'device_b_interface' in ednIptObj:
                ednIpt.device_b_interface = ednIptObj['device_b_interface']
            else:
                ednIpt.device_b_interface = 'N/A'
            if 'device_b_ip' in ednIptObj:
                ednIpt.device_b_ip = ednIptObj['device_b_ip']
            else:
                ednIpt.device_b_ip = 'N/A'
            if 'device_b_type' in ednIptObj:
                ednIpt.device_b_type = ednIptObj['device_b_type']
            else:
                ednIpt.device_b_type = 'N/A'
            if 'device_b_port_desc' in ednIptObj:
                portDesc = ednIptObj['device_b_port_desc']
                portDesc.replace('<',"")
                portDesc.replace('>',"")
                portDesc.replace('|'," , ")
                ednIpt.device_b_port_desc = portDesc
            else:
                ednIpt.device_b_port_desc = 'N/A'
            if 'device_a_mac' in ednIptObj:
                ednIpt.device_a_mac = ednIptObj['device_a_mac']
            else:
                ednIpt.device_a_mac = 'N/A'
            if 'device_b_mac' in ednIptObj:
                ednIpt.device_b_mac = ednIptObj['device_b_mac']
            else:
                ednIpt.device_b_mac = 'N/A'
            if 'device_a_port_desc' in ednIptObj:
                portDesc = ednIptObj['device_a_port_desc']
                portDesc.replace('<',"")
                portDesc.replace('>',"")
                portDesc.replace('|'," , ")
                ednIpt.device_a_port_desc = portDesc
            else:
                ednIpt.device_a_port_desc = 'N/A'
            if 'device_a_vlan' in ednIptObj:
                ednIpt.device_a_vlan = ednIptObj['device_a_vlan']
            else:
                ednIpt.device_a_vlan = 'N/A'
            if 'service_vendor' in ednIptObj:
                ednIpt.service_vendor = ednIptObj['service_vendor']
            else:
                ednIpt.service_vendor = 'N/A'

            ednIpt.creation_date= time
            ednIpt.modification_date = time
            # if Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first() is not None:
            #     seed.seed_id = Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first()[0]
            #     print("Updated " + seedObj['ne_ip_address'],file=sys.stderr)
            #     UpdateData(seed)
            # else:
            #     print("Inserted " +seedObj['ne_ip_address'],file=sys.stderr)
            #     seed.onboard_status = 'false'
            InsertData(ednIpt)
       
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnIpt", methods = ['GET'])
@token_required
def GetAllEdnIpt(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednIptObjList=[]
        
        ednIptObjs = phy_engine.execute(f"SELECT * FROM edn_ipt WHERE creation_date = (SELECT max(creation_date) FROM edn_ipt)")

        for ednIptObj in ednIptObjs:

            ednIptDataDict= {}
            ednIptDataDict['edn_ipt_id']=ednIptObj['EDN_IPT_ID']
            ednIptDataDict['device_a_name'] = ednIptObj['DEVICE_A_NAME']
            ednIptDataDict['device_a_interface'] = ednIptObj['DEVICE_A_INTERFACE']
            ednIptDataDict['device_a_trunk_name'] = ednIptObj['DEVICE_A_TRUNK_NAME']
            ednIptDataDict['device_a_ip'] = ednIptObj['DEVICE_A_IP']
            ednIptDataDict['device_b_system_name'] = ednIptObj['DEVICE_B_SYSTEM_NAME']
            ednIptDataDict['device_b_interface'] = ednIptObj['DEVICE_B_INTERFACE']
            ednIptDataDict['device_b_ip'] = ednIptObj['DEVICE_B_IP']
            ednIptDataDict['device_b_type'] = ednIptObj['DEVICE_B_TYPE']
            ednIptDataDict['device_b_port_desc'] = ednIptObj['DEVICE_B_PORT_DESC']
            ednIptDataDict['device_a_mac'] = ednIptObj['DEVICE_A_MAC']
            ednIptDataDict['device_b_mac'] = ednIptObj['DEVICE_B_MAC']
            ednIptDataDict['device_a_port_desc'] = ednIptObj['DEVICE_A_PORT_DESC']
            ednIptDataDict['device_a_vlan'] = ednIptObj['DEVICE_A_VLAN']
            ednIptDataDict['service_vendor'] = ednIptObj['SERVICE_VENDOR']
            ednIptDataDict['creation_date'] = FormatDate(ednIptObj['CREATION_DATE'])
            ednIptDataDict['modification_date'] = FormatDate(ednIptObj['MODIFICATION_DATE'])
            ednIptObjList.append(ednIptDataDict)

        content = gzip.compress(json.dumps(ednIptObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/exportEdnIpt", methods = ['GET'])
@token_required
def ExportEdnIpt(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednIptObjList=[]
        ednIptObjs = EDN_IPT.query.all()

        for ednIptObj in ednIptObjs:

            ednIptDataDict= {}
            ednIptDataDict['edn_ipt_id']=ednIptObj.edn_ipt_id
            ednIptDataDict['device_a_name'] = ednIptObj.device_a_name
            ednIptDataDict['device_a_interface'] = ednIptObj.device_a_interface
            ednIptDataDict['device_a_trunk_name'] = ednIptObj.device_a_trunk_name
            ednIptDataDict['device_a_ip'] = ednIptObj.device_a_ip
            ednIptDataDict['device_b_system_name'] = ednIptObj.device_b_system_name
            ednIptDataDict['device_b_interface'] = ednIptObj.device_b_interface
            ednIptDataDict['device_b_ip'] = ednIptObj.device_b_ip
            ednIptDataDict['device_b_type'] = ednIptObj.device_b_type
            ednIptDataDict['device_b_port_desc'] = ednIptObj.device_b_port_desc
            ednIptDataDict['device_a_mac'] = ednIptObj.device_a_mac
            ednIptDataDict['device_b_mac'] = ednIptObj.device_b_mac
            ednIptDataDict['device_a_port_desc'] = ednIptObj.device_a_port_desc
            ednIptDataDict['device_a_vlan'] = ednIptObj.device_a_vlan
            ednIptDataDict['creation_date'] = FormatDate(ednIptObj.creation_date)
            ednIptDataDict['modification_date'] = FormatDate(ednIptObj.modification_date)
            
            ednIptObjList.append(ednIptDataDict)

        return jsonify(ednIptObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/addEdnExecVideoEPsDevice",methods = ['POST'])
@token_required
def AddEdnExecVideoEPsDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednExecVideoEpsObj = request.get_json()

        print(ednExecVideoEpsObj,file=sys.stderr)
        ednExecVideoEps = EDN_EXEC_VIDEO_EPS()
        ednExecVideoEps.device_a_ip = ednExecVideoEpsObj['device_a_ip']
        if ednExecVideoEpsObj['device_a_name']:
            ednExecVideoEps.device_a_name = ednExecVideoEpsObj['device_a_name']
        if ednExecVideoEpsObj['device_a_interface']:
            ednExecVideoEps.device_a_interface = ednExecVideoEpsObj['device_a_interface']    
        if ednExecVideoEpsObj['device_a_trunk_name']:
            ednExecVideoEps.device_a_trunk_name = ednExecVideoEpsObj['device_a_trunk_name']
        if ednExecVideoEpsObj['device_a_ip']:
            ednExecVideoEps.device_a_ip = ednExecVideoEpsObj['device_a_ip']
        if ednExecVideoEpsObj['device_b_system_name']:
            ednExecVideoEps.device_b_system_name= ednExecVideoEpsObj['device_b_system_name']
        if ednExecVideoEpsObj['device_b_interface']:
            ednExecVideoEps.device_b_interface = ednExecVideoEpsObj['device_b_interface']
        if ednExecVideoEpsObj['device_b_ip']:
            ednExecVideoEps.device_b_ip= ednExecVideoEpsObj['device_b_ip']
        if ednExecVideoEpsObj['device_b_type']:
            ednExecVideoEps.device_b_type= ednExecVideoEpsObj['device_b_type']
        if ednExecVideoEpsObj['device_b_port_desc']:
            portDesc = ednExecVideoEpsObj['device_b_port_desc']
            portDesc.replace('<',"")
            portDesc.replace('>',"")
            portDesc.replace('|'," , ")
            ednExecVideoEps.device_b_port_desc= portDesc
            #ednExecVideoEps.device_b_port_desc= ednExecVideoEpsObj['device_b_port_desc']
        if ednExecVideoEpsObj['device_a_mac']:
            ednExecVideoEps.device_a_mac= ednExecVideoEpsObj['device_a_mac']
        if ednExecVideoEpsObj['device_b_mac']:
            ednExecVideoEps.device_b_mac= ednExecVideoEpsObj['device_b_mac']
        if ednExecVideoEpsObj['device_a_port_desc']:
            portDesc = ednExecVideoEpsObj['device_a_port_desc']
            portDesc.replace('<',"")
            portDesc.replace('>',"")
            portDesc.replace('|'," , ")
            ednExecVideoEps.device_a_port_desc= portDesc
            #ednExecVideoEps.device_a_port_desc= ednExecVideoEpsObj['device_a_port_desc']
        if ednExecVideoEpsObj['device_a_vlan']:
            ednExecVideoEps.device_a_vlan= ednExecVideoEpsObj['device_a_vlan']
        #print(device.sw_eol_date,file=sys.stderr)
        
        if EDN_EXEC_VIDEO_EPS.query.with_entities(EDN_EXEC_VIDEO_EPS.ipt_exec_video_eps_id).filter_by(ipt_exec_video_eps_id=ednExecVideoEpsObj['ipt_exec_video_eps_id']).first() is not None:
            ednExecVideoEps.ipt_exec_video_eps_id = EDN_EXEC_VIDEO_EPS.query.with_entities(EDN_EXEC_VIDEO_EPS.ipt_exec_video_eps_id).filter_by(ipt_exec_video_eps_id=ednExecVideoEpsObj['ipt_exec_video_eps_id']).first()[0]
            print(f"Updated {ednExecVideoEpsObj['ipt_exec_video_eps_id']}",file=sys.stderr)
            ednExecVideoEps.modification_date= datetime.now(tz)
            UpdateData(ednExecVideoEps)
            
        else:
            print("Inserted Record",file=sys.stderr)
            ednExecVideoEps.creation_date= datetime.now(tz)
            InsertData(ednExecVideoEps)
          
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnExecVideoEPsDeviceDates",methods=['GET'])
@token_required
def GetAllEdnExecVideoEPsDeviceDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct CREATION_DATE from edn_exec_video_eps ORDER by CREATION_DATE desc;"
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllEdnExecVideoEPsDeviceByDate", methods = ['POST'])
@token_required
def GetAllEdnExecVideoEPsDeviceByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednExecVideoEPsObjList=[]
        #ednExecVideoEPsObjs = EDN_EXEC_VIDEO_EPS.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        ednExecVideoEPsObjs = phy_engine.execute(f"SELECT * FROM edn_exec_video_eps WHERE creation_date = '{current_time}'")

        for ednExecVideoEPsObj in ednExecVideoEPsObjs:

            ednExecVideoEPsDataDict= {}
            ednExecVideoEPsDataDict['ipt_exec_video_eps_id']=ednExecVideoEPsObj['IPT_EXEC_VIDEO_EPS_ID']
            ednExecVideoEPsDataDict['device_a_name'] = ednExecVideoEPsObj['DEVICE_A_NAME']
            ednExecVideoEPsDataDict['device_a_interface'] = ednExecVideoEPsObj['DEVICE_A_INTERFACE']
            ednExecVideoEPsDataDict['device_a_trunk_name'] = ednExecVideoEPsObj['DEVICE_A_TRUNK_NAME']
            ednExecVideoEPsDataDict['device_a_ip'] = ednExecVideoEPsObj['DEVICE_A_IP']
            ednExecVideoEPsDataDict['device_b_system_name'] = ednExecVideoEPsObj['DEVICE_B_SYSTEM_NAME']
            ednExecVideoEPsDataDict['device_b_interface'] = ednExecVideoEPsObj['DEVICE_B_INTERFACE']
            ednExecVideoEPsDataDict['device_b_ip'] = ednExecVideoEPsObj['DEVICE_B_IP']
            ednExecVideoEPsDataDict['device_b_type'] = ednExecVideoEPsObj['DEVICE_B_TYPE']
            ednExecVideoEPsDataDict['device_b_port_desc'] = ednExecVideoEPsObj['DEVICE_B_PORT_DESC']
            ednExecVideoEPsDataDict['device_a_mac'] = ednExecVideoEPsObj['DEVICE_A_MAC']
            ednExecVideoEPsDataDict['device_b_mac'] = ednExecVideoEPsObj['DEVICE_B_MAC']
            ednExecVideoEPsDataDict['device_a_port_desc'] = ednExecVideoEPsObj['DEVICE_A_PORT_DESC']
            ednExecVideoEPsDataDict['device_a_vlan'] = ednExecVideoEPsObj['DEVICE_A_VLAN']
            ednExecVideoEPsDataDict['creation_date'] = FormatDate(ednExecVideoEPsObj['CREATION_DATE'])
            ednExecVideoEPsDataDict['modification_date'] = FormatDate(ednExecVideoEPsObj['MODIFICATION_DATE'])
            ednExecVideoEPsObjList.append(ednExecVideoEPsDataDict)
       
        content = gzip.compress(json.dumps(ednExecVideoEPsObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteEdnExecVideoEPsDevice",methods = ['POST'])
@token_required
def DeleteEdnExecVideoEPsDevice(user_data):
    if True:#session.get('token', None):
        ednExecVideoEpsObj = request.get_json()
        #ednExecVideoEpsObj= ednExecVideoEpsObj.get("ips")
        #ednExecVideoEpsObj = [9,10,11,12,13]
        print(ednExecVideoEpsObj,file = sys.stderr)
        
        for obj in ednExecVideoEpsObj.get("ips"):
            ednExecVideoEpsId = EDN_EXEC_VIDEO_EPS.query.filter(EDN_EXEC_VIDEO_EPS.ipt_exec_video_eps_id==obj).first()
            print(ednExecVideoEpsId,file=sys.stderr)
            if obj:
                db.session.delete(ednExecVideoEpsId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
        
@app.route("/addEdnExecVideoEPsDevices", methods = ['POST'])
@token_required
def AddEdnExecVideoEPsDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()

        print(postData,file=sys.stderr)
        time= datetime.now(tz)
        for ednExecVideoEpsObj in postData:
            ednExecVideoEps = EDN_EXEC_VIDEO_EPS()
            if 'device_a_name' in ednExecVideoEpsObj:
                ednExecVideoEps.device_a_name = ednExecVideoEpsObj['device_a_name']
            else:
                ednExecVideoEps.device_a_name = 'N/A'
            if 'device_a_interface' in ednExecVideoEpsObj:
                ednExecVideoEps.device_a_interface = ednExecVideoEpsObj['device_a_interface']
            else:
                ednExecVideoEps.device_a_interface = 'N/A'
            if 'device_a_trunk_name' in ednExecVideoEpsObj:
                ednExecVideoEps.device_a_trunk_name = ednExecVideoEpsObj['device_a_trunk_name']
            else:
                ednExecVideoEps.device_a_trunk_name = 'N/A'
            if 'device_a_ip' in ednExecVideoEpsObj:
                ednExecVideoEps.device_a_ip = ednExecVideoEpsObj['device_a_ip']
            else:
                ednExecVideoEps.device_a_ip = 'N/A'
            if 'device_b_system_name' in ednExecVideoEpsObj:
                ednExecVideoEps.device_b_system_name = ednExecVideoEpsObj['device_b_system_name']
            else:
                ednExecVideoEps.device_b_system_name = 'N/A'
            if 'device_b_interface' in ednExecVideoEpsObj:
                ednExecVideoEps.device_b_interface = ednExecVideoEpsObj['device_b_interface']
            else:
                ednExecVideoEps.device_b_interface = 'N/A'
            if 'device_b_ip' in ednExecVideoEpsObj:
                ednExecVideoEps.device_b_ip = ednExecVideoEpsObj['device_b_ip']
            else:
                ednExecVideoEps.device_b_ip = 'N/A'
            if 'device_b_type' in ednExecVideoEpsObj:
                ednExecVideoEps.device_b_type = ednExecVideoEpsObj['device_b_type']
            else:
                ednExecVideoEps.device_b_type = 'N/A'
            if 'device_b_port_desc' in ednExecVideoEpsObj:
                portDesc = ednExecVideoEpsObj['device_b_port_desc']
                portDesc.replace('<',"")
                portDesc.replace('>',"")
                portDesc.replace('|'," , ")
                ednExecVideoEps.device_b_port_desc = portDesc
            else:
                ednExecVideoEps.device_b_port_desc = 'N/A'
            if 'device_a_mac' in ednExecVideoEpsObj:
                ednExecVideoEps.device_a_mac = ednExecVideoEpsObj['device_a_mac']
            else:
                ednExecVideoEps.device_a_mac = 'N/A'
            if 'device_b_mac' in ednExecVideoEpsObj:
                ednExecVideoEps.device_b_mac = ednExecVideoEpsObj['device_b_mac']
            else:
                ednExecVideoEps.device_b_mac = 'N/A'
            if 'device_a_port_desc' in ednExecVideoEpsObj:
                portDesc = ednExecVideoEpsObj['device_a_port_desc']
                portDesc.replace('<',"")
                portDesc.replace('>',"")
                portDesc.replace('|'," , ")
                ednExecVideoEps.device_a_port_desc = portDesc
            else:
                ednExecVideoEps.device_a_port_desc = 'N/A'
            if 'device_a_vlan' in ednExecVideoEpsObj:
                ednExecVideoEps.device_a_vlan = ednExecVideoEpsObj['device_a_vlan']
            else:
                ednExecVideoEps.device_a_vlan = 'N/A'

            ednExecVideoEps.creation_date= time
            # if Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first() is not None:
            #     seed.seed_id = Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first()[0]
            #     print("Updated " + seedObj['ne_ip_address'],file=sys.stderr)
            #     UpdateData(seed)
            # else:
            #     print("Inserted " +seedObj['ne_ip_address'],file=sys.stderr)
            #     seed.onboard_status = 'false'
            InsertData(ednExecVideoEps)
       
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnExecVideoEPs", methods = ['GET'])
@token_required
def GetAllEdnExecVideoEPs(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednExecVideoEpsObjList=[]
        
        ednExecVideoEPsObjs = phy_engine.execute(f"SELECT * FROM edn_exec_video_eps WHERE creation_date = (SELECT max(creation_date) FROM edn_exec_video_eps)")

        for ednExecVideoEPsObj in ednExecVideoEPsObjs:

            ednExecVideoEPsDataDict= {}
            ednExecVideoEPsDataDict['ipt_exec_video_eps_id']=ednExecVideoEPsObj['IPT_EXEC_VIDEO_EPS_ID']
            ednExecVideoEPsDataDict['device_a_name'] = ednExecVideoEPsObj['DEVICE_A_NAME']
            ednExecVideoEPsDataDict['device_a_interface'] = ednExecVideoEPsObj['DEVICE_A_INTERFACE']
            ednExecVideoEPsDataDict['device_a_trunk_name'] = ednExecVideoEPsObj['DEVICE_A_TRUNK_NAME']
            ednExecVideoEPsDataDict['device_a_ip'] = ednExecVideoEPsObj['DEVICE_A_IP']
            ednExecVideoEPsDataDict['device_b_system_name'] = ednExecVideoEPsObj['DEVICE_B_SYSTEM_NAME']
            ednExecVideoEPsDataDict['device_b_interface'] = ednExecVideoEPsObj['DEVICE_B_INTERFACE']
            ednExecVideoEPsDataDict['device_b_ip'] = ednExecVideoEPsObj['DEVICE_B_IP']
            ednExecVideoEPsDataDict['device_b_type'] = ednExecVideoEPsObj['DEVICE_B_TYPE']
            ednExecVideoEPsDataDict['device_b_port_desc'] = ednExecVideoEPsObj['DEVICE_B_PORT_DESC']
            ednExecVideoEPsDataDict['device_a_mac'] = ednExecVideoEPsObj['DEVICE_A_MAC']
            ednExecVideoEPsDataDict['device_b_mac'] = ednExecVideoEPsObj['DEVICE_B_MAC']
            ednExecVideoEPsDataDict['device_a_port_desc'] = ednExecVideoEPsObj['DEVICE_A_PORT_DESC']
            ednExecVideoEPsDataDict['device_a_vlan'] = ednExecVideoEPsObj['DEVICE_A_VLAN']
            ednExecVideoEPsDataDict['creation_date'] = FormatDate(ednExecVideoEPsObj['CREATION_DATE'])
            ednExecVideoEPsDataDict['modification_date'] = FormatDate(ednExecVideoEPsObj['MODIFICATION_DATE'])
            ednExecVideoEpsObjList.append(ednExecVideoEPsDataDict)
        
        content = gzip.compress(json.dumps(ednExecVideoEpsObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/exportEdnExecVideoEPs", methods = ['GET'])
@token_required
def ExportEdnExecVideoEPs(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednExecVideoEpsObjList=[]
        ednExecVideoEpsObjs = EDN_EXEC_VIDEO_EPS.query.all()

        for ednExecVideoEpsObj in ednExecVideoEpsObjs:

            ednExecVideoEpsDataDict= {}
            ednExecVideoEpsDataDict['ipt_exec_video_eps_id']=ednExecVideoEpsObj.ipt_exec_video_eps_id
            ednExecVideoEpsDataDict['device_a_name'] = ednExecVideoEpsObj.device_a_name
            ednExecVideoEpsDataDict['device_a_interface'] = ednExecVideoEpsObj.device_a_interface
            ednExecVideoEpsDataDict['device_a_trunk_name'] = ednExecVideoEpsObj.device_a_trunk_name
            ednExecVideoEpsDataDict['device_a_ip'] = ednExecVideoEpsObj.device_a_ip
            ednExecVideoEpsDataDict['device_b_system_name'] = ednExecVideoEpsObj.device_b_system_name
            ednExecVideoEpsDataDict['device_b_interface'] = ednExecVideoEpsObj.device_b_interface
            ednExecVideoEpsDataDict['device_b_ip'] = ednExecVideoEpsObj.device_b_ip
            ednExecVideoEpsDataDict['device_b_type'] = ednExecVideoEpsObj.device_b_type
            ednExecVideoEpsDataDict['device_b_port_desc'] = ednExecVideoEpsObj.device_b_port_desc
            ednExecVideoEpsDataDict['device_a_mac'] = ednExecVideoEpsObj.device_a_mac
            ednExecVideoEpsDataDict['device_b_mac'] = ednExecVideoEpsObj.device_b_mac
            ednExecVideoEpsDataDict['device_a_port_desc'] = ednExecVideoEpsObj.device_a_port_desc
            ednExecVideoEpsDataDict['device_a_vlan'] = ednExecVideoEpsObj.device_a_vlan
            ednExecVideoEpsDataDict['creation_date'] = FormatDate(ednExecVideoEpsObj.creation_date)
            ednExecVideoEpsDataDict['modification_date'] = FormatDate(ednExecVideoEpsObj.modification_date)
            
            ednExecVideoEpsObjList.append(ednExecVideoEpsDataDict)

        return jsonify(ednExecVideoEpsObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    

@app.route("/getEdnMacLegacyFetchStatus", methods = ['GET'])
@token_required
def GetAllEdnMacLegacyFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednMacLegacyData={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        ednMacLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-MAC-Legacy").first()
        if ednMacLegacyStatus:
            script_status= ednMacLegacyStatus.status
            script_modifiation_date= str(ednMacLegacyStatus.modification_date)
        ednMacLegacyData["fetch_status"] = script_status
        ednMacLegacyData["fetch_date"]= script_modifiation_date

        content = gzip.compress(json.dumps(ednMacLegacyData).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getEdnLldpAciFetchStatus", methods = ['GET'])
@token_required
def GetAllEdnLldpAciFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednLldpAciData={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        ednLldpAciStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-LLDP").first()
        if ednLldpAciStatus:
            script_status= ednLldpAciStatus.status
            script_modifiation_date= str(ednLldpAciStatus.modification_date)
        ednLldpAciData["fetch_status"] = script_status
        ednLldpAciData["fetch_date"]= script_modifiation_date
        
        content = gzip.compress(json.dumps(ednLldpAciData).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getEdnFirewallArpFetchStatus", methods = ['GET'])
@token_required
def GetAllEdnFirewallArpFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednFirewallArpData={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        ednFirewallArpStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-Firewall-Arp").first()
        if ednFirewallArpStatus:
            script_status= ednFirewallArpStatus.status
            script_modifiation_date= str(ednFirewallArpStatus.modification_date)
        ednFirewallArpData["fetch_status"] = script_status
        ednFirewallArpData["fetch_date"]= script_modifiation_date

        content = gzip.compress(json.dumps(ednFirewallArpData).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getIgwCdpLegacyFetchStatus", methods = ['GET'])
@token_required
def GetIgwCdpLegacyFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwCdpLegacyData={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        igwCdpLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "IGW-CDP-Legacy").first()
        if igwCdpLegacyStatus:
            script_status= igwCdpLegacyStatus.status
            script_modifiation_date= str(igwCdpLegacyStatus.modification_date)
        igwCdpLegacyData["fetch_status"] = script_status
        igwCdpLegacyData["fetch_date"]= script_modifiation_date
        content = gzip.compress(json.dumps(igwCdpLegacyData).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getIgwLldpAciFetchStatus", methods = ['GET'])
@token_required
def GetIgwLldpAciFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwLldpAciData={}

        #Getting status of script
        script_status=""
        script_modifiation_date=""
        igwLldACIStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "IGW-LLDP").first()
        if igwLldACIStatus:
            script_status= igwLldACIStatus.status
            script_modifiation_date= str(igwLldACIStatus.modification_date)
        igwLldpAciData["fetch_status"] = script_status
        igwLldpAciData["fetch_date"]= script_modifiation_date

        content = gzip.compress(json.dumps(igwLldpAciData).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnLldpLegacy", methods = ['GET'])
@token_required
def GetAllEdnLldpLegacy(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednLldpLegacyObjList=[]
        #ednLldpLegacyObjs = EDN_LLDP_LEGACY.query.all()
        ednLldpLegacyObjs = phy_engine.execute('SELECT * FROM edn_lldp_legacy WHERE creation_date = (SELECT max(creation_date) FROM edn_lldp_legacy)')

        for ednLldpLegacyObj in ednLldpLegacyObjs:

            ednLldpLegacyDataDict= {}
            ednLldpLegacyDataDict['edn_lldp_legacy_id']=ednLldpLegacyObj['EDN_LLDP_LEGACY_ID']
            ednLldpLegacyDataDict['device_a_name'] = ednLldpLegacyObj['DEVICE_A_NAME']
            ednLldpLegacyDataDict['device_a_interface'] = ednLldpLegacyObj['DEVICE_A_INTERFACE']
            ednLldpLegacyDataDict['device_a_trunk_name'] = ednLldpLegacyObj['DEVICE_A_TRUNK_NAME']
            ednLldpLegacyDataDict['device_a_ip'] = ednLldpLegacyObj['DEVICE_A_IP']
            ednLldpLegacyDataDict['device_b_system_name'] = ednLldpLegacyObj['DEVICE_B_SYSTEM_NAME']
            ednLldpLegacyDataDict['device_b_interface'] = ednLldpLegacyObj['DEVICE_B_INTERFACE']
            ednLldpLegacyDataDict['device_b_ip'] = ednLldpLegacyObj['DEVICE_B_IP']
            ednLldpLegacyDataDict['device_b_type'] = ednLldpLegacyObj['DEVICE_B_TYPE']
            ednLldpLegacyDataDict['device_b_port_desc'] = ednLldpLegacyObj['DEVICE_B_PORT_DESC']
            ednLldpLegacyDataDict['device_a_mac'] = ednLldpLegacyObj['DEVICE_A_MAC']
            ednLldpLegacyDataDict['device_b_mac'] = ednLldpLegacyObj['DEVICE_B_MAC']
            ednLldpLegacyDataDict['device_a_port_desc'] = ednLldpLegacyObj['DEVICE_A_PORT_DESC']
            ednLldpLegacyDataDict['device_a_vlan'] = ednLldpLegacyObj['DEVICE_A_VLAN']
            ednLldpLegacyDataDict['server_name'] = ednLldpLegacyObj['SERVER_NAME']
            ednLldpLegacyDataDict['server_os'] = ednLldpLegacyObj['SERVER_OS']
            ednLldpLegacyDataDict['app_name'] = ednLldpLegacyObj['APP_NAME']
            ednLldpLegacyDataDict['owner_name'] = ednLldpLegacyObj['OWNER_NAME']
            ednLldpLegacyDataDict['owner_email'] = ednLldpLegacyObj['OWNER_EMAIL']
            ednLldpLegacyDataDict['owner_contact'] = ednLldpLegacyObj['OWNER_CONTACT']
            ednLldpLegacyDataDict['service_vendor'] = ednLldpLegacyObj['SERVICE_VENDOR']
            ednLldpLegacyDataDict['creation_date'] = FormatDate(ednLldpLegacyObj['CREATION_DATE'])
            ednLldpLegacyDataDict['modification_date'] = FormatDate(ednLldpLegacyObj['MODIFICATION_DATE'])
            ednLldpLegacyObjList.append(ednLldpLegacyDataDict)
       
        content = gzip.compress(json.dumps(ednLldpLegacyObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllEdnLldpLegacyDates',methods=['GET'])
@token_required
def GetAllEdnLldpLegacyDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from edn_lldp_legacy  ORDER BY creation_date DESC;"
        
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllEdnLldpLegacyByDate", methods = ['POST'])
@token_required
def GetAllEdnLldpLegacyByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednLldpLegacyObjList=[]
        #ednLldpLegacyObjs = EDN_LLDP_LEGACY.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        ednLldpLegacyObjs = phy_engine.execute(f"SELECT * FROM edn_lldp_legacy WHERE creation_date = '{current_time}'")

        for ednLldpLegacyObj in ednLldpLegacyObjs:

            ednLldpLegacyDataDict= {}
            ednLldpLegacyDataDict['edn_lldp_legacy_id']=ednLldpLegacyObj['EDN_LLDP_LEGACY_ID']
            ednLldpLegacyDataDict['device_a_name'] = ednLldpLegacyObj['DEVICE_A_NAME']
            ednLldpLegacyDataDict['device_a_interface'] = ednLldpLegacyObj['DEVICE_A_INTERFACE']
            ednLldpLegacyDataDict['device_a_trunk_name'] = ednLldpLegacyObj['DEVICE_A_TRUNK_NAME']
            ednLldpLegacyDataDict['device_a_ip'] = ednLldpLegacyObj['DEVICE_A_IP']
            ednLldpLegacyDataDict['device_b_system_name'] = ednLldpLegacyObj['DEVICE_B_SYSTEM_NAME']
            ednLldpLegacyDataDict['device_b_interface'] = ednLldpLegacyObj['DEVICE_B_INTERFACE']
            ednLldpLegacyDataDict['device_b_ip'] = ednLldpLegacyObj['DEVICE_B_IP']
            ednLldpLegacyDataDict['device_b_type'] = ednLldpLegacyObj['DEVICE_B_TYPE']
            ednLldpLegacyDataDict['device_b_port_desc'] = ednLldpLegacyObj['DEVICE_B_PORT_DESC']
            ednLldpLegacyDataDict['device_a_mac'] = ednLldpLegacyObj['DEVICE_A_MAC']
            ednLldpLegacyDataDict['device_b_mac'] = ednLldpLegacyObj['DEVICE_B_MAC']
            ednLldpLegacyDataDict['device_a_port_desc'] = ednLldpLegacyObj['DEVICE_A_PORT_DESC']
            ednLldpLegacyDataDict['device_a_vlan'] = ednLldpLegacyObj['DEVICE_A_VLAN']
            ednLldpLegacyDataDict['device_a_vlan_name'] = ednLldpLegacyObj["DEVICE_A_VLAN_NAME"]
            ednLldpLegacyDataDict['server_name'] = ednLldpLegacyObj['SERVER_NAME']
            ednLldpLegacyDataDict['server_os'] = ednLldpLegacyObj['SERVER_OS']
            ednLldpLegacyDataDict['app_name'] = ednLldpLegacyObj['APP_NAME']
            ednLldpLegacyDataDict['owner_name'] = ednLldpLegacyObj['OWNER_NAME']
            ednLldpLegacyDataDict['owner_email'] = ednLldpLegacyObj['OWNER_EMAIL']
            ednLldpLegacyDataDict['owner_contact'] = ednLldpLegacyObj['OWNER_CONTACT']
            ednLldpLegacyDataDict['service_vendor'] = ednLldpLegacyObj['SERVICE_VENDOR']
            ednLldpLegacyDataDict['creation_date'] = FormatDate(ednLldpLegacyObj['CREATION_DATE'])
            ednLldpLegacyDataDict['modification_date'] = FormatDate(ednLldpLegacyObj['MODIFICATION_DATE'])
            ednLldpLegacyObjList.append(ednLldpLegacyDataDict)
       
        content = gzip.compress(json.dumps(ednLldpLegacyObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/exportEdnLldpLegacy", methods = ['GET'])
@token_required
def ExportEdnLldpLegacy(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednLldpLegacyObjList=[]
        #ednLldpLegacyObjs = EDN_LLDP_LEGACY.query.all()
        ednLldpLegacyObjs = phy_engine.execute('SELECT * FROM edn_lldp_legacy WHERE creation_date = (SELECT max(creation_date) FROM edn_lldp_legacy)')

        for ednLldpLegacyObj in ednLldpLegacyObjs:

            ednLldpLegacyDataDict= {}
            ednLldpLegacyDataDict['edn_lldp_legacy_id']=ednLldpLegacyObj['EDN_LLDP_LEGACY_ID']
            ednLldpLegacyDataDict['device_a_name'] = ednLldpLegacyObj['DEVICE_A_NAME']
            ednLldpLegacyDataDict['device_a_interface'] = ednLldpLegacyObj['DEVICE_A_INTERFACE']
            ednLldpLegacyDataDict['device_a_trunk_name'] = ednLldpLegacyObj['DEVICE_A_TRUNK_NAME']
            ednLldpLegacyDataDict['device_a_ip'] = ednLldpLegacyObj['DEVICE_A_IP']
            ednLldpLegacyDataDict['device_b_system_name'] = ednLldpLegacyObj['DEVICE_B_SYSTEM_NAME']
            ednLldpLegacyDataDict['device_b_interface'] = ednLldpLegacyObj['DEVICE_B_INTERFACE']
            ednLldpLegacyDataDict['device_b_ip'] = ednLldpLegacyObj['DEVICE_B_IP']
            ednLldpLegacyDataDict['device_b_type'] = ednLldpLegacyObj['DEVICE_B_TYPE']
            ednLldpLegacyDataDict['device_b_port_desc'] = ednLldpLegacyObj['DEVICE_B_PORT_DESC']
            ednLldpLegacyDataDict['device_a_mac'] = ednLldpLegacyObj['DEVICE_A_MAC']
            ednLldpLegacyDataDict['device_b_mac'] = ednLldpLegacyObj['DEVICE_B_MAC']
            ednLldpLegacyDataDict['device_a_port_desc'] = ednLldpLegacyObj['DEVICE_A_PORT_DESC']
            ednLldpLegacyDataDict['device_a_vlan'] = ednLldpLegacyObj['DEVICE_A_VLAN']
            ednLldpLegacyDataDict['server_name'] = ednLldpLegacyObj['SERVER_NAME']
            ednLldpLegacyDataDict['owner_name'] = ednLldpLegacyObj['OWNER_NAME']
            ednLldpLegacyDataDict['owner_email'] = ednLldpLegacyObj['OWNER_EMAIL']
            ednLldpLegacyDataDict['owner_contact'] = ednLldpLegacyObj['OWNER_CONTACT']
            ednLldpLegacyDataDict['creation_date'] = FormatDate(ednLldpLegacyObj['CREATION_DATE'])
            ednLldpLegacyDataDict['modification_date'] = FormatDate(ednLldpLegacyObj['MODIFICATION_DATE'])

            
            ednLldpLegacyObjList.append(ednLldpLegacyDataDict)

        return jsonify(ednLldpLegacyObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editEdnLldpLegacy",methods = ['POST'])
@token_required
def EditEdnLldpLegacy(user_data):
    #if request.headers.get('X-Auth-Key') ==session.get('token', None):
    if True:#session.get('token', None):
        ednLldpLegacyObj = request.get_json()
        print(ednLldpLegacyObj,file = sys.stderr)
        ednLldpLegacy = EDN_LLDP_LEGACY.query.with_entities(EDN_LLDP_LEGACY).filter_by(edn_lldp_legacy_id=ednLldpLegacyObj["edn_lldp_legacy_id"]).first()
        '''
        if ednLldpLegacyObj['device_a_name']:
            ednLldpLegacy.device_a_name = ednLldpLegacyObj['device_a_name']          
        if ednLldpLegacyObj['device_a_interface']:
            ednLldpLegacy.device_a_interface = ednLldpLegacyObj['device_a_interface']
        if ednLldpLegacyObj['device_a_trunk_name']:
            ednLldpLegacy.device_a_trunk_name = ednLldpLegacyObj['device_a_trunk_name']
        
        if ednLldpLegacyObj['device_a_ip']:
            ednLldpLegacy.device_a_ip = ednLldpLegacyObj['device_a_ip']
        '''
        if ednLldpLegacyObj['device_b_system_name']:
            ednLldpLegacy.device_b_system_name = ednLldpLegacyObj['device_b_system_name']
        
        if ednLldpLegacyObj['device_b_interface']:
            ednLldpLegacy.device_b_interface = ednLldpLegacyObj['device_b_interface']
        #if ednLldpLegacyObj['device_b_ip']:
        #    ednLldpLegacy.device_b_ip = ednLldpLegacyObj['device_b_ip']
        if ednLldpLegacyObj['device_b_type']:
            ednLldpLegacy.device_b_type = ednLldpLegacyObj['device_b_type']
        if ednLldpLegacyObj['device_b_port_desc']:
            ednLldpLegacy.device_b_port_desc = ednLldpLegacyObj['device_b_port_desc']
        '''
        if ednLldpLegacyObj['device_a_mac']:
            ednLldpLegacy.device_a_mac = ednLldpLegacyObj['device_a_mac']
        if ednLldpLegacyObj['device_b_mac']:
            ednLldpLegacy.device_b_mac = ednLldpLegacyObj['device_b_mac']
        if ednLldpLegacyObj['device_a_port_desc']:
            ednLldpLegacy.device_a_port_desc = ednLldpLegacyObj['device_a_port_desc']
        if ednLldpLegacyObj['device_a_vlan']:
            ednLldpLegacy.device_a_vlan = ednLldpLegacyObj['device_a_vlan']
        '''
        if ednLldpLegacyObj['server_name']:
            ednLldpLegacy.server_name = ednLldpLegacyObj['server_name']
        if ednLldpLegacyObj['server_os']:
            ednLldpLegacy.server_os = ednLldpLegacyObj['server_os']
        if ednLldpLegacyObj['app_name']:
            ednLldpLegacy.app_name = ednLldpLegacyObj['app_name']
        if ednLldpLegacyObj['owner_name']:
            ednLldpLegacy.owner_name = ednLldpLegacyObj['owner_name']
        if ednLldpLegacyObj['owner_email']:
            ednLldpLegacy.owner_email = ednLldpLegacyObj['owner_email']
        if ednLldpLegacyObj['owner_contact']:
            ednLldpLegacy.owner_contact = ednLldpLegacyObj['owner_contact']
        
        UpdateData(ednLldpLegacy)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/fetchEdnLldpLegacy", methods = ['GET'])
@token_required
def FetchEdnLldpLegacy(user_data):  
    if True:
        try:
            FetchEdnLldpLegacyFunc(user_data)
            return jsonify("Success"), 200
            
        except Exception as e:
            return jsonify("Failure"), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchEdnLldpLegacyFunc(user_data):
    ednLLDPLegacyList = []
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query_string = "select ne_ip_address, device_id, sw_type from seed_table where cisco_domain = 'EDN-NET' and (sw_type = 'IOS-XE' or sw_type = 'NX-OS' or sw_type = 'IOS' or sw_type = 'IOS-XR') and operation_status='Production';" 
    result = db.session.execute(query_string)
    for row in result:
        #print(row[0], row[1], row[2], file=sys.stderr)
        ednLLDPLegacyDict = {}
        ednLLDPLegacyDict['ip'] = row[0]
        ednLLDPLegacyDict['hostname'] = row[1]
        ednLLDPLegacyDict['sw_type'] = row[2]
        ednLLDPLegacyDict['time'] = current_time
        ednLLDPLegacyDict['type'] = 'EDN'

        ednLLDPLegacyList.append(ednLLDPLegacyDict)

    print(ednLLDPLegacyList, file=sys.stderr)

    '''
    MAC ACI
    '''
    ednLLDPACIDict = {}
    query_string = "select ne_ip_address, device_id, sw_type, site_id from seed_table where cisco_domain = 'EDN-NET' and sw_type = 'APIC' and operation_status='Production';" 
    result = db.session.execute(query_string)
    for row in result:
        site_apic= row[1].split('-')
        site_apic= '-'.join(site_apic[:-1])
        #print(row[0], row[1], row[2], file=sys.stderr)
        if site_apic in ednLLDPACIDict:
            ednLLDPACIDictEntry = {}
            ednLLDPACIDictEntry['ip'] = row[0]
            ednLLDPACIDictEntry['hostname'] = row[1]
            ednLLDPACIDictEntry['sw_type'] = row[2]
            ednLLDPACIDictEntry['time'] = current_time
            ednLLDPACIDictEntry['type'] = 'EDN-LLDP'
    
            ednLLDPACIDict[site_apic].append(ednLLDPACIDictEntry)
        else:
            site_apic= row[1].split('-')
            site_apic= '-'.join(site_apic[:-1])
            ednLLDPACIDict[site_apic] = []

            ednLLDPACIDictEntry = {}
            ednLLDPACIDictEntry['ip'] = row[0]
            ednLLDPACIDictEntry['hostname'] = row[1]
            ednLLDPACIDictEntry['sw_type'] = row[2]
            ednLLDPACIDictEntry['time'] = current_time
            ednLLDPACIDictEntry['type'] = 'EDN-LLDP'
            ednLLDPACIDict[site_apic].append(ednLLDPACIDictEntry)
    


    '''
    MAC ACI ENDS
    '''

    lldpLegacy= LLDPLegacy()
    ednLLDP= LLDPPuller()
    
    #Update Script Status
    lldpLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-LLDP-Legacy").first()
    try:
        lldpLegacyStatus.script = "EDN-LLDP-Legacy"
        lldpLegacyStatus.status = "Running"
        lldpLegacyStatus.creation_date= current_time
        lldpLegacyStatus.modification_date= current_time
        db.session.add(lldpLegacyStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    try:
        lldpLegacy.getPhysicalMapping(ednLLDPLegacyList)
    except Exception as e:
        print(e, file=sys.stderr)
    
    try:
        ednLLDP.getPhysicalMapping(ednLLDPACIDict, "EDN-LLDP")
    except Exception as e:
        print(e, file=sys.stderr)

    #temp=[{'ip': '10.73.0.1', 'hostname': 'RYD-MLGII-ENT-COR-SW1', 'sw_type': 'NX-OS', 'time': '2022-02-11 18:05:10', 'type': 'EDN'}, {'ip': '10.27.78.108', 'hostname': 'JED-BHN-ENT-EDG-CO-SW108', 'sw_type': 'IOS', 'time': '2022-02-11 18:11:08', 'type': 'EDN'}]
    #lldpLegacy.getPhysicalMapping(temp)
    
    #Update Script Status
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        lldpLegacyStatus.script = "EDN-LLDP-Legacy"
        lldpLegacyStatus.status = "Completed"
        lldpLegacyStatus.creation_date= current_time
        lldpLegacyStatus.modification_date= current_time
        db.session.add(lldpLegacyStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)
    
@app.route("/getEdnLldpLegacyFetchStatus", methods = ['GET'])
@token_required
def GetAllEdnLldpLegacyFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        
        ednLldpLegacyData={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        ednLldpLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-LLDP-Legacy").first()
        if ednLldpLegacyStatus:
            script_status= ednLldpLegacyStatus.status
            script_modifiation_date= str(ednLldpLegacyStatus.modification_date)
        ednLldpLegacyData["fetch_status"] = script_status
        ednLldpLegacyData["fetch_date"]= script_modifiation_date
        content = gzip.compress(json.dumps(ednLldpLegacyData).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllIgwLldpLegacy", methods = ['GET'])
@token_required
def GetAllIgwLldpLegacy(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwLldpLegacyObjList=[]
        
        #igwLldpLegacyObjs = IGW_LLDP_LEGACY.query.all()
        igwLldpLegacyObjs = phy_engine.execute('SELECT * FROM igw_lldp_legacy WHERE creation_date = (SELECT max(creation_date) FROM igw_lldp_legacy)')
        
        for igwLldpLegacyObj in igwLldpLegacyObjs:

            igwLldpLegacyDataDict= {}
            igwLldpLegacyDataDict['igw_lldp_legacy_id']=igwLldpLegacyObj['IGW_LLDP_LEGACY_ID']
            igwLldpLegacyDataDict['device_a_name'] = igwLldpLegacyObj['DEVICE_A_NAME']
            igwLldpLegacyDataDict['device_a_interface'] = igwLldpLegacyObj['DEVICE_A_INTERFACE']
            igwLldpLegacyDataDict['device_a_trunk_name'] = igwLldpLegacyObj['DEVICE_A_TRUNK_NAME']
            igwLldpLegacyDataDict['device_a_ip'] = igwLldpLegacyObj['DEVICE_A_IP']
            igwLldpLegacyDataDict['device_b_system_name'] = igwLldpLegacyObj['DEVICE_B_SYSTEM_NAME']
            igwLldpLegacyDataDict['device_b_interface'] = igwLldpLegacyObj['DEVICE_B_INTERFACE']
            igwLldpLegacyDataDict['device_b_ip'] = igwLldpLegacyObj['DEVICE_B_IP']
            igwLldpLegacyDataDict['device_b_type'] = igwLldpLegacyObj['DEVICE_B_TYPE']
            igwLldpLegacyDataDict['device_b_port_desc'] = igwLldpLegacyObj['DEVICE_B_PORT_DESC']
            igwLldpLegacyDataDict['device_a_mac'] = igwLldpLegacyObj['DEVICE_A_MAC']
            igwLldpLegacyDataDict['device_b_mac'] = igwLldpLegacyObj['DEVICE_B_MAC']
            igwLldpLegacyDataDict['device_a_port_desc'] = igwLldpLegacyObj['DEVICE_A_PORT_DESC']
            igwLldpLegacyDataDict['device_a_vlan'] = igwLldpLegacyObj['DEVICE_A_VLAN']
            igwLldpLegacyDataDict['server_name'] = igwLldpLegacyObj['SERVER_NAME']
            igwLldpLegacyDataDict['server_os'] = igwLldpLegacyObj['SERVER_OS']
            igwLldpLegacyDataDict['app_name'] = igwLldpLegacyObj['APP_NAME']
            igwLldpLegacyDataDict['owner_name'] = igwLldpLegacyObj['OWNER_NAME']
            igwLldpLegacyDataDict['owner_email'] = igwLldpLegacyObj['OWNER_EMAIL']
            igwLldpLegacyDataDict['owner_contact'] = igwLldpLegacyObj['OWNER_CONTACT']
            igwLldpLegacyDataDict['service_vendor'] = igwLldpLegacyObj['SERVICE_VENDOR']
            igwLldpLegacyDataDict['creation_date'] = FormatDate(igwLldpLegacyObj['CREATION_DATE'])
            igwLldpLegacyDataDict['modification_date'] = FormatDate(igwLldpLegacyObj['MODIFICATION_DATE'])
            igwLldpLegacyDataDict['device_b_mac_vendor'] = igwLldpLegacyObj["DEVICE_B_MAC_VENDOR"]
            igwLldpLegacyObjList.append(igwLldpLegacyDataDict)

        content = gzip.compress(json.dumps(igwLldpLegacyObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllIgwLldpLegacyDates',methods=['GET'])
@token_required
def GetAllIgwLldpLegacyDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from igw_lldp_legacy ORDER BY creation_date DESC;"
        
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllIgwLldpLegacyByDate", methods = ['POST'])
@token_required
def GetAllIgwLldpLegacyByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwLldpLegacyObjList=[]
        
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        #igwLldpLegacyObjs = IGW_LLDP_LEGACY.query.all()
        igwLldpLegacyObjs = phy_engine.execute(f"SELECT * FROM igw_lldp_legacy WHERE creation_date = '{current_time}'")
        
        for igwLldpLegacyObj in igwLldpLegacyObjs:

            igwLldpLegacyDataDict= {}
            igwLldpLegacyDataDict['igw_lldp_legacy_id']=igwLldpLegacyObj['IGW_LLDP_LEGACY_ID']
            igwLldpLegacyDataDict['device_a_name'] = igwLldpLegacyObj['DEVICE_A_NAME']
            igwLldpLegacyDataDict['device_a_interface'] = igwLldpLegacyObj['DEVICE_A_INTERFACE']
            igwLldpLegacyDataDict['device_a_trunk_name'] = igwLldpLegacyObj['DEVICE_A_TRUNK_NAME']
            igwLldpLegacyDataDict['device_a_ip'] = igwLldpLegacyObj['DEVICE_A_IP']
            igwLldpLegacyDataDict['device_b_system_name'] = igwLldpLegacyObj['DEVICE_B_SYSTEM_NAME']
            igwLldpLegacyDataDict['device_b_interface'] = igwLldpLegacyObj['DEVICE_B_INTERFACE']
            igwLldpLegacyDataDict['device_b_ip'] = igwLldpLegacyObj['DEVICE_B_IP']
            igwLldpLegacyDataDict['device_b_type'] = igwLldpLegacyObj['DEVICE_B_TYPE']
            igwLldpLegacyDataDict['device_b_port_desc'] = igwLldpLegacyObj['DEVICE_B_PORT_DESC']
            igwLldpLegacyDataDict['device_a_mac'] = igwLldpLegacyObj['DEVICE_A_MAC']
            igwLldpLegacyDataDict['device_b_mac'] = igwLldpLegacyObj['DEVICE_B_MAC']
            igwLldpLegacyDataDict['device_a_port_desc'] = igwLldpLegacyObj['DEVICE_A_PORT_DESC']
            igwLldpLegacyDataDict['device_a_vlan'] = igwLldpLegacyObj['DEVICE_A_VLAN']
            igwLldpLegacyDataDict['server_name'] = igwLldpLegacyObj['SERVER_NAME']
            igwLldpLegacyDataDict['server_os'] = igwLldpLegacyObj['SERVER_OS']
            igwLldpLegacyDataDict['app_name'] = igwLldpLegacyObj['APP_NAME']
            igwLldpLegacyDataDict['owner_name'] = igwLldpLegacyObj['OWNER_NAME']
            igwLldpLegacyDataDict['owner_email'] = igwLldpLegacyObj['OWNER_EMAIL']
            igwLldpLegacyDataDict['owner_contact'] = igwLldpLegacyObj['OWNER_CONTACT']
            igwLldpLegacyDataDict['service_vendor'] = igwLldpLegacyObj['SERVICE_VENDOR']
            igwLldpLegacyDataDict['creation_date'] = FormatDate(igwLldpLegacyObj['CREATION_DATE'])
            igwLldpLegacyDataDict['modification_date'] = FormatDate(igwLldpLegacyObj['MODIFICATION_DATE'])
            igwLldpLegacyDataDict['device_b_mac_vendor'] = igwLldpLegacyObj["DEVICE_B_MAC_VENDOR"]
            igwLldpLegacyObjList.append(igwLldpLegacyDataDict)

        content = gzip.compress(json.dumps(igwLldpLegacyObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/exportIgwLldpLegacy", methods = ['GET'])
@token_required
def ExportIgwLldpLegacy(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwLldpLegacyObjList=[]
        
        #igwLldpLegacyObjs = IGW_LLDP_LEGACY.query.all()
        igwLldpLegacyObjs = phy_engine.execute('SELECT * FROM igw_lldp_legacy WHERE creation_date = (SELECT max(creation_date) FROM igw_lldp_legacy)')
        
        for igwLldpLegacyObj in igwLldpLegacyObjs:

            igwLldpLegacyDataDict= {}
            igwLldpLegacyDataDict['igw_lldp_legacy_id']=igwLldpLegacyObj['IGW_LLDP_LEGACY_ID']
            igwLldpLegacyDataDict['device_a_name'] = igwLldpLegacyObj['DEVICE_A_NAME']
            igwLldpLegacyDataDict['device_a_interface'] = igwLldpLegacyObj['DEVICE_A_INTERFACE']
            igwLldpLegacyDataDict['device_a_trunk_name'] = igwLldpLegacyObj['DEVICE_A_TRUNK_NAME']
            igwLldpLegacyDataDict['device_a_ip'] = igwLldpLegacyObj['DEVICE_A_IP']
            igwLldpLegacyDataDict['device_b_system_name'] = igwLldpLegacyObj['DEVICE_B_SYSTEM_NAME']
            igwLldpLegacyDataDict['device_b_interface'] = igwLldpLegacyObj['DEVICE_B_INTERFACE']
            igwLldpLegacyDataDict['device_b_ip'] = igwLldpLegacyObj['DEVICE_B_IP']
            igwLldpLegacyDataDict['device_b_type'] = igwLldpLegacyObj['DEVICE_B_TYPE']
            igwLldpLegacyDataDict['device_b_port_desc'] = igwLldpLegacyObj['DEVICE_B_PORT_DESC']
            igwLldpLegacyDataDict['device_a_mac'] = igwLldpLegacyObj['DEVICE_A_MAC']
            igwLldpLegacyDataDict['device_b_mac'] = igwLldpLegacyObj['DEVICE_B_MAC']
            igwLldpLegacyDataDict['device_a_port_desc'] = igwLldpLegacyObj['DEVICE_A_PORT_DESC']
            igwLldpLegacyDataDict['device_a_vlan'] = igwLldpLegacyObj['DEVICE_A_VLAN']
            igwLldpLegacyDataDict['server_name'] = igwLldpLegacyObj['SERVER_NAME']
            igwLldpLegacyDataDict['owner_name'] = igwLldpLegacyObj['OWNER_NAME']
            igwLldpLegacyDataDict['owner_email'] = igwLldpLegacyObj['OWNER_EMAIL']
            igwLldpLegacyDataDict['owner_contact'] = igwLldpLegacyObj['OWNER_CONTACT']
            igwLldpLegacyDataDict['creation_date'] = FormatDate(igwLldpLegacyObj['CREATION_DATE'])
            igwLldpLegacyDataDict['modification_date'] = FormatDate(igwLldpLegacyObj['MODIFICATION_DATE'])
            
            igwLldpLegacyObjList.append(igwLldpLegacyDataDict)

        return jsonify(igwLldpLegacyObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/fetchIgwLldpLegacy", methods = ['GET'])
@token_required
def FetchIGWLldpLegacy(user_data):
    
    if True:
        try:
            FetchIGWLldpLegacyFunc(user_data)
            return jsonify("Success"), 200
            
        except Exception as e:
            return jsonify("Failure"), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchIGWLldpLegacyFunc(user_data):    
    igwLLDPLegacyList = []

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query_string = "select ne_ip_address, device_id, sw_type from seed_table where cisco_domain = 'IGW-NET' and (sw_type = 'IOS-XE' or sw_type = 'NX-OS' or sw_type = 'IOS' or sw_type = 'IOS-XR') and operation_status='Production';" 
    result = db.session.execute(query_string)
    for row in result:
        #print(row[0], row[1], row[2], file=sys.stderr)
        igwLLDPLegacyDict = {}
        igwLLDPLegacyDict['ip'] = row[0]
        igwLLDPLegacyDict['hostname'] = row[1]
        igwLLDPLegacyDict['sw_type'] = row[2]
        igwLLDPLegacyDict['time'] = current_time
        igwLLDPLegacyDict['type'] = 'IGW'

        igwLLDPLegacyList.append(igwLLDPLegacyDict)
    
    igwLLDPACIDict = {}
    query_string = "select ne_ip_address, device_id, sw_type, site_id from seed_table where cisco_domain = 'IGW-NET' and sw_type = 'APIC' and operation_status='Production';" 
    result = db.session.execute(query_string)
    for row in result:
        site_apic= row[1].split('-')
        site_apic= '-'.join(site_apic[:-1])
        #print(row[0], row[1], row[2], file=sys.stderr)
        if site_apic in igwLLDPACIDict:
            igwLLDPACIDictEntry = {}
            igwLLDPACIDictEntry['ip'] = row[0]
            igwLLDPACIDictEntry['hostname'] = row[1]
            igwLLDPACIDictEntry['sw_type'] = row[2]
            igwLLDPACIDictEntry['time'] = current_time
            igwLLDPACIDictEntry['type'] = 'IGW-LLDP'
    
            igwLLDPACIDict[site_apic].append(igwLLDPACIDictEntry)
        else:
            site_apic= row[1].split('-')
            site_apic= '-'.join(site_apic[:-1])
            igwLLDPACIDict[site_apic] = []

            igwLLDPACIDictEntry = {}
            igwLLDPACIDictEntry['ip'] = row[0]
            igwLLDPACIDictEntry['hostname'] = row[1]
            igwLLDPACIDictEntry['sw_type'] = row[2]
            igwLLDPACIDictEntry['time'] = current_time
            igwLLDPACIDictEntry['type'] = 'IGW-LLDP'
        

            igwLLDPACIDict[site_apic].append(igwLLDPACIDictEntry)

    print(igwLLDPACIDict, file=sys.stderr)

    igwLLDP= LLDPPuller()

    print(igwLLDPLegacyList, file=sys.stderr)
    try:
        lldpLegacy= LLDPLegacy()

    except Exception as e:
        print("Exception Occured In LLDP Legacy", file=sys.stderr)
    #Update Script Status
    igwLldpStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "IGW-LLDP-Legacy").first()
    try:
        
        igwLldpStatus.script = "IGW-LLDP-Legacy"
        igwLldpStatus.status = "Running"
        igwLldpStatus.creation_date= current_time
        igwLldpStatus.modification_date= current_time
        db.session.add(igwLldpStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

    
    try:
        lldpLegacy.getPhysicalMapping(igwLLDPLegacyList)
    except Exception as e:
        print(e, file=sys.stderr)
    
    try:
        igwLLDP.getPhysicalMapping(igwLLDPACIDict, "IGW")
    except Exception as e:
        print(e, file=sys.stderr)


    #Update Script Status
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        
        igwLldpStatus.script = "IGW-LLDP-Legacy"
        igwLldpStatus.status = "Completed"
        igwLldpStatus.creation_date= current_time
        igwLldpStatus.modification_date= current_time
        db.session.add(igwLldpStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

@app.route("/getIgwLldpLegacyFetchStatus", methods = ['GET'])
@token_required
def GetIgwLldpLegacyFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwLldpLegacyData={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        igwLldpLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "IGW-LLDP-Legacy").first()
        if igwLldpLegacyStatus:
            script_status= igwLldpLegacyStatus.status
            script_modifiation_date= str(igwLldpLegacyStatus.modification_date)
        igwLldpLegacyData["fetch_status"] = script_status
        igwLldpLegacyData["fetch_date"]= script_modifiation_date
        content = gzip.compress(json.dumps(igwLldpLegacyData).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

### EDN Services

@app.route("/addEdnService",methods = ['POST'])
@token_required
def AddEdnServiceDevice(user_data):
    #
    ipStr = ""
    macStr = ""
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednServiceMappingObj = request.get_json()

        print(ednServiceMappingObj,file=sys.stderr)
        ednServiceMapping = EDN_SERVICE_MAPPING()
        if ednServiceMappingObj['device_a_name']:
            ednServiceMapping.device_a_name = ednServiceMappingObj['device_a_name']
        else: 
             ednServiceMapping.device_a_name=""
        if ednServiceMappingObj['device_a_interface']:
            ednServiceMapping.device_a_interface = ednServiceMappingObj['device_a_interface']    
        
        if ednServiceMappingObj['device_b_ip']:
            ipStr = ""
            try:
                ipStr += str(ednServiceMappingObj['device_b_ip'])+","
            except Exception as e:
                print("IP Not Found", file=sys.stderr)
            ednServiceMapping.device_b_ip= ipStr      
        else:
            ipstr=""

        if ednServiceMappingObj['device_b_mac']:
            macStr = ""
            try:
                macStr += str(ednServiceMappingObj['device_b_mac'])+","
            except Exception as e:
                print("MAC Not Found", file=sys.stderr)
            ednServiceMapping.device_b_mac= macStr
        else: 
             macStr = ""
        
        if ednServiceMappingObj['device_b_system_name']:
            ednServiceMapping.device_b_system_name= ednServiceMappingObj['device_b_system_name']
        if ednServiceMappingObj['service_vendor']:
            ednServiceMapping.service_vendor= ednServiceMappingObj['service_vendor']
        if ednServiceMappingObj['device_b_type']:
            ednServiceMapping.device_b_type= ednServiceMappingObj['device_b_type']
        if ednServiceMappingObj['server_name']:
            ednServiceMapping.server_name= ednServiceMappingObj['server_name']
        else:
            return jsonify({'response': "Key 'server_name' is Missing"}), 500 
            raise Exception("Key 'server_name' is Missing")

        if ednServiceMappingObj['server_os']:
            ednServiceMapping.server_os= ednServiceMappingObj['server_os']
        if ednServiceMappingObj['app_name']:
            ednServiceMapping.app_name= ednServiceMappingObj['app_name']
        if ednServiceMappingObj['owner_name']:
            ednServiceMapping.owner_name= ednServiceMappingObj['owner_name']
        if ednServiceMappingObj['owner_email']:
            ednServiceMapping.owner_email= ednServiceMappingObj['owner_email']
        if ednServiceMappingObj['owner_contact']:
            ednServiceMapping.owner_contact= ednServiceMappingObj['owner_contact']
        ednServiceMapping.modified_by = user_data['user_id']
        
        #print(device.sw_eol_date,file=sys.stderr)
        #longest match
        # print(f"WWWWWWWWWWWWWWW {ipStr}   {macStr}   {ednServiceMappingObj['device_a_name']}   {ednServiceMappingObj['device_a_interface']}", file=sys.stderr)
        # if EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip= ipStr).filter_by(device_b_mac= macStr).filter_by(device_a_name= ednServiceMappingObj['device_a_name']).filter_by(device_a_interface= ednServiceMappingObj['device_a_interface']).first() is not None:
        #     ednServiceMapping.edn_service_mapping_id = EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip= ipStr).filter_by(device_b_mac= macStr).filter_by(device_a_name= ednServiceMappingObj['device_a_name']).filter_by(device_a_interface= ednServiceMappingObj['device_a_interface']).first()[0]
        #     print(f"Updated {ednServiceMapping.edn_service_mapping_id}",file=sys.stderr)
        #     ednServiceMapping.modification_date= datetime.now(tz)
        #     UpdateData(ednServiceMapping)
        
        
        # else:
        #     ednServiceMapping.creation_date= datetime.now(tz)
        #     print("Inserted Record",file=sys.stderr)
        #     InsertData(ednServiceMapping)
        
        '''
        #medium match
        elif EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip= ipStr).filter_by(device_b_mac= macStr).filter(EDN_SERVICE_MAPPING.device_a_interface != ednServiceMappingObj['device_a_interface']).first().filter(EDN_SERVICE_MAPPING.device_a_name != ednServiceMappingObj['device_a_name']).first() is not None:
            ednServiceMapping.edn_service_mapping_id = EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter(device_b_ip= ipStr).filter_by(device_b_mac= macStr).filter_by(EDN_SERVICE_MAPPING.device_a_interface !=ednServiceMappingObj['device_a_interface']).filter(EDN_SERVICE_MAPPING.device_a_name != ednServiceMappingObj['device_a_name']).first()[0]
            print(f"Updated {ednServiceMapping.edn_service_mapping_id}",file=sys.stderr)
            ednServiceMapping.modification_date= datetime.now(tz)
            UpdateData(ednServiceMapping) 
        
        elif EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip= ipStr).filter_by(device_b_mac != macStr).filter_by(device_a_interface = ednServiceMappingObj['device_a_interface']).filter_by(device_a_name = ednServiceMappingObj['device_a_name']).first() is not None:
            ednServiceMapping.edn_service_mapping_id = EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip= ipStr).filter_by(device_b_mac != macStr).filter_by(device_a_interface =ednServiceMappingObj['device_a_interface']).filter_by(device_a_name = ednServiceMappingObj['device_a_name']).first()[0]
            print(f"Updated {ednServiceMapping.edn_service_mapping_id}",file=sys.stderr)
            ednServiceMapping.modification_date= datetime.now(tz)
            UpdateData(ednServiceMapping) 
        
        elif EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip != ipStr).filter_by(device_b_mac= macStr).filter_by(device_a_interface = ednServiceMappingObj['device_a_interface']).filter_by(device_a_name = ednServiceMappingObj['device_a_name']).first() is not None:
            ednServiceMapping.edn_service_mapping_id = EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip != ipStr).filter_by(device_b_mac= macStr).filter_by(device_a_interface =ednServiceMappingObj['device_a_interface']).filter_by(device_a_name = ednServiceMappingObj['device_a_name']).first()[0]
            print(f"Updated {ednServiceMapping.edn_service_mapping_id}",file=sys.stderr)
            ednServiceMapping.modification_date= datetime.now(tz)
            UpdateData(ednServiceMapping) 

        # shortest match
        elif EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip != ipStr).filter_by(device_b_mac != macStr).filter_by(device_a_interface = ednServiceMappingObj['device_a_interface']).filter_by(device_a_name = ednServiceMappingObj['device_a_name']).first() is not None:
            ednServiceMapping.edn_service_mapping_id = EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip != ipStr).filter_by(device_b_mac!= macStr).filter_by(device_a_interface =ednServiceMappingObj['device_a_interface']).filter_by(device_a_name = ednServiceMappingObj['device_a_name']).first()[0]
            print(f"Updated {ednServiceMapping.edn_service_mapping_id}",file=sys.stderr)
            ednServiceMapping.modification_date= datetime.now(tz)
            UpdateData(ednServiceMapping) 

        elif EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip != ipStr).filter_by(device_b_mac= macStr).filter_by(device_a_interface != ednServiceMappingObj['device_a_interface']).filter_by(device_a_name != ednServiceMappingObj['device_a_name']).first() is not None:
            ednServiceMapping.edn_service_mapping_id = EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip != ipStr).filter_by(device_b_mac= macStr).filter_by(device_a_interface !=ednServiceMappingObj['device_a_interface']).filter_by(device_a_name != ednServiceMappingObj['device_a_name']).first()[0]
            print(f"Updated {ednServiceMapping.edn_service_mapping_id}",file=sys.stderr)
            ednServiceMapping.modification_date= datetime.now(tz)
            UpdateData(ednServiceMapping) 

        elif EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip = ipStr).filter_by(device_b_mac!= macStr).filter_by(device_a_interface != ednServiceMappingObj['device_a_interface']).filter_by(device_a_name != ednServiceMappingObj['device_a_name']).first() is not None:
            ednServiceMapping.edn_service_mapping_id = EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip = ipStr).filter_by(device_b_mac!= macStr).filter_by(device_a_interface !=ednServiceMappingObj['device_a_interface']).filter_by(device_a_name != ednServiceMappingObj['device_a_name']).first()[0]
            print(f"Updated {ednServiceMapping.edn_service_mapping_id}",file=sys.stderr)
            ednServiceMapping.modification_date= datetime.now(tz)
            UpdateData(ednServiceMapping) 
        '''
        #insert
        if EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(server_name = ednServiceMappingObj['server_name']).first() is not None:
            if 'edn_service_mapping_id' in ednServiceMappingObj:
                if not ednServiceMappingObj['edn_service_mapping_id']:
                    return jsonify({'response': "Server Already Exists"}), 500 
            ednServiceMapping.edn_service_mapping_id = EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(server_name = ednServiceMappingObj['server_name']).first()[0]
            latestTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ednServiceMapping.modification_date=latestTime

            print(f"Updated {ednServiceMapping.edn_service_mapping_id}" ,file=sys.stderr)
            UpdateData(ednServiceMapping)
        #if ednServiceMappingObj.get('device_b_ip') =="" and ednServiceMappingObj.get('device_b_mac') !="" and ednServiceMappingObj.get('device_a_interface') !="" and ednServiceMappingObj.get('device_a_name') !="": 
        #    if EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip = ednServiceMappingObj['device_b_ip']).filter_by(device_b_mac= ednServiceMappingObj['device_b_mac']).filter_by(device_b_name= ednServiceMappingObj['device_a_name']).filter_by(device_b_interface= ednServiceMappingObj['device_a_interface']).first() is not None:
        #        ednServiceMapping.modification_date=time
        #        ednServiceMapping.edn_service_mapping_id = EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip= ednServiceMappingObj['device_b_ip']).filter_by(device_b_mac= ednServiceMappingObj['device_b_mac']).filter_by(device_b_name= ednServiceMappingObj['device_a_name']).filter_by(device_b_interface= ednServiceMappingObj['device_a_interface']).first()[0]
        #        print(f"Updated {ednServiceMapping.edn_service_mapping_id}" ,file=sys.stderr)
        #        UpdateData(ednServiceMapping)

        else:
            latestTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            ednServiceMapping.creation_date= latestTime
            ednServiceMapping.modification_date= latestTime
            InsertData(ednServiceMapping)
            print("Data Inserted Successfully", file=sys.stderr)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnServiceDates",methods=['GET'])
@token_required
def GetAllEdnServiceDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from edn_service_mapping  ORDER BY creation_date DESC;"
        
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllEdnServicebyDate", methods = ['POST'])
@token_required
def GetAllEdnServicebyDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednServiceMappingObjList=[]
        #ednServiceMappingObjs = EDN_SERVICE_MAPPING.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        ednServiceMappingObjs = phy_engine.execute(f"SELECT * FROM edn_service_mapping WHERE creation_date = '{current_time}'")

        for ednServiceMappingObj in ednServiceMappingObjs:

            ednServiceMappingDataDict= {}
            ednServiceMappingDataDict['edn_service_mapping_id']=ednServiceMappingObj['EDN_SERVICE_MAPPING_ID']
            ednServiceMappingDataDict['device_a_name'] = ednServiceMappingObj['DEVICE_A_NAME']
            ednServiceMappingDataDict['device_a_interface'] = ednServiceMappingObj['DEVICE_A_INTERFACE']
            ednServiceMappingDataDict['device_b_ip'] = ednServiceMappingObj['DEVICE_B_IP']
            ednServiceMappingDataDict['device_b_mac'] = ednServiceMappingObj['DEVICE_B_MAC']
            ednServiceMappingDataDict['device_b_system_name'] = ednServiceMappingObj['DEVICE_B_SYSTEM_NAME']
            ednServiceMappingDataDict['device_b_type'] = ednServiceMappingObj['DEVICE_B_TYPE']
            ednServiceMappingDataDict['server_name'] = ednServiceMappingObj['SERVER_NAME']
            ednServiceMappingDataDict['server_os'] = ednServiceMappingObj['SERVER_OS']
            ednServiceMappingDataDict['app_name'] = ednServiceMappingObj['APP_NAME']
            ednServiceMappingDataDict['owner_name'] = ednServiceMappingObj['OWNER_NAME']
            ednServiceMappingDataDict['owner_email'] = ednServiceMappingObj['OWNER_EMAIL']
            ednServiceMappingDataDict['owner_contact'] = ednServiceMappingObj['OWNER_CONTACT']
            ednServiceMappingDataDict['service_vendor'] = ednServiceMappingObj['service_vendor']
            ednServiceMappingDataDict['creation_date'] = FormatDate(ednServiceMappingObj['CREATION_DATE'])
            ednServiceMappingDataDict['modification_date'] = FormatDate(ednServiceMappingObj['MODIFICATION_DATE'])
            ednServiceMappingObjList.append(ednServiceMappingDataDict)
       
        content = gzip.compress(json.dumps(ednServiceMappingObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteEdnServiceDevice",methods = ['POST'])
@token_required
def DeleteEdnServiceDevice(user_data):
    if True:#session.get('token', None):
        ednServiceMappingObj = request.get_json()
        #ednServiceMappingObj= ednServiceMappingObj.get("ips")
        #ednServiceMappingObj = [9,10,11,12,13]
        print(ednServiceMappingObj,file = sys.stderr)
        
        for obj in ednServiceMappingObj.get("ips"):
            ednServiceMappingId = EDN_SERVICE_MAPPING.query.filter(EDN_SERVICE_MAPPING.edn_service_mapping_id==obj).first()
            print(ednServiceMappingId,file=sys.stderr)
            if obj:
                db.session.delete(ednServiceMappingId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
        
@app.route("/getAllEdnServices", methods = ['GET'])
@token_required
def GetAllEdnServiceMapping(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednServiceMappingObjList=[]
        
        ednServiceMappingObjs = phy_engine.execute(f'SELECT * FROM edn_service_mapping')

        for ednServiceMappingObj in ednServiceMappingObjs:
            try:
                ednServiceMappingDataDict={}

                ednServiceMappingDataDict['edn_service_mapping_id']=ednServiceMappingObj['EDN_SERVICE_MAPPING_ID']
                ednServiceMappingDataDict['device_a_name'] = ednServiceMappingObj['DEVICE_A_NAME']
                ednServiceMappingDataDict['device_a_interface'] = ednServiceMappingObj['DEVICE_A_INTERFACE']
                ip= ednServiceMappingObj['DEVICE_B_IP']
                if ip:
                    ip=ip[:-1]
                    ednServiceMappingDataDict['device_b_ip'] = ip
                
                mac= ednServiceMappingObj['DEVICE_B_MAC']
                if mac:
                    mac=mac[:-1]
                    ednServiceMappingDataDict['device_b_mac'] = mac
                ednServiceMappingDataDict['device_b_system_name'] = ednServiceMappingObj['DEVICE_B_SYSTEM_NAME']
                ednServiceMappingDataDict['device_b_type'] = ednServiceMappingObj['DEVICE_B_TYPE']            
                ednServiceMappingDataDict['server_name'] = ednServiceMappingObj['SERVER_NAME']
                ednServiceMappingDataDict['server_os'] = ednServiceMappingObj['SERVER_OS']
                ednServiceMappingDataDict['app_name'] = ednServiceMappingObj['APP_NAME']
                ednServiceMappingDataDict['owner_name'] = ednServiceMappingObj['OWNER_NAME']
                ednServiceMappingDataDict['owner_email'] = ednServiceMappingObj['OWNER_EMAIL']
                ednServiceMappingDataDict['owner_contact'] = ednServiceMappingObj['OWNER_CONTACT']
                ednServiceMappingDataDict['modified_by'] = ednServiceMappingObj['MODIFIED_BY']
                ednServiceMappingDataDict['service_vendor'] = ednServiceMappingObj['SERVICE_VENDOR']
                ednServiceMappingDataDict['creation_date'] = FormatDate(ednServiceMappingObj['CREATION_DATE'])
                ednServiceMappingDataDict['modification_date'] = FormatDate(ednServiceMappingObj['MODIFICATION_DATE'])
                ednServiceMappingObjList.append(ednServiceMappingDataDict)
            except Exception as e:
                traceback.print_exc()
                print(f"Error {e}", file=sys.stderr)
        content = gzip.compress(json.dumps(ednServiceMappingObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/exportEdnServices", methods = ['GET'])
@token_required
def ExportEdnServiceMapping(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednServiceMappingObjList=[]
        ednServiceMappingObjs = EDN_SERVICE_MAPPING.query.all()

        for ednServiceMappingObj in ednServiceMappingObjs:

            ednServiceMappingDataDict= {}
            ednServiceMappingDataDict['edn_service_mapping_id']=ednServiceMappingObjs.edn_service_mapping_id
            ednServiceMappingDataDict['device_a_name'] = ednServiceMappingObj.device_a_name
            ednServiceMappingDataDict['device_a_interface'] = ednServiceMappingObj.device_a_interface
            ednServiceMappingDataDict['device_a_trunk_name'] = ednServiceMappingObj.device_a_trunk_name
            ednServiceMappingDataDict['device_a_ip'] = ednServiceMappingObj.device_a_ip
            ednServiceMappingDataDict['device_b_system_name'] = ednServiceMappingObj.device_b_system_name
            ednServiceMappingDataDict['device_b_interface'] = ednServiceMappingObj.device_b_interface
            ednServiceMappingDataDict['device_b_ip'] = ednServiceMappingObj.device_b_ip
            ednServiceMappingDataDict['device_b_type'] = ednServiceMappingObj.device_b_type
            ednServiceMappingDataDict['device_b_port_desc'] = ednServiceMappingObj.device_b_port_desc
            ednServiceMappingDataDict['device_a_mac'] = ednServiceMappingObj.device_a_mac
            ednServiceMappingDataDict['device_b_mac'] = ednServiceMappingObj.device_b_mac
            ednServiceMappingDataDict['device_a_port_desc'] = ednServiceMappingObj.device_a_port_desc
            ednServiceMappingDataDict['device_a_vlan'] = ednServiceMappingObj.device_a_vlan
            ednServiceMappingDataDict['creation_date'] = FormatDate(ednServiceMappingObj.creation_date)
            ednServiceMappingDataDict['modification_date'] = FormatDate(ednServiceMappingObj.modification_date)
            
            ednServiceMappingObjList.append(ednServiceMappingDataDict)

        return jsonify(ednServiceMappingObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/addIgwService",methods = ['POST'])
@token_required
def AddIgwServiceMappingDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwServiceMappingObj = request.get_json()

        print(igwServiceMappingObj,file=sys.stderr)
        igwServiceMapping = IGW_SERVICE_MAPPING()
        if igwServiceMappingObj['device_a_name']:
            igwServiceMapping.device_a_name = igwServiceMappingObj['device_a_name']
        if igwServiceMappingObj['device_a_interface']:
            igwServiceMapping.device_a_interface = igwServiceMappingObj['device_a_interface']    
        if igwServiceMappingObj['device_b_ip']:
            igwServiceMapping.device_b_ip= igwServiceMappingObj['device_b_ip']      
        if igwServiceMappingObj['device_b_mac']:
            igwServiceMapping.device_b_mac= igwServiceMappingObj['device_b_mac']
        if igwServiceMappingObj['device_b_system_name']:
            igwServiceMapping.device_b_system_name= igwServiceMappingObj['device_b_system_name']
        if igwServiceMappingObj['device_b_type']:
            igwServiceMapping.device_b_type= igwServiceMappingObj['device_b_type']
        if igwServiceMappingObj['server_name']:
            igwServiceMapping.server_name= igwServiceMappingObj['server_name']
        if igwServiceMappingObj['server_os']:
            igwServiceMapping.server_os= igwServiceMappingObj['server_os']
        if igwServiceMappingObj['app_name']:
            igwServiceMapping.app_name= igwServiceMappingObj['app_name']
        if igwServiceMappingObj['owner_name']:
            igwServiceMapping.owner_name= igwServiceMappingObj['owner_name']
        if igwServiceMappingObj['owner_email']:
            igwServiceMapping.owner_email= igwServiceMappingObj['owner_email']
        if igwServiceMappingObj['owner_contact']:
            igwServiceMapping.owner_contact= igwServiceMappingObj['owner_contact']
       
        #print(device.sw_eol_date,file=sys.stderr)
        
        if IGW_SERVICE_MAPPING.query.with_entities(IGW_SERVICE_MAPPING.igw_service_mapping_id).filter_by(igw_service_mapping_id=igwServiceMappingObj['igw_service_mapping_id']).first() is not None:
            igwServiceMapping.igw_service_mapping_id = IGW_SERVICE_MAPPING.query.with_entities(IGW_SERVICE_MAPPING.igw_service_mapping_id).filter_by(igw_service_mapping_id=igwServiceMappingObj['igw_service_mapping_id']).first()[0]
            print(f"Updated {igwServiceMappingObj['igw_service_mapping_id']}",file=sys.stderr)
            igwServiceMapping.modification_date= datetime.now(tz)
            UpdateData(igwServiceMapping)
            
        else:
            igwServiceMapping.creation_date= datetime.now(tz)
            igwServiceMapping.modification_date= datetime.now(tz)
            print("Inserted Record",file=sys.stderr)
            InsertData(igwServiceMapping)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllIgwServiceDates", methods=['GET'])
@token_required
def GetAllIgwServiceDates(user_data):
    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from igw_service_mapping  ORDER BY creation_date DESC;"
        
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getAllIgwServicebyDate", methods = ['POST'])
@token_required
def GetAllIgwServicebyDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwServiceMappingObjList=[]
        #igwServiceMappingObjs = IGW_SERVICE_MAPPING.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        
        igwServiceMappingObjs = phy_engine.execute(f"SELECT * FROM igw_service_mapping WHERE creation_date = '{current_time}'")

        for igwServiceMappingObj in igwServiceMappingObjs:

            igwServiceMappingDataDict= {}
            igwServiceMappingDataDict['igw_service_mapping_id']=igwServiceMappingObj['IGW_SERVICE_MAPPING_ID']
            igwServiceMappingDataDict['device_a_name'] = igwServiceMappingObj['DEVICE_A_NAME']
            igwServiceMappingDataDict['device_a_interface'] = igwServiceMappingObj['DEVICE_A_INTERFACE']
            igwServiceMappingDataDict['device_b_ip'] = igwServiceMappingObj['DEVICE_B_IP']
            igwServiceMappingDataDict['device_b_mac'] = igwServiceMappingObj['DEVICE_B_MAC']
            igwServiceMappingDataDict['device_b_system_name'] = igwServiceMappingObj['DEVICE_B_SYSTEM_NAME']
            igwServiceMappingDataDict['device_b_type'] = igwServiceMappingObj['DEVICE_B_TYPE']
            
            igwServiceMappingDataDict['server_name'] = igwServiceMappingObj['SERVER_NAME']
            igwServiceMappingDataDict['server_os'] = igwServiceMappingObj['SERVER_OS']
            igwServiceMappingDataDict['app_name'] = igwServiceMappingObj['APP_NAME']
            igwServiceMappingDataDict['owner_name'] = igwServiceMappingObj['OWNER_NAME']
            igwServiceMappingDataDict['owner_email'] = igwServiceMappingObj['OWNER_EMAIL']
            igwServiceMappingDataDict['owner_contact'] = igwServiceMappingObj['OWNER_CONTACT']
            igwServiceMappingDataDict['creation_date'] = FormatDate(igwServiceMappingObj['CREATION_DATE'])
            igwServiceMappingDataDict['modification_date'] = FormatDate(igwServiceMappingObj['MODIFICATION_DATE'])
            igwServiceMappingObjList.append(igwServiceMappingDataDict)
       
        content = gzip.compress(json.dumps(igwServiceMappingObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteIgwServiceDevice",methods = ['POST'])
@token_required
def DeleteIgwServiceDevice(user_data):
    if True:#session.get('token', None):
        igwServiceMappingObj = request.get_json()
        #igwServiceMappingObj= igwServiceMappingObj.get("ips")
        #igwServiceMappingObj = [9,10,11,12,13]
        print(igwServiceMappingObj,file = sys.stderr)
        
        for obj in igwServiceMappingObj.get("ips"):
            igwServiceMappingId = IGW_SERVICE_MAPPING.query.filter(IGW_SERVICE_MAPPING.igw_service_mapping_id==obj).first()
            print(igwServiceMappingId,file=sys.stderr)
            if obj:
                db.session.delete(igwServiceMappingId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
       
@app.route("/getAllIgwServices", methods = ['GET'])
@token_required
def GetAllIgwServiceMapping(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwServiceMappingObjList=[]
        
        igwServiceMappingObjs = phy_engine.execute(f'SELECT * FROM igw_service_mapping ')

        for igwServiceMappingObj in igwServiceMappingObjs:
            igwServiceMappingDataDict={}

            igwServiceMappingDataDict['igw_service_mapping_id']=igwServiceMappingObj['IGW_SERVICE_MAPPING_ID']
            igwServiceMappingDataDict['device_a_name'] = igwServiceMappingObj['DEVICE_A_NAME']
            igwServiceMappingDataDict['device_a_interface'] = igwServiceMappingObj['DEVICE_A_INTERFACE']
            igwServiceMappingDataDict['device_b_ip'] = igwServiceMappingObj['DEVICE_B_IP']
            igwServiceMappingDataDict['device_b_mac'] = igwServiceMappingObj['DEVICE_B_MAC']
            igwServiceMappingDataDict['device_b_system_name'] = igwServiceMappingObj['DEVICE_B_SYSTEM_NAME']
            igwServiceMappingDataDict['device_b_type'] = igwServiceMappingObj['DEVICE_B_TYPE']
            
            igwServiceMappingDataDict['server_name'] = igwServiceMappingObj['SERVER_NAME']
            igwServiceMappingDataDict['server_os'] = igwServiceMappingObj['SERVER_OS']
            igwServiceMappingDataDict['app_name'] = igwServiceMappingObj['APP_NAME']
            igwServiceMappingDataDict['owner_name'] = igwServiceMappingObj['OWNER_NAME']
            igwServiceMappingDataDict['owner_email'] = igwServiceMappingObj['OWNER_EMAIL']
            igwServiceMappingDataDict['owner_contact'] = igwServiceMappingObj['OWNER_CONTACT']
            igwServiceMappingDataDict['creation_date'] = FormatDate(igwServiceMappingObj['CREATION_DATE'])
            igwServiceMappingDataDict['modification_date'] = FormatDate(igwServiceMappingObj['MODIFICATION_DATE'])
            igwServiceMappingObjList.append(igwServiceMappingDataDict)
        content = gzip.compress(json.dumps(igwServiceMappingObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/exportIgwServices", methods = ['GET'])
@token_required
def ExportIgwServiceMapping(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwServiceMappingObjList=[]
        igwServiceMappingObjs = IGW_SERVICE_MAPPING.query.all()

        for igwServiceMappingObj in igwServiceMappingObjs:

            igwServiceMappingDataDict= {}
            igwServiceMappingDataDict['igw_service_mapping_id']=igwServiceMappingObjs.igw_service_mapping_id
            igwServiceMappingDataDict['device_a_name'] = igwServiceMappingObj.device_a_name
            igwServiceMappingDataDict['device_a_interface'] = igwServiceMappingObj.device_a_interface
            igwServiceMappingDataDict['device_a_trunk_name'] = igwServiceMappingObj.device_a_trunk_name
            igwServiceMappingDataDict['device_a_ip'] = igwServiceMappingObj.device_a_ip
            igwServiceMappingDataDict['device_b_system_name'] = igwServiceMappingObj.device_b_system_name
            igwServiceMappingDataDict['device_b_interface'] = igwServiceMappingObj.device_b_interface
            igwServiceMappingDataDict['device_b_ip'] = igwServiceMappingObj.device_b_ip
            igwServiceMappingDataDict['device_b_type'] = igwServiceMappingObj.device_b_type
            igwServiceMappingDataDict['device_b_port_desc'] = igwServiceMappingObj.device_b_port_desc
            igwServiceMappingDataDict['device_a_mac'] = igwServiceMappingObj.device_a_mac
            igwServiceMappingDataDict['device_b_mac'] = igwServiceMappingObj.device_b_mac
            igwServiceMappingDataDict['device_a_port_desc'] = igwServiceMappingObj.device_a_port_desc
            igwServiceMappingDataDict['device_a_vlan'] = igwServiceMappingObj.device_a_vlan
            igwServiceMappingDataDict['creation_date'] = FormatDate(igwServiceMappingObj.creation_date)
            igwServiceMappingDataDict['modification_date'] = FormatDate(igwServiceMappingObj.modification_date)
            
            igwServiceMappingObjList.append(igwServiceMappingDataDict)

        return jsonify(igwServiceMappingObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/addEdnServices", methods = ['POST'])
@token_required
def AddEdnServiceDevices(user_data):
    if True  :#request.headers.get('X-Auth-Key') == session.get('token', None):
        try:       
            result= AddEdnServiceDevicesFunc(user_data)

            return result
        except Exception as e:
            print(f"Error occured when importing igw Mapping {e}", file=sys.stderr)
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Unauthorized", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Access'}), 401


def AddEdnServiceDevicesFunc(user_data):

        postData = request.get_json()
        time= datetime.now(tz)
        print(postData, file=sys.stderr)
        if not postData:
            print("No Data Found", file=sys.stderr)
            return jsonify({'response': "Please Insert Data"}), 406
        isFailed=False

        try:
            for ednServiceMappingObj in postData:
                ipStr = ""
                macStr = ""
                isMissing=False
                ednServiceMapping = EDN_SERVICE_MAPPING()

                if 'device_a_name' in ednServiceMappingObj:
                    if ednServiceMappingObj['device_a_name']:
                        ednServiceMapping.device_a_name = ednServiceMappingObj['device_a_name']
                    else:
                        ednServiceMapping.device_a_name = ''
                    #     isMissing= True
                else:
                    ednServiceMapping.device_a_name = ''
                    # isMissing= True
                
                if 'device_a_interface' in ednServiceMappingObj:
                    if ednServiceMappingObj['device_a_interface']:
                        ednServiceMapping.device_a_interface = ednServiceMappingObj['device_a_interface']
                    else:
                        ednServiceMapping.device_a_interface = ''
                else:
                    ednServiceMapping.device_a_interface = ''
                    # isMissing= True
                
                if 'device_b_ip' in ednServiceMappingObj:
                    if ednServiceMappingObj['device_b_ip']:
                        ipStr = ""
                        try:
                            ipStr += str(ednServiceMappingObj['device_b_ip'])+","
                        except Exception as e:
                            print("IP Not Found", file=sys.stderr)
                        ednServiceMapping.device_b_ip = ipStr 
                    else:
                        ednServiceMapping.device_b_ip = ''
                    #    isMissing= True
                else:
                    ednServiceMapping.device_b_ip = ''
                    #isMissing= True
                if 'device_b_mac' in ednServiceMappingObj:
                    if ednServiceMappingObj['device_b_mac']:
                        macStr = ""
                        try:
                            macStr += str(ednServiceMappingObj['device_b_mac'])+","
                        except Exception as e:
                            print("MAC Not Found", file=sys.stderr)
                        ednServiceMapping.device_b_mac = macStr
                    else:
                        ednServiceMapping.device_b_mac = ''
                    #    isMissing= True
                else:
                    ednServiceMapping.device_b_mac = ''
                    #isMissing= True
                
                if 'device_b_system_name' in ednServiceMappingObj:
                    if ednServiceMappingObj['device_b_system_name']:
                        ednServiceMapping.device_b_system_name = ednServiceMappingObj['device_b_system_name']
                    else:
                        ednServiceMapping.device_b_system_name = 'NA'
                    #     isMissing= True
                else:
                    ednServiceMapping.device_b_system_name = 'NA'
                    
                    # isMissing= True
                
                if 'device_b_type' in ednServiceMappingObj:
                    if ednServiceMappingObj['device_b_type']:
                        ednServiceMapping.device_b_type = ednServiceMappingObj['device_b_type']
                    else:
                        ednServiceMapping.device_b_type = 'NA'
                    #     isMissing= True
                else:
                    ednServiceMapping.device_b_type = 'NA'
                    
                    # isMissing= True
                
                if 'server_name' in ednServiceMappingObj:
                    if ednServiceMappingObj['server_name']:
                        ednServiceMapping.server_name= ednServiceMappingObj['server_name']
                    else:
                        ednServiceMapping.server_name = 'NA'
                    #     isMissing= True
                else:
                        ednServiceMapping.server_name = 'NA'
                    
                    # isMissing= True

                if 'server_os' in ednServiceMappingObj:
                    if ednServiceMappingObj['server_os']:
                        ednServiceMapping.server_os= ednServiceMappingObj['server_os']
                    else:
                        ednServiceMapping.server_os = 'NA'
                    #     isMissing= True
                else:
                    ednServiceMapping.server_os = 'NA'
                    

                if 'app_name' in ednServiceMappingObj:
                    if ednServiceMappingObj['app_name']:
                        ednServiceMapping.app_name= ednServiceMappingObj['app_name']    
                    else:
                        ednServiceMapping.app_name = 'NA'
                    #     isMissing= True
                else:
                    ednServiceMapping.app_name = 'NA'
                    
                    # isMissing= True

                if 'owner_name' in ednServiceMappingObj:
                    if ednServiceMappingObj['owner_name']:
                        ednServiceMapping.owner_name= ednServiceMappingObj['owner_name']
                    else:
                        ednServiceMapping.owner_name = 'NA'
                    #     isMissing= True
                else:
                    ednServiceMapping.owner_name = 'NA'
                    
                    # isMissing= True

                if 'owner_email' in ednServiceMappingObj:
                    if ednServiceMappingObj['owner_email']:
                        ednServiceMapping.owner_email= ednServiceMappingObj['owner_email']
                    else:
                        ednServiceMapping.owner_email = 'NA'
                    #     isMissing= True
                else:
                    ednServiceMapping.owner_email = 'NA'
                    
                if 'service_vendor' in ednServiceMappingObj:
                    if ednServiceMappingObj['service_vendor']:
                        ednServiceMapping.service_vendor= ednServiceMappingObj['service_vendor']
                    else:
                        ednServiceMapping.service_vendor = 'NA'
                    #     isMissing= True
                else:
                    ednServiceMapping.service_vendor = 'NA'
                    # isMissing= True

                if 'owner_contact' in ednServiceMappingObj:
                    if ednServiceMappingObj['owner_contact']:
                        ednServiceMapping.owner_contact= ednServiceMappingObj['owner_contact']
                    else:
                        ednServiceMapping.owner_contact = 'NA'
                    #     isMissing= True
                else:
                    ednServiceMapping.owner_contact = 'NA'
                    
                    # isMissing= True
                ednServiceMapping.modified_by = user_data['user_id']
                
                # if isMissing==True:
                #     isFailed=True
                
                #ednServiceMapping.creation_date= time
                #ednServiceMapping.modification_date=time

                # exists= False
                # if isMissing== False:
                    #if ednServiceMappingObj.get('device_b_ip') !="" and ednServiceMappingObj.get('device_b_mac') !="" and ednServiceMappingObj.get('device_a_interface') !="" and ednServiceMappingObj.get('device_a_name') !="": 

                # if EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip= ipStr).filter_by(device_b_mac= macStr).filter_by(device_a_name= ednServiceMappingObj.get('device_a_name')).filter_by(device_a_interface= ednServiceMappingObj.get('device_a_interface')).first() is not None:
                #     ednServiceMapping.edn_service_mapping_id = EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip= ipStr).filter_by(device_b_mac= macStr).filter_by(device_a_name= ednServiceMappingObj.get('device_a_name')).filter_by(device_a_interface= ednServiceMappingObj.get('device_a_interface')).first()[0]
                if EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(server_name = ednServiceMappingObj['server_name']).first() is not None:
                    ednServiceMapping.edn_service_mapping_id = EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(server_name = ednServiceMappingObj['server_name']).first()[0]
                    ednServiceMapping.modification_date=time
                    print(f"Updated {ednServiceMapping.edn_service_mapping_id}" ,file=sys.stderr)
                    ednServiceMappingIPOld = EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.device_b_ip).filter_by(server_name = ednServiceMappingObj['server_name']).first()[0]
                    ednServiceMappingMacOld= EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.device_b_mac).filter_by(server_name = ednServiceMappingObj['server_name']).first()[0]
                    
                    device_b_ip= ednServiceMappingIPOld+ednServiceMapping.device_b_ip
                    print(device_b_ip, file=sys.stderr)
                    device_b_ip = ",".join(collections.OrderedDict.fromkeys(device_b_ip.split(",")).keys())
                    print(device_b_ip, file=sys.stderr)
                    ednServiceMapping.device_b_ip= device_b_ip

                    device_b_mac=ednServiceMappingMacOld+ednServiceMapping.device_b_mac
                    device_b_mac = ",".join(collections.OrderedDict.fromkeys(device_b_mac.split(",")).keys())
                    ednServiceMapping.device_b_mac= device_b_mac

                    

                    UpdateData(ednServiceMapping)
                #if ednServiceMappingObj.get('device_b_ip') =="" and ednServiceMappingObj.get('device_b_mac') !="" and ednServiceMappingObj.get('device_a_interface') !="" and ednServiceMappingObj.get('device_a_name') !="": 
                #    if EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip = ednServiceMappingObj['device_b_ip']).filter_by(device_b_mac= ednServiceMappingObj['device_b_mac']).filter_by(device_b_name= ednServiceMappingObj['device_a_name']).filter_by(device_b_interface= ednServiceMappingObj['device_a_interface']).first() is not None:
                #        ednServiceMapping.modification_date=time
                #        ednServiceMapping.edn_service_mapping_id = EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip= ednServiceMappingObj['device_b_ip']).filter_by(device_b_mac= ednServiceMappingObj['device_b_mac']).filter_by(device_b_name= ednServiceMappingObj['device_a_name']).filter_by(device_b_interface= ednServiceMappingObj['device_a_interface']).first()[0]
                #        print(f"Updated {ednServiceMapping.edn_service_mapping_id}" ,file=sys.stderr)
                #        UpdateData(ednServiceMapping)

                else:
                    ednServiceMapping.creation_date= time
                    ednServiceMapping.modification_date=time
                    InsertData(ednServiceMapping)
                    print("Data Inserted Successfully", file=sys.stderr)
        
            if isFailed== True:
                if len(postData)>1:
                    return jsonify({'response': "Failed to insert some records due to missing values"}), 406 
                else:
                    return jsonify({'response': "Failed to insert record due to missing values"}), 406 
                
        except Exception as e:
            print(f"Error occured when importing edn Mapping {e}", file=sys.stderr)
            traceback.print_exc()
            return jsonify({'response': "Internal Server Error"}), 500 
        
        return jsonify({'response': "success","code":"200"})
    
def AddEdnServiceDevicesFuncApi(user_data):
        
        postData = request.get_json()
        time= datetime.now(tz)
        print(postData,file=sys.stderr)
        if not postData:
            print("No Data Found", file=sys.stderr)
            return jsonify({'response': "Please Insert Data"}), 406
        isFailed=False
        try:
            for ednServiceMappingObj in postData:
                isMissing=False
                ednServiceMapping = EDN_SERVICE_MAPPING()
                if 'device_a_name' in ednServiceMappingObj:
                    ednServiceMapping.device_a_name = ednServiceMappingObj['device_a_name']
                else:
                    ednServiceMapping.device_a_name = ''
                if 'device_a_interface' in ednServiceMappingObj:
                    ednServiceMapping.device_a_interface = ednServiceMappingObj['device_a_interface']
                else:
                    ednServiceMapping.device_a_interface = ''
                
                if 'device_b_ip' in ednServiceMappingObj:
                    if ednServiceMappingObj['device_b_ip']:
                        ednServiceMapping.device_b_ip = ednServiceMappingObj['device_b_ip'] 
                    else:
                        isMissing= True
                else:
                    ednServiceMapping.device_b_ip = ''
                    isMissing= True
                if 'device_b_mac' in ednServiceMappingObj:
                    if ednServiceMappingObj['device_b_mac']:
                        ednServiceMapping.device_b_mac = ednServiceMappingObj['device_b_mac']
                    else:
                        isMissing= True
                else:
                    ednServiceMapping.device_b_mac = ''
                    isMissing= True
                
                if 'device_b_system_name' in ednServiceMappingObj:
                    if ednServiceMappingObj['device_b_system_name']:
                        ednServiceMapping.device_b_system_name = ednServiceMappingObj['device_b_system_name']
                    else:
                        isMissing= True
                else:
                    ednServiceMapping.device_b_system_name = ''
                    isMissing= True
                
                if 'device_b_type' in ednServiceMappingObj:
                    if ednServiceMappingObj['device_b_type']:
                        ednServiceMapping.device_b_type = ednServiceMappingObj['device_b_type']
                    else:
                        isMissing= True
                else:
                    ednServiceMapping.device_b_type = ''
                    isMissing= True
                
                if 'server_name' in ednServiceMappingObj:
                    if ednServiceMappingObj['server_name']:
                        ednServiceMapping.server_name= ednServiceMappingObj['server_name']
                    else:
                        isMissing= True
                else:
                    isMissing= True

                if 'server_os' in ednServiceMappingObj:
                    if ednServiceMappingObj['server_os']:
                        ednServiceMapping.server_os= ednServiceMappingObj['server_os']
                    else:
                        isMissing= True
                else:
                    isMissing= True

                if 'app_name' in ednServiceMappingObj:
                    if ednServiceMappingObj['app_name']:
                        ednServiceMapping.app_name= ednServiceMappingObj['app_name']    
                    else:
                        isMissing= True
                else:
                    isMissing= True

                if 'owner_name' in ednServiceMappingObj:
                    if ednServiceMappingObj['owner_name']:
                        ednServiceMapping.owner_name= ednServiceMappingObj['owner_name']
                    else:
                        isMissing= True
                else:
                    isMissing= True

                if 'owner_email' in ednServiceMappingObj:
                    if ednServiceMappingObj['owner_email']:
                        ednServiceMapping.owner_email= ednServiceMappingObj['owner_email']
                    else:
                        isMissing= True
                else:
                    isMissing= True

                if 'owner_contact' in ednServiceMappingObj:
                    if ednServiceMappingObj['owner_contact']:
                        ednServiceMapping.owner_contact= ednServiceMappingObj['owner_contact']
                    else:
                        isMissing= True
                else:
                    isMissing= True
                
                if isMissing==True:
                    isFailed=True
                
                #ednServiceMapping.creation_date= time
                #ednServiceMapping.modification_date=time


                if isMissing== False:
                    if EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip= ednServiceMappingObj['device_b_ip']).filter_by(device_b_mac= ednServiceMappingObj['device_b_mac']).first() is not None:
                        ednServiceMapping.modification_date=time
                        ednServiceMapping.edn_service_mapping_id = EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(device_b_ip= ednServiceMappingObj['device_b_ip']).filter_by(device_b_mac= ednServiceMappingObj['device_b_mac']).first()[0]
                        print(f"Updated {ednServiceMapping.edn_service_mapping_id}" ,file=sys.stderr)
                        UpdateData(ednServiceMapping)
                    else:
                        ednServiceMapping.creation_date= time
                        ednServiceMapping.modification_date=time

                        print(f"Inserted {ednServiceMapping.edn_service_mapping_id}",file=sys.stderr)
                        InsertData(ednServiceMapping)
        
            if isFailed== True:
                if len(postData)>1:
                    return jsonify({'response': "Failed to insert some records due to missing values"}), 406 
                else:
                    return jsonify({'response': "Failed to insert record due to missing values"}), 406 
                
        except Exception as e:
            print(f"Error occured when importing edn Mapping {e}", file=sys.stderr)
            return jsonify({'response': "Internal Server Error"}), 500 
        
        return jsonify({'response': "success","code":"200"})
    

@app.route("/addIgwServices", methods = ['POST'])
@token_required
def AddIgwServiceDevices(user_data):
    print(user_data, file=sys.stderr)
    if True  :#request.headers.get('X-Auth-Key') == session.get('token', None):
        try:       
            result= AddIgwServiceDevicesFunc(user_data)

            return result
        except Exception as e:
            print(f"Error occured when importing igw Mapping {e}", file=sys.stderr)
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Unauthorized", file=sys.stderr)
        return jsonify({'message': 'Unauthorized to Access'}), 401

def AddIgwServiceDevicesFunc(user_data):
        
        postData = request.get_json()
        time= datetime.now(tz)
        print(postData,file=sys.stderr)
        if not postData:
            print("No Data Found", file=sys.stderr)
            return jsonify({'response': "Please Insert Data"}), 406
        isFailed=False
        try:
            for igwServiceMappingObj in postData:
                isMissing=False
                igwServiceMapping = IGW_SERVICE_MAPPING()
                if 'device_a_name' in igwServiceMappingObj:
                    if igwServiceMappingObj['device_a_name']:
                        igwServiceMapping.device_a_name = igwServiceMappingObj['device_a_name']
                    else:
                        isMissing= True
                else:
                    igwServiceMapping.device_a_name = ''
                    isMissing= True
                
                if 'device_a_interface' in igwServiceMappingObj:
                    if igwServiceMappingObj['device_a_interface']:
                        igwServiceMapping.device_a_interface = igwServiceMappingObj['device_a_interface']
                else:
                    igwServiceMapping.device_a_interface = ''
                    isMissing= True
                
                if 'device_b_ip' in igwServiceMappingObj:
                    if igwServiceMappingObj['device_b_ip']:
                        igwServiceMapping.device_b_ip = igwServiceMappingObj['device_b_ip'] 
                    #else:
                    #    isMissing= True
                else:
                    igwServiceMapping.device_b_ip = ''
                    #isMissing= True
                if 'device_b_mac' in igwServiceMappingObj:
                    if igwServiceMappingObj['device_b_mac']:
                        igwServiceMapping.device_b_mac = igwServiceMappingObj['device_b_mac']
                    #else:
                    #    isMissing= True
                else:
                    igwServiceMapping.device_b_mac = ''
                    #isMissing= True
                
                if 'device_b_system_name' in igwServiceMappingObj:
                    if igwServiceMappingObj['device_b_system_name']:
                        igwServiceMapping.device_b_system_name = igwServiceMappingObj['device_b_system_name']
                    else:
                        isMissing= True
                else:
                    igwServiceMapping.device_b_system_name = ''
                    isMissing= True
                
                if 'device_b_type' in igwServiceMappingObj:
                    if igwServiceMappingObj['device_b_type']:
                        igwServiceMapping.device_b_type = igwServiceMappingObj['device_b_type']
                    else:
                        isMissing= True
                else:
                    igwServiceMapping.device_b_type = ''
                    isMissing= True
                
                if 'server_name' in igwServiceMappingObj:
                    if igwServiceMappingObj['server_name']:
                        igwServiceMapping.server_name= igwServiceMappingObj['server_name']
                    else:
                        isMissing= True
                else:
                    isMissing= True

                if 'server_os' in igwServiceMappingObj:
                    if igwServiceMappingObj['server_os']:
                        igwServiceMapping.server_os= igwServiceMappingObj['server_os']
                    else:
                        isMissing= True
                else:
                    isMissing= True

                if 'app_name' in igwServiceMappingObj:
                    if igwServiceMappingObj['app_name']:
                        igwServiceMapping.app_name= igwServiceMappingObj['app_name']    
                    else:
                        isMissing= True
                else:
                    isMissing= True

                if 'owner_name' in igwServiceMappingObj:
                    if igwServiceMappingObj['owner_name']:
                        igwServiceMapping.owner_name= igwServiceMappingObj['owner_name']
                    else:
                        isMissing= True
                else:
                    isMissing= True

                if 'owner_email' in igwServiceMappingObj:
                    if igwServiceMappingObj['owner_email']:
                        igwServiceMapping.owner_email= igwServiceMappingObj['owner_email']
                    else:
                        isMissing= True
                else:
                    isMissing= True

                if 'owner_contact' in igwServiceMappingObj:
                    if igwServiceMappingObj['owner_contact']:
                        igwServiceMapping.owner_contact= igwServiceMappingObj['owner_contact']
                    else:
                        isMissing= True
                else:
                    isMissing= True
                
                if isMissing==True:
                    isFailed=True
                
                #igwServiceMapping.creation_date= time
                #igwServiceMapping.modification_date=time

                exists= False
                if isMissing== False:
                    #if igwServiceMappingObj.get('device_b_ip') !="" and igwServiceMappingObj.get('device_b_mac') !="" and igwServiceMappingObj.get('device_a_interface') !="" and igwServiceMappingObj.get('device_a_name') !="": 
                    if IGW_SERVICE_MAPPING.query.with_entities(IGW_SERVICE_MAPPING.igw_service_mapping_id).filter_by(device_b_ip= igwServiceMappingObj.get('device_b_ip', "")).filter_by(device_b_mac= igwServiceMappingObj.get('device_b_mac', "")).filter_by(device_a_name= igwServiceMappingObj['device_a_name']).filter_by(device_a_interface= igwServiceMappingObj['device_a_interface']).first() is not None:
                        igwServiceMapping.modification_date=time
                        igwServiceMapping.igw_service_mapping_id = IGW_SERVICE_MAPPING.query.with_entities(IGW_SERVICE_MAPPING.igw_service_mapping_id).filter_by(device_b_ip= igwServiceMappingObj.get('device_b_ip', "")).filter_by(device_b_mac= igwServiceMappingObj.get('device_b_mac', "")).filter_by(device_a_name= igwServiceMappingObj['device_a_name']).filter_by(device_a_interface= igwServiceMappingObj['device_a_interface']).first()[0]
                        print(f"Updated {igwServiceMapping.igw_service_mapping_id}" ,file=sys.stderr)
                        UpdateData(igwServiceMapping)
                    #if igwServiceMappingObj.get('device_b_ip') =="" and igwServiceMappingObj.get('device_b_mac') !="" and igwServiceMappingObj.get('device_a_interface') !="" and igwServiceMappingObj.get('device_a_name') !="": 
                    #    if IGW_SERVICE_MAPPING.query.with_entities(IGW_SERVICE_MAPPING.igw_service_mapping_id).filter_by(device_b_ip = igwServiceMappingObj['device_b_ip']).filter_by(device_b_mac= igwServiceMappingObj['device_b_mac']).filter_by(device_b_name= igwServiceMappingObj['device_a_name']).filter_by(device_b_interface= igwServiceMappingObj['device_a_interface']).first() is not None:
                    #        igwServiceMapping.modification_date=time
                    #        igwServiceMapping.igw_service_mapping_id = IGW_SERVICE_MAPPING.query.with_entities(IGW_SERVICE_MAPPING.igw_service_mapping_id).filter_by(device_b_ip= igwServiceMappingObj['device_b_ip']).filter_by(device_b_mac= igwServiceMappingObj['device_b_mac']).filter_by(device_b_name= igwServiceMappingObj['device_a_name']).filter_by(device_b_interface= igwServiceMappingObj['device_a_interface']).first()[0]
                    #        print(f"Updated {igwServiceMapping.igw_service_mapping_id}" ,file=sys.stderr)
                    #        UpdateData(igwServiceMapping)

                    else:
                        igwServiceMapping.creation_date= time
                        igwServiceMapping.modification_date=time

                        print(f"Inserted {igwServiceMapping.igw_service_mapping_id}",file=sys.stderr)
                        InsertData(igwServiceMapping)
        
            if isFailed== True:
                if len(postData)>1:
                    return jsonify({'response': "Failed to insert some records due to missing values"}), 406 
                else:
                    return jsonify({'response': "Failed to insert record due to missing values"}), 406 
                
        except Exception as e:
            print(f"Error occured when importing igw Mapping {e}", file=sys.stderr)
            return jsonify({'response': "Internal Server Error"}), 500 
        
        return jsonify({'response': "success","code":"200"})
    
def AddIgwServiceDevicesFuncApi(user_data):
        
        postData = request.get_json()
        time= datetime.now(tz)
        print(postData,file=sys.stderr)
        if not postData:
            print("No Data Found", file=sys.stderr)
            return jsonify({'response': "Please Insert Data"}), 406
        isFailed=False
        try:
            for igwServiceMappingObj in postData:
                isMissing=False
                igwServiceMapping = IGW_SERVICE_MAPPING()
                if 'device_a_name' in igwServiceMappingObj:
                    igwServiceMapping.device_a_name = igwServiceMappingObj['device_a_name']
                else:
                    igwServiceMapping.device_a_name = ''
                if 'device_a_interface' in igwServiceMappingObj:
                    igwServiceMapping.device_a_interface = igwServiceMappingObj['device_a_interface']
                else:
                    igwServiceMapping.device_a_interface = ''
                
                if 'device_b_ip' in igwServiceMappingObj:
                    if igwServiceMappingObj['device_b_ip']:
                        igwServiceMapping.device_b_ip = igwServiceMappingObj['device_b_ip'] 
                    else:
                        isMissing= True
                else:
                    igwServiceMapping.device_b_ip = ''
                    isMissing= True
                if 'device_b_mac' in igwServiceMappingObj:
                    if igwServiceMappingObj['device_b_mac']:
                        igwServiceMapping.device_b_mac = igwServiceMappingObj['device_b_mac']
                    else:
                        isMissing= True
                else:
                    igwServiceMapping.device_b_mac = ''
                    isMissing= True
                
                if 'device_b_system_name' in igwServiceMappingObj:
                    if igwServiceMappingObj['device_b_system_name']:
                        igwServiceMapping.device_b_system_name = igwServiceMappingObj['device_b_system_name']
                    else:
                        isMissing= True
                else:
                    igwServiceMapping.device_b_system_name = ''
                    isMissing= True
                
                if 'device_b_type' in igwServiceMappingObj:
                    if igwServiceMappingObj['device_b_type']:
                        igwServiceMapping.device_b_type = igwServiceMappingObj['device_b_type']
                    else:
                        isMissing= True
                else:
                    igwServiceMapping.device_b_type = ''
                    isMissing= True
                
                if 'server_name' in igwServiceMappingObj:
                    if igwServiceMappingObj['server_name']:
                        igwServiceMapping.server_name= igwServiceMappingObj['server_name']
                    else:
                        isMissing= True
                else:
                    isMissing= True

                if 'server_os' in igwServiceMappingObj:
                    if igwServiceMappingObj['server_os']:
                        igwServiceMapping.server_os= igwServiceMappingObj['server_os']
                    else:
                        isMissing= True
                else:
                    isMissing= True

                if 'app_name' in igwServiceMappingObj:
                    if igwServiceMappingObj['app_name']:
                        igwServiceMapping.app_name= igwServiceMappingObj['app_name']    
                    else:
                        isMissing= True
                else:
                    isMissing= True

                if 'owner_name' in igwServiceMappingObj:
                    if igwServiceMappingObj['owner_name']:
                        igwServiceMapping.owner_name= igwServiceMappingObj['owner_name']
                    else:
                        isMissing= True
                else:
                    isMissing= True

                if 'owner_email' in igwServiceMappingObj:
                    if igwServiceMappingObj['owner_email']:
                        igwServiceMapping.owner_email= igwServiceMappingObj['owner_email']
                    else:
                        isMissing= True
                else:
                    isMissing= True

                if 'owner_contact' in igwServiceMappingObj:
                    if igwServiceMappingObj['owner_contact']:
                        igwServiceMapping.owner_contact= igwServiceMappingObj['owner_contact']
                    else:
                        isMissing= True
                else:
                    isMissing= True
                
                if isMissing==True:
                    isFailed=True
                
                #igwServiceMapping.creation_date= time
                #igwServiceMapping.modification_date=time

                if isMissing== False:
                    if IGW_SERVICE_MAPPING.query.with_entities(IGW_SERVICE_MAPPING.igw_service_mapping_id).filter_by(device_b_ip= igwServiceMappingObj['device_b_ip']).filter_by(device_b_mac= igwServiceMappingObj['device_b_mac']).first() is not None:
                        igwServiceMapping.modification_date=time
                        igwServiceMapping.igw_service_mapping_id = IGW_SERVICE_MAPPING.query.with_entities(IGW_SERVICE_MAPPING.igw_service_mapping_id).filter_by(device_b_ip= igwServiceMappingObj['device_b_ip']).filter_by(device_b_mac= igwServiceMappingObj['device_b_mac']).first()[0]
                        print(f"Updated {igwServiceMapping.igw_service_mapping_id}" ,file=sys.stderr)
                        UpdateData(igwServiceMapping)
                    else:
                        igwServiceMapping.creation_date= time
                        igwServiceMapping.modification_date=time

                        print(f"Inserted {igwServiceMapping.igw_service_mapping_id}",file=sys.stderr)
                        InsertData(igwServiceMapping)
        
            if isFailed== True:
                if len(postData)>1:
                    return jsonify({'response': "Failed to insert some records due to missing values"}), 406 
                else:
                    return jsonify({'response': "Failed to insert record due to missing values"}), 406 
                
        except Exception as e:
            print(f"Error occured when importing igw Mapping {e}", file=sys.stderr)
            return jsonify({'response': "Internal Server Error"}), 500 
        
        return jsonify({'response': "success","code":"200"})

@app.route("/fetchIgwMacLegacy", methods = ['GET'])
@token_required
def FetchIgwMacLegacy(user_data):
    if True:
        try:
            FetchIgwMacLegacyFunc(user_data)
            return jsonify("Success"), 200
            
        except Exception as e:
            print(f"Exception Occured {e}", file=sys.stderr)
            return jsonify("Failure"), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def FetchIgwMacLegacyFunc(user_data):
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    igwLLDPACIDict = {}
    query_string = "select ne_ip_address, device_id, sw_type, site_id from seed_table where cisco_domain = 'IGW-NET' and sw_type = 'APIC' and operation_status='Production';" 
    result = db.session.execute(query_string)
    for row in result:
        #print(row[0], row[1], row[2], file=sys.stderr)
        site_apic= row[1].split('-')
        site_apic= '-'.join(site_apic[:-1])
        if site_apic in igwLLDPACIDict:
            igwLLDPACIDictEntry = {}
            igwLLDPACIDictEntry['ip'] = row[0]
            igwLLDPACIDictEntry['hostname'] = row[1]
            igwLLDPACIDictEntry['sw_type'] = row[2]
            igwLLDPACIDictEntry['time'] = current_time
            igwLLDPACIDictEntry['type'] = 'IGW-MAC'
    
            igwLLDPACIDict[site_apic].append(igwLLDPACIDictEntry)
        else:
            site_apic= row[1].split('-')
            site_apic= '-'.join(site_apic[:-1])
            igwLLDPACIDict[site_apic] = []

            igwLLDPACIDictEntry = {}
            igwLLDPACIDictEntry['ip'] = row[0]
            igwLLDPACIDictEntry['hostname'] = row[1]
            igwLLDPACIDictEntry['sw_type'] = row[2]
            igwLLDPACIDictEntry['time'] = current_time
            igwLLDPACIDictEntry['type'] = 'IGW-MAC'
        
            igwLLDPACIDict[site_apic].append(igwLLDPACIDictEntry)

    print(igwLLDPACIDict, file=sys.stderr)

    igwLLDP= LLDPPuller()
    igwMacLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "IGW-MAC-Legacy").first()

    try:
        igwMacLegacyStatus.script = "IGW-MAC-Legacy"
        igwMacLegacyStatus.status = "Running"
        igwMacLegacyStatus.creation_date= current_time
        igwMacLegacyStatus.modification_date= current_time
        db.session.add(igwMacLegacyStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)


    try:
        igwLLDP.getPhysicalMapping(igwLLDPACIDict, "EDN-MAC-Legacy")
    except Exception as e:
        print(e, file=sys.stderr)
   
    #Update Script Status
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        igwMacLegacyStatus.script = "IGW-MAC-Legacy"
        igwMacLegacyStatus.status = "Completed"
        igwMacLegacyStatus.creation_date= current_time
        igwMacLegacyStatus.modification_date= current_time
        db.session.add(igwMacLegacyStatus)
        db.session.commit() 
    except Exception as e:
        db.session.rollback()
        print(f"Error while updating script status {e}", file=sys.stderr)

@app.route("/getIgwMacLegacyFetchStatus", methods = ['GET'])
@token_required
def GetAllIgwMacLegacyFetchStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwMacLegacyData={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        igwMacLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "IGW-MAC-Legacy").first()
        if igwMacLegacyStatus:
            script_status= igwMacLegacyStatus.status
            script_modifiation_date= str(igwMacLegacyStatus.modification_date)
        igwMacLegacyData["fetch_status"] = script_status
        igwMacLegacyData["fetch_date"]= script_modifiation_date

        content = gzip.compress(json.dumps(igwMacLegacyData).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllIgwMacLegacy", methods = ['GET'])
@token_required
def GetAllIgwMacLegacy(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwMacLegacyObjList=[]
        #igwMacLegacyObjs = IGW_MAC_LEGACY.query.all()
        igwMacLegacyObjs = phy_engine.execute('SELECT * FROM igw_mac_legacy WHERE creation_date = (SELECT max(creation_date) FROM igw_mac_legacy)')
        
        for igwMacLegacyObj in igwMacLegacyObjs:

            igwMacLegacyDataDict= {}
            igwMacLegacyDataDict['igw_mac_legacy_id']=igwMacLegacyObj["IGW_MAC_LEGACY_ID"]
            igwMacLegacyDataDict['device_a_name'] = igwMacLegacyObj["DEVICE_A_NAME"]
            igwMacLegacyDataDict['device_a_interface'] = igwMacLegacyObj["DEVICE_A_INTERFACE"]
            igwMacLegacyDataDict['device_a_trunk_name'] = igwMacLegacyObj["DEVICE_A_TRUNK_NAME"]
            igwMacLegacyDataDict['device_a_ip'] = igwMacLegacyObj["DEVICE_A_IP"]
            igwMacLegacyDataDict['device_b_system_name'] = igwMacLegacyObj["DEVICE_B_SYSTEM_NAME"]
            igwMacLegacyDataDict['device_b_interface'] = igwMacLegacyObj["DEVICE_B_INTERFACE"]
            igwMacLegacyDataDict['device_b_ip'] = igwMacLegacyObj["DEVICE_B_IP"]
            igwMacLegacyDataDict['device_b_type'] = igwMacLegacyObj["DEVICE_B_TYPE"]
            igwMacLegacyDataDict['device_b_port_desc'] = igwMacLegacyObj["DEVICE_B_PORT_DESC"]
            igwMacLegacyDataDict['device_a_mac'] = igwMacLegacyObj["DEVICE_A_MAC"]
            igwMacLegacyDataDict['device_b_mac'] = igwMacLegacyObj["DEVICE_B_MAC"]
            igwMacLegacyDataDict['device_a_port_desc'] = igwMacLegacyObj["DEVICE_A_PORT_DESC"]
            igwMacLegacyDataDict['device_a_vlan'] = igwMacLegacyObj["DEVICE_A_VLAN"]
            igwMacLegacyDataDict['device_a_vlan_name'] = igwMacLegacyObj["DEVICE_A_VLAN_NAME"]
            igwMacLegacyDataDict['server_name'] = igwMacLegacyObj["SERVER_NAME"]
            igwMacLegacyDataDict['server_os'] = igwMacLegacyObj["SERVER_OS"]
            igwMacLegacyDataDict['app_name'] = igwMacLegacyObj["APP_NAME"]
            igwMacLegacyDataDict['owner_name'] = igwMacLegacyObj["OWNER_NAME"]
            igwMacLegacyDataDict['owner_email'] = igwMacLegacyObj["OWNER_EMAIL"]
            igwMacLegacyDataDict['owner_contact'] = igwMacLegacyObj["OWNER_CONTACT"]
            igwMacLegacyDataDict['creation_date'] = FormatDate(igwMacLegacyObj["CREATION_DATE"])
            igwMacLegacyDataDict['modification_date'] = FormatDate(igwMacLegacyObj["MODIFICATION_DATE"])
            igwMacLegacyDataDict['device_b_mac_vendor'] = igwMacLegacyObj["DEVICE_B_MAC_VENDOR"]
            igwMacLegacyObjList.append(igwMacLegacyDataDict)

        content = gzip.compress(json.dumps(igwMacLegacyObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllIgwMacLegacyDates',methods=['GET'])
@token_required
def GetAllIgwMacLegacyDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from igw_mac_legacy ORDER BY creation_date DESC;"
        
        result = phy_engine.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getAllIgwMacLegacyByDate", methods = ['POST'])
@token_required
def GetAllIgwMacLegacyByDate(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        igwMacLegacyObjList=[]
        #igwMacLegacyObjs = IGW_MAC_LEGACY.query.all()
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)

        igwMacLegacyObjs = phy_engine.execute(f"SELECT * FROM igw_mac_legacy WHERE creation_date = '{current_time}'")
        
        for igwMacLegacyObj in igwMacLegacyObjs:

            igwMacLegacyDataDict= {}
            igwMacLegacyDataDict['igw_mac_legacy_id']=igwMacLegacyObj["IGW_MAC_LEGACY_ID"]
            igwMacLegacyDataDict['device_a_name'] = igwMacLegacyObj["DEVICE_A_NAME"]
            igwMacLegacyDataDict['device_a_interface'] = igwMacLegacyObj["DEVICE_A_INTERFACE"]
            igwMacLegacyDataDict['device_a_trunk_name'] = igwMacLegacyObj["DEVICE_A_TRUNK_NAME"]
            igwMacLegacyDataDict['device_a_ip'] = igwMacLegacyObj["DEVICE_A_IP"]
            igwMacLegacyDataDict['device_b_system_name'] = igwMacLegacyObj["DEVICE_B_SYSTEM_NAME"]
            igwMacLegacyDataDict['device_b_interface'] = igwMacLegacyObj["DEVICE_B_INTERFACE"]
            igwMacLegacyDataDict['device_b_ip'] = igwMacLegacyObj["DEVICE_B_IP"]
            igwMacLegacyDataDict['device_b_type'] = igwMacLegacyObj["DEVICE_B_TYPE"]
            igwMacLegacyDataDict['device_b_port_desc'] = igwMacLegacyObj["DEVICE_B_PORT_DESC"]
            igwMacLegacyDataDict['device_a_mac'] = igwMacLegacyObj["DEVICE_A_MAC"]
            igwMacLegacyDataDict['device_b_mac'] = igwMacLegacyObj["DEVICE_B_MAC"]
            igwMacLegacyDataDict['device_a_port_desc'] = igwMacLegacyObj["DEVICE_A_PORT_DESC"]
            igwMacLegacyDataDict['device_a_vlan'] = igwMacLegacyObj["DEVICE_A_VLAN"]
            igwMacLegacyDataDict['device_a_vlan_name'] = igwMacLegacyObj["DEVICE_A_VLAN_NAME"]
            igwMacLegacyDataDict['server_name'] = igwMacLegacyObj["SERVER_NAME"]
            igwMacLegacyDataDict['owner_name'] = igwMacLegacyObj["OWNER_NAME"]
            igwMacLegacyDataDict['server_os'] = igwMacLegacyObj["SERVER_OS"]
            igwMacLegacyDataDict['app_name'] = igwMacLegacyObj["APP_NAME"]
            igwMacLegacyDataDict['owner_email'] = igwMacLegacyObj["OWNER_EMAIL"]
            igwMacLegacyDataDict['owner_contact'] = igwMacLegacyObj["OWNER_CONTACT"]
            igwMacLegacyDataDict['creation_date'] = FormatDate(igwMacLegacyObj["CREATION_DATE"])
            igwMacLegacyDataDict['modification_date'] = FormatDate(igwMacLegacyObj["MODIFICATION_DATE"])
            igwMacLegacyDataDict['device_b_mac_vendor'] = igwMacLegacyObj["DEVICE_B_MAC_VENDOR"]
            igwMacLegacyObjList.append(igwMacLegacyDataDict)

        content = gzip.compress(json.dumps(igwMacLegacyObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/syncMacAddressInEDNMAC", methods = ['GET'])
@token_required
def SyncMacAddressInEDNMAC(user_data):
    try:
        count=0
        date=""
        
        fw= AddFwIP()
        newTime= datetime.now(tz)
        ednFirewallArpObjs = phy_engine.execute('SELECT max(creation_date) FROM edn_mac_legacy')
        for row in ednFirewallArpObjs:
            date=row[0]
        if date:
            count= fw.addFWIPToEdnMacLegacy(date, newTime)
        return str(count)
    except Exception as e:
        print("Exception occured in syncing IP addresses", file=sys.stderr)
    return str(f"Success {count}"), 200

@app.route("/syncFromEdnServices", methods = ['GET'])
@token_required
def SyncFromEdnServices(user_data):
    try:
        currentTime=""
        newTime= datetime.now(tz)
        serviceMapping= AddServiceMapping()
        
        currentTimeObj = phy_engine.execute('SELECT max(creation_date) FROM edn_mac_legacy;')
        for row in currentTimeObj:
            currentTime=row[0]
        serviceMapping.addEdnMacLegacyServiceMapping(currentTime, newTime)
        
        return ""
    except Exception as e:
        print("Exception occured in syncing EDN Services", file=sys.stderr)
    return "Success", 200

@app.route("/getEdnMacLegacySyncFirewallStatus", methods = ['GET'])
@token_required
def GetEdnMacLegacySyncFirewallStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednMacLegacyData={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        ednMacLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-MAC-Legacy-FW-Sync").first()
        if ednMacLegacyStatus:
            script_status= ednMacLegacyStatus.status
            script_modifiation_date= str(ednMacLegacyStatus.modification_date)
        ednMacLegacyData["fetch_status"] = script_status
        ednMacLegacyData["fetch_date"]= script_modifiation_date

        content = gzip.compress(json.dumps(ednMacLegacyData).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getEdnMacLegacySyncEDNServicesStatus", methods = ['GET'])
@token_required
def GetEdnMacLegacySyncEdnServicesStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednMacLegacyData={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        ednMacLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-MAC-Legacy-Service-Mapping-Sync").first()
        if ednMacLegacyStatus:
            script_status= ednMacLegacyStatus.status
            script_modifiation_date= str(ednMacLegacyStatus.modification_date)
        ednMacLegacyData["fetch_status"] = script_status
        ednMacLegacyData["fetch_date"]= script_modifiation_date

        content = gzip.compress(json.dumps(ednMacLegacyData).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route("/getEdnServiceMappingSyncFromItStatus", methods = ['GET'])
@token_required
def GetEdnServiceMappingSyncFromItStatus(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednMacLegacyData={}
        
        #Getting status of script
        script_status=""
        script_modifiation_date=""
        ednMacLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-Service-Mapping-Sync").first()
        if ednMacLegacyStatus:
            script_status= ednMacLegacyStatus.status
            script_modifiation_date= str(ednMacLegacyStatus.modification_date)
        ednMacLegacyData["fetch_status"] = script_status
        ednMacLegacyData["fetch_date"]= script_modifiation_date

        content = gzip.compress(json.dumps(ednMacLegacyData).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
