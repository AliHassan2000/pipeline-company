from functools import wraps
import imp
from flask import Flask, request
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import pytz, json, sys
from flasgger import Swagger
from flask_jsonpify import jsonify
import jwt
from sqlalchemy.pool import QueuePool


app = Flask(__name__)
swagger = Swagger(app)
cors = CORS(app, supports_credentials=True)

api = Api(app)

app.secret_key = 'cisco-mobily'
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"



app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:As123456?@invdb:3306/InventoryDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_BINDS'] = {
        'phymapping': 'mysql+pymysql://root:As123456?@phymapping:3306/PhyMappingDB',
        'InventoryDB': 'mysql+pymysql://root:As123456?@invdb:3306/InventoryDB'
}


db = SQLAlchemy(app)
phy_engine = db.get_engine(app, 'phymapping')
inv_engine = db.get_engine(app, 'InventoryDB')
tz = pytz.timezone('Asia/Riyadh')
#########initialize Operational Influx DB
token = "token"
operationalClient = InfluxDBClient(url="http://influxdb:8086", token=token)
write_operational = operationalClient.write_api(write_options=SYNCHRONOUS)
read_operational = operationalClient.query_api()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        #if "Authorization" in request.headers:
        if "X-Auth-Key" in request.headers:
            token = request.headers["X-Auth-Key"]#.split(" ")[1]
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            user_data=jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"], options={"require": ["user_id", "user_role", "user_status", "iat", "exp"]})
            if user_data["user_id"] is None or user_data["user_role"] is None or user_data["user_status"] != "Active":
                return {
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401
            
        except jwt.ExpiredSignatureError as error:
            return {
                "message": "Token is expired",
                "data": None,
                "error": "Session Expired"
            }, 401

        except jwt.exceptions.InvalidTokenError as error:
                return {
                "message": "Invalid Token",
                "data": None,
                "error": "Invalid Token"
            }, 401
        except jwt.exceptions.InvalidSignatureError:
                return {
                "message": "Invalid Token Signature",
                "data": None,
                "error": "Invalid Token Signature"
            }, 401
        except Exception as e:
            print(f"Error occured while Decoding Data {e}", file=sys.stderr)
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500
        
        return f(user_data, *args, **kwargs)

    return decorated

'''
def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       token = None
       if 'X-Auth-Key' in request.headers:
           token = request.headers['X-Auth-Key']
 
       if not token:
           return jsonify({'message': 'a valid token is missing'})
       try:
           #data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
           #current_user = Users.query.filter_by(public_id=data['public_id']).first()
           session.pop('token', None)
       except:
           return jsonify({'message': 'token is invalid'})
 
       return f(current_user, *args, **kwargs)
   return decorator


with open('app/util.json') as util_file:
        auth = json.loads(util_file.read())
        if 'authorization' in auth:
            auth_key = auth['authorization']

@app.before_request
def before_calback():
    print(request.headers.get('authorization'), file=sys.stderr)
    
    if request.method != 'OPTIONS':  
        auth_header = request.headers.get("authorization")
        if auth_header == auth_key:
            print("Authentication Successfull", file=sys.stderr)
        else:
            print("Authentication Failed", file=sys.stderr)
            return jsonify({'message': 'Token is missing'}), 401
    else:
        print("Token is missing", file=sys.stderr)
        return jsonify({'message': 'Token is missing'}), 401
    
    return jsonify({'message': 'Token is missing'}), 200
'''

from app.routes import inventory_routes
from app import scheduler
from app.routes import operationstatus_routes
from app.routes import edn_service_mapping_routes
from app.routes import login_routes
from app.routes import dashboard_routes
from app.routes import test_routes
from app.routes import physical_mapping_routes
from app.routes import user_routes
from app.routes import ipt_endpoints_routes
from app.routes import edn_net_dashboard_routes
from app.routes import igw_net_dashboard_routes
from app.routes import edn_sys_dashboard_routes
from app.routes import igw_sys_dashboard_routes
from app.routes import soc_dashboard_routes
from app.routes import eos_expiry_routes
from app.routes import ipam_routes
from app.routes import dc_capacity_routes
from app.routes import dc_capacity_dashboard_routes
from app.routes import ipam_dashboard_routes
from app.routes import edn_exchange_routes
from app.routes import public_apis_routes
from app.routes import edn_exchange_dashboard_routes
from app.routes import access_points_routes
from app.routes import it_services_routes
from app.routes import tracker_routes
from app.routes import admin_routes
from app.routes import ipt_endpoints_dashboard_routes
from app.routes import failed_devices_routes
from app.routes import vulnerabilities_routes
from app.routes import vulneribility_dashboard_routes
from app.routes import service_mapping_dashboard_routes
from app.routes import f5_routes
from app.routes import f5_dashboard_routes
from app.routes import igw_link_routes
from app.routes import edn_core_routing_routes
from app.routes import security_compliance_dashboards