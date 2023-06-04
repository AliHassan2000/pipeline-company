from errno import ECANCELED
import os
import sys, json
import traceback
from flask_jsonpify import jsonify
from flask import Flask, request, make_response, Response
from app import app ,db , tz, phy_engine, inv_engine
import requests
from app.models.inventory_models import Phy_Table, Rack_Table, Device_Table, Board_Table, Subboard_Table, SFP_Table, License_Table, Seed, PnCode_SNAP_Table, Seed, EDN_SEC_Seed, POWER_FEEDS_TABLE, EDN_EXCHANGE, EXTERNAL_VRF_ANALYSIS, VRF_ROUTES, EDN_CORE_ROUTING
import pandas as pd
from datetime import datetime, timedelta
from netmiko import Netmiko
from random import randint
import smtplib
from smtplib import SMTPException
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.message import EmailMessage
import socket
#import pysftp
from app.routes.physical_mapping_routes import FetchEdnArpFunc, FetchEdnCdpLegacyFunc, FetchEdnMacLegacyFunc, FetchEdnLLDPACIFunc, FetchIGWCdpLegacyFunc, FetchIGWLLDPACIFunc, getAllIgwMappingsFunc, GetAllEdnMappingsFunc
from app.models.phy_mapping_models import EDN_FIREWALL_ARP
import pysftp
from app.models.inventory_models import Access_Points_Table, Seed
from app.scheduler import SendPhysicalMappingReports
import os
import shutil
#from netaddr import oui
from sqlalchemy import update
import netaddr
from netaddr import IPNetwork, IPAddress

from app.models.inventory_models import IPT_Endpoints_Table
from app.models.inventory_models import POWER_FEEDS_TABLE
from app.models.inventory_models import SNTC_Table

def InsertData(obj):
    #add data to db
    obj.creation_date= datetime.now(tz)
    obj.modification_date= datetime.now(tz)
    db.session.add(obj)
    db.session.commit()
    return True

def UpdateData(obj):
    #add data to db
    try:
        obj.modification_date= datetime.now(tz)
        db.session.merge(obj)
        db.session.commit()
        #print(obj.site_name, file=sys.stderr)
    except:
        db.session.rollback()
        print("Something else went wrong", file=sys.stderr)
    
    return True
def FormatStringDate(date):
    print(date, file=sys.stderr)
    try:
    #if date:
        if date is not None:
            if '-' in date:
                result = datetime.strptime(date,'%Y-%m-%d')
            elif '/' in date:
                result = datetime.strptime(date,'%Y/%m/%d')
            else:
                print("incorrect date format", file=sys.stderr)
                result = datetime(2000, 1, 1)
        else:
            #result = datetime(2000, 1, 1)
            result = datetime(2000, 1, 1)
    except:
        result=date
        print("date format exception", file=sys.stderr)

    return result

def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%d-%m-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

@app.route("/UpdateBoardsTagIdsInDB", methods = ['GET'])
def updateSBoardsTagIdsInDB():
    tagIdsStart= 1867668
    objs = Board_Table.query.filter(Board_Table.device_id.like("SULM%")).filter(Board_Table.status != "dismantle").filter(Board_Table.board_name.notlike("%Transceiver%")).all()
    try:
        for obj in objs:
            try:
                obj.tag_id= tagIdsStart
                db.session.flush()
                db.session.commit()
                tagIdsStart+=1
            except Exception as e:
                db.session.rollback()
                print("Failed to assign Tag Id", fie=sys.stderr)
        return f"Last Assigned Tag is {(tagIdsStart-1)}"
    except Exception as e:
        return "Failed to assign tag ids "+str(e)

@app.route("/UpdateSubBoardsTagIdsInDB", methods = ['GET'])
def upateSubBoardsTagIdsInDB():
    tagIdsStart= 1867969
    objs = Subboard_Table.query.filter(Subboard_Table.device_id.like("SULM%")).filter(Subboard_Table.status != "dismantle").filter(Subboard_Table.subboard_name.notlike("%Transceiver%")).all()
    try:
        for obj in objs:
            try:
                obj.tag_id= tagIdsStart
                db.session.flush()
                db.session.commit()
                tagIdsStart+=1
            except Exception as e:
                db.session.rollback()
                print("Failed to assign Tag Id", fie=sys.stderr)
        return f"Last Assigned Tag is  ||  {(tagIdsStart-1)}"
    except Exception as e:
        return "Failed to assign tag ids "+str(e)


@app.route("/countBoardsSelectedForTagIds", methods = ['GET'])
def CountBOARDSFORTAGIDS():
    #queryString = f"select * from board_table where device_id LIKE 'SULM%' and STATUS != 'dismantle' and board_name not LIKE 'Transceiver%';"
    #result = db.session.execute(queryString) 
    count=0    
    #for row in result:                  
    #    count+=1
    objs = Board_Table.query.filter(Board_Table.device_id.like("SULM%")).filter(Board_Table.status != "dismantle").filter(Board_Table.board_name.notlike("%Transceiver%")).all()
    for obj in objs:
        count+=1
    
    return str(count)
        
@app.route("/updateDeviceStatus", methods = ['GET'])
def UpdateDeviceStatus():
    
    df = pd.read_excel('temp/dismantle list.xlsx', sheet_name = 'Sheet1')

    # db.session.execute("SET FOREIGN_KEY_CHECKS=0")

    for index, frame in df['ne_ip_address'].iteritems():
 
        try:
            obj = Device_Table.query.filter(Device_Table.ne_ip_address == frame).first()
            if(obj):
                obj.status = 'Excluded'

                db.session.flush()
                db.session.commit()
                print(frame + " Excluded" , file=sys.stderr)
            else:
                print(f"Not Found {frame}", file=sys.stderr)
        except:
            print('Error in Updating Device Table' , file=sys.stderr)
            db.session.rollback()
            raise
        
        try:
            obj = Seed.query.filter(Seed.ne_ip_address == frame).first()
            if(obj):

                obj.operation_status = 'Excluded'
                db.session.flush()
                db.session.commit()

                print(frame + " Excluded  " , file=sys.stderr)

        except:
            print('Error in Updating Seed Table' , file=sys.stderr)

    ################################ Offloaded devices

    df = pd.read_excel('temp/dismantle list.xlsx', sheet_name = 'Sheet2')

    for index, frame in df['ne_ip_address'].iteritems():
 
        try:
            obj = Device_Table.query.filter(Device_Table.ne_ip_address == frame).first()
            if(obj):
                obj.status = 'Offloaded'

                db.session.flush()
                db.session.commit()
                print(frame + " Offloaded" , file=sys.stderr)

        except:
            print('Error in Updating Device Table' , file=sys.stderr)
            db.session.rollback()
            raise
        
        try:
            obj = Seed.query.filter(Seed.ne_ip_address == frame).first()
            if(obj):

                obj.operation_status = 'Offloaded'
                db.session.flush()
                db.session.commit()

                print(frame + " Offloaded  " , file=sys.stderr)

        except:
            print('Error in Updating Seed Table' , file=sys.stderr)
        
        # try:
        #     objs = Board_Table.query.filter(Board_Table.device_id == frame).all()
        #     if(objs):
        #         for obj in objs:
        #             obj.device_id = df.loc[index,'New Hostname']
        #             db.session.flush()
        #             db.session.commit()
        #             print(frame + "    " +df.loc[index,'New Hostname'] , file=sys.stderr)

        # except:
        #     print('Error in Updateing Board Table' , file=sys.stderr)

        # try:
        #     objs = Subboard_Table.query.filter(Subboard_Table.device_id == frame).all()
        #     if(objs):
        #         for obj in objs:
        #             obj.device_id = df.loc[index,'New Hostname']
        #             db.session.flush()
        #             db.session.commit()
        #             print(frame + "    " +df.loc[index,'New Hostname'] , file=sys.stderr)

        # except:
        #     print('Error in Updateing Board Table' , file=sys.stderr)

        # try:
        #     objs = SFP_Table.query.filter(SFP_Table.device_id == frame).all()
        #     if(objs):
        #         for obj in objs:
        #             obj.device_id = df.loc[index,'New Hostname']
        #             db.session.flush()
        #             db.session.commit()
        #             print(frame + "    " +df.loc[index,'New Hostname'] , file=sys.stderr)

        # except:
        #     print('Error in Updateing Board Table' , file=sys.stderr)   

        # try:
        #     objs = License_Table.query.filter(License_Table.ne_name == frame).all()
        #     if(objs):
        #         for obj in objs:
        #             obj.ne_name = df.loc[index,'New Hostname']
        #             db.session.flush()
        #             db.session.commit()
        #             print(frame + "    " +df.loc[index,'New Hostname'] , file=sys.stderr)

        # except:
        #     print('Error in Updateing Board Table' , file=sys.stderr)   
        
    # data = db.session.execute("SET FOREIGN_KEY_CHECKS=1")

    return "Mobily Network Management System"

@app.route("/addSiteIds", methods = ['GET'])
def AddSiteIds():
    count =0 

    db.session.execute("SET FOREIGN_KEY_CHECKS=0")

    ##############################################
    objs = Rack_Table.query.filter(Rack_Table.site_id == "ALRASHID").all()
    if(objs):
        for obj in objs:
            print(obj.site_id, file=sys.stderr)
            obj.site_id = 'RSHD'
            db.session.flush()
            db.session.commit()
            print("Rack Updated RSHD" , file=sys.stderr)

    objs = Device_Table.query.filter(Device_Table.site_id == "ALRASHID").all()
    if(objs):
        for obj in objs:
            print(obj.site_id, file=sys.stderr)
            obj.site_id = 'RSHD'
            db.session.flush()
            db.session.commit()
            print("Device Updated RSHD" , file=sys.stderr)
    '''
     ##############################################
    objs = Rack_Table.query.filter(Rack_Table.site_id == "SULEMANIYA").all()
    if(objs):
        for obj in objs:
            print(obj.site_id, file=sys.stderr)
            obj.site_id = 'SULM'
            db.session.flush()
            db.session.commit()
            print("Rack Updated SULM" , file=sys.stderr)

    objs = Device_Table.query.filter(Device_Table.site_id == "SULEMANIYA").all()
    if(objs):
        for obj in objs:
            print(obj.site_id, file=sys.stderr)
            obj.site_id = 'SULM'
            db.session.flush()
            db.session.commit()
            print("Device Updated SULM" , file=sys.stderr)

    #objs = Phy_Table.query.filter(Phy_Table.site_id == "Malga").delete()
    #db.session.commit()

    ##############################################
    objs = Rack_Table.query.filter(Rack_Table.site_id == "SULAY").all()
    if(objs):
        for obj in objs:
            print(obj.site_id, file=sys.stderr)
            obj.site_id = 'SULY'
            db.session.flush()
            db.session.commit()
            print("Rack Updated SULY" , file=sys.stderr)

    objs = Device_Table.query.filter(Device_Table.site_id == "SULAY").all()
    if(objs):
        for obj in objs:
            print(obj.site_id, file=sys.stderr)
            obj.site_id = 'SULY'
            db.session.flush()
            db.session.commit()
            print("Device Updated SULY" , file=sys.stderr)

    #objs = Phy_Table.query.filter(Phy_Table.site_id == "Jeddah-1").delete()
    #db.session.commit()

    ##############################################
    objs = Rack_Table.query.filter(Rack_Table.site_id == "Sulay DC").all()
    if(objs):
        for obj in objs:
            print(obj.site_id, file=sys.stderr)
            obj.site_id = 'SULY'
            db.session.flush()
            db.session.commit()
            print("Rack Updated SULY" , file=sys.stderr)

    objs = Device_Table.query.filter(Device_Table.site_id == "Sulay DC").all()
    if(objs):
        for obj in objs:
            print(obj.site_id, file=sys.stderr)
            obj.site_id = 'SULY'
            db.session.flush()
            db.session.commit()
            print("Device Updated SULY" , file=sys.stderr)

    ##############################################
    objs = Rack_Table.query.filter(Rack_Table.site_id == "SULTANA").all()
    if(objs):
        for obj in objs:
            print(obj.site_id, file=sys.stderr)
            obj.site_id = 'SULT'
            db.session.flush()
            db.session.commit()
            print("Rack Updated SULT" , file=sys.stderr)

    objs = Device_Table.query.filter(Device_Table.site_id == "SULTANA").all()
    if(objs):
        for obj in objs:
            print(obj.site_id, file=sys.stderr)
            obj.site_id = 'SULT'
            db.session.flush()
            db.session.commit()
            print("Device Updated SULT" , file=sys.stderr)

    ##############################################
    objs = Rack_Table.query.filter(Rack_Table.site_id == "ADAMA").all()
    if(objs):
        for obj in objs:
            print(obj.site_id, file=sys.stderr)
            obj.site_id = 'ADAM'
            db.session.flush()
            db.session.commit()
            print("Rack Updated ADAM" , file=sys.stderr)

    objs = Device_Table.query.filter(Device_Table.site_id == "ADAMA").all()
    if(objs):
        for obj in objs:
            print(obj.site_id, file=sys.stderr)
            obj.site_id = 'ADAM'
            db.session.flush()
            db.session.commit()
            print("Device Updated ADAM" , file=sys.stderr)

    '''

    data = db.session.execute("SET FOREIGN_KEY_CHECKS=1")

    return "Mobily Network Management System " + str(count)

