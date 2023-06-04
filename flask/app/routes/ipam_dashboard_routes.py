from lib2to3.pgen2 import token
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

@app.route('/ednIpamPerRegion',methods = ['GET'])
@token_required
def EdnIpamPerRegion(user_data):
    if True:
        # queryString = f"select count(distinct IP_ADDRESS) from edn_ipam_table where REGION='WESTERN' and CREATION_DATE=(select max(CREATION_DATE) from edn_ipam_table);"
        # queryString1 = f"select count(distinct IP_ADDRESS) from edn_ipam_table where REGION='EASTERN' and CREATION_DATE=(select max(CREATION_DATE) from edn_ipam_table);"
        # queryString2 = f"select count(distinct IP_ADDRESS) from edn_ipam_table where REGION='CENTRAL' and CREATION_DATE=(select max(CREATION_DATE) from edn_ipam_table);"
        # result = db.session.execute(queryString).scalar()
        # result1 = db.session.execute(queryString1).scalar()
        # result2 = db.session.execute(queryString2).scalar()
        # objList = [
        #     {
        #         "name":"WESTERN",
        #         "value":result
        #     },
        #     {
        #         "name":"EASTERN",
        #         "value":result1
        #     },
        #     {
        #         "name":"CENTRAL",
        #         "value":result2
        #     }
        # ]
        queryString = f"select region,count(distinct IP_ADDRESS) from edn_ipam_table where CREATION_DATE in (select max(CREATION_DATE) from edn_ipam_table) group by region;"
        result = db.session.execute(queryString)
        objList = []
        for row in result:
            objDict = {}
            region = row[0]
            count = row[1]
            objDict["name"] = region
            objDict['value'] = count
            objList.append(objDict)
        print(objList,file=sys.stderr)
        return jsonify(objList),200
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/ednIpamSites',methods = ['GET'])
@token_required
def EdnIpamSites(user_data):
    if True:
        queryString = f"select SITE_TYPE,COUNT(distinct IP_ADDRESS) from edn_ipam_table where CREATION_DATE=(select max(CREATION_DATE) from edn_ipam_table) group by SITE_TYPE;"
        result = db.session.execute(queryString)
        objList = []
        for row in result:
            objDict = {}
            site_type = row[0] 
            count = row[1]
            objDict['name'] = site_type
            objDict['value'] = count
            objList.append(objDict)
        print(objList,file=sys.stderr)
        return jsonify(objList),200
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/ednIpamIpCount',methods = ['GET'])
@token_required
def EdnIpamIpCount(user_data):
    if True:
        queryString = f"select count(distinct IP_ADDRESS) from edn_ipam_table where CREATION_DATE=(select max(CREATION_DATE) from edn_ipam_table);"
        result = db.session.execute(queryString).scalar()
        objList = [
            {
                "name":"IP Addresses",
                "value":result
            }
        ]
        return jsonify(objList),200
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getEdnIpamLastTenFetches',methods = ['GET'])
@token_required
def GetEdnIpamLastTenFetches(user_data):


    if True:
        objList = []
        queryString = f"select count(*),CREATION_DATE from edn_ipam_table where CREATION_DATE in (select MAX(CREATION_DATE) as date from edn_ipam_table group by YEAR(CREATION_DATE), MONTH(CREATION_DATE),DAY(CREATION_DATE)) group by CREATION_DATE ORDER by CREATION_DATE;"
        result = db.session.execute(queryString)
        count = 0
        for row in result:
            objDict = {}
            count = row[0]
            fetchDate = row[1]
            objDict['Fetched Count'] = count
            objDict['Fetch Date'] = FormatDate(fetchDate)
            objList.append(objDict)
            count+=1
            if count==10:
                print("Maximum count for the fetch has reached: ",count,file=sys.stderr)
        
        final_array =[]
        unique_dates=list(set([date['Fetch Date'] for date in objList]))
        for date in unique_dates:
            dic={}
            dic["Fetch Date"]= date
            for record in objList:
                if record["Fetch Date"]== date:
                    dic.update(record)
            final_array.append(dic)
        final_array.sort(key = lambda x: datetime.strptime(x['Fetch Date'], '%d-%m-%Y'))
        print(final_array,file=sys.stderr)
        return jsonify(final_array),200
        # return jsonify(objList),200
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/igwIpamPerRegion',methods = ['GET'])
@token_required
def IgwIpamPerRegion(user_data):
    if True:
        # queryString = f"select count(distinct IP_ADDRESS) from igw_ipam_table where REGION='WESTERN' and CREATION_DATE=(select max(CREATION_DATE) from igw_ipam_table);"
        # queryString1 = f"select count(distinct IP_ADDRESS) from igw_ipam_table where REGION='EASTERN' and CREATION_DATE=(select max(CREATION_DATE) from igw_ipam_table);"
        # queryString2 = f"select count(distinct IP_ADDRESS) from igw_ipam_table where REGION='CENTRAL' and CREATION_DATE=(select max(CREATION_DATE) from igw_ipam_table);"
        # queryString3 = f"select count(distinct IP_ADDRESS) from igw_ipam_table where REGION='International' and CREATION_DATE=(select max(CREATION_DATE) from igw_ipam_table);"
        # queryString4 = f"select count(distinct IP_ADDRESS) from igw_ipam_table where REGION='Outside KSA' and CREATION_DATE=(select max(CREATION_DATE) from igw_ipam_table);"
        # result = db.session.execute(queryString).scalar()
        # result1 = db.session.execute(queryString1).scalar()
        # result2 = db.session.execute(queryString2).scalar()
        # result3 = db.session.execute(queryString3).scalar()
        # result4 = db.session.execute(queryString4).scalar()
        # objList = [
        #     {
        #         "name":"WESTERN",
        #         "value":result
        #     },
        #     {
        #         "name":"EASTERN",
        #         "value":result1
        #     },
        #     {
        #         "name":"CENTRAL",
        #         "value":result2
        #     },
        #     {
        #         "name":"International",
        #         "value":result3
        #     },
        #     {
        #         "name":"Outside KSA",
        #         "value":result4
        #     }
        # ]
        queryString = f"select region,count(distinct IP_ADDRESS) from igw_ipam_table where CREATION_DATE in (select max(CREATION_DATE) from igw_ipam_table) group by region;"
        result = db.session.execute(queryString)
        objList = []
        for row in result:
            objDict = {}
            region = row[0]
            count = row[1]
            objDict["name"] = region
            objDict['value'] = count
            objList.append(objDict)
        return jsonify(objList),200
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/igwIpamSites',methods = ['GET'])
@token_required
def IgwIpamSites(user_data):
    if True:
        queryString = f"select SITE_TYPE,COUNT(distinct IP_ADDRESS) from igw_ipam_table where SITE_TYPE is NOT NULL and CREATION_DATE=(select max(CREATION_DATE) from igw_ipam_table) group by SITE_TYPE;"
        result = db.session.execute(queryString)
        objList = []
        for row in result:
            objDict = {}
            site_type = row[0]
            count = row[1]
            objDict['name'] = site_type
            objDict['value'] = count
            objList.append(objDict)
        print(objList,file=sys.stderr)
        return jsonify(objList),200
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/igwIpamIpCount',methods = ['GET'])
@token_required
def IgwIpamIpCount(user_data):
    if True:
        queryString = f"select count(distinct IP_ADDRESS) from igw_ipam_table where CREATION_DATE=(select max(CREATION_DATE) from igw_ipam_table);"
        result = db.session.execute(queryString).scalar()
        objList = [
            {
                "name":"IP Addresses",
                "value":result
            }
        ]
        return jsonify(objList),200
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getIgwIpamLastTenFetches',methods = ['GET'])
@token_required
def GetIgwIpamLastTenFetches(user_data):


    if True:
        objList = []
        queryString = f"select count(*),CREATION_DATE from igw_ipam_table where CREATION_DATE in (select MAX(CREATION_DATE) as date from igw_ipam_table group by YEAR(CREATION_DATE), MONTH(CREATION_DATE),DAY(CREATION_DATE)) group by CREATION_DATE ORDER by CREATION_DATE;"
        result = db.session.execute(queryString)
        count = 0
        for row in result:
            objDict = {}
            count = row[0]
            fetchDate = row[1]
            objDict['Fetched Count'] = count
            objDict['Fetch Date'] = FormatDate(fetchDate)
            objList.append(objDict)
            count+=1
            if count==10:
                print("Maximum count for the fetch has reached: ",count,file=sys.stderr)
        
        final_array =[]
        unique_dates=list(set([date['Fetch Date'] for date in objList]))
        for date in unique_dates:
            dic={}
            dic["Fetch Date"]= date
            for record in objList:
                if record["Fetch Date"]== date:
                    dic.update(record)
            final_array.append(dic)
        final_array.sort(key = lambda x: datetime.strptime(x['Fetch Date'], '%d-%m-%Y'))
        print(final_array,file=sys.stderr)
        return jsonify(final_array),200
        # return jsonify(objList),200
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   