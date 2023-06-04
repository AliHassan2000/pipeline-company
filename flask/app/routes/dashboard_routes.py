import sys, json
from flask_jsonpify import jsonify
from flask import Flask, request, make_response, Response, session
from app import app ,db , tz
from app.models.inventory_models import Phy_Table, Rack_Table, Device_Table, Board_Table, Subboard_Table, SFP_Table, License_Table, Seed, SNTC_Table,CDN_Table
from sqlalchemy import func
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask_cors import CORS, cross_origin
from app.middleware import token_required

def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%d-%m-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

@app.route("/getChart", methods = ['GET'])
@token_required
def getChart(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        resp = {}

        resp['Total-IGW'] = db.session.query(Seed).filter_by(cisco_domain='IGW-NET').count()
        resp['Total-EDN'] = db.session.query(Seed).filter_by(cisco_domain='EDN-NET').count()
        resp['Total-System'] = db.session.query(Seed).filter_by(cisco_domain='SYS').count()
        resp['Total-IPT'] = db.session.query(Seed).filter_by(cisco_domain='EDN-IPT').count()
        resp['Total-AP'] = db.session.query(Seed).filter_by(cisco_domain='AP').count()
        resp['Total-Security'] = db.session.query(Seed).filter_by(cisco_domain='Security').count()

        resp['IGW'] = db.session.query(Device_Table).filter_by(cisco_domain='IGW-NET').count()
        resp['EDN'] = db.session.query(Device_Table).filter_by(cisco_domain='EDN-NET').count()
        resp['System'] = db.session.query(Device_Table).filter_by(department='SYS').count()
        resp['IPT'] = db.session.query(Device_Table).filter_by(cisco_domain='EDN-IPT').count()
        resp['AP'] = db.session.query(Device_Table).filter_by(cisco_domain='AP').count()
        resp['Security'] = db.session.query(Device_Table).filter_by(cisco_domain='Security').count()

        print(resp, file=sys.stderr)

        return resp, 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getChartDetail", methods = ['POST'])
@token_required
def getChartDetail(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        deviceObjList = []
        data = request.get_json()
        #data = {'key' : 'IGW'}
        if data['key'] == 'EDN':
            key = 'EDN-NET'
        elif data['key'] == 'IGW':
            key = 'IGW-NET'
        elif data['key'] == 'System':
            key = 'SYS'
        elif data['key'] == 'IGW System':
            key = 'IGW-SYS'
        elif data['key'] == 'EDN System':
            key = 'EDN-SYS'
        elif data['key'] == 'IPT':
            key = 'EDN-IPT'
        elif data['key'] == 'IPT-Endpoints':
            key = 'EDN-IPT-Endpoints'
        elif data['key'] == 'Security':
            key = 'Security'
        else:
            key = 'N/A'
            

        print(data['key'], file=sys.stderr)
        
        deviceObjs = db.session.query(Device_Table).filter_by(cisco_domain=key).filter_by(status='Production').all()

        for deviceObj in deviceObjs:
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
            deviceDataDict['ru'] = deviceObj.ru
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

            deviceDataDict['site_name'] = Phy_Table.query.with_entities(Phy_Table.site_name).filter_by(site_id=deviceObj.site_id).first()[0]
            deviceDataDict['rack_name'] = Rack_Table.query.with_entities(Rack_Table.rack_name).filter_by(rack_id=deviceObj.rack_id).first()[0]
            
        
            deviceObjList.append(deviceDataDict)
        
        return jsonify(deviceObjList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/ciscoDomains", methods = ['GET'])
@token_required
def CiscoDomains(user_data):
    if True:
    #if session.get('token', None):
        objList = []

        # servers = db.session.query(func.count(Device_Table.cisco_domain).label('total_cisco_domain'), Device_Table.cisco_domain).filter_by(status='Production').group_by(Device_Table.cisco_domain).all()

        # for server in servers:
            #print(server.cisco_domain, server.total_cisco_domain, file=sys.stderr)

            # if server.cisco_domain == 'IGW-NET':
        device_count = db.session.execute("select coalesce(sum(STACK),0) from device_table where cisco_domain = 'IGW-NET' and status = 'Production';").scalar()
        dict = {}
        dict['name'] = 'IGW-NET'
        dict['value']=int(device_count)
        #dict['value'] = 186
        #dict['value'] = server.total_cisco_domain
        objList.append(dict)

            # if server.cisco_domain == 'EDN-NET':
        device_count = db.session.execute("select coalesce(sum(stack),0) from device_table where cisco_domain = 'EDN-NET' and status = 'Production';").scalar()
        
        dict = {}
        dict['name'] = 'EDN-NET'
        dict['value'] = int(device_count)
        #dict['value'] = server.total_cisco_domain
        #dict['value'] = 2154
        objList.append(dict)

            # if server.cisco_domain == 'IGW-SYS':
        device_count = db.session.execute("select coalesce(sum(stack),0) from device_table where cisco_domain = 'IGW-SYS' and status = 'Production';").scalar()
        dict = {}
        dict['name'] = 'IGW-SYS'
        dict['value'] = int(device_count)
        #dict['value'] = 463
        objList.append(dict)
    
            # if server.cisco_domain == 'EDN-SYS':
        device_count = db.session.execute("select coalesce(sum(stack),0) from device_table where cisco_domain = 'EDN-SYS' and status = 'Production';").scalar()
        dict = {}
        dict['name'] = 'EDN-SYS'
        dict['value'] = int(device_count)
        #dict['value'] = 463
        objList.append(dict)

            # if server.cisco_domain == 'EDN-IPT':
        device_count = db.session.execute("select coalesce(sum(stack),0) from device_table where cisco_domain = 'EDN-IPT' and status = 'Production';").scalar()
        dict = {}
        dict['name'] = 'EDN-IPT'
        dict['value'] = int(device_count)
        objList.append(dict)

            # if server.cisco_domain == 'Security':
        device_count = db.session.execute("select coalesce(sum(stack),0) from device_table where cisco_domain = 'SOC' and status = 'Production';").scalar()
        dict = {}
        dict['name'] = 'SOC'
        dict['value'] = int(device_count)
        objList.append(dict)
            
            # if server.cisco_domain == 'EDN-IPT-Endpoints':
            #     dict = {}
            #     dict['name'] = 'IPT-Endpoints'
            #     dict['value'] = server.total_cisco_domain
            #     objList.append(dict)


        dict = {}
        dict['name'] = 'CDN'
        dict['value'] = int(db.session.execute("select sum(COUNT) from cdn_table;").scalar())
        objList.append(dict)
        posCount = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where operation_status='Production';").scalar()
        dict1 = {}
        dict1['name']= 'POS'
        dict1['value']=int(posCount)
        
        objList.append(dict1)
        rebdCount = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where operation_status='Production';").scalar()
        dict2 = {}
        dict2['name']= 'REBD'
        dict2['value']=int(rebdCount)
        objList.append(dict2)
        print(objList,file=sys.stderr)
        return jsonify(objList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/inventoryCounts", methods = ['GET'])
@token_required
def InventoryCounts(user_data):
    #if request.headers.get('X-Auth-Key') == session.get('token', None):
    if True:
    #if session.get('token', None):
        objList = []

        phy_count = db.session.execute("select count(SITE_ID) from phy_table where STATUS='Production';").scalar() 
        dict =  {}
        dict['name']= "Sites"
        dict['value'] = phy_count
        objList.append(dict)

        rack_count = db.session.execute("select count(RACK_ID) from rack_table where STATUS='Production';").scalar() 
        dict =  {}
        dict['name']= "Racks"
        dict['value'] = rack_count
        objList.append(dict)

        device_count = db.session.execute("select coalesce(sum(STACK),0) from device_table where status='Production';").scalar()
        dict =  {}
        dict['name']= "Devices"
        posCount = db.session.execute(f"select coalesce(sum(stack),0) from pos_table where OPERATION_STATUS='Production';").scalar()
        rebdCount = db.session.execute(f"select coalesce(sum(stack),0) from rebd_table where OPERATION_STATUS='Production';").scalar()
        #dict['value'] = str(device_count + 577)
        #dict['value'] = int(db.session.execute("select sum(COUNT) from cdn_table;").scalar())
        cdnCount = db.session.execute("select coalesce(sum(COUNT),0) from cdn_table;").scalar()
        dict['value']=int(device_count) + int(cdnCount)+int(posCount)+int(rebdCount)

        # #dict['value'] = "5993" 
        objList.append(dict)

        #board_count = db.session.query(func.count(Board_Table.board_id)).scalar() 
        board_count = db.session.execute("select count(*) from board_table where status='Production';").scalar()
        dict =  {}
        dict['name']= "Boards"
        dict['value'] = board_count
        objList.append(dict)

        #subboard_count = db.session.query(func.count(Subboard_Table.subboard_id)).scalar() 
        subboard_count = db.session.execute("select count(*) from subboard_table where status='Production';").scalar()
        dict =  {}
        dict['name']= "Sub Boards"
        dict['value'] = subboard_count
        objList.append(dict)

        #sfp_count = db.session.query(func.count(SFP_Table.sfp_id)).scalar() 
        sfp_count = db.session.execute("select count(*) from sfp_table where status='Production';").scalar()
        dict =  {}
        dict['name']= "SFPs"
        dict['value'] = sfp_count
        objList.append(dict)

        #license_count = db.session.query(func.count(License_Table.license_id)).scalar() 
        # license_count = db.session.execute("select count(*) from license_table where status='Production';").scalar()
        # dict =  {}
        # dict['name']= "Licenses"
        # dict['value'] = license_count
        # objList.append(dict)

        jabber_count = db.session.execute("select count(*) from ipt_endpoints_table where (hostname like 'CSF%' or  hostname like 'BOT%' or  hostname like 'TAB%' or  hostname like 'TCT%') and status='Registered' ;").scalar()
        phones_count = db.session.execute("select count(*) from ipt_endpoints_table where hostname like 'SEP%'and status='Registered';").scalar()
        dict =  {}
        dict['name']= "Jabber / Phones"
        dict['value'] = str(jabber_count)+ " / "+str(phones_count)
        objList.append(dict)
        '''
        phones_count = db.session.execute("select count(*) from ipt_endpoints_table where hostname like 'SEP%'and status='Registered';").scalar()
        dict =  {}
        dict['name']= "Phones"
        dict['value'] = phones_count
        objList.append(dict)
        '''
        return jsonify(objList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/totalDeviceFunctions", methods = ['GET'])
@token_required
def TotalDeviceFunctions(user_data):
    #if request.headers.get('X-Auth-Key') == session.get('token', None):
    if True:#session.get('token', None):
        ###IGW
        aci_string = "select count(`FUNCTION`) from device_table where `FUNCTION` not like '%ROUTER%' and CISCO_DOMAIN = 'IGW-NET' and status='Production';"
        igw_aci_count = db.session.execute(aci_string).scalar()
        
        igw_router_string = "select count(`FUNCTION`) from device_table where `FUNCTION` like '%ROUTER%' and CISCO_DOMAIN = 'IGW-NET' and status='Production';"
        igw_router_count = db.session.execute(igw_router_string).scalar()

        #EDN
        edn_router_string = "select count(`FUNCTION`) from device_table where `FUNCTION` like '%ROUTER%' and CISCO_DOMAIN = 'EDN-NET' and status='Production';"
        edn_router_count = db.session.execute(edn_router_string).scalar()

        edn_switch_string = "select count(`FUNCTION`) from device_table where `FUNCTION` like '%SWITCH%' and CISCO_DOMAIN = 'EDN-NET' and status='Production';"
        edn_switch_count = db.session.execute(edn_switch_string).scalar() + 2

        edn_aci_string = "select count(`FUNCTION`) from device_table where `FUNCTION` like '%ACI%' and CISCO_DOMAIN = 'EDN-NET' and status='Production';"
        edn_aci_count = db.session.execute(edn_aci_string).scalar()
        
        edn_server_string = "select count(`FUNCTION`)  from device_table where `FUNCTION` like 'PRIME' or `FUNCTION` like 'UCS'  and cisco_domain = 'EDN-NET' and status='Production';"
        edn_server_count = db.session.execute(edn_server_string).scalar()
        
        edn_otv_router_string = "select count(`FUNCTION`)  from device_table where `FUNCTION` like '%OTV-RTR%' and cisco_domain = 'EDN-NET' and status='Production';"
        edn_otv_router_count = db.session.execute(edn_otv_router_string).scalar()
        
        #IPT
        ipt_server_string = "select count(`FUNCTION`) from device_table where `FUNCTION` not like '%ROUTER%' and cisco_domain = 'EDN-IPT' and status='Production';"
        ipt_server_count = db.session.execute(ipt_server_string).scalar()

        ipt_router_string = "select count(`FUNCTION`) from device_table where `FUNCTION` like '%ROUTER%' and cisco_domain = 'EDN-IPT' and status='Production';"
        ipt_router_count = db.session.execute(ipt_router_string).scalar()
        
        #System
        sys_server_string = "select count(`FUNCTION`) from device_table where  cisco_domain = 'SYS' and status='Production';"
        sys_server_count = db.session.execute(sys_server_string).scalar()

        #Security
        sec_firewall_string = "select count(`FUNCTION`) from device_table where `FUNCTION` like '%Firewall%' and  cisco_domain = 'Security' and status='Production';"
        sec_firewall_count = db.session.execute(sec_firewall_string).scalar()

        sec_secSer_string = "select count(`FUNCTION`) from device_table where `FUNCTION`not like '%Firewall%' and  cisco_domain = 'Security' and status='Production';"
        sec_secServer_count = db.session.execute(sec_secSer_string).scalar()

        edn_ipt_endpoints_string = "select count(cisco_domain) from device_table where cisco_domain = 'EDN-IPT-Endpoints' and status='Production';"
        edn_ipt_endpoints__count = db.session.execute(edn_ipt_endpoints_string).scalar()

        firewall  = sec_firewall_count
        security_server = sec_secServer_count
        aci =  igw_aci_count + edn_aci_count
        switch = edn_switch_count
        router = igw_router_count + edn_router_count + edn_otv_router_count + ipt_router_count
        server = edn_server_count + ipt_server_count + sys_server_count


        #print(sec_firewall_count + sec_secServer_count + igw_aci_count + edn_aci_count + edn_switch_count + igw_router_count + edn_router_count + edn_otv_router_count + ipt_router_count + edn_server_count + ipt_server_count + sys_server_count, file=sys.stderr)
        
        # objDict = {
        #             "total_site": 525,
        #             "firewall": 3000,
        #             "security_server":4000,
        #             "aci":3700,
        #             "switch":4000,
        #             "router":3700,
        #             "server":4000,
        #         }
        #total_devices = firewall + security_server + aci + switch + router + server

        total_devices= db.session.execute("select sum(stack) from device_table where status='Production';").scalar()
        
        objDict = {}
        #objDict["total_devices"]= str(total_devices+577)
        #objDict["total_devices"]= 5993
        objDict["firewall"] = firewall
        objDict["security_server"] = security_server
        objDict["aci"] = aci
        objDict["switch"] = switch
        objDict["router"] = router
        objDict["server"] =  server
        objDict["edn_ipt_endpoints"] = edn_ipt_endpoints__count

        return objDict, 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deviceFunctions", methods = ['GET'])
@token_required
def DeviceFunctions(user_data):
    #if request.headers.get('X-Auth-Key') == session.get('token', None):
    if True:#session.get('token', None):
        objList = []

        query_string = "select site_id ,count(site_id) from device_table where status='Production' group by site_id order by count(site_id) desc limit 4;"
        result = db.session.execute(query_string)
        for row in result:
            print(row[0], row[1], file=sys.stderr)
            site_name = row[0]
            count = row[1]
            if site_name=='N/A':
                continue
            aci_string = f"select count(`FUNCTION`) from device_table where `FUNCTION` not like '%ROUTER%' and CISCO_DOMAIN = 'IGW-NET' and status='Production' and site_id = \'{site_name}\';"
            igw_aci_count = db.session.execute(aci_string).scalar()
            
            igw_router_string = f"select count(`FUNCTION`) from device_table where `FUNCTION` like '%ROUTER%' and CISCO_DOMAIN = 'IGW-NET' and status='Production' and site_id = \'{site_name}\';"
            igw_router_count = db.session.execute(igw_router_string).scalar()

            #EDN
            edn_router_string = f"select count(`FUNCTION`) from device_table where `FUNCTION` like '%ROUTER%' and CISCO_DOMAIN = 'EDN-NET' and status='Production' and site_id = \'{site_name}\';"
            edn_router_count = db.session.execute(edn_router_string).scalar()

            edn_switch_string = f"select count(`FUNCTION`) from device_table where `FUNCTION` like '%SWITCH%' and CISCO_DOMAIN = 'EDN-NET' and status='Production' and site_id = \'{site_name}\';"
            edn_switch_count = db.session.execute(edn_switch_string).scalar() + 2

            edn_aci_string = f"select count(`FUNCTION`) from device_table where `FUNCTION` like '%ACI%' and CISCO_DOMAIN = 'EDN-NET' and status='Production' and site_id = \'{site_name}\';"
            edn_aci_count = db.session.execute(edn_aci_string).scalar()
            
            edn_server_string = f"select count(`FUNCTION`)  from device_table where `FUNCTION` like 'PRIME' or `FUNCTION` like 'UCS'  and cisco_domain = 'EDN-NET' and status='Production' and site_id = \'{site_name}\';"
            edn_server_count = db.session.execute(edn_server_string).scalar()
            
            edn_otv_router_string = f"select count(`FUNCTION`)  from device_table where `FUNCTION` like '%OTV-RTR%' and cisco_domain = 'EDN-NET' and status='Production' and site_id = \'{site_name}\';"
            edn_otv_router_count = db.session.execute(edn_otv_router_string).scalar()
            
            #IPT
            ipt_server_string = f"select count(`FUNCTION`) from device_table where `FUNCTION` not like '%ROUTER%' and cisco_domain = 'EDN-IPT' and status='Production' and site_id = \'{site_name}\';"
            ipt_server_count = db.session.execute(ipt_server_string).scalar()

            ipt_router_string = f"select count(`FUNCTION`) from device_table where `FUNCTION` like '%ROUTER%' and cisco_domain = 'EDN-IPT' and status='Production' and site_id = \'{site_name}\';"
            ipt_router_count = db.session.execute(ipt_router_string).scalar()
            
            #System
            sys_server_string = f"select count(`FUNCTION`) from device_table where  cisco_domain = 'SYS' and status='Production' and site_id = \'{site_name}\';"
            sys_server_count = db.session.execute(sys_server_string).scalar()

            #Security
            sec_firewall_string = f"select count(`FUNCTION`) from device_table where `FUNCTION` like '%Firewall%' and  cisco_domain = 'Security' and status='Production' and site_id = \'{site_name}\';"
            sec_firewall_count = db.session.execute(sec_firewall_string).scalar()

            sec_secSer_string = f"select count(`FUNCTION`) from device_table where `FUNCTION`not like '%Firewall%' and  cisco_domain = 'Security' and status='Production' and site_id = \'{site_name}\';"
            sec_secServer_count = db.session.execute(sec_secSer_string).scalar()

            firewall  = sec_firewall_count
            security_server = sec_secServer_count
            aci =  igw_aci_count + edn_aci_count
            switch = edn_switch_count
            router = igw_router_count + edn_router_count + edn_otv_router_count + ipt_router_count
            server = edn_server_count + ipt_server_count + sys_server_count

            total_sites = firewall + security_server + aci + switch + router + server

            objDict = {}
            objDict['site_name'] = site_name
            objDict['device_count'] = count
            objDict["total_site"]= count
            objDict["firewall"] = firewall
            objDict["security_server"] = security_server
            objDict["aci"] = aci
            objDict["switch"] = switch
            objDict["router"] = router
            objDict["server"] =  server

            objList.append(objDict)

            #print(objDict, file=sys.stderr)

        return jsonify(objList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/onboardedDevicesPerMonth", methods = ['GET'])
@token_required
def OnBoardDevicePerMonth(user_data):
    #if request.headers.get('X-Auth-Key') == session.get('token', None):
    current_date = datetime.today()

    date_1 = (current_date - relativedelta(months=0)).strftime('%Y-%m')
    print(date_1, file=sys.stderr)

    date_2 = (current_date - relativedelta(months=1)).strftime('%Y-%m')
    print(date_2, file=sys.stderr)

    date_3 = (current_date - relativedelta(months=2)).strftime('%Y-%m')
    print(date_3, file=sys.stderr)

    date_4 = (current_date - relativedelta(months=3)).strftime('%Y-%m')
    print(date_4, file=sys.stderr)

    date_5 = (current_date - relativedelta(months =4)).strftime('%Y-%m')
    print(date_5,file=sys.stderr)
    
    date_6 = (current_date - relativedelta(months =5)).strftime('%Y-%m')
    print(date_6,file=sys.stderr)
    
    date_7 = (current_date - relativedelta(months =6)).strftime('%Y-%m')
    print(date_7,file=sys.stderr)
    
    date_8 = (current_date - relativedelta(months =7)).strftime('%Y-%m')
    print(date_8,file=sys.stderr)
    igw_net_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_8}%' and CISCO_DOMAIN='IGW-NET';").scalar()
    igw_net_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_7}%' and CISCO_DOMAIN='IGW-NET';").scalar()
    igw_net_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_6}%' and CISCO_DOMAIN='IGW-NET';").scalar()
    igw_net_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_5}%' and CISCO_DOMAIN='IGW-NET';").scalar()   
    igw_net_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_4}%' and CISCO_DOMAIN='IGW-NET';").scalar()
    igw_net_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_3}%' and CISCO_DOMAIN='IGW-NET';").scalar()
    igw_net_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_2}%' and CISCO_DOMAIN='IGW-NET';").scalar()
    igw_net_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_1}%' and CISCO_DOMAIN='IGW-NET';").scalar()
    
    edn_net_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_8}%' and CISCO_DOMAIN='EDN-NET';").scalar()
    edn_net_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_7}%' and CISCO_DOMAIN='EDN-NET';").scalar()
    edn_net_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_6}%' and CISCO_DOMAIN='EDN-NET';").scalar()
    edn_net_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_5}%' and CISCO_DOMAIN='EDN-NET';").scalar()
    edn_net_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_4}%' and CISCO_DOMAIN='EDN-NET';").scalar()
    edn_net_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_3}%' and CISCO_DOMAIN='EDN-NET';").scalar()
    edn_net_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_2}%' and CISCO_DOMAIN='EDN-NET';").scalar()
    edn_net_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_1}%' and CISCO_DOMAIN='EDN-NET';").scalar()
    
    igw_sys_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_8}%' and CISCO_DOMAIN='IGW-SYS';").scalar()
    igw_sys_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_7}%' and CISCO_DOMAIN='IGW-SYS';").scalar()
    igw_sys_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_6}%' and CISCO_DOMAIN='IGW-SYS';").scalar()
    igw_sys_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_5}%' and CISCO_DOMAIN='IGW-SYS';").scalar()
    igw_sys_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_4}%' and CISCO_DOMAIN='IGW-SYS';").scalar()
    igw_sys_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_3}%' and CISCO_DOMAIN='IGW-SYS';").scalar()
    igw_sys_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_2}%' and CISCO_DOMAIN='IGW-SYS';").scalar()
    igw_sys_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_1}%' and CISCO_DOMAIN='IGW-SYS';").scalar()
    
    edn_sys_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_8}%' and CISCO_DOMAIN='EDN-SYS';").scalar()
    edn_sys_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_7}%' and CISCO_DOMAIN='EDN-SYS';").scalar()
    edn_sys_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_6}%' and CISCO_DOMAIN='EDN-SYS';").scalar()
    edn_sys_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_5}%' and CISCO_DOMAIN='EDN-SYS';").scalar()
    edn_sys_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_4}%' and CISCO_DOMAIN='EDN-SYS';").scalar()
    edn_sys_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_3}%' and CISCO_DOMAIN='EDN-SYS';").scalar()
    edn_sys_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_2}%' and CISCO_DOMAIN='EDN-SYS';").scalar()
    edn_sys_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_1}%' and CISCO_DOMAIN='EDN-SYS';").scalar()
    
    
    
    soc_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_8}%' and CISCO_DOMAIN='Security';").scalar()
    soc_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_7}%' and CISCO_DOMAIN='Security';").scalar()
    soc_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_6}%' and CISCO_DOMAIN='Security';").scalar()
    soc_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_5}%' and CISCO_DOMAIN='Security';").scalar()
    soc_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_4}%' and CISCO_DOMAIN='Security';").scalar()
    soc_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_3}%' and CISCO_DOMAIN='Security';").scalar()
    soc_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_2}%' and CISCO_DOMAIN='Security';").scalar()
    soc_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_1}%' and CISCO_DOMAIN='Security';").scalar()
    
    edn_ipt_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_8}%' and CISCO_DOMAIN='EDN-IPT';").scalar()
    edn_ipt_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_7}%' and CISCO_DOMAIN='EDN-IPT';").scalar()
    edn_ipt_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_6}%' and CISCO_DOMAIN='EDN-IPT';").scalar()
    edn_ipt_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_5}%' and CISCO_DOMAIN='EDN-IPT';").scalar()
    edn_ipt_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_4}%' and CISCO_DOMAIN='EDN-IPT';").scalar()
    edn_ipt_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_3}%' and CISCO_DOMAIN='EDN-IPT';").scalar()
    edn_ipt_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_2}%' and CISCO_DOMAIN='EDN-IPT';").scalar()
    edn_ipt_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_1}%' and CISCO_DOMAIN='EDN-IPT';").scalar()
    
    pos_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where CREATION_DATE like '%{date_8}%';").scalar()
    pos_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where CREATION_DATE like '%{date_7}%';").scalar()
    pos_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where CREATION_DATE like '%{date_6}%';").scalar()
    pos_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where CREATION_DATE like '%{date_5}%';").scalar()
    pos_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where CREATION_DATE like '%{date_4}%';").scalar()
    pos_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where CREATION_DATE like '%{date_3}%';").scalar()
    pos_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where CREATION_DATE like '%{date_2}%';").scalar()
    pos_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where CREATION_DATE like '%{date_1}%';").scalar()
    
    rebd_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where CREATION_DATE like '%{date_8}%';").scalar()
    rebd_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where CREATION_DATE like '%{date_7}%';").scalar()
    rebd_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where CREATION_DATE like '%{date_6}%';").scalar()
    rebd_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where CREATION_DATE like '%{date_5}%';").scalar()
    rebd_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where CREATION_DATE like '%{date_4}%';").scalar()
    rebd_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where CREATION_DATE like '%{date_3}%';").scalar()
    rebd_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where CREATION_DATE like '%{date_2}%';").scalar()
    rebd_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where CREATION_DATE like '%{date_1}%';").scalar()
    # edn_ipt_endpoints_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_8}%' and CISCO_DOMAIN='EDN-IPT-Endpoints';").scalar()
    # edn_ipt_endpoints_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_7}%' and CISCO_DOMAIN='EDN-IPT-Endpoints';").scalar()
    # edn_ipt_endpoints_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_6}%' and CISCO_DOMAIN='EDN-IPT-Endpoints';").scalar()
    # edn_ipt_endpoints_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_5}%' and CISCO_DOMAIN='EDN-IPT-Endpoints';").scalar()
    # edn_ipt_endpoints_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_4}%' and CISCO_DOMAIN='EDN-IPT-Endpoints';").scalar()
    # edn_ipt_endpoints_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_3}%' and CISCO_DOMAIN='EDN-IPT-Endpoints';").scalar()
    # edn_ipt_endpoints_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_2}%' and CISCO_DOMAIN='EDN-IPT-Endpoints';").scalar()
    # edn_ipt_endpoints_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_1}%' and CISCO_DOMAIN='EDN-IPT-Endpoints';").scalar()
    

    if True:
    
        objList = [
            {
                "month": date_8,
                "IGW-NET":int(igw_net_8_count),
                "EDN-NET": int(edn_net_8_count),
                "IGW-SYS": int(igw_sys_8_count),
                "EDN-SYS": int(edn_sys_8_count),
                "EDN-IPT": int(edn_ipt_8_count),
                "SOC": int(soc_8_count)
                # "POS" : int(pos_8_count),
                # "REBD" : int(rebd_8_count),
                
            },
            {
                "month": date_7,
                "IGW-NET":int(igw_net_7_count),
                "EDN-NET": int(edn_net_7_count),
                "IGW-SYS": int(igw_sys_7_count),
                "EDN-SYS": int(edn_sys_7_count),
                "EDN-IPT": int(edn_ipt_7_count),
                "SOC": int(soc_7_count)
                # "POS" : int(pos_7_count),
                # "REBD" : int(rebd_8_count),
            },
            {
                "month": date_6,
                "IGW-NET":int(igw_net_6_count),
                "EDN-NET": int(edn_net_6_count),
                "IGW-SYS": int(igw_sys_6_count),
                "EDN-SYS": int(edn_sys_6_count),
                "EDN-IPT": int(edn_ipt_6_count),
                "SOC": int(soc_6_count)
                # "POS" : int(pos_6_count),
                # "REBD" : int(rebd_6_count),
            },
            {
                "month": date_5,
                "IGW-NET":int(igw_net_5_count),
                "EDN-NET": int(edn_net_5_count),
                "IGW-SYS": int(igw_sys_5_count),
                "EDN-SYS": int(edn_sys_5_count),
                "EDN-IPT": int(edn_ipt_5_count),
                "SOC": int(soc_5_count)
                # "POS" : int(pos_5_count),
                # "REBD" : int(rebd_5_count)
                
            },
            {
                "month": date_4,
                "IGW-NET":int(igw_net_4_count),
                "EDN-NET": int(edn_net_4_count),
                "IGW-SYS": int(igw_sys_4_count),
                "EDN-SYS": int(edn_sys_4_count),
                "EDN-IPT": int(edn_ipt_4_count),
                "SOC": int(soc_4_count)
                # "POS" : int(pos_4_count),
                # "REBD" : int(rebd_4_count)
                
            },
            {
                "month": date_3,
                "IGW-NET":int(igw_net_3_count),
                "EDN-NET": int(edn_net_3_count),
                "IGW-SYS": int(igw_sys_3_count),
                "EDN-SYS": int(edn_sys_3_count),
                "EDN-IPT": int(edn_ipt_3_count),
                "SOC": int(soc_3_count)
                # "POS" : int(pos_3_count),
                # "REBD" : int(rebd_3_count)
            },
            {
                "month": date_2,
                "IGW-NET":int(igw_net_2_count),
                "EDN-NET": int(edn_net_2_count),
                "IGW-SYS": int(igw_sys_2_count),
                "EDN-SYS": int(edn_sys_2_count),
                "EDN-IPT": int(edn_ipt_2_count),
                "SOC": int(soc_2_count)
                # "POS" : int(pos_2_count),
                # "REBD" : int(rebd_2_count)
            },
            {
                "month": date_1,
                "IGW-NET":int(igw_net_1_count),
                "EDN-NET": int(edn_net_1_count),
                "IGW-SYS": int(igw_sys_1_count),
                "EDN-SYS": int(edn_sys_1_count),
                "EDN-IPT": int(edn_ipt_1_count),
                "SOC": int(soc_1_count)
                # "POS" : int(pos_1_count),
                # "REBD" : int(rebd_1_count)
            }
        ]

        return jsonify(objList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/pnCodeStatGrowth',methods=['GET'])
@token_required
def InventoryGrowth(user_data):
    if True:
        objList = []
        # current_date = datetime.today()
        # date_1 = (current_date - relativedelta(months=0)).strftime('%Y-%m')
        queryString = f"select coalesce(sum(EDN_NET),0),CREATION_DATE from pncode_snap_table where CREATION_DATE in (select MAX(CREATION_DATE) as date from pncode_snap_table group by YEAR(CREATION_DATE), MONTH(CREATION_DATE)) group by CREATION_DATE ORDER by CREATION_DATE;"
        result = db.session.execute(queryString)
        count = 0
        count1 = 0
        count2 = 0
        count3 = 0
        count4 = 0
        count5 = 0
        count6 = 0
        count7 = 0
        for row in result:
            
            dict = {}
            sum = int(row[0])
            creationDate = FormatDate(row[1])
            dict["EDN-NET"]=sum
            dict["month"]=creationDate
            objList.append(dict)
            count+=1
            print('Number of iterations for EDN-NET: ',count,file=sys.stderr)
            if count>=12:
                print("Maximum limit for the months has reached",file=sys.stderr)
                break

        queryString1 = f"select coalesce(sum(IGW_NET),0),CREATION_DATE from pncode_snap_table where CREATION_DATE in (select MAX(CREATION_DATE) as date from pncode_snap_table group by YEAR(CREATION_DATE), MONTH(CREATION_DATE)) group by CREATION_DATE ORDER by CREATION_DATE;"
        result1 = db.session.execute(queryString1)
        for row in result1:
            dict = {}
            sum = int(row[0])
            creationDate = FormatDate(row[1])
            dict["IGW-NET"]= sum
            dict["month"]=creationDate
            objList.append(dict)
            count1+=1
            print('Number of iterations for IGW-NET: ',count1,file=sys.stderr)
            if count1>=12:
                print("Maximum limit for the months has reached",file=sys.stderr)
                break

        queryString2 = f"select coalesce(sum(EDN_SYS),0),CREATION_DATE from pncode_snap_table where CREATION_DATE in (select MAX(CREATION_DATE) as date from pncode_snap_table group by YEAR(CREATION_DATE), MONTH(CREATION_DATE)) group by CREATION_DATE ORDER BY CREATION_DATE;"
        result2 = db.session.execute(queryString2)
        for row in result2:
            dict = {}
            sum = int(row[0])
            creationDate = FormatDate(row[1])
            dict["EDN-SYS"]=sum
            dict["month"]=creationDate
            objList.append(dict)
            count2+=1
            print('Number of iterations for EDN-SYS: ',count2,file=sys.stderr)
            if count2>=12:
                print("Maximum limit for the months has reached",file=sys.stderr)
                break
        
        queryString3 = f"select coalesce(sum(IGW_SYS),0),CREATION_DATE from pncode_snap_table where CREATION_DATE in (select MAX(CREATION_DATE) as date from pncode_snap_table group by YEAR(CREATION_DATE), MONTH(CREATION_DATE)) group by CREATION_DATE ORDER by CREATION_DATE;"
        result3 = db.session.execute(queryString3)
        for row in result3:
            dict = {}
            sum = int(row[0])
            creationDate = FormatDate(row[1])
            dict["IGW-SYS"]=sum
            dict["month"]=creationDate
            objList.append(dict)
            count3+=1
            print('Number of iterations for IGW-SYS: ',count3,file=sys.stderr)
            if count3>=12:
                print("Maximum limit for the months has reached",file=sys.stderr)
                break
        
        queryString4 = f"select coalesce(sum(SOC),0),CREATION_DATE from pncode_snap_table where CREATION_DATE in (select MAX(CREATION_DATE) as date from pncode_snap_table group by YEAR(CREATION_DATE), MONTH(CREATION_DATE)) group by CREATION_DATE ORDER BY CREATION_DATE;"
        result4 = db.session.execute(queryString4)
        for row in result4:
            dict = {}
            sum = int(row[0])
            creationDate = FormatDate(row[1])
            dict["SOC"]=sum
            dict["month"]=creationDate
            objList.append(dict)
            count4+=1
            print('Number of iterations for SOC: ',count4,file=sys.stderr)
            if count4>=12:
                print("Maximum limit for the months has reached",file=sys.stderr)
                break
        
        queryString5 = f"select coalesce(sum(CDN),0),CREATION_DATE from pncode_snap_table where CREATION_DATE in (select MAX(CREATION_DATE) as date from pncode_snap_table group by YEAR(CREATION_DATE), MONTH(CREATION_DATE)) group by CREATION_DATE ORDER BY CREATION_DATE;"
        result5 = db.session.execute(queryString5)
        for row in result5:
            dict = {}
            sum = int(row[0])
            creationDate = FormatDate(row[1])
            dict["CDN"]=sum
            dict['month']=creationDate
            objList.append(dict)
            count5+=1
            print("Number of Iterations for CDP: ",count5,file=sys.stderr)
            if count5>=12:
                print("Maximum limit for the months has reached",file=sys.stderr)
                break
        queryString6 = f"select coalesce(sum(POS),0),CREATION_DATE from pncode_snap_table where CREATION_DATE in (select MAX(CREATION_DATE) as date from pncode_snap_table group by YEAR(CREATION_DATE), MONTH(CREATION_DATE)) group by CREATION_DATE ORDER BY CREATION_DATE;"
        result6 = db.session.execute(queryString6)
        for row in result6:
            dict = {}
            sum = int(row[0])
            creationDate = FormatDate(row[1])
            dict["POS"]=sum
            dict['month']=creationDate
            objList.append(dict)
            count6+=1
            print("Number of Iterations for POS: ",count5,file=sys.stderr)
            if count6>=12:
                print("Maximum limit for the months has reached",file=sys.stderr)
                break
        queryString7 = f"select coalesce(sum(REBD),0),CREATION_DATE from pncode_snap_table where CREATION_DATE in (select MAX(CREATION_DATE) as date from pncode_snap_table group by YEAR(CREATION_DATE), MONTH(CREATION_DATE)) group by CREATION_DATE ORDER BY CREATION_DATE;"
        result7 = db.session.execute(queryString7)
        for row in result7:
            dict = {}
            sum = int(row[0])
            creationDate = FormatDate(row[1])
            dict["REBD"]=sum
            dict['month']=creationDate
            objList.append(dict)
            count7+=1
            print("Number of Iterations for REBD: ",count5,file=sys.stderr)
            if count7>=12:
                print("Maximum limit for the months has reached",file=sys.stderr)
                break
      
        final_array =[]
        unique_dates=list(set([date['month'] for date in objList]))
        for date in unique_dates:
            dic={}
            dic["month"]= date
            for record in objList:
                if record["month"]== date:
                    dic.update(record)
            final_array.append(dic)
        final_array.sort(key = lambda x: datetime.strptime(x['month'], '%d-%m-%Y'))
        print(final_array,file=sys.stderr)
        return jsonify(final_array),200
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/eosExpiry',methods = ['GET'])
@token_required
def EoxStatus(user_data):
    if True:
        queryString1 = f"select coalesce(sum(STACK),0) from device_table where HW_EOS_DATE <= NOW() and STATUS='Production';"
        queryString2 = f"select coalesce(sum(STACK),0) from device_table where HW_EOS_DATE >= NOW() and STATUS='Production';"
        result1 = db.session.execute(queryString1).scalar()
        result2 = db.session.execute(queryString2).scalar()
        objList = [
            {
                "name":"EoX",
                "value":int(result1)
            },
            {
                "name":"non-EoX",
                "value":int(result2)
            }
        ]
        print(objList,file=sys.stderr)
        return jsonify(objList),200
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/tagId',methods = ['GET'])
@token_required
def TagId(user_data):
    if True:
        tbfCount = db.session.execute(f"select count(TAG_ID) from device_table where `VIRTUAL`='Not Virtual' and status='Production' and TAG_ID='TBF';").scalar()
        notTbfCount = db.session.execute(f"select count(TAG_ID) from device_table where `VIRTUAL`='Not Virtual' and status='Production' and TAG_ID!='TBF';").scalar()
        
        objList = [
            {
                "name":"No Tag ID",
                "value":tbfCount
            },
            {
                "name":"Tag ID Recorded",
                "value":notTbfCount
            }
        
        ]
        print(objList,file=sys.stderr)
        return jsonify(objList),200
    else:
        print("Authentication Failed",file=sys.stderr)
        return jsonify({"message":"Authentication Failed"}),401
    
@app.route('/tagIdVDate',methods = ['GET'])
@token_required
def GetTagIdVDate(user_data):
    tbfCount = db.session.execute(f"SELECT COUNT(TAG_ID) FROM device_table WHERE `VIRTUAL` = 'Not Virtual' AND status = 'Production' AND TAG_ID = 'TBF' and rfs_date >= '2022-01-01';").scalar()
    notTbfCount = db.session.execute(f"SELECT COUNT(TAG_ID) FROM device_table WHERE `VIRTUAL` = 'Not Virtual' AND status = 'Production' AND TAG_ID != 'TBF' and rfs_date >= '2022-01-01';").scalar()
    
    objList = [
        {
            "name":"No Tag ID",
            "value":tbfCount
        },
        {
            "name":"Tag ID Recorded",
            "value":notTbfCount
        }
    
    ]
    print(objList,file=sys.stderr)
    return jsonify(objList),200

@app.route("/functions",methods = ['GET'])
@token_required
def Functions(user_data):
    if True:
        objDict = {}
        # queryString = "select distinct `FUNCTION`,count(`FUNCTION`) from device_table where status='Production' group by CISCO_DOMAIN,`FUNCTION` order by count(`FUNCTION`);"
        queryString = "select distinct `FUNCTION`,count(`FUNCTION`) from device_table where status='Production' group by CISCO_DOMAIN,`FUNCTION` order by count(`FUNCTION`) DESC LIMIT 20;"
        result = db.session.execute(queryString)
        for row in result:
            function = row[0]
            functionCount = row[1]
            if function in objDict:
                count = 'value'
                objDict[function][count]=functionCount
                print(objDict,file=sys.stderr)
            else:
                objDict[function]={}
                count  = 'value'
                objDict[function]['value']=0
                objDict[function]['value']=functionCount
        objList=[]
        for function in objDict:
            dict = objDict[function]
            dict['name']=function
            objList.append(dict)
        print(objList,file=sys.stderr)
        return jsonify(objList),200

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/dismantledDevicesPerMonth", methods = ['GET'])
@token_required
def DismantledDevicePerMonth(user_data):
    #if request.headers.get('X-Auth-Key') == session.get('token', None):
    current_date = datetime.today()

    date_1 = (current_date - relativedelta(months=0)).strftime('%Y-%m')
    print(date_1, file=sys.stderr)

    date_2 = (current_date - relativedelta(months=1)).strftime('%Y-%m')
    print(date_2, file=sys.stderr)

    date_3 = (current_date - relativedelta(months=2)).strftime('%Y-%m')
    print(date_3, file=sys.stderr)

    date_4 = (current_date - relativedelta(months=3)).strftime('%Y-%m')
    print(date_4, file=sys.stderr)

    date_5 = (current_date - relativedelta(months =4)).strftime('%Y-%m')
    print(date_5,file=sys.stderr)
    
    date_6 = (current_date - relativedelta(months =5)).strftime('%Y-%m')
    print(date_6,file=sys.stderr)
    
    date_7 = (current_date - relativedelta(months =6)).strftime('%Y-%m')
    print(date_7,file=sys.stderr)
    
    date_8 = (current_date - relativedelta(months =7)).strftime('%Y-%m')
    print(date_8,file=sys.stderr)
    igw_net_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Dismantle';").scalar()
    igw_net_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Dismantle';").scalar()
    igw_net_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Dismantle';").scalar()
    igw_net_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Dismantle';").scalar()   
    igw_net_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Dismantle';").scalar()
    igw_net_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Dismantle';").scalar()
    igw_net_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Dismantle';").scalar()
    igw_net_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Dismantle';").scalar()
    
    edn_net_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Dismantle';").scalar()
    edn_net_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Dismantle';").scalar()
    edn_net_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Dismantle';").scalar()
    edn_net_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Dismantle';").scalar()
    edn_net_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Dismantle';").scalar()
    edn_net_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Dismantle';").scalar()
    edn_net_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Dismantle';").scalar()
    edn_net_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Dismantle';").scalar()
    
    igw_sys_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Dismantle';").scalar()
    igw_sys_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Dismantle';").scalar()
    igw_sys_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Dismantle';").scalar()
    igw_sys_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Dismantle';").scalar()
    igw_sys_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Dismantle';").scalar()
    igw_sys_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Dismantle';").scalar()
    igw_sys_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Dismantle';").scalar()
    igw_sys_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Dismantle';").scalar()
    
    edn_sys_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Dismantle';").scalar()
    edn_sys_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Dismantle';").scalar()
    edn_sys_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Dismantle';").scalar()
    edn_sys_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Dismantle';").scalar()
    edn_sys_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Dismantle';").scalar()
    edn_sys_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Dismantle';").scalar()
    edn_sys_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Dismantle';").scalar()
    edn_sys_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Dismantle';").scalar()
    
    soc_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='Security' and STATUS='Dismantle';").scalar()
    soc_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='Security' and STATUS='Dismantle';").scalar()
    soc_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='Security' and STATUS='Dismantle';").scalar()
    soc_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='Security' and STATUS='Dismantle';").scalar()
    soc_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='Security' and STATUS='Dismantle';").scalar()
    soc_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='Security' and STATUS='Dismantle';").scalar()
    soc_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='Security' and STATUS='Dismantle';").scalar()
    soc_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='Security' and STATUS='Dismantle';").scalar()
    
    edn_ipt_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Dismantle';").scalar()
    edn_ipt_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Dismantle';").scalar()
    edn_ipt_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Dismantle';").scalar()
    edn_ipt_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Dismantle';").scalar()
    edn_ipt_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Dismantle';").scalar()
    edn_ipt_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Dismantle';").scalar()
    edn_ipt_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Dismantle';").scalar()
    edn_ipt_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Dismantle';").scalar()
    
    pos_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_8}%' and OPERATION_STATUS='Dismantle';").scalar()
    pos_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_7}%' and OPERATION_STATUS='Dismantle';").scalar()
    pos_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_6}%' and OPERATION_STATUS='Dismantle';").scalar()
    pos_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_5}%' and OPERATION_STATUS='Dismantle';").scalar()
    pos_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_4}%' and OPERATION_STATUS='Dismantle';").scalar()
    pos_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_3}%' and OPERATION_STATUS='Dismantle';").scalar()
    pos_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_2}%' and OPERATION_STATUS='Dismantle';").scalar()
    pos_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_1}%' and OPERATION_STATUS='Dismantle';").scalar()
    
    rebd_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_8}%' and OPERATION_STATUS='Dismantle';").scalar()
    rebd_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_7}%' and OPERATION_STATUS='Dismantle';").scalar()
    rebd_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_6}%' and OPERATION_STATUS='Dismantle';").scalar()
    rebd_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_5}%' and OPERATION_STATUS='Dismantle';").scalar()
    rebd_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_4}%' and OPERATION_STATUS='Dismantle';").scalar()
    rebd_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_3}%' and OPERATION_STATUS='Dismantle';").scalar()
    rebd_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_2}%' and OPERATION_STATUS='Dismantle';").scalar()
    rebd_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_1}%' and OPERATION_STATUS='Dismantle';").scalar()
    
    
    
    if True:
    #if session.get('token', None):
        objList = [
            {
                "month": date_8,
                "IGW-NET":int(igw_net_8_count),
                "EDN-NET": int(edn_net_8_count),
                "IGW-SYS": int(igw_sys_8_count),
                "EDN-SYS": int(edn_sys_8_count),
                "EDN-IPT": int(edn_ipt_8_count),
                "SOC": int(soc_8_count)
                # "POS" : int(pos_8_count),
                # "REBD" : int(rebd_8_count),
                
            },
            {
                "month": date_7,
                "IGW-NET":int(igw_net_7_count),
                "EDN-NET": int(edn_net_7_count),
                "IGW-SYS": int(igw_sys_7_count),
                "EDN-SYS": int(edn_sys_7_count),
                "EDN-IPT": int(edn_ipt_7_count),
                "SOC": int(soc_7_count)
                # "POS" : int(pos_7_count),
                # "REBD" : int(rebd_7_count),
            },
            {
                "month": date_6,
                "IGW-NET":int(igw_net_6_count),
                "EDN-NET": int(edn_net_6_count),
                "IGW-SYS": int(igw_sys_6_count),
                "EDN-SYS": int(edn_sys_6_count),
                "EDN-IPT": int(edn_ipt_6_count),
                "SOC": int(soc_6_count)
                # "POS" : int(pos_6_count),
                # "REBD" : int(rebd_6_count),
            },
            {
                "month": date_5,
                "IGW-NET":int(igw_net_5_count),
                "EDN-NET": int(edn_net_5_count),
                "IGW-SYS": int(igw_sys_5_count),
                "EDN-SYS": int(edn_sys_5_count),
                "EDN-IPT": int(edn_ipt_5_count),
                "SOC": int(soc_5_count)
                # "POS" : int(pos_5_count),
                # "REBD" : int(rebd_5_count)
                
            },
            {
                "month": date_4,
                "IGW-NET":int(igw_net_4_count),
                "EDN-NET": int(edn_net_4_count),
                "IGW-SYS": int(igw_sys_4_count),
                "EDN-SYS": int(edn_sys_4_count),
                "EDN-IPT": int(edn_ipt_4_count),
                "SOC": int(soc_4_count)
                # "POS" : int(pos_4_count),
                # "REBD" : int(rebd_7_count)
                
            },
            {
                "month": date_3,
                "IGW-NET":int(igw_net_3_count),
                "EDN-NET": int(edn_net_3_count),
                "IGW-SYS": int(igw_sys_3_count),
                "EDN-SYS": int(edn_sys_3_count),
                "EDN-IPT": int(edn_ipt_3_count),
                "SOC": int(soc_3_count)
                # "POS" : int(pos_3_count),
                # "REBD" : int(rebd_3_count)
            },
            {
                "month": date_2,
                "IGW-NET":int(igw_net_2_count),
                "EDN-NET": int(edn_net_2_count),
                "IGW-SYS": int(igw_sys_2_count),
                "EDN-SYS": int(edn_sys_2_count),
                "EDN-IPT": int(edn_ipt_2_count),
                "SOC": int(soc_2_count)
                # "POS" : int(pos_2_count),
                # "REBD" : int(rebd_7_count)
            },
            {
                "month": date_1,
                "IGW-NET":int(igw_net_1_count),
                "EDN-NET": int(edn_net_1_count),
                "IGW-SYS": int(igw_sys_1_count),
                "EDN-SYS": int(edn_sys_1_count),
                "EDN-IPT": int(edn_ipt_1_count),
                "SOC": int(soc_1_count)
                # "POS" : int(pos_1_count),
                # "REBD" : int(pos_1_count)
            }
        ]

        return jsonify(objList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/offloadedOffPerMonth", methods = ['GET'])
@token_required
def OffloadedPerMonth(user_data):
    #if request.headers.get('X-Auth-Key') == session.get('token', None):
    current_date = datetime.today()

    date_1 = (current_date - relativedelta(months=0)).strftime('%Y-%m')
    print(date_1, file=sys.stderr)

    date_2 = (current_date - relativedelta(months=1)).strftime('%Y-%m')
    print(date_2, file=sys.stderr)

    date_3 = (current_date - relativedelta(months=2)).strftime('%Y-%m')
    print(date_3, file=sys.stderr)

    date_4 = (current_date - relativedelta(months=3)).strftime('%Y-%m')
    print(date_4, file=sys.stderr)

    date_5 = (current_date - relativedelta(months =4)).strftime('%Y-%m')
    print(date_5,file=sys.stderr)
    
    date_6 = (current_date - relativedelta(months =5)).strftime('%Y-%m')
    print(date_6,file=sys.stderr)
    
    date_7 = (current_date - relativedelta(months =6)).strftime('%Y-%m')
    print(date_7,file=sys.stderr)
    
    date_8 = (current_date - relativedelta(months =7)).strftime('%Y-%m')
    print(date_8,file=sys.stderr)
    igw_net_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Offloaded';").scalar()
    igw_net_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Offloaded';").scalar()
    igw_net_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Offloaded';").scalar()
    igw_net_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Offloaded';").scalar()   
    igw_net_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Offloaded';").scalar()
    igw_net_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Offloaded';").scalar()
    igw_net_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Offloaded';").scalar()
    igw_net_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Offloaded';").scalar()
    
    edn_net_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Offloaded';").scalar()
    edn_net_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Offloaded';").scalar()
    edn_net_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Offloaded';").scalar()
    edn_net_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Offloaded';").scalar()
    edn_net_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Offloaded';").scalar()
    edn_net_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Offloaded';").scalar()
    edn_net_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Offloaded';").scalar()
    edn_net_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Offloaded';").scalar()
    
    igw_sys_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Offloaded';").scalar()
    igw_sys_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Offloaded';").scalar()
    igw_sys_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Offloaded';").scalar()
    igw_sys_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Offloaded';").scalar()
    igw_sys_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Offloaded';").scalar()
    igw_sys_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Offloaded';").scalar()
    igw_sys_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Offloaded';").scalar()
    igw_sys_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Offloaded';").scalar()
    
    edn_sys_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Offloaded';").scalar()
    edn_sys_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Offloaded';").scalar()
    edn_sys_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Offloaded';").scalar()
    edn_sys_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Offloaded';").scalar()
    edn_sys_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Offloaded';").scalar()
    edn_sys_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Offloaded';").scalar()
    edn_sys_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Offloaded';").scalar()
    edn_sys_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Offloaded';").scalar()
    
    soc_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='Security' and STATUS='Offloaded';").scalar()
    soc_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='Security' and STATUS='Offloaded';").scalar()
    soc_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='Security' and STATUS='Offloaded';").scalar()
    soc_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='Security' and STATUS='Offloaded';").scalar()
    soc_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='Security' and STATUS='Offloaded';").scalar()
    soc_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='Security' and STATUS='Offloaded';").scalar()
    soc_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='Security' and STATUS='Offloaded';").scalar()
    soc_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='Security' and STATUS='Offloaded';").scalar()
    
    edn_ipt_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Offloaded';").scalar()
    edn_ipt_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Offloaded';").scalar()
    edn_ipt_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Offloaded';").scalar()
    edn_ipt_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Offloaded';").scalar()
    edn_ipt_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Offloaded';").scalar()
    edn_ipt_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Offloaded';").scalar()
    edn_ipt_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Offloaded';").scalar()
    edn_ipt_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Offloaded';").scalar()
    
    pos_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_8}%' and OPERATION_STATUS='Offloaded';").scalar()
    pos_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_7}%' and OPERATION_STATUS='Offloaded';").scalar()
    pos_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_6}%' and OPERATION_STATUS='Offloaded';").scalar()
    pos_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_5}%' and OPERATION_STATUS='Offloaded';").scalar()
    pos_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_4}%' and OPERATION_STATUS='Offloaded';").scalar()
    pos_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_3}%' and OPERATION_STATUS='Offloaded';").scalar()
    pos_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_2}%' and OPERATION_STATUS='Offloaded';").scalar()
    pos_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_1}%' and OPERATION_STATUS='Offloaded';").scalar()
    
    rebd_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_8}%' and OPERATION_STATUS='Offloaded';").scalar()
    rebd_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_7}%' and OPERATION_STATUS='Offloaded';").scalar()
    rebd_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_6}%' and OPERATION_STATUS='Offloaded';").scalar()
    rebd_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_5}%' and OPERATION_STATUS='Offloaded';").scalar()
    rebd_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_4}%' and OPERATION_STATUS='Offloaded';").scalar()
    rebd_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_3}%' and OPERATION_STATUS='Offloaded';").scalar()
    rebd_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_2}%' and OPERATION_STATUS='Offloaded';").scalar()
    rebd_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_1}%' and OPERATION_STATUS='Offloaded';").scalar()
    
    
    
    if True:
    #if session.get('token', None):
        objList = [
            {
                "month": date_8,
                "IGW-NET":int(igw_net_8_count),
                "EDN-NET": int(edn_net_8_count),
                "IGW-SYS": int(igw_sys_8_count),
                "EDN-SYS": int(edn_sys_8_count),
                "EDN-IPT": int(edn_ipt_8_count),
                "SOC": int(soc_8_count)
                # "POS" : int(pos_8_count),
                # "REBD" : int(rebd_8_count),
                
            },
            {
                "month": date_7,
                "IGW-NET":int(igw_net_7_count),
                "EDN-NET": int(edn_net_7_count),
                "IGW-SYS": int(igw_sys_7_count),
                "EDN-SYS": int(edn_sys_7_count),
                "EDN-IPT": int(edn_ipt_7_count),
                "SOC": int(soc_7_count)
                # "POS" : int(pos_7_count),
                # "REBD" : int(rebd_7_count),
            },
            {
                "month": date_6,
                "IGW-NET":int(igw_net_6_count),
                "EDN-NET": int(edn_net_6_count),
                "IGW-SYS": int(igw_sys_6_count),
                "EDN-SYS": int(edn_sys_6_count),
                "EDN-IPT": int(edn_ipt_6_count),
                "SOC": int(soc_6_count)
                # "POS" : int(pos_6_count),
                # "REBD" : int(rebd_6_count),
            },
            {
                "month": date_5,
                "IGW-NET":int(igw_net_5_count),
                "EDN-NET": int(edn_net_5_count),
                "IGW-SYS": int(igw_sys_5_count),
                "EDN-SYS": int(edn_sys_5_count),
                "EDN-IPT": int(edn_ipt_5_count),
                "SOC": int(soc_5_count)
                # "POS" : int(pos_5_count),
                # "REBD" : int(rebd_5_count)
                
            },
            {
                "month": date_4,
                "IGW-NET":int(igw_net_4_count),
                "EDN-NET": int(edn_net_4_count),
                "IGW-SYS": int(igw_sys_4_count),
                "EDN-SYS": int(edn_sys_4_count),
                "EDN-IPT": int(edn_ipt_4_count),
                "SOC": int(soc_4_count)
                # "POS" : int(pos_4_count),
                # "REBD" : int(rebd_4_count)
                
            },
            {
                "month": date_3,
                "IGW-NET":int(igw_net_3_count),
                "EDN-NET": int(edn_net_3_count),
                "IGW-SYS": int(igw_sys_3_count),
                "EDN-SYS": int(edn_sys_3_count),
                "EDN-IPT": int(edn_ipt_3_count),
                "SOC": int(soc_3_count)
                # "POS" : int(pos_3_count),
                # "REBD" : int(rebd_3_count)
            },
            {
                "month": date_2,
                "IGW-NET":int(igw_net_2_count),
                "EDN-NET": int(edn_net_2_count),
                "IGW-SYS": int(igw_sys_2_count),
                "EDN-SYS": int(edn_sys_2_count),
                "EDN-IPT": int(edn_ipt_2_count),
                "SOC": int(soc_2_count)
                # "POS" : int(pos_2_count),
                # "REBD" : int(rebd_2_count)
            },
            {
                "month": date_1,
                "IGW-NET":int(igw_net_1_count),
                "EDN-NET": int(edn_net_1_count),
                "IGW-SYS": int(igw_sys_1_count),
                "EDN-SYS": int(edn_sys_1_count),
                "EDN-IPT": int(edn_ipt_1_count),
                "SOC": int(soc_1_count)
                # "POS" : int(pos_1_count),
                # "REBD" : int(rebd_1_count)
            }
        ]

        return jsonify(objList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route("/poweredOffPerMonth", methods = ['GET'])
@token_required
def PoweredOffPerMonth(user_data):
    #if request.headers.get('X-Auth-Key') == session.get('token', None):
    current_date = datetime.today()

    date_1 = (current_date - relativedelta(months=0)).strftime('%Y-%m')
    print(date_1, file=sys.stderr)

    date_2 = (current_date - relativedelta(months=1)).strftime('%Y-%m')
    print(date_2, file=sys.stderr)

    date_3 = (current_date - relativedelta(months=2)).strftime('%Y-%m')
    print(date_3, file=sys.stderr)

    date_4 = (current_date - relativedelta(months=3)).strftime('%Y-%m')
    print(date_4, file=sys.stderr)

    date_5 = (current_date - relativedelta(months =4)).strftime('%Y-%m')
    print(date_5,file=sys.stderr)
    
    date_6 = (current_date - relativedelta(months =5)).strftime('%Y-%m')
    print(date_6,file=sys.stderr)
    
    date_7 = (current_date - relativedelta(months =6)).strftime('%Y-%m')
    print(date_7,file=sys.stderr)
    
    date_8 = (current_date - relativedelta(months =7)).strftime('%Y-%m')
    print(date_8,file=sys.stderr)
    igw_net_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Powered Off';").scalar()
    igw_net_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Powered Off';").scalar()
    igw_net_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Powered Off';").scalar()
    igw_net_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Powered Off';").scalar()   
    igw_net_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Powered Off';").scalar()
    igw_net_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Powered Off';").scalar()
    igw_net_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Powered Off';").scalar()
    igw_net_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='IGW-NET' and STATUS='Powered Off';").scalar()
    
    edn_net_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Powered Off';").scalar()
    edn_net_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Powered Off';").scalar()
    edn_net_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Powered Off';").scalar()
    edn_net_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Powered Off';").scalar()
    edn_net_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Powered Off';").scalar()
    edn_net_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Powered Off';").scalar()
    edn_net_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Powered Off';").scalar()
    edn_net_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='EDN-NET' and STATUS='Powered Off';").scalar()
    
    igw_sys_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Powered Off';").scalar()
    igw_sys_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Powered Off';").scalar()
    igw_sys_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Powered Off';").scalar()
    igw_sys_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Powered Off';").scalar()
    igw_sys_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Powered Off';").scalar()
    igw_sys_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Powered Off';").scalar()
    igw_sys_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Powered Off';").scalar()
    igw_sys_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='IGW-SYS' and STATUS='Powered Off';").scalar()
    
    edn_sys_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Powered Off';").scalar()
    edn_sys_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Powered Off';").scalar()
    edn_sys_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Powered Off';").scalar()
    edn_sys_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Powered Off';").scalar()
    edn_sys_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Powered Off';").scalar()
    edn_sys_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Powered Off';").scalar()
    edn_sys_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Powered Off';").scalar()
    edn_sys_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='EDN-SYS' and STATUS='Powered Off';").scalar()
    
    soc_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='Security' and STATUS='Powered Off';").scalar()
    soc_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='Security' and STATUS='Powered Off';").scalar()
    soc_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='Security' and STATUS='Powered Off';").scalar()
    soc_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='Security' and STATUS='Powered Off';").scalar()
    soc_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='Security' and STATUS='Powered Off';").scalar()
    soc_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='Security' and STATUS='Powered Off';").scalar()
    soc_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='Security' and STATUS='Powered Off';").scalar()
    soc_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='Security' and STATUS='Powered Off';").scalar()
    
    edn_ipt_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Powered Off';").scalar()
    edn_ipt_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Powered Off';").scalar()
    edn_ipt_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Powered Off';").scalar()
    edn_ipt_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Powered Off';").scalar()
    edn_ipt_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Powered Off';").scalar()
    edn_ipt_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Powered Off';").scalar()
    edn_ipt_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Powered Off';").scalar()
    edn_ipt_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='EDN-IPT' and STATUS='Powered Off';").scalar()
    
    pos_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_8}%' and OPERATION_STATUS='Powered Off';").scalar()
    pos_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_7}%' and OPERATION_STATUS='Powered Off';").scalar()
    pos_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_6}%' and OPERATION_STATUS='Powered Off';").scalar()
    pos_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_5}%' and OPERATION_STATUS='Powered Off';").scalar()
    pos_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_4}%' and OPERATION_STATUS='Powered Off';").scalar()
    pos_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_3}%' and OPERATION_STATUS='Powered Off';").scalar()
    pos_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_2}%' and OPERATION_STATUS='Powered Off';").scalar()
    pos_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_1}%' and OPERATION_STATUS='Powered Off';").scalar()
    pos_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from pos_table where MODIFICATION_DATE like '%{date_1}%' and OPERATION_STATUS='Powered Off';").scalar()
    
    rebd_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_8}%' and OPERATION_STATUS='Powered Off';").scalar()
    rebd_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_7}%' and OPERATION_STATUS='Powered Off';").scalar()
    rebd_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_6}%' and OPERATION_STATUS='Powered Off';").scalar()
    rebd_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_5}%' and OPERATION_STATUS='Powered Off';").scalar()
    rebd_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_4}%' and OPERATION_STATUS='Powered Off';").scalar()
    rebd_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_3}%' and OPERATION_STATUS='Powered Off';").scalar()
    rebd_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_2}%' and OPERATION_STATUS='Powered Off';").scalar()
    rebd_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from rebd_table where MODIFICATION_DATE like '%{date_1}%' and OPERATION_STATUS='Powered Off';").scalar()
    if True:
    #if session.get('token', None):
        objList = [
            {
                "month": date_8,
                "IGW-NET":int(igw_net_8_count),
                "EDN-NET": int(edn_net_8_count),
                "IGW-SYS": int(igw_sys_8_count),
                "EDN-SYS": int(edn_sys_8_count),
                "EDN-IPT": int(edn_ipt_8_count),
                "SOC": int(soc_8_count)
                # "POS" : int(pos_8_count),
                # "REBD" : int(rebd_8_count),
                
            },
            {
                "month": date_7,
                "IGW-NET":int(igw_net_7_count),
                "EDN-NET": int(edn_net_7_count),
                "IGW-SYS": int(igw_sys_7_count),
                "EDN-SYS": int(edn_sys_7_count),
                "EDN-IPT": int(edn_ipt_7_count),
                "SOC": int(soc_7_count)
                # "POS" : int(pos_7_count),
                # "REBD" : int(rebd_7_count),
            },
            {
                "month": date_6,
                "IGW-NET":int(igw_net_6_count),
                "EDN-NET": int(edn_net_6_count),
                "IGW-SYS": int(igw_sys_6_count),
                "EDN-SYS": int(edn_sys_6_count),
                "EDN-IPT": int(edn_ipt_6_count),
                "SOC": int(soc_6_count)
                # "POS" : int(pos_6_count),
                # "REBD" : int(rebd_6_count),
            },
            {
                "month": date_5,
                "IGW-NET":int(igw_net_5_count),
                "EDN-NET": int(edn_net_5_count),
                "IGW-SYS": int(igw_sys_5_count),
                "EDN-SYS": int(edn_sys_5_count),
                "EDN-IPT": int(edn_ipt_5_count),
                "SOC": int(soc_5_count)
                # "POS" : int(pos_5_count),
                # "REBD" : int(rebd_5_count)
                
            },
            {
                "month": date_4,
                "IGW-NET":int(igw_net_4_count),
                "EDN-NET": int(edn_net_4_count),
                "IGW-SYS": int(igw_sys_4_count),
                "EDN-SYS": int(edn_sys_4_count),
                "EDN-IPT": int(edn_ipt_4_count),
                "SOC": int(soc_4_count)
                # "POS" : int(pos_4_count),
                # "REBD" : int(rebd_4_count)
                
            },
            {
                "month": date_3,
                "IGW-NET":int(igw_net_3_count),
                "EDN-NET": int(edn_net_3_count),
                "IGW-SYS": int(igw_sys_3_count),
                "EDN-SYS": int(edn_sys_3_count),
                "EDN-IPT": int(edn_ipt_3_count),
                "SOC": int(soc_3_count)
                # "POS" : int(pos_3_count),
                # "REBD" : int(rebd_3_count)
            },
            {
                "month": date_2,
                "IGW-NET":int(igw_net_2_count),
                "EDN-NET": int(edn_net_2_count),
                "IGW-SYS": int(igw_sys_2_count),
                "EDN-SYS": int(edn_sys_2_count),
                "EDN-IPT": int(edn_ipt_2_count),
                "SOC": int(soc_2_count)
                # "POS" : int(pos_2_count),
                # "REBD" : int(rebd_2_count)
            },
            {
                "month": date_1,
                "IGW-NET":int(igw_net_1_count),
                "EDN-NET": int(edn_net_1_count),
                "IGW-SYS": int(igw_sys_1_count),
                "EDN-SYS": int(edn_sys_1_count),
                "EDN-IPT": int(edn_ipt_1_count),
                "SOC": int(soc_1_count)
                # "POS" : int(pos_1_count),
                # "REBD" : int(rebd_1_count)
            }
        ]

        return jsonify(objList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401



@app.route("/sitesPerSiteType",methods = ['GET'])
@token_required
def SitesPerSiteType(user_data):
    
    if True:
        sites= Phy_Table.query.filter_by(status='Production').all()
        objList= []
        objDic= {}

        if sites:
            for site in sites:
                
                if site.site_type:
                    siteTypes= site.site_type.split(',')

                    for siteType in siteTypes:
                        if siteType in objDic:
                            objDic[siteType]= int(objDic[siteType])+1
                        else:
                            objDic[siteType]= 1
                else:
                    if "NE" in objDic:
                        objDic['NE']= int(objDic['NE'])+1
                    else:
                        objDic['NE']= 1

            for k,v in objDic.items():
                objList.append({"name":k, "value":v})
        
        return jsonify(objList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
