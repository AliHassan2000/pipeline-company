import sys, json
from flask_jsonpify import jsonify
from flask import Flask, request, make_response, Response, session
from app import app ,db , tz
from app.models.inventory_models import *
from sqlalchemy import func
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask_cors import CORS, cross_origin
from app.middleware import token_required
import traceback
from itertools import chain
from app.routes.vulnerabilities_routes import GetEdnVulnerabilityOverallStatusFunc, GetEdnVulnerabilityTechnicalContactFunc,  GetIgwVulnerabilityOverallStatusFunc, GetIgwVulnerabilityTechnicalContactFunc, GetSocVulnerabilityOverallStatusFunc, GetSocVulnerabilityTechnicalContactFunc
import collections
def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%d-%m-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

####################################### EDN VULN Dashboard Routes ##########################################

@app.route('/getEdnVulnerabilityCards',methods = ['GET'])
@token_required
def GetEdnVulnerabilityCards(user_data):
    if True:
        try:
            exceptions = []
            queryString = f"select count(*) from vulnerability_edn_master WHERE overall_status LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_edn_master);"
            result = db.session.execute(queryString).scalar()
            queryString1 = f"select count(*) from vulnerability_edn_master WHERE overall_status NOT LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_edn_master);"
            result1 = db.session.execute(queryString1).scalar()
            #queryString2 = f"select count(*) from vulnerability_overdue WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_overdue);"
            #result2 = db.session.execute(queryString2).scalar()
            #queryString4 = f"select count(*) from vulnerability_inprogress WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_inprogress);"
            #result4 = db.session.execute(queryString4).scalar()
            queryString5 = f"select count(distinct(device_name)) from vulnerability_edn_master WHERE OVERALL_STATUS NOT LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_edn_master);"
            result5 = db.session.execute(queryString5).scalar()
            # queryString3 = f"select EXCEPTION_REQUESTS from vulnerability_inprogress where EXCEPTION_REQUESTS!='' or EXCEPTION_REQUESTS is not NULL or EXCEPTION_REQUESTS!=' ' and creation_date = (SELECT max(creation_date) FROM vulnerability_inprogress);"
            # result3 = db.session.execute(queryString3).scalar()
            # for row3 in result3:
            #     exceptions.append(row3[0])
            # uniqueExceptions = set(exceptions)
            # uniqueExceptions = list(uniqueExceptions)
            # uniqueExceptionsCount = len(uniqueExceptions)
            objList = [
                {
                    "name":"Closed Vulnerabilities",
                    "value":result
                },
                {
                    "name":"Open/Over./Inprog. Vuln.",
                    "value": str(result1)# + result2 + result4)
                },
                # {
                #     "name":"Inprogress Exceptions",
                #     "value":uniqueExceptionsCount
                # }
                {
                    "name":"Devices",
                    "value":result5
                }

            ]
            return jsonify(objList),200
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503


@app.route('/getEdnOverallStatus',methods = ['GET'])
#@token_required
def GetEdnOverallStatus():
    if True:
        try:

            objList = objList2=[]
            queryString = f"select OVERALL_STATUS,count(OVERALL_STATUS) from vulnerability_edn_master WHERE OVERALL_STATUS LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_edn_master) group by OVERALL_STATUS;"
            result = db.session.execute(queryString)

            objDict = {}
            objDict['name'] = 'Closed'
            for row in result:  
                if 'value' in objDict:
                    objDict['value']= objDict['value']+row[1]
                else:
                    objDict['value'] = row[1]
            #print(f"### {objDict}", file=sys.stderr)
            objList.append(objDict)

            
            queryString = f"select OVERALL_STATUS,count(OVERALL_STATUS) from vulnerability_edn_master WHERE OVERALL_STATUS NOT LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_edn_master) group by OVERALL_STATUS;"
            result = db.session.execute(queryString)

            for row in result:
                objDict = {}
                objDict["name"] = row[0]
                objDict['value'] = row[1]
                objList.append(objDict)
                

            return jsonify(objList),200
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

def getEdnSearchpattern(dateObj):
    #print(type(dateObj['date']),file=sys.stderr)  
          

    searchPattern=""
    allVulContact= GetEdnVulnerabilityTechnicalContactFunc()
    allVulStatus= GetEdnVulnerabilityOverallStatusFunc()
    if dateObj.get('technicalContact')[0]=="All" or dateObj.get('technicalContact')[0]=="":
        del allVulContact[0]
        for index, status in enumerate(allVulContact):
            if index==0:
                searchPattern+=" and ( TECHNICAL_CONTACT='"+status+"' "
            else:
                searchPattern+=" or TECHNICAL_CONTACT='"+status+"' "
        searchPattern+=") "
    else:
        searchList= list(set(allVulContact) & set( dateObj.get('technicalContact')))
        for index, search in enumerate(searchList):
            if index==0:
                searchPattern+=" and ( TECHNICAL_CONTACT='"+search+"' "
            else:
                searchPattern+=" or TECHNICAL_CONTACT='"+search+"' "

        searchPattern+=") "
    
    if dateObj.get('overAllStatus')[0]=="All" or dateObj.get('overAllStatus')[0]=="":
        del allVulStatus[0]
        for index, status in enumerate(allVulStatus):
            if index==0:
                searchPattern+=" and ( OVERALL_STATUS='"+status+"' "
            else:
                searchPattern+=" or OVERALL_STATUS='"+status+"' "

        searchPattern+=") "

    else:
        searchList= list(set(allVulStatus) & set( dateObj.get('overAllStatus')))
        for index, search in enumerate(searchList):
            if index==0:
                searchPattern+=" and ( OVERALL_STATUS='"+search+"' "
            else:
                searchPattern+=" or OVERALL_STATUS='"+search+"' "
        searchPattern+=") "
        

    return searchPattern

