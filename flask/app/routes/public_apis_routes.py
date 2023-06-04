from ast import Not
import imp
import traceback
from unittest import result
from flask import Flask, jsonify, make_response, request
from functools import wraps
import jwt
from datetime import datetime, timedelta
from app import app ,tz
import json
import sys
from app.models.phy_mapping_models import  EDN_SERVICE_MAPPING, IGW_SERVICE_MAPPING
from app import app,db,phy_engine
from app.routes.physical_mapping_routes import AddEdnServiceDevicesFuncApi, AddIgwServiceDevicesFuncApi
from app.models.phy_mapping_models import IT_APP_TABLE, IT_IP_TABLE, IT_MAC_TABLE, IT_OS_TABLE, IT_OWNER_TABLE, IT_PHYSICAL_SERVERS_TABLE
from app.routes.it_services_routes import AddAppDataFunc, AddIpDataFunc, AddMacDataFunc, AddOSDataFunc, AddOwnersDataFunc, AddPhysicalServerFunc

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
    print(f"Dataa is : {obj.creation_date}", file=sys.stderr)
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
 
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'X-Auth-Key' in request.headers:
           token = request.headers['X-Auth-Key']
 
        if not token:
           return jsonify({'Response': ' Authentication Token is Missing'})
        try:
           data = jwt.decode(token, "itteam@mobily", algorithms=["HS256"])
           #current_user = Users.query.filter_by(public_id=data['public_id']).first()
         
        except jwt.ExpiredSignatureError as error:
            return {
                "Response": "Token is expired",
                "data": None,
                "error": "Session Expired"
            }, 401

        except jwt.exceptions.InvalidTokenError as error:
                return {
                "Response": "Invalid Token",
                "data": None,
                "error": "Invalid Token"
            }, 401
        
        except Exception as e:
            print(f"Error occured while Decoding Data {e}", file=sys.stderr)
            return {
                "Response": "Internal Server Error",
                "data": None,
                "error": str(e)
            }, 500
        
        return f(data, *args, **kwargs)
 
    return decorator

@app.route('/services-login', methods=['POST']) 
def login_user():
    auth = request.authorization  
    if not auth or not auth.username or not auth.password: 
        return make_response('could not verify', 401, {'Authentication': 'login required"'})   

    with open('app/cred.json') as inventory:
        inv = json.loads(inventory.read())
        
        user_name = inv['IT_TEAM']['user']
        user_password= inv['IT_TEAM']['pwd']
    #print(user_name, file=sys.stderr)
    #print(user_password, file=sys.stderr)
    #print(auth.username, file=sys.stderr)
    #print(auth.password, file=sys.stderr)

    #user = Users.query.filter_by(name=auth.username).first()  
    if user_name== auth.username and user_password== auth.password:
        token = jwt.encode({'user_name' : user_name, 'user_role': 'it_team', 'exp' : datetime.utcnow() + timedelta(minutes=45)}, "itteam@mobily", "HS256")
        return jsonify({'token' : token})
    
    return make_response('Authentication Failed',  401, {'Authentication': '"login required"'})

@app.route("/ednServices", methods = ['POST'])
@token_required
def AddEdnServices(user_data):
    
    if user_data['user_role']=="it_team"  :#request.headers.get('X-Auth-Key') == session.get('token', None):
        try:       
            result= AddEdnServiceDevicesFuncApi(user_data)

            return result
        except Exception as e:
            print(f"Error occured when importing igw Mapping {e}", file=sys.stderr)
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Unauthorized", file=sys.stderr)
        return jsonify({'Response': 'Unauthorized to Post Data'}), 401
  
@app.route("/igwServices", methods = ['POST'])
@token_required
def AddIgwServices(user_data):
    
    print(user_data, file=sys.stderr)
    if user_data['user_role']=="it_team"  :#request.headers.get('X-Auth-Key') == session.get('token', None):
        try:       
            result= AddIgwServiceDevicesFuncApi(user_data)
            return result
        except Exception as e:
            print(f"Error occured when importing igw Mapping {e}", file=sys.stderr)
        
    
    else: 
        print("Unauthorized", file=sys.stderr)
        return jsonify({'Response': 'Unauthorized to Post Data'}), 401
    
'''
IT Serviec Routes

'''

@app.route('/physicalServers', methods=['POST'])
@token_required
def AddPhysicalServer(user_data):
    if True:
        response= AddPhysicalServerFunc()
        return response
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'Response': 'Unauthorized to Post Data'}), 401


@app.route('/appTable', methods=['POST'])

def AddAppData():
    if True:
        
        response= AddAppDataFunc()
        return response
        
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'Response': 'Unauthorized to Post Data'}), 401



@app.route('/osTable', methods=['POST'])

def AddOSData():
    if True:
        response= AddOSDataFunc()
        return response

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'Response': 'Unauthorized to Post Data'}), 401


@app.route('/macTable', methods=['POST'])

def AddMacData():
    if True:
        response= AddMacDataFunc()
        return response

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'Response': 'Unauthorized to Post Data'}), 401


@app.route('/ipTable', methods=['POST'])

def AddIpData():
    if True:
        response= AddIpDataFunc()
        return response
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'Response': 'Unauthorized to Post Data'}), 401

@app.route('/owners', methods=['POST'])

def AddOwnersData():
    if True:
        response= AddOwnersDataFunc()
        return response

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'Response': 'Unauthorized to Post Data'}), 401   