import gzip
import sys, json
from flask_jsonpify import jsonify
from flask import Flask, request, make_response, Response, session
from app import app ,db , phy_engine, tz
from app.models.phy_mapping_models import *
from sqlalchemy import func
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask_cors import CORS, cross_origin
from app.middleware import token_required
import traceback
from itertools import chain
from operator import itemgetter

def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%d-%m-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

@app.route('/getEdnMacServiceMappingCards', methods= ['GET'])
@token_required
def GetEdnMacServiceMappingCards(user_data):
    if True:
        try:
            queryString = f"select count(distinct(device_b_mac)) from edn_mac_legacy where creation_date = (SELECT max(creation_date) FROM edn_mac_legacy);"
            result = phy_engine.execute(queryString).scalar()
            queryString1 = f"select count(distinct(device_b_ip)) from edn_mac_legacy where creation_date = (SELECT max(creation_date) FROM edn_mac_legacy);"
            result1 = phy_engine.execute(queryString1).scalar()
            queryString2 = f"select count(distinct(device_b_mac)) from edn_mac_legacy where creation_date = (SELECT max(creation_date) FROM edn_mac_legacy) AND modified_by = 'IT SYNC';"
            result2 = phy_engine.execute(queryString2).scalar()
            queryString3 = f"select count(distinct(device_b_mac)) from edn_mac_legacy where creation_date = (SELECT max(creation_date) FROM edn_mac_legacy) AND service_vendor <> 'IT' AND service_vendor IS NOT NULL;"
            result3 = phy_engine.execute(queryString3).scalar()
            queryString4 = f"select count(distinct(device_b_ip)) from edn_mac_legacy where creation_date = (SELECT max(creation_date) FROM edn_mac_legacy) AND f5_lb IS NOT NULL;"
            result4 = phy_engine.execute(queryString4).scalar()

            objList = [
                {
                    "name": "Learned MAC Address",
                    "value": result
                },
                {
                    "name": "Learned IP Address",
                    "value": result1
                },
                {
                    "name": "Mapped IT Services",
                    "value": result2
                },
                {
                    "name": "Mapped Tech Op Services",
                    "value": result3
                },
                {
                    "name": "Matched Nodes Behind F5",
                    "value": result4
                }
            ]
            return jsonify(objList), 200
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

@app.route('/getServiceMappingWeeklyInsertedCount',methods = ['GET'])
@token_required
def GetItServiceMappingWeeklyInsertedCount(user_data):
    if True:
        try:            
            queryString = f"select count(*) from it_physical_servers_table where creation_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_app_table where creation_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result1 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_os_table where creation_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result2 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_ip_table where creation_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result3 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_mac_table where creation_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result4 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_owner_table where creation_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result5 = phy_engine.execute(queryString).scalar()

            objList = [
                {
                    "name": "Physical Servers",
                    "value": result
                },
                {
                    "name": "App",
                    "value": result1
                },
                {
                    "name": "OS",
                    "value": result2
                },
                {
                    "name": "IP",
                    "value": result3
                },
                {
                    "name": "MAC",
                    "value": result4
                },
                {
                    "name": "Owner",
                    "value": result5
                }
            ]

            newList = sorted(objList, key=itemgetter('value'), reverse=True)

            return jsonify(newList),200
        
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

@app.route('/getServiceMappingWeeklyUpdatedCount',methods = ['GET'])
@token_required
def GetServiceMappingWeeklyUpdatedCount(user_data):
    if True:
        try:            
            queryString = f"select count(*) from it_physical_servers_table where modification_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_app_table where modification_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result1 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_os_table where modification_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result2 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_ip_table where modification_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result3 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_mac_table where modification_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result4 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_owner_table where modification_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result5 = phy_engine.execute(queryString).scalar()

            objList = [
                {
                    "name": "Physical Servers",
                    "value": result
                },
                {
                    "name": "App",
                    "value": result1
                },
                {
                    "name": "OS",
                    "value": result2
                },
                {
                    "name": "IP",
                    "value": result3
                },
                {
                    "name": "MAC",
                    "value": result4
                },
                {
                    "name": "Owner",
                    "value": result5
                }
            ]

            newList = sorted(objList, key=itemgetter('value'), reverse=True)

            return jsonify(newList),200
        
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