@app.route('/getEdnGrcSeverity',methods = ['POST'])
@token_required
def GetEdnGrcSeverity(user_data):
    if True:
        try:
            dateObj = request.get_json()
            searchpattern= getEdnSearchpattern(dateObj)
            
            objList = []
            queryString = f"select SEVERITY,count(SEVERITY) from vulnerability_edn_master WHERE OVERALL_STATUS NOT LIKE 'Closed%' {searchpattern} and creation_date = (SELECT max(creation_date) FROM vulnerability_edn_master) group by SEVERITY;"
            #print(queryString, file=sys.stderr)
            result = db.session.execute(queryString)
            for row in result:
                objDict = {}
                objDict['name'] = row[0]
                objDict['value'] = row[1]
                objList.append(objDict)
            return jsonify(objList),200
        except Exception as e:
            print("Error Occured {e}", file=sys.stderr)
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

@app.route('/getEdnVulnFixPlanStatus',methods = ['POST'])
@token_required
def GetEdnVulnFixPlanStatus(user_data):
    if True:
        try:
            objList = []
            dateObj = request.get_json()
            searchPattern= getEdnSearchpattern(dateObj)
            
            queryString = f"select VULN_FIX_PLAN_STATUS,count(VULN_FIX_PLAN_STATUS) from vulnerability_edn_master  WHERE OVERALL_STATUS NOT LIKE 'Closed%' {searchPattern} and creation_date = (SELECT max(creation_date) FROM vulnerability_edn_master) group by VULN_FIX_PLAN_STATUS;"
            result = db.session.execute(queryString)
            for row in result:
                objDict = {}
                objDict['name'] = row[0]
                if objDict['name']== "NE":
                    objDict['name']= "Not Found"
                objDict['value'] = row[1]
                objList.append(objDict)
            return jsonify(objList),200
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

@app.route('/getEdnGRCSeverityVsVulnFixPlanStatus',methods = ['POST'])
@token_required
def GetEdnGRCSeverityVsVulnFixPlanStatus(user_data):
    if True:
        objList=[]
        try:
            #VULN_FIX_PLAN_STATUS='No Plan' and
            dateObj = request.get_json()
            searchPattern= getEdnSearchpattern(dateObj)
            queryString = f"select VULN_FIX_PLAN_STATUS, SEVERITY ,count(VULN_FIX_PLAN_STATUS) from vulnerability_edn_master WHERE OVERALL_STATUS NOT LIKE 'Closed%' {searchPattern} and  creation_date = (SELECT max(creation_date) FROM vulnerability_edn_master) group by VULN_FIX_PLAN_STATUS, SEVERITY;"
            result = db.session.execute(queryString)
            objDict = {} 
            for row in result:
                fix_plan_status = row[0]
                if fix_plan_status=="NE":
                    fix_plan_status="Not Found"
                
                sevirity= row[1]
                count = row[2]

                if sevirity in objDict:
                    if fix_plan_status in objDict[sevirity]:

                        objDict[sevirity] [fix_plan_status]= objDict[sevirity][fix_plan_status]+count
                    else:
                        objDict[sevirity][fix_plan_status]=count

                else:
                    objDict[sevirity] = {}
                    objDict[sevirity][fix_plan_status]=count
                    
                objList = []
                for sevirity in objDict:
                    dict = objDict[sevirity]
                    dict['name']=sevirity
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

@app.route('/getEdnGRCSeverityVsPNCode',methods = ['POST'])
@token_required
def GetEdnGRCSeverityVsPNCode(user_data):
    if True:
        objList=[]
        try:
            #VULN_FIX_PLAN_STATUS='No Plan' and
            dateObj = request.get_json()
            searchPattern= getEdnSearchpattern(dateObj)
            queryString = f"select pn_code, SEVERITY ,count(pn_code) from vulnerability_edn_master  WHERE  OVERALL_STATUS NOT LIKE 'Closed%' {searchPattern} and creation_date = (SELECT max(creation_date) FROM vulnerability_edn_master) group by pn_code, SEVERITY;"
            result = db.session.execute(queryString)
            objDict = {} 
            for row in result:
                pn_code = row[0]
                if pn_code=="NE":
                    pn_code="Not Found"

                if 'N5K' in pn_code:
                    pn_code="N5K"
                if '3750' in pn_code:
                    pn_code="3750"
                if '3850' in pn_code:
                    pn_code="3850"
                if '3560' in pn_code:
                    pn_code="3560"
                if 'N77' in pn_code:
                    pn_code="N7k"
                if 'N7K' in pn_code:
                    pn_code="N7k"
                if 'N9K' in pn_code:
                    pn_code="N9K"
                if 'ASR1' in pn_code:
                    pn_code="ASR1K"
                if 'CISCO76' in pn_code:
                    pn_code="7600"
                if 'WS-C65' in pn_code:
                    pn_code="6500"
                
                sevirity= row[1]
                count = row[2]

                if sevirity in objDict:
                    if pn_code in objDict[sevirity]:

                        objDict[sevirity] [pn_code]= objDict[sevirity][pn_code]+count
                    else:
                        objDict[sevirity][pn_code]=count

                else:
                    objDict[sevirity] = {}
                    objDict[sevirity][pn_code]=count
                    
                objList = []
                for sevirity in objDict:
                    dict = objDict[sevirity]
                    dict['name']=sevirity
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

