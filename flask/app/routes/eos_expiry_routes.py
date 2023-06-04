from operator import pos
from re import sub
from app import app,db, tz
from app.models.inventory_models import Phy_Table, Rack_Table, Device_Table, Board_Table, Subboard_Table, SFP_Table, License_Table, Seed, SNTC_Table, PnCode_SNAP_Table
from flask_jsonpify import jsonify
import pandas as pd
import json, sys, time
from datetime import date, datetime
from flask import request, make_response, Response,session
from app.pullers.IOS.ios_inv import IOSPuller
from app.pullers.NXOS.nxos_inv import NXOSPuller
from app.pullers.IOSXR.ios_xr_inv import XRPuller
from app.pullers.IOSXE.ios_xe_inv import XEPuller
from app.pullers.IOS.ios_inv import IOSPuller
from app.pullers.ACI.aci_inv import ACIPuller
from app.pullers.WLC.cisco_wlc_inv import WLCPuller
from app.pullers.Prime.prime_inv import PrimePuller
from app.pullers.UCS.ucs_cimc_inv import UCSPuller
from app.pullers.A10.a10_inv import A10Puller
from app.pullers.Infoblox.infoblox_inv import InfoboxPuller
from app.pullers.Arista.arista_inv import AristaPuller
from app.pullers.Arbor.arbor_inv import ArborPuller
from app.pullers.IPT.ipt_inv import IPTPuller
from app.pullers.Wirefilter.wirefilter_inv import WirefilterPuller
from app.pullers.Fortinet.fortinet_inv import FortinetPuller
from app.pullers.Juniper.juniper_inv import JuniperPuller
from app.pullers.Juniper_Screenos.juniper_screenos_inv import JuniperScreenosPuller
from app.pullers.ASA.cisco_asa_inv import ASAPuller
from app.pullers.ASA.cisco_asa_inv96 import ASA96Puller
from app.pullers.PaloAlto.palo_alto_inv import PaloAltoPuller
from app.pullers.Pulse_Secure.pulse_secure_inv import PulseSecurePuller
from app.pullers.Symantec.symantec_inv import SymantecPuller
from app.pullers.Fireeye.fireeye_inv import FireEyePuller
from app.pullers.Firepower.firepower_inv import FirePowerPuller
from app.pullers.Firepower.firepower_inv_ssh import FirePowerPullerSSH
from multiprocessing import Process, Pool, Semaphore
import gzip
import io
from sqlalchemy import func
from app.middleware import token_required


@app.route('/eosStatusEdnNet',methods=['GET'])
@token_required
def EosStatusEdnNet(user_data):
    if True:
        queryString1 = "select coalesce(sum(STACK),0) from device_table where HW_EOS_DATE <= NOW() and CISCO_DOMAIN='EDN-NET' and STATUS='Production';"
        queryString2 = "select coalesce(sum(STACK),0) from device_table where HW_EOS_DATE >= NOW() and CISCO_DOMAIN='EDN-NET' and STATUS='Production';"
        result1 = db.session.execute(queryString1).scalar()
        result2 = db.session.execute(queryString2).scalar()
        
        objList = [
            {
                "name":"Expired EOS",
                "value":result1  
            },
            {
                "name":"Valid EOS",
                "value":result2
            }
        ] 
        return jsonify(objList),200
    else:
        print("Authentication Failed",file=sys.stderr)
        return jsonify({"message":"Authentication Failed"}),401
    
@app.route('/eosStatusIgwNet',methods=['GET'])
@token_required
def EosStatusIgwNet(user_data):
    if True:
        queryString1 = "select coalesce(sum(STACK),0) from device_table where HW_EOS_DATE <= NOW() and CISCO_DOMAIN='IGW-NET' and STATUS='Production';"
        queryString2 = "select coalesce(sum(STACK),0) from device_table where HW_EOS_DATE >= NOW() and CISCO_DOMAIN='IGW-NET' and STATUS='Production';"
        result1 = db.session.execute(queryString1).scalar()
        result2 = db.session.execute(queryString2).scalar()
        
        objList = [
            {
                "name":"Expired EOS",
                "value":int(result1)  
            },
            {
                "name":"Valid EOS",
                "value":int(result2)
            }
        ] 
        return jsonify(objList),200
    else:
        print("Authentication Failed",file=sys.stderr)
        return jsonify({"message":"Authentication Failed"}),401
    
