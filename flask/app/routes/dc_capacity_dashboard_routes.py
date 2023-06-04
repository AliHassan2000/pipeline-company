import sys, json
from flask_jsonpify import jsonify
from flask import Flask, request, make_response, Response, session
from app import app ,db , tz
from app.models.inventory_models import Phy_Table, Rack_Table, Device_Table, Board_Table, Subboard_Table, SFP_Table, License_Table, Seed, SNTC_Table,CDN_Table,EDN_DC_CAPACITY,IGW_DC_CAPACITY
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

@app.route('/ednDCMCounts',methods =['GET'])
@token_required
def EdnDCMCounts(user_data):
    if True:
        # queryString = f"select count(distinct SITE_ID) from edn_dc_capacity where SITE_ID in(select SITE_ID from seed_table where SITE_TYPE='DC and `FUNCTION` like '%SWITCH%') and CREATION_DATE=(select(max(CREATION_DATE)) from edn_dc_capacity);""
        queryString = f"select count(distinct SITE_ID) from edn_dc_capacity where CREATION_DATE=(select(max(CREATION_DATE)) from edn_dc_capacity);"
        result = db.session.execute(queryString).scalar()
        queryString1 = f'select count(DEVICE_ID) from edn_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);'
        result1 = db.session.execute(queryString1).scalar()
        queryString2 = f'select sum(NOT_CONNECTED_1G) from edn_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);'
        queryString3 = f'select sum(NOT_CONNECTED_10G) from edn_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);'
        queryString4 = f'select sum(NOT_CONNECTED_40G) from edn_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);'
        queryString5 = f'select sum(NOT_CONNECTED_100G) from edn_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);'
        queryString12 = f'select sum(NOT_CONNECTED_25G) from edn_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);'
        queryString13 = f'select sum(NOT_CONNECTED_FAST_ETHERNET) from edn_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);'
        result2 = db.session.execute(queryString2).scalar() 
        result3 = db.session.execute(queryString3).scalar()
        result4 = db.session.execute(queryString4).scalar()
        result5 = db.session.execute(queryString5).scalar()
        result12 = db.session.execute(queryString12).scalar()
        result13 = db.session.execute(queryString13).scalar()
        sum = result2+result3+result4+result5+result12+result13
        queryString6 = f'select sum(TOTAL_1G_PORTS) from edn_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);'
        queryString7 = f'select sum(TOTAL_10G_PORTS) from edn_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);'
        queryString8 = f'select sum(TOTAL_40G_PORTS) from edn_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);'
        queryString9 = f'select sum(TOTAL_100G_PORTS) from edn_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);'
        queryString10 = f"select sum(TOTAL_FAST_ETHERNET_PORTS) from edn_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);"
        queryString11 = f'select sum(TOTAL_25G_PORTS) from edn_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);'
        result6 = db.session.execute(queryString6).scalar()
        result7 = db.session.execute(queryString7).scalar()
        result8 = db.session.execute(queryString8).scalar()
        result9 = db.session.execute(queryString9).scalar()
        result10 = db.session.execute(queryString10).scalar()
        result11 = db.session.execute(queryString11).scalar()
        sum1 = result6+result7+result8+result9+result10+result11
        objList = [
            {
                "name":"DC Count",
                "value":result
            },
            {
                "name":"Switches Count",
                "value":result1
            },
            {
                "name":"Total Ports",
                "value":sum1
            },
            {
                "name":"Not Connected Ports",
                "value":sum
            }

        ]


        return jsonify(objList),200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401