@app.route('/getEdnvulnerabilityInventoryGrowth',methods = ['GET'])
@token_required
def VulnerabilityEdnInventoryGrowth(user_data):
    try:
        queryString = f"select overall_status, count(overall_status), creation_date from vulnerability_edn_master where (OVERALL_STATUS LIKE '%Closed%' OR OVERALL_STATUS LIKE '%Open%' OR OVERALL_STATUS LIKE '%Exception%') AND creation_date in (select MAX(creation_date) from vulnerability_edn_master group by WEEK(CREATION_DATE)) group by overall_status, creation_date order by creation_date;"
        result = db.session.execute(queryString)
        ClosedStatusDateList = []
        openStatusDateList = []
        exceptionStatusDateList = []
        for row in result:
            ClosedStatusDateDict = openStatusDateDict = exceptionStatusDateDict ={}
            
            overall_status = row[0]
            count = row[1]                
            creation_date = FormatDate(row[2])
            if 'Closed' in overall_status:
                ClosedStatusDateDict[creation_date] = count
                ClosedStatusDateList.append(ClosedStatusDateDict)
            elif 'Open' in overall_status:
                openStatusDateDict[creation_date] = count
                openStatusDateList.append(openStatusDateDict)
            elif 'Exception' in overall_status:
                exceptionStatusDateDict[creation_date] = count
                exceptionStatusDateList.append(exceptionStatusDateDict)
            
        counter = collections.Counter()
        
        for d in ClosedStatusDateList:
            counter.update(d)
        res = dict(counter)
        print(res,file=sys.stderr)
        
        objList = []
        for i in res:
            objDict = {}
            objDict['Closed']  = res[i]
            objDict['date'] = i
            objList.append(objDict)

        counter = collections.Counter()
        
        for d in openStatusDateList:
            counter.update(d)
        res = dict(counter)
        print(res,file=sys.stderr)
        
        
        for i in res:
            objDict = {}
            objDict['date'] = i
            objDict['Open'] = res[i] 
            objList.append(objDict)

        counter = collections.Counter()
        
        for d in exceptionStatusDateList:
            counter.update(d)
        res = dict(counter)
        print(res,file=sys.stderr)
        
        
        for i in res:
            objDict = {}
            objDict['date'] = i
            objDict['Exception'] = res[i]
            objList.append(objDict)
        
        new_obj_list = {}
        for obj in objList:
            if obj['date'] not in new_obj_list:
                new_obj_list[obj['date']] = {"Closed":0, "Open":0, "Exception": 0, "date": obj['date']}
            if obj.get('Closed'):
                new_obj_list[obj['date']]['Closed'] = obj.get('Closed')
            if obj.get('Open'):
                new_obj_list[obj['date']]['Open'] = obj.get('Open')
            if obj.get('Exception'):
                new_obj_list[obj['date']]['Exception'] = obj.get('Exception')

        finalList = []
        finalList = (list(new_obj_list.values()))
        finalList.sort(key = lambda x: datetime.strptime(x['date'], '%d-%m-%Y'))
        print(finalList, file=sys.stderr)

        return jsonify(finalList),200

    except Exception as e:  

        print(str(e),file=sys.stderr)
        traceback.print_exc()
        return str(e),500



####################################### IGW VULN Dashboard Routes ##########################################


@app.route('/getIgwVulnerabilityCards',methods = ['GET'])
@token_required
def GetIgwVulnerabilityCards(user_data):
    if True:
        try:
            exceptions = []
            queryString = f"select count(*) from vulnerability_igw_master WHERE overall_status LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_igw_master);"
            result = db.session.execute(queryString).scalar()
            queryString1 = f"select count(*) from vulnerability_igw_master WHERE overall_status NOT LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_igw_master);"
            result1 = db.session.execute(queryString1).scalar()
            #queryString2 = f"select count(*) from vulnerability_overdue WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_overdue);"
            #result2 = db.session.execute(queryString2).scalar()
            #queryString4 = f"select count(*) from vulnerability_inprogress WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_inprogress);"
            #result4 = db.session.execute(queryString4).scalar()
            queryString5 = f"select count(distinct(device_name)) from vulnerability_igw_master WHERE OVERALL_STATUS NOT LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_igw_master);"
            result5 = db.session.execute(queryString5).scalar()
            # queryString3 = f"select EXCEPTION_REQUESTS from vulnerability_inprogress where EXCEPTION_REQUESTS!='' or EXCEPTION_REQUESTS is not NULL or EXCEPTION_REQUESTS!=' ' and creation_date = (SELECT max(creation_date) FROM vulnerability_inprogress);"
            # result3 = db.session.execute(queryString3).scalar()
            # for row3 in result3:
            #     exceptions.append(row3[0])
            # uniqueExceptions = set(exceptions)
            # uniqueExceptions = list(uniqueExceptions)
            # uniqueExceptionsCount = len(uniqueExceptions)
            objList = [
                {
                    "name":"Closed Vulnerabilities",
                    "value":result
                },
                {
                    "name":"Open/Over./Inprog. Vuln.",
                    "value": str(result1)# + result2 + result4)
                },
                # {
                #     "name":"Inprogress Exceptions",
                #     "value":uniqueExceptionsCount
                # }
                {
                    "name":"Devices",
                    "value":result5
                }

            ]
            return jsonify(objList),200
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503