@app.route("/setDomain", methods = ['GET'])
def SetDomain():
    count =0 

    dfIGW = pd.read_excel('temp/Domain.xlsx', sheet_name = 'IGW')
    for index, frame in dfIGW['ne_ip_address'].iteritems():
        obj = Device_Table.query.filter(Device_Table.ne_ip_address == frame).first()
        if(obj):
            print(obj.ne_ip_address, file=sys.stderr)
            obj.domain = 'IGW-NET'
            db.session.flush()
            db.session.commit()

    dfEDN = pd.read_excel('temp/Domain.xlsx', sheet_name = 'EDN')
    for index, frame in dfEDN['ne_ip_address'].iteritems():
        obj = Device_Table.query.filter(Device_Table.ne_ip_address == frame).first()
        if(obj):
            print(obj.ne_ip_address, file=sys.stderr)
            obj.domain = 'EDN-NET'
            db.session.flush()
            db.session.commit()

    dfIPT = pd.read_excel('temp/Domain.xlsx', sheet_name = 'IPT')
    for index, frame in dfIPT['ne_ip_address'].iteritems():
        obj = Device_Table.query.filter(Device_Table.ne_ip_address == frame).first()
        if(obj):
            print(obj.ne_ip_address, file=sys.stderr)
            obj.domain = 'EDN-IPT'
            db.session.flush()
            db.session.commit()

    dfSys = pd.read_excel('temp/Domain.xlsx', sheet_name = 'SYS')
    for index, frame in dfSys['ne_ip_address'].iteritems():
        obj = Device_Table.query.filter(Device_Table.ne_ip_address == frame).first()
        if(obj):
            print(obj.ne_ip_address, file=sys.stderr)
            obj.domain = 'SYS'
            db.session.flush()
            db.session.commit()

    return "Success"
    #db.session.execute("SET FOREIGN_KEY_CHECKS=0")

    ##############################################
    

    #data = db.session.execute("SET FOREIGN_KEY_CHECKS=1")

@app.route("/setNotVirtual", methods = ['GET'])
def SetNotVirtual():
    objs = Device_Table.query.filter(Device_Table.virtual == 'TBF').all()
    if(objs):
        for obj in objs:
            if obj.virtual == 'TBF':
                print(obj.virtual, file=sys.stderr)
                obj.virtual = 'Not Virtual'
                db.session.flush()
                db.session.commit()
    
    return "Success"

def is_ip_in_subnet(ip_address, subnet):
    try:
        ip_network = ipaddress.ip_network(subnet)
        ip = ipaddress.ip_address(ip_address)
        return ip in ip_network
    except ValueError:
        # Invalid IP address or subnet
        return False

@app.route("/setEOS", methods = ['GET'])
def SetEOS():
    objs = Device_Table.query.all()
    for obj in objs:
        if obj.hw_eos_date.strftime('%d-%m-%Y') == '01-01-2000':
            print(obj.hw_eos_date, file=sys.stderr)
            obj.hw_eos_date = datetime(2030, 1, 1)
            db.session.flush()
            db.session.commit()

        if obj.hw_eol_date.strftime('%d-%m-%Y') == '01-01-2000':
            print(obj.hw_eol_date, file=sys.stderr)
            obj.hw_eol_date = datetime(2030, 1, 1)
            db.session.flush()
            db.session.commit()
        
        if obj.sw_eos_date.strftime('%d-%m-%Y') == '01-01-2000':
            print(obj.sw_eos_date, file=sys.stderr)
            obj.sw_eos_date = datetime(2030, 1, 1)
            db.session.flush()
            db.session.commit()
        
        if obj.sw_eol_date.strftime('%d-%m-%Y') == '01-01-2000':
            print(obj.sw_eol_date, file=sys.stderr)
            obj.sw_eol_date = datetime(2030, 1, 1)
            db.session.flush()
            db.session.commit()

    return "Success"

@app.route("/setEDNLat", methods = ['GET'])
def setEDNLAT():
    df = pd.read_excel('temp/EDN Lat Long.xlsx')

    for index, frame in df['site_id'].iteritems():
 
        if index:
            objs = Phy_Table.query.filter(Phy_Table.site_id == frame).all()
            if(objs):
                for obj in objs:
                    obj.latitude = df.loc[index,'latitude']
                    obj.longitude = df.loc[index,'longitude']
                    db.session.flush()
                    db.session.commit()
                    print(frame, file=sys.stderr)

    return "Success"

@app.route("/setDepartment", methods = ['GET'])
def SetDepartment():
    objs = Device_Table.query.filter(Device_Table.domain == 'Security operation').all()
    for obj in objs:
        #print(obj.ne_ip_address, file=sys.stderr)
        obj.department = 'Security Operations'
        obj.section = 'Security Infrastructure Management'
        db.session.flush()
        db.session.commit()

    objs = Device_Table.query.filter(Device_Table.domain == 'SYS').all()
    for obj in objs:
        print(obj.ne_ip_address, file=sys.stderr)
        obj.department = 'Technology Network Operation Center'
        obj.section = 'Cloud and virtualization systems'
        db.session.flush()
        db.session.commit()

    return "Success"

@app.route("/addNA", methods = ['GET'])
def SetNA():
    phyObj = Phy_Table()
    phyObj.site_id = 'N/A'
    phyObj.site_name = 'N/A'   
    phyObj.latitude = 'N/A'
    phyObj.longitude = 'N/A'
    phyObj.city = 'N/A'
    phyObj.status= 'N/A'
    phyObj.region = 'N/A'

    siteID = Phy_Table.query.with_entities(Phy_Table.site_id).filter_by(site_id='N/A').first()
    if siteID is not None:
        phyObj.site_id = siteID[0]
        print("Updated site " + phyObj.site_name,file=sys.stderr)
        UpdateData(phyObj)
    else:
        print("Inserted site " +phyObj.site_name,file=sys.stderr)
        InsertData(phyObj)
    '''
    rackObj = Rack_Table()
    rackObj.site_id= 'N/A'
    rackObj.rack_name= 'N/A'
    rackObj.serial_number= 'N/A'
    rackObj.unit_position= 'N/A'
    rackObj.status= 'N/A'       
    rackObj.pn_code= 'N/A'
    rackObj.tag_id= 'N/A'
    rackObj.rack_model= 'N/A'
    rackObj.floor= 'N/A'

    rackID = Rack_Table.query.with_entities(Rack_Table.rack_id).filter_by(rack_name=rackObj.rack_name).first()
    if rackID is not None:
        rackObj.rack_id = rackID[0]
        print("Updated rack " + rackObj.rack_name,file=sys.stderr)
        UpdateData(rackObj)
    else:
        print("Inserted rack " +rackObj.rack_name,file=sys.stderr)
        InsertData(rackObj)
    '''
    return "Success"

@app.route("/addSiteType", methods = ['GET'])
def AddSiteType():
    count =0 
    
    #df = pd.read_excel('temp/Systems New Hostnames.xlsx')
    df = pd.read_excel('temp/Site Type.xlsx')

    #db.session.execute("SET FOREIGN_KEY_CHECKS=0")

    for index, frame in df['ne_ip_address'].iteritems():
 
        try:
            obj = Device_Table.query.filter(Device_Table.ne_ip_address == frame).first()
            if(obj):
                obj.site_type = df.loc[index,'Site Type']
                db.session.flush()
                db.session.commit()
                print(frame + "    " +df.loc[index,'Site Type'] , file=sys.stderr)
        
        except:
            print('Error in Updateing Device Table' , file=sys.stderr)
            db.session.rollback()
            raise
        
        try:
            obj = Seed.query.filter(Seed.ne_ip_address == frame).first()
            if(obj):
                obj.site_type = df.loc[index,'Site Type']
                db.session.flush()
                db.session.commit()
                print(frame + "    " +df.loc[index,'Site Type'] , file=sys.stderr)

        except:
            print('Error in Updateing Seed Table' , file=sys.stderr)
            db.session.rollback()
            raise
        
        
    #data = db.session.execute("SET FOREIGN_KEY_CHECKS=1")

    return "Success " + str(count)

@app.route("/setTagId", methods = ['GET'])
def setTagId():
    df = pd.read_excel('temp/tag_ids.xlsx')
    
    for index, frame in df['device_id'].iteritems():
        print(f"Frame is: {frame}", file=sys.stderr)
        if pd.isnull(frame):
            continue
        else:
            obj = Device_Table.query.filter(Device_Table.device_id == frame).first()
            if(obj):
                try:
                    obj.tag_id = df.loc[index,'tag_id']
                    #obj.serial_number = df.loc[index,'S/N']
                    db.session.flush()
                    db.session.commit()
                    print(frame, file=sys.stderr)
                except Exception as e: 
                    exception+="  |  "+str(e)
                    db.session.rollback()
    #except Exception as e:
    #    exception+="  |  "+str(e)


    return "Success "

@app.route("/setSNTCDate", methods = ['GET'])
def setSNTCDate():
    df = pd.read_excel('temp/SNTC-latest.xlsx')

    for index, frame in df['pn_code'].iteritems():
        if pd.isnull(frame):
            continue
        else:
            parse_date = df.loc[index,'hw_eos_date'].to_pydatetime()

            '''
            objs = Device_Table.query.filter(Device_Table.pn_code == frame).all()
            for obj in objs:
                obj.hw_eos_date = parse_date
                db.session.flush()
                db.session.commit()
                print(frame, file=sys.stderr)

            objs = Board_Table.query.filter(Board_Table.pn_code == frame).all()
            for obj in objs:
                obj.eos_date = parse_date
                db.session.flush()
                db.session.commit()
                print(frame, file=sys.stderr)

            objs = Subboard_Table.query.filter(Subboard_Table.pn_code == frame).all()
            for obj in objs:
                obj.eos_date = parse_date
                db.session.flush()
                db.session.commit()
                print(frame, file=sys.stderr)

            objs = SFP_Table.query.filter(SFP_Table.pn_code == frame).all()
            for obj in objs:
                obj.eos_date = parse_date
                db.session.flush()
                db.session.commit()
                print(frame, file=sys.stderr)

            '''
            objs = SNTC_Table.query.filter(SNTC_Table.pn_code == frame).all()
            for obj in objs:
                obj.hw_eos_date = parse_date
                db.session.flush()
                db.session.commit()
                print(frame, file=sys.stderr)

    return "Success"

