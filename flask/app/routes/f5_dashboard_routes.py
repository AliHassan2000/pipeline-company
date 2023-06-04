import sys, json
from flask_jsonpify import jsonify
from flask import Flask, request, make_response, Response, session
from app import app ,db , inv_engine, tz
from app.models.inventory_models import *
from sqlalchemy import func
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask_cors import CORS, cross_origin
from app.middleware import token_required
import traceback
from itertools import chain

@app.route('/getF5Cards', methods= ['GET'])
@token_required
def GetF5Cards(user_data):
    if True:
        try:
            exceptions = []
            queryString = f"select count(distinct(device_id)) from f5 where creation_date = (SELECT max(creation_date) FROM f5);"
            result = inv_engine.execute(queryString).scalar()
            queryString1 = f"select count(distinct(vserver_name)) from f5 where creation_date = (SELECT max(creation_date) FROM f5);"
            result1 = inv_engine.execute(queryString1).scalar()
            queryString2 = f"select count(distinct(node)) from f5 where creation_date = (SELECT max(creation_date) FROM f5);"
            result2 = inv_engine.execute(queryString2).scalar()

            objList = [
                {
                    "name": "F5",
                    "value": result
                },
                {
                    "name": "V Servers",
                    "value": result1
                },
                {
                    "name": "Nodes",
                    "value": result2
                }
            ]
            return jsonify(objList), 200
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

@app.route("/getF5PerSiteVServerCount", methods = ['GET'])
@token_required
def getF5PerSiteVServerCount(user_data):
    if True:
        objDict = {}
        queryString = "select site_id, count(distinct(vserver_name)) from f5 where creation_date = (SELECT max(creation_date) FROM f5) group by site_id order by count(vserver_name);"
        result = inv_engine.execute(queryString)
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

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getF5NodeHealthStatusCount", methods = ['GET'])
@token_required
def GetF5NodeHealthStatusCount(user_data):
    if True:
        objDict = {}
        queryString = "select distinct(count(node)), monitor_status from f5 where creation_date = (SELECT max(creation_date) FROM f5) group by monitor_status order by monitor_status;"
        result = inv_engine.execute(queryString)
        for row in result:
            node = row[0]
            monitor_status = row[1]
            if node in objDict:
                count = 'name'
                objDict[node][count] = monitor_status
                print(objDict, file=sys.stderr)
            else:
                objDict[node] = {}
                count = 'name'
                objDict[node]['name'] = 0
                objDict[node][count] = monitor_status
        objList = []
        for node in objDict:
            dict = objDict[node]
            dict['value'] = node
            objList.append(dict)
        # print(objList, file=sys.stderr)
        return jsonify(objList), 200

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getF5SitesVNodeStatus',methods = ['GET'])
@token_required
def getF5SitesVNodeStatus(user_data):
    if True:
        objList=[]
        try:
            #VULN_FIX_PLAN_STATUS='No Plan' and
            
            queryString = f"select site_id, count(site_id), monitor_status from f5 where creation_date = (SELECT max(creation_date) FROM f5) group by site_id, monitor_status;"
            result = inv_engine.execute(queryString)
            objDict = {}
            
            for row in result:
                site_id = row[0]
                count = row[1]
                status = row[2]

                if site_id in objDict:
                    if status in objDict[site_id]:

                        objDict[site_id] [status]= objDict[site_id][status]
                    else:
                        objDict[site_id][status]=count

                else:
                    objDict[site_id] = {}
                    objDict[site_id][status]=count
                    
                objList = []
                for site_id in objDict:
                    dict = objDict[site_id]
                    dict['name']=site_id
                    objList.append(dict)
            
            #Unique Keys:
            keys=   list(set(chain.from_iterable(sub.keys() for sub in objList))) 
            for key in keys:
                for  obj in objList:
                    obj.setdefault(key, 0)

           
            #objList.append(objDict)

            return jsonify(objList),200
        
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503
        