@app.route('/getIgwOverallStatus',methods = ['GET'])
#@token_required
def GetIgwOverallStatus():
    if True:
        try:

            objList = objList2=[]
            queryString = f"select OVERALL_STATUS,count(OVERALL_STATUS) from vulnerability_igw_master WHERE OVERALL_STATUS LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_igw_master) group by OVERALL_STATUS;"
            result = db.session.execute(queryString)

            objDict = {}
            objDict['name'] = 'Closed'
            for row in result:  
                if 'value' in objDict:
                    objDict['value']= objDict['value']+row[1]
                else:
                    objDict['value'] = row[1]
            #print(f"### {objDict}", file=sys.stderr)
            objList.append(objDict)

            
            queryString = f"select OVERALL_STATUS,count(OVERALL_STATUS) from vulnerability_igw_master WHERE OVERALL_STATUS NOT LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_igw_master) group by OVERALL_STATUS;"
            result = db.session.execute(queryString)

            for row in result:
                objDict = {}
                objDict["name"] = row[0]
                objDict['value'] = row[1]
                objList.append(objDict)
                

            return jsonify(objList),200
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

def getIgwSearchpattern(dateObj):
    #print(type(dateObj['date']),file=sys.stderr)  
          

    searchPattern=""
    allVulContact= GetIgwVulnerabilityTechnicalContactFunc()
    allVulStatus= GetIgwVulnerabilityOverallStatusFunc()
    if dateObj.get('technicalContact')[0]=="All" or dateObj.get('technicalContact')[0]=="":
        del allVulContact[0]
        for index, status in enumerate(allVulContact):
            if index==0:
                searchPattern+=" and ( TECHNICAL_CONTACT='"+status+"' "
            else:
                searchPattern+=" or TECHNICAL_CONTACT='"+status+"' "
        searchPattern+=") "
    else:
        searchList= list(set(allVulContact) & set( dateObj.get('technicalContact')))
        for index, search in enumerate(searchList):
            if index==0:
                searchPattern+=" and ( TECHNICAL_CONTACT='"+search+"' "
            else:
                searchPattern+=" or TECHNICAL_CONTACT='"+search+"' "

        searchPattern+=") "
    
    if dateObj.get('overAllStatus')[0]=="All" or dateObj.get('overAllStatus')[0]=="":
        del allVulStatus[0]
        for index, status in enumerate(allVulStatus):
            if index==0:
                searchPattern+=" and ( OVERALL_STATUS='"+status+"' "
            else:
                searchPattern+=" or OVERALL_STATUS='"+status+"' "

        searchPattern+=") "

    else:
        searchList= list(set(allVulStatus) & set( dateObj.get('overAllStatus')))
        for index, search in enumerate(searchList):
            if index==0:
                searchPattern+=" and ( OVERALL_STATUS='"+search+"' "
            else:
                searchPattern+=" or OVERALL_STATUS='"+search+"' "
        searchPattern+=") "
        

    return searchPattern

@app.route('/getIgwGrcSeverity',methods = ['POST'])
@token_required
def GetIgwGrcSeverity(user_data):
    if True:
        try:
            dateObj = request.get_json()
            searchpattern= getIgwSearchpattern(dateObj)
            
            objList = []
            queryString = f"select SEVERITY,count(SEVERITY) from vulnerability_igw_master WHERE OVERALL_STATUS NOT LIKE 'Closed%' {searchpattern} and creation_date = (SELECT max(creation_date) FROM vulnerability_igw_master) group by SEVERITY;"
            #print(queryString, file=sys.stderr)
            result = db.session.execute(queryString)
            for row in result:
                objDict = {}
                objDict['name'] = row[0]
                objDict['value'] = row[1]
                objList.append(objDict)
            return jsonify(objList),200
        except Exception as e:
            print("Error Occured {e}", file=sys.stderr)
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

@app.route('/getIgwVulnFixPlanStatus',methods = ['POST'])
@token_required
def GetIgwVulnFixPlanStatus(user_data):
    if True:
        try:
            objList = []
            dateObj = request.get_json()
            searchPattern= getIgwSearchpattern(dateObj)
            
            queryString = f"select VULN_FIX_PLAN_STATUS,count(VULN_FIX_PLAN_STATUS) from vulnerability_igw_master  WHERE OVERALL_STATUS NOT LIKE 'Closed%' {searchPattern} and creation_date = (SELECT max(creation_date) FROM vulnerability_igw_master) group by VULN_FIX_PLAN_STATUS;"
            result = db.session.execute(queryString)
            for row in result:
                objDict = {}
                objDict['name'] = row[0]
                if objDict['name']== "NE":
                    objDict['name']= "Not Found"
                objDict['value'] = row[1]
                objList.append(objDict)
            return jsonify(objList),200
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