@app.route("/setPN", methods = ['GET'])
def setPN():
    objDict = {}

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    queryString = f"select PN_CODE,count(PN_CODE),DOMAIN from device_table where PN_CODE is not null group by PN_CODE,DOMAIN;"
    result = db.session.execute(queryString)
         
    for row in result:                  
        print(row[0],row[1],row[2],file=sys.stderr)         
        pnCode = (row[0])
        pnCodeCount = row[1]
        domain = row[2]
            
        if pnCode in objDict:
            objDict[pnCode][domain] = pnCodeCount
            print(objDict,file=sys.stderr)
        else:
            
            objDict[pnCode] = {}
            objDict[pnCode]["IGW-NET"]=0
            objDict[pnCode]["IGW-SYS"]=0
            objDict[pnCode]["EDN-NET"]=0
            objDict[pnCode]["EDN-SYS"]=0
            objDict[pnCode]["EDN-IPT"]=0
            objDict[pnCode]["EDN-IPT-Endpoints"]=0
            objDict[pnCode]["SOC"]=0

            objDict[pnCode][domain] = pnCodeCount

    for key in objDict:

        snap = PnCode_SNAP_Table()
        print(key)
        snap.pn_code = key
        snap.igw_net = objDict[key]["IGW-NET"]
        snap.igw_sys = objDict[key]["IGW-SYS"]
        snap.edn_net = objDict[key]["EDN-NET"]
        snap.edn_sys = objDict[key]["EDN-SYS"]
        snap.edn_ipt = objDict[key]["EDN-IPT"]
        snap.edn_ipt_endpoints = objDict[key]["EDN-IPT-Endpoints"]
        snap.soc = objDict[key]["SOC"]
        snap.creation_date = current_time

        print("Inserted PN Code " + key,file=sys.stderr)
        InsertData(snap)

    return "Success"

@app.route('/pnCodePerBoard',methods=['GET'])
def PnCodePerBoard():
    if True:#session.get('token', None):
        objDict = {}
        
        queryString = f"select PN_CODE,count(PN_CODE),DOMAIN,STACK from device_table where PN_CODE is not null group by PN_CODE,DOMAIN,STACK;"
        result = db.session.execute(queryString)

        for row in result:              
            print(row[0],row[1],row[2],file=sys.stderr)         
            pnCode = (row[0])
            pnCodeCount = row[1]
            domain = row[2]
            stack = row[3]
            if pnCode in objDict:
                objDict[pnCode][domain] = pnCodeCount
                print(objDict,file=sys.stderr)
            else:
                
                objDict[pnCode] = {}
                objDict[pnCode]["IGW-NET"]=0
                objDict[pnCode]["IGW-SYS"]=0
                objDict[pnCode]["EDN-NET"]=0
                objDict[pnCode]["EDN-SYS"]=0
                objDict[pnCode]["EDN-IPT"]=0
                objDict[pnCode]["EDN-IPT-Endpoints"]=0
                objDict[pnCode]["SOC"]=0
                objDict[pnCode][domain] = pnCodeCount

            queryString = f"select PN_CODE,count(PN_CODE) from board_table where BOARD_NAME like '%9300%' or BOARD_NAME like '%3850%' or BOARD_NAME like '%3750%' group by PN_CODE;"
            result = db.session.execute(queryString)

            for row in result:              
                print(row[0],row[1],file=sys.stderr)
                pnCode = (row[0])
                pnCodeCount = row[1] 
                if pnCode in objDict:
                    objDict[pnCode]["EDN-NET"] = objDict[pnCode]["EDN-NET"]+pnCodeCount
                else:
                    objDict[pnCode] = {}
                    objDict[pnCode]["EDN-NET"] = pnCodeCount    
                
        objList = []
        for pn_code in objDict:
            dict = objDict[pn_code]
            dict['pn_code']=pn_code
            objList.append(dict)
     
        print(objList,file=sys.stderr)   
        return jsonify(objList), 200
        

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getMasterSwitches',methods=['GET'])
def GETMasterSwitches():
    count=0
    ips=[]
    objs = Device_Table.query.filter(Device_Table.stack != "1").all()
    for obj in objs:
        while c < 3 :
            try:
                device = Netmiko(objs.ne_ip_address, username="ciscotac", password="C15c0@mob1ly", device_type='cisco_ios', timeout=600, global_delay_factor=2)
                is_login = True
                break
            except Exception as e:
                c +=1
                login_exception = str(e)
        try:
            stack=1
            print("getting stack switches")
            stacks = device.send_command("show switch detail", use_textfsm=True)    
            print(stacks)            
            for stk in stacks:
                stack+=1
            if(stack>1):    
                for stk in stacks:
                    if int(stk['priority'])> self.stack_priority:
                        stack_priority= int(stk['priority'])
                        stack_switch=stk['switch']

        except Exception as e:
            print(f"stack switches not found {e}")
                
                     #obj.domain = 'IGW-NET'
        #db.session.flush()
        #db.session.commit()
    return f"Ips found {str(ips)}"

# queryString = f"select PN_CODE,count(PN_CODE),BOARD_NAME from board_table where BOARD_NAME like '%9300%' or BOARD_NAME like '%3850%' group by PN_CODE,BOARD_NAME;"
    

@app.route("/oldDeviceIDFile", methods = ['GET'])
def OldDeviceIDFile():
    db.session.execute("SET FOREIGN_KEY_CHECKS=0")

    df = pd.read_excel('temp/consolidated_seed.xlsx')

    for index, frame in df['ne_ip_address'].iteritems():
        obj = Device_Table.query.filter(Device_Table.ne_ip_address == frame).first()

        if obj:
            print(df.loc[index,'device_id'], file=sys.stderr)
            df.loc[index,'status'] = 'Found'
            df.loc[index,'old device IDs'] = obj.device_id
        else:
            df.loc[index,'status'] = 'Not Found'

    df.to_excel('OldDeviceIDFile.xlsx')
    
    return "Success"


@app.route("/setDeviceID", methods = ['GET'])
def SetDeviceID():

    db.session.execute("SET FOREIGN_KEY_CHECKS=0")

    df = pd.read_excel('temp/consolidated_seed.xlsx')


    for index, frame in df['ne_ip_address'].iteritems():
        obj = Device_Table.query.filter(Device_Table.ne_ip_address == frame).first()

        if(obj):
            print(frame + "    "+ df.loc[index,'device_id'], file=sys.stderr)

            try:
                obj.device_id = df.loc[index,'device_id']
                obj.device_name = df.loc[index,'hostname']
                obj.virtual = df.loc[index,'virtual']
                obj.department = df.loc[index,'department']
                obj.section = df.loc[index,'section']
                obj.function = df.loc[index,'function']
                obj.site_type = df.loc[index,'site_type']

                
                if pd.notna(df.loc[index,'tag_id']):
                    if obj.tag_id == 'TBF':
                        obj.tag_id = df.loc[index,'tag_id']

                db.session.flush()
                db.session.commit()

                obj = Seed.query.filter(Seed.ne_ip_address == frame).first()
                obj.onboard_status = 'true'
                db.session.flush()
                db.session.commit()

            except:
                try:
                    db.session.rollback()
                    expobj = Device_Table.query.filter(Device_Table.device_id == df.loc[index,'device_id']).first()
                    if expobj:
                        expobj.device_id = "dummy_id"+str(randint(1,1000))
                        db.session.flush()
                        db.session.commit()

                        obj.device_id = df.loc[index,'device_id']
                        obj.device_name = df.loc[index,'hostname']
                        obj.virtual = df.loc[index,'virtual']
                        obj.department = df.loc[index,'department']
                        obj.section = df.loc[index,'section']
                        obj.function = df.loc[index,'function']
                        obj.site_type = df.loc[index,'site_type']

                        
                        if pd.notna(df.loc[index,'tag_id']):
                            if obj.tag_id == 'TBF':
                                obj.tag_id = df.loc[index,'tag_id']

                        db.session.flush()
                        db.session.commit()

                        obj = Seed.query.filter(Seed.ne_ip_address == frame).first()
                        obj.onboard_status = 'true'
                        db.session.flush()
                        db.session.commit()

                except:
                    db.session.rollback()
                    raise

    db.session.execute("SET FOREIGN_KEY_CHECKS=1")

    return "Success"

@app.route("/setotherIDtodup", methods = ['GET'])
def SetotherID():
    db.session.execute("SET FOREIGN_KEY_CHECKS=0")
    '''
    for boardObj in boardObjs:
        boardObj.device_id = boardObj.device_id+"-dup"
        db.session.flush()
        db.session.commit()
    
    df = pd.read_excel('temp/OldDeviceIDFile.xlsx')

    for index, frame in df['old device IDs'].iteritems():
        if pd.notna(frame):
            objs = Board_Table.query.filter(Board_Table.device_id == frame+"-dup").all()
            if objs:
                for obj in objs:
                    obj.device_id = df.loc[index,'device_id']
                    try:
                        print(df.loc[index,'device_id'] + "   "+ frame+"-dup", file=sys.stderr)
                        db.session.flush()
                        db.session.commit()
                    except:
                        db.session.rollback()
                        raise

    objs = Board_Table.query.filter(Board_Table.device_id.like("%-dup")).all()
    for obj in objs:
        try:
            obj.device_id = obj.device_id.split("-dup")[0]
            print(obj.device_id, file=sys.stderr)
            db.session.flush()
            db.session.commit()

        except:
            db.session.rollback()
            raise

    '''

    df = pd.read_excel('temp/OldDeviceIDFile.xlsx')

    for index, frame in df['old device IDs'].iteritems():
        if pd.notna(frame):
            objs = Board_Table.query.filter(Board_Table.device_id == frame+"-dup").first()
            if objs:
                old_id = frame+"-dup"
                db.session.execute("update sfp_table set device_id = '"+ df.loc[index,'device_id'] +"' where device_id='"+old_id+"';")
    
    db.session.execute("SET FOREIGN_KEY_CHECKS=1")

    return "Success"

@app.route("/fixtag", methods = ['GET'])
def Fixtag():
    deviceObjs = Device_Table.query.all()
    site_list = ["DCN","CO","DC","MFB","FB","KSK","FS","MOI"]
    for deviceObj in deviceObjs:
        if deviceObj.tag_id in site_list:
            print(deviceObj.ne_ip_address, file=sys.stderr)
            objSeed = Seed.query.filter(Seed.ne_ip_address == deviceObj.ne_ip_address).first()
            if objSeed:
                deviceObj.tag_id = objSeed.tag_id
            else:
                deviceObj.tag_id = ""
            
            db.session.flush()
            db.session.commit()

    return "Success"

@app.route("/fixSerial", methods = ['GET'])
def fixSerial():
    sfpObjs = SFP_Table.query.filter(SFP_Table.serial_number.ilike('00000%')).all()
    #print(len(sfpObjs), file=sys.stderr)
    for obj in sfpObjs:
        obj.serial_number = obj.serial_number.split('00000')[1]
        db.session.flush()
        db.session.commit()
        print(obj.serial_number, file=sys.stderr)
    return "Success"

@app.route("/dismantledev", methods = ['GET'])
def DismantleDev():
    df = pd.read_excel('temp/ip_report.xlsx')

    for index, frame in df['ne_ip_address'].iteritems():
        if pd.isnull(frame):
            continue
        else:
            obj = Device_Table.query.filter(Device_Table.ne_ip_address == frame).first()
            if obj:
                obj.status = 'dismantle'
                db.session.flush()
                db.session.commit()
                print(f"{obj.ne_ip_address} with {obj.status}", file=sys.stderr)
    return "Success"


@app.route("/httpTest", methods = ['GET'])
def HttpTest():
    return "Receiving on HTTP"

@app.route("/httpsTest", methods = ['GET'])
def HttpsTest():
    return "Receiving on HTTPS"

