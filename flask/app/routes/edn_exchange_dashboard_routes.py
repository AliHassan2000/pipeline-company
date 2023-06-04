from lib2to3.pgen2 import token
import sys, json
from flask_jsonpify import jsonify
from flask import Flask, request, make_response, Response, session
from app import app ,db , tz
from app.models.inventory_models import Phy_Table, Rack_Table, Device_Table, Board_Table, Subboard_Table, SFP_Table, License_Table, Seed, SNTC_Table,CDN_Table,EDN_DC_CAPACITY,IGW_DC_CAPACITY
from sqlalchemy import func
from datetime import datetime
from dateutil.relativedelta import relativedelta
import traceback
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


@app.route('/ednExchangeVrfCount',methods = ['GET'])
@token_required
def EdnExchangeVrfCount(user_data):
    if True:
        queryString = f"select count(distinct VRF_NAME) from edn_exchange where CREATION_DATE=(select max(CREATION_DATE) from edn_exchange);"
        result = db.session.execute(queryString).scalar()
        objList = [
            {
                "name":"VRFs",
                "value":result
            }
                    ]
        return jsonify(objList),200
    else:
        
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getVrfPerRegion',methods = ['GET'])
@token_required
def GetVrfPerRegion(user_data):
    if True:
        objList = []
        # queryString1 = f"SELECT count(distinct VRF_NAME) from edn_exchange where DEVICE_ID in (select distinct DEVICE_ID from device_table where SITE_ID in (select distinct SITE_ID from phy_table WHERE REGION='EASTERN'));"
        # queryString2 = f"SELECT count(distinct VRF_NAME) from edn_exchange where DEVICE_ID in (select distinct DEVICE_ID from device_table where SITE_ID in (select distinct SITE_ID from phy_table WHERE REGION='WESTERN'));"
        # queryString3 = f"SELECT count(distinct VRF_NAME) from edn_exchange where DEVICE_ID in (select distinct DEVICE_ID from device_table where SITE_ID in (select distinct SITE_ID from phy_table WHERE REGION='CENTRAL'));"
        # result1 = db.session.execute(queryString1).scalar()
        # result2 = db.session.execute(queryString2).scalar()
        # result3 = db.session.execute(queryString3).scalar()
        # objList = [
        #     {
        #         "name":"EASTERN",
        #         "value":result1
        #     },
        #     {
        #         "name":"WESTERN",
        #         "value":result2
        #     },
        #     {
        #         "name":"CENTRAL",
        #         "value":result3
        #     }
        # ]
        queryString = f"select REGION,count(DISTINCT VRF_NAME) from edn_exchange where CREATION_DATE=(select max(CREATION_DATE) from edn_exchange) group by REGION;"
        result = db.session.execute(queryString)
        for row in result:
            objDict  ={}
            region = row[0]
            count = row[1]
            objDict["name"]=region
            objDict["value"] = count
            objList.append(objDict) 
        return jsonify(objList),200
    else:
        
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getVrfPerSiteId',methods = ['GET'])
@token_required
def GetVrfPerSiteId(user_data):
    if True:
        objList = []
        queryString = f"select SITE_ID,count(DISTINCT VRF_NAME) from edn_exchange where CREATION_DATE=(select max(CREATION_DATE) from edn_exchange) group by SITE_ID;"
        result = db.session.execute(queryString)
        for row in result:
            objDict  ={}
            region = row[0]
            count = row[1]
            objDict["name"]=region
            objDict["value"] = count
            objList.append(objDict) 
        return jsonify(objList),200
    else:
        
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
@app.route('/getEdnExchangeLastTenFetches',methods = ['GET'])
@token_required
def GetEdnExchangeLastTenFetches(user_data):


    if True:
        objList = []
        queryString = f"select count(*),CREATION_DATE from edn_exchange where CREATION_DATE in (select MAX(CREATION_DATE) as date from edn_exchange group by YEAR(CREATION_DATE), MONTH(CREATION_DATE),DAY(CREATION_DATE)) group by CREATION_DATE ORDER by CREATION_DATE;"
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

@app.route("/getSpofVrfsTable", methods = ['GET'])
@token_required
def GetSpofVrfsTable(user_data):
    try:

        objList = GetSpofVrfsTableFunc(user_data)
        return jsonify(objList), 200
    
    except Exception as e:
        traceback.print_exc()
        return str(e), 500

