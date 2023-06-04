from operator import pos
from re import sub
import site
import traceback
from app import app,db, tz
from app.models.inventory_models import Phy_Table, Rack_Table, Device_Table, Board_Table, Subboard_Table, SFP_Table, License_Table, Seed, SNTC_Table, PnCode_SNAP_Table,IPT_Endpoints_Table
from flask_jsonpify import jsonify
import pandas as pd
import json, sys, time
from datetime import date, datetime
from flask import request, make_response, Response
import gzip
import io
from dateutil.relativedelta import relativedelta
from sqlalchemy import func

from app.middleware import token_required


@app.route('/iptEndpointsInventoryCounts',methods = ['GET'])
@token_required
def IptEndpointsInventoryCounts(user_data):
    if True:
        try:
            objList = []
            queryString = f"select count(*) from ipt_endpoints_table where hostname not like '%SEP%' and STATUS='Registered';"
            result = db.session.execute(queryString).scalar()
            queryStringA = f"select count(*) from ipt_endpoints_table where hostname not like '%SEP%' and STATUS!='Removed';"
            resultA = db.session.execute(queryStringA).scalar()
            objDict = {}
            objDict['name'] = 'Registered Soft Phones'
            objDict['value'] = f"{int(result)}"
            objList.append(objDict)

            queryString1 = f"select count(*) from ipt_endpoints_table where hostname like 'SEP%' and STATUS='Registered';"
            result1 = db.session.execute(queryString1).scalar()
            queryStringB  = f"select count(*) from ipt_endpoints_table where hostname like '%SEP%' and STATUS!='Removed';"
            resultB = db.session.execute(queryStringB).scalar()
            objDict = {}
            objDict['name'] = 'Registered Phones'
            objDict['value'] = f"{int(result1)}"
            objList.append(objDict)

            queryString2 = f"select distinct (EXTENSIONS) from ipt_endpoints_table where extensions is not null and extensions!='';"
            result2 = db.session.execute(queryString2)
            queryStringC = f"select count(EXTENSIONS) from ipt_endpoints_table where extensions is not null and extensions!='' and STATUS!='Removed';"
            resultC = db.session.execute(queryStringC).scalar()
            count = 0
            for row in result2:
                    count+=1
            objDict = {}
            objDict['name'] = 'Total number of Lines'
            objDict['value'] = f"{int(count)}"
            objList.append(objDict)

            queryString3 = f"select count(*) from ipt_endpoints_table where PRODUCT_ID='Cisco TelePresence EX90' and STATUS='Registered';"
            result3= db.session.execute(queryString3).scalar()
            queryStringD = f"select count(*) from ipt_endpoints_table where PRODUCT_ID='Cisco TelePresence EX90' and STATUS!='Removed';"
            resultD = db.session.execute(queryStringD).scalar()
            objDict = {}
            objDict['name'] = 'Registered EX90'
            objDict['value'] = f"{int(result3)}/{int(resultD)}"
            objList.append(objDict)

            queryString4 = f"select count(*) from ipt_endpoints_table where PRODUCT_ID='Cisco Webex DX80' and STATUS='Registered';"
            result4 = db.session.execute(queryString4).scalar()
            queryStringE = f"select count(*) from ipt_endpoints_table where PRODUCT_ID='Cisco Webex DX80' and STATUS!='Removed';"
            resultE = db.session.execute(queryStringE).scalar()
            objDict = {}
            objDict['name'] = 'Registered DX80'
            objDict['value'] = f"{int(result4)}/{int(resultE)}"
            objList.append(objDict)
            
            queryString5 = f"select count(*) from ipt_endpoints_table where PRODUCT_ID='Cisco Webex Desk Pro' and STATUS='Registered';"
            result5 = db.session.execute(queryString5).scalar()
            queryStringF = f"select count(*) from ipt_endpoints_table where PRODUCT_ID='Cisco Webex Desk Pro' and STATUS!='Removed';"
            resultF = db.session.execute(queryStringF).scalar()
            objDict = {}
            objDict['name'] = 'Registered DeskPro'
            objDict['value'] = f"{int(result5)}/{int(resultF)}"
            objList.append(objDict)

            queryString6 = f"select count(*) from ipt_endpoints_table where PRODUCT_ID='Cisco Webex Board 55' or PRODUCT_ID='Cisco Webex Room 70 Single' or PRODUCT_ID='Cisco Webex Board Pro 55'or PRODUCT_ID='Cisco Webex Room 55' and STATUS='Registered';"
            result6 = db.session.execute(queryString6).scalar()
            queryStringG = f"select count(*) from ipt_endpoints_table where PRODUCT_ID='Cisco Webex Board 55' or PRODUCT_ID='Cisco Webex Room 70 Single' or PRODUCT_ID='Cisco Webex Board Pro 55'or PRODUCT_ID='Cisco Webex Room 55' and STATUS!='Removed';"
            resultG = db.session.execute(queryStringG).scalar()
            objDict = {}
            objDict['name'] = 'Registered Webex 55/70'
            objDict['value'] = f"{int(result6)}/{int(resultG)}"
            objList.append(objDict)

            print(objList,file=sys.stderr)
            return jsonify(objList),200
        except Exception as e:
            traceback.print_exc()
            print(str(e),file=sys.stderr)
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route('/topUsersWithAssociatedPhones',methods = ['GET'])
@token_required
def TopUsersWithAssociatedPhones(user_data):
    if True:
        try:
            objList = []
            # queryString = f"select EXTENSIONS,count(EXTENSIONS) as Registered from ipt_endpoints_table where STATUS='Registered' and EXTENSIONS is not NULL  and EXTENSIONS!='' group by EXTENSIONS ORDER BY count(EXTENSIONS) DESC LIMIT 5;"

            queryString = f"select user,count(user)  from ipt_endpoints_table where STATUS='Registered' and user is not NULL  and user!='' group by user ORDER BY count(user) DESC LIMIT 5;" 
            result = db.session.execute(queryString)
            for row in result:
                user = row[0]
                count = row[1]
                objDict = {}
                objDict['user_id'] = user
                objDict['registered_phones_count'] = count
                queryString1 = f"select user,count(user)  from ipt_endpoints_table where STATUS='Unregistered' and user='{user}'"
                result1 = db.session.execute(queryString1)
                for row1 in result1:
                    # user1 = row1[0]
                    count1 = row1[1]
                    objDict['unregistered_phones_count'] = count1
                    
                    objList.append(objDict)
            print(objList,file=sys.stderr)
            return  jsonify(objList),200
        except Exception as e:
            traceback.print_exc()
            print(str(e),file=sys.stderr)
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401