@app.route("/fixsites", methods = ['GET'])
def FixSites():
    db.session.execute("SET FOREIGN_KEY_CHECKS=0")

    seedObjs = Seed.query.all()
    for seedObj in seedObjs:
        obj = Device_Table.query.filter(Device_Table.ne_ip_address == seedObj.ne_ip_address).first()
        if obj:
            obj.site_id = seedObj.site_id
            db.session.flush()
            db.session.commit()
            print(f"{obj.ne_ip_address}", file=sys.stderr)

            rack = Rack_Table.query.filter(Rack_Table.rack_id == obj.rack_id).first()
            rack.site_id = seedObj.site_id
            db.session.flush()
            db.session.commit()
            print(f"{rack.rack_name}", file=sys.stderr)
                
    db.session.execute("SET FOREIGN_KEY_CHECKS=1")
    return "Success"

@app.route("/fixSEC", methods = ['GET'])
def FixSec():
    df = pd.read_excel('temp/NE_IPs_Puller.xlsx')

    for index, frame in df['Switch IP-Address'].iteritems():
        if pd.isnull(frame):
            continue
        else:
            obj = Device_Table.query.filter(Device_Table.ne_ip_address == frame).first()
            if obj:
                df.loc[index,'Device_id'] = obj.device_id 
                
                
    df.to_excel('NE_IPs_Puller_new.xlsx')

    df = pd.read_excel('temp/SEC_IPs_Puller.xlsx', sheet_name = 'EDN_SEC')

    for index, frame in df['FW IP-Address'].iteritems():
        if pd.isnull(frame):
            continue
        else:
            obj = Device_Table.query.filter(Device_Table.ne_ip_address == frame).first()
            if obj:
                df.loc[index,'Device_id'] = obj.device_id 
                    
    df.to_excel('SEC_IPs_Puller_new.xlsx')

    return "Receiving on HTTPS"

@app.route("/testmail", methods = ['GET'])
def TestMail():
    responseMessage = 'success'
    failedList = ['abc_xyz']
    smtpAddress = '84.23.106.12'
    sender = 'IGW/MGN Network Devices - Daily Backup Notification <reporter-sw@mobily.com.sa>'
    receivers = ['m.ajmal@mobily.com.sa']

    if len(failedList) == 0:
        msg = MIMEText("""
        Hello,

        """+responseMessage+""" 

        Best regards,""")

    else:
        msg = MIMEText("""
        Hello,

        """+responseMessage+""" 

        Failed Devices:
        """+str(failedList)+"""

        Best regards,""")

 

    try:
        print("connecting")
        smtpObj = smtplib.SMTP('84.23.106.12', 25)
        print("connected")
        print("sending mail")
        msg['Subject'] = 'IGW/MGN Network Devices - Daily Backup Notification'
        msg['From'] = 'IGW/MGN Network Devices - Daily Backup Notification <reporter-sw@mobily.com.sa>'
        msg['To'] = 'CISCO-MNS-IM@mobily.com.sa'
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open("WorkBook3.xlsx", "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="WorkBook3.xlsx"')
        msg.attach(part)
        smtpObj.sendmail(sender, receivers, msg.as_string())
        print("Successfully sent email")
    except SMTPException:
        print("Error: unable to send email")

    msg = MIMEText("""Hello,"""+responseMessage+"""Failed Devices:"""+str(failedList)+"""Best regards,""")
    return "Success"

@app.route("/testStack", methods = ['GET'])
def TestStack():
    queryString = f"select device_id, stack from device_table where stack > 1;"
    result = db.session.execute(queryString)     
    for row in result:                  
        id = row[0]
        stack = row[1]
        obj = Board_Table.query.filter(Board_Table.device_id == id).all()
        query2String = f"select device_id, stack from device_table where stack > 1;"
        print(f"id stack value is {stack} and obj count is {len(obj)}")


    return "Receiving on HTTPS"

@app.route("/testmail3", methods = ['GET'])
def TestMail3():
  try:
        responseMessage = 'success'
        smtpAddress = '84.23.106.12'
        sender = 'IGW/MGN Network Devices - Daily Backup Notification <reporter-sw@mobily.com.sa>'
        receivers = ['m.ajmal@mobily.com.sa']
        msg = EmailMessage()
 
        msg.set_content("Hello World")
        
        print("connecting")
        smtpObj = smtplib.SMTP('84.23.106.12', 25)
        print("connected")
        print("sending mail")
        msg['Subject'] = 'IGW/MGN Network Devices - Daily Backup Notification'
        msg['From'] = 'IGW/MGN Network Devices - Daily Backup Notification <reporter-sw@mobily.com.sa>'
        recipients = ['m.ajmal@mobily.com.sa', 'sohaib.ajmal@nets-international.com']
        msg['To'] = ", ".join(recipients)
        
        with open('temp/SEC_IPs_Puller.xlsx', "rb") as f:
          file_data= f.read()
          file_name= f.name
          msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename="test")
           
        smtpObj.sendmail(sender, receivers, msg.as_string())
        print("Successfully sent email", file=sys.stderr)
        return "Success"
  except SMTPException:
    print("Error: unable to send email", file=sys.stderr)
    print("Error")

@app.route("/getIP", methods = ['GET'])
def GETIP():
    ## getting the hostname by socket.gethostname() method
    hostname = socket.gethostname()
    ## getting the IP address using socket.gethostbyname() method
    ip_address = socket.gethostbyname(hostname)
    ## printing the hostname and ip_address
    print(f"Hostname: {hostname}")
    print(f"IP Address: {ip_address}")
    #return NODENAME: '{{.Node.Hostname}}'

@app.route("/sendPhysicalMappingReports", methods = ['GET'])
def SendPhysicalMappingReportsss():
    print("Sending Physical  Report in Email", file=sys.stderr)

    print("Generating Reports", file=sys.stderr)
    ednFileName= "app/physical_mapping_reports/CISCO-EDN-"+datetime.now().strftime("%d-%m-%Y")
    igwFileName= "app/physical_mapping_reports/CISCO-IGWMGN-"+datetime.now().strftime("%d-%m-%Y")
    if not os.path.exists('app/physical_mapping_reports'):
        os.makedirs('app/physical_mapping_reports')
    try:
        print("Generating EDN Mapping", file=sys.stderr)
        ednMapping= GetAllEdnMappingsFunc("")
        GeneratePhysicalMappingCsvReport(ednMapping, ednFileName, "EDN Mapping")

        print("Generating IGW Mapping", file=sys.stderr)
        igwMapping= getAllIgwMappingsFunc("")
        GeneratePhysicalMappingCsvReport(igwMapping, igwFileName, "IGW Mapping")
    except Exception as e:
        print(f"Exception Occured in Generating Reports {e}", file=sys.stderr)
    
    try:
        sendEmail(ednFileName, igwFileName)
    except Exception as e:
        print(f"Exception Occured in Sending Mail Reports {e}", file=sys.stderr)
    
    try:
        UploadToSFTP(ednFileName, igwFileName)
    except Exception as e:
        print("Exception Occured in Uploading file to SFTP", file=sys.stderr)
    return "Success"
def GeneratePhysicalMappingCsvReport(data, file_name, mapping_type): 
    #iterate over data and save to excel
    dfObj = pd.DataFrame(columns=['Device A Name', 'Device A Interface', 'Device A Trunk Name',	'Device A IP',	'Device B System Name',	'Device B Interface',	'Device B IP',	'Device B Type', 'Device B Port Description', 'Device A MAC', 'Device B MAC', 'Device A Port Description', 'Vlan', 'Service Name', 'Owner Name', 'Owner Email', 'Owner Contact', 'Creation Date','Modification Date'])
    obj_in=0
   
    try:
        for pm_data in data:
            dfObj.loc[obj_in,'Device A Name'] = pm_data.get('device_a_name', "")
            dfObj.loc[obj_in,'Device A Interface'] = pm_data.get('device_a_interface', "")
            dfObj.loc[obj_in,'Device A Trunk Name'] = pm_data.get('device_a_trunk_name', "")
            dfObj.loc[obj_in,'Device A IP'] = pm_data.get('device_a_ip', "") 
            dfObj.loc[obj_in,'Device B System Name'] = pm_data.get('device_b_system_name', "")
            dfObj.loc[obj_in,'Device B Interface'] = pm_data.get('device_b_interface', "")
            dfObj.loc[obj_in,'Device B IP'] = pm_data.get('device_b_ip', "")
            dfObj.loc[obj_in,'Device B Type'] = pm_data.get('device_b_type', "")
            dfObj.loc[obj_in,'Device B Port Description'] = pm_data.get('device_b_port_desc', "")
            dfObj.loc[obj_in,'Device A MAC'] = pm_data.get('device_a_mac', "")
            dfObj.loc[obj_in,'Device B MAC'] = pm_data.get('device_b_mac', "")
            dfObj.loc[obj_in,'Device A Port Description'] = pm_data.get('device_a_port_desc', "")
            dfObj.loc[obj_in,'Vlan'] = pm_data.get('device_a_vlan', "")
            dfObj.loc[obj_in,'Service Name'] = pm_data.get('service_name', "")
            dfObj.loc[obj_in,'Owner Name'] = pm_data.get('owner_name', "")
            dfObj.loc[obj_in,'Owner Email'] = pm_data.get('owner_email', "")
            dfObj.loc[obj_in,'Owner Contact'] = pm_data.get('owner_contact', "")
            dfObj.loc[obj_in,'Creation Date'] = pm_data.get('creation_date', "")
            dfObj.loc[obj_in,'Modification Date'] = pm_data.get('modification_date', "")
            obj_in+=1
    except Exception as e:
        print("error writing df")
        print(e, file=sys.stderr)

    try:
        writer = pd.ExcelWriter(file_name+".xlsx")
        #write dataframe to excel
        dfObj.to_excel(writer, sheet_name=mapping_type, index=False)
        writer.save()
        
        #Write CSV
        dfObj.to_csv(file_name+".csv",index=False)
        print('DataFrame is written successfully to CSV File.', file=sys.stderr)
    except Exception as e:
        print(f'Error While writind data to CSV file {e}', file=sys.stderr)

def sendEmail(ednFileName, igwFileName): 
    try:
        sender = 'IGW/EDN Physical Mapping Report <reporter-sw@mobily.com.sa>'
        receivers = ['a.harras@mobily.com.sa', 'ralanqar@cisco.com', 'l.odetallah@mobily.com.sa', 'anraees@cisco.com', 'm.elhalawany@mobily.com.sa']

        msg = EmailMessage()
 
        msg.set_content('''
        Dear Team,

        Please Find Weekly IGW and EDN Physical Mapping Report.

        Regards,

        ''')
        
        print("connecting")
        with open('app/cred.json') as inventory:
            inv = json.loads(inventory.read())
            smtpServer=  inv['SMTP']['ip']
            smtpServerPort=  inv['SMTP']['port']
           
        smtpObj = smtplib.SMTP(smtpServer, smtpServerPort)
        print("connected")
        print("sending mail")
        msg['Subject'] = 'IGW/EDN Physical Mapping Report <reporter-sw@mobily.com.sa>'
        msg['From'] = 'IGW/EDN Physical Mapping Report <reporter-sw@mobily.com.sa>'
        msg['To'] = ", ".join(receivers)
        
        try:
            with open(ednFileName+".xlsx", "rb") as f:
                file_data= f.read()
                file_name= f.name
                msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=file_name)
        
        except Exception as e:
           print(f"EDN Mapping Not Found {e}", file=sys.stderr)

        try:
            with open(igwFileName+".xlsx", "rb") as f:
                file_data= f.read()
                file_name= f.name
                msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=file_name)
        
        except Exception as e:
           print(f"IGW Mapping Not Found {e}", file=sys.stderr)  

        smtpObj.sendmail(sender, receivers, msg.as_string())
        print("Successfully Sent email", file=sys.stderr)
        return "Success"
    except SMTPException:
        print(f"Error: unable to send email {e}", file=sys.stderr)
    