@app.route('/ednDCMDatacenters',methods = ['GET'])
@token_required
def EdnDCMDatacenters(user_data):
    if True:
        objList = []
        queryString = f"select distinct SITE_ID from edn_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);"
        result = db.session.execute(queryString)
        for row in result:
            datacenters = row[0]
            objList.append(datacenters)
        objList.append("ALL")
        return jsonify(objList),200
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/ednDCMPortsGroup',methods= ['POST'])
@token_required
def EdnDCMPortsGroup(user_data):
    if True:
        siteObj = request.get_json()
        # siteObj = {"datacenter":"ALL"}
        print(siteObj,file = sys.stderr)
        queryString = ''
        if siteObj['datacenter']=='ALL':
            queryString = f"select sum(TOTAL_1G_PORTS),sum(TOTAL_10G_PORTS),sum(TOTAL_40G_PORTS),sum(TOTAL_100G_PORTS),sum(CONNECTED_1G),sum(CONNECTED_10G),sum(CONNECTED_40G),sum(CONNECTED_100G),sum(NOT_CONNECTED_1G),sum(NOT_CONNECTED_10G),sum(NOT_CONNECTED_40G),sum(NOT_CONNECTED_100G),sum(UNUSED_SFPS_1G),sum(UNUSED_SFPS_10G),sum(UNUSED_SFPS_40G),sum(UNUSED_SFPS_100G),sum(TOTAL_FAST_ETHERNET_PORTS),sum(CONNECTED_FAST_ETHERNET),sum(NOT_CONNECTED_FAST_ETHERNET),sum(TOTAL_25G_PORTS),sum(CONNECTED_25G),sum(NOT_CONNECTED_25G),sum(UNUSED_SFPS_25G) from edn_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);"
            result = db.session.execute(queryString)
            for row in result:


                total_1g_ports = int(row[0])
                total_10g_ports = int(row[1])
                total_40g_ports = int(row[2])
                total_100g_ports = int(row[3])
                connected_1g = int(row[4])
                connected_10g = int(row[5])
                connected_40g = int(row[6])
                connected_100g = int(row[7])
                not_connect_1g = int(row[8])
                not_connect_10g = int(row[9])
                not_connect_40g = int(row[10])
                not_connect_100g = int(row[11])
                unused_sfps_1g = int(row[12])
                unused_sfps_10g = int(row[13])
                unused_sfps_40g = int(row[14])
                unused_sfps_100g = int(row[15])
                total_fast_ethernet = int(row[16])
                connected_fast_ethernet = int(row[17])
                not_connect_fast_ethernet = int(row[18])
                total_25_ports = int(row[19])
                connected_25g = int(row[20])
                not_connect_25g = int(row[21])
                unused_sfps_25g = int(row[22])
                objDict = {}
                total = (int(total_1g_ports)+int(total_10g_ports)+int(total_40g_ports)+int(total_100g_ports))
                
                objDict['total']=[]
                objDict['total'] = [{"name":"1G","value":total_1g_ports},{"name":'10G','value':total_10g_ports},{"name":'25G','value':total_25_ports},{"name":"40G",'value':total_40g_ports},{"name":"100G","value":total_100g_ports},{"name":"Fast Ethernet","value":total_fast_ethernet}]
                objDict['connected'] = [{"name":"1G","value":connected_1g},{"name":"10G","value":connected_10g},{"name":'25G','value':connected_25g},{"name":"40G","value":connected_40g},{"name":"100G","value":connected_100g},{"name":"Fast Ethernet","value":connected_fast_ethernet}]     
                objDict['not_connected'] = [{"name":"1G","value":not_connect_1g},{"name":"10G","value":not_connect_10g},{"name":'25G','value':not_connect_25g},{"name":"40G","value":not_connect_40g},{"name":"100G","value":not_connect_100g},{"name":"Fast Ethernet","value":not_connect_fast_ethernet}]    
                objDict['unused'] = [{"name":"1G","value":unused_sfps_1g},{"name":"10G","value":unused_sfps_10g},{"name":'25G','value':unused_sfps_25g},{"name":"40G","value":unused_sfps_40g},{"name":"100G","value":unused_sfps_100g},{"name":"Fast Ethernet","value":0}]   
                print(objDict,file=sys.stderr)
                for i in objDict:
                    print(objDict[i],type(objDict[i]),file=sys.stderr)
                return objDict,200
        else:

            queryString = f"select SITE_ID,COUNT(SITE_ID),sum(TOTAL_1G_PORTS),sum(TOTAL_10G_PORTS),sum(TOTAL_40G_PORTS),sum(TOTAL_100G_PORTS),sum(CONNECTED_1G),sum(CONNECTED_10G),sum(CONNECTED_40G),sum(CONNECTED_100G),sum(NOT_CONNECTED_1G),sum(NOT_CONNECTED_10G),sum(NOT_CONNECTED_40G),sum(NOT_CONNECTED_100G),sum(UNUSED_SFPS_1G),sum(UNUSED_SFPS_10G),sum(UNUSED_SFPS_40G),sum(UNUSED_SFPS_100G),sum(TOTAL_FAST_ETHERNET_PORTS),sum(CONNECTED_FAST_ETHERNET),sum(NOT_CONNECTED_FAST_ETHERNET),sum(TOTAL_25G_PORTS),sum(CONNECTED_25G),sum(NOT_CONNECTED_25G),sum(UNUSED_SFPS_25G) from edn_dc_capacity where SITE_ID='{siteObj['datacenter']}' and CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity) group by SITE_ID;"
            result = db.session.execute(queryString)
            for row in result:


                total_1g_ports = int(row[2])
                total_10g_ports = int(row[3])
                total_40g_ports = int(row[4])
                total_100g_ports = int(row[5])
                connected_1g = int(row[6])
                connected_10g = int(row[7])
                connected_40g = int(row[8])
                connected_100g = int(row[9])
                not_connect_1g = int(row[10])
                not_connect_10g = int(row[11])
                not_connect_40g = int(row[12])
                not_connect_100g = int(row[13])
                unused_sfps_1g = int(row[14])
                unused_sfps_10g = int(row[15])
                unused_sfps_40g = int(row[16])
                unused_sfps_100g = int(row[17])
                total_fast_ethernet = int(row[18])
                connected_fast_ethernet = int(row[19])
                not_connect_fast_ethernet = int(row[20])
                total_25_ports = int(row[21])
                connected_25g = int(row[22])
                not_connect_25g = int(row[23])
                unused_sfps_25g = int(row[24])
                objDict = {}
                total = (int(total_1g_ports)+int(total_10g_ports)+int(total_40g_ports)+int(total_100g_ports))
                
                objDict['total']=[]
                objDict['total'] = [{"name":"1G","value":total_1g_ports},{"name":'10G','value':total_10g_ports},{"name":'25G','value':total_25_ports},{"name":"40G",'value':total_40g_ports},{"name":"100G","value":total_100g_ports},{"name":"Fast Ethernet","value":total_fast_ethernet}]
                objDict['connected'] = [{"name":"1G","value":connected_1g},{"name":"10G","value":connected_10g},{"name":'25G','value':connected_25g},{"name":"40G","value":connected_40g},{"name":"100G","value":connected_100g},{"name":"Fast Ethernet","value":connected_fast_ethernet}]     
                objDict['not_connected'] = [{"name":"1G","value":not_connect_1g},{"name":"10G","value":not_connect_10g},{"name":'25G','value':not_connect_25g},{"name":"40G","value":not_connect_40g},{"name":"100G","value":not_connect_100g},{"name":"Fast Ethernet","value":not_connect_fast_ethernet}]    
                objDict['unused'] = [{"name":"1G","value":unused_sfps_1g},{"name":"10G","value":unused_sfps_10g},{"name":'25G','value':0},{"name":"40G","value":unused_sfps_40g},{"name":"100G","value":unused_sfps_100g}]   
                print(objDict,file=sys.stderr)
                for i in objDict:
                    print(objDict[i],type(objDict[i]),file=sys.stderr)
                return objDict,200

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/ednDCMDatacentersPerRegion',methods = ['GET'])
@token_required
def EdnDCMDatacentersPerRegion(user_data):
    if True:
        queryString = f"select count(distinct SITE_ID) from edn_dc_capacity where SITE_ID in (select SITE_ID from phy_table where REGION='WESTERN') and CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);"
        queryString1 = f"select count(distinct SITE_ID) from edn_dc_capacity where SITE_ID in (select SITE_ID from phy_table where REGION='EASTERN') and CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);"
        queryString2 = f"select count(distinct SITE_ID) from edn_dc_capacity where SITE_ID in (select SITE_ID from phy_table where REGION='CENTRAL') and CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity);"
        result = db.session.execute(queryString).scalar()
        result1 = db.session.execute(queryString1).scalar()
        result2 = db.session.execute(queryString2).scalar()
        objList = [
            {
                "name":"WESTERN",
                "value":result
            },
            {
                "name":"EASTERN",
                "value":result1
            },
            {
                "name":"CENTRAL",
                "value":result2
            }
        ]
        return jsonify(objList),200

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/ednDCMSwitchesPerDatacenter',methods=['GET'])
@token_required
def EdnDCMSwitchesPerDatacenter(user_data):
    if True:
        objList = []
        
        queryString = f"select distinct SITE_ID,OS_VERSION,count(OS_VERSION) from edn_dc_capacity where SITE_ID in (select distinct SITE_ID from seed_table where SITE_TYPE='DC' and SW_TYPE='IOS') and OS_VERSION='IOS' and CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity) group by OS_VERSION,SITE_ID;"
        result = db.session.execute(queryString)
        objDict = {} 
        for row in result:
               
            site_id = row[0]
            sw_type = row[1]
            count = row[2]
            if site_id in objDict:

                objDict[site_id] ["IOS"]= objDict[site_id]["IOS"]+count
            else:
                objDict[site_id] = {}
                objDict[site_id]["IOS"]=count
                objDict[site_id]["IOS-XE"]=0
                objDict[site_id]["NX-OS"]=0
                objDict[site_id]["ACI-SPINE"]=0
                objDict[site_id]["ACI-LEAF"]=0

        queryString = f"select distinct SITE_ID,OS_VERSION,count(OS_VERSION) from edn_dc_capacity where SITE_ID in (select distinct SITE_ID from seed_table where SITE_TYPE='DC' and SW_TYPE='IOS-XE') and OS_VERSION='IOS-XE' and CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity) group by OS_VERSION,SITE_ID;"
        result = db.session.execute(queryString)
        
        for row in result:
               
            site_id = row[0]
            sw_type = row[1]
            count = row[2]
            if site_id in objDict:

                objDict[site_id] ["IOS-XE"]= objDict[site_id]["IOS-XE"]+count
            else:
                objDict[site_id] = {}
                objDict[site_id]["IOS"]=0
                objDict[site_id]["IOS-XE"]=count
                objDict[site_id]["NX-OS"]=0
                objDict[site_id]["ACI-SPINE"]=0
                objDict[site_id]["ACI-LEAF"]=0
        
        queryString = f"select distinct SITE_ID,OS_VERSION,count(OS_VERSION) from edn_dc_capacity where SITE_ID in (select distinct SITE_ID from seed_table where SITE_TYPE='DC' and SW_TYPE='NX-OS') and OS_VERSION='NX-OS' and CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity) group by OS_VERSION,SITE_ID;"
        result = db.session.execute(queryString)
        
        for row in result:
               
            site_id = row[0]
            sw_type = row[1]
            count = row[2]
            if site_id in objDict:

                objDict[site_id] ["NX-OS"]= objDict[site_id]["NX-OS"]+count
            else:
                objDict[site_id] = {}
                objDict[site_id]["IOS"]=0
                objDict[site_id]["IOS-XE"]=0
                objDict[site_id]["NX-OS"]=count
                objDict[site_id]["ACI-SPINE"]=0
                objDict[site_id]["ACI-LEAF"]=0
            objList = []
            for site_id in objDict:
                dict = objDict[site_id]
                dict['name']=site_id
                objList.append(dict)
        
        queryString = f"select distinct SITE_ID,OS_VERSION,count(OS_VERSION) from edn_dc_capacity where SITE_ID in (select distinct SITE_ID from seed_table where SITE_TYPE='DC' and SW_TYPE='ACI-SPINE') and OS_VERSION='ACI-SPINE' and CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity) group by OS_VERSION,SITE_ID;"
        result = db.session.execute(queryString)
        for row in result:
            site_id = row[0]
            sw_type = row[1]
            count = row[2]
            if site_id in objDict:

                objDict[site_id] ["ACI-SPINE"]= objDict[site_id]["ACI-SPINE"]+count
            else:
                objDict[site_id] = {}
                objDict[site_id]["IOS"]=0
                objDict[site_id]["IOS-XE"]=0
                objDict[site_id]["NX-OS"]=0
                objDict[site_id]["ACI-SPINE"]=count
                objDict[site_id]["ACI-LEAF"]=0
            objList = []
            for site_id in objDict:
                dict = objDict[site_id]
                dict['name']=site_id
                objList.append(dict)

        queryString = f"select distinct SITE_ID,OS_VERSION,count(OS_VERSION) from edn_dc_capacity where SITE_ID in (select distinct SITE_ID from seed_table where SITE_TYPE='DC' and SW_TYPE='ACI-LEAF') and OS_VERSION='ACI-LEAF' and CREATION_DATE=(select max(CREATION_DATE) from edn_dc_capacity) group by OS_VERSION,SITE_ID;"
        result = db.session.execute(queryString)
        for row in result:
            site_id = row[0]
            sw_type = row[1]
            count = row[2   ]
            if site_id in objDict:
                objDict[site_id] ["ACI-LEAF"]= objDict[site_id]["ACI-LEAF"]+count
            else:
                objDict[site_id] = {}
                objDict[site_id]["IOS"]=0
                objDict[site_id]["IOS-XE"]=0
                objDict[site_id]["NX-OS"]=0
                objDict[site_id]["ACI-SPINE"]=0
                objDict[site_id]["ACI-LEAF"]=count
            objList = []
            
            for site_id in objDict:
                dict = objDict[site_id]
                dict['name']=site_id
                objList.append(dict)

        return jsonify(objList),200

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/igwDCMCounts',methods =['GET'])
@token_required
def IgwDCMCounts(user_data):
    if True:
        
        queryString = f" select count(distinct SITE_ID) from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);"
        result = db.session.execute(queryString).scalar()
        queryString1 = f'select count(DEVICE_ID) from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);'
        result1 = db.session.execute(queryString1).scalar()
        queryString2 = f'select sum(NOT_CONNECTED_1G) from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);'
        queryString3 = f'select sum(NOT_CONNECTED_10G) from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);'
        queryString4 = f'select sum(NOT_CONNECTED_40G) from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);'
        queryString5 = f'select sum(NOT_CONNECTED_100G) from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);'
        queryString12 = f'select coalesce(sum(NOT_CONNECTED_25G),0) from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);'
        queryString13 = f'select coalesce(sum(NOT_CONNECTED_FAST_ETHERNET),0) from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);'
        result2 = db.session.execute(queryString2).scalar()
        result3 = db.session.execute(queryString3).scalar()
        result4 = db.session.execute(queryString4).scalar()
        result5 = db.session.execute(queryString5).scalar()
        result12 = db.session.execute(queryString12).scalar()
        result13 = db.session.execute(queryString13).scalar()
        sum = int(result2)+int(result3)+int(result4)+int(result5)+int(result12)+int(result13)
        queryString6 = f'select sum(TOTAL_1G_PORTS) from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);'
        queryString7 = f'select sum(TOTAL_10G_PORTS) from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);'
        queryString8 = f'select sum(TOTAL_40G_PORTS) from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);'
        queryString9 = f'select sum(TOTAL_100G_PORTS) from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);'
        queryString10 = f'select sum(TOTAL_25G_PORTS) from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);'
        queryString11 = f'select sum(TOTAL_FAST_ETHERNET_PORTS) from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);'
        result6 = db.session.execute(queryString6).scalar()
        result7 = db.session.execute(queryString7).scalar()
        result8 = db.session.execute(queryString8).scalar()
        result9 = db.session.execute(queryString9).scalar()
        result10 = db.session.execute(queryString10).scalar()
        result11 = db.session.execute(queryString11).scalar()
        sum1 = result6+result7+result8+result9+result10+result11
        objList = [
            {
                "name":"DC Count",
                "value":result
            },
            {
                "name":"Switches Count",
                "value":result1
            },
            {
                "name":"Total Ports",
                "value":sum1
            },
            {
                "name":"Not Connected Ports",
                "value":sum
            }

        ]


        return jsonify(objList),200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route('/igwDCMDatacenters',methods = ['GET'])