@app.route('/getIgwGRCSeverityVsVulnFixPlanStatus',methods = ['POST'])
@token_required
def GetIgwGRCSeverityVsVulnFixPlanStatus(user_data):
    if True:
        objList=[]
        try:
            #VULN_FIX_PLAN_STATUS='No Plan' and
            dateObj = request.get_json()
            searchPattern= getIgwSearchpattern(dateObj)
            queryString = f"select VULN_FIX_PLAN_STATUS, SEVERITY ,count(VULN_FIX_PLAN_STATUS) from vulnerability_igw_master WHERE OVERALL_STATUS NOT LIKE 'Closed%' {searchPattern} and  creation_date = (SELECT max(creation_date) FROM vulnerability_igw_master) group by VULN_FIX_PLAN_STATUS, SEVERITY;"
            result = db.session.execute(queryString)
            objDict = {} 
            for row in result:
                fix_plan_status = row[0]
                if fix_plan_status=="NE":
                    fix_plan_status="Not Found"
                
                sevirity= row[1]
                count = row[2]

                if sevirity in objDict:
                    if fix_plan_status in objDict[sevirity]:

                        objDict[sevirity] [fix_plan_status]= objDict[sevirity][fix_plan_status]+count
                    else:
                        objDict[sevirity][fix_plan_status]=count

                else:
                    objDict[sevirity] = {}
                    objDict[sevirity][fix_plan_status]=count
                    
                objList = []
                for sevirity in objDict:
                    dict = objDict[sevirity]
                    dict['name']=sevirity
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

@app.route('/getIgwGRCSeverityVsPNCode',methods = ['POST'])
@token_required
def GetIgwGRCSeverityVsPNCode(user_data):
    if True:
        objList=[]
        try:
            #VULN_FIX_PLAN_STATUS='No Plan' and
            dateObj = request.get_json()
            searchPattern= getIgwSearchpattern(dateObj)
            queryString = f"select pn_code, SEVERITY ,count(pn_code) from vulnerability_igw_master  WHERE  OVERALL_STATUS NOT LIKE 'Closed%' {searchPattern} and creation_date = (SELECT max(creation_date) FROM vulnerability_igw_master) group by pn_code, SEVERITY;"
            result = db.session.execute(queryString)
            objDict = {} 
            for row in result:
                pn_code = row[0]
                if pn_code=="NE":
                    pn_code="Not Found"

                if 'N5K' in pn_code:
                    pn_code="N5K"
                if '3750' in pn_code:
                    pn_code="3750"
                if '3850' in pn_code:
                    pn_code="3850"
                if '3560' in pn_code:
                    pn_code="3560"
                if 'N77' in pn_code:
                    pn_code="N7k"
                if 'N7K' in pn_code:
                    pn_code="N7k"
                if 'N9K' in pn_code:
                    pn_code="N9K"
                if 'ASR1' in pn_code:
                    pn_code="ASR1K"
                if 'CISCO76' in pn_code:
                    pn_code="7600"
                if 'WS-C65' in pn_code:
                    pn_code="6500"
                
                sevirity= row[1]
                count = row[2]

                if sevirity in objDict:
                    if pn_code in objDict[sevirity]:

                        objDict[sevirity] [pn_code]= objDict[sevirity][pn_code]+count
                    else:
                        objDict[sevirity][pn_code]=count

                else:
                    objDict[sevirity] = {}
                    objDict[sevirity][pn_code]=count
                    
                objList = []
                for sevirity in objDict:
                    dict = objDict[sevirity]
                    dict['name']=sevirity
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