def UploadToSFTP(ednFileName, igwFileName):
    sftpServer = ""
    with open('app/cred.json') as inventory:
        inv = json.loads(inventory.read())
        sftpServer=  inv['SFTP']['ip']
        userName= inv['SFTP']['user']
        Password= inv['SFTP']['pwd']
        path= inv['SFTP']['path']
    try:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None  

        srv =  pysftp.Connection(host=sftpServer, username=userName, password=Password, cnopts=cnopts)
        print("Connection successfully established ... ", file=sys.stderr)

        with srv.cd(path): 
            srv.put(ednFileName+".csv") 
            srv.put(igwFileName+".csv")

        srv.close()
        print("Successfully uploaded files to SFTP server", file=sys.stderr)
    except SMTPException as e:
        print(f"Failed to upload files to SFTP server {e}", file=sys.stderr)


@app.route("/updateRackIdsInSeed", methods = ['GET'])
def updateRackIdsInSeed():
    #queryString = f"select * from board_table where device_id LIKE 'SULM%' and STATUS != 'dismantle' and board_name not LIKE 'Transceiver%';"
    #result = db.session.execute(queryString) 
    count=0    
    #for row in result:                  
    #    count+=1
    objs = Seed.query.all()
    for obj in objs:
        deviceObjs= Device_Table.query.filter(Device_Table.device_id== obj.device_id).all()
        #deviceObjs= Device_Table.query.filter(Device_Table.ne_ip_address== obj.ne_ip_address).all()
        for device in deviceObjs:
            obj.rack_id= device.rack_id
            try:
                db.session.merge(obj)
                db.session.commit()
                count+=1
                print("Rack Id Updated", file=sys.stderr)
                #print(obj.site_name, file=sys.stderr)
            except:
                db.session.rollback()
                print("Something else went wrong", file=sys.stderr)
    return str(count)


@app.route("/updateIptSerialNumber", methods = ['GET'])
def UpdateIptSerialNumber():
    count=0
    count2=0
    df = pd.read_csv('temp/ipt.csv')

    for index, frame in df.iterrows():
        hostname= str(frame['Hostname'])
        serial_number= str(frame['Serial Number'])
        if ("sep" in  hostname.lower() or "csf" in hostname.lower()) and 'nan' not in serial_number  :
            count+=1
            print(f" {hostname} :  {serial_number}", file=sys.stderr)

        ipt = IPT_Endpoints_Table.query.filter(IPT_Endpoints_Table.hostname== hostname).first()
        if ipt:
            #for ipt in ipts:
            try:
                ipt.serial_number= serial_number
                db.session.flush()
                db.session.merge(ipt)
                db.session.commit()
                count2=count2+1 
                print("Updatedddd Serial Number", file=sys.stderr)
            except Exception as e:
                db.session.rollback()
                print("Failed to Update Serial Number", file=sys.stderr)

    '''
    telephones = Device_Table.query.filter(Device_Table.domain == "EDN-IPT-Endpoints").all()
    if telephones:
        for telephone in telephones:
            count=count+1 

            
            if ipts:
                for ipt in ipts:
                    try:
                        ipt.serial_number= telephone.device_id
                        #db.session.flush()
                        db.session.merge(ipt)
                        db.session.commit()
                        count2=count2+1 
                        print("Updatedddd Serial Number", file=sys.stderr)
                    except Exception as e:
                        db.session.rollback()
                        print("Failed to Update Serial Number", file=sys.stderr)
    '''
    return str(f"{count}     {count2} ") 


@app.route("/addDeviceTagIdsToSeeds", methods = ['GET'])
def AddDeviceTagIdsToSeeds():
    count=0
    count2=0
    devices = Device_Table.query.all()
    if devices:
        for device in devices:
            count=count+1 

            seeds = Seed.query.filter(Seed.device_id== device.device_id).all()
            if seeds:
                for seed in seeds:
                    try:
                        pass
                        seed.tag_id= device.tag_id
                        db.session.flush()
                        db.session.merge(seed)
                        db.session.commit()
                        count2=count2+1 
                        print("Updatedddd TAG ID", file=sys.stderr)
                    except Exception as e:
                        db.session.rollback()
                        print("Failed to Update Ta ID", file=sys.stderr)

    return str(count2) 

@app.route("/updateAPs", methods = ['GET'])
def UpdateAPs():
    db.session.execute("SET FOREIGN_KEY_CHECKS=0")

    df = pd.read_excel('temp/APs.xlsx', sheet_name = 'Sheet1')

    for index, frame in df['Device Name'].iteritems():
    
        obj = Device_Table.query.filter(Device_Table.device_id== frame).first()
        if obj:
            obj.device_id = df.loc[index,'Device ID']
            UpdateData(obj)
            print(f"{index} {obj.device_id} {obj.ne_ip_address} {obj.device_name}", file=sys.stderr)
    
        obj = Seed.query.filter(Seed.device_id== frame).first()
        if obj:
            obj.device_id = df.loc[index,'Device ID']
            UpdateData(obj)
            print(f"{index} {obj.device_id} {obj.ne_ip_address} {obj.hostname}", file=sys.stderr)
    
    db.session.execute("SET FOREIGN_KEY_CHECKS=1")
    return "Successfull"


@app.route("/addDeviceRfsDatesToSeeds", methods = ['GET'])
def AddDeviceRfsDatesToSeeds():
    count=0
    count2=0
    devices = Device_Table.query.all()
    if devices:
        for device in devices:
            count=count+1 

            seeds = Seed.query.filter(Seed.device_id== device.device_id).all()
            if seeds:
                for seed in seeds:
                    try:
                        seed.rfs_date= device.rfs_date
                        db.session.flush()
                        db.session.merge(seed)
                        db.session.commit()
                        count2=count2+1 
                        print("Updatedddd RFS Date", file=sys.stderr)
                    except Exception as e:
                        db.session.rollback()
                        print("Failed to Update RFS Date", file=sys.stderr)

    return str(count2) 


@app.route("/populatePowerFeed", methods = ['GET'])
def PopulatePowerFeed():
    print("Populating Power feeds from device table")
    devices = Device_Table.query.filter(Device_Table.status== "Production").all()
    if devices:
        for device in devices:
            
            try:
                if device.function != "Access Point":
                    powerObj= POWER_FEEDS_TABLE()
                    powerObj.device_id= device.device_id 
                    powerObj.rack_id= device.rack_id 
                    powerObj.site_id= device.site_id 
                    #device.rfs_date= device.rfs_date
                    #db.session.flush()
                    #db.session.merge(seed)
                    #db.session.commit()
                    #count2=count2+1 
                    InsertData(powerObj)
                    print(f"Added Device ID {powerObj.device_id}", file=sys.stderr)
                else:
                    print("Access Point", file=sys.stderr)
            except Exception as e:
                db.session.rollback()
                print(f"Failed to add  Device ID {powerObj.device_id}", file=sys.stderr)

    return str("Success")



@app.route("/checkFirewallDevices", methods = ['GET'])
def CheckFirewallDevices():
    fwObjs = EDN_SEC_Seed.query.all()
    time= datetime.now()
    dfObj = pd.DataFrame(columns=['FW IP', 'FW Host Name', 'OS Type', 'Status', 'Domain'])
    obj_in=0
    countLogin=0
    countFailed=0
    i=0
    for fwObj in fwObjs: 
        i+=1
        ip = fwObj.fw_ip_address
        hostname = fwObj.fw_id
        sw_type = fwObj.os_type
        status=""
        
        try:
        
            with open('app/cred.json') as inventory:
                inv = json.loads(inventory.read())
        
            if sw_type == 'IOS':
                device_type = 'cisco_ios'
                username= inv['EDN']['user']
                password= inv['EDN']['pwd']
                
            elif sw_type == 'NX-OS':
                device_type = 'cisco_nxos'
                username= inv['EDN']['user']
                password= inv['EDN']['pwd']
                
            elif sw_type == 'FOS':
                device_type = 'fortinet'
                username= inv['SEC']['user']
                password= inv['SEC']['pwd']
                
            elif sw_type == 'Junos':
                device_type = 'juniper_junos'
                username= inv['SEC']['user']
                password= inv['SEC']['pwd']
                
            elif sw_type == 'ASA':
                device_type = 'cisco_asa'
                username= inv['SEC']['user']
                password= inv['SEC']['pwd']

            login_tries = 2
            c = 0
            is_login = False
            
            
            while c < login_tries :
                try:
                                
                    device = Netmiko(host=ip, username=username, password=password, device_type=device_type, timeout=800, global_delay_factor=2)
                    print(f"Success: logged in to host {i} {ip} ", file=sys.stderr)
                    
                    status = "Success"
                    countLogin+=1
                    is_login=True
                    break
                except Exception as e:
                    c +=1
            
            if is_login==False:
                status = "Failed"
                countFailed+=1
                print(f"Faied to login {i} {ip}", file=sys.stderr)

            dfObj.loc[obj_in,'FW IP'] = ip
            dfObj.loc[obj_in,'FW Host Name'] = hostname
            dfObj.loc[obj_in,'OS Type'] = sw_type
            dfObj.loc[obj_in,'Status'] = status
            print(f"Status is {status}", file=sys.stderr)
            obj_in+=1
        except Exception as e:
            print(f"Error in SW Type {e}", file=sys.stderr)   

    try:
        writer = pd.ExcelWriter(f"Firewalls-Status-{time}.xlsx")
        #write dataframe to excel
        dfObj.to_excel(writer, sheet_name="Firewalls ", index=False)
        writer.save()
        
    except Exception as e:
        print(f'Error While writing data to Excel File {e}', file=sys.stderr)

    print("Finished Completing Firewall Test", file=sys.stderr)   
    return f"Passed: {countLogin},   Failed: {countFailed}" 
 




@app.route("/syncDeviceIdsOfAps", methods = ['GET'])
def SyncDeviceIdsOfAps():
    print("Populating Device Id")

    aps = Access_Points_Table.query.all()
    if aps:
        for ap in aps:
            
            try:
                device = Device_Table.query.filter(Device_Table.device_name== ap.device_name).first()
                if device:
                        #print(device, file=sys.stderr)
                        ap.device_id= device.device_id
                        InsertData(ap)
                        #print(f"Updated Device ID ", file=sys.stderr)
                else:
                    ap.device_id= ap.device_name
                    print(f"Updated Device ID for Hostname {ap.device_name}", file=sys.stderr)

            except Exception as e:
                db.session.rollback()
                print(f"Failed to add  Device ID {ap.device_name} {e} ", file=sys.stderr)

    return str("Success")


@app.route("/sendCustomPhysicalMappingReports", methods = ['GET'])
def SendCustomPhysicalMappingReports():
    print("Send Physical Mapping Reports")
    SendPhysicalMappingReports()
    return "Sucess"

@app.route("/testBurdApic", methods = ['GET'])
def TestBurdApic():

    ednLLDPACIDict = {}

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query_string = "select ne_ip_address, device_id, sw_type, site_id from seed_table where cisco_domain = 'EDN-NET' and sw_type = 'APIC';" 
    result = db.session.execute(query_string)
    for row in result:
        #print(row[0], row[1], row[2], file=sys.stderr)
        site_apic= row[1].split('-')
        site_apic= '-'.join(site_apic[:-1])
        if site_apic in ednLLDPACIDict:
            ednLLDPACIDictEntry = {}
            ednLLDPACIDictEntry['ip'] = row[0]
            ednLLDPACIDictEntry['hostname'] = row[1]
            ednLLDPACIDictEntry['sw_type'] = row[2]
            ednLLDPACIDictEntry['time'] = current_time
            ednLLDPACIDictEntry['type'] = 'EDN'

            ednLLDPACIDict[site_apic].append(ednLLDPACIDictEntry)
        else:
            site_apic= row[1].split('-')
            site_apic= '-'.join(site_apic[:-1])
            ednLLDPACIDict[site_apic] = []

            ednLLDPACIDictEntry = {}
            ednLLDPACIDictEntry['ip'] = row[0]
            ednLLDPACIDictEntry['hostname'] = row[1]
            ednLLDPACIDictEntry['sw_type'] = row[2]
            ednLLDPACIDictEntry['time'] = current_time
            ednLLDPACIDictEntry['type'] = 'EDN'
        

            ednLLDPACIDict[site_apic].append(ednLLDPACIDictEntry)
    
    return str(ednLLDPACIDict)