@token_required
def IgwDCMDatacenters(user_data):
    if True:
        objList = []
        queryString = f" select distinct SITE_ID from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);"
        result = db.session.execute(queryString)
        for row in result:
            datacenters = row[0]
            objList.append(datacenters)
        objList.append("ALL")
        return jsonify(objList),200
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/igwDCMPortsGroup',methods= ['POST'])
@token_required
def IgwDCMPortsGroup(user_data):
    if True:
        siteObj = request.get_json()
        print(siteObj,file = sys.stderr)
        queryString = ''
        if siteObj['datacenter']=='ALL':
            queryString = f"select sum(TOTAL_1G_PORTS),sum(TOTAL_10G_PORTS),sum(TOTAL_40G_PORTS),sum(TOTAL_100G_PORTS),sum(CONNECTED_1G),sum(CONNECTED_10G),sum(CONNECTED_40G),sum(CONNECTED_100G),sum(NOT_CONNECTED_1G),sum(NOT_CONNECTED_10G),sum(NOT_CONNECTED_40G),sum(NOT_CONNECTED_100G),sum(UNUSED_SFPS_1G),sum(UNUSED_SFPS_10G),sum(UNUSED_SFPS_40G),sum(UNUSED_SFPS_100G),sum(TOTAL_FAST_ETHERNET_PORTS),sum(CONNECTED_FAST_ETHERNET),sum(NOT_CONNECTED_FAST_ETHERNET),sum(TOTAL_25G_PORTS),sum(CONNECTED_25G),sum(NOT_CONNECTED_25G),sum(UNUSED_SFPS_25G) from igw_dc_capacity where CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);"    
            result = db.session.execute(queryString)
            for row in result:


                total_1g_ports = int(row[0])
                total_10g_ports = int(row[1])
                total_40g_ports = int(row[2])
                total_100g_ports = int(row[3])
                connected_1g = int(row[4])
                connected_10g = int(row[5])
                connected_40g = int(row[6])
                connected_100g = int(row[7])
                not_connect_1g = int(row[8])
                not_connect_10g = int(row[9])
                not_connect_40g = int(row[10])
                not_connect_100g = int(row[11])
                unused_sfps_1g = int(row[12])
                unused_sfps_10g = int(row[13])
                unused_sfps_40g = int(row[14])
                unused_sfps_100g = int(row[15])
                total_fast_ethernet = int(row[16])
                connected_fast_ethernet = int(row[17])
                not_connect_fast_ethernet = int(row[18])
                total_25_ports = int(row[19])
                connected_25g = int(row[20])
                not_connect_25g = int(row[21])
                unused_sfps_25g = int(row[22])
                objDict = {}
                total = (int(total_1g_ports)+int(total_10g_ports)+int(total_40g_ports)+int(total_100g_ports))
                
                objDict['total']=[]
                objDict['total'] = [{"name":"1G","value":total_1g_ports},{"name":'10G','value':total_10g_ports},{"name":'25G','value':total_25_ports},{"name":"40G",'value':total_40g_ports},{"name":"100G","value":total_100g_ports},{"name":"Fast Ethernet","value":total_fast_ethernet}]
                objDict['connected'] = [{"name":"1G","value":connected_1g},{"name":"10G","value":connected_10g},{"name":'25G','value':connected_25g},{"name":"40G","value":connected_40g},{"name":"100G","value":connected_100g},{"name":"Fast Ethernet","value":connected_fast_ethernet}]     
                objDict['not_connected'] = [{"name":"1G","value":not_connect_1g},{"name":"10G","value":not_connect_10g},{"name":'25G','value':not_connect_25g},{"name":"40G","value":not_connect_40g},{"name":"100G","value":not_connect_100g},{"name":"Fast Ethernet","value":not_connect_fast_ethernet}]    
                objDict['unused'] = [{"name":"1G","value":unused_sfps_1g},{"name":"10G","value":unused_sfps_10g},{"name":'25G','value':unused_sfps_25g},{"name":"40G","value":unused_sfps_40g},{"name":"100G","value":unused_sfps_100g},{"name":"Fast Ethernet","value":0}]   
                print(objDict,file=sys.stderr)
                for i in objDict:
                    print(objDict[i],type(objDict[i]),file=sys.stderr)
                return objDict,200
        else:

            queryString = f"select SITE_ID,COUNT(SITE_ID),sum(TOTAL_1G_PORTS),sum(TOTAL_10G_PORTS),sum(TOTAL_40G_PORTS),sum(TOTAL_100G_PORTS),sum(CONNECTED_1G),sum(CONNECTED_10G),sum(CONNECTED_40G),sum(CONNECTED_100G),sum(NOT_CONNECTED_1G),sum(NOT_CONNECTED_10G),sum(NOT_CONNECTED_40G),sum(NOT_CONNECTED_100G),sum(UNUSED_SFPS_1G),sum(UNUSED_SFPS_10G),sum(UNUSED_SFPS_40G),sum(UNUSED_SFPS_100G),coalesce(sum(TOTAL_FAST_ETHERNET_PORTS),0),coalesce(sum(CONNECTED_FAST_ETHERNET),0),coalesce(sum(NOT_CONNECTED_FAST_ETHERNET),0),coalesce(sum(TOTAL_25G_PORTS),0),coalesce(sum(CONNECTED_25G),0),coalesce(sum(NOT_CONNECTED_25G),0),coalesce(sum(UNUSED_SFPS_25G),0) from igw_dc_capacity where SITE_ID='{siteObj['datacenter']}' and CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity) group by SITE_ID;"
            result = db.session.execute(queryString)
            for row in result:

                site_id = row[0]
                count_site_id = row[1]
                total_1g_ports = int(row[2])
                total_10g_ports = int(row[3])
                total_40g_ports = int(row[4])
                total_100g_ports = int(row[5])
                connected_1g = int(row[6])
                connected_10g = int(row[7])
                connected_40g = int(row[8])
                connected_100g = int(row[9])
                not_connect_1g = int(row[10])
                not_connect_10g = int(row[11])
                not_connect_40g = int(row[12])
                not_connect_100g = int(row[13])
                unused_sfps_1g = int(row[14])
                unused_sfps_10g = int(row[15])
                unused_sfps_40g = int(row[16])
                unused_sfps_100g = int(row[17])
                total_fast_ethernet = int(row[18])
                connected_fast_ethernet = int(row[19])
                not_connect_fast_ethernet = int(row[20])
                total_25_ports = int(row[21])
                connected_25g = int(row[22])
                not_connect_25g = int(row[23])
                unused_sfps_25g = int(row[24])
                objDict = {}
                total = (int(total_1g_ports)+int(total_10g_ports)+int(total_40g_ports)+int(total_100g_ports))
                
                objDict['total']=[]
                objDict['total'] = [{"name":"1G","value":total_1g_ports},{"name":'10G','value':total_10g_ports},{"name":'25G','value':total_25_ports},{"name":"40G",'value':total_40g_ports},{"name":"100G","value":total_100g_ports},{"name":"Fast Ethernet","value":total_fast_ethernet}]
                objDict['connected'] = [{"name":"1G","value":connected_1g},{"name":"10G","value":connected_10g},{"name":'25G','value':connected_25g},{"name":"40G","value":connected_40g},{"name":"100G","value":connected_100g},{"name":"Fast Ethernet","value":connected_fast_ethernet}]     
                objDict['not_connected'] = [{"name":"1G","value":not_connect_1g},{"name":"10G","value":not_connect_10g},{"name":'25G','value':not_connect_25g},{"name":"40G","value":not_connect_40g},{"name":"100G","value":not_connect_100g},{"name":"Fast Ethernet","value":not_connect_fast_ethernet}]    
                objDict['unused'] = [{"name":"1G","value":unused_sfps_1g},{"name":"10G","value":unused_sfps_10g},{"name":'25G','value':unused_sfps_25g},{"name":"40G","value":unused_sfps_40g},{"name":"100G","value":unused_sfps_100g}]   
                print(objDict,file=sys.stderr)
                for i in objDict:
                    print(objDict[i],type(objDict[i]),file=sys.stderr)
                return objDict,200

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/igwDCMDatacentersPerRegion',methods = ['GET'])
@token_required
def IgwDCMDatacentersPerRegion(user_data):
    if True:
        queryString = f"select count(distinct SITE_ID) from igw_dc_capacity where SITE_ID in (select SITE_ID from phy_table where REGION='WESTERN') and CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);"
        queryString1 = f"select count(distinct SITE_ID) from igw_dc_capacity where SITE_ID in (select SITE_ID from phy_table where REGION='EASTERN') and CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);"
        queryString2 = f"select count(distinct SITE_ID) from igw_dc_capacity where SITE_ID in (select SITE_ID from phy_table where REGION='CENTRAL') and CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity);"
        result = db.session.execute(queryString).scalar()
        result1 = db.session.execute(queryString1).scalar()
        result2 = db.session.execute(queryString2).scalar()
        objList = [
            {
                "name":"WESTERN",
                "value":result
            },
            {
                "name":"EASTERN",
                "value":result1
            },
            {
                "name":"CENTRAL",
                "value":result2
            }
        ]
        return jsonify(objList),200

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/igwDCMSwitchesPerDatacenter',methods=['GET'])
@token_required
def IgwDCMSwitchesPerDatacenter(user_data):
    if True:
        objList = []
        
        queryString = f"select distinct SITE_ID,OS_VERSION,count(OS_VERSION) from igw_dc_capacity where OS_VERSION='ACI-SPINE' and CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity) group by OS_VERSION,SITE_ID;"
        result = db.session.execute(queryString)
        objDict = {} 
        for row in result:
               
            site_id = row[0]
            sw_type = row[1]
            count = row[2]
            if site_id in objDict:

                objDict[site_id] ["ACI-SPINE"]= objDict[site_id]["ACI-SPINE"]+count
            else:
                objDict[site_id] = {}
                objDict[site_id]["ACI-SPINE"]=count
                objDict[site_id]["ACI-LEAF"]=0

        queryString = f"select distinct SITE_ID,OS_VERSION,count(OS_VERSION) from igw_dc_capacity where OS_VERSION='ACI-LEAF' and CREATION_DATE=(select max(CREATION_DATE) from igw_dc_capacity) group by OS_VERSION,SITE_ID;"
        result = db.session.execute(queryString)
        
        for row in result:
               
            site_id = row[0]
            sw_type = row[1]
            count = row[2]
            if site_id in objDict:

                objDict[site_id] ["ACI-LEAF"]= objDict[site_id]["ACI-LEAF"]+count
            else:
                objDict[site_id] = {}
                objDict[site_id]["ACI-SPINE"]=0
                objDict[site_id]["ACI-LEAF"]=count
        
            objList = []
            for site_id in objDict:
                dict = objDict[site_id]
                dict['name']=site_id
                objList.append(dict)
        
        return jsonify(objList),200

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401