@app.route('/getServiceMappingTotalMacCountPerSiteType',methods = ['GET'])
@token_required
def GetServiceMappingTotalMacCountPerSiteType(user_data):
    if True:
        objList=[]
        try:
            
            queryString = f"select distinct(SUBSTRING_INDEX(device_a_name, '-', 1)) as name, count(distinct(device_b_mac)) as count from edn_mac_legacy where creation_date = (SELECT max(creation_date) FROM edn_mac_legacy) group by name order by count DESC;"
            result = phy_engine.execute(queryString)
            objDict = {}
            
            for row in result:
                device_name = row[0]
                total_count = row[1]
                if device_name in objDict:
                    count = 'value'
                    objDict[device_name][count] = total_count
                    print(objDict, file=sys.stderr)
                else:
                    objDict[device_name] = {}
                    count = 'value'
                    objDict[device_name]['value'] = 0
                    objDict[device_name][count] = total_count
            objList = []
            for device_name in objDict:
                dict = objDict[device_name]
                dict['name'] = device_name
                objList.append(dict)

            return jsonify(objList), 200
        
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

@app.route('/getServiceMappingTotalIPCountPerSiteType',methods = ['GET'])
@token_required
def GetServiceMappingTotalIPCountPerSiteType(user_data):
    if True:
        objList=[]
        try:
            
            queryString = f"select distinct(SUBSTRING_INDEX(device_a_name, '-', 1)) as name, count(distinct(device_b_ip)) as count from edn_mac_legacy where creation_date = (SELECT max(creation_date) FROM edn_mac_legacy) group by name order by count DESC;"
            result = phy_engine.execute(queryString)
            objDict = {}
            
            for row in result:
                device_name = row[0]
                total_count = row[1]
                if device_name in objDict:
                    count = 'value'
                    objDict[device_name][count] = total_count
                    print(objDict, file=sys.stderr)
                else:
                    objDict[device_name] = {}
                    count = 'value'
                    objDict[device_name]['value'] = 0
                    objDict[device_name][count] = total_count
            objList = []
            for device_name in objDict:
                dict = objDict[device_name]
                dict['name'] = device_name
                objList.append(dict)

            return jsonify(objList), 200
        
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

@app.route('/getServiceMappingItMappedTotalMacCountPerSiteType',methods = ['GET'])
@token_required
def GetServiceMappingItMappedTotalMacCountPerSiteType(user_data):
    if True:
        objList=[]
        try:
            
            queryString = f"select distinct(SUBSTRING_INDEX(device_a_name, '-', 1)) as name, count(distinct(device_b_mac)) as count from edn_mac_legacy where creation_date = (SELECT max(creation_date) FROM edn_mac_legacy) AND modified_by = 'IT SYNC' group by name order by count DESC;"
            result = phy_engine.execute(queryString)
            objDict = {}
            
            for row in result:
                device_name = row[0]
                total_count = row[1]
                if device_name in objDict:
                    count = 'value'
                    objDict[device_name][count] = total_count
                    print(objDict, file=sys.stderr)
                else:
                    objDict[device_name] = {}
                    count = 'value'
                    objDict[device_name]['value'] = 0
                    objDict[device_name][count] = total_count
            objList = []
            for device_name in objDict:
                dict = objDict[device_name]
                dict['name'] = device_name
                objList.append(dict)

            return jsonify(objList), 200
        
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

@app.route("/getServiceMappingTopFiveApps", methods = ['GET'])
@token_required
def GetServiceMappingTopFiveApps(user_data):
    if True:
        try:
            objList = []
            apps = phy_engine.execute(f"select distinct(app_name) as name, count(distinct(device_b_mac)) as count from edn_mac_legacy where creation_date = (SELECT max(creation_date) FROM edn_mac_legacy) AND app_name <> 'NA' AND app_name <> '' group by name order by count DESC LIMIT 5;")
            for name, count in apps:
                sites = phy_engine.execute(f"select distinct(SUBSTRING_INDEX(device_a_name, '-', 1)) as name, count(distinct(device_b_mac)) as count from edn_mac_legacy where creation_date = (SELECT max(creation_date)FROM edn_mac_legacy) AND app_name = '{name}' group by name order by count;")
                dict = {}
                dict['app_name'] = name
                dict['no_of_macs'] = count
                dict['sites'] = []
                for site, no in sites:
                    dict['sites'].append( site + "(" + str(no) + ")")
                dict['sites'] = ", ".join(dict['sites'])

                objList.append(dict)

            return jsonify(objList), 200
        
        except Exception as e:
            return str(e), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getEdnMacServiceMappingCardsLineGraph', methods = ['GET'])