@app.route("/changeDeviceIds", methods = ['GET'])
def ChangeDeviceID():

    db.session.execute("SET FOREIGN_KEY_CHECKS=0")

    df = pd.read_excel('temp/device.xlsx')


    for index, frame in df['Current device id'].iteritems():
        obj = Device_Table.query.filter(Device_Table.device_id == frame).first()

        if(obj):
            print(frame + "    "+ df.loc[index,'new device id'], file=sys.stderr)

            try:
                obj.device_id = df.loc[index,'new device id']
                db.session.flush()
                db.session.commit()
                print("updated in device", file=sys.stderr)

                obj = Seed.query.filter(Seed.device_id == frame).first()
                obj.device_id = df.loc[index,'new device id']
                db.session.flush()
                db.session.commit()
                print("updated in seed", file=sys.stderr)

                objs = Board_Table.query.filter(Board_Table.device_id == frame).all()
                for obj in objs:
                    board_ids =0 
                    try:
                        obj.device_id = df.loc[index,'new device id']
                        db.session.flush()
                        db.session.commit()
                        board_ids+=1
                    except Exception as e:
                        db.session.rollback()
                        print("Failed to assign Id", fie=sys.stderr)

                    print("updated boards " + str(board_ids), file=sys.stderr)

                objs = Subboard_Table.query.filter(Subboard_Table.device_id == frame).all()
                for obj in objs:
                    subboard_ids =0 
                    try:
                        obj.device_id = df.loc[index,'new device id']
                        db.session.flush()
                        db.session.commit()
                        subboard_ids+=1
                    except Exception as e:
                        db.session.rollback()
                        print("Failed to assign Id", fie=sys.stderr)

                    print("updated subboards " + str(subboard_ids), file=sys.stderr)

                objs = SFP_Table.query.filter(SFP_Table.device_id == frame).all()
                for obj in objs:
                    sfp_id =0 
                    try:
                        obj.device_id = df.loc[index,'new device id']
                        db.session.flush()
                        db.session.commit()
                        sfp_id+=1
                    except Exception as e:
                        db.session.rollback()
                        print("Failed to assign Id", fie=sys.stderr)

                    print("updated subboards " + str(sfp_id), file=sys.stderr)

            except:
                db.session.rollback()
                raise

    db.session.execute("SET FOREIGN_KEY_CHECKS=1")

    return "Success"

@app.route("/updateVuln", methods = ['GET'])
def UpdateVuln():
    
    df = pd.read_excel('temp/vuln_devices_dump.xlsx', sheet_name = 'Sheet1')


    for index, frame in df['device_id'].iteritems():
 
        try:
            obj = Device_Table.query.filter(Device_Table.device_id == frame).first()
            if(obj):

                obj.vuln_fix_plan_status = df.loc[index,'vuln_fix_plan_status']

                db.session.flush()
                db.session.commit()
                
                print(frame + " Updated" , file=sys.stderr)
            else:
                print(f"Not Found {frame}", file=sys.stderr)
        except:
            print('Error in Updating Device Table' , file=sys.stderr)
            db.session.rollback()
            raise
        
        try:
            obj = Seed.query.filter(Seed.device_id == frame).first()
            if(obj):

                obj.vuln_fix_plan_status = df.loc[index,'vuln_fix_plan_status']
                db.session.flush()
                db.session.commit()

                print(frame + " Updated  " , file=sys.stderr)

        except:
            print('Error in Updating Seed Table' , file=sys.stderr)


    return "Successfull"



@app.route("/updateOuiFile", methods = ['GET'])
def UpdateOuiFile():
    # Path of local OUI file
    local_oui_file = "temp/oui.txt"

    # Path to the current OUI file in the netaddr library
    #netaddr_oui_file = "path/to/your/netaddr/library/oui.txt"
    netaddr_oui_file = os.path.dirname(netaddr.__file__) + "/oui.txt"


    # check if the OUI file already exists in the netaddr library
    if os.path.exists(netaddr_oui_file):
        # make a backup copy of the current OUI file
        shutil.copy2(netaddr_oui_file, netaddr_oui_file + ".bak")
        print("Backup of the current OUI file created.", file=sys.stderr)

    # copy the local OUI file to the netaddr library
    shutil.copy2(local_oui_file, netaddr_oui_file)

    # regenerate the index file
    #oui.init()
        #script_path = "path/to/your/netaddr/library/oui-gen-idx.py"

    # path to the current OUI file in the netaddr library
    oui_file = "path/to/your/netaddr/library/oui.txt"

    # run the script and generate the index file
    #subprocess.run([script_path, oui_file])
        #
        #
    #
    print("OUI file and index file successfully updated.", file=sys.stderr)

def UpdateData(obj):
    #add data to db
    #print(obj, file=sys.stderr)
    try:
        # db.session.flush()

        db.session.merge(obj)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong during Database Update {e}", file=sys.stderr)
    
    return True

@app.route("/updateItemDesc", methods = ['GET'])
def UpdateItemDesc():
    boardObjs = Board_Table.query.all()
    
    for board in boardObjs:
        try:
            if board.item_desc =="None":
                board.item_desc= board.board_name

                sntcDevice = SNTC_Table.query.filter_by(pn_code=board.pn_code).first()
                if sntcDevice.item_desc is None:
                    sntcDevice.item_desc= board.board_name
                    UpdateData(sntcDevice)
                UpdateData(board)
                print("Updated Board", file=sys.stderr)
        except Exception as e:
            print("Exception Occures", file=sys.stderr)


    subBoardObjs = Subboard_Table.query.all()
    
    for subBoard in subBoardObjs:
        if subBoard.item_desc== "None":
            try:
                subBoard.item_desc= subBoard.subboard_type

                sntcDevice = SNTC_Table.query.filter_by(pn_code=board.pn_code).first()
                if sntcDevice.item_desc is None:
                    sntcDevice.item_desc= subBoard.subboard_type
                    UpdateData(sntcDevice)
                UpdateData(subBoard)
                print("Updated Sub Board", file=sys.stderr)
            except Exception as e:
                print("Exception Occures", file=sys.stderr)
    
    return ""
        

def connectACI(self, host):
        requests.packages.urllib3.disable_warnings()
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        try:
            requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        except AttributeError:
            # no pyopenssl support used / needed / available
            pass
                
        print(f"Connecting to {host['host']}")
        login_tries = 10
        c = 0
        port =443
        is_login = False
        self.base_url = f"https://{host['host']}:{port}"
        while c < login_tries :
            try:
                url = self.base_url+"/api/aaaLogin.json"
                payload = {
                    "aaaUser": {
                        "attributes": {
                            "name": host['user'],
                            "pwd": host['pwd']
                        }
                    }
                }
                headers = {'cache-control': "no-cache"}
                response = requests.post(url, data=json.dumps(payload), headers={'Content-Type': "application/json"}, verify=False).json()
                token = response['imdata'][0]['aaaLogin']['attributes']['token']                
                self.cookie['APIC-cookie'] = token
                print(f"Success: logged in {host['host']}")
                is_login = True
                break
            except Exception as e:
                print(e)
                c +=1
    
        return is_login
    

@app.route("/changeF5Devices", methods = ['GET'])
def ChangeF5Devices():
    ccount=0
    db.session.execute("SET FOREIGN_KEY_CHECKS=0")

    df = pd.read_excel('temp/f5dev.xlsx')

    for index, frame in df['ne_ip_address'].iteritems():
        obj = Device_Table.query.filter(Device_Table.ne_ip_address == frame).first()
        if not obj:
            print(f"!!!!!! Frame Not Updated {frame}", file=sys.stderr)
        
        if(obj):
            ccount+=1
            old_id= obj.device_id

           
                
            print(frame + "    "+ df.loc[index,'device_id'], file=sys.stderr)

            try:
                obj.device_id = df.loc[index,'device_id']
                obj.function = df.loc[index,'function']
                obj.serial_number = df.loc[index,'serial_number']
                obj.pn_code = df.loc[index,'pn_code']
                db.session.flush()
                db.session.commit()
                print(f"updated in device {index}   {ccount}", file=sys.stderr)

                obj = Seed.query.filter(Seed.ne_ip_address == frame).first()
                if obj:
                    obj.device_id = df.loc[index,'device_id']
                    obj.function = df.loc[index,'function']
                    db.session.flush()
                    db.session.commit()
                    print("updated in seed", file=sys.stderr)

                objs = Board_Table.query.filter(Board_Table.device_id == old_id).all()
                for obj in objs:
                    board_ids =0 
                    try:
                        obj.device_id = df.loc[index,'device_id']
                        db.session.flush()
                        db.session.commit()
                        board_ids+=1
                    except Exception as e:
                        db.session.rollback()
                        print("Failed to assign Id", fie=sys.stderr)
                    print("updated boards " + str(board_ids), file=sys.stderr)

                objs = Subboard_Table.query.filter(Subboard_Table.device_id == old_id).all()
                for obj in objs:
                    subboard_ids =0 
                    try:
                        obj.device_id = df.loc[index,'device_id']
                        db.session.flush()
                        db.session.commit()
                        subboard_ids+=1
                    except Exception as e:
                        db.session.rollback()
                        print("Failed to assign Id", fie=sys.stderr)
                    print("updated subboards " + str(subboard_ids), file=sys.stderr)

                objs = SFP_Table.query.filter(SFP_Table.device_id == old_id).all()
                for obj in objs:
                    sfp_id =0 
                    try:
                        obj.device_id = df.loc[index,'device_id']
                        db.session.flush()
                        db.session.commit()
                        sfp_id+=1
                    except Exception as e:
                        db.session.rollback()
                        print("Failed to assign Id", fie=sys.stderr)

                    print("updated SFP " + str(sfp_id), file=sys.stderr)

                objs =  POWER_FEEDS_TABLE.query.filter(POWER_FEEDS_TABLE.device_id == old_id).all()
                for obj in objs:
                    power_id =0 
                    try:
                        obj.device_id = df.loc[index,'device_id']
                        db.session.flush()
                        db.session.commit()
                        power_id+=1
                    except Exception as e:
                        db.session.rollback()
                        print("Failed to assign Id", fie=sys.stderr)

                    print("updated Power " + str(power_id), file=sys.stderr)

            except:
                db.session.rollback()
                raise

    db.session.execute("SET FOREIGN_KEY_CHECKS=1")

    return f"Success  {ccount}"