@app.route('/getIgwvulnerabilityInventoryGrowth',methods = ['GET'])
@token_required
def VulnerabilityIgwInventoryGrowth(user_data):
    try:
        queryString = f"select overall_status, count(overall_status), creation_date from vulnerability_igw_master where (OVERALL_STATUS LIKE '%Closed%' OR OVERALL_STATUS LIKE '%Open%' OR OVERALL_STATUS LIKE '%Exception%') AND creation_date in (select MAX(creation_date) from vulnerability_igw_master group by WEEK(CREATION_DATE)) group by overall_status, creation_date order by creation_date;"
        result = db.session.execute(queryString)
        ClosedStatusDateList = []
        openStatusDateList = []
        exceptionStatusDateList = []
        for row in result:
            ClosedStatusDateDict = openStatusDateDict = exceptionStatusDateDict ={}
            
            overall_status = row[0]
            count = row[1]                
            creation_date = FormatDate(row[2])
            if 'Closed' in overall_status:
                ClosedStatusDateDict[creation_date] = count
                ClosedStatusDateList.append(ClosedStatusDateDict)
            elif 'Open' in overall_status:
                openStatusDateDict[creation_date] = count
                openStatusDateList.append(openStatusDateDict)
            elif 'Exception' in overall_status:
                exceptionStatusDateDict[creation_date] = count
                exceptionStatusDateList.append(exceptionStatusDateDict)
            
        counter = collections.Counter()
        
        for d in ClosedStatusDateList:
            counter.update(d)
        res = dict(counter)
        print(res,file=sys.stderr)
        
        objList = []
        for i in res:
            objDict = {}
            objDict['Closed']  = res[i]
            objDict['date'] = i
            objList.append(objDict)

        counter = collections.Counter()
        
        for d in openStatusDateList:
            counter.update(d)
        res = dict(counter)
        print(res,file=sys.stderr)
        
        
        for i in res:
            objDict = {}
            objDict['date'] = i
            objDict['Open'] = res[i] 
            objList.append(objDict)

        counter = collections.Counter()
        
        for d in exceptionStatusDateList:
            counter.update(d)
        res = dict(counter)
        print(res,file=sys.stderr)
        
        
        for i in res:
            objDict = {}
            objDict['date'] = i
            objDict['Exception'] = res[i]
            objList.append(objDict)
        
        new_obj_list = {}
        for obj in objList:
            if obj['date'] not in new_obj_list:
                new_obj_list[obj['date']] = {"Closed":0, "Open":0, "Exception": 0, "date": obj['date']}
            if obj.get('Closed'):
                new_obj_list[obj['date']]['Closed'] = obj.get('Closed')
            if obj.get('Open'):
                new_obj_list[obj['date']]['Open'] = obj.get('Open')
            if obj.get('Exception'):
                new_obj_list[obj['date']]['Exception'] = obj.get('Exception')

        finalList = []
        finalList = (list(new_obj_list.values()))
        finalList.sort(key = lambda x: datetime.strptime(x['date'], '%d-%m-%Y'))
        print(finalList, file=sys.stderr)

        return jsonify(finalList),200

    except Exception as e:  

        print(str(e),file=sys.stderr)
        traceback.print_exc()
        return str(e),500
    
####################################### SOC VULN Dashboard Routes ##########################################


@app.route('/getSocVulnerabilityCards',methods = ['GET'])
@token_required
def GetSocVulnerabilityCards(user_data):
    if True:
        try:
            exceptions = []
            queryString = f"select count(*) from vulnerability_soc_master WHERE overall_status LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_soc_master);"
            result = db.session.execute(queryString).scalar()
            queryString1 = f"select count(*) from vulnerability_soc_master WHERE overall_status NOT LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_soc_master);"
            result1 = db.session.execute(queryString1).scalar()
            #queryString2 = f"select count(*) from vulnerability_overdue WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_overdue);"
            #result2 = db.session.execute(queryString2).scalar()
            #queryString4 = f"select count(*) from vulnerability_inprogress WHERE creation_date = (SELECT max(creation_date) FROM vulnerability_inprogress);"
            #result4 = db.session.execute(queryString4).scalar()
            queryString5 = f"select count(distinct(device_name)) from vulnerability_soc_master WHERE OVERALL_STATUS NOT LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_soc_master);"
            result5 = db.session.execute(queryString5).scalar()
            # queryString3 = f"select EXCEPTION_REQUESTS from vulnerability_inprogress where EXCEPTION_REQUESTS!='' or EXCEPTION_REQUESTS is not NULL or EXCEPTION_REQUESTS!=' ' and creation_date = (SELECT max(creation_date) FROM vulnerability_inprogress);"
            # result3 = db.session.execute(queryString3).scalar()
            # for row3 in result3:
            #     exceptions.append(row3[0])
            # uniqueExceptions = set(exceptions)
            # uniqueExceptions = list(uniqueExceptions)
            # uniqueExceptionsCount = len(uniqueExceptions)
            objList = [
                {
                    "name":"Closed Vulnerabilities",
                    "value":result
                },
                {
                    "name":"Open/Over./Inprog. Vuln.",
                    "value": str(result1)# + result2 + result4)
                },
                # {
                #     "name":"Inprogress Exceptions",
                #     "value":uniqueExceptionsCount
                # }
                {
                    "name":"Devices",
                    "value":result5
                }

            ]
            return jsonify(objList),200
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503


@app.route('/getSocOverallStatus',methods = ['GET'])
#@token_required
def GetSocOverallStatus():
    if True:
        try:

            objList = objList2=[]
            queryString = f"select OVERALL_STATUS,count(OVERALL_STATUS) from vulnerability_soc_master WHERE OVERALL_STATUS LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_soc_master) group by OVERALL_STATUS;"
            result = db.session.execute(queryString)

            objDict = {}
            objDict['name'] = 'Closed'
            for row in result:  
                if 'value' in objDict:
                    objDict['value']= objDict['value']+row[1]
                else:
                    objDict['value'] = row[1]
            #print(f"### {objDict}", file=sys.stderr)
            objList.append(objDict)

            
            queryString = f"select OVERALL_STATUS,count(OVERALL_STATUS) from vulnerability_soc_master WHERE OVERALL_STATUS NOT LIKE 'Closed%' and creation_date = (SELECT max(creation_date) FROM vulnerability_soc_master) group by OVERALL_STATUS;"
            result = db.session.execute(queryString)

            for row in result:
                objDict = {}
                objDict["name"] = row[0]
                objDict['value'] = row[1]
                objList.append(objDict)
                

            return jsonify(objList),200
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