@token_required
def GetEdnMacServiceMappingCardsLineGraph(user_data):
    try:
        objList = []
        queryString = f"select count(distinct(device_b_mac)), CREATION_DATE from edn_mac_legacy group by CREATION_DATE ORDER by CREATION_DATE DESC;"
        result = phy_engine.execute(queryString)
        count = 0
        count1 = 0
        count2 = 0
        for row in result:
            dict = {}
            sum = int(row[0])
            creationDate = FormatDate(row[1])
            dict["MAC-ADDRESS"] = sum
            dict["date"] = creationDate
            objList.append(dict)
            count+=1
            print('Number of iterations for MAC-ADDRESS:', count, file=sys.stderr)
            if count>=12:
                print("Maximum limit for the dates has reached", file=sys.stderr)
                break

        queryString1 = f"select count(distinct(device_b_ip)),CREATION_DATE from edn_mac_legacy group by CREATION_DATE ORDER by CREATION_DATE DESC;"
        result1 = phy_engine.execute(queryString1)
        for row in result1:
            dict = {}
            sum = int(row[0])
            creationDate = FormatDate(row[1])
            dict["IP-ADDRESS"] = sum
            dict["date"] = creationDate
            objList.append(dict)
            count1+=1
            print('Number of iterations for IP-ADDRESS:', count1, file=sys.stderr)
            if count1>=12:
                print("Maximum limit for the dates has reached", file=sys.stderr)
                break

        queryString2 = f"select count(distinct(device_b_mac)),CREATION_DATE from edn_mac_legacy where modified_by = 'IT SYNC' group by CREATION_DATE ORDER by CREATION_DATE DESC;"
        result2 = phy_engine.execute(queryString2)
        for row in result2:
            dict = {}
            sum = int(row[0])
            creationDate = FormatDate(row[1])
            dict["IT Mapped"] = sum
            dict["date"] = creationDate
            objList.append(dict)
            count2+=1
            print('Number of iterations for IT Mapped(MAC-ADDRESS):', count2, file=sys.stderr)
            if count2>=12:
                print("Maximum limit for the dates has reached", file=sys.stderr)
                break
        
        new_obj_list = {}
        for obj in objList:
            if obj['date'] not in new_obj_list:
                new_obj_list[obj['date']] = {"MAC-ADDRESS":0, "IP-ADDRESS":0, "IT Mapped": 0, "date": obj['date']}
            if obj.get('MAC-ADDRESS'):
                new_obj_list[obj['date']]['MAC-ADDRESS'] = obj.get('MAC-ADDRESS')
            if obj.get('IP-ADDRESS'):
                new_obj_list[obj['date']]['IP-ADDRESS'] = obj.get('IP-ADDRESS')
            if obj.get('IT Mapped'):
                new_obj_list[obj['date']]['IT Mapped'] = obj.get('IT Mapped')

        finalList = []
        finalList = (list(new_obj_list.values()))
        finalList.sort(key = lambda x: datetime.strptime(x['date'], '%d-%m-%Y'))

        return jsonify(finalList),200
    
    except Exception as e:
        traceback.print_exc()
        return str(e), 500

@app.route('/getServiceMappingWeeklyInsertedCountLineGraph', methods = ['GET'])
@token_required
def GetServiceMappingWeeklyInsertedCountGraph(user_data):
    try:
        objList = []
        queryString = f"select physical_servers_inserted, apps_inserted, os_inserted, ips_inserted, macs_inserted, owners_inserted, CREATION_DATE from it_services_snapshots_table ORDER by CREATION_DATE DESC;"
        result = phy_engine.execute(queryString)
        count = 0

        for row in result:
            dict = {}
            phy = int(row[0])
            app = int(row[1])
            os = int(row[2])
            ip = int(row[3])
            mac = int(row[4])
            owner = int(row[5])
            creationDate = FormatDate(row[6])
            dict["PhysicalServer"] = phy
            dict["App"] = app
            dict["OS"] = os
            dict["IP"] = ip
            dict["MAC"] = mac
            dict["Owner"] = owner
            dict["date"] = creationDate
            objList.append(dict)
            count+=1
            print('Number of iterations for Data:', count, file=sys.stderr)
            if count>=12:
                print("Maximum limit for the dates has reached", file=sys.stderr)
                break
        
        new_obj_list = {}
        for obj in objList:
            if obj['date'] not in new_obj_list:
                new_obj_list[obj['date']] = {"PhysicalServer":0, "App":0, "OS": 0, "IP": 0, "MAC": 0, "Owner": 0, "date": obj['date']}
            if obj.get('PhysicalServer'):
                new_obj_list[obj['date']]['PhysicalServer'] = obj.get('PhysicalServer')
            if obj.get('App'):
                new_obj_list[obj['date']]['App'] = obj.get('App')
            if obj.get('OS'):
                new_obj_list[obj['date']]['OS'] = obj.get('OS')
            if obj.get('IP'):
                new_obj_list[obj['date']]['IP'] = obj.get('IP')
            if obj.get('MAC'):
                new_obj_list[obj['date']]['MAC'] = obj.get('MAC')
            if obj.get('Owner'):
                new_obj_list[obj['date']]['Owner'] = obj.get('Owner')

        finalList = []
        finalList = (list(new_obj_list.values()))
        finalList.sort(key = lambda x: datetime.strptime(x['date'], '%d-%m-%Y'))

        return jsonify(finalList),200
    
    except Exception as e:
        traceback.print_exc()
        return str(e), 500