@app.route('/eosStatusEdnSys',methods=['GET'])
@token_required
def EosStatusEdnSys(user_data):
    if True:
        queryString1 = "select coalesce(sum(STACK),0) from device_table where HW_EOS_DATE <= NOW() and CISCO_DOMAIN='EDN-SYS' and STATUS='Production';"
        queryString2 = "select coalesce(sum(STACK),0) from device_table where HW_EOS_DATE >= NOW() and CISCO_DOMAIN='EDN-SYS' and STATUS='Production';"
        result1 = db.session.execute(queryString1).scalar()
        result2 = db.session.execute(queryString2).scalar()
        
        objList = [
            {
                "name":"Expired EOS",
                "value":int(result1)  
            },
            {
                "name":"Valid EOS",
                "value":int(result2)
            }
        ] 
        return jsonify(objList),200
    else:
        print("Authentication Failed",file=sys.stderr)
        return jsonify({"message":"Authentication Failed"}),401
    
@app.route('/eosStatusIgwSys',methods=['GET'])
@token_required
def EosStatusIgwSys(user_data):
    if True:
        queryString1 = "select coalesce(sum(STACK),0) from device_table where HW_EOS_DATE <= NOW() and CISCO_DOMAIN='IGW-SYS' and STATUS='Production';"
        queryString2 = "select coalesce(sum(STACK),0) from device_table where HW_EOS_DATE >= NOW() and CISCO_DOMAIN='IGW-SYS' and STATUS='Production';"
        result1 = db.session.execute(queryString1).scalar()
        result2 = db.session.execute(queryString2).scalar()
        
        objList = [
            {
                "name":"Expired EOS",
                "value":int(result1)  
            },
            {
                "name":"Valid EOS",
                "value":int(result2)
            }
        ] 
        return jsonify(objList),200
    else:
        print("Authentication Failed",file=sys.stderr)
        return jsonify({"message":"Authentication Failed"}),401
    
@app.route('/eosStatusSoc',methods=['GET'])
@token_required
def EosStatusSoc(user_data):
    if True:
        queryString1 = "select coalesce(sum(STACK),0) from device_table where HW_EOS_DATE <= NOW() and CISCO_DOMAIN='SOC' and STATUS='Production';"
        queryString2 = "select coalesce(sum(STACK),0) from device_table where HW_EOS_DATE >= NOW() and CISCO_DOMAIN='SOC' and STATUS='Production';"
        result1 = db.session.execute(queryString1).scalar()
        result2 = db.session.execute(queryString2).scalar()
        
        objList = [
            {
                "name":"Expired EOS",
                "value":int(result1)  
            },
            {
                "name":"Valid EOS",
                "value":int(result2)
            }
        ] 
        return jsonify(objList),200
    else:
        print("Authentication Failed",file=sys.stderr)
        return jsonify({"message":"Authentication Failed"}),401
    
@app.route('/eosStatusEdnIpt',methods=['GET'])
@token_required
def EosStatusEdnIpt(user_data):
    if True:
        queryString1 = "select count(*) from device_table where HW_EOS_DATE <= NOW() and CISCO_DOMAIN='EDN-IPT' and STATUS='Production';"
        queryString2 = "select count(*) from device_table where HW_EOS_DATE >= NOW() and CISCO_DOMAIN='EDN-IPT' and STATUS='Production';"
        result1 = db.session.execute(queryString1).scalar()
        result2 = db.session.execute(queryString2).scalar()
        
        objList = [
            {
                "name":"Expired EOS",
                "value":int(result1)  
            },
            {
                "name":"Valid EOS",
                "value":int(result2)
            }
        ] 
        return jsonify(objList),200
    else:
        print("Authentication Failed",file=sys.stderr)
        return jsonify({"message":"Authentication Failed"}),401
    
@app.route('/eosStatusPos',methods=['GET'])
@token_required
def EosStatusPos(user_data):
    if True:
        # queryString1 = "select count(*) from device_table where HW_EOS_DATE <= NOW() and CISCO_DOMAIN='POS';"
        # queryString2 = "select count(*) from device_table where HW_EOS_DATE >= NOW() and CISCO_DOMAIN='POS';"
        # result1 = db.session.execute(queryString1).scalar()
        # result2 = db.session.execute(queryString2).scalar()
        
        objList = [
            {
                "name":"Expired EOS",
                # "value":result1  
                "value":0
            },
            {
                "name":"Valid EOS",
                # "value":result2
                "value":0
            }
        ] 
        return jsonify(objList),200
    else:
        print("Authentication Failed",file=sys.stderr)
        return jsonify({"message":"Authentication Failed"}),401