def getSocSearchpattern(dateObj):
    #print(type(dateObj['date']),file=sys.stderr)  
          

    searchPattern=""
    allVulContact= GetSocVulnerabilityTechnicalContactFunc()
    allVulStatus= GetSocVulnerabilityOverallStatusFunc()
    if dateObj.get('technicalContact')[0]=="All" or dateObj.get('technicalContact')[0]=="":
        del allVulContact[0]
        for index, status in enumerate(allVulContact):
            if index==0:
                searchPattern+=" and ( TECHNICAL_CONTACT='"+status+"' "
            else:
                searchPattern+=" or TECHNICAL_CONTACT='"+status+"' "
        searchPattern+=") "
    else:
        searchList= list(set(allVulContact) & set( dateObj.get('technicalContact')))
        for index, search in enumerate(searchList):
            if index==0:
                searchPattern+=" and ( TECHNICAL_CONTACT='"+search+"' "
            else:
                searchPattern+=" or TECHNICAL_CONTACT='"+search+"' "

        searchPattern+=") "
    
    if dateObj.get('overAllStatus')[0]=="All" or dateObj.get('overAllStatus')[0]=="":
        del allVulStatus[0]
        for index, status in enumerate(allVulStatus):
            if index==0:
                searchPattern+=" and ( OVERALL_STATUS='"+status+"' "
            else:
                searchPattern+=" or OVERALL_STATUS='"+status+"' "

        searchPattern+=") "

    else:
        searchList= list(set(allVulStatus) & set( dateObj.get('overAllStatus')))
        for index, search in enumerate(searchList):
            if index==0:
                searchPattern+=" and ( OVERALL_STATUS='"+search+"' "
            else:
                searchPattern+=" or OVERALL_STATUS='"+search+"' "
        searchPattern+=") "
        

    return searchPattern

@app.route('/getSocGrcSeverity',methods = ['POST'])
@token_required
def GetSocGrcSeverity(user_data):
    if True:
        try:
            dateObj = request.get_json()
            searchpattern= getSocSearchpattern(dateObj)
            
            objList = []
            queryString = f"select SEVERITY,count(SEVERITY) from vulnerability_soc_master WHERE OVERALL_STATUS NOT LIKE 'Closed%' {searchpattern} and creation_date = (SELECT max(creation_date) FROM vulnerability_soc_master) group by SEVERITY;"
            #print(queryString, file=sys.stderr)
            result = db.session.execute(queryString)
            for row in result:
                objDict = {}
                objDict['name'] = row[0]
                objDict['value'] = row[1]
                objList.append(objDict)
            return jsonify(objList),200
        except Exception as e:
            print("Error Occured {e}", file=sys.stderr)
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

@app.route('/getSocVulnFixPlanStatus',methods = ['POST'])
@token_required
def GetSocVulnFixPlanStatus(user_data):
    if True:
        try:
            objList = []
            dateObj = request.get_json()
            searchPattern= getSocSearchpattern(dateObj)
            
            queryString = f"select VULN_FIX_PLAN_STATUS,count(VULN_FIX_PLAN_STATUS) from vulnerability_soc_master  WHERE OVERALL_STATUS NOT LIKE 'Closed%' {searchPattern} and creation_date = (SELECT max(creation_date) FROM vulnerability_soc_master) group by VULN_FIX_PLAN_STATUS;"
            result = db.session.execute(queryString)
            for row in result:
                objDict = {}
                objDict['name'] = row[0]
                if objDict['name']== "NE":
                    objDict['name']= "Not Found"
                objDict['value'] = row[1]
                objList.append(objDict)
            return jsonify(objList),200
        except Exception as e:
            traceback.print_exc()
            return str(e), 500

    else:
        print("Service not Available", file=sys.stderr)
        return jsonify({"Response": "Service not Available"}), 503

@app.route('/getSocGRCSeverityVsVulnFixPlanStatus',methods = ['POST'])
@token_required
def GetSocGRCSeverityVsVulnFixPlanStatus(user_data):
    if True:
        objList=[]
        try:
            #VULN_FIX_PLAN_STATUS='No Plan' and
            dateObj = request.get_json()
            searchPattern= getSocSearchpattern(dateObj)
            queryString = f"select VULN_FIX_PLAN_STATUS, SEVERITY ,count(VULN_FIX_PLAN_STATUS) from vulnerability_soc_master WHERE OVERALL_STATUS NOT LIKE 'Closed%' {searchPattern} and  creation_date = (SELECT max(creation_date) FROM vulnerability_soc_master) group by VULN_FIX_PLAN_STATUS, SEVERITY;"
            result = db.session.execute(queryString)
            objDict = {} 
            for row in result:
                fix_plan_status = row[0]
                if fix_plan_status=="NE":
                    fix_plan_status="Not Found"
                
                sevirity= row[1]
                count = row[2]

                if sevirity in objDict:
                    if fix_plan_status in objDict[sevirity]:

                        objDict[sevirity] [fix_plan_status]= objDict[sevirity][fix_plan_status]+count
                    else:
                        objDict[sevirity][fix_plan_status]=count

                else:
                    objDict[sevirity] = {}
                    objDict[sevirity][fix_plan_status]=count
                    
                objList = []
                for sevirity in objDict:
                    dict = objDict[sevirity]
                    dict['name']=sevirity
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