@app.route('/getServiceMappingWeeklyUpdatedCountLineGraph', methods = ['GET'])
@token_required
def GetServiceMappingWeeklyUpdatedCountGraph(user_data):
    try:
        objList = []
        queryString = f"select physical_servers_updated, apps_updated, os_updated, ips_updated, macs_updated, owners_updated, CREATION_DATE from it_services_snapshots_table ORDER by CREATION_DATE DESC;"
        result = phy_engine.execute(queryString)
        count = 0

        for row in result:
            dict = {}
            phy = int(row[0])
            app = int(row[1])
            os = int(row[2])
            ip = int(row[3])
            mac = int(row[4])
            owner = int(row[5])
            creationDate = FormatDate(row[6])
            dict["PhysicalServer"] = phy
            dict["App"] = app
            dict["OS"] = os
            dict["IP"] = ip
            dict["MAC"] = mac
            dict["Owner"] = owner
            dict["date"] = creationDate
            objList.append(dict)
            count+=1
            print('Number of iterations for Data:', count, file=sys.stderr)
            if count>=12:
                print("Maximum limit for the dates has reached", file=sys.stderr)
                break
        
        new_obj_list = {}
        for obj in objList:
            if obj['date'] not in new_obj_list:
                new_obj_list[obj['date']] = {"PhysicalServer":0, "App":0, "OS": 0, "IP": 0, "MAC": 0, "Owner": 0, "date": obj['date']}
            if obj.get('PhysicalServer'):
                new_obj_list[obj['date']]['PhysicalServer'] = obj.get('PhysicalServer')
            if obj.get('App'):
                new_obj_list[obj['date']]['App'] = obj.get('App')
            if obj.get('OS'):
                new_obj_list[obj['date']]['OS'] = obj.get('OS')
            if obj.get('IP'):
                new_obj_list[obj['date']]['IP'] = obj.get('IP')
            if obj.get('MAC'):
                new_obj_list[obj['date']]['MAC'] = obj.get('MAC')
            if obj.get('Owner'):
                new_obj_list[obj['date']]['Owner'] = obj.get('Owner')

        finalList = []
        finalList = (list(new_obj_list.values()))
        finalList.sort(key = lambda x: datetime.strptime(x['date'], '%d-%m-%Y'))

        return jsonify(finalList),200
    
    except Exception as e:
        traceback.print_exc()
        return str(e), 500

@app.route("/ednServiceMatchedBy", methods = ['GET'])
@token_required
def EdnServiceMatchedBy(user_data):
    if True:
        try:

            objList = objList2=[]
            queryString = f"select SERVICE_MATCHED_BY ,count(SERVICE_MATCHED_BY) from edn_mac_legacy WHERE SERVICE_MATCHED_BY='MAC' and creation_date = (SELECT max(creation_date) FROM edn_mac_legacy) group by SERVICE_MATCHED_BY;"
            result =phy_engine.execute(queryString)

            objDict = {}
            objDict['name'] = 'MAC'
            for row in result:  
                if 'value' in objDict:
                    objDict['value']= objDict['value']+row[1]
                else:
                    objDict['value'] = row[1]
            #print(f"### {objDict}", file=sys.stderr)
            objList.append(objDict)

            
            queryString = f"select SERVICE_MATCHED_BY ,count(SERVICE_MATCHED_BY) from edn_mac_legacy WHERE SERVICE_MATCHED_BY='IP' and creation_date = (SELECT max(creation_date) FROM edn_mac_legacy) group by SERVICE_MATCHED_BY;"
            result = phy_engine.execute(queryString)

            for row in result:
                objDict = {}
                objDict["name"] = row[0]
                objDict['value'] = row[1]
                objList.append(objDict)
            
            queryString = "select SERVICE_MATCHED_BY ,count(SERVICE_MATCHED_BY) from edn_mac_legacy WHERE SERVICE_MATCHED_BY LIKE '%%IP%%'and SERVICE_MATCHED_BY LIKE '%%MAC%%' and creation_date = (SELECT max(creation_date) FROM edn_mac_legacy) group by SERVICE_MATCHED_BY;"
            result = phy_engine.execute(queryString)

            for row in result:
                objDict = {}
                objDict["name"] ="MAC and IP"
                objDict['value'] = row[1]
                objList.append(objDict)
            
            mac_ip_sum = 0
            for item in objList:
                if item["name"] == "MAC and IP":
                    mac_ip_sum += item["value"]

            new_data = []
            new_data.append({"name": "MAC and IP", "value": mac_ip_sum})

            for item in objList:
                if item["name"] != "MAC and IP":
                    new_data.append(item)
                        
                

            return jsonify(new_data),200
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

