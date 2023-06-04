import gzip
import sys, json
from flask_jsonpify import jsonify
from flask import request, make_response, Response
from app import app ,db , tz
from app.models.inventory_models import User_Table
from sqlalchemy import func
from datetime import datetime
import hashlib, secrets, string
from app.middleware import token_required

def InsertData(obj):
    #add data to db
    try:
        obj.creation_date= datetime.now(tz)
        obj.modification_date= datetime.now(tz)
        db.session.add(obj)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong in Database Insertion {e}", file=sys.stderr)

    return True

def UpdateData(obj):
    #add data to db
    #print(obj, file=sys.stderr)
    try:
        obj.modification_date= datetime.now(tz)
        db.session.merge(obj)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong in Database Updation {e}", file=sys.stderr)
    return True

def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%d-%m-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

@app.route("/addUser", methods = ['POST'])
@token_required
def AddUser(user_data):
    
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        userObj = request.get_json()
        #print(userObj,file=sys.stderr)

        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for i in range(16))

        user = User_Table()
        user.user_id = userObj['user_id']
        user.email = userObj['email_address']
        user.name = userObj['name']
        user.role = userObj['role']
        user.status = userObj['status']
        user.account_type = userObj['account_type']
        user.team = userObj['team']
        user.vendor = userObj['vendor']
        #user.token = userObj['name']+token

        if userObj['account_type'] == "Local":
            pas = hashlib.sha512()
            pas.update(userObj['password'].encode("utf8"))
            user.password=  str(pas.digest())
        else:
            pass
            #print("Can not Create User Without Password ",file=sys.stderr)
            #return jsonify({'response': "Can not Create User Without Password","code":"409"})
        
        if User_Table.query.with_entities(User_Table.user_id).filter_by(user_id=userObj['user_id']).first() is not None :          
            print("User Id Already Exists ",file=sys.stderr)
            return jsonify({'response': "User Id Already Exists","code":"409"})
        else:
            InsertData(user)
            print("Inserted " +userObj['user_id'],file=sys.stderr)
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllUsers", methods = ['GET'])
@token_required
def GetAllUsers(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        usersList=[]
        users = User_Table.query.all()

        for user in users:

            usersDic= {}
            usersDic['user_id']=user.user_id
            usersDic['email_address'] = user.email
            usersDic['name'] = user.name
            usersDic['role'] = user.role
            usersDic['status'] = user.status 
            usersDic['account_type'] = user.account_type
            usersDic['creation_date'] = FormatDate(user.creation_date)
            usersDic['modification_date'] = FormatDate(user.modification_date)
            usersDic['last_login'] = FormatDate(user.last_login)
            #usersDic['last_login'] = str(user.last_login)
            usersDic['team'] = user.team
            usersDic['vendor'] = user.vendor
            #usersDic['password'] = user.password
            
            usersList.append(usersDic)

        content = gzip.compress(json.dumps(usersList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editUser", methods = ['POST'])
@token_required
def EditUser(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        userObj = request.get_json()
        #print(userObj,file=sys.stderr)
        user = User_Table()
        user.user_id = userObj['user_id']
        user.email = userObj['email_address']
        user.name = userObj['name']
        user.role = userObj['role']
        user.status = userObj['status']
        user.account_type = userObj['account_type']
        user.team = userObj['team']
        user.vendor = userObj['vendor']

        #edit Password
        if userObj['password']:
            pas = hashlib.sha512()
            pas.update(userObj['password'].encode("utf8"))
            user.password=  str(pas.digest())
        
        UpdateData(user)
        print("Updated " + userObj['user_id'],file=sys.stderr)
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/getUserByToken", methods = ['GET'])
@token_required
def GetUserByToken(user_Data):
    user_info={}
    try:
        user_info["user_name"]= user_Data.get("user_id")
        user_info["user_role"]= user_Data.get("user_role")

        content = gzip.compress(json.dumps(user_info).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    
    except Exception as e:
            print("Failed to get user details", file=sys.stderr)
            return jsonify({'message': 'Failed to get user details'}), 401

@app.route("/editPassword", methods = ['POST'])
@token_required
def EditPassword(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
    
        userObj = request.get_json()
        pas = hashlib.sha512()
        pas.update(userObj['old_password'].encode("utf8"))
        userObj['old_password']=  str(pas.digest())  
        

        user = User_Table.query.filter_by(user_id=userObj['user_id']).filter_by(password=userObj['old_password']).first()
        if user:
            if user.status=="Active":
                print(userObj,file=sys.stderr)
                user = User_Table()
                user.user_id = userObj['user_id']
                pas = hashlib.sha512()
                pas.update(userObj['new_password'].encode("utf8"))
                user.password=  str(pas.digest())     
                UpdateData(user)
                print("Updated Password " + userObj['user_id'],file=sys.stderr)
                return jsonify({'response': "success","code":"200"})
            else:
                print("User is Inactive", file=sys.stderr)
                return jsonify({'message': 'User is Inactive'}), 401

        else: 
            print("Authentication Failed Incorrect Username/Password", file=sys.stderr)
            return jsonify({'message': 'Authentication Failed Incorrect Username/Password'}), 401


    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 

@app.route("/deleteUsers", methods = ['POST'])
@token_required
def DeleteUsers(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):

        userObj = request.get_json()
        for uid in userObj.get("user_ids"):
            
            user = User_Table.query.filter_by(user_id=uid).first()
            if user:
                db.session.delete(user)
                db.session.commit()
                print("User Deleted Successfully", file=sys.stderr)
                
            else: 
                print("User Not Found", file=sys.stderr)
                return jsonify({'message': 'User Not Found'}), 401
        return jsonify({'response': "success","code":"200"})
            

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 
