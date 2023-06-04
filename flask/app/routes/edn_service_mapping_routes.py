from crypt import methods
import imp
from operator import pos
import sys, json
from tkinter import N
import traceback
from flask_jsonpify import jsonify
from app import app,phy_engine,db, tz
from flask import request, make_response
from datetime import datetime, timedelta
from app.models.inventory_models import EDN_NET_Seed, EDN_SEC_Seed, EDN_IT_Seed, EDN_Mapping, Device_Table
from app.models.phy_mapping_models import EDN_SERVICE_MAPPING, IT_IP_TABLE, IT_MAC_TABLE, IT_OS_TABLE, IT_OWNER_TABLE, IT_PHYSICAL_SERVERS_TABLE
from app.physical_mapping_scripts.addSericeMapping import AddServiceMapping
import pandas as pd
import gzip
from flask_cors import cross_origin
from app.pullers.EDN_Service_map.servicemap import ServicePuller
from app.pullers.EDN_Service_map.fw_puller import FWPuller
from app.middleware import token_required
from app.models.phy_mapping_models import SCRIPT_STATUS

def InsertData(obj):
    #add data to db
    db.session.add(obj)
    db.session.commit()
    return True

def UpdateData(obj):
    #add data to db
    try:
        db.session.merge(obj)
        db.session.commit()
    except:
        print("Something else went wrong")
    
    return True