@app.route("/getDccmDevicesUpTime", methods = ['GET'])
def GetDccmDevicesUpTime():
    dfObj = pd.DataFrame(columns=['Device Id', 'IP Address', 'Cisco Domain' ,'SW Type', 'Up Time', 'Failure Reason'])
    obj_in=0
    query_string = "select site_id, device_id,ne_ip_address, sw_type,cisco_domain from seed_table where (cisco_domain = 'EDN-NET' or cisco_domain = 'IGW-NET') and (sw_type='IOS' or sw_type='IOS-XE' or sw_type='IOS-XR' or sw_type='NX-OS') and `function` LIKE '%SWITCH%' and site_type='DC' and operation_status='Production';" 
    result = db.session.execute(query_string)
    ednDcCapacityList=[]
    with open('app/cred.json') as inventory:
            inv = json.loads(inventory.read())
    for row in result:
        ednDcCapacityDict = {}
        ednDcCapacityDict['site_id'] = row[0]
        ednDcCapacityDict['device_id'] = row[1]
        ednDcCapacityDict['device_ip'] = row[2]
        ednDcCapacityDict['sw_type'] = row[3]
        ednDcCapacityDict['sw'] = row[3]

        if  row[4]=='EDN-NET':
            ednDcCapacityDict['type'] = 'EDN'
        if  row[4]=='IGW-NET':
            ednDcCapacityDict['type'] = 'IGW'
        ednDcCapacityList.append(ednDcCapacityDict)
    devNo= 1
    for device in  ednDcCapacityList:

        failure=""
        uptime=""

        if device['type'] == 'IGW':
            user_name = inv['IGW']['user']
            password = inv['IGW']['pwd']

        if device['type'] == 'EDN':
            user_name = inv['EDN']['user']
            password = inv['EDN']['pwd']

        os_version= (device['sw_type'])
        sw_type = str(device['sw_type']).lower()
        sw_type = sw_type.strip()
        #print(sw_type,file=sys.stderr)
        
        if sw_type=='ios':
            sw_type = 'cisco_ios'
        elif sw_type=='ios-xe':
            sw_type = 'cisco_ios'
        #elif sw_type == 'ios-xr':
        #    sw_type = 'cisco_xr'
        elif sw_type == 'nx-os':
            sw_type = 'cisco_nxos'
        #elif sw_type=='aci-leaf':
        #    sw_type = 'cisco_nxos-leaf'
        else:
            sw_type=''
        

        c=0
        is_login=False
        print(f"Connecting to device No {devNo}/{len(ednDcCapacityList)}, IP {device['device_ip']}:", file=sys.stderr)
        devNo+=1
        while c < 3 :         
            try:
                            
                dev = Netmiko(host=device['device_ip'], username=user_name, password=password, device_type=sw_type, timeout=800, global_delay_factor=2)
                print(f"Success: logged in")
                
                is_login = True
                break
            except Exception as e:
                print(e)
                c +=1

        if is_login==False:
            #failedDB
            failure="Login Failed"
            print(f"Failed to login ")
            

        if is_login==True:
            print(f"Successfully logged into host")

            try:
                output= dev.send_command("show version",  use_textfsm=True)
                #output2= device.send_command("show interface Ethernet10/10")
                if("Invalid command" in str(output)):
                    failure= "Failed to send command, show version"+str(output)
                    raise Exception("Failed to send Command, show version"+str(output))
                if len(output)>0:
                    uptime= output[0].get('uptime')
                    #print(output[0].get('uptime'))   
            except Exception as e:
                print(f"Failed to send Command, {e}", file=sys.stderr)
                failure= f"Failed to send Command {e}"
        
        dfObj.loc[obj_in,'Device Id'] = device['device_id']
        dfObj.loc[obj_in,'IP Address'] = device['device_ip']
        dfObj.loc[obj_in,'SW Type'] = device['sw']
        dfObj.loc[obj_in,'Up Time'] = uptime
        dfObj.loc[obj_in,'Failure Reason'] = failure 

        if device['type'] == 'EDN':
            dfObj.loc[obj_in,'Cisco Domain'] = "EDN-NET"
        if device['type'] == 'IGW':
            dfObj.loc[obj_in,'Cisco Domain'] = "IGW-NET"

        obj_in+=1




    #ACI
    query_string = "select ne_ip_address,  device_id, cisco_domain from seed_table where (cisco_domain = 'EDN-NET' or cisco_domain = 'IGW-NET') and sw_type = 'APIC' and site_type='DC' and operation_status='Production';" 
    result = db.session.execute(query_string)
    ednACIDict = {}
    try:
        for row in result:
            site_apic= row[1].split('-')
            site_apic= '-'.join(site_apic[:-1])
            if site_apic in ednACIDict:
                ednACIDictEntry = {}
                ednACIDictEntry['ip'] = row[0]
                if row[2]=="EDN-NET":
                    ednACIDictEntry['type'] = 'EDN'
                if row[2]=="IGW-NET":
                    ednACIDictEntry['type'] = 'IGW'

                ednACIDictEntry['device_id'] =row[1]

                ednACIDict[site_apic].append(ednACIDictEntry)
            else:
                site_apic= row[1].split('-')
                site_apic= '-'.join(site_apic[:-1])
                ednACIDict[site_apic] = []


                ednACIDictEntry = {}
                ednACIDictEntry['ip'] = row[0]
                ednACIDictEntry['type'] = 'EDN'
                ednACIDictEntry['device_id'] =row[1]
            
                ednACIDict[site_apic].append(ednACIDictEntry)
    except Exception as e:
        print("Exception, {e} ", file=sys.stderr)
        traceback.print_exc()


    with open('app/cred.json') as inventory:
        inv = json.loads(inventory.read())
    
    for dc in ednACIDict:
        hosts = []
        for apic in ednACIDict[dc]:
            if apic['type'] == 'IGW':
                user_name = inv['IGW']['user']
                password = inv['IGW']['pwd']

            if apic['type'] == 'EDN':
                user_name = inv['EDN']['user']
                password = inv['EDN']['pwd']

            host={
                "host": apic["ip"],
                "user": user_name,
                "pwd": password,
                'type': apic["type"]  , 
                'device_id': apic['device_id']             
            }
        
            hosts.append(host)    

                      
        print(f"DEVICES APIC DATA: {hosts}", file=sys.stderr)
        try:
            
            ## Here
            # for host in hosts:

            for host in hosts:
                failure=""
                ##Login
                requests.packages.urllib3.disable_warnings()
                requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
                try:
                    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
                except AttributeError:
                    # no pyopenssl support used / needed / available
                    pass
                        
                cookie = {}
                base_url= None
                headers = None

                print(f"Connecting to {host['host']}")
                login_tries = 3
                c = 0
                port =443
                is_login = False
                base_url = f"https://{host['host']}:{port}"
                while c < login_tries :
                    try:
                        url = base_url+"/api/aaaLogin.json"
                        payload = {
                            "aaaUser": {
                                "attributes": {
                                    "name": host['user'],
                                    "pwd": host['pwd']
                                }
                            }
                        }
                        headers = {'cache-control': "no-cache"}
                        response = requests.post(url, data=json.dumps(payload), headers={'Content-Type': "application/json"}, verify=False).json()
                        token = response['imdata'][0]['aaaLogin']['attributes']['token']                
                        cookie['APIC-cookie'] = token
                        print(f"Success: logged in {host['host']}")
                        is_login = True
                        break
                    except Exception as e:
                        print(e)
                        c +=1
    

                ##login End
            
                if is_login==False:  
                    failure="Login Failed"
                else:
                    try:
                        print("getting APIC Node Ip Address data", file=sys.stderr)
        
                        ip_url = f'{base_url}/api/node/class/topSystem.json?&order-by=topSystem.modTs|desc'
                        
                        headers = {'cache-control': "no-cache"}
                        ip_response = requests.get(ip_url, headers=headers, cookies=cookie, verify=False)
                        
                    
                        if ip_response.ok:
                            ip_response= ip_response.json()
                            ipdataList = ip_response['imdata']
                            for ipdata in ipdataList:
                                uptime = ipdata['topSystem']['attributes']['systemUpTime']
                                dev_id = ipdata['topSystem']['attributes']['name']
                                dev_ip = ipdata['topSystem']['attributes']['oobMgmtAddr']
                                #print(ip_response, file=sys.stderr)


                                uptime_parts = uptime.split(":")
                                days = int(uptime_parts[0])
                                hours = int(uptime_parts[1])
                                minutes = int(uptime_parts[2])
                                seconds = int(uptime_parts[3].split(".")[0])
                                milliseconds = int(uptime_parts[3].split(".")[1])

                                # Convert to a datetime.timedelta object
                                uptime = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)
                                uptime_formatted = f"{uptime.days} day(s), {uptime.seconds // 3600} hour(s), {(uptime.seconds // 60) % 60} minute(s), {uptime.seconds % 60} second(s)"

                                #print(f"Uptime is {uptime}", file=sys.stderr)
                                query_string = f"select sw_type cisco_domain from seed_table where ne_ip_address= '{dev_ip}' and site_type='DC';" 
                                result = db.session.execute(query_string)
                                for row in result:
                                    sw_type= row[0]
                                    if sw_type:

                                        dfObj.loc[obj_in,'Device Id'] = dev_id
                                        dfObj.loc[obj_in,'IP Address'] = dev_ip
                                        dfObj.loc[obj_in,'SW Type'] = sw_type
                                        dfObj.loc[obj_in,'Up Time'] = uptime_formatted
                                        dfObj.loc[obj_in,'Failure Reason'] = failure 
                                        if device['type'] == 'EDN':
                                            dfObj.loc[obj_in,'Cisco Domain'] = "EDN-NET"
                                        if device['type'] == 'IGW':
                                            dfObj.loc[obj_in,'Cisco Domain'] = "IGW-NET"
                                        obj_in+=1
                                        

                            break
                    
                    except Exception as e: 
                        traceback.print_exc()
                        print(f"Exception occured {e}", file=sys.stderr)

        except Exception as e: 
            traceback.print_exc()
            print(f"Exception occured {e}", file=sys.stderr)
        

    #puller.print_failed_devices()
    print("DC Capacity Completed", file=sys.stderr)


    
    try:
        writer = pd.ExcelWriter("uptime"+".xlsx")
        #write dataframe to excel
        dfObj.to_excel(writer, sheet_name="uptime", index=False)
        writer.save()
        
        # #Write CSV
        # dfObj.to_csv(file_name+".csv",index=False)
        # print('DataFrame is written successfully to CSV File.', file=sys.stderr)
    except Exception as e:
        print(f'Error While writing data to CSV file {e}', file=sys.stderr)


    return "Success"


@app.route("/changeDeviceIdsInInventoryTable", methods = ['GET'])
def ChangeDeviceIdsInInventoryTable():

    db.session.execute("SET FOREIGN_KEY_CHECKS=0")

    query_string = f"select device_id, seed_id from seed_table where device_id like '%YFWs%';" 
    result = db.session.execute(query_string)
    count = 0
    for row, sd in result:
        print("$$OLD$$", row, sd, file=sys.stderr)
        newString = row.replace("YFWs", "YFWS")
        print("$$NEW$$", newString, file=sys.stderr)

        objs = Seed.query.filter(Seed.seed_id == sd).all()
        for obj in objs:
            try:
                obj.device_id = newString
                db.session.flush()
                db.session.commit()
                count+=1
            except Exception as e:
                db.session.rollback()
                print("Failed to assign Id", fie=sys.stderr)

    query_string = f"select device_id from device_table where device_id like '%YFWs%';" 
    result = db.session.execute(query_string)
    count1 = 0
    for row in result:
        print("$$OLD$$", row[0], file=sys.stderr)
        newString = row[0].replace("YFWs", "YFWS")
        print("$$NEW$$", newString, file=sys.stderr)

        objs = Device_Table.query.filter(Device_Table.device_id == row[0]).all()
        
        for obj in objs:
            try:
                obj.device_id = newString
                db.session.flush()
                db.session.commit()
                count1+=1
            except Exception as e:
                db.session.rollback()
                traceback.print_exc()
                print("Failed to assign Id", file=sys.stderr)
    
    print("COUNT IS: ", count1, file=sys.stderr)

    query_string = f"select device_id, board_id from board_table where device_id like '%YFWs%';" 
    result = db.session.execute(query_string)
    count2 = 0
    for row, sd in result:
        print("$$OLD$$", row, sd, file=sys.stderr)
        newString = row.replace("YFWs", "YFWS")
        print("$$NEW$$", newString, file=sys.stderr)

        objs = Board_Table.query.filter(Board_Table.board_id == sd).all()
        for obj in objs:
            try:
                obj.device_id = newString
                db.session.flush()
                db.session.commit()
                count2+=1
            except Exception as e:
                db.session.rollback()
                print("Failed to assign Id", fie=sys.stderr)


    query_string = f"select device_id, subboard_id from subboard_table where device_id like '%YFWs%';" 
    result = db.session.execute(query_string)
    count3 = 0
    for row, sd in result:
        print("$$OLD$$", row, sd, file=sys.stderr)
        newString = row.replace("YFWs", "YFWS")
        print("$$NEW$$", newString, file=sys.stderr)

        objs = Subboard_Table.query.filter(Subboard_Table.subboard_id == sd).all()
        for obj in objs:
            try:
                obj.device_id = newString
                db.session.flush()
                db.session.commit()
                count3+=1
            except Exception as e:
                db.session.rollback()
                print("Failed to assign Id", fie=sys.stderr)

    query_string = f"select device_id, sfp_id from sfp_table where device_id like '%YFWs%';" 
    result = db.session.execute(query_string)
    count4 = 0
    for row, sd in result:
        print("$$OLD$$", row, sd, file=sys.stderr)
        newString = row.replace("YFWs", "YFWS")
        print("$$NEW$$", newString, file=sys.stderr)

        objs = SFP_Table.query.filter(SFP_Table.sfp_id == sd).all()
        for obj in objs:
            try:
                obj.device_id = newString
                db.session.flush()
                db.session.commit()
                count4+=1
            except Exception as e:
                db.session.rollback()
                print("Failed to assign Id", fie=sys.stderr)

    query_string = f"select device_id, power_id from power_feeds_table where device_id like '%YFWs%';" 
    result = db.session.execute(query_string)
    count5 = 0
    for row, sd in result:
        print("$$OLD$$", row, sd, file=sys.stderr)
        newString = row.replace("YFWs", "YFWS")
        print("$$NEW$$", newString, file=sys.stderr)

        objs = POWER_FEEDS_TABLE.query.filter(POWER_FEEDS_TABLE.power_id == sd).all()
        for obj in objs:
            try:
                obj.device_id = newString
                db.session.flush()
                db.session.commit()
                count5+=1
            except Exception as e:
                db.session.rollback()
                print("Failed to assign Id", fie=sys.stderr)

    print("Seed COUNT IS: ", count, file=sys.stderr)
    print("Device COUNT IS: ", count1, file=sys.stderr)
    print("Board COUNT IS: ", count2, file=sys.stderr)
    print("Subboard COUNT IS: ", count3, file=sys.stderr)
    print("Sfps COUNT IS: ", count4, file=sys.stderr)
    print("Power Feed COUNT IS: ", count5, file=sys.stderr)

    db.session.execute("SET FOREIGN_KEY_CHECKS=1")

    return "Success"

