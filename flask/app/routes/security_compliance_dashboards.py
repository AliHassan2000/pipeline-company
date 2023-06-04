from app import app, db, tz
import traceback
from app.middleware import token_required
import json, sys
from datetime import date, datetime
from flask import request
import traceback
from flask_jsonpify import jsonify
from sqlalchemy import or_, and_
from app.models.inventory_models import SECURITY_COMPLIANCE_TABLE, Device_Table

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

def rows_as_dicts(cursor):
    """convert tuple result to dict with cursor"""
    col_names = [i[0] for i in cursor.description]
    return [dict(zip(col_names, row)) for row in cursor]

@app.route('/addNode', methods=['POST'])
@token_required
def addNode(user_data):
    try:
        obj = request.get_json()
        node = SECURITY_COMPLIANCE_TABLE()
        if "node_name" in obj:
            node.node_name = obj['node_name']
        else:
            raise Exception("Key 'node_name' is Missing")
        if "functions" in obj:
            functions_str = ",".join(obj["functions"])
            node.function = functions_str
        if "pn_codes" in obj:
            pncode_str = ",".join(obj["pn_codes"])
            node.pn_code = pncode_str
        if "domain" in obj:
            node.domain = obj['domain']
        else:
            raise Exception("Key 'domain' is Missing")
        try:
            if "node_id" in obj:
                if SECURITY_COMPLIANCE_TABLE.query.with_entities(SECURITY_COMPLIANCE_TABLE.node_id).filter_by(node_name=obj['node_name']).first() is not None:
                    node.node_id= SECURITY_COMPLIANCE_TABLE.query.with_entities(SECURITY_COMPLIANCE_TABLE.node_id).filter_by(node_name=obj['node_name']).first()[0]

                    node.modification_date= datetime.now(tz)
                    node.modified_by = user_data['user_id']
                    UpdateData(node)
                    print(f"Data Updated For VM: {node.node_name}", file=sys.stderr)
                    return jsonify({'code': "200", 'message': "Successfully Updated"}),200
                else:
                    return jsonify({'code': "200", 'message': f"{node.node_name} Not Found"}),200
            else:
                node.modification_date= datetime.now(tz)
                node.creation_date= datetime.now(tz)
                node.created_by = user_data['user_id']
                node.modified_by = user_data['user_id']
                InsertData(node)
                print("Data Inserted Into DB", file=sys.stderr)
                return jsonify({'message': "Successfully Inserted"}),200
        except Exception as e:
            print("Error While Adding Data In Table", file=sys.stderr)
            traceback.print_exc()
            return jsonify({'code': "400", 'message': "Node Name Already Exists For This Domain"}),200
        
    except Exception as e:
        print("Error While Adding Data In Table", file=sys.stderr)
        traceback.print_exc()
        return jsonify({f"Response": f"Failed to Update/Insert {e}"}),500

@app.route('/getNodeDataByNodeName', methods=['POST'])
@token_required
def GetNodeDataByNodeName(user_data):
    try:
        nodeObj = request.get_json()
        obj = SECURITY_COMPLIANCE_TABLE.query.with_entities(SECURITY_COMPLIANCE_TABLE.node_id, SECURITY_COMPLIANCE_TABLE.node_name, SECURITY_COMPLIANCE_TABLE.function, SECURITY_COMPLIANCE_TABLE.pn_code, SECURITY_COMPLIANCE_TABLE.domain).filter_by(node_name = nodeObj["node_name"]).filter_by(domain = nodeObj['domain']).first()
        func = []
        pncode = []
        if obj[2]:
            func = [s for s in obj[2].split(",")]
        if obj[3]:
            pncode = [s for s in obj[3].split(",")]
        dataDict = {}
        dataDict['node_id'] = obj[0]
        dataDict['node_name'] = obj[1]
        dataDict['functions'] = func
        dataDict['pn_codes'] = pncode
        dataDict['domain'] = obj[4]
        return jsonify(dataDict),200
    except Exception as e:
        print(f"Exception Occured {e}", file=sys.stderr)
        return str(e),500

@app.route('/deleteNode', methods=['POST'])
@token_required
def DeleteNode(user_data):
        try:
            objs = request.get_json()
            SECURITY_COMPLIANCE_TABLE.query.filter_by(node_name= objs["node_name"]).filter_by(domain = objs["domain"]).delete()
            db.session.commit()

            return jsonify({'response': "success", "code": "200"})
            
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
            return str(e),500