@app.route('/getSocGRCSeverityVsPNCode',methods = ['POST'])
@token_required
def GetSocGRCSeverityVsPNCode(user_data):
    if True:
        objList=[]
        try:
            #VULN_FIX_PLAN_STATUS='No Plan' and
            dateObj = request.get_json()
            searchPattern= getSocSearchpattern(dateObj)
            queryString = f"select pn_code, SEVERITY ,count(pn_code) from vulnerability_soc_master  WHERE  OVERALL_STATUS NOT LIKE 'Closed%' {searchPattern} and creation_date = (SELECT max(creation_date) FROM vulnerability_soc_master) group by pn_code, SEVERITY;"
            result = db.session.execute(queryString)
            objDict = {} 
            for row in result:
                pn_code = row[0]
                if pn_code=="NE":
                    pn_code="Not Found"

                if 'N5K' in pn_code:
                    pn_code="N5K"
                if '3750' in pn_code:
                    pn_code="3750"
                if '3850' in pn_code:
                    pn_code="3850"
                if '3560' in pn_code:
                    pn_code="3560"
                if 'N77' in pn_code:
                    pn_code="N7k"
                if 'N7K' in pn_code:
                    pn_code="N7k"
                if 'N9K' in pn_code:
                    pn_code="N9K"
                if 'ASR1' in pn_code:
                    pn_code="ASR1K"
                if 'CISCO76' in pn_code:
                    pn_code="7600"
                if 'WS-C65' in pn_code:
                    pn_code="6500"
                
                sevirity= row[1]
                count = row[2]

                if sevirity in objDict:
                    if pn_code in objDict[sevirity]:

                        objDict[sevirity] [pn_code]= objDict[sevirity][pn_code]+count
                    else:
                        objDict[sevirity][pn_code]=count

                else:
                    objDict[sevirity] = {}
                    objDict[sevirity][pn_code]=count
                    
                objList = []
                for sevirity in objDict:
                    dict = objDict[sevirity]
                    dict['name']=sevirity
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

@app.route('/getSocvulnerabilityInventoryGrowth',methods = ['GET'])
@token_required
def VulnerabilitySocInventoryGrowth(user_data):
    try:
        queryString = f"select overall_status, count(overall_status), creation_date from vulnerability_soc_master where (OVERALL_STATUS LIKE '%Closed%' OR OVERALL_STATUS LIKE '%Open%' OR OVERALL_STATUS LIKE '%Exception%') AND creation_date in (select MAX(creation_date) from vulnerability_soc_master group by WEEK(CREATION_DATE)) group by overall_status, creation_date order by creation_date;"
        result = db.session.execute(queryString)
        ClosedStatusDateList = []
        openStatusDateList = []
        exceptionStatusDateList = []
        for row in result:
            ClosedStatusDateDict = openStatusDateDict = exceptionStatusDateDict ={}
            
            overall_status = row[0]
            count = row[1]                
            creation_date = FormatDate(row[2])
            if 'Closed' in overall_status:
                ClosedStatusDateDict[creation_date] = count
                ClosedStatusDateList.append(ClosedStatusDateDict)
            elif 'Open' in overall_status:
                openStatusDateDict[creation_date] = count
                openStatusDateList.append(openStatusDateDict)
            elif 'Exception' in overall_status:
                exceptionStatusDateDict[creation_date] = count
                exceptionStatusDateList.append(exceptionStatusDateDict)
            
        counter = collections.Counter()
        
        for d in ClosedStatusDateList:
            counter.update(d)
        res = dict(counter)
        print(res,file=sys.stderr)
        
        objList = []
        for i in res:
            objDict = {}
            objDict['Closed']  = res[i]
            objDict['date'] = i
            objList.append(objDict)

        counter = collections.Counter()
        
        for d in openStatusDateList:
            counter.update(d)
        res = dict(counter)
        print(res,file=sys.stderr)
        
        
        for i in res:
            objDict = {}
            objDict['date'] = i
            objDict['Open'] = res[i] 
            objList.append(objDict)

        counter = collections.Counter()
        
        for d in exceptionStatusDateList:
            counter.update(d)
        res = dict(counter)
        print(res,file=sys.stderr)
        
        
        for i in res:
            objDict = {}
            objDict['date'] = i
            objDict['Exception'] = res[i]
            objList.append(objDict)
        
        new_obj_list = {}
        for obj in objList:
            if obj['date'] not in new_obj_list:
                new_obj_list[obj['date']] = {"Closed":0, "Open":0, "Exception": 0, "date": obj['date']}
            if obj.get('Closed'):
                new_obj_list[obj['date']]['Closed'] = obj.get('Closed')
            if obj.get('Open'):
                new_obj_list[obj['date']]['Open'] = obj.get('Open')
            if obj.get('Exception'):
                new_obj_list[obj['date']]['Exception'] = obj.get('Exception')

        finalList = []
        finalList = (list(new_obj_list.values()))
        finalList.sort(key = lambda x: datetime.strptime(x['date'], '%d-%m-%Y'))
        print(finalList, file=sys.stderr)

        return jsonify(finalList),200

    except Exception as e:  

        print(str(e),file=sys.stderr)
        traceback.print_exc()
        return str(e),500