@app.route("/deleteDuplicateVRF")
def removeDuplicates():
    data = EXTERNAL_VRF_ANALYSIS.query.all()
    dictionary = {}
    for record in data:
        if record.vrf in dictionary:
            dictionary[record.vrf].append(record)
        else:
            dictionary[record.vrf] = [record]
    
    new_list = list(dictionary.values())
    for record in new_list:
        if len(record) > 1:
            for i in range(1, len(record)):
                db.session.execute(f"DELETE FROM external_vrf_analysis WHERE external_vrf_analysis_id = {record[i].external_vrf_analysis_id}")
                db.session.commit()

    # data = [d.as_dict() for d in data]
    # new_dict = {}
    # for d in data:
    #     if d['vrf'] not in new_dict:
    #         new_dict[d['vrf']] = d
    # new_list = list(new_dict.values())
    # print(len(new_list), file=sys.stderr)
    # db.session.query(EXTERNAL_VRF_ANALYSIS).delete()
    # db.session.commit()
    # for record in new_list:
    #     vrf = EXTERNAL_VRF_ANALYSIS()
    #     vrf.vrf = record['vrf']
    #     vrf.primary_site = record['primary_site']
    #     vrf.secondary_site = record['secondary_site']
    #     vrf.no_of_received_routes = record['no_of_received_routes']
    #     vrf.missing_routes_in_secondary_site = record['missing_routes_in_secondary_site']
    #     vrf.creation_date = record['creation_date']
    #     vrf.modification_date = record['modification_date']
    #     vrf.created_by = record['created_by']
    #     vrf.modified_by = record['modified_by']
    #     InsertData(vrf)
    
    return "data"




@app.route("/findArp", methods = ['GET'])
def FindArp():
    df = pd.read_excel('temp/arp.xlsx')
    dfObj2 = pd.DataFrame(columns=['Ip', 'Found in IMS'])
    obj_in=1

    for index, frame in df['IP'].iteritems():
        print(f"No: {index}", file=sys.stderr)
        dfObj2.loc[obj_in,'Ip'] = frame
        if index >= 0:
            #objs = EDN_FIREWALL_ARP.query.filter(EDN_FIREWALL_ARP.ip == 'frame').filter(EDN_FIREWALL_ARP.creation_date, "2023-04-01 05:00:00").all()
            # objs = EDN_FIREWALL_ARP.query.filter(
            # EDN_FIREWALL_ARP.ip.like('%frame%'), 
            # EDN_FIREWALL_ARP.creation_date == "2023-04-01 05:00:00").all()
            
            query= "SELECT * FROM edn_firewall_arp WHERE ip LIKE '%%{}%%' AND DATE(creation_date) BETWEEN DATE_SUB(NOW(), INTERVAL 2 MONTH) AND NOW() ORDER BY creation_date DESC;".format(frame)
            objs= phy_engine.execute(query)
            rows = objs.fetchall()
            if len(rows) == 0:
                dfObj2.loc[obj_in,'Found in IMS'] = "No"
            else:
                dfObj2.loc[obj_in,'Found in IMS'] = "Yes"            
                     
        obj_in+=1 

        writer = pd.ExcelWriter("ips"+".xlsx")
        #write dataframe to excel
        dfObj2.to_excel(writer, sheet_name="ip", index=False)
        writer.save()
        

    return "Success"
    
@app.route("/findArpFromIpamNew", methods = ['GET'])
def FindArpFromIpamNew():
    print("Starting The Endpoint", file=sys.stderr)
    df = pd.read_excel('temp/infoblox_all.xlsx')
    dfObj2 = pd.DataFrame(columns=['Ip', 'Found in IMS', 'Owner'])
    obj_in=1
    # print(df.head(), file=sys.stderr)
    list_of_dicts = df.to_dict(orient='records')
    for frame in list_of_dicts:
        dfObj2.loc[obj_in, 'Ip'] = frame['ipv4addr'].strip()
        #print("This is the IP from file: ", frame['ipv4addr'], file=sys.stderr)
        
        query= f"SELECT distinct * FROM edn_firewall_arp WHERE ip like '%%{frame['ipv4addr'].strip()}%%';"
        objs= phy_engine.execute(query)
        rows = objs.fetchall()
        print("Output from DB is: ", rows, file=sys.stderr)
        if len(rows) == 0:
            dfObj2.loc[obj_in,'Found in IMS'] = "No"
        else:
            dfObj2.loc[obj_in,'Found in IMS'] = "Yes"
        
        if frame['owner'] and frame['owner'] != 'nan':
            dfObj2.loc[obj_in,'Owner'] = frame['owner']
                
                     
        obj_in+=1

        writer = pd.ExcelWriter("ips23"+".xlsx")
        #write dataframe to excel
        dfObj2.to_excel(writer, sheet_name="ip", index=False)
        writer.save()
        

    return "Success"

@app.route("/findArpFromIpamNewTable", methods = ['GET'])
def FindArpFromIpamNewTable():
    try:
        print("Starting The Endpoint", file=sys.stderr)
        df = pd.read_excel('temp/infoblox_all.xlsx')
        dfObj2 = pd.DataFrame(columns=['Ip', 'Found in IMS', 'Owner'])
        obj_in=1
        # print(df.head(), file=sys.stderr)
        # list_of_dicts = df.to_dict(orient='records')
        query= f"SELECT distinct(ip) FROM edn_firewall_arp;"
        objs= phy_engine.execute(query)
        rows = objs.fetchall()
        output = []
        for index, row in enumerate(rows):
            ipaddresses = row[0].split(",")
            print(index, "/", len(rows), file=sys.stderr)
            for ipaddress in ipaddresses:
                if ipaddress in df['ipv4addr'].values:
                    # print("FOUND ", file=sys.stderr)
                    current_dict = {
                        "Ip":ipaddress,
                        "Found in IMS": "Yes",
                        "Owner": df.loc[df.ipv4addr==ipaddress].owner.iloc[0]
                    }
                else:
                    # print("NOT FOUND ", file=sys.stderr)
                    current_dict = {
                        "Ip": ipaddress,
                        "Found in IMS": "No",
                        "Owner": ""
                    }
                output.append(current_dict)
        new_df = pd.DataFrame(output)
        print(new_df.loc[new_df['Found in IMS'] == "Yes"].head(), file=sys.stderr)
            # if df[df['ipv4addr'].str.contains('10.14.108.11')] > 0:
            #     print("Present 10.14.108.11 ", row[0], file=sys.stderr)
            #     break
                # dfObj2.loc[obj_in, 'Ip'] = frame['ipv4addr'].strip()
                # if frame['ipv4addr'] == row:
                #     dfObj2.loc[obj_in,'Found in IMS'] = "Yes"
                #     dfObj2.loc[obj_in,'Owner'] = frame['owner']
                # else:
                #     dfObj2.loc[obj_in,'Found in IMS'] = "No"
                #     dfObj2.loc[obj_in,'Owner'] = frame['owner']
                
                # print("This is the IP from file: ", frame['ipv4addr'], frame['owner'], file=sys.stderr)
                # print("Output from DB is: ", dfObj2, file=sys.stderr)
                        
                            
                # obj_in+=1

        writer = pd.ExcelWriter("ips2.xlsx")
        #write dataframe to excel
        new_df.to_excel(writer, sheet_name="ip", index=False)
        writer.save()
        

        return "Success"
    except Exception as e:
        traceback.print_exc()
        return str(e), 500
    
@app.route("/findCoreRoutingFromIpam", methods = ['GET'])
def FindCoreRoutingFromIpam():
    try:
        print("Starting The Endpoint", file=sys.stderr)
        df = pd.read_excel('temp/infoblox_all.xlsx')
        dfObj2 = pd.DataFrame(columns=['IP', 'Found in Subnet', 'Subnet', 'Originator IP'])
        obj_in=1
        ipList = []
        subnetList = []
        start_date = datetime.now()
        # ipList = list(df['ipv4addr'])
        for index, frame in df['ipv4addr'].iteritems():
            # print(f"No: {index}", file=sys.stderr)
            ipList.append(frame.strip())
        subnets = EDN_CORE_ROUTING.query.with_entities(EDN_CORE_ROUTING.subnet).distinct().filter(EDN_CORE_ROUTING.subnet != '0.0.0.0/0').all()
        for subnet in subnets:
            subnetList.append(IPNetwork(subnet[0]))
        subnetList.sort(key=lambda x:x.prefixlen, reverse=True)
        # for subnet in subnetList:
        # print(str(subnetList[0]), file =sys.stderr)
        # return ""
        for ip in ipList:
            ip_address_check = IPAddress(ip)
            not_found = True
            for subnet_check in subnetList:
                if ip_address_check in subnet_check:
                    print(f"The IP address {ip} is within the subnet {str(subnet_check)}", file=sys.stderr)
                    originatorIp = EDN_CORE_ROUTING.query.with_entities(EDN_CORE_ROUTING.originated_from_ip).filter_by(subnet = str(subnet_check)).first()
                    dfObj2.loc[obj_in,'IP'] = ip
                    dfObj2.loc[obj_in,'Found in Subnet'] = "Yes"
                    dfObj2.loc[obj_in,'Subnet'] = str(subnet_check)
                    dfObj2.loc[obj_in,'Originator IP'] = originatorIp[0]
                    not_found = False
                    obj_in+=1
                    break
                
            if not_found:
                print("The IP address {ip} is not within any subnet", file=sys.stderr)
                dfObj2.loc[obj_in,'IP'] = ip
                dfObj2.loc[obj_in,'Found in Subnet'] = "No"
                obj_in+=1

        writer = pd.ExcelWriter("corerouting.xlsx")
        #write dataframe to excel
        dfObj2.to_excel(writer, sheet_name="ip", index=False)
        writer.save()
        end_date = datetime.now()
        print("EXECUTION TIME: ", start_date, end_date, file=sys.stderr)

        return "Success"
    except Exception as e:
        traceback.print_exc()
        return str(e), 500

