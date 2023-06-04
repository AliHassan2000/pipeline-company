from operator import pos
from re import sub
import site
from app import app,db, tz
from app.models.inventory_models import Phy_Table, Rack_Table, Device_Table, Board_Table, Subboard_Table, SFP_Table, License_Table, Seed, SNTC_Table, PnCode_SNAP_Table
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
tbf = 'TBF'
na = 'NE'

def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%d-%m-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

@app.route("/igwNetVirtual",methods = ['GET'])
@token_required
def igwNetVirtual(user_data):
    if True:
        
        objDict = {}
        queryString = "select `VIRTUAL`,count(`VIRTUAL`) from device_table where CISCO_DOMAIN='IGW-NET' group by `VIRTUAL`,CISCO_DOMAIN;"
        result = db.session.execute(queryString)
        for row in result:
            virtual = row[0]
            countVirtual = row[1]

            if virtual in objDict:
                count = 'value'
                objDict[virtual][count] = countVirtual
                print(objDict,file=sys.stderr)
            else:
                objDict[virtual] = {}
                count = 'value'
                objDict[virtual]['value']=0
                objDict[virtual][count]= countVirtual
        
        objList = []
        for virtual in objDict:
            dict = objDict[virtual]
            dict['name']=virtual
            objList.append(dict)
        print(objList,file = sys.stderr)
        return (jsonify(objList), 200)
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/igwNetOnBoardingPerMonth",methods = ['GET'])
@token_required
def IgwNetOnBoardingPerMonth(user_data):
    
    current_date = datetime.today()

    date_1 = (current_date - relativedelta(months=0)).strftime('%Y-%m')
    print(date_1, file=sys.stderr)
    date_2 = (current_date - relativedelta(months=1)).strftime('%Y-%m')
    print(date_2, file=sys.stderr)

    date_3 = (current_date - relativedelta(months=2)).strftime('%Y-%m')
    print(date_3, file=sys.stderr)

    date_4 = (current_date - relativedelta(months=3)).strftime('%Y-%m')
    print(date_4, file=sys.stderr)
    
    date_5 = (current_date -relativedelta(months=4)).strftime('%Y-%m')
    print(date_5, file=sys.stderr)  
    
    date_6 = (current_date -relativedelta(months=5)).strftime('%Y-%m')
    print(date_6, file=sys.stderr)
    
    date_7 = (current_date -relativedelta(months=6)).strftime('%Y-%m')
    print(date_7, file=sys.stderr)
    
    date_8 = (current_date -relativedelta(months=7)).strftime('%Y-%m')
    print(date_8, file=sys.stderr)
    
    igw_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_8}%' and CISCO_DOMAIN='IGW-NET';").scalar()
    igw_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_7}%' and CISCO_DOMAIN='IGW-NET';").scalar()  
    igw_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_6}%' and CISCO_DOMAIN='IGW-NET';").scalar()
    igw_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_5}%' and CISCO_DOMAIN='IGW-NET';").scalar()    
    igw_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_4}%' and CISCO_DOMAIN='IGW-NET';").scalar()
    igw_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_3}%' and CISCO_DOMAIN='IGW-NET';").scalar()
    igw_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_2}%' and CISCO_DOMAIN='IGW-NET';").scalar()
    igw_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where CREATION_DATE like '%{date_1}%' and CISCO_DOMAIN='IGW-NET';").scalar()
    
    if True:
        objList = [
            {
                "month":date_8,
                "IGW-NET":int(igw_8_count)
            },

            {
                "month":date_7,
                "IGW-NET":int(igw_7_count)
            },

            {
                "month":date_6,
                "IGW-NET":int(igw_6_count)
            },
            {
              "month":date_5,
              "IGW-NET":int(igw_5_count)  
            },
            {
                "month": date_4,
                "IGW-NET": int(igw_4_count)
                
            },
            {
                "month": date_3,
                "IGW-NET": int(igw_3_count)
                
            },
            {
                "month": date_2,
                "IGW-NET": int(igw_2_count)
                
            },
            {
                "month": date_1,
                "IGW-NET": int(igw_1_count)
                
            }
        ]

        return jsonify(objList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/igwNetInventoryCountPerDataCenter",methods = ['GET'])
@token_required
def IgwNetInventoryCountPerDataCenter(user_data):
    if True:
        objDict = {}
        queryString = "select SITE_ID,COUNT(SITE_ID) from device_table where CISCO_DOMAIN='IGW-NET' and SITE_TYPE='DC' and STATUS='Production' group by SITE_ID,CISCO_DOMAIN;"
        result = db.session.execute(queryString)
        for row in result:
            siteId = row[0]
            countSiteId = row[1]
            if siteId in objDict:
                count = 'value'
                objDict[siteId][count] = countSiteId
                print(objDict,file=sys.stderr)
            else:
                objDict[siteId] = {}
                count = 'value'
                objDict[siteId]['value']=0
                objDict[siteId][count]= countSiteId
        
        objList = []
        for siteId in objDict:
            dict = objDict[siteId]
            dict['name']=siteId
            objList.append(dict)
        print(objList,file = sys.stderr)
        return (jsonify(objList), 200)
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/igwNetFunctions",methods = ['GET'])
@token_required
def IgwNetFunctions(user_data):
    if True:
        objDict = {}
        queryString = f"select distinct `FUNCTION`,count(`FUNCTION`) from device_table where CISCO_DOMAIN='IGW-NET' and status='Production' group by CISCO_DOMAIN,`FUNCTION` order by count(`FUNCTION`) DESC LIMIT 20;"
        result = db.session.execute(queryString)
        for row in result:
            function = row[0]
            functionCount = row[1]
            if function in objDict:
                count = 'value'
                objDict[function][count]=functionCount
                print(objDict,file=sys.stderr)
            else:
                objDict[function]={}
                count  = 'value'
                objDict[function]['value']=0
                objDict[function]['value']=functionCount
        objList=[]
        for function in objDict:
            dict = objDict[function]
            dict['name']=function
            objList.append(dict)
        print(objList,file=sys.stderr)
        return jsonify(objList),200

    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/igwNetInventoryCounts",methods = ['GET'])
@token_required
def IgwNetInventoryCounts(user_data):
    if True:
        objList = []

        queryString = "select count(SITE_ID) from phy_table where SITE_ID  in (select SITE_ID from device_table where CISCO_DOMAIN='IGW-NET' and STATUS='Production') and STATUS='Production';"
        phyCount = db.session.execute(queryString).scalar()
        dict = {}
        dict['name']='Sites'
        dict['value'] = phyCount
        objList.append(dict)
        
        queryString1 = "select count(distinct(rack_id)) from device_table where status='Production' and cisco_domain='IGW-NET';"
        rackCount = db.session.execute(queryString1).scalar()
        dict = {}
        dict['name'] = 'Racks'
        dict['value'] = rackCount
        objList.append(dict)
        
        queryString2 = "select coalesce(sum(STACK),0) from device_table where status ='Production' and CISCO_DOMAIN='IGW-NET';"
        deviceCount = db.session.execute(queryString2).scalar()
        deviceCount = int(deviceCount)
        dict = {}
        dict['name']  = 'Devices'
        dict['value'] = deviceCount 
        objList.append(dict)
        
        queryString3 = "select count(DEVICE_ID) from board_table where DEVICE_ID  in (select DEVICE_ID from device_table where CISCO_DOMAIN='IGW-NET' and STATUS='Production') and STATUS='Production';"
        boardCount = db.session.execute(queryString3).scalar()
        dict = {}
        dict['name'] = 'Boards'
        dict['value'] = boardCount
        objList.append(dict)
        
        queryString4 = "select count(DEVICE_ID) from subboard_table where DEVICE_ID  in (select DEVICE_ID from device_table where CISCO_DOMAIN='IGW-NET' and STATUS='Production') and STATUS='Production';"
        subBoardCount = db.session.execute(queryString4).scalar()
        dict = {}
        dict['name'] = 'Sub Boards'
        dict['value'] = subBoardCount
        objList.append(dict)
        
        queryString5 = "select count(DEVICE_ID) from sfp_table where DEVICE_ID  in (select DEVICE_ID from device_table where CISCO_DOMAIN='IGW-NET' and STATUS='Production') and STATUS='Production';"
        sfpCount = db.session.execute(queryString5).scalar()
        dict = {}
        dict['name'] = 'SFPs'
        dict['value'] = sfpCount
        objList.append(dict)
        
        # queryString6 = "select count(NE_NAME) from license_table where NE_NAME in (select DEVICE_NAME from device_table where CISCO_DOMAIN='IGW-NET' and STATUS='Production') and STATUS='Production';"
        # licenseCount = db.session.execute(queryString6).scalar()
        # dict = {}
        # dict['name'] = 'Licenses'
        # dict['value'] = licenseCount
        # objList.append(dict)
        
        print(objList,file=sys.stderr)
        return jsonify(objList),200
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/eosExpiryIgwNet',methods = ['GET'])
@token_required
def EoxStatusIgwNet(user_data):
    if True:
        queryString1 = f"select coalesce(sum(STACK),0) from device_table where HW_EOS_DATE <= NOW() and CISCO_DOMAIN='IGW-NET' and STATUS='Production';"
        queryString2 = f"select coalesce(sum(STACK),0) from device_table where HW_EOS_DATE >= NOW() and CISCO_DOMAIN='IGW-NET' and STATUS='Production';"
        result1 = db.session.execute(queryString1).scalar()
        result2 = db.session.execute(queryString2).scalar()
        objList = [
            {
                "name":"EoX",
                "value":int(result1)
            },
            {
                "name":"non-EoX",
                "value":int(result2)
            }
        ]
        print(objList,file=sys.stderr)
        return jsonify(objList),200
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401 
    
@app.route('/tagIdIgwNet',methods = ['GET'])
@token_required
def TagIdIgwNet(user_data):
    if True:
        tbfCount = db.session.execute(f"select count(TAG_ID) from device_table where `VIRTUAL`='Not Virtual' and status='Production' and TAG_ID='TBF' and CISCO_DOMAIN='IGW-NET';").scalar()
        notTbfCount = db.session.execute(f"select count(TAG_ID) from device_table where `VIRTUAL`='Not Virtual' and status='Production' and TAG_ID!='TBF' and CISCO_DOMAIN='IGW-NET';").scalar()
        
        objList = [
            {
                "name":"No Tag ID",
                "value":tbfCount
            },
            {
                "name":"Tag ID Recorded",
                "value":notTbfCount
            }
        
        ]
        print(objList,file=sys.stderr)
        return jsonify(objList),200
    else:
        print("Authentication Failed",file=sys.stderr)
        return jsonify({"message":"Authentication Failed"}),401

@app.route('/tagIdIgwNetVDate',methods = ['GET'])
@token_required
def TagIdIgwNetVDate(user_data):
    tbfCount = db.session.execute(f"select count(TAG_ID) from device_table where `VIRTUAL`='Not Virtual' and status='Production' and TAG_ID='TBF' and CISCO_DOMAIN='IGW-NET' and rfs_date >= '2022-01-01';").scalar()
    notTbfCount = db.session.execute(f"select count(TAG_ID) from device_table where `VIRTUAL`='Not Virtual' and status='Production' and TAG_ID!='TBF' and CISCO_DOMAIN='IGW-NET' and rfs_date >= '2022-01-01';").scalar()
    
    objList = [
        {
            "name":"No Tag ID",
            "value":tbfCount
        },
        {
            "name":"Tag ID Recorded",
            "value":notTbfCount
        }
    
    ]
    print(objList,file=sys.stderr)
    return jsonify(objList),200

@app.route('/inventoryGrowthIgwNet',methods=['GET'])
@token_required
def InventoryGrowthIgwNet(user_data):
    if True:
        objList = []
        queryString3 = f"select coalesce(sum(IGW_NET),0),CREATION_DATE from pncode_snap_table where CREATION_DATE in (select MAX(CREATION_DATE) as date from pncode_snap_table group by YEAR(CREATION_DATE), MONTH(CREATION_DATE) ORDER by MAX(CREATION_DATE) ASC) group by CREATION_DATE ORDER by CREATION_DATE ASC;"
        result3 = db.session.execute(queryString3)
        count3=0
        for row in result3:
            dict = {}
            sum = int(row[0])
            creationDate = FormatDate(row[1])
            dict["IGW-NET"]=sum
            dict["month"]=creationDate
            objList.append(dict)
            count3+=1
            print('Number of iterations for IGW-SYS: ',count3,file=sys.stderr)
            if count3>=12:
                print("Maximum limit for the months has reached",file=sys.stderr)
                break
        return jsonify(objList),200
        # current_date = datetime.today()
        # date_1 = (current_date - relativedelta(months=0)).strftime('%Y-%m')
        # date_2 = (current_date - relativedelta(months=1)).strftime('%Y-%m')
        # date_3 = (current_date - relativedelta(months=2)).strftime('%Y-%m')
        # date_4 = (current_date - relativedelta(months=3)).strftime('%Y-%m')
        # date_5 = (current_date - relativedelta(months=4)).strftime('%Y-%m')
        # date_6 = (current_date - relativedelta(months=5)).strftime('%Y-%m')
        # date_7 = (current_date - relativedelta(months=6)).strftime('%Y-%m')
        # date_8 = (current_date - relativedelta(months=7)).strftime('%Y-%m')
        # date_9 = (current_date - relativedelta(months=8)).strftime('%Y-%m')
        # date_10 = (current_date - relativedelta(months=9)).strftime('%Y-%m')
        # date_11 = (current_date - relativedelta(months=10)).strftime('%Y-%m')
        # date_12 = (current_date - relativedelta(months=11)).strftime('%Y-%m')

        # igwNetCount1 = db.session.execute(f"select coalesce(sum(IGW_NET),0) from pncode_snap_table where CREATION_DATE like '%{date_1}%'").scalar()
        # igwNetCount2 = db.session.execute(f"select coalesce(sum(IGW_NET),0) from pncode_snap_table where CREATION_DATE like '%{date_2}%'").scalar()
        # igwNetCount3 = db.session.execute(f"select coalesce(sum(IGW_NET),0) from pncode_snap_table where CREATION_DATE like '%{date_3}%'").scalar()
        # igwNetCount4 = db.session.execute(f"select coalesce(sum(IGW_NET),0) from pncode_snap_table where CREATION_DATE like '%{date_4}%'").scalar()
        # igwNetCount5 = db.session.execute(f"select coalesce(sum(IGW_NET),0) from pncode_snap_table where CREATION_DATE like '%{date_5}%'").scalar()
        # igwNetCount6 = db.session.execute(f"select coalesce(sum(IGW_NET),0) from pncode_snap_table where CREATION_DATE like '%{date_6}%'").scalar()
        # igwNetCount7 = db.session.execute(f"select coalesce(sum(IGW_NET),0) from pncode_snap_table where CREATION_DATE like '%{date_7}%'").scalar()
        # igwNetCount8 = db.session.execute(f"select coalesce(sum(IGW_NET),0) from pncode_snap_table where CREATION_DATE like '%{date_8}%'").scalar()
        # igwNetCount9 = db.session.execute(f"select coalesce(sum(IGW_NET),0) from pncode_snap_table where CREATION_DATE like '%{date_9}%'").scalar()
        # igwNetCount10 = db.session.execute(f"select coalesce(sum(IGW_NET),0) from pncode_snap_table where CREATION_DATE like '%{date_10}%'").scalar()
        # igwNetCount11 = db.session.execute(f"select coalesce(sum(IGW_NET),0) from pncode_snap_table where CREATION_DATE like '%{date_11}%'").scalar()
        # igwNetCount12 = db.session.execute(f"select coalesce(sum(EDN_NET),0) from pncode_snap_table where CREATION_DATE like '%{date_12}%'").scalar()
        # objDict = [
        #     {
        #         "month":date_12,
        #         "IGW-NET":int(igwNetCount12)
        #     },
            
        #     {
        #         "month":date_11,
        #         "IGW-NET":int(igwNetCount11)
        #     },
        #     {
        #         "month":date_10,
        #         "IGW-NET":int(igwNetCount10)
        #     },
        #     {
        #         "month":date_9,
        #         "IGW-NET":int(igwNetCount9)
        #     },
        #     {
        #         "month":date_8,
        #         "IGW-NET":int(igwNetCount8)
        #     },
        #     {
        #         "month":date_7,
        #         "IGW-NET":int(igwNetCount7)
        #     },
        #     {
        #         "month":date_6,
        #         "IGW-NET":int(igwNetCount6)
        #     },
        #     {
        #         "month":date_5,
        #         "IGW-NET":int(igwNetCount5)
        #     },
        #     {
        #         "month":date_4,
        #         "IGW-NET":int(igwNetCount4)
        #     },
        #     {
        #         "month":date_3,
        #         "IGW-NET":int(igwNetCount3)
        #     },
        #     {
        #         "month":date_2,
        #         "IGW-NET":int(igwNetCount2)
        #     },
        #     {
        #         "month":date_1,
        #         "IGW-NET":int(igwNetCount1)
        #     }
        # ]
        # print(objDict,file=sys.stderr)
        # return jsonify(objDict),200
    else:
        print("Authentication Failed",file=sys.stderr)
        return jsonify({"message":"Authentication Failed"}),401

@app.route("/getAllPhyIgwNet", methods = ['GET'])
@token_required
def GetAllPhyIgwNet(user_data):
    """
        Get all datacenters endpoint
        ---
        description: Get all datacenters
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true

        responses:
            200:
                description: All Datacenters to be returned from inventory DB
                schema:
                    type: array
                    items:
                        type: object
                        properties:
                            site_id:
                                type: string
                            region:
                                type: string
                            site_name:
                                type: string
                            latitude:
                                type: number
                            longitude:
                                type: number
                            city:
                                type: string
                            creation_date:
                                type: date
                                example: "2019-05-17 12:12:12"
                            modification_date:
                                type: date
                                example: "2019-05-17 12:12:12"
                            status:
                                type: string
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        objList = []
        queryString = "select SITE_ID,REGION,SITE_NAME,LATITUDE,LONGITUDE,CITY,CREATION_DATE,MODIFICATION_DATE,STATUS from phy_table where SITE_ID in (select SITE_ID from device_table where CISCO_DOMAIN='IGW-NET' and STATUS='Production') and STATUS='Production';"
        result = db.session.execute(queryString)
        for row in result:
            objDict = {}
            siteID = row[0]
            region = row[1]
            siteName = row[2]
            latitude = row[3]
            longitude = row[4]
            city = row[5]
            creationDate = row[6]
            modificationDate = row[7] 
            status = row[8]
            objDict["site_id"]=siteID
            objDict["region"]=region
            objDict["site_name"]=siteName
            objDict["latitude"]=latitude
            objDict["longitude"]=longitude
            objDict["city"]=city
            objDict["creation_date"]=FormatDate(creationDate)
            objDict["modification_date"]=FormatDate(modificationDate)
            objDict["status"]=status
            objList.append(objDict)
        print((objList),file=sys.stderr)
        return jsonify(objList),200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getAllRacksIgwNet',methods=['GET'])
@token_required
def GetAllRacksIgwNet(user_data):
    if True:
        objList = []
        queryString = "select RACK_ID,SITE_ID,RACK_NAME,SERIAL_NUMBER,MANUFACTUER_DATE,UNIT_POSITION,CREATION_DATE,MODIFICATION_DATE,STATUS,RU,RFS_DATE,HEIGHT,WIDTH,DEPTH,PN_CODE,TAG_ID,RACK_MODEL,FLOOR from rack_table where SITE_ID in (select SITE_ID from device_table where CISCO_DOMAIN='IGW-NET' and STATUS='Production') and STATUS='Production';"
        result = db.session.execute(queryString)
        for row in result:
            objDict = {}
            rackId = row[0]
            siteId = row[1]
            rackName = row[2]
            serialNumber = row[3]
            manufactuerDate = row[4]
            unitPosition = row[5]
            creationDate = row[6]
            modificationDate = row[7]
            status = row[8]
            ru = row[9]
            rfsDate = row[10]
            height = row[11]
            width = row[12]
            depth = row[13]
            pnCode = row[14]
            tagId = row[15]
            rackModel = row[16]
            floor = row[17]
            objDict["rack_id"]=rackId
            objDict["site_id"]=siteId
            objDict["rack_name"]=rackName
            objDict["serial_number"]=serialNumber
            objDict["manufactuer_date"]=FormatDate(manufactuerDate)
            objDict["unit_position"]=unitPosition
            objDict["creation_date"]=FormatDate(creationDate)
            objDict["modification_date"]=FormatDate(modificationDate)
            objDict["status"]=status
            objDict["ru"]=ru
            objDict["rfs_date"]=FormatDate(rfsDate)
            objDict["height"]=height
            objDict["width"]=width
            objDict["depth"]=depth
            objDict["pn_code"]=pnCode
            objDict["tag_id"]=tagId
            objDict["rack_model"]=rackModel
            objDict["floor"]=floor
            objList.append(objDict)

        print(objList,file=sys.stderr)
        return jsonify(objList),200
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllDevicesIgwNet", methods = ['GET'])
@token_required
def GetAllDevicesIgwNet(user_data):
    """
        Get all Devices endpoint
        ---
        description: Get all Devices
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true
          
        responses:
            200:
                description: All Devices to be returned from inventory DB
                schema:
                    type: array
                    items:
                        type: object
                        properties:
                            device_id:
                                type: string
                            site_id:
                                type: string
                            rack_id:
                                type: integer
                            ne_ip_address:
                                type: string
                            device_name:
                                type: string
                            software_version:
                                type: string
                            patch_version:
                                type: string
                            creation_date:
                                type: string
                                example: "2019-05-17 12:12:12"
                            modification_date:
                                type: date
                                example: "2019-05-17 12:12:12"
                            status:
                                type: string
                            ru:
                                type: integer
                            department:
                                type: string
                            section:
                                type: string
                            criticality:
                                type: string
                            function:
                                type: string
                            cisco_domain:
                                type: string
                            manufacturer:
                                type: string
                            hw_eos_date:
                                type: date
                                example: "2000-01-01"
                            hw_eol_date:
                                type: date
                                example: "2000-01-01"
                            sw_eos_date:
                                type: date
                                example: "2000-01-01"
                            sw_eol_date:
                                type: date
                                example: "2000-01-01"
                            virtual:
                                type: string
                            rfs_date:
                                type: date
                                example: "2000-01-01"
                            authentication:
                                type: string
                            serial_number:
                                type: string
                            pn_code:
                                type: string
                            tag_id:
                                type: string
                            subrack_id_number:
                                type: string
                            manufactuer_date:
                                type: date
                                example: "2000-01-01"
                            hardware_version:
                                type: string
                            max_power:
                                type: string
                            site_type:
                                type: string
                            source:
                                type: string
                            stack:
                                type: string
                            contract_number:
                                type: string
                            contract_expiry:
                                type: date
                                example: "2000-01-01"            
                            
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        deviceObjList=[]
        deviceObjs = Device_Table.query.filter_by(cisco_domain='IGW-NET')

        for deviceObj in deviceObjs:
            deviceDataDict= {}
            deviceDataDict['device_id'] = deviceObj.device_id
            deviceDataDict['site_id'] = deviceObj.site_id
            deviceDataDict['rack_id'] = deviceObj.rack_id
            deviceDataDict['ne_ip_address'] = deviceObj.ne_ip_address
            deviceDataDict['device_name'] = deviceObj.device_name
            deviceDataDict['software_version'] = deviceObj.software_version
            deviceDataDict['patch_version'] = deviceObj.patch_version
            deviceDataDict['creation_date'] = FormatDate(deviceObj.creation_date)
            deviceDataDict['modification_date'] = FormatDate(deviceObj.modification_date)
            deviceDataDict['status'] = deviceObj.status
            deviceDataDict['ru'] = deviceObj.ru
            deviceDataDict['department'] = deviceObj.department
            deviceDataDict['section'] = deviceObj.section
            deviceDataDict['criticality'] = deviceObj.criticality
            deviceDataDict['function'] = deviceObj.function
            deviceDataDict['cisco_domain'] = deviceObj.cisco_domain
            deviceDataDict['manufacturer'] = deviceObj.manufacturer
            deviceDataDict['hw_eos_date'] = FormatDate(deviceObj.hw_eos_date)
            deviceDataDict['hw_eol_date'] = FormatDate(deviceObj.hw_eol_date)
            deviceDataDict['sw_eos_date'] = FormatDate(deviceObj.sw_eos_date)
            deviceDataDict['sw_eol_date'] = FormatDate(deviceObj.sw_eol_date)
            deviceDataDict['virtual'] = deviceObj.virtual
            deviceDataDict['rfs_date'] = FormatDate(deviceObj.rfs_date)
            deviceDataDict['authentication'] = deviceObj.authentication
            deviceDataDict['serial_number'] = deviceObj.serial_number
            deviceDataDict['pn_code'] = deviceObj.pn_code
            deviceDataDict['tag_id'] = deviceObj.tag_id
            deviceDataDict['subrack_id_number'] = deviceObj.subrack_id_number
            deviceDataDict['manufactuer_date'] = FormatDate(deviceObj.manufactuer_date)
            deviceDataDict['hardware_version'] = deviceObj.hardware_version
            deviceDataDict['max_power'] = deviceObj.max_power
            deviceDataDict['site_type'] = deviceObj.site_type
            deviceDataDict['source'] = deviceObj.source
            deviceDataDict['stack'] = deviceObj.stack
            deviceDataDict['contract_number'] = deviceObj.contract_number
            deviceDataDict['contract_expiry'] = FormatDate(deviceObj.contract_expiry)

            # deviceDataDict['site_name'] = Phy_Table.query.with_entities(Phy_Table.site_name).filter_by(site_id=deviceObj.site_id).first()[0]
            # deviceDataDict['rack_name'] = Rack_Table.query.with_entities(Rack_Table.rack_name).filter_by(rack_id=deviceObj.rack_id).first()[0]
            
        
            deviceObjList.append(deviceDataDict)
        print((deviceObjList),file=sys.stderr)
        return jsonify(deviceObjList), 200
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllBoardsIgwNet", methods = ['GET'])
@token_required
def GetAllBoardsIgwNet(user_data):
    """
        Get all Boards endpoint
        ---
        description: Get all Boards
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true
          
        responses:
            200:
                description: All Boards to be returned from inventory DB
                schema:
                    type: array
                    items:
                        type: object
                        properties:
                            board_id:
                                type: integer
                            device_id:
                                type: string
                            board_name:
                                type: string
                            device_slot_id:
                                type: string
                            hardware_version:
                                type: string
                            software_version:
                                type: string
                            serial_number:
                                type: string
                            manufactuer_date:
                                type: date
                                example: "2000-01-01"
                            creation_date:
                                type: date
                                example: "2019-05-17 12:12:12"
                            modification_date:
                                type: date
                                example: "2019-05-17 12:12:12"
                            status:
                                type: string
                            eos_date:
                                type: date
                                example: "2000-01-01"
                            eol_date:
                                type: date
                                example: "2000-01-01"
                            rfs_date:
                                type: date
                                example: "2000-01-01"
                            pn_code:
                                type: string
                            tag_id:
                                type: string
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        
        objList=[]
        queryString = "select BOARD_ID,DEVICE_ID,BOARD_NAME,DEVICE_SLOT_ID,SOFTWARE_VERSION,HARDWARE_VERSION,SERIAL_NUMBER,MANUFACTUER_DATE,CREATION_DATE,MODIFICATION_DATE,STATUS,EOS_DATE,EOL_DATE,RFS_DATE,PN_CODE,TAG_ID from board_table where DEVICE_ID in (select DEVICE_ID from device_table where CISCO_DOMAIN='IGW-NET' and STATUS='Production') and STATUS='Production';"
        result = db.session.execute(queryString)
        for row in result:
            boardId = row[0]
            deviceId = row[1]
            boardName = row[2]
            deviceSlotId = row[3]
            softwareVersion = row[4]
            hardwareVersion = row[5]
            serialNumner = row[6]
            manufactuerDate = row[7]
            creationDate = row[8]
            modificationDate = row[9]
            status = row[10]
            eosDate = row[11]
            eolDate = row[12]
            rfsDate = row[13]
            pnCode = row[14]
            tagId = row[15]

            objDict= {}
            objDict['board_id'] = boardId 
            objDict['device_id'] = deviceId
            objDict['board_name'] = boardName
            objDict['device_slot_id'] = deviceSlotId 
            objDict['software_version'] = softwareVersion 
            objDict['hardware_version'] = hardwareVersion 
            objDict['serial_number'] = serialNumner 
            objDict['manufactuer_date'] = FormatDate(manufactuerDate)
            objDict['creation_date'] = FormatDate(creationDate)
            objDict['modification_date'] = FormatDate(modificationDate)
            objDict['status'] = status 
            objDict['eos_date'] = FormatDate(eosDate)
            objDict['eol_date'] = FormatDate(eolDate)
            objDict['rfs_date'] = FormatDate(rfsDate)
            objDict['pn_code'] = pnCode 
            objDict['tag_id'] = tagId
            objList.append(objDict)

        print(len(objList),file = sys.stderr)
        return jsonify(objList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllSubboardsIgwNet", methods = ['GET'])
@token_required
def GetAllSubboardsIgwNet(user_data):
    """
        Get all Sub-Boards endpoint
        ---
        description: Get all Sub-Boards
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true
          
        responses:
            200:
                description: All Sub-Boards to be returned from inventory DB
                schema:
                    type: array
                    items:
                        type: object
                        properties:
                            subboard_id:
                                type: integer
                            device_id:
                                type: string
                            subboard_name:
                                type: string
                            subboard_type:
                                type: string
                            subrack_id:
                                type: string
                            slot_number:
                                type: string
                            subslot_number:
                                type: string
                            hardware_version:
                                type: string
                            software_version:
                                type: string
                            serial_number:
                                type: string
                            creation_date:
                                type: date
                                example: "2019-05-17 12:12:12"
                            modification_date:
                                type: date
                                example: "2019-05-17 12:12:12"
                            status:
                                type: string
                            eos_date:
                                type: date
                                example: "2000-01-01"
                            eol_date:
                                type: date
                                example: "2000-01-01"
                            rfs_date:
                                type: date
                                example: "2000-01-01"
                            pn_code:
                                type: string
                            tag_id:
                                type: string
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        objList=[]
        queryString = "select SUBBOARD_ID,DEVICE_ID,SUBBOARD_NAME,SUBBOARD_TYPE,SUBRACK_ID,SLOT_NUMBER,SUBSLOT_NUMBER,SOFTWARE_VERSION,HARDWARE_VERSION,SERIAL_NUMBER,CREATION_DATE,MODIFICATION_DATE,STATUS,EOS_DATE,EOL_DATE,RFS_DATE,TAG_ID,PN_CODE from subboard_table where DEVICE_ID in (select DEVICE_ID from device_table where CISCO_DOMAIN='IGW-NET' and STATUS='Production' and STATUS='Production');"
        result = db.session.execute(queryString)
        for row in result:
            subboardId = row[0]
            deviceID = row[1]
            subboardName = row[2]
            subboardType = row[3]
            subrackId = row[4]
            slotNumber = row[5]
            subslotNumber = row[6]
            softwareVersion = row[7]
            hardwareVersion = row[8]
            serialNumber = row[9]
            creationDate = row[10]
            modificationDate = row[11]
            status = row[12]
            eosDate = row[13]
            eolDate = row[14]
            rfsDate = row[15]
            tagId = row[16]
            pnCode = row[17]

            objDict= {}
            objDict['subboard_id'] = subboardId
            objDict['device_id'] = deviceID
            objDict['subboard_name'] = subboardName
            objDict['subboard_type'] = subboardType
            objDict['subrack_id'] = subrackId
            objDict['slot_number'] = slotNumber
            objDict['subslot_number']=subslotNumber
            objDict['hardware_version'] = hardwareVersion
            objDict['software_version'] = softwareVersion
            objDict['serial_number'] = serialNumber
            objDict['creation_date'] = FormatDate(creationDate)
            objDict['modification_date'] = FormatDate(modificationDate)
            objDict['status'] = status
            objDict['eos_date'] = FormatDate(eosDate)
            objDict['eol_date'] = FormatDate(eolDate)
            objDict['rfs_date'] = FormatDate(rfsDate)
            objDict['tag_id'] = tagId
            objDict['pn_code'] = pnCode
            
            objList.append(objDict)

        print(len(objList),file = sys.stderr)
        return jsonify(objList), 200
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllSfpsIgwNet", methods = ['GET'])
@token_required
def GetAllSFPSIgwNet(user_data):
    """
        Get all SFPs endpoint
        ---
        description: Get all SFPs
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true
          
        responses:
            200:
                description: All SFPs to be returned from inventory DB
                schema:
                    type: array
                    items:
                        type: object
                        properties:
                            sfp_id:
                                type: integer
                            device_id:
                                type: string
                            media_type:
                                type: string
                            port_name:
                                type: string
                            port_type:
                                type: string
                            connector:
                                type: string
                            mode:
                                type: string
                            speed:
                                type: string
                            wavelength:
                                type: string
                            manufacturer:
                                type: string
                            optical_direction_type:
                                type: string
                            pn_code:
                                type: string
                            creation_date:
                                type: date
                                example: "2019-05-17 12:12:12"
                            modification_date:
                                type: date
                                example: "2019-05-17 12:12:12"
                            status:
                                type: string
                            eos_date:
                                type: date
                                example: "2000-01-01"
                            eol_date:
                                type: date
                                example: "2000-01-01"
                            rfs_date:
                                type: date
                                example: "2000-01-01"
                            tag_id:
                                type: string  
                            serial_number:
                                type: string  
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        objList=[]
        queryString = "select SFP_ID,DEVICE_ID,MEDIA_TYPE,PORT_NAME,PORT_TYPE,CONNECTOR,MODE,SPEED,WAVELENGTH,MANUFACTURER,OPTICAL_DIRECTION_TYPE,PN_CODE,CREATION_DATE,MODIFICATION_DATE,STATUS,EOS_DATE,EOL_DATE,RFS_DATE,TAG_ID,SERIAL_NUMBER from sfp_table where DEVICE_ID in (select DEVICE_ID from device_table where CISCO_DOMAIN='IGW-NET' and STATUS='Production') and STATUS='Production';"
        result = db.session.execute(queryString)
        for row in result:
            sfpId = row[0]
            deviceId = row[1]
            mediaType = row[2]
            portName = row[3]
            portType = row[4]
            connector = row[5]
            mode = row[6]
            speed = row[7]
            wavelength = row[8]
            manufacturer = row[9]
            opticalDirectionType = row[10]
            pnCode = row[11]
            creationDate = row[12]
            modificationDate = row[13]
            status = row[14]
            eosDate = row[15]
            eolDate = row[16]
            rfsDate = row[17]
            tagId = row[18]
            serialNumber = row[19]

            objDict= {}

            objDict['sfp_id'] = sfpId
            objDict['device_id'] = deviceId
            objDict['media_type'] = mediaType
            objDict['port_name'] = portName
            objDict['port_type'] = portType
            objDict['connector'] = connector
            objDict['mode'] = mode
            objDict['speed'] = speed
            objDict['wavelength'] = wavelength
            objDict['manufacturer'] = manufacturer
            objDict['optical_direction_type'] = opticalDirectionType
            objDict['pn_Code'] = pnCode
            objDict['creation_date'] = FormatDate(creationDate)
            objDict['modification_date'] = FormatDate(modificationDate)
            objDict['status'] = status
            objDict['eos_date'] = FormatDate(eosDate)
            objDict['eol_date'] = FormatDate(eolDate)
            objDict['rfs_date'] = FormatDate(rfsDate)
            objDict['tag_id'] = tagId
            objDict['serial_number'] = serialNumber



            objList.append(objDict)
        print(len(objList),file = sys.stderr)
        return jsonify(objList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllLicensesIgwNet", methods = ['GET'])
@token_required
def GetAllLicencesIgwNet(user_data):
    """
        Get all SFPsLicenses endpoint
        ---
        description: Get all Licenses
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true
          
        responses:
            200:
                description: All Licenses to be returned from inventory DB
                schema:
                    type: array
                    items:
                        type: object
                        properties:
                            license_id:
                                type: integer
                            license_name:
                                type: string
                            license_description:
                                type: string
                            ne_name:
                                type: string
                            rfs_date:
                                type: date
                                example: "2000-01-01"
                            activation_date:
                                type: date
                                example: "2000-01-01"
                            expiry_date:
                                type: date
                                example: "2000-01-01"
                            grace_period:
                                type: string
                            serial_number:
                                type: string
                            creation_date:
                                type: date
                                example: "2019-05-17 12:12:12"
                            modification_date:
                                type: date
                                example: "2019-05-17 12:12:12"
                            status:
                                type: string
                            tag_id:
                                type: string
                            capacity:
                                type: string
                            usage:
                                type: string
                            pn_code:
                                type: string
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        objList=[]
        queryString = "select LICENSE_ID,LICENSE_NAME,LICENSE_DESCRIPTION,NE_NAME,RFS_DATE,ACTIVATION_DATE,EXPIRY_DATE,GRACE_PERIOD,SERIAL_NUMBER,CREATION_DATE,MODIFICATION_DATE,STATUS,TAG_ID,CAPACITY,`USAGE`,PN_CODE from license_table where NE_NAME in (select DEVICE_ID from device_table where CISCO_DOMAIN='IGW-NET' and STATUS='Production') and STATUS='Production';"
        result = db.session.execute(queryString)
        for row in result:
            licenseId = row[0]
            licenseName = row[1]
            licenseDescription = row[2]
            neName = row[3]
            rfsDate = row[4]
            activationDate = row[5]
            expiryDate = row[6]
            gracePeriod = row[7]
            serialNumber = row[8]
            creationDate = row[9]
            modificationDate = row[10]
            status = row[11]
            tagId = row[12]
            capacity = row[13]
            usage = row[14]
            pnCode = row[15]
            objDict= {}

            objDict['license_id'] = licenseId 
            objDict['license_name'] = licenseName
            objDict['license_description'] = licenseDescription
            objDict['ne_name'] = neName
            objDict['rfs_date'] = FormatDate(rfsDate)
            objDict['activation_date'] = FormatDate(activationDate)
            objDict['expiry_date'] = FormatDate(expiryDate)
            objDict['grace_period'] = gracePeriod
            objDict['serial_number'] = serialNumber
            objDict['creation_date'] = FormatDate(creationDate)
            objDict['modification_date'] = FormatDate(modificationDate)
            objDict['status'] = status
            objDict['tag_id'] = tagId
            objDict['capacity'] = capacity
            objDict['usage'] = usage
            objDict['pn_code'] = pnCode
            
            objList.append(objDict)
        print(len(objList),file = sys.stderr)
        return jsonify(objList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/dismantledDevicesPerMonthIgwNet",methods = ['GET'])
@token_required
def DismantledDevicesPerMonthIgwNet(user_data):
    
    current_date = datetime.today()

    date_1 = (current_date - relativedelta(months=0)).strftime('%Y-%m')
    print(date_1, file=sys.stderr)
    date_2 = (current_date - relativedelta(months=1)).strftime('%Y-%m')
    print(date_2, file=sys.stderr)

    date_3 = (current_date - relativedelta(months=2)).strftime('%Y-%m')
    print(date_3, file=sys.stderr)

    date_4 = (current_date - relativedelta(months=3)).strftime('%Y-%m')
    print(date_4, file=sys.stderr)
    
    date_5 = (current_date -relativedelta(months=4)).strftime('%Y-%m')
    print(date_5, file=sys.stderr)  
    
    date_6 = (current_date -relativedelta(months=5)).strftime('%Y-%m')
    print(date_6, file=sys.stderr)
    
    date_7 = (current_date -relativedelta(months=6)).strftime('%Y-%m')
    print(date_7, file=sys.stderr)
    
    date_8 = (current_date -relativedelta(months=7)).strftime('%Y-%m')
    print(date_8, file=sys.stderr)
    
    igw_8_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_8}%' and CISCO_DOMAIN='IGW-NET' and STATUS='dismantle';").scalar()
    igw_7_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_7}%' and CISCO_DOMAIN='IGW-NET' and STATUS='dismantle';").scalar()  
    igw_6_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_6}%' and CISCO_DOMAIN='IGW-NET' and STATUS='dismantle';").scalar()
    igw_5_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_5}%' and CISCO_DOMAIN='IGW-NET' and STATUS='dismantle';").scalar()    
    igw_4_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_4}%' and CISCO_DOMAIN='IGW-NET' and STATUS='dismantle';").scalar()
    igw_3_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_3}%' and CISCO_DOMAIN='IGW-NET' and STATUS='dismantle';").scalar()
    igw_2_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_2}%' and CISCO_DOMAIN='IGW-NET' and STATUS='dismantle';").scalar()
    igw_1_count = db.session.execute(f"select coalesce(sum(STACK),0) from device_table where DISMANTLE_DATE like '%{date_1}%' and CISCO_DOMAIN='IGW-NET' and STATUS='dismantle';").scalar()
    
    if True:
        objList = [
            {
                "month":date_8,
                "IGW-NET":int(igw_8_count)
            },

            {
                "month":date_7,
                "IGW-NET":int(igw_7_count)
            },

            {
                "month":date_6,
                "IGW-NET":int(igw_6_count)
            },
            {
              "month":date_5,
              "IGW-NET":int(igw_5_count)  
            },
            {
                "month": date_4,
                "IGW-NET": int(igw_4_count)
                
            },
            {
                "month": date_3,
                "IGW-NET": int(igw_3_count)
                
            },
            {
                "month": date_2,
                "IGW-NET": int(igw_2_count)
                
            },
            {
                "month": date_1,
                "IGW-NET": int(igw_1_count)
                
            }
        ]

        return jsonify(objList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