@app.route('/getSecurityCoverageSummaryStatus',methods = ['POST'])
@token_required
def GetSecurityCoverageSummaryStatus(user_data):
    try:
        domainObj = request.get_json()
        cisco_domain = domainObj['domain']
        nodes = SECURITY_COMPLIANCE_TABLE.query.with_entities(SECURITY_COMPLIANCE_TABLE.node_name, SECURITY_COMPLIANCE_TABLE.function, SECURITY_COMPLIANCE_TABLE.pn_code).filter_by(domain = cisco_domain).all()
        if nodes:
            devices = []
            function = []
            pn_code = []
            query_list = []
            dictList = []
            for node in nodes:
                if node[0] not in ('NULL',None):
                    devices.append(node[0])
                if node[1] not in ('NULL',None):
                    function = node[1].split(",")
                    # print("THIS IS MY FUNCTION", function, file=sys.stderr)
                if node[2] not in ('NULL',None):
                    pn_code = node[2].split(",")
                    # print("THIS IS MY PNCODE", pn_code, file=sys.stderr)
            
                query = createSecurityComplianceDomainsQuery(function, pn_code, cisco_domain)
                # print("$$$$$$$$$$$$$$$", query, file=sys.stderr)
                query_list.append(query)
            output = {}
            categories = ["PAM Integrations", "AAA Integrations", "MBSS Approved", "MBSS Compliance"]
            for category in categories:
                output[category] = {}
                for device in devices:
                    output[category][device] = []
            
            for query in query_list:
                finalObjs = db.session.execute(query)
                dict = rows_as_dicts(finalObjs.cursor)[0]
                # print("!!!!!!", dict, file=sys.stderr)
                dictList.append(dict)
            # print("THIS IS MY DICTIONARY LIST", dictList, file=sys.stderr)
            for i in range(len(devices)):
                device = devices[i]
                dict = dictList[i]
                # print("SINGLE DICT", dict, file=sys.stderr)
                output["PAM Integrations"][device] = [f"{dict['integrated_with_paam_progress']}/{dict['integrated_with_paam_scope']}", int(dict['integrated_with_paam_progress']/dict['integrated_with_paam_scope']*100) if dict['integrated_with_paam_scope'] !=0 else 0]
                output["AAA Integrations"][device] = [f"{dict['integrated_with_aaa_progress']}/{dict['integrated_with_aaa_scope']}", int(dict['integrated_with_aaa_progress']/dict['integrated_with_aaa_scope']*100) if dict['integrated_with_aaa_scope'] !=0 else 0]
                output["MBSS Approved"][device] = [f"{dict['approved_mbss_progress']}/{dict['approved_mbss_scope']}", int(dict['approved_mbss_progress']/dict['approved_mbss_scope']*100) if dict['approved_mbss_scope'] !=0 else 0]
                output["MBSS Compliance"][device] = [f"{dict['mbss_integration_check_progress']}/{dict['mbss_integration_check_scope']}", int(dict['mbss_integration_check_progress']/dict['mbss_integration_check_scope']*100) if dict['mbss_integration_check_scope'] !=0 else 0]
            
            total_dict = {}
            for keys in output:
                for key in output[keys]:
                    scope_list = output[keys][key]
                    if scope_list:
                        scope_progress = scope_list[0].split("/")
                        progress, scope = int(scope_progress[0]), int(scope_progress[1])
                        if keys + "_progress" in total_dict:
                            total_dict[keys + "_progress"] += progress
                        else:
                            total_dict[keys + "_progress"] = progress
                        
                        if keys + "_scope" in total_dict:
                            total_dict[keys + "_scope"] += scope
                        else:
                            total_dict[keys + "_scope"] = scope

            name = "PAM Integrations"
            output[name]['Total'] = [str(total_dict[f"{name}_progress"])+"/"+ str(total_dict[f"{name}_scope"]), round(total_dict[f"{name}_progress"]*100//total_dict[f"{name}_scope"], 2) if total_dict[f"{name}_scope"] != 0 else 0]
            name = "AAA Integrations"
            output[name]['Total'] = [str(total_dict[f"{name}_progress"])+"/"+ str(total_dict[f"{name}_scope"]), round(total_dict[f"{name}_progress"]*100//total_dict[f"{name}_scope"], 2) if total_dict[f"{name}_scope"] != 0 else 0]
            name = "MBSS Approved"
            output[name]['Total'] = [str(total_dict[f"{name}_progress"])+"/"+ str(total_dict[f"{name}_scope"]), round(total_dict[f"{name}_progress"]*100//total_dict[f"{name}_scope"], 2) if total_dict[f"{name}_scope"] != 0 else 0]
            name = "MBSS Compliance"
            output[name]['Total'] = [str(total_dict[f"{name}_progress"])+"/"+ str(total_dict[f"{name}_scope"]), round(total_dict[f"{name}_progress"]*100//total_dict[f"{name}_scope"], 2) if total_dict[f"{name}_scope"] != 0 else 0]

            json_data = json.dumps(output)
            return json_data,200
        
        tableDict = {}
        categories = ["PAM Integrations", "AAA Integrations", "MBSS Approved", "MBSS Compliance"]
        for category in categories:
            tableDict[category] = {}
        return tableDict
  
    except Exception as e:
      traceback.print_exc()
      return str(e), 500

@app.route('/getFunctions', methods=['GET'])
@token_required
def GetFunctions(user_data):
    try:
        domain = request.args.get('domain')
        objList = []

        if domain == "EDN":
            objs = Device_Table.query.with_entities(Device_Table.function.distinct()).filter(or_(Device_Table.cisco_domain == "EDN-NET", Device_Table.cisco_domain == "EDN-IPT")).all()
        elif domain == "IGW":
            objs = Device_Table.query.with_entities(Device_Table.function.distinct()).filter(Device_Table.cisco_domain == "IGW-NET").all()
        elif domain == "SYSTEM":
            objs = Device_Table.query.with_entities(Device_Table.function.distinct()).filter(or_(Device_Table.cisco_domain == "EDN-SYS", Device_Table.cisco_domain == "IGW-SYS")).all()
        elif domain == "SOC":
            objs = Device_Table.query.with_entities(Device_Table.function.distinct()).filter(Device_Table.cisco_domain == "SOC").all()
        
        for obj in objs:
            objList.append(str(obj[0]))

        return jsonify(objList),200
    except Exception as e:
        traceback.print_exc()
        print(f"Exception Occured in Loading Owners {e}", file=sys.stderr)
        return str(e),500

@app.route('/getPnCodes', methods=['POST'])
@token_required
def GetPnCodes(user_data):
    try:
        domain = request.args.get('domain')
        func = request.get_json()
        function = func['functions']
        objList = []
        
        if '' not in function and function:
            query = ''
            final_query = ''
            if domain == "EDN":
                final_query = """SELECT 
                DISTINCT(PN_CODE) 
                FROM device_table 
                WHERE (CISCO_DOMAIN = 'EDN-NET' OR CISCO_DOMAIN = 'EDN-IPT')"""
            elif domain == "IGW":
                final_query = """SELECT 
                DISTINCT(PN_CODE) 
                FROM device_table 
                WHERE CISCO_DOMAIN = 'IGW-NET'"""
            elif domain == "SYSTEM":
                final_query = """SELECT 
                DISTINCT(PN_CODE) 
                FROM device_table 
                WHERE (CISCO_DOMAIN = 'EDN-SYS' OR CISCO_DOMAIN = 'IGW-SYS')"""
            elif domain == "SOC":
                final_query = """SELECT 
                DISTINCT(PN_CODE) 
                FROM device_table 
                WHERE CISCO_DOMAIN = 'SOC'"""

            if '' not in function and function:
                if len(function)>1:
                    query += f" AND ("
                else:
                    query += f" AND "
                i=0
                for objs in function:
                    if i==0:
                        query += f"`FUNCTION` = '{objs}'"
                    else:
                        query += f" OR `FUNCTION` = '{objs}'"
                    i+=1
                if len(function)>1:
                    query += f")"

            final_query+= query+";"
            # print("@@@@@@@@@@@@", final_query, file=sys.stderr)
            objs = db.session.execute(final_query)

        else:
            if domain == "EDN":
                objs = Device_Table.query.with_entities(Device_Table.pn_code.distinct()).filter(or_(Device_Table.cisco_domain == "EDN-NET", Device_Table.cisco_domain == "EDN-IPT")).all()
            elif domain == "IGW":
                objs = Device_Table.query.with_entities(Device_Table.pn_code.distinct()).filter(Device_Table.cisco_domain == "IGW-NET").all()
            elif domain == "SYSTEM":
                objs = Device_Table.query.with_entities(Device_Table.pn_code.distinct()).filter(or_(Device_Table.cisco_domain == "EDN-SYS", Device_Table.cisco_domain == "IGW-SYS")).all()
            elif domain == "SOC":
                objs = Device_Table.query.with_entities(Device_Table.pn_code.distinct()).filter(Device_Table.cisco_domain == "SOC").all()

        for obj in objs:
            objList.append(str(obj[0]))

        return jsonify(objList),200
    except Exception as e:
        traceback.print_exc()
        print(f"Exception Occured in Loading Owners {e}", file=sys.stderr)
        return str(e),500

@app.route('/getFunctionsForBulkUpdate', methods=['GET'])
@token_required
def GetFunctionsForBulkUpdate(user_data):
    try:
        domain = request.args.get('domain')
        objList = []

        objs = Device_Table.query.with_entities(Device_Table.function.distinct()).filter_by(cisco_domain = domain).all()
        
        for obj in objs:
            objList.append(str(obj[0]))

        return jsonify(objList),200
    except Exception as e:
        print(f"Exception Occured in Loading Owners {e}", file=sys.stderr)
        return str(e),500

@app.route('/getPnCodesForBulkUpdate', methods=['POST'])
@token_required
def GetPnCodesForBulkUpdate(user_data):
    try:
        data = request.get_json()
        domain = data['domain']
        func = data['function']
        objList = []
        
        if func:
            objs = Device_Table.query.with_entities(Device_Table.pn_code.distinct()).filter(and_(Device_Table.cisco_domain == domain, Device_Table.function == func)).all()   
        else:
            objs = Device_Table.query.with_entities(Device_Table.pn_code.distinct()).filter_by(cisco_domain = domain).all()

        for obj in objs:
            objList.append(str(obj[0]))

        return jsonify(objList),200
    except Exception as e:
        print(f"Exception Occured in Loading Owners {e}", file=sys.stderr)
        return str(e),500
    
@app.route('/getDeviceIdsForBulkUpdate', methods=['POST'])
@token_required
def GetDeviceIdsForBulkUpdate(user_data):
    try:
        data = request.get_json()
        domain = data['domain']
        func = data['function']
        pncode = data['pn_code']
        objList = []

        if func and pncode:
            objs = Device_Table.query.with_entities(Device_Table.device_id.distinct()).filter(and_(Device_Table.cisco_domain == domain, Device_Table.function == func, Device_Table.pn_code == pncode)).all()
        elif func and not pncode:
            objs = Device_Table.query.with_entities(Device_Table.device_id.distinct()).filter(and_(Device_Table.cisco_domain == domain, Device_Table.function == func)).all()
        elif pncode and not func:
            objs = Device_Table.query.with_entities(Device_Table.device_id.distinct()).filter(and_(Device_Table.cisco_domain == domain, Device_Table.pn_code == pncode)).all()
        else:
            objs = Device_Table.query.with_entities(Device_Table.device_id.distinct()).filter_by(cisco_domain = domain).all()

        for obj in objs:
            objList.append(str(obj[0]))

        return jsonify(objList),200
    except Exception as e:
        print(f"Exception Occured in Loading Owners {e}", file=sys.stderr)
        return str(e),500

def createSecurityComplianceDomainsQuery(function, pn_code, domain):
    try:
        query=""
        count_query=""
        if domain == "EDN":
            count_query = """SELECT
            COUNT(INTEGRATED_WITH_PAAM) AS integrated_with_paam_scope,
            COALESCE(SUM(INTEGRATED_WITH_PAAM = 'Yes'), 0) AS integrated_with_paam_progress,
            COUNT(INTEGRATED_WITH_AAA) AS integrated_with_aaa_scope,
            COALESCE(SUM(INTEGRATED_WITH_AAA = 'Yes'), 0) AS integrated_with_aaa_progress,
            COUNT(APPROVED_MBSS) AS approved_mbss_scope,
            COALESCE(SUM(APPROVED_MBSS = 'Yes'), 0) AS approved_mbss_progress,
            COUNT(MBSS_INTEGRATION_CHECK) AS mbss_integration_check_scope,
            COALESCE(SUM(MBSS_INTEGRATION_CHECK = 'Yes'), 0) AS mbss_integration_check_progress
                FROM device_table WHERE STATUS = 'Production' AND (CISCO_DOMAIN = 'EDN-NET' OR CISCO_DOMAIN = 'EDN-IPT')"""
        elif domain == "IGW":
            count_query = """SELECT
            COUNT(INTEGRATED_WITH_PAAM) AS integrated_with_paam_scope,
            COALESCE(SUM(INTEGRATED_WITH_PAAM = 'Yes'), 0) AS integrated_with_paam_progress,
            COUNT(INTEGRATED_WITH_AAA) AS integrated_with_aaa_scope,
            COALESCE(SUM(INTEGRATED_WITH_AAA = 'Yes'), 0) AS integrated_with_aaa_progress,
            COUNT(APPROVED_MBSS) AS approved_mbss_scope,
            COALESCE(SUM(APPROVED_MBSS = 'Yes'), 0) AS approved_mbss_progress,
            COUNT(MBSS_INTEGRATION_CHECK) AS mbss_integration_check_scope,
            COALESCE(SUM(MBSS_INTEGRATION_CHECK = 'Yes'), 0) AS mbss_integration_check_progress
                FROM device_table WHERE STATUS = 'Production' AND CISCO_DOMAIN = 'IGW-NET'"""
        elif domain == "SYSTEM":
            count_query = """SELECT
            COUNT(INTEGRATED_WITH_PAAM) AS integrated_with_paam_scope,
            COALESCE(SUM(INTEGRATED_WITH_PAAM = 'Yes'), 0) AS integrated_with_paam_progress,
            COUNT(INTEGRATED_WITH_AAA) AS integrated_with_aaa_scope,
            COALESCE(SUM(INTEGRATED_WITH_AAA = 'Yes'), 0) AS integrated_with_aaa_progress,
            COUNT(APPROVED_MBSS) AS approved_mbss_scope,
            COALESCE(SUM(APPROVED_MBSS = 'Yes'), 0) AS approved_mbss_progress,
            COUNT(MBSS_INTEGRATION_CHECK) AS mbss_integration_check_scope,
            COALESCE(SUM(MBSS_INTEGRATION_CHECK = 'Yes'), 0) AS mbss_integration_check_progress
                FROM device_table WHERE STATUS = 'Production' AND (CISCO_DOMAIN = 'EDN-SYS' OR CISCO_DOMAIN = 'IGW-SYS')"""
        elif domain == "SOC":
            count_query = """SELECT
            COUNT(INTEGRATED_WITH_PAAM) AS integrated_with_paam_scope,
            COALESCE(SUM(INTEGRATED_WITH_PAAM = 'Yes'), 0) AS integrated_with_paam_progress,
            COUNT(INTEGRATED_WITH_AAA) AS integrated_with_aaa_scope,
            COALESCE(SUM(INTEGRATED_WITH_AAA = 'Yes'), 0) AS integrated_with_aaa_progress,
            COUNT(APPROVED_MBSS) AS approved_mbss_scope,
            COALESCE(SUM(APPROVED_MBSS = 'Yes'), 0) AS approved_mbss_progress,
            COUNT(MBSS_INTEGRATION_CHECK) AS mbss_integration_check_scope,
            COALESCE(SUM(MBSS_INTEGRATION_CHECK = 'Yes'), 0) AS mbss_integration_check_progress
                FROM device_table WHERE STATUS = 'Production' AND CISCO_DOMAIN = 'SOC'"""
        if '' not in function and function:
            # print("##FUNCTION##", function, file=sys.stderr)
            if len(function)>1:
                query += f" AND ("
            else:
                query += f" AND "
            i=0
            for objs in function:
                if i==0:
                    query += f"`FUNCTION` = '{objs}'"
                else:
                    query += f" OR `FUNCTION` = '{objs}'"
                i+=1
            if len(function)>1:
                query += f")"  
        if '' not in pn_code and pn_code:
            # print("##PN_CODE##", pn_code, file=sys.stderr)
            if len(pn_code)>1:
                query += f" AND ("
            else:
                query += f" AND "
            i=0
            for objs in pn_code:
                if i==0:
                  query += f"PN_CODE = '{objs}'"
                else:
                    query += f" OR PN_CODE = '{objs}'"
                i+=1
            if len(pn_code)>1:
                query += f")"
            
        count_query+= query+";"
        return count_query
    except Exception as e:
        return ""