@app.route("/addNetSeed", methods = ['POST'])
@token_required
def AddNetSeed(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()

        print(postData,file=sys.stderr)
        
        for seedObj in postData:

            netSeed = EDN_NET_Seed()
            if 'region' in seedObj:
                netSeed.region = seedObj['region'] 
            if 'segment' in seedObj:
                netSeed.segment = seedObj['segment'] 
            if 'switch_id' in seedObj:
                netSeed.switch_id = seedObj['switch_id'] 
            if 'switch_ip_address' in seedObj:
                netSeed.switch_ip_address = seedObj['switch_ip_address'] 
            if 'vendor' in seedObj:
                netSeed.vendor = seedObj['vendor'] 
            if 'os_type' in seedObj:
                netSeed.os_type = seedObj['os_type']    
            try:
                if EDN_NET_Seed.query.with_entities(EDN_NET_Seed.edn_net_seed_id).filter_by(switch_ip_address=seedObj['switch_ip_address']).first() is not None:
                    netSeed.edn_net_seed_id = EDN_NET_Seed.query.with_entities(EDN_NET_Seed.edn_net_seed_id).filter_by(switch_ip_address=seedObj['switch_ip_address']).first()[0]
                    print("Updated " + seedObj['switch_ip_address'],file=sys.stderr)
                    UpdateData(netSeed)
                else:
                    print("Inserted " +seedObj['switch_ip_address'],file=sys.stderr)
                    InsertData(netSeed)
            except Exception as e:
                print(f"Some error occured skipping {e}",file=sys.stderr)

        return jsonify({'response': "success","code":"200"})

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addSecSeed", methods = ['POST'])
@token_required
def AddSecSeed(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()

        print(postData,file=sys.stderr)
        
        for seedObj in postData:
            secSeed = EDN_SEC_Seed()
            if 'region' in seedObj:
                secSeed.region = seedObj['region'] 
            if 'segment' in seedObj:
                secSeed.segment = seedObj['segment'] 
            if 'fw_id' in seedObj:
                secSeed.fw_id = seedObj['fw_id'] 
            if 'fw_ip_address' in seedObj:
                secSeed.fw_ip_address = seedObj['fw_ip_address'] 
            if 'vendor' in seedObj:
                secSeed.vendor = seedObj['vendor'] 
            if 'os_type' in seedObj:
                secSeed.os_type = seedObj['os_type']    
            try:
                if EDN_SEC_Seed.query.with_entities(EDN_SEC_Seed.edn_sec_seed_id).filter_by(fw_ip_address=seedObj['fw_ip_address']).first() is not None:
                    secSeed.edn_sec_seed_id = EDN_SEC_Seed.query.with_entities(EDN_SEC_Seed.edn_sec_seed_id).filter_by(fw_ip_address=seedObj['fw_ip_address']).first()[0]
                    print("Updated " + seedObj['fw_ip_address'],file=sys.stderr)
                    UpdateData(secSeed)
                else:
                    print("Inserted " +seedObj['fw_ip_address'],file=sys.stderr)
                    InsertData(secSeed)
            except:
                print("Some error occured skipping",file=sys.stderr)
            
        return jsonify({'response': "success","code":"200"})

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addITSeed", methods = ['POST'])
@token_required
def AddITSeed(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()

        print(postData,file=sys.stderr)
        
        for seedObj in postData:

            itSeed = EDN_IT_Seed()
            if 'Server Name' in seedObj:
                itSeed.server_name = seedObj['Server Name'] 
            if 'IP Address' in seedObj:
                itSeed.ip_address = seedObj['IP Address'] 
            if 'Application Name' in seedObj:
                itSeed.application_name = seedObj['Application Name'] 
            if 'Owner Email' in seedObj:
                itSeed.owner_email = seedObj['Owner Email'] 
            if 'Owner Contact' in seedObj:
                itSeed.owner_contact = seedObj['Owner Contact'] 

            #try:
            if EDN_IT_Seed.query.with_entities(EDN_IT_Seed.edn_it_seed_id).filter_by(ip_address=seedObj['IP Address']).first() is not None:
                itSeed.edn_it_seed_id = EDN_IT_Seed.query.with_entities(EDN_IT_Seed.edn_it_seed_id).filter_by(ip_address=seedObj['IP Address']).first()[0]
                print("Updated " + seedObj['IP Address'],file=sys.stderr)
                UpdateData(itSeed)
            else:
                print("Inserted " +seedObj['IP Address'],file=sys.stderr)
                InsertData(itSeed)
            #except:
            #    print("Some error occured skipping",file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addEdnMaster", methods = ['POST'])
@token_required
def AddEdnMaster(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()
        current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        
        #print(postData,file=sys.stderr)
        
        for seedObj in postData:

            print(seedObj,file=sys.stderr)

            master = EDN_Mapping()

            if 'Region' in seedObj:
                master.region = seedObj['Region']
            if 'Segment' in seedObj:
                master.segment = seedObj['Segment']
            if 'Switch Name' in seedObj:
                master.switch_id = seedObj['Switch Name']
            if 'MAC Address' in seedObj:
                master.mac_address = seedObj['MAC Address']
            if 'Switch Interface' in seedObj:
                master.switch_interface = seedObj['Switch Interface']
            if 'Interface Description' in seedObj:
                master.interface_description = seedObj['Interface Description']
            if 'VLAN' in seedObj:
                master.vlan = seedObj['VLAN']
            if 'Server Name' in seedObj:
                master.server_name = seedObj['Server Name']
            if 'IP Address' in seedObj:
                master.ip_address = seedObj['IP Address']
            if 'Application Name' in seedObj:
                master.application_name = seedObj['Application Name']
            if 'Owner Email' in seedObj:
                master.owner_email = seedObj['Owner Email']
            if 'Owner Contact' in seedObj:
                master.owner_contact = seedObj['Owner Contact']    

            master.creation_date = current_time
            master. modification_date = current_time

            #queryString = "SELECT edn_id FROM edn_mapping WHERE creation_date = \'"+current_time+"\' AND mac_address = \'"+master.mac_address+"\'"
            #data = db.session.execute(queryString)
            #print(queryString,file=sys.stderr)
            #for obj in data:
            #   print(obj,file=sys.stderr)
            
            #data = EDN_Mapping.query.with_entities(EDN_Mapping.edn_id).filter(EDN_Mapping.creation_date==current_time, EDN_Mapping.mac_address==master.mac_address)
            #print(data,file=sys.stderr)

            if EDN_Mapping.query.with_entities(EDN_Mapping.edn_id).filter_by(creation_date=current_time).filter_by(mac_address=master.mac_address).first() is not None:
                master.seed_id = EDN_Mapping.query.with_entities(EDN_Mapping.edn_id).filter_by(creation_date=current_time).filter_by(mac_address=master.mac_address).first()[0]
                print("Updated " + master.mac_address,file=sys.stderr)
                UpdateData(master)
            else:
                print("Inserted " + master.mac_address,file=sys.stderr)
                InsertData(master) 
                
        
        return jsonify({'response': "success","code":"200"})

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
 
@app.route("/exportEdnMaster", methods = ['GET'])
@token_required
def ExportEdnMaster(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednObjList=[]
        data = db.session.execute('SELECT * FROM edn_mapping WHERE creation_date = (SELECT max(creation_date) FROM edn_mapping)')
        for obj in data:
            #print(obj[1],file=sys.stderr)
            ednDataDict= {}

            ednDataDict['Region'] = obj[1]
            ednDataDict['Segment'] = obj[2]
            ednDataDict['Switch Name'] = obj[3]
            ednDataDict['MAC Address'] = obj[4]
            ednDataDict['Switch Interface'] = obj[5]
            ednDataDict['Interface Description'] = obj[6]
            ednDataDict['VLAN'] = obj[7]
            ednDataDict['Server Name'] = obj[10]
            ednDataDict['IP Address'] = obj[11]
            ednDataDict['Application Name'] = obj[12]
            ednDataDict['Owner Email'] = obj[13]
            ednDataDict['Owner Contact'] = obj[14]

            ednObjList.append(ednDataDict)

        # df = pd.DataFrame(ednObjList)
        
        # df.to_excel('ExportEDN.xlsx')
        
        return jsonify(ednObjList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllEdnMaster", methods = ['GET'])
@token_required
def GetAllEdnMaster(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ednObjList=[]
        data = db.session.execute('SELECT * FROM edn_mapping WHERE creation_date = (SELECT max(creation_date) FROM edn_mapping)')
        
        for obj in data:
            
            ednDataDict= {}

            ednDataDict['Region'] = obj[1]
            ednDataDict['Segment'] = obj[2]
            ednDataDict['Switch Name'] = obj[3]
            ednDataDict['MAC Address'] = obj[4]
            ednDataDict['Switch Interface'] = obj[5]
            ednDataDict['Interface Description'] = obj[6]
            ednDataDict['VLAN'] = obj[7]
            ednDataDict['Server Name'] = obj[10]
            ednDataDict['IP Address'] = obj[11]
            ednDataDict['Application Name'] = obj[12]
            ednDataDict['Owner Email'] = obj[13]
            ednDataDict['Owner Contact'] = obj[14]

            ednObjList.append(ednDataDict)
        
        print(ednObjList,file=sys.stderr)

        
        content = gzip.compress(json.dumps(ednObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/fetchEdnData", methods = ['GET'])
@token_required
def FetchEdnData(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        objDictList = []
        secobjDictList = []
        current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        print('Started at: '+current_time, file=sys.stderr)
        ednNetObjs = EDN_NET_Seed.query.all()
        
        with open('app/cred.json','r') as cred:
            fw_cred = json.loads(cred.read())
        for ednNet in ednNetObjs:
            objDict = {}
            objDict['host'] = ednNet.switch_ip_address
            objDict['sw_type'] = ednNet.os_type
            objDict['user']= fw_cred['EDN']['user']
            objDict['pwd']= fw_cred['EDN']['pwd']
            
            objDictList.append(objDict)

        pullerService = ServicePuller()
        pullerResp = pullerService.get_address_table_data(objDictList)
        
        ednSecObjs = EDN_SEC_Seed.query.all()
        
        for ednSec in ednSecObjs:
            secobjDict = {}
            secobjDict['host'] = ednSec.fw_ip_address
            secobjDict['sw_type'] = ednSec.os_type
            secobjDict['user']= fw_cred['FW']['user']
            secobjDict['pwd']= fw_cred['FW']['pwd']
            secobjDictList.append(secobjDict)
            
        fwpullerService = FWPuller()
        fwpullerResp = fwpullerService.get_arp_table(secobjDictList)
        
        for secIP in fwpullerResp:
            for sec_mac in fwpullerResp[secIP]['arp-table']:
                for respIp in pullerResp:
                    print(respIp, file=sys.stderr)
                    netSeed = db.session.query(EDN_NET_Seed).filter_by(switch_ip_address=respIp).first()
                    for ip in pullerResp[respIp]:
                        for mac in pullerResp[respIp]['address-table']:
                            #print(mac, file=sys.stderr)
                            sec_mac_address=sec_mac['mac'].replace(':','').replace('.','')
                            net_mac_address=mac['MAC Address'].replace(':','').replace('.','')
                            print(f'sec_mac={sec_mac_address} and net_mac={net_mac_address}', file=sys.stderr)
                            if sec_mac_address == net_mac_address:
                                master = EDN_Mapping()

                                master.region = netSeed.region
                                master.segment = netSeed.segment
                                master.switch_id =netSeed.switch_id
                                master.mac_address = mac['MAC Address']
                                master.switch_interface = mac['Switch Interface']
                                master.interface_description = mac['Interface Description']
                                master.vlan = mac['Vlan']
                                master.ip_address = sec_mac['ip_address']

                                master.creation_date = current_time
                                master. modification_date = current_time
                                
                                #master.server_name = 
                                #master.application_name= 
                                #master.owner_email= 
                                #master.owner_contact = 

                                InsertData(master)
                                print("Inserted " + master.mac_address,file=sys.stderr)

        return jsonify("Success"), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteEdnSecSeed",methods = ['POST'])
@token_required
def DeleteEdnSecSeed(user_data):
    if True:#session.get('token', None):
        ednSecObj = request.get_json()
        print(ednSecObj,file = sys.stderr)
        
        for obj in ednSecObj.get("ips"):
            ednSecIp = EDN_SEC_Seed.query.filter(EDN_SEC_Seed.fw_ip_address==obj).first()
            print(ednSecIp,file=sys.stderr)
            if obj:
                db.session.delete(ednSecIp)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllSecIps", methods = ['GET'])
@token_required
def GetAllSecIps(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        secIpsList=[]
        secObjs = EDN_SEC_Seed.query.all()

        #print(type(secObj.creation_date), file=sys.stderr)

        for secObj in secObjs:

            secDataDict= {}
            secDataDict['edn_sec_seed_id'] = secObj.edn_sec_seed_id
            secDataDict['region'] = secObj.region
            secDataDict['segment'] = secObj.segment
            secDataDict['fw_id'] = secObj.fw_id
            secDataDict['fw_ip_address'] = secObj.fw_ip_address
            secDataDict['vendor'] = secObj.vendor
            secDataDict['creation_date'] = secObj.creation_date
            secDataDict['modification_date'] = secObj.modification_date
            secDataDict['os_type'] = secObj.os_type
            

            #print(type(secObj.creation_date), file=sys.stderr)

            secIpsList.append(secDataDict)

        return jsonify(secIpsList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteEdnNetSeed",methods = ['POST'])
@token_required
def DeleteEdnNetSeed(user_data):
    if True:#session.get('token', None):
        ednNetObj = request.get_json()
        print(ednNetObj,file = sys.stderr)
        
        for obj in ednNetObj.get("ips"):
            ednNetIp = EDN_NET_Seed.query.filter(EDN_NET_Seed.switch_ip_address==obj).first()
            print(ednNetIp,file=sys.stderr)
            if obj:
                db.session.delete(ednNetIp)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllNeIps", methods = ['GET'])
@token_required
def GetAllNeIps(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        neIpsList=[]
        neObjs = EDN_NET_Seed.query.all()

        print(len(neObjs), file=sys.stderr)


        for neObj in neObjs:

            neDataDict= {}
            neDataDict['edn_net_seed_id'] = neObj.edn_net_seed_id
            neDataDict['region'] = neObj.region
            neDataDict['segment'] = neObj.segment
            neDataDict['switch_id'] = neObj.switch_id
            neDataDict['switch_ip_address'] = neObj.switch_ip_address
            neDataDict['vendor'] = neObj.vendor
            neDataDict['creation_date'] = neObj.creation_date
            neDataDict['modification_date'] = neObj.modification_date
            neDataDict['os_type'] = neObj.os_type
            

            #print(type(neObj.creation_date), file=sys.stderr)

            neIpsList.append(neDataDict)

        return jsonify(neIpsList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllItIps", methods = ['GET'])
@token_required
def GetAllItIps(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        itIpsList=[]
        itObjs = EDN_IT_Seed.query.all()

        for itObj in itObjs:

            itDataDict= {}
            itDataDict['edn_it_seed_id'] = itObj.edn_it_seed_id
            itDataDict['server_name'] = itObj.server_name
            itDataDict['ip_address'] = itObj.ip_address
            itDataDict['application_name'] = itObj.application_name
            itDataDict['owner_email'] = itObj.owner_email
            itDataDict['owner_contact'] = itObj.owner_contact
            itDataDict['creation_date'] = itObj.creation_date
            itDataDict['modification_date'] = itObj.modification_date
            

            #print(type(itObj.creation_date), file=sys.stderr)

            itIpsList.append(itDataDict)

        return jsonify(itIpsList), 200
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/showEDNInventoryData", methods = ['POST'])
@token_required
def ShowEDNInventoryData(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()
        #print(postData,file=sys.stderr)

        ip = postData['ip']
        type = postData['type']

        deviceDataDict = {}

        deviceObj = db.session.query(Device_Table).filter_by(ne_ip_address=ip).first()

        #print(deviceObj,file=sys.stderr)
        if deviceObj is not None:

            deviceDataDict['device_id'] = deviceObj.device_id
            deviceDataDict['site_id'] = deviceObj.site_id
            deviceDataDict['rack_id'] = deviceObj.rack_id
            deviceDataDict['ne_ip_address'] = deviceObj.ne_ip_address
            deviceDataDict['software_version'] = deviceObj.software_version
            deviceDataDict['patch_version'] = deviceObj.patch_version
            deviceDataDict['creation_date'] = deviceObj.creation_date
            deviceDataDict['modification_date'] = deviceObj.modification_date
            deviceDataDict['status'] = deviceObj.status
            deviceDataDict['ru'] = deviceObj.ru
            deviceDataDict['department'] = deviceObj.department
            deviceDataDict['section'] = deviceObj.section
            deviceDataDict['criticality'] = deviceObj.criticality
            deviceDataDict['function'] = deviceObj.function
            deviceDataDict['cisco_domain'] = deviceObj.cisco_domain
            deviceDataDict['manufacturer'] = deviceObj.manufacturer
            deviceDataDict['hw_eos_date'] = deviceObj.hw_eos_date
            deviceDataDict['hw_eol_date'] = deviceObj.hw_eol_date
            deviceDataDict['sw_eos_date'] = deviceObj.sw_eos_date
            deviceDataDict['sw_eol_date'] = deviceObj.sw_eol_date
            deviceDataDict['virtual'] = deviceObj.virtual
            deviceDataDict['rfs_date'] = deviceObj.rfs_date
            deviceDataDict['authentication'] = deviceObj.authentication
            deviceDataDict['serial_number'] = deviceObj.serial_number
            deviceDataDict['pn_code'] = deviceObj.pn_code
            deviceDataDict['tag_id'] = deviceObj.tag_id
            deviceDataDict['subrack_id_number'] = deviceObj.subrack_id_number
            deviceDataDict['manufactuer_date'] = deviceObj.manufactuer_date
            deviceDataDict['hardware_version'] = deviceObj.hardware_version
            deviceDataDict['max_power'] = deviceObj.max_power
            
            return deviceDataDict, 200
    
        else:
            return {"msg": "No Data"}, 200
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addNeDevice", methods = ['POST'])
@token_required
def AddNeDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        seedObj = request.get_json()

        print(seedObj,file=sys.stderr)

        netSeed = EDN_NET_Seed()
        if 'region' in seedObj:
            netSeed.region = seedObj['region'] 
        if 'segment' in seedObj:
            netSeed.segment = seedObj['segment'] 
        if 'switch_id' in seedObj:
            netSeed.switch_id = seedObj['switch_id'] 
        if 'switch_ip_address' in seedObj:
            netSeed.switch_ip_address = seedObj['switch_ip_address'] 
        if 'vendor' in seedObj:
            netSeed.vendor = seedObj['vendor'] 
        if 'os_type' in seedObj:
            netSeed.os_type = seedObj['os_type']    
        try:
            if EDN_NET_Seed.query.with_entities(EDN_NET_Seed.edn_net_seed_id).filter_by(switch_ip_address=seedObj['switch_ip_address']).first() is not None:
                netSeed.edn_net_seed_id = EDN_NET_Seed.query.with_entities(EDN_NET_Seed.edn_net_seed_id).filter_by(switch_ip_address=seedObj['switch_ip_address']).first()[0]
                print("Updated " + seedObj['switch_ip_address'],file=sys.stderr)
                UpdateData(netSeed)
            else:
                print("Inserted " +seedObj['switch_ip_address'],file=sys.stderr)
                InsertData(netSeed)
        except:
            print("Some error occured skipping",file=sys.stderr)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addSecDevice", methods = ['POST'])
@token_required
def AddSecDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        seedObj = request.get_json()

        print(seedObj,file=sys.stderr)

        secSeed = EDN_SEC_Seed()
        if 'region' in seedObj:
            secSeed.region = seedObj['region'] 
        if 'segment' in seedObj:
            secSeed.segment = seedObj['segment'] 
        if 'fw_id' in seedObj:
            secSeed.fw_id = seedObj['fw_id'] 
        if 'fw_ip_address' in seedObj:
            secSeed.fw_ip_address = seedObj['fw_ip_address'] 
        if 'vendor' in seedObj:
            secSeed.vendor = seedObj['vendor'] 
        if 'os_type' in seedObj:
            secSeed.os_type = seedObj['os_type']    
        try:
            if EDN_SEC_Seed.query.with_entities(EDN_SEC_Seed.edn_sec_seed_id).filter_by(fw_ip_address=seedObj['fw_ip_address']).first() is not None:
                secSeed.edn_sec_seed_id = EDN_SEC_Seed.query.with_entities(EDN_SEC_Seed.edn_sec_seed_id).filter_by(fw_ip_address=seedObj['fw_ip_address']).first()[0]
                print("Updated " + seedObj['fw_ip_address'],file=sys.stderr)
                UpdateData(secSeed)
            else:
                print("Inserted " +seedObj['fw_ip_address'],file=sys.stderr)
                InsertData(secSeed)
        except:
                    print("Some error occured skipping",file=sys.stderr)

        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addItDevice", methods = ['POST'])
@token_required
def AddItDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        seedObj = request.get_json()

        print(seedObj,file=sys.stderr)

        itSeed = EDN_IT_Seed()
        if 'server_name' in seedObj:
            itSeed.server_name = seedObj['server_name'] 
        if 'ip_address' in seedObj:
            itSeed.ip_address = seedObj['ip_address'] 
        if 'application_name' in seedObj:
            itSeed.application_name = seedObj['application_name'] 
        if 'owner_email' in seedObj:
            itSeed.owner_email = seedObj['owner_email'] 
        if 'owner_contact' in seedObj:
            itSeed.owner_contact = seedObj['owner_contact'] 

        try:
            if EDN_IT_Seed.query.with_entities(EDN_IT_Seed.edn_it_seed_id).filter_by(ip_address=seedObj['ip_address']).first() is not None:
                itSeed.edn_it_seed_id = EDN_IT_Seed.query.with_entities(EDN_IT_Seed.edn_it_seed_id).filter_by(ip_address=seedObj['ip_address']).first()[0]
                print("Updated " + seedObj['ip_address'],file=sys.stderr)
                UpdateData(itSeed)
            else:
                print("Inserted " +seedObj['ip_address'],file=sys.stderr)
                InsertData(itSeed)
        except:
            print("Some error occured skipping",file=sys.stderr)
                    
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/addEdnServiceMapping", methods = ['GET'])
@token_required
def AddEdnServiceMapping(user_data):
    try:
        serviceMapping= AddServiceMapping()
        
        serviceMapping.AddEdnServiceMappingFunc()
        
        return ""
    except Exception as e:
        print("Exception occured in syncing EDN Services", file=sys.stderr)
    return "Success", 200