@app.route("/ednLearnedMacAddresses", methods = ['GET'])
@token_required
def EdnLearnedMacAddresses(user_data):
    if True:
        try:

            objList = objList2=[]
            queryString = f"SELECT SUM(count) FROM (SELECT COUNT(DEVICE_B_IP) as count FROM edn_mac_legacy  WHERE DEVICE_B_IP != '' AND DEVICE_B_IP != '0.0.0.0'  AND creation_date = (SELECT MAX(creation_date) FROM edn_mac_legacy)  GROUP BY DEVICE_B_IP) as count_result;"
            result =phy_engine.execute(queryString)

            objDict = {}
            #objDict['name'] = 'Device B IP'
            for row in result:
                objDict = {}
                objDict["name"] = "With IP"
                if row[0] is None:
                    objDict['value']= 0
                else:
                    objDict['value'] = int(row[0])
                objList.append(objDict)
            
            queryString = f"SELECT SUM(count) FROM (SELECT COUNT(DEVICE_B_IP) as count FROM edn_mac_legacy  WHERE ( DEVICE_B_IP = '' or DEVICE_B_IP = ' ' or DEVICE_B_IP = '0.0.0.0' or DEVICE_B_IP IS NULL ) AND creation_date = (SELECT MAX(creation_date) FROM edn_mac_legacy)  GROUP BY DEVICE_B_IP) as count_result;"

            result = phy_engine.execute(queryString)

            for row in result:
                objDict = {}
                objDict["name"] = "Without IP"
                if row[0] is None:
                    objDict['value']= 0
                else:
                    objDict['value'] = int(row[0])
                objList.append(objDict)
            
          
                

            return jsonify(objList),200
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

@app.route("/ednMappedTechOpServicesVServiceVendorsPieGraph", methods = ['GET'])
@token_required
def GetEdnMappedTechOpServicesVServiceVendorsPieGraph(user_data):
    objDict = {}
    queryString = "select service_vendor, count(distinct(device_b_mac)) from edn_mac_legacy where creation_date = (SELECT max(creation_date) FROM edn_mac_legacy) AND service_vendor <> 'IT' AND service_vendor IS NOT NULL group by service_vendor;"
    result = phy_engine.execute(queryString)
    for row in result:
        node = row[0]
        monitor_status = row[1]
        if node in objDict:
            count = 'value'
            objDict[node][count] = monitor_status
            print(objDict, file=sys.stderr)
        else:
            objDict[node] = {}
            count = 'value'
            objDict[node]['value'] = 0
            objDict[node][count] = monitor_status
    objList = []
    for node in objDict:
        dict = objDict[node]
        dict['name'] = node
        objList.append(dict)
    # print(objList, file=sys.stderr)
    return jsonify(objList), 200

@app.route("/ednServicesVServiceVendorPieGraph", methods = ['GET'])
@token_required
def GetEdnServicesVServiceVendorPieGraph(user_data):
    objDict = {}
    queryString = "select service_vendor, count(*) from edn_service_mapping group by service_vendor;"
    result = phy_engine.execute(queryString)
    for row in result:
        node = row[0]
        monitor_status = row[1]
        if node in objDict:
            count = 'value'
            objDict[node][count] = monitor_status
            print(objDict, file=sys.stderr)
        else:
            objDict[node] = {}
            count = 'value'
            objDict[node]['value'] = 0
            objDict[node][count] = monitor_status
    objList = []
    for node in objDict:
        dict = objDict[node]
        dict['name'] = node
        objList.append(dict)
    # print(objList, file=sys.stderr)
    return jsonify(objList), 200