def GetSpofVrfsTableFunc(user_data):
    try:
        objList = []
        vrfs = db.session.execute(f"select vrf, primary_site, secondary_site from external_vrf_analysis where creation_date = (SELECT max(creation_date) FROM external_vrf_analysis);")
        for vrf in vrfs:
            if not vrf[1] or not vrf[2]:
                dict = {}
                dict['vrf_name'] = vrf['vrf']
                dict['primary_site'] = vrf['primary_site']
                dict['secondary_site'] = vrf['secondary_site']

                objList.append(dict)

        return objList
    
    except Exception as e:
        traceback.print_exc()
        return str(e), 500
    
@app.route("/getUnusedVrfsTable", methods = ['GET'])
@token_required
def GetUnusedVrfsTable(user_data):
    try:
        objList= GetUnusedVrfsTableFunc(user_data)

        return jsonify(objList), 200
    
    except Exception as e:
        traceback.print_exc()
        return str(e), 500

def GetUnusedVrfsTableFunc(user_data):
    try:
        objList = []
        vrfs = db.session.execute(f"select vrf, primary_site, secondary_site, no_of_received_routes from external_vrf_analysis where creation_date = (SELECT max(creation_date) FROM external_vrf_analysis);")
        for vrf in vrfs:
            if vrf[3] == None or vrf[3] == '':
                dict = {}
                dict['vrf_name'] = vrf['vrf']
                dict['primary_site'] = vrf['primary_site']
                dict['secondary_site'] = vrf['secondary_site']

                objList.append(dict)

        return objList
    
    except Exception as e:
        traceback.print_exc()
        return str(e), 500


@app.route("/getVrfsWithMissingRoutesTable", methods = ['GET'])
@token_required
def GetVrfsWithMissingRoutesTable(user_data):
    try:

        objList= GetVrfsWithMissingRoutesFunc(user_data)

        return jsonify(objList), 200
    
    except Exception as e:
        traceback.print_exc()
        return str(e), 500

def GetVrfsWithMissingRoutesFunc(user_data):
    try:
        objList = []
        vrfs = db.session.execute(f"select vrf, primary_site, secondary_site, no_of_received_routes, missing_routes_in_secondary_site from external_vrf_analysis where creation_date = (SELECT max(creation_date) FROM external_vrf_analysis);")

        for vrf in vrfs:
            if not vrf[1] or not vrf[2]:
                pass
            else:
                if vrf[4]:
                    dict = {}
                    dict['vrf_name'] = vrf['vrf']
                    dict['primary_site'] = vrf['primary_site']
                    dict['secondary_site'] = vrf['secondary_site']
                    dict['no_of_received_routes'] = vrf['no_of_received_routes']
                    dict['missing_routes_in_secondary_site'] = vrf['missing_routes_in_secondary_site']

                    objList.append(dict)

        return objList
    
    except Exception as e:
        traceback.print_exc()
        return str(e), 500

@app.route("/getIntranetVrfsWithMissingRoutesTable", methods = ['GET'])
@token_required
def GetIntranetVrfsWithMissingRoutesTable(user_data):
    try:
        objList = GetIntranetVrfsWithMissingRoutesTableFunc(user_data)
        return jsonify(objList), 200
    
    except Exception as e:
        traceback.print_exc()
        return str(e), 500
    
def GetIntranetVrfsWithMissingRoutesTableFunc(user_data):
    try:
        objList = []
        vrfs = db.session.execute(f"select vrf, region, primary_site, secondary_site, no_of_received_routes, missing_routes_in_secondary_site, missing_sites_in_secondary_site from intranet_vrf_analysis where creation_date = (SELECT max(creation_date) FROM intranet_vrf_analysis);")
        for vrf in vrfs:
            if vrf[5]:
                dict = {}
                dict['vrf'] = vrf['vrf']
                dict['region'] = vrf['region']
                dict['primary_site'] = vrf['primary_site']
                dict['secondary_site'] = vrf['secondary_site']
                dict['number_of_received_routes'] = vrf['no_of_received_routes']
                dict['missing_routes_in_secondary_site'] = vrf['missing_routes_in_secondary_site']
                dict['missing_sites_in_secondary_site'] = vrf['missing_sites_in_secondary_site']

                objList.append(dict)

        return objList
    
    except Exception as e:
        traceback.print_exc()
        return str(e), 500
