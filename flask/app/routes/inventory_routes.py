from decimal import Decimal
from lib2to3.pgen2 import token
from operator import pos
from random import seed
from re import sub
import re
from termios import CDSUSP
import traceback
from unittest.result import failfast
from app import app,db, tz
from app.models.inventory_models import Phy_Table, Rack_Table, Device_Table, Board_Table, Subboard_Table, SFP_Table, License_Table, Seed, SNTC_Table, PnCode_SNAP_Table, CDN_Table, POWER_FEEDS_TABLE,Rebd_Table,Pos_Table, FUNCTIONS_TABLE, DOMAINS_TABLE
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
from dateutil.relativedelta import relativedelta

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

def InsertData(obj):
    #add data to db
    try:        
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
        # db.session.flush()

        db.session.merge(obj)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong during Database Update {e}", file=sys.stderr)
    
    return True

def InsertInventoryData(pullerData, user_data):
    failed=False
    for ip_addr in pullerData:
        data = pullerData[ip_addr]
        print(data,  file=sys.stderr)
        
        if 'error' in data:
            print("Login Failed Skipping",  file=sys.stderr)
            #print("Login Failed adding static information",  file=sys.stderr)
            #InsertSeedInventoryData(ip_addr)

        elif  data['status'] == 'success':

            seed = Seed.query.filter_by(ne_ip_address=ip_addr).first()
            if not seed:
                print("Seed Not found", file=sys.stderr)
                continue

            site = Phy_Table.query.filter_by(site_id=seed.site_id).first()
            rack = Rack_Table.query.filter_by(rack_id=seed.rack_id).first()
            
            if not site:
                print("Site Not found", file=sys.stderr)
                failed=True
                continue

            if not rack:
                print("Racks Not found", file=sys.stderr)
                failed= True
                continue

            print("Puller Contain Data",file=sys.stderr)
            
            
            dismantleOnBoardDeviceFun(ip_addr, user_data, True)


            seed.onboard_status = 'true'
            seed.operation_status = 'Production'
            seed.modified_by= user_data['user_id']
            UpdateData(seed)
            

            '''
            
            if seed.region is not None:
                phyObj.region= seed.region
            else:
                phyObj.region = tbf
            
            phyObj.site_name = seed.site_name
            if seed.latitude is not None:
                phyObj.latitude = seed.latitude
            else:
                phyObj.latitude = tbf
            if seed.longitude is not None:
                phyObj.longitude = seed.longitude
            else:
                phyObj.longitude = tbf
            if seed.city is not None:
                phyObj.city = seed.city
            else:
                phyObj.city = tbf
            if seed.datacentre_status is not None:
                phyObj.status= seed.datacentre_status
            else:
                phyObj.status= tbf

            siteID = Phy_Table.query.with_entities(Phy_Table.site_id).filter_by(site_id=seed.site_id).first()
            if siteID is not None:
                phyObj.site_id = siteID[0]
                print("Updated site " + phyObj.site_name,file=sys.stderr)
                phyObj.modification_date= datetime.now(tz)
                UpdateData(phyObj)
            else:
                print("Inserted site " +phyObj.site_name,file=sys.stderr)
                phyObj.creation_date= datetime.now(tz)
                phyObj.modification_date= datetime.now(tz)
                InsertData(phyObj)

            rackObj = Rack_Table()
            rackObj.site_id= phyObj.site_id
            rackObj.rack_name= seed.rack_name
            if seed.serial_number is not None:
                rackObj.serial_number= seed.serial_number
            else:
                rackObj.serial_number= tbf
            if seed.manufactuer_date is not None:
                rackObj.manufactuer_date= seed.manufactuer_date
            if seed.unit_position is not None:
                rackObj.unit_position= seed.unit_position
            else:
                rackObj.unit_position= tbf
            if seed.rack_status is not None:
                rackObj.status= seed.rack_status
            else:
                rackObj.status= tbf
            if seed.ru is not None:
                rackObj.ru= seed.ru
            if seed.rfs_date is not None:
                rackObj.rfs_date= seed.rfs_date
            if seed.height is not None:
                rackObj.height= seed.height
            if seed.width is not None:
                rackObj.width= seed.width
            if seed.depth is not None:
                rackObj.depth= seed.depth
            if seed.pn_code is not None:
                rackObj.pn_code= seed.pn_code
            else:
                rackObj.pn_code= tbf
            if seed.tag_id is not None:
                rackObj.tag_id= seed.tag_id
            else:
                rackObj.tag_id= tbf
            if seed.rack_model is not None:
                rackObj.rack_model= seed.rack_model
            else:
                rackObj.rack_model= tbf
            if seed.floor is not None:
                rackObj.floor= seed.floor
            else:
                rackObj.floor= tbf

            rackID = Rack_Table.query.with_entities(Rack_Table.rack_id).filter_by(rack_name=rackObj.rack_name).first()
            if rackID is not None:
                rackObj.rack_id = rackID[0]
                print("Updated rack " + rackObj.rack_name,file=sys.stderr)
                rackObj.modification_date= datetime.now(tz)
                UpdateData(rackObj)
            else:
                print("Inserted rack " +rackObj.rack_name,file=sys.stderr)
                rackObj.creation_date= datetime.now(tz)
                rackObj.modification_date= datetime.now(tz)
                InsertData(rackObj)
            '''
            deviceObj = Device_Table() 
            deviceObj.device_id= seed.device_id
            deviceObj.site_id= seed.site_id #
            deviceObj.rack_id= seed.rack_id#
            deviceObj.ne_ip_address= ip_addr
            if data['device']['software_version'] is not None: 
                deviceObj.software_version= data['device']['software_version']
            else:
                deviceObj.software_version= na
            if 'patch_version' in data and data['device']['patch_version'] is not None: 
                deviceObj.patch_version= data['device']['patch_version']
            else:
                deviceObj.patch_version = na
            if seed.hostname is not None:
                deviceObj.device_name= seed.hostname
            else:
                deviceObj.device_name = tbf
            if data['device']['status'] is not None:
                deviceObj.status= data['device']['status']
                deviceObj.ims_status= "Active"
            else:
                deviceObj.status= na
            if seed.device_ru is not None:
                deviceObj.ru= seed.device_ru
            if seed.department is not None:
                deviceObj.department= seed.department
            else:
                deviceObj.department = tbf
            if seed.section is not None:
                deviceObj.section= seed.section
            else:
                deviceObj.section = tbf
            if seed.criticality is not None:
                deviceObj.criticality= seed.criticality
            else:
                deviceObj.criticality = tbf
            if seed.function is not None:
                deviceObj.function= seed.function
            else:
                deviceObj.function = tbf
            if seed.cisco_domain is not None:
                deviceObj.cisco_domain= seed.cisco_domain                
                if "EDN" in str(seed.cisco_domain):
                    deviceObj.domain= "ENT"
                if "IGW" in str(seed.cisco_domain):
                    deviceObj.domain= "IGW"
                if "SOC" in str(seed.cisco_domain):
                    deviceObj.domain= "Security"
            else:
                deviceObj.cisco_domain = tbf
            
            if data['device']['manufecturer'] is not None:
                deviceObj.manufacturer= data['device']['manufecturer']
            else:
                deviceObj.manufacturer= na
            if seed.virtual is not None:
                deviceObj.virtual= seed.virtual
            else:
                deviceObj.virtual = tbf
            if data['device']['authentication'] is not None:
                deviceObj.authentication= data['device']['authentication']
            else:
                deviceObj.authentication= na
            if data['device']['serial_number'] is not None:
                deviceObj.serial_number= data['device']['serial_number']
            else:
                deviceObj.serial_number= na
            if data['device']['pn_code'] is not None:
                deviceObj.pn_code= data['device']['pn_code']
            else:
                deviceObj.pn_code= na
            if seed.tag_id is not None:
                deviceObj.tag_id= seed.tag_id
            else:
                deviceObj.tag_id = tbf
            if seed.subrack_id_number is not None:
                deviceObj.subrack_id_number= seed.subrack_id_number
            else:
                deviceObj.subrack_id_number= na
            if data['device']['hw_version'] is not None:
                deviceObj.hardware_version= data['device']['hw_version']
            else:
                deviceObj.hardware_version= na
            if data['device']['max_power'] is not None:
                deviceObj.max_power= data['device']['max_power']
            else:
                deviceObj.max_power= na
                
            if seed.rfs_date is not None:
                deviceObj.rfs_date = seed.rfs_date
            if seed.site_type is not None:
                deviceObj.site_type= seed.site_type
            else:
                deviceObj.site_type = tbf

            if 'stack' in data['device']:
                deviceObj.stack= data['device']['stack']
            else:
                deviceObj.stack= 1

            deviceObj.source = 'Dynamic'

            if seed.contract_number is not None:
                deviceObj.contract_number= seed.contract_number
            else:
                deviceObj.contract_number = tbf

            if seed.contract_expiry is not None:
                deviceObj.contract_expiry = seed.contract_expiry

            if seed.item_code is not None:
                deviceObj.item_code= seed.item_code
            else:
                deviceObj.item_code= tbf

            if seed.item_desc is not None:
                deviceObj.item_desc= seed.item_desc
            else:
                deviceObj.item_desc= tbf

            if seed.clei is not None:
                deviceObj.clei= seed.clei
            else:
                deviceObj.clei= tbf
            if seed.parent is not None:
                deviceObj.parent= seed.parent

            if seed.vuln_fix_plan_status is not None:
                deviceObj.vuln_fix_plan_status= seed.vuln_fix_plan_status

            if seed.vuln_ops_severity is not None:
                deviceObj.vuln_ops_severity= seed.vuln_ops_severity
            
            if seed.integrated_with_aaa is not None:
                deviceObj.integrated_with_aaa= seed.integrated_with_aaa
            if seed.integrated_with_paam is not None:
                deviceObj.integrated_with_paam= seed.integrated_with_paam
            if seed.approved_mbss is not None:
                deviceObj.approved_mbss= seed.approved_mbss
            if seed.mbss_implemented is not None:
                deviceObj.mbss_implemented= seed.mbss_implemented
            if seed.mbss_integration_check is not None:
                deviceObj.mbss_integration_check= seed.mbss_integration_check
            if seed.integrated_with_siem is not None:
                deviceObj.integrated_with_siem= seed.integrated_with_siem
            if seed.threat_cases is not None:
                deviceObj.threat_cases= seed.threat_cases
            if seed.vulnerability_scanning is not None:
                deviceObj.vulnerability_scanning= seed.vulnerability_scanning
            if seed.vulnerability_severity is not None:
                deviceObj.vulnerability_severity= seed.vulnerability_severity


            if deviceObj.pn_code is not None:
                sntcDevice = SNTC_Table.query.filter_by(pn_code=deviceObj.pn_code).first()
                if sntcDevice:

                    if sntcDevice.hw_eos_date is not None:
                        deviceObj.hw_eos_date = sntcDevice.hw_eos_date
                    if sntcDevice.hw_eol_date is not None:
                        deviceObj.hw_eol_date = sntcDevice.hw_eol_date
                    if sntcDevice.sw_eos_date is not None:
                        deviceObj.sw_eos_date = sntcDevice.sw_eos_date
                    if sntcDevice.sw_eol_date is not None:
                        deviceObj.sw_eol_date = sntcDevice.sw_eol_date
                    if sntcDevice.item_desc is not None:
                        deviceObj.item_desc = sntcDevice.item_desc
                    if sntcDevice.item_code is not None:
                        deviceObj.item_code = sntcDevice.item_code
            try:
                imsFunction= str(deviceObj.device_id).split('-') 
                imsFunction= imsFunction[1] 
                
                imsFunctionObj = FUNCTIONS_TABLE.query.with_entities(FUNCTIONS_TABLE.function).filter_by(tfun=imsFunction).first() 
                if imsFunctionObj:
                    deviceObj.ims_function= imsFunctionObj[0]
                else:
                    deviceObj.ims_function= imsFunction
            except Exception as e:
                print(f"Exception Occured in Getting IMS Function {e}", file=sys.stderr)

            deviceID = Device_Table.query.with_entities(Device_Table.device_id).filter_by(ne_ip_address=deviceObj.ne_ip_address).first()
            if deviceID is not None:
                deviceObj.device_id = deviceID[0]
                print("Updated device " + deviceObj.ne_ip_address,file=sys.stderr)
                deviceObj.modification_date= datetime.now(tz)
                deviceObj.modified_by= user_data['user_id']

                UpdateData(deviceObj)
            else:
                print("Inserted device " +deviceObj.ne_ip_address,file=sys.stderr)
                deviceObj.creation_date= datetime.now(tz)
                deviceObj.modification_date= datetime.now(tz)
                deviceObj.created_by= user_data['user_id']
                deviceObj.modified_by= user_data['user_id']
                InsertData(deviceObj)
            
            deviceID = Device_Table.query.with_entities(Device_Table.device_id).filter_by(ne_ip_address=deviceObj.ne_ip_address).first()[0]
            
            power= POWER_FEEDS_TABLE()
            if POWER_FEEDS_TABLE.query.with_entities(POWER_FEEDS_TABLE).filter_by(device_id=deviceID).first() is not None:
                row= POWER_FEEDS_TABLE.query.with_entities(POWER_FEEDS_TABLE.device_id,POWER_FEEDS_TABLE.power_id).filter_by(device_id=deviceID).first()
                power.device_id = row[0]
                power.power_id= row[1]
                power.status= deviceObj.status

                print("Updated Power Feed ",file=sys.stderr)
                power.created_by= user_data['user_id']
                UpdateData(power)
            else:
                
                power.device_id =deviceID
                power.status= deviceObj.status
                power.created_by= user_data['user_id']
                power.modified_by= user_data['user_id']

                print("Inserted Power Feed" ,file=sys.stderr)
                InsertData(power)


            for board in data['board']:
                #print(board,file=sys.stderr)
                boardObj = Board_Table() 
                boardObj.device_id= deviceID
                if 'board_name' in board:
                    boardObj.board_name = board['board_name']
                if board['slot_id'] is not None:
                    boardObj.device_slot_id = board['slot_id']
                else:
                    boardObj.device_slot_id= na
                if  board['hw_version'] is not None:
                    boardObj.hardware_version = board['hw_version']
                else:
                    boardObj.hardware_version= na
                if board['software_version'] is not None:
                    boardObj.software_version = board['software_version']
                else:
                    boardObj.software_version= na
                if  board['serial_number']  is not None:
                    boardObj.serial_number = board['serial_number'] 
                else:
                    boardObj.serial_number= na
                if board['status'] is not None:
                    boardObj.status = board['status']
                else:
                    boardObj.status= na
                if board['pn_code'] is not None:
                    boardObj.pn_code = board['pn_code']
                else:
                    boardObj.pn_code= na
                boardObj.tag_id= "non-taggable"
                #if seed.tag_id is not None:
                #    boardObj.tag_id= seed.tag_id
                #else:
                #    boardObj.tag_id = tbf
                #if seed.rfs_date is not None:
                #    boardObj.rfs_date = seed.rfs_date
                boardObj.item_code= tbf
                boardObj.item_desc= tbf
                boardObj.clei= tbf

                if boardObj.pn_code is not None:
                    sntcDevice = SNTC_Table.query.filter_by(pn_code=boardObj.pn_code).first()
                    if sntcDevice:

                        if sntcDevice.hw_eos_date is not None:
                            boardObj.eos_date = sntcDevice.hw_eos_date
                        if sntcDevice.hw_eol_date is not None:
                            boardObj.eol_date = sntcDevice.hw_eol_date
                        if sntcDevice.manufactuer_date is not None:
                            boardObj.manufactuer_date = sntcDevice.manufactuer_date
                        if sntcDevice.item_desc is not None:
                            boardObj.item_desc = sntcDevice.item_desc
                        else:

                            sntcDevice.item_desc= boardObj.board_name
                            boardObj.item_desc= boardObj.board_name
                            UpdateData(sntcDevice)
                            
                        if sntcDevice.item_code is not None:
                            boardObj.item_code = sntcDevice.item_code
                        

                boardObj.rfs_date= deviceObj.rfs_date

                if boardObj.serial_number:
                    boardID = Board_Table.query.with_entities(Board_Table.board_id).filter_by(serial_number=boardObj.serial_number).first()
                else:
                    boardID = Board_Table.query.with_entities(Board_Table.board_id).filter_by(board_name=boardObj.board_name).first()

                if boardID is not None:
                    boardObj.board_id = boardID[0]
                    print("Updated board " + boardObj.board_name+ " with serial number "+ boardObj.serial_number,file=sys.stderr)
                    boardObj.modification_date= datetime.now(tz)
                    boardObj.modified_by= user_data['user_id']
                    UpdateData(boardObj)
                else:
                    print("Inserted board " +boardObj.board_name+ " with serial number "+ boardObj.serial_number,file=sys.stderr)
                    boardObj.creation_date= datetime.now(tz)
                    boardObj.created_by= user_data['user_id']
                    boardObj.modified_by= user_data['user_id']
                    boardObj.modification_date= datetime.now(tz)
                    InsertData(boardObj)

            for subboard in data['sub_board']:
                subboardObj = Subboard_Table() 
                subboardObj.device_id= deviceID
                subboardObj.subboard_name = subboard['subboard_name']
                if subboard['subboard_type'] is not None:
                    subboardObj.subboard_type = subboard['subboard_type']
                else:
                    subboardObj.subboard_type= na
                if 'subrack_id' in subboard and subboard['subrack_id'] is not None:
                    subboardObj.subrack_id = subboard['subrack_id']
                else:
                    subboardObj.subrack_id= na
                if subboard['slot_number'] is not None:
                    subboardObj.slot_number = subboard['slot_number']
                else:
                    subboardObj.slot_number= na
                if subboard['subslot_number'] is not None:
                    subboardObj.subslot_number = subboard['subslot_number']
                else:
                    subboardObj.subslot_number= na
                if subboard['hw_version'] is not None:
                    subboardObj.hardware_version = subboard['hw_version']
                else:
                    subboardObj.hardware_version= na
                if 'software_version' in subboard and  subboard['software_version'] is not None:
                    subboardObj.software_version = subboard['software_version']
                else:
                    subboardObj.software_version= na
                if subboard['serial_number'] is not None:
                    subboardObj.serial_number = subboard['serial_number']
                else:
                    subboardObj.serial_number= na
                if subboard['status'] is not None:
                    subboardObj.status = subboard['status']
                else:
                    subboardObj.status= na
                if subboard['pn_code'] is not None:
                    subboardObj.pn_code = subboard['pn_code']
                else:
                    subboardObj.pn_code= na

                subboardObj.item_code= tbf
                subboardObj.item_desc= tbf
                subboardObj.clei= tbf
                subboardObj.tag_id= "non-taggable"
                #if seed.tag_id is not None:
                #    subboardObj.tag_id= seed.tag_id
                #else:
                #    subboardObj.tag_id = tbf
                #if seed.rfs_date is not None:
                #    subboardObj.rfs_date = seed.rfs_date

                if subboardObj.pn_code is not None:
                    sntcDevice = SNTC_Table.query.filter_by(pn_code=subboardObj.pn_code).first()
                    if sntcDevice:

                        if sntcDevice.hw_eos_date is not None:
                            subboardObj.eos_date = sntcDevice.hw_eos_date
                        if sntcDevice.hw_eol_date is not None:
                            subboardObj.eol_date = sntcDevice.hw_eol_date
                        if sntcDevice.item_desc is not None:
                            subboardObj.item_desc = sntcDevice.item_desc
                        else:
                            sntcDevice.item_desc= subboardObj.subboard_type
                            subboardObj.item_desc= subboardObj.subboard_type
                            UpdateData(sntcDevice)
                        if sntcDevice.item_code is not None:
                            subboardObj.item_code = sntcDevice.item_code
                        
                
                subboardObj.rfs_date= deviceObj.rfs_date                          
                    
                if subboardObj.serial_number:
                    subboardID = Subboard_Table.query.with_entities(Subboard_Table.subboard_id).filter_by(serial_number=subboardObj.serial_number).first()
                else:
                    subboardID = Subboard_Table.query.with_entities(Subboard_Table.subboard_id).filter_by(subboard_name=subboardObj.subboard_name).first()
                if subboardID is not None:
                    subboardObj.subboard_id = subboardID[0]
                    print("Updated subboard " + str(subboardObj.subboard_name) + " with serial number "+ subboardObj.serial_number,file=sys.stderr)
                    subboardObj.modification_date= datetime.now(tz)
                    subboardObj.modified_by= user_data['user_id']
                    UpdateData(subboardObj)
                else:
                    print("Inserted subboard " + str(subboardObj.subboard_name)+ " with serial number "+ subboardObj.serial_number,file=sys.stderr)
                    subboardObj.creation_date= datetime.now(tz)
                    subboardObj.modification_date= datetime.now(tz)
                    subboardObj.created_by= user_data['user_id']
                    subboardObj.modified_by= user_data['user_id']
                    InsertData(subboardObj)
            
            for sfp in data['sfp']:
                sfpData = SFP_Table()
                sfpData.device_id = deviceID
                if sfp['media_type'] is not None:
                    sfpData.media_type = sfp['media_type']
                else:
                    sfpData.media_type= na
                if sfp['port_name'] is not None:
                    sfpData.port_name = sfp['port_name'].strip()
                else:
                    sfpData.port_name= na
                if sfp['port_type'] is not None:
                    sfpData.port_type = sfp['port_type']
                else:
                    sfpData.port_type= na
                if sfp['connector'] is not None:
                    sfpData.connector = sfp['connector']
                else:
                    sfpData.connector= na
                    
                #print(f"Connector value is {sfpData.connector}", file=sys.stderr)
                if sfp['mode'] is not None:
                    sfpData.mode = sfp['mode']
                else:
                    sfpData.mode= na
                if sfp['speed'] is not None:
                    sfpData.speed = sfp['speed']
                else:
                    sfpData.speed= na
                if sfp['wavelength'] is not None:
                    sfpData.wavelength = sfp['wavelength']
                else:
                    sfpData.wavelength= na
                if sfp['manufacturer'] is not None:
                    sfpData.manufacturer = sfp['manufacturer']
                else:
                    sfpData.manufacturer= na
                if sfp['optical_direction_type'] is not None:
                    sfpData.optical_direction_type = sfp['optical_direction_type']
                else:
                    sfpData.optical_direction_type= na
                if sfp['pn_code'] is not None:
                    sfpData.pn_code = sfp['pn_code']
                else:
                    sfpData.pn_code= na
                if sfp['status'] is not None:
                    sfpData.status = sfp['status']
                else:
                    sfpData.status= na
                
                sfpData.item_code= tbf
                sfpData.item_desc= tbf
                sfpData.clei= tbf
                sfpData.tag_id= "non-taggable"
                #if seed.tag_id is not None:
                #    sfpData.tag_id= seed.tag_id
                #else:
                #    sfpData.tag_id = tbf
                #if seed.rfs_date is not None:
                #    sfpData.rfs_date = seed.rfs_date
            
                sfpData.rfs_date= deviceObj.rfs_date
                if sfp['serial_number'] is not None:
                    sfpData.serial_number = sfp['serial_number']
                else:
                    sfpData.serial_number= na
                if sfpData.pn_code is not None:
                    sntcDevice = SNTC_Table.query.filter_by(pn_code=sfpData.pn_code).first()
                    if sntcDevice:
                        
                        if sntcDevice.hw_eos_date is not None:
                            sfpData.eos_date = sntcDevice.hw_eos_date
                        if sntcDevice.hw_eol_date is not None:
                            sfpData.eol_date = sntcDevice.hw_eol_date
                        if sntcDevice.item_desc is not None:
                            sfpData.item_desc = sntcDevice.item_desc  
                        if sntcDevice.item_code is not None:
                            sfpData.item_code = sntcDevice.item_code                  
                
                #sfpID = SFP_Table.query.with_entities(SFP_Table.sfp_id).filter_by(device_id=sfpData.device_id).filter_by(port_name=sfpData.port_name).first()
                #temp= SFP_Table.query.with_entities(SFP_Table.sfp_id).filter_by(device_id=sfpData.device_id).filter_by(port_name=sfpData.port_name).first()

                sfpObj = SFP_Table.query.with_entities(SFP_Table).filter_by(serial_number=sfpData.serial_number).first()
                if sfpObj:
                    if sfpObj.serial_number=="NE":
                        sfpObj = SFP_Table.query.with_entities(SFP_Table).filter_by(device_id=sfpData.device_id).filter_by(port_name=sfpData.port_name.strip()).first()
        
                if sfpObj:
                        sfpData.sfp_id = sfpObj.sfp_id
                        print("Updated sfp " + str(sfpData.port_name) + " with serial number "+ sfpData.serial_number,file=sys.stderr)
                        sfpData.modification_date= datetime.now(tz)
                        sfpData.modified_by= user_data['user_id']
                        UpdateData(sfpData)   
                else:
                        
                        print("Inserted sfp " + str(sfpData.port_name)+ " with serial number "+ sfpData.serial_number,file=sys.stderr)
                        sfpData.creation_date= datetime.now(tz)
                        sfpData.modification_date= datetime.now(tz)
                        sfpData.created_by= user_data['user_id']
                        sfpData.modified_by= user_data['user_id']
                        InsertData(sfpData)
                # if sfpID is not None :
                #     sfpData.sfpID = sfpID[0]
                #     print("Updated port " + str(sfpData.port_name),file=sys.stderr)
                #     UpdateData(sfpData)

                # if sfpID is None:
                #     print("Inserted port " +str(sfpData.port_name),file=sys.stderr)
                #     InsertData(sfpData)
                    
            for license in data['license']:
                if license['name'] != "":
                    licenseData = License_Table()
                    if 'name' in license:
                        licenseData.license_name = license['name']
                    if license['description'] is not None:
                        licenseData.license_description = license['description']
                    else:
                        licenseData.license_description= na
                    licenseData.ne_name = seed.hostname
                    if 'activation_date' in license:
                        licenseData.activation_date = FormatStringDate(license['activation_date'])
                    if license['grace_period'] is not None:
                        licenseData.grace_period = license['grace_period']
                    else:
                        licenseData.grace_period= na
                    if 'expiry_date' in license:
                        licenseData.expiry_date = FormatStringDate(license['expiry_date'])
                    if license['serial_number'] is not None:
                        licenseData.serial_number = license['serial_number']
                    else:
                        licenseData.serial_number= na
                    if license['status'] is not None:
                        licenseData.status = license['status']
                    else:
                        licenseData.status= na
                    if license['capacity'] is not None:
                        licenseData.capacity = license['capacity']
                    else:
                        licenseData.capacity= na
                    if license['usage'] is not None:
                        licenseData.usage = license['usage']
                    else:
                        licenseData.usage= na
                    if license['pn_code'] is not None:
                        licenseData.pn_code = license['pn_code']
                    else:
                        licenseData.pn_code= na
                    if seed.tag_id is not None:
                        licenseData.tag_id= seed.tag_id
                    else:
                        licenseData.tag_id = tbf

                    licenseData.item_code= tbf
                    licenseData.item_desc= tbf
                    licenseData.clei= tbf
                    licenseData.rfs_date= deviceObj.rfs_date
                    licenseID = License_Table.query.with_entities(License_Table.license_id).filter_by(license_name=licenseData.license_name).first()
                    if licenseID is not None:
                        licenseDataID = licenseID[0]
                        #print("Updated license " + str(licenseData),file=sys.stderr)
                        #licenseData.modification_date= datetime.now(tz)
                        licenseData.license_id = licenseDataID
                        licenseData.modified_by= user_data['user_id']
                        UpdateData(licenseData)
                    else:
                        # print("Inserted license " +str(licenseData),file=sys.stderr)
                        #licenseData.creation_date= datetime.now(tz)
                        #licenseData.modification_date= datetime.now(tz)
                        licenseData.created_by= user_data['user_id']
                        licenseData.modified_by= user_data['user_id']
                        InsertData(licenseData)
            seed.onboard_status = 'true'
            seed.modified_by= user_data['user_id']
            UpdateData(seed)
            '''
            ######ADDITIONS BY HAMZA###########
            power= POWER_FEEDS_TABLE()

            if POWER_FEEDS_TABLE.query.with_entities(POWER_FEEDS_TABLE).filter_by(device_id=deviceObj.device_id).first() is not None:

                row= POWER_FEEDS_TABLE.query.with_entities(POWER_FEEDS_TABLE.device_id,POWER_FEEDS_TABLE.power_id).filter_by(device_id=deviceObj.device_id).first()

                power.device_id = row[0]

                power.power_id= row[1]
                print("Updated Power Feed ",file=sys.stderr)

                UpdateData(power)
            else:
                power.device_id =deviceObj.device_id
                power.status= deviceObj.status
                print("Inserted Power Feed" ,file=sys.stderr)
                InsertData(power)
            '''
        else:
            print("Error while getting data from device " + ip_addr,file=sys.stderr)
    return failed

def FormatStringDate(date):
    print(date, file=sys.stderr)

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

def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%d-%m-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

def getESXIIpsList():
    ip_list = []
    
    Objs = Seed.query.filter_by(sw_type='IPT').all()

    for obj in Objs:
        ip = {}
        ip['ip'] = obj.ne_ip_address
        ip['device_name'] = obj.hostname
        ip['function'] = obj.function
        ip_list.append(ip)

    return ip_list

def getBladeHosts(master):
    print(master, file=sys.stderr)

    slave_list = []
    master_split = master.split('-SCB')[0]
    master_split = master_split+'-FB'

    #print(master_split, file=sys.stderr)
    resp = Seed.query.filter(Seed.hostname.contains(master_split))

    for obj in resp:
        slave = {}
        slave['ip'] = obj.ne_ip_address
        slave['device_name'] = obj.hostname
        slave_list.append(slave)
        print(obj.ne_ip_address + '  '+ obj.hostname, file=sys.stderr)

    return slave_list

def CreatePullersDictList(postData):
    hosts = []
    
    with open('app/cred.json') as inventory:
        inv = json.loads(inventory.read())

    for data in postData:
        #print(ip, file=sys.stderr)
        hostDict = {}
        hostDict["host"] = data['ip']
        
        if data['asset_type'] == 'IGW':
            hostDict["user"] = inv['IGW']['user']
            hostDict["pwd"] = inv['IGW']['pwd']

        elif data['asset_type'] == 'EDN':
            hostDict["user"] = inv['EDN']['user']
            hostDict["pwd"] = inv['EDN']['pwd']

        elif data['asset_type'] == 'WLC':
            hostDict["user"] = inv['WLC']['user']
            hostDict["pwd"] = inv['WLC']['pwd']
            
        elif data['asset_type'] == 'PRIME_UCS_EDN':
            hostDict["user"] = inv['PRIME_UCS_EDN']['user']
            hostDict["pwd"] = inv['PRIME_UCS_EDN']['pwd']
            
        elif data['asset_type'] == 'SYSTEMS':
            hostDict["user"] = inv['SYSTEMS']['user']
            hostDict["pwd"] = inv['SYSTEMS']['pwd']

        elif data['asset_type'] == 'SYS-ESXI':
            hostDict["user"] = inv['SYSTEMS']['user']
            hostDict["pwd"] = inv['SYSTEMS']['pwd']

        elif data['asset_type']=='UCS-CIMC':
            hostDict["user"] = inv['SYSTEMS']['user']
            hostDict["pwd"] = inv['SYSTEMS']['pwd']

        elif data['asset_type'] == 'WireFilter':
            hostDict["user"] = inv['SYSTEMS']['user']
            hostDict["pwd"] = inv['SYSTEMS']['pwd']
            hostDict["slave"]= getBladeHosts(data['device_name'])
            hostDict["master"]={
                'ip': data['ip'],
                'device_name': data['device_name']
            }

        elif data['asset_type']=='IPT-UCS':
            hostDict["user"] = inv['IPT_UCS']['user']
            hostDict["pwd"] = inv['IPT_UCS']['pwd']
           
        elif data['asset_type']=='IPT-ROUTER':
            hostDict["user"] = inv['EDN']['user']
            hostDict["pwd"] = inv['EDN']['pwd']
            
        elif data['asset_type']=='IPT-ESXI':
            hostDict["user"] = inv['IPT']['user']
            hostDict["pwd"] = inv['IPT']['pwd']
            hostDict["auth-key"] = inv['IPT']['auth-key']
            hostDict["ipt-list"] = getESXIIpsList()
            hostDict['ipt-type'] = data['function']

        elif data['asset_type'] == 'Arbor-Sec':
            hostDict["user"] = inv['SEC']['user']
            hostDict["pwd"] = inv['SEC']['pwd']
            
        elif data['asset_type'] == 'Fortinet-Sec':
            hostDict["user"] = inv['SEC']['user']
            hostDict["pwd"] = inv['SEC']['pwd']
            
        elif data['asset_type'] == 'ASA-SOC':
            hostDict["user"] = inv['SEC']['user']
            hostDict["pwd"] = inv['SEC']['pwd']
        
        elif data['asset_type'] == 'ASA96':
            hostDict["user"] = inv['SEC']['user']
            hostDict["pwd"] = inv['SEC']['pwd']
            
        elif data['asset_type'] == 'Juniper-Sec':
            hostDict["user"] = inv['SEC']['user']
            hostDict["pwd"] = inv['SEC']['pwd']
        
        elif data['asset_type'] == 'Juniper-Screenos':
            hostDict["user"] = inv['SEC']['user']
            hostDict["pwd"] = inv['SEC']['pwd']

        elif data['asset_type'] == 'PaloAlto':
            hostDict["user"] = inv['SEC']['user']
            hostDict["pwd"] = inv['SEC']['pwd']
            
        elif data['asset_type'] == 'Symantec-SOC':
            hostDict["user"] = inv['SEC']['user']
            hostDict["pwd"] = inv['SEC']['pwd']
            
        elif data['asset_type'] == 'FireEye-SOC':
            hostDict["user"] = inv['SEC']['user']
            hostDict["pwd"] = inv['SEC']['pwd']
            
        elif data['asset_type'] == 'Firepower-SOC':
            hostDict["user"] = inv['SEC']['user']
            hostDict["pwd"] = inv['SEC']['pwd']

        elif data['asset_type'] == 'FirepowerServer':
            hostDict["user"] = inv['SEC']['user']
            hostDict["pwd"] = inv['SEC']['pwd']
        
        elif data['asset_type'] == 'Firepower-SSH':
            hostDict["user"] = inv['SEC']['user']
            hostDict["pwd"] = inv['SEC']['pwd']
            
        elif data['asset_type'] == 'PulseSecure':
            hostDict["user"] = inv['SEC']['user']
            hostDict["pwd"] = inv['SEC']['pwd']
            
        else:
            hostDict["user"] = inv['IGW']['user']
            hostDict["pwd"] = inv['IGW']['pwd']

        hosts.append(hostDict)

    print(hosts, file=sys.stderr)
    return hosts

def GetDatafromPullers(hosts,key):
    pullerResp = {}
    if key == 'IOS-XR':
        print("IOS-XR device puller started", file=sys.stderr)
        pullerXR = XRPuller()
        pullerResp = pullerXR.get_inventory_data(hosts)

    elif key == 'IOS':
        print("IOS device puller started", file=sys.stderr)
        pullerIOS = IOSPuller()
        pullerResp = pullerIOS.get_inventory_data(hosts)

    elif key == 'IOS-XE':
        print("IOS-XE device puller started", file=sys.stderr)
        pullerXE = XEPuller()
        pullerResp = pullerXE.get_inventory_data(hosts)

    elif key == 'NX-OS' :
        print(f"{key} device puller started", file=sys.stderr)
        pullerNXOS = NXOSPuller()
        pullerResp = pullerNXOS.get_inventory_data(hosts)

    elif key == 'APIC' or key=='APIC-SYS':
        pulleraci = ACIPuller()
        pullerResp = pulleraci.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)

    elif key == 'WLC':
        pullerwlc = WLCPuller()
        pullerResp = pullerwlc.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
    
    elif key == 'PRIME':
        pullerprime = PrimePuller()
        pullerResp = pullerprime.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
    
    elif key == 'UCS' or key=='UCS-SYS' or key=="UCS-CIMC":
        pullerUcs = UCSPuller()
        pullerResp = pullerUcs.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
    
    elif key == 'A10':
        pullerA10 = A10Puller()
        pullerResp = pullerA10.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
    
    elif key == 'Infoblox':
        pullerInfo = InfoboxPuller()
        pullerResp = pullerInfo.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
    
    elif key == 'Arista':
        pullerArista = AristaPuller()
        pullerResp = pullerArista.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
    
    elif key == 'Arbor' or key=='Arbor-Sec':
        pullerArbor = ArborPuller()
        pullerResp = pullerArbor.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
    
    elif key == 'WireFilter':
        pullerWireFilter = WirefilterPuller()
        pullerResp = pullerWireFilter.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
    
    elif key == 'IPT-ESXI' or key == 'SYS-ESXI':
        pullerIPT = IPTPuller()
        pullerResp = pullerIPT.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
    
    elif key == 'IPT-UCS':
        pullerucs = UCSPuller()
        pullerResp = pullerucs.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
        
    elif key == 'IPT-ROUTER':
        pullerxe = XEPuller()
        pullerResp = pullerxe.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)

    elif key == 'Fortinet-Sec':
        pullerucs = FortinetPuller()
        pullerResp = pullerucs.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)

    elif key == 'Juniper-Sec':
        pullerucs = JuniperPuller()
        pullerResp = pullerucs.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
    
    elif key == 'Juniper-Screenos':
        pullerucs = JuniperScreenosPuller()
        pullerResp = pullerucs.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
    
    elif key == 'ASA-SOC':
        pullerAsa = ASAPuller()
        pullerResp = pullerAsa.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
    
    elif key == 'ASA96':
        pullerAsa96 = ASA96Puller()
        pullerResp = pullerAsa96.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
    
    elif key == 'PaloAlto':
        pullerPP = PaloAltoPuller()
        pullerResp = pullerPP.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
            
    elif key == 'PulseSecure':
        pullerPS = PulseSecurePuller()
        pullerResp = pullerPS.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
    
    elif key == 'Symantec':
        pullerSYN = SymantecPuller()
        pullerResp = pullerSYN.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
    
    elif key == 'FireEye':
        pullerfire = FireEyePuller()
        pullerResp = pullerfire.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
        
    elif key == 'FirepowerServer':
        pullerfireP = FirePowerPuller()
        pullerResp = pullerfireP.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)

    elif key == 'Firepower-SSH':
        pullerfireP = FirePowerPullerSSH()
        pullerResp = pullerfireP.get_inventory_data(hosts)
        print(f"{key} device puller started", file=sys.stderr)
        
    else:
        print("Unknow device skipping", file=sys.stderr)


    return pullerResp

@app.route("/editRacks", methods = ['POST'])
@token_required
def EditRacks(user_data):    
    if True:#session.get('token', None):
        racksObj = request.get_json()
        print(racksObj,file = sys.stderr)
        racks = Rack_Table.query.with_entities(Rack_Table).filter_by(rack_id=racksObj["rack_id"]).first()
        
        racks.tag_id = racksObj['tag_id']          
        racks.rfs_date = FormatStringDate(racksObj['rfs_date'])
        racks.modification_date= datetime.now(tz)
        racks.modified_by= user_data['user_id']
        UpdateData(racks)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editDevices", methods = ['POST'])
@token_required
def EditDevices(user_data):    
    if True:#session.get('token', None):
        deviceObj = request.get_json()
        print(deviceObj,file = sys.stderr)
        device = Device_Table.query.with_entities(Device_Table).filter_by(device_id=deviceObj["device_id"]).first()
        seed = Seed.query.with_entities(Seed).filter_by(device_id=deviceObj["device_id"]).first()
        if Phy_Table.query.with_entities(Phy_Table.site_id).filter_by(site_id=deviceObj['site_id']).first() != None and Rack_Table.query.with_entities(Rack_Table.rack_id).filter_by(rack_id=deviceObj['rack_id']).first() != None:
            device.tag_id = deviceObj['tag_id']
            device.device_name = deviceObj['device_name']          
            
            device.rfs_date = FormatStringDate(deviceObj['rfs_date'])
            device.function = deviceObj['function']
            #device.item_code = deviceObj['item_code']
            #device.item_desc = deviceObj['item_desc']
            device.clei = deviceObj['clei']

            rack=""
            rack= str(deviceObj['rack_id'])
            if rack:
                rack= rack.split('|')
                rack=rack[0]

            device.rack_id = rack
            device.site_id = deviceObj['site_id']
            #device.manufacture_date = deviceObj['manufactuer_date']
            device.virtual = deviceObj['virtual']
            device.authentication = deviceObj['authentication']
            device.subrack_id_number = deviceObj['subrack_id_number']
            device.criticality = deviceObj['criticality']
            device.cisco_domain = deviceObj['cisco_domain']
            if "EDN" in str(device.cisco_domain):
                device.domain= "ENT"
            if "IGW" in str(device.cisco_domain):
                device.domain= "IGW"
            if "SOC" in str(device.cisco_domain):
                device.domain= "Security"
            device.patch_version = deviceObj['patch_version']
            #device.section = deviceObj['section']
            device.software_version = deviceObj['software_version']
            device.hardware_version = deviceObj['hardware_version']
            #device.department = deviceObj['department']
            device.serial_number = deviceObj['serial_number']
            device.pn_code = deviceObj['pn_code']
            device.max_power = deviceObj['max_power']
            if deviceObj['device_ru']:
                device.ru = deviceObj['device_ru']
            device.manufacturer = deviceObj['manufacturer']
            device.stack = deviceObj['stack']
            device.source = deviceObj['source']
            device.site_type = deviceObj['site_type']
            device.contract_number = deviceObj['contract_number']
            device.contract_expiry = FormatStringDate(deviceObj['contract_expiry'])
            device.status = deviceObj['status']
            device.parent = deviceObj['parent']
            device.vuln_fix_plan_status = deviceObj['vuln_fix_plan_status']
            device.vuln_ops_severity = deviceObj['vuln_ops_severity']
            device.integrated_with_aaa = deviceObj['integrated_with_aaa']
            device.integrated_with_paam = deviceObj['integrated_with_paam']
            device.approved_mbss = deviceObj['approved_mbss']
            device.mbss_implemented = deviceObj['mbss_implemented']
            device.mbss_integration_check = deviceObj['mbss_integration_check']
            device.integrated_with_siem = deviceObj['integrated_with_siem']
            device.threat_cases = deviceObj['threat_cases']
            device.vulnerability_scanning = deviceObj['vulnerability_scanning']
            if 'vulnerability_severity' in deviceObj:
                device.vulnerability_severity = deviceObj['vulnerability_severity']


            if deviceObj['dismantle_date']:
                device.dismantle_date = FormatStringDate(deviceObj['dismantle_date'])
            

            if device.status =="Production" or device.status =="Offloaded" or device.status =="Powered Off":
                device.ims_status = "Active"
            if device.status =="Dismantle":
                device.ims_status = "Decommissioned"
            if device.status =="Powered Off" :
                device.ims_status = "Offline"
            
            try:
                
                domainsnObj = DOMAINS_TABLE.query.filter_by(cisco_domain=seed.cisco_domain).first() 
                if domainsnObj:
                    device.department= domainsnObj.department
                    device.section= domainsnObj.section
                    seed.department= domainsnObj.department
                    seed.section= domainsnObj.section
                
            except Exception as e:
                print(f"Exception Occured in Getting Domains Information {e}", file=sys.stderr)

            #device.hw_eos_date = FormatStringDate(deviceObj['hw_eos_date'])
            #device.hw_eol_date = FormatStringDate(deviceObj['hw_eol_date'])
            #device.sw_eos_date = FormatStringDate(deviceObj['sw_eos_date'])

            try:
                seed.tag_id = deviceObj['tag_id']
                seed.device_ru = deviceObj.get('device_ru')
                seed.hostname = deviceObj['device_name']
                seed.rfs_date = FormatStringDate(deviceObj['rfs_date'])
                seed.function = deviceObj['function']
    
                # seed.item_code = deviceObj['item_code']
                # seed.item_desc = deviceObj['item_desc']
                seed.clei = deviceObj['clei']
                
                rack=""
                rack= str(deviceObj['rack_id'])
                if rack:
                    rack= rack.split('|')
                    rack=rack[0]
                seed.rack_id = rack
                seed.site_id = deviceObj['site_id']
                seed.virtual = deviceObj['virtual']
                seed.authentication = deviceObj['authentication']
                seed.subrack_id_number = deviceObj['subrack_id_number']
                seed.criticality = deviceObj['criticality']
                seed.cisco_domain = deviceObj['cisco_domain']
                #seed.section = deviceObj['section']
                #seed.department = deviceObj['department']
                # seed.device_ru = deviceObj['ru']
                seed.site_type = deviceObj['site_type']
                seed.contract_number = deviceObj['contract_number']
                seed.contract_expiry = FormatStringDate(deviceObj['contract_expiry'])
                seed.operation_status = deviceObj['status']
                seed.parent = deviceObj['parent']
                seed.vuln_fix_plan_status = deviceObj['vuln_fix_plan_status']
                seed.vuln_ops_severity = deviceObj['vuln_ops_severity']
                seed.integrated_with_aaa = deviceObj['integrated_with_aaa']
                seed.integrated_with_paam = deviceObj['integrated_with_paam']
                seed.approved_mbss = deviceObj['approved_mbss']
                seed.mbss_implemented = deviceObj['mbss_implemented']
                seed.mbss_integration_check = deviceObj['mbss_integration_check']
                seed.integrated_with_siem = deviceObj['integrated_with_siem']
                seed.threat_cases = deviceObj['threat_cases']
                seed.vulnerability_scanning = deviceObj['vulnerability_scanning']
                if "vulnerability_severity" in deviceObj:
                    seed.vulnerability_severity = deviceObj['vulnerability_severity']

                #if seed.operation_status !="Dismantle":
                seed.modified_by= user_data['user_id']
                device.modification_date= datetime.now(tz)
                    
                
                UpdateData(seed)
            except Exception as e:
                print(str(e),file=sys.stderr)
                print("Device not Found in seed", file=sys.stderr)

            try:
                powerObj = db.session.query(POWER_FEEDS_TABLE).filter_by(device_id=deviceObj.get('device_id')).first()
                if powerObj:   
                    powerObj.status = deviceObj['status']
                    
                    #if device.status !="Dismantle":
                    powerObj.modified_by= user_data['user_id']
                    device.modification_date= datetime.now(tz)
                    
                    UpdateData(powerObj)
               
            except Exception as e:
                print(f"Device not Found in Power Feed {e}", file=sys.stderr)
            print("Updated Device", file=sys.stderr)
            
            
            #if device.status !="Dismantle":
            device.modified_by= user_data['user_id']
            device.modification_date= datetime.now(tz)
            
            UpdateData(device)
            return jsonify({'Response': "Success","Code":"200"})
        else:
            print("Rack ID or Site ID does not exists", file=sys.stderr)   
            return jsonify({'response': "Rack Id or Site Id does not Exists"}), 500  

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editBoards", methods = ['POST'])
@token_required
def EditBoards(user_data):    
    if True:#session.get('token', None):
        boardsObj = request.get_json()
        print(boardsObj,file = sys.stderr)
        boards = Board_Table.query.with_entities(Board_Table).filter_by(board_id=boardsObj["board_id"]).first()
        
        boards.tag_id = boardsObj['tag_id']          
        #boards.rfs_date = FormatStringDate(boardsObj['rfs_date'])
        #boards.item_code = boardsObj['item_code']
        #boards.item_desc = boardsObj['item_desc']
        boards.clei = boardsObj['clei']
        boards.status = boardsObj['status']
        #if boards.status != "Dismantle":
        boards.modification_date= datetime.now(tz)
        boards.modified_by= user_data['user_id']
        boards.dismantle_date= FormatStringDate(boardsObj['dismantle_date'])
        
        UpdateData(boards)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editSubBoards", methods = ['POST'])
@token_required
def EditSubBoards(user_data):    
    if True:#session.get('token', None):
        subBoardsObj = request.get_json()
        print(subBoardsObj,file = sys.stderr)
        subBoards = Subboard_Table.query.with_entities(Subboard_Table).filter_by(subboard_id=subBoardsObj["subboard_id"]).first()
        subBoards.tag_id = subBoardsObj['tag_id']          
        #subBoards.rfs_date = FormatStringDate(subBoardsObj['rfs_date'])
        #subBoards.item_code = subBoardsObj['item_code']
        #subBoards.item_desc = subBoardsObj['item_desc']
        subBoards.clei = subBoardsObj['clei']
        
        subBoards.status = subBoardsObj['status']
        #if subBoards.status != "Dismantle":
        subBoards.modified_by= user_data['user_id']
        subBoards.modification_date= datetime.now(tz)
        subBoards.dismantle_date = FormatStringDate(subBoardsObj['dismantle_date'])
        UpdateData(subBoards)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editSfps", methods = ['POST'])
@token_required
def EditSfps(user_data):    
    if True:#session.get('token', None):
        sfpsObj = request.get_json()
        print(sfpsObj,file = sys.stderr)
        sfps = SFP_Table.query.with_entities(SFP_Table).filter_by(sfp_id=sfpsObj["sfp_id"]).first()
        
        sfps.tag_id = sfpsObj['tag_id']          
        #sfps.rfs_date = FormatStringDate(sfpsObj['rfs_date'])
        #sfps.item_code = sfpsObj['item_code']
        #sfps.item_desc = sfpsObj['item_desc']
        sfps.clei = sfpsObj['clei']
        sfps.status = sfpsObj['status']
        
        #if sfps.status != "Dismantle":
        sfps.modification_date= datetime.now(tz)
        sfps.modified_by= user_data['user_id']
        sfps.dismantle_date = FormatStringDate(sfpsObj['dismantle_date'])

        UpdateData(sfps)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/editLicenses", methods = ['POST'])
@token_required
def EditLicenses(user_data):    
    if True:#session.get('token', None):
        licensesObj = request.get_json()
        print(licensesObj,file = sys.stderr)
        licenses = License_Table.query.with_entities(License_Table).filter_by(license_id=licensesObj["license_id"]).first()
        
        #licenses.item_code = licensesObj['item_code']
        #licenses.item_desc = licensesObj['item_desc']
        licenses.clei = licensesObj['clei']
        licenses.modification_date= datetime.now(tz)
        licenses.modified_by= user_data['user_id']
        licenses.dismantle_date = FormatStringDate(licensesObj['dismantle_date'])
        if 'status' in licensesObj:
            licenses.status=licensesObj['status']
        
        UpdateData(licenses)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/")
def hello():
    return "Mobily Network Management System"

@app.route("/getAllPhy", methods = ['GET'])
@token_required
def GetAllPhy(user_data):
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
        phyObjList=[]
        phyObjs = Phy_Table.query.all()

        for phyObj in phyObjs:

            phyDataDict= {}
            phyDataDict['site_id'] = phyObj.site_id
            phyDataDict['region'] = phyObj.region
            phyDataDict['site_name'] = phyObj.site_name
            phyDataDict['latitude'] = phyObj.latitude
            phyDataDict['longitude'] = phyObj.longitude
            phyDataDict['city'] = phyObj.city
            phyDataDict['creation_date'] = FormatDate(phyObj.creation_date)
            phyDataDict['modification_date'] = FormatDate(phyObj.modification_date)
            phyDataDict['status'] = phyObj.status
            phyDataDict['total_devices']=phyObj.total_count
            phyDataDict['created_by'] = phyObj.created_by
            phyDataDict['modified_by'] = phyObj.modified_by
            phyDataDict['site_type'] = phyObj.site_type
            #print(type(phyObj.creation_date), file=sys.stderr)

            phyObjList.append(phyDataDict)

        return jsonify(phyObjList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route("/getAllRacks", methods = ['GET'])
@token_required
def GetAllRack(user_data):
    """
        Get all Racks endpoint
        ---
        description: Get all Racks
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true
          
        responses:
            200:
                description: All Racks to be returned from inventory DB
                schema:
                    type: array
                    items:
                        type: object
                        properties:
                            rack_id:
                                type: integer
                            site_id:
                                type: string
                            rack_name:
                                type: string
                            serial_number:
                                type: string
                            manufactuer_date:
                                type: date
                                example: "2019-05-17"
                            unit_position:
                                type: number
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
                            rfs_date:
                                type: date
                                example: "2019-05-17"
                            height:
                                type: integer
                            width:
                                type: integer
                            depth:
                                type: integer
                            pn_code:
                                type: string
                            tag_id:
                                type: string
                            rack_model:
                                type: string
                            floor:
                                type: string
    """
    
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        rackObjList=[]
        rackObjs = Rack_Table.query.all()

        for rackObj in rackObjs:
            rackDataDict= {}
            rackDataDict['rack_id'] = rackObj.rack_id
            rackDataDict['site_id'] = rackObj.site_id
            rackDataDict['rack_name'] = rackObj.rack_name
            rackDataDict['serial_number'] = rackObj.serial_number
            rackDataDict['manufactuer_date'] = FormatDate(rackObj.manufactuer_date)
            rackDataDict['unit_position'] = rackObj.unit_position
            rackDataDict['creation_date'] = FormatDate(rackObj.creation_date)
            rackDataDict['modification_date'] = FormatDate(rackObj.modification_date)
            rackDataDict['status'] = rackObj.status
            rackDataDict['ru'] = rackObj.ru
            rackDataDict['rfs_date'] = FormatDate(rackObj.rfs_date)
            rackDataDict['height'] = rackObj.height
            rackDataDict['width'] = rackObj.width
            rackDataDict['depth'] = rackObj.depth
            rackDataDict['pn_code'] = rackObj.pn_code
            rackDataDict['tag_id'] = rackObj.tag_id
            rackDataDict['rack_model'] = rackObj.rack_model
            rackDataDict['floor'] = rackObj.floor
            rackDataDict['site_name'] = Phy_Table.query.with_entities(Phy_Table.site_name).filter_by(site_id=rackObj.site_id).first()[0]
            rackDataDict['total_devices'] = rackObj.total_count
            rackDataDict['created_by'] = rackObj.created_by
            rackDataDict['modified_by'] = rackObj.modified_by
            
            rackObjList.append(rackDataDict)

        return jsonify(rackObjList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllDevices", methods = ['GET'])
@token_required
def GetAllDevices(user_data):
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
                            item_code:
                                type: string
                            item_desc:
                                type: string
                            clei:
                                type: string
                            parent:
                                type: string
                            vuln_fix_plan_status:
                                type: string
                            vuln_ops_severity:
                                type: string
                            integrated_with_aaa:
                                type: string
                            integrated_with_paam:
                                type: string
                            approved_mbss:
                                type: string
                            mbss_implemented:
                                type: string
                            mbss_integration_check:
                                type: string
                            integrated_with_siem:
                                type: string
                            threat_cases:
                                type: string
                            vulnerability_scanning:
                                type: string
                            vulnerability_severity:
                                type: string                          
                            ims_status:
                                type: string
                            ims_function:
                                type: string          
                            
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        deviceObjList=[]
        deviceObjs = Device_Table.query.all()

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
            deviceDataDict['device_ru'] = deviceObj.ru
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
            deviceDataDict['item_code'] = deviceObj.item_code
            deviceDataDict['item_desc'] = deviceObj.item_desc
            deviceDataDict['clei'] = deviceObj.clei
            deviceDataDict['domain'] = deviceObj.domain
            deviceDataDict['ims_status'] = deviceObj.ims_status
            deviceDataDict['ims_function'] = deviceObj.ims_function
            deviceDataDict['parent'] = deviceObj.parent
            deviceDataDict['vuln_fix_plan_status'] = deviceObj.vuln_fix_plan_status
            deviceDataDict['vuln_ops_severity'] = deviceObj.vuln_ops_severity
            deviceDataDict['integrated_with_aaa'] = deviceObj.integrated_with_aaa
            deviceDataDict['integrated_with_paam'] = deviceObj.integrated_with_paam
            deviceDataDict['approved_mbss'] = deviceObj.approved_mbss
            deviceDataDict['mbss_implemented'] = deviceObj.mbss_implemented
            deviceDataDict['mbss_integration_check'] = deviceObj.mbss_integration_check
            deviceDataDict['integrated_with_siem'] = deviceObj.integrated_with_siem
            deviceDataDict['threat_cases'] = deviceObj.threat_cases
            deviceDataDict['vulnerability_scanning'] = deviceObj.vulnerability_scanning
            deviceDataDict['vulnerability_severity'] = deviceObj.vulnerability_severity
            deviceDataDict['created_by'] = deviceObj.created_by
            deviceDataDict['modified_by'] = deviceObj.modified_by
            if deviceObj.dismantle_date:
                deviceDataDict['dismantle_date'] = FormatDate(deviceObj.dismantle_date)
            #deviceDataDict['site_name'] = Phy_Table.query.with_entities(Phy_Table.site_name).filter_by(site_id=deviceObj.site_id).first()[0]
            #deviceDataDict['rack_name'] = Rack_Table.query.with_entities(Rack_Table.rack_name).filter_by(rack_id=deviceObj.rack_id).first()[0]
            
            deviceObjList.append(deviceDataDict)

        return jsonify(deviceObjList), 200
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllBoards", methods = ['GET'])
@token_required
def GetAllBoards(user_data):
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
                            item_code:
                                type: string
                            item_desc:
                                type: string
                            clei:
                                type: string
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        boardObjList=[]
        boardObjs = Board_Table.query.all()

        for boardObj in boardObjs:
            boardDataDict= {}
            boardDataDict['board_id'] = boardObj.board_id
            boardDataDict['device_id'] = boardObj.device_id
            boardDataDict['board_name'] = boardObj.board_name
            boardDataDict['device_slot_id'] = boardObj.device_slot_id
            boardDataDict['hardware_version'] = boardObj.hardware_version
            boardDataDict['software_version'] = boardObj.software_version
            boardDataDict['serial_number'] = boardObj.serial_number
            boardDataDict['manufactuer_date'] = FormatDate(boardObj.manufactuer_date)
            boardDataDict['creation_date'] = FormatDate(boardObj.creation_date)
            boardDataDict['modification_date'] = FormatDate(boardObj.modification_date)
            boardDataDict['status'] = boardObj.status
            boardDataDict['eos_date'] = FormatDate(boardObj.eos_date)
            boardDataDict['eol_date'] = FormatDate(boardObj.eol_date)
            boardDataDict['rfs_date'] = FormatDate(boardObj.rfs_date)
            boardDataDict['pn_code'] = boardObj.pn_code
            boardDataDict['tag_id'] = boardObj.tag_id
            boardDataDict['item_code'] = boardObj.item_code
            boardDataDict['item_desc'] = boardObj.item_desc
            boardDataDict['clei'] = boardObj.clei
            boardDataDict['created_by'] = boardObj.created_by
            boardDataDict['modified_by'] = boardObj.modified_by
            if boardObj.dismantle_date:
                boardDataDict['dismantle_date'] = FormatDate(boardObj.dismantle_date)
            

            # boardDataDict['device_ip'] = Device_Table.query.with_entities(Device_Table.ne_ip_address).filter_by(device_id=boardObj.device_id).first()
        
            boardObjList.append(boardDataDict)

        return jsonify(boardObjList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllSubboards", methods = ['GET'])
@token_required
def GetAllSubboards(user_data):
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
                            item_code:
                                type: string
                            item_desc:
                                type: string
                            clei:
                                type: string
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        subboardObjList=[]
        subboardObjs = Subboard_Table.query.all()

        for subboardObj in subboardObjs:
            subboardDataDict= {}
            subboardDataDict['subboard_id'] = subboardObj.subboard_id
            subboardDataDict['device_id'] = subboardObj.device_id
            subboardDataDict['subboard_name'] = subboardObj.subboard_name
            subboardDataDict['subboard_type'] = subboardObj.subboard_type
            subboardDataDict['subrack_id'] = subboardObj.subrack_id
            subboardDataDict['slot_number'] = subboardObj.slot_number
            subboardDataDict['hardware_version'] = subboardObj.hardware_version
            subboardDataDict['software_version'] = subboardObj.software_version
            subboardDataDict['serial_number'] = subboardObj.serial_number
            subboardDataDict['creation_date'] = FormatDate(subboardObj.creation_date)
            subboardDataDict['modification_date'] = FormatDate(subboardObj.modification_date)
            subboardDataDict['status'] = subboardObj.status
            subboardDataDict['eos_date'] = FormatDate(subboardObj.eos_date)
            subboardDataDict['eol_date'] = FormatDate(subboardObj.eol_date)
            subboardDataDict['rfs_date'] = FormatDate(subboardObj.rfs_date)
            subboardDataDict['tag_id'] = subboardObj.tag_id
            subboardDataDict['pn_code'] = subboardObj.pn_code
            subboardDataDict['item_code'] = subboardObj.item_code
            subboardDataDict['item_desc'] = subboardObj.item_desc
            subboardDataDict['clei'] = subboardObj.clei
            subboardDataDict['created_by'] = subboardObj.created_by
            subboardDataDict['modified_by'] = subboardObj.modified_by
            if subboardObj.dismantle_date:
                subboardDataDict['dismantle_date'] = FormatDate(subboardObj.dismantle_date)
            

            # subboardDataDict['device_ip'] = Device_Table.query.with_entities(Device_Table.ne_ip_address).filter_by(device_id=subboardObj.device_id).first()[0]
            
            subboardObjList.append(subboardDataDict)

        return jsonify(subboardObjList), 200
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllSfps", methods = ['GET'])
@token_required
def GetAllSFPS(user_data):
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
                            item_code:
                                type: string
                            item_desc:
                                type: string
                            clei:
                                type: string
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        sfpObjList=[]
        sfpObjs = SFP_Table.query.all()

        for sfpObj in sfpObjs:
            sfpDataDict= {}

            sfpDataDict['sfp_id'] = sfpObj.sfp_id
            sfpDataDict['device_id'] = sfpObj.device_id
            sfpDataDict['media_type'] = sfpObj.media_type
            sfpDataDict['port_name'] = sfpObj.port_name
            sfpDataDict['port_type'] = sfpObj.port_type
            sfpDataDict['connector'] = sfpObj.connector
            sfpDataDict['mode'] = sfpObj.mode
            sfpDataDict['speed'] = sfpObj.speed
            sfpDataDict['wavelength'] = sfpObj.wavelength
            sfpDataDict['manufacturer'] = sfpObj.manufacturer
            sfpDataDict['optical_direction_type'] = sfpObj.optical_direction_type
            sfpDataDict['pn_code'] = sfpObj.pn_code
            sfpDataDict['creation_date'] = FormatDate(sfpObj.creation_date)
            sfpDataDict['modification_date'] = FormatDate(sfpObj.modification_date)
            sfpDataDict['status'] = sfpObj.status
            sfpDataDict['eos_date'] = FormatDate(sfpObj.eos_date)
            sfpDataDict['eol_date'] = FormatDate(sfpObj.eol_date)
            sfpDataDict['rfs_date'] = FormatDate(sfpObj.rfs_date)
            sfpDataDict['tag_id'] = sfpObj.tag_id
            sfpDataDict['serial_number'] = sfpObj.serial_number
            sfpDataDict['item_code'] = sfpObj.item_code
            sfpDataDict['item_desc'] = sfpObj.item_desc
            sfpDataDict['clei'] = sfpObj.clei
            sfpDataDict['created_by'] = sfpObj.created_by
            sfpDataDict['modified_by'] = sfpObj.modified_by
            if sfpObj.dismantle_date:
                sfpDataDict['dismantle_date'] = FormatDate(sfpObj.dismantle_date)
            

            # sfpDataDict['device_ip'] = Device_Table.query.with_entities(Device_Table.ne_ip_address).filter_by(device_id=sfpObj.device_id).first()[0]

            sfpObjList.append(sfpDataDict)

        return jsonify(sfpObjList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllLicenses", methods = ['GET'])
@token_required
def GetAllLicences(user_data):
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
                            item_code:
                                type: string
                            item_desc:
                                type: string
                            clei:
                                type: string
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        licenseObjList=[]
        licenseObjs = License_Table.query.all()

        for licenseObj in licenseObjs:
            licenseDataDict= {}

            licenseDataDict['license_id'] = licenseObj.license_id
            licenseDataDict['license_name'] = licenseObj.license_name
            licenseDataDict['license_description'] = licenseObj.license_description
            licenseDataDict['ne_name'] = licenseObj.ne_name
            licenseDataDict['rfs_date'] = licenseObj.rfs_date
            licenseDataDict['activation_date'] = licenseObj.activation_date
            licenseDataDict['expiry_date'] = licenseObj.expiry_date
            licenseDataDict['grace_period'] = licenseObj.grace_period
            licenseDataDict['serial_number'] = licenseObj.serial_number
            licenseDataDict['creation_date'] = FormatDate(licenseObj.creation_date)
            licenseDataDict['modification_date'] = FormatDate(licenseObj.modification_date)
            licenseDataDict['status'] = licenseObj.status
            licenseDataDict['tag_id'] = licenseObj.tag_id
            licenseDataDict['capacity'] = licenseObj.capacity
            licenseDataDict['usage'] = licenseObj.usage
            licenseDataDict['pn_code'] = licenseObj.pn_code
            licenseDataDict['item_code'] = licenseObj.item_code
            licenseDataDict['item_desc'] = licenseObj.item_desc
            licenseDataDict['clei'] = licenseObj.clei
            licenseDataDict['created_by'] = licenseObj.created_by
            licenseDataDict['modified_by'] = licenseObj.modified_by
            if licenseObj.dismantle_date:
                licenseDataDict['dismantle_date'] = FormatDate(licenseObj.dismantle_date)
            
            licenseObjList.append(licenseDataDict)

        return jsonify(licenseObjList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addDevice", methods = ['POST'])
@token_required
def AddSeedDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        seedObj = request.get_json()

        print(seedObj,file=sys.stderr)
        if Phy_Table.query.with_entities(Phy_Table.site_id).filter_by(site_id=seedObj['site_id']).first() != None and Rack_Table.query.with_entities(Rack_Table.rack_id).filter_by(rack_id=seedObj['rack_id']).first() != None:
            seed = Seed()
            seed.site_id = seedObj['site_id']
            rack=""
            rack= str(seedObj['rack_id'])
            if rack:
                rack= rack.split('|')
                rack=rack[0]
            seed.rack_id = rack
            '''
            seed.region = seedObj['region']
            seed.site_name = seedObj['site_name']
            seed.latitude = seedObj['latitude']
            seed.longitude = seedObj['longitude']
            seed.city = seedObj['city']
            seed.datacentre_status = seedObj['datacentre_status']
            '''
            
            '''
            seed.floor = seedObj['floor']
            seed.rack_name = seedObj['rack_name']
            seed.serial_number = seedObj['serial_number']
            seed.manufactuer_date = FormatStringDate(seedObj['manufactuer_date'])
            seed.unit_position = seedObj['unit_position']
            seed.rack_status = seedObj['rack_status']
            if isinstance(seedObj['ru'],int ):
                seed.ru = seedObj['ru']
            else:
                seed.ru = 0
            seed.rfs_date = FormatStringDate(seedObj['rfs_date'])
            if isinstance(seedObj['height'],int ):
                seed.height = seedObj['height']
            else:
                seed.height = 0
            if isinstance(seedObj['width'],int ):
                seed.width = seedObj['width']
            else:
                seed.width = 0
            if isinstance(seedObj['depth'],int ):
                seed.depth = seedObj['depth']
            else:
                seed.depth = 0
            seed.pn_code = seedObj['pn_code']
            
            seed.rack_model = seedObj['rack_model']
            '''
            seed.tag_id = seedObj['tag_id']
            if 'rfs_date' in seedObj:
                seed.rfs_date = FormatStringDate(seedObj['rfs_date'])
            
            seed.device_id = seedObj['device_id']
            seed.ne_ip_address = seedObj['ne_ip_address']
            if str(seedObj['device_ru']).isdigit():
                seed.device_ru = seedObj['device_ru']
            else:
                seed.device_ru = 0 
            #seed.department = seedObj['department']
            #seed.section = seedObj['section']
            seed.criticality = seedObj['criticality']
            seed.function = seedObj['function']
            seed.cisco_domain = seedObj['cisco_domain']
            seed.virtual = seedObj['virtual']
            seed.authentication = seedObj['authentication']
            seed.subrack_id_number = seedObj['subrack_id_number'] 
            seed.hostname = seedObj['hostname']
            seed.site_type = seedObj['site_type'] 
            if 'sw_type' in seedObj:
                seed.sw_type = seedObj['sw_type']
            else:
                seed.sw_type = 'N/A'
            if 'vendor' in seedObj:
                seed.vendor = seedObj['vendor']
            if 'asset_type' in seedObj:
                seed.asset_type = seedObj['asset_type']
            else:
                seed.asset_type = 'N/A'
            if 'operation_status' in seedObj:
                seed.operation_status = seedObj['operation_status']

            seed.contract_number = seedObj['contract_number']
            seed.contract_expiry = FormatStringDate(seedObj['contract_expiry'])

            if 'item_code' in seedObj:
                seed.item_code = seedObj['item_code']
            if 'item_desc' in seedObj:
                seed.item_desc = seedObj['item_desc']
            if 'clei' in seedObj:
                seed.clei = seedObj['clei']
            
            if 'parent' in seedObj:
                seed.parent = seedObj['parent']
            
            # if 'vuln_fix_plan_status' in seedObj:
            #     seed.vuln_fix_plan_status = seedObj['vuln_fix_plan_status']

            #if 'vuln_ops_severity' in seedObj:
            #    seed.vuln_ops_severity = seedObj['vuln_ops_severity']
            
            if 'integrated_with_aaa' in seedObj:
                seed.integrated_with_aaa = seedObj['integrated_with_aaa']
            if 'integrated_with_paam' in seedObj:
                seed.integrated_with_paam = seedObj['integrated_with_paam']

            if 'approved_mbss' in seedObj:
                seed.approved_mbss = seedObj['approved_mbss']
            if 'mbss_implemented' in seedObj:
                seed.mbss_implemented = seedObj['mbss_implemented']

            if 'mbss_integration_check' in seedObj:
                seed.mbss_integration_check = seedObj['mbss_integration_check']
            if 'integrated_with_siem' in seedObj:
                seed.integrated_with_siem = seedObj['integrated_with_siem']

            if 'threat_cases' in seedObj:
                seed.threat_cases = seedObj['threat_cases']
            if 'vulnerability_scanning' in seedObj:
                seed.vulnerability_scanning = seedObj['vulnerability_scanning']

            if 'vulnerability_severity' in seedObj:
                seed.vulnerability_severity = seedObj['vulnerability_severity']
            
            try:
                
                domainsnObj = DOMAINS_TABLE.query.filter_by(cisco_domain=seed.cisco_domain).first() 
                if domainsnObj:
                    seed.department= domainsnObj.department
                    seed.section= domainsnObj.section    
            except Exception as e:
                print(f"Exception Occured in Getting Domains Information {e}", file=sys.stderr)


            if Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first() is not None:
                seed.seed_id = Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first()[0]
                print("Updated " + seedObj['ne_ip_address'],file=sys.stderr)
                seed.modified_by= user_data['user_id']
                UpdateData(seed)
            else:
                print("Inserted " +seedObj['ne_ip_address'],file=sys.stderr)
                seed.onboard_status = 'false'
                seed.created_by= user_data['user_id']
                seed.modified_by= user_data['user_id']
                InsertData(seed)
                    
            return jsonify({'response': "success","code":"200"})

        else:
            print("Rack ID or Site ID does not exists", file=sys.stderr)   
            return jsonify({'response': "Rack Id or Site Id does not Exists"}), 500  

    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/addSeed", methods = ['POST'])
@token_required
def AddSeed(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        failed=False
        postData = request.get_json()

        print(postData,file=sys.stderr)

        for seedObj in postData:

            if Phy_Table.query.with_entities(Phy_Table.site_id).filter_by(site_id=seedObj['site_id']).first()!= None and Rack_Table.query.with_entities(Rack_Table.rack_id).filter_by(rack_id=seedObj['rack_id']).first() != None:
                seed = Seed()
                if 'site_id' in seedObj:
                    seed.site_id = seedObj['site_id']
                '''
                if 'region' in seedObj:
                    seed.region = seedObj['region']
                if 'site_name' in seedObj:
                    seed.site_name = seedObj['site_name']
                else:
                    seed.site_name = 'N/A'
                if 'latitude' in seedObj:
                    seed.latitude = seedObj['latitude']
                if 'longitude' in seedObj:
                    seed.longitude = seedObj['longitude']
                if 'city' in seedObj:
                    seed.city = seedObj['city']
                
                if 'datacentre_status' in seedObj:
                    seed.datacentre_status = seedObj['datacentre_status']
                '''
                
                
                if 'rack_id' in seedObj:
                    rack= str(seedObj['rack_id'])
                    rack= rack.split('|')
                    rack=rack[0]
                    seed.rack_id = rack
                '''
                if 'floor' in seedObj:
                    seed.floor = seedObj['floor']
                
                if 'rack_name' in seedObj:
                    seed.rack_name = seedObj['rack_name']
                else:
                    seed.rack_name = 'N/A'
                if 'serial_number' in seedObj:
                    seed.serial_number = seedObj['serial_number']
                if 'manufactuer_date' in seedObj:
                    seed.manufactuer_date = FormatStringDate(seedObj['manufactuer_date'])
                if 'unit_position' in seedObj:
                    seed.unit_position = seedObj['unit_position']
                if 'rack_status' in seedObj:
                    seed.rack_status = seedObj['rack_status']
                if 'ru' in seedObj:
                    seed.ru = seedObj['ru']
                
                if 'height' in seedObj:
                    seed.height = seedObj['height']
                if 'width' in seedObj:
                    seed.width = seedObj['width']
                if 'depth' in seedObj:
                    seed.depth = seedObj['depth']
                if 'pn_code' in seedObj:
                    seed.pn_code = seedObj['pn_code']
                
                if 'rack_model' in seedObj:
                    seed.rack_model = seedObj['rack_model']
                '''
                if 'tag_id' in seedObj:
                    seed.tag_id = seedObj['tag_id']
                
                #if 'rfs_date' in seedObj:
                seed.rfs_date = FormatStringDate(seedObj['rfs_date'])

                seed.device_id = seedObj['device_id']
                seed.ne_ip_address = seedObj['ne_ip_address']
                if 'device_ru' in seedObj:
                    seed.device_ru = seedObj['device_ru']
                #if 'department' in seedObj:
                #    seed.department = seedObj['department']
                #if 'section' in seedObj:
                #    seed.section = seedObj['section']
                if 'criticality' in seedObj:
                    seed.criticality = seedObj['criticality']
                if 'function' in seedObj:
                    seed.function = seedObj['function']
                if 'cisco_domain' in seedObj:
                    seed.cisco_domain = seedObj['cisco_domain']
                if 'virtual' in seedObj:
                    seed.virtual = seedObj['virtual']
                if 'authentication' in seedObj:
                    seed.authentication = seedObj['authentication']
                if 'subrack_id_number' in seedObj:
                    seed.subrack_id_number = seedObj['subrack_id_number'] 
                if 'hostname' in seedObj:
                    seed.hostname = seedObj['hostname'] 
                if 'site_type' in seedObj:
                    seed.site_type = seedObj['site_type'] 
                if 'sw_type' in seedObj:
                    seed.sw_type = seedObj['sw_type']
                else:
                    seed.sw_type = 'N/A'
                if 'vendor' in seedObj:
                    seed.vendor = seedObj['vendor']
                if 'asset_type' in seedObj:
                    seed.asset_type = seedObj['asset_type']
                else:
                    seed.asset_type = 'N/A'
                if 'operation_status' in seedObj:
                    seed.operation_status = seedObj['operation_status']

                if 'contract_number' in seedObj:
                    seed.contract_number = seedObj['contract_number']

                if 'contract_expiry' in seedObj:
                    seed.contract_expiry = FormatStringDate(seedObj['contract_expiry'])
                
                if 'item_code' in seedObj:
                    seed.item_code = seedObj['item_code']
                if 'item_desc' in seedObj:
                    seed.item_desc = seedObj['item_desc']
                if 'clei' in seedObj:
                    seed.clei = seedObj['clei']
                if 'parent' in seedObj:
                    seed.parent = seedObj['parent']
                # if 'vuln_fix_plan_status' in seedObj:
                #     seed.vuln_fix_plan_status = seedObj['vuln_fix_plan_status']
                if 'vuln_ops_severity' in seedObj:
                    seed.vuln_ops_severity = seedObj['vuln_ops_severity']
                
                if 'integrated_with_aaa' in seedObj:
                    if not seedObj['integrated_with_aaa']:
                        seed.integrated_with_aaa = "Yes"
                    seed.integrated_with_aaa = seedObj['integrated_with_aaa']
                    
                else:
                    seed.integrated_with_aaa = "Yes"
                
                if 'integrated_with_paam' in seedObj:
                    if not seedObj['integrated_with_paam']:
                        seed.integrated_with_paam = "Yes"
                    seed.integrated_with_paam = seedObj['integrated_with_paam']
                else:
                    seed.integrated_with_paam = "NA"
                
                if 'approved_mbss' in seedObj:
                    if not seedObj['approved_mbss']:
                        seed.approved_mbss = "Yes"
                    seed.approved_mbss = seedObj['approved_mbss']
                else:
                    seed.approved_mbss = "Yes"

                if 'mbss_implemented' in seedObj:
                    if not seedObj['mbss_implemented']:
                        seed.mbss_implemented = "Yes"
                    seed.mbss_implemented = seedObj['mbss_implemented']
                else:
                    seed.mbss_implemented = "Yes"

                if 'mbss_integration_check' in seedObj:
                    if not seedObj['mbss_integration_check']:
                        seed.mbss_integration_check = "Yes"
                    seed.mbss_integration_check = seedObj['mbss_integration_check']
                else:
                    seed.mbss_integration_check = "Yes"

                if 'integrated_with_siem' in seedObj:
                    if not seedObj['integrated_with_siem']:
                        seed.integrated_with_siem = "Yes"
                    seed.integrated_with_siem = seedObj['integrated_with_siem']
                else:
                    seed.integrated_with_siem = "Yes"

                if 'threat_cases' in seedObj:
                    if not seedObj['threat_cases']:
                        seed.threat_cases = "Yes"
                    seed.threat_cases = seedObj['threat_cases']
                else:
                    seed.threat_cases = "Yes"

                if 'vulnerability_scanning' in seedObj:
                    if seedObj['vulnerability_scanning']:
                        seed.vulnerability_scanning = "Yes"
                    seed.vulnerability_scanning = seedObj['vulnerability_scanning']
                else:
                    seed.vulnerability_scanning = "Yes"

                if 'vulnerability_severity' in seedObj:
                    if not seedObj['vulnerability_severity']:
                        seed.vulnerability_severity = "Yes"
                    seed.vulnerability_severity = seedObj['vulnerability_severity']
                else:
                    seed.vulnerability_severity = ""
            
                try:
                
                    domainsnObj = DOMAINS_TABLE.query.filter_by(cisco_domain=seed.cisco_domain).first() 
                    if domainsnObj:
                        seed.department= domainsnObj.department
                        seed.section= domainsnObj.section
                   
                except Exception as e:
                    print(f"Exception Occured in Getting Domains Information {e}", file=sys.stderr)

                

                seed.onboard_status='False'
            
                
                if Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first() is not None:
                    seed.seed_id = Seed.query.with_entities(Seed.seed_id).filter_by(ne_ip_address=seedObj['ne_ip_address']).first()[0]
                    print("Updated " + seedObj['ne_ip_address'],file=sys.stderr)
                    seed.modified_by= user_data['user_id']
                    UpdateData(seed)
                else:
                    print("Inserted " +seedObj['ne_ip_address'],file=sys.stderr)
                    seed.onboard_status = 'false'
                    seed.created_by= user_data['user_id']
                    seed.modified_by= user_data['user_id']
                    InsertData(seed)

            else:
                print("Rack ID or Site ID does not exists", file=sys.stderr)   
                failed= True
                    
        if failed:
            return jsonify({'response': "Rack Id or Site Id does not Exists for some devices",}), 500 
        else:
            return jsonify({'response': "success","code":"200"})

        
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
    
@app.route("/getSeeds", methods = ['GET'])
@token_required
def GetAllSeed(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        seedObjList=[]
        seedObjs = Seed.query.all()

        for seedObj in seedObjs:

            seedDataDict= {}
            seedDataDict['seed_id'] = seedObj.seed_id
            seedDataDict['site_id'] = seedObj.site_id
            '''
            seedDataDict['region'] = seedObj.region
            seedDataDict['site_name'] = seedObj.site_name
            seedDataDict['latitude'] = seedObj.latitude
            seedDataDict['longitude'] = seedObj.longitude
            seedDataDict['city'] = seedObj.city
            seedDataDict['datacentre_status'] = seedObj.datacentre_status
            '''
            seedDataDict['rack_id'] = seedObj.rack_id
            '''
            seedDataDict['floor'] = seedObj.floor
            seedDataDict['rack_name'] = seedObj.rack_name
            seedDataDict['serial_number'] = seedObj.serial_number
            seedDataDict['manufactuer_date'] = FormatDate(seedObj.manufactuer_date)
            seedDataDict['unit_position'] = seedObj.unit_position
            seedDataDict['rack_status'] = seedObj.rack_status
            seedDataDict['ru'] = seedObj.ru
            
            seedDataDict['height'] = seedObj.height
            seedDataDict['width'] = seedObj.width
            seedDataDict['depth'] = seedObj.depth
            seedDataDict['pn_code'] = seedObj.pn_code
            seedDataDict['tag_id'] = seedObj.tag_id
            seedDataDict['rack_model'] = seedObj.rack_model
            '''
            seedDataDict['tag_id'] = seedObj.tag_id
            #print(f" ####################  {type(seedObj.rfs_date)}    {seedObj.rfs_date}  {seedObj.ne_ip_address}", file=sys.stderr)
            seedDataDict['rfs_date'] = FormatDate(seedObj.rfs_date)
            seedDataDict['device_id'] = seedObj.device_id
            seedDataDict['ne_ip_address'] = seedObj.ne_ip_address
            seedDataDict['device_ru'] = seedObj.device_ru
            seedDataDict['department'] = seedObj.department
            seedDataDict['section'] = seedObj.section
            seedDataDict['criticality'] = seedObj.criticality
            seedDataDict['function'] = seedObj.function
            seedDataDict['cisco_domain'] = seedObj.cisco_domain
            seedDataDict['virtual'] = seedObj.virtual
            seedDataDict['authentication'] = seedObj.authentication
            seedDataDict['subrack_id_number'] = seedObj.subrack_id_number
            seedDataDict['hostname'] = seedObj.hostname
            seedDataDict['site_type'] = seedObj.site_type   
            seedDataDict['sw_type'] = seedObj.sw_type
            seedDataDict['vendor'] = seedObj.vendor
            seedDataDict['asset_type'] = seedObj.asset_type
            seedDataDict['operation_status'] = seedObj.operation_status
            seedDataDict['onboard_status'] = seedObj.onboard_status
            seedDataDict['contract_number'] = seedObj.contract_number
            seedDataDict['contract_expiry'] = FormatDate(seedObj.contract_expiry)
            # seedDataDict['item_code'] = seedObj.item_code
            # seedDataDict['item_desc'] = seedObj.item_desc
            seedDataDict['clei'] = seedObj.clei
            seedDataDict['parent'] = seedObj.parent
            seedDataDict['vuln_fix_plan_status'] = seedObj.vuln_fix_plan_status
            seedDataDict['vuln_ops_severity'] = seedObj.vuln_ops_severity
            seedDataDict['integrated_with_aaa'] = seedObj.integrated_with_aaa
            seedDataDict['integrated_with_paam'] = seedObj.integrated_with_paam
            seedDataDict['approved_mbss'] = seedObj.approved_mbss
            seedDataDict['mbss_implemented'] = seedObj.mbss_implemented
            seedDataDict['mbss_integration_check'] = seedObj.mbss_integration_check
            seedDataDict['integrated_with_siem'] = seedObj.integrated_with_siem
            seedDataDict['threat_cases'] = seedObj.threat_cases
            seedDataDict['vulnerability_scanning'] = seedObj.vulnerability_scanning
            seedDataDict['vulnerability_severity'] = seedObj.vulnerability_severity
            seedDataDict['created_by'] = seedObj.created_by
            seedDataDict['modified_by'] = seedObj.modified_by
            
                
            seedObjList.append(seedDataDict)

        content = gzip.compress(json.dumps(seedObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/getSeed/<seed>', methods = ['POST'])
def GetSeed(ip_addr):
    if request.headers.get('X-Auth-Key') == session.get('token', None):
        seedObj = db.session.query(Seed).filter_by(ne_ip_address=ip_addr).first()
        
        seedDataDict= {}
        seedDataDict['seed_id'] = seedObj.seed_id
        
        seedDataDict['site_id'] = seedObj.site_id
        '''
        seedDataDict['region'] = seedObj.region
        seedDataDict['site_name'] = seedObj.site_name
        seedDataDict['latitude'] = seedObj.latitude
        seedDataDict['longitude'] = seedObj.longitude
        seedDataDict['city'] = seedObj.city
        seedDataDict['datacentre_status'] = seedObj.datacentre_status
        '''
        seedDataDict['rack_id'] = seedObj.rack_id
        '''
        seedDataDict['floor'] = seedObj.floor
        seedDataDict['rack_name'] = seedObj.rack_name
        seedDataDict['serial_number'] = seedObj.serial_number
        seedDataDict['manufactuer_date'] = FormatDate(seedObj.manufactuer_date)
        seedDataDict['unit_position'] = seedObj.unit_position
        seedDataDict['rack_status'] = seedObj.rack_status
        seedDataDict['ru'] = seedObj.ru
        seedDataDict['rfs_date'] = FormatDate(seedObj.rfs_date)
        seedDataDict['height'] = seedObj.height
        seedDataDict['width'] = seedObj.width
        seedDataDict['depth'] = seedObj.depth
        seedDataDict['pn_code'] = seedObj.pn_code
        seedDataDict['tag_id'] = seedObj.tag_id
        seedDataDict['rack_model'] = seedObj.rack_model
        '''
        seedDataDict['device_id'] = seedObj.device_id
        seedDataDict['ne_ip_address'] = seedObj.ne_ip_address
        seedDataDict['device_ru'] = seedObj.device_ru
        seedDataDict['department'] = seedObj.department
        seedDataDict['section'] = seedObj.section
        seedDataDict['criticality'] = seedObj.criticality
        seedDataDict['function'] = seedObj.function
        seedDataDict['cisco_domain'] = seedObj.cisco_domain
        seedDataDict['virtual'] = seedObj.virtual
        seedDataDict['authentication'] = seedObj.authentication
        seedDataDict['subrack_id_number'] = seedObj.subrack_id_number
        seedDataDict['hostname'] = seedObj.hostname
        seedDataDict['site_type'] = seedObj.site_type
        seedDataDict['sw_type'] = seedObj.sw_type
        seedDataDict['vendor'] = seedObj.vendor
        seedDataDict['asset_type'] = seedObj.asset_type
        seedDataDict['operation_status'] = seedObj.operation_status
        seedDataDict['onboard_status'] = seedObj.onboard_status
        seedDataDict['contract_number'] = seedObj.contract_number
        seedDataDict['contract_expiry'] = FormatDate(seedObj.contract_expiry)
        seedDataDict['item_code'] = seedObj.item_code
        seedDataDict['item_desc'] = seedObj.item_desc
        seedDataDict['clei'] = seedObj.clei


        return jsonify(seedDataDict), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/onBoardDevice", methods = ['POST'])
@token_required
def OnBoardDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        devObj = {
            'IOS' : [],
            'IOS-XR' : [],
            'IOS-XE' : [],
            'NX-OS' : [],
            'APIC':[],
            'NX-OS ACI' : [],
            'WLC' : [],
            'PRIME':[],
            'UCS':[],
            'A10':[],
            'APIC-SYS':[],
            'UCS-SYS':[],
            'Infoblox':[],
            'Arista':[],
            'WireFilter':[],
            'IPT-UCS':[],
            'IPT-ESXI':[],
            'Arbor':[],
            'IPT':[],
            'IPT-ROUTER':[],
            'Arbor-Sec' :[],
            'Fortinet-Sec' :[],
            'Juniper-Sec' :[],
            'Juniper-Screenos' :[],
            'ASA-SOC':[],
            'ASA96':[],
            'PaloAlto':[],
            'PulseSecure':[],
            'Symantec':[],
            'FireEye':[],
            'FirepowerServer':[],
            'SYS-ESXI':[],
            'UCS-CIMC':[]
        }
        

        postData = request.get_json()
        print('Started at: '+datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S'),file=sys.stderr)

        
        for ip in postData:

            obj = Seed.query.filter_by(ne_ip_address=ip).first()

            obj.sw_type = obj.sw_type.rstrip()
            if obj.sw_type in devObj:
                
                objDict = {}
                objDict['ip'] = ip
                objDict['asset_type'] = obj.asset_type
                
                if obj.sw_type=='PRIME':
                    objDict['asset_type'] = 'PRIME_UCS_EDN'
                    
                elif obj.sw_type=='UCS':
                    objDict['asset_type'] = 'PRIME_UCS_EDN'
                    
                elif obj.sw_type=='A10':
                    objDict['asset_type'] = 'SYSTEMS'

                elif obj.sw_type=='WLC':
                    objDict['asset_type'] = 'WLC'
                   
                elif obj.sw_type=='APIC-SYS':
                    objDict['asset_type'] = 'SYSTEMS'
                    
                elif obj.sw_type=='UCS-SYS':
                    objDict['asset_type'] = 'SYSTEMS'

                elif obj.sw_type=='UCS-CIMC':
                    objDict['asset_type'] = 'SYSTEMS'

                elif obj.sw_type=='Infoblox':
                    objDict['asset_type'] = 'SYSTEMS'
                
                elif obj.sw_type=='Arista':
                    objDict['asset_type'] = 'SYSTEMS'
                
                elif obj.sw_type=='Arbor':
                    objDict['asset_type'] = 'SYSTEMS'
                    
                elif obj.sw_type=='ASA-SOC':
                    objDict['asset_type'] = 'ASA-SOC'
                
                elif obj.sw_type=='ASA96':
                    objDict['asset_type'] = 'ASA96'
                
                elif obj.sw_type=='PaloAlto':
                    objDict['asset_type'] = 'PaloAlto' 
                
                elif obj.sw_type=='PulseSecure':
                    objDict['asset_type'] = 'PulseSecure'
                    
                elif obj.sw_type=='WireFilter':
                    objDict['asset_type'] = 'WireFilter'
                    objDict['device_name']= obj.hostname

                elif obj.sw_type=='Arbor-Sec':
                    objDict['asset_type'] = 'Arbor-Sec'
                    objDict['device_name']= obj.hostname

                elif obj.sw_type=='Fortinet-Sec':
                    objDict['asset_type'] = 'Fortinet-Sec'
                    objDict['device_name']= obj.hostname
                    
                elif obj.sw_type=='Juniper-Sec':
                    objDict['asset_type'] = 'Juniper-Sec'
                    objDict['device_name']= obj.hostname
                
                elif obj.sw_type=='Juniper-Screenos':
                    objDict['asset_type'] = 'Juniper-Screenos'

                elif obj.sw_type=='Symantec':
                    objDict['sw_type'] = 'Symantec'
                    objDict['device_name']= obj.hostname
                    
                elif obj.sw_type=='FireEye':
                    objDict['sw_type'] = 'FireEye'
                    objDict['device_name']= obj.hostname
                
                elif obj.sw_type=='SYS-ESXI':
                    objDict['sw_type'] = 'SYS-ESXI'
                    
                elif obj.sw_type=='FirepowerServer':
                    objDict['sw_type'] = 'FirepowerServer'
                    objDict['device_name']= obj.hostname
                
                elif obj.sw_type=='Firepower-SSH':
                    objDict['sw_type'] = 'Firepower-SSH'
                     
                elif obj.sw_type=='IPT':
                    print(obj.function.rstrip(), file=sys.stderr)
                    objDict['function']= obj.function.rstrip()
                    
                    if obj.function == 'ESXi Hypervisor':
                        print(f"value of function is {obj.function}", file=sys.stderr)
                        objDict['sw_type'] = 'IPT-ESXI'
                        devObj['IPT-ESXI'].append(objDict)
                        continue

                    elif obj.function == 'UCS Server CIMC':
                        print(f"value of function is {obj.function}", file=sys.stderr)
                        objDict['sw_type'] = 'IPT-UCS'
                        devObj['IPT-UCS'].append(objDict)
                        continue
                    
                    elif obj.function == 'ROUTER':
                        print(f"value of function is {obj.function}", file=sys.stderr)
                        objDict['sw_type'] = 'IPT-ROUTER'
                        devObj['IPT-ROUTER'].append(objDict)
                        continue
                    
                    else:
                        print("else", file=sys.stderr)
                        continue
                            
                devObj[obj.sw_type].append(objDict)
            
        print(devObj,file=sys.stderr)
        racks_error=False
        for key in devObj:
            if len(devObj[key]) !=0:
                hosts = CreatePullersDictList(devObj[key])
                
                ### Get Data from pullers
                pullerData = GetDatafromPullers(hosts,key)

                ### Get Data from sample file
                # pullerData = json.load(open('temp/sample.json',)
                
                racks_error= InsertInventoryData(pullerData, user_data)
        
        if racks_error:
            return jsonify({'response': "Rack Id or Site Id does not Exists for some devices"}), 500 
        else:
            return jsonify({'response': "success","code":"200"})
            
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllOnBoardDevices", methods = ['GET'])
@token_required
def GetAllOnBoardDevices(user_data):
    """
        Get all OnboardedDevices endpoint
        ---
        description: Get all OnboardedDevices
        responses:
            200:
                description: All Devices from inventory DB where status is production
                schema:
                    type: array
                    items:
                        type: object
                        properties:
                            site_name:
                                type: string
                            region:
                                type: string
                            city:
                                type: string
                            rack_name:
                                type: string
                            device_id:
                                type: integer
                            site_id:
                                type: integer
                            rack_id:
                                type: integer
                            ne_ip_address:
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
                                type: string
                                example: "2019-05-17 12:12:12"
                            hw_eol_date:
                                type: string
                                example: "2019-05-17 12:12:12"
                            sw_eos_date:
                                type: string
                                example: "2019-05-17 12:12:12"
                            sw_eol_date:
                                type: string
                                example: "2019-05-17 12:12:12"
                            virtual:
                                type: string
                            rfs_date:
                                type: string
                                example: "2019-05-17 12:12:12"
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
                                type: string
                                example: "2019-05-17 12:12:12"
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
                                type: string
                                example: "2019-05-17"
                            item_code:
                                type: string
                            item_desc:
                                type: string
                            clei:
                                type: string
                            parent:
                                type: string
                            integrated_with_aaa:
                                type: string
                            integrated_with_paam:
                                type: string
                            approved_mbss:
                                type: string
                            mbss_implemented:
                                type: string
                            mbss_integration_check:
                                type: string
                            integrated_with_siem:
                                type: string
                            threat_cases:
                                type: string
                            vulnerability_scanning:
                                type: string
                            vulnerability_severity:
                                type: string
                            vuln_fix_plan_status:
                                type: string
                            vuln_ops_severity:
                                type: string
                            ims_status:
                                type: string
                            ims_function:
                                type: string
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        onBoardedDeviceList=[]
        deviceObjs = Device_Table.query.filter(Device_Table.status!='Dismantle').all()
        print("Fetching Onboarded devices", file=sys.stderr)
        for deviceObj in deviceObjs:
            #print(deviceObj.ne_ip_address,file=sys.stderr)

            phyObj = db.session.query(Phy_Table).filter_by(site_id=deviceObj.site_id).first()
            rackObj = db.session.query(Rack_Table).filter_by(rack_id=deviceObj.rack_id).first()

            onBoardedDeviceDict= {}

            #onBoardedDeviceDict['site_name'] = phyObj.site_name
            #onBoardedDeviceDict['region'] = phyObj.region
            #onBoardedDeviceDict['city'] = phyObj.city

            #onBoardedDeviceDict['rack_name'] = rackObj.rack_name

            onBoardedDeviceDict['device_id'] = deviceObj.device_id
            onBoardedDeviceDict['site_id'] = deviceObj.site_id
            onBoardedDeviceDict['rack_id'] = deviceObj.rack_id
            onBoardedDeviceDict['ne_ip_address'] = deviceObj.ne_ip_address
            onBoardedDeviceDict['device_name'] = deviceObj.device_name
            onBoardedDeviceDict['software_version'] = deviceObj.software_version
            onBoardedDeviceDict['patch_version'] = deviceObj.patch_version
            
            onBoardedDeviceDict['creation_date'] = FormatDate(deviceObj.creation_date)
            onBoardedDeviceDict['modification_date'] = FormatDate(deviceObj.modification_date)

            onBoardedDeviceDict['status'] = deviceObj.status
            onBoardedDeviceDict['device_ru'] = deviceObj.ru
            onBoardedDeviceDict['department'] = deviceObj.department
            onBoardedDeviceDict['section'] = deviceObj.section
            onBoardedDeviceDict['criticality'] = deviceObj.criticality
            onBoardedDeviceDict['function'] = deviceObj.function
            onBoardedDeviceDict['cisco_domain'] = deviceObj.cisco_domain
            onBoardedDeviceDict['manufacturer'] = deviceObj.manufacturer
            onBoardedDeviceDict['hw_eos_date'] = FormatDate(deviceObj.hw_eos_date)
            onBoardedDeviceDict['hw_eol_date'] = FormatDate(deviceObj.hw_eol_date)
            onBoardedDeviceDict['sw_eos_date'] = FormatDate(deviceObj.sw_eos_date)
            onBoardedDeviceDict['sw_eol_date'] = FormatDate(deviceObj.sw_eol_date)
            onBoardedDeviceDict['virtual'] = deviceObj.virtual
            onBoardedDeviceDict['rfs_date'] = FormatDate(deviceObj.rfs_date)
            onBoardedDeviceDict['authentication'] = deviceObj.authentication
            onBoardedDeviceDict['serial_number'] = deviceObj.serial_number
            onBoardedDeviceDict['pn_code'] = deviceObj.pn_code
            onBoardedDeviceDict['tag_id'] = deviceObj.tag_id
            onBoardedDeviceDict['subrack_id_number'] = deviceObj.subrack_id_number
            onBoardedDeviceDict['manufactuer_date'] = FormatDate(deviceObj.manufactuer_date)
            onBoardedDeviceDict['hardware_version'] = deviceObj.hardware_version
            onBoardedDeviceDict['max_power'] = deviceObj.max_power
            onBoardedDeviceDict['site_type'] = deviceObj.site_type
            onBoardedDeviceDict['source'] = deviceObj.source
            onBoardedDeviceDict['stack'] = deviceObj.stack
            onBoardedDeviceDict['contract_number'] = deviceObj.contract_number
            onBoardedDeviceDict['contract_expiry'] = FormatDate(deviceObj.contract_expiry)
            onBoardedDeviceDict['item_code'] = deviceObj.item_code
            onBoardedDeviceDict['item_desc'] = deviceObj.item_desc
            onBoardedDeviceDict['clei'] = deviceObj.clei
            onBoardedDeviceDict['domain'] = deviceObj.domain
            onBoardedDeviceDict['ims_status'] = deviceObj.ims_status
            onBoardedDeviceDict['parent'] = deviceObj.parent
            onBoardedDeviceDict['vuln_fix_plan_status'] = deviceObj.vuln_fix_plan_status
            onBoardedDeviceDict['vuln_ops_severity'] = deviceObj.vuln_ops_severity
            onBoardedDeviceDict['integrated_with_aaa'] = deviceObj.integrated_with_aaa
            onBoardedDeviceDict['integrated_with_paam'] = deviceObj.integrated_with_paam
            onBoardedDeviceDict['approved_mbss'] = deviceObj.approved_mbss
            onBoardedDeviceDict['mbss_implemented'] = deviceObj.mbss_implemented
            onBoardedDeviceDict['mbss_integration_check'] = deviceObj.mbss_integration_check
            onBoardedDeviceDict['integrated_with_siem'] = deviceObj.integrated_with_siem
            onBoardedDeviceDict['threat_cases'] = deviceObj.threat_cases
            onBoardedDeviceDict['vulnerability_scanning'] = deviceObj.vulnerability_scanning
            onBoardedDeviceDict['vulnerability_severity'] = deviceObj.vulnerability_severity
            onBoardedDeviceDict['created_by'] = deviceObj.created_by
            onBoardedDeviceDict['modified_by'] = deviceObj.modified_by
                
            onBoardedDeviceDict['ims_function'] = deviceObj.ims_function
            onBoardedDeviceList.append(onBoardedDeviceDict)

        print("Fetched Onboarded devices", file=sys.stderr)

        return jsonify(onBoardedDeviceList), 200
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getOnBoardDevice", methods = ['POST'])
@token_required
def GetOnBoardDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        ipObj = request.get_json()
        print(ipObj, file=sys.stderr)
        ip_addr = ipObj['ip']
        
        onBoardDict = {}

        deviceObj = db.session.query(Device_Table).filter_by(ne_ip_address=ip_addr).first()
        deviceDataDict= {}
        if deviceObj:

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
            deviceDataDict['device_ru'] = deviceObj.ru
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
            deviceDataDict['item_code'] = deviceObj.item_code
            deviceDataDict['item_desc'] = deviceObj.item_desc
            deviceDataDict['clei'] = deviceObj.clei
        
        print(deviceObj.as_dict(), file=sys.stderr)
        
        phyObj = db.session.query(Phy_Table).filter_by(site_id=deviceObj.site_id).first()
        phyDataDict= {}
        if phyObj:

            phyDataDict['site_id'] = phyObj.site_id
            phyDataDict['region'] = phyObj.region
            phyDataDict['site_name'] = phyObj.site_name
            phyDataDict['latitude'] = phyObj.latitude
            phyDataDict['longitude'] = phyObj.longitude
            phyDataDict['city'] = phyObj.city
            phyDataDict['creation_date'] = FormatDate(phyObj.creation_date)
            phyDataDict['modification_date'] = FormatDate(phyObj.modification_date)
            phyDataDict['status'] = phyObj.status

        rackObj = db.session.query(Rack_Table).filter_by(rack_id=deviceObj.rack_id).first()
        rackDataDict= {}

        if rackObj:

            rackDataDict['rack_id'] = rackObj.rack_id
            rackDataDict['site_id'] = rackObj.site_id
            rackDataDict['rack_name'] = rackObj.rack_name
            rackDataDict['serial_number'] = rackObj.serial_number
            rackDataDict['manufactuer_date'] = FormatDate(rackObj.manufactuer_date)
            rackDataDict['unit_position'] = rackObj.unit_position
            rackDataDict['creation_date'] = FormatDate(rackObj.creation_date)
            rackDataDict['modification_date'] = FormatDate(rackObj.modification_date)
            rackDataDict['status'] = rackObj.status
            rackDataDict['device_ru'] = rackObj.ru
            rackDataDict['rfs_date'] = FormatDate(rackObj.rfs_date)
            rackDataDict['height'] = rackObj.height
            rackDataDict['width'] = rackObj.width
            rackDataDict['depth'] = rackObj.depth
            rackDataDict['pn_code'] = rackObj.pn_code
            rackDataDict['tag_id'] = rackObj.tag_id
            rackDataDict['rack_model'] = rackObj.rack_model
            rackDataDict['floor'] = rackObj.floor

        boardObjs = db.session.query(Board_Table).filter_by(device_id=deviceObj.device_id)
        boardObjList=[]

        for boardObj in boardObjs:
            boardDataDict= {}
            boardDataDict['board_id'] = boardObj.board_id
            boardDataDict['device_id'] = boardObj.device_id
            boardDataDict['board_name'] = boardObj.board_name
            boardDataDict['device_slot_id'] = boardObj.device_slot_id
            boardDataDict['hardware_version'] = boardObj.hardware_version
            boardDataDict['software_version'] = boardObj.software_version
            boardDataDict['serial_number'] = boardObj.serial_number
            boardDataDict['manufactuer_date'] = FormatDate(boardObj.manufactuer_date)
            boardDataDict['creation_date'] = FormatDate(boardObj.creation_date)
            boardDataDict['modification_date'] = FormatDate(boardObj.modification_date)
            boardDataDict['status'] = boardObj.status
            boardDataDict['eos_date'] = FormatDate(boardObj.eos_date)
            boardDataDict['eol_date'] = FormatDate(boardObj.eol_date)
            boardDataDict['rfs_date'] = FormatDate(boardObj.rfs_date)
            boardDataDict['pn_code'] = boardObj.pn_code
            boardDataDict['tag_id'] = boardObj.tag_id
            boardDataDict['item_code'] = boardObj.item_code
            boardDataDict['item_desc'] = boardObj.item_desc
            boardDataDict['clei'] = boardObj.clei
            
            boardObjList.append(boardDataDict)

        
        subboardObjs = db.session.query(Subboard_Table).filter_by(device_id=deviceObj.device_id)
        subboardObjList=[]

        for subboardObj in subboardObjs:
            subboardDataDict= {}
            subboardDataDict['subboard_id'] = subboardObj.subboard_id
            subboardDataDict['device_id'] = subboardObj.device_id
            subboardDataDict['subboard_name'] = subboardObj.subboard_name
            subboardDataDict['subboard_type'] = subboardObj.subboard_type
            subboardDataDict['subrack_id'] = subboardObj.subrack_id
            subboardDataDict['slot_number'] = subboardObj.slot_number
            subboardDataDict['hardware_version'] = subboardObj.hardware_version
            subboardDataDict['software_version'] = subboardObj.software_version
            subboardDataDict['serial_number'] = subboardObj.serial_number
            subboardDataDict['creation_date'] = FormatDate(subboardObj.creation_date)
            subboardDataDict['modification_date'] = FormatDate(subboardObj.modification_date)
            subboardDataDict['status'] = subboardObj.status
            subboardDataDict['eos_date'] = FormatDate(subboardObj.eos_date)
            subboardDataDict['eol_date'] = FormatDate(subboardObj.eol_date)
            subboardDataDict['rfs_date'] = FormatDate(subboardObj.rfs_date)
            subboardDataDict['tag_id'] = subboardObj.tag_id
            subboardDataDict['pn_code'] = subboardObj.pn_code
            subboardDataDict['item_code'] = subboardObj.item_code
            subboardDataDict['item_desc'] = subboardObj.item_desc
            subboardDataDict['clei'] = subboardObj.clei
            
            subboardObjList.append(subboardDataDict)

        sfpObjs = db.session.query(SFP_Table).filter_by(device_id=deviceObj.device_id)
        sfpObjList=[]

        for sfpObj in sfpObjs:
            sfpDataDict= {}

            sfpDataDict['sfp_id'] = sfpObj.sfp_id
            sfpDataDict['device_id'] = sfpObj.device_id
            sfpDataDict['media_type'] = sfpObj.media_type
            sfpDataDict['port_name'] = sfpObj.port_name
            sfpDataDict['port_type'] = sfpObj.port_type
            sfpDataDict['connector'] = sfpObj.connector
            sfpDataDict['mode'] = sfpObj.mode
            sfpDataDict['speed'] = sfpObj.speed
            sfpDataDict['wavelength'] = sfpObj.wavelength
            sfpDataDict['manufacturer'] = sfpObj.manufacturer
            sfpDataDict['optical_direction_type'] = sfpObj.optical_direction_type
            sfpDataDict['pn_code'] = sfpObj.pn_code
            sfpDataDict['creation_date'] = FormatDate(sfpObj.creation_date)
            sfpDataDict['modification_date'] = FormatDate(sfpObj.modification_date)
            sfpDataDict['status'] = sfpObj.status
            sfpDataDict['eos_date'] = FormatDate(sfpObj.eos_date)
            sfpDataDict['eol_date'] = FormatDate(sfpObj.eol_date)
            sfpDataDict['rfs_date'] = FormatDate(sfpObj.rfs_date)
            sfpDataDict['tag_id'] = sfpObj.tag_id
            sfpDataDict['item_code'] = sfpObj.item_code
            sfpDataDict['item_desc'] = sfpObj.item_desc
            sfpDataDict['clei'] = sfpObj.clei
            
            sfpObjList.append(sfpDataDict)

        licenseObjs = db.session.query(License_Table).filter_by(ne_name=deviceObj.device_name)
        licenseObjList=[]

        for licenseObj in licenseObjs:
            licenseDataDict= {}

            licenseDataDict['license_id'] = licenseObj.license_id
            licenseDataDict['license_name'] = licenseObj.license_name
            licenseDataDict['license_description'] = licenseObj.license_description
            licenseDataDict['ne_name'] = licenseObj.ne_name
            licenseDataDict['rfs_date'] = licenseObj.rfs_date
            licenseDataDict['activation_date'] = licenseObj.activation_date
            licenseDataDict['expiry_date'] = licenseObj.expiry_date
            licenseDataDict['grace_period'] = licenseObj.grace_period
            licenseDataDict['serial_number'] = licenseObj.serial_number
            licenseDataDict['creation_date'] = FormatDate(licenseObj.creation_date)
            licenseDataDict['modification_date'] = FormatDate(licenseObj.modification_date)
            licenseDataDict['status'] = licenseObj.status
            licenseDataDict['tag_id'] = licenseObj.tag_id
            licenseDataDict['capacity'] = licenseObj.capacity
            licenseDataDict['usage'] = licenseObj.usage
            licenseDataDict['pn_code'] = licenseObj.pn_code
            licenseDataDict['item_code'] = licenseObj.item_code
            licenseDataDict['item_desc'] = licenseObj.item_desc
            licenseDataDict['clei'] = licenseObj.clei
            
            licenseObjList.append(licenseDataDict)

        onBoardDict['device'] = deviceDataDict
        onBoardDict['datacenter'] = phyDataDict
        onBoardDict['rack'] = rackDataDict
        onBoardDict['board'] = boardObjList
        onBoardDict['subboard'] = subboardObjList
        onBoardDict['sfp'] = sfpObjList
        onBoardDict['license'] = licenseObjList

        return onBoardDict, 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/exportSeed", methods = ['GET'])
@token_required
def ExportSeed(user_data):
    """
        Export all Seed endpoint
        ---
        description: Export all Seed Data in Excel format
        responses:
            200:
                description: All Seed Information from Seed DB exported in an excel file       
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        seedObjList=[]
        seedObjs = Seed.query.all()

        for seedObj in seedObjs:
            seedDataDict= {}
            seedDataDict['seed_id'] = seedObj.seed_id
            seedDataDict['site_id'] = seedObj.site_id
            '''
            seedDataDict['region'] = seedObj.region
            seedDataDict['site_name'] = seedObj.site_name
            seedDataDict['latitude'] = seedObj.latitude
            seedDataDict['longitude'] = seedObj.longitude
            seedDataDict['city'] = seedObj.city
            seedDataDict['datacentre_status'] = seedObj.datacentre_status
            '''

            seedDataDict['rack_id'] = seedObj.rack_id
            '''
            seedDataDict['floor'] = seedObj.floor
            seedDataDict['rack_name'] = seedObj.rack_name
            seedDataDict['serial_number'] = seedObj.serial_number
            seedDataDict['manufactuer_date'] = seedObj.manufactuer_date
            seedDataDict['unit_position'] = seedObj.unit_position
            seedDataDict['rack_status'] = seedObj.rack_status
            seedDataDict['ru'] = seedObj.ru
            seedDataDict['rfs_date'] = seedObj.rfs_date
            seedDataDict['height'] = seedObj.height
            seedDataDict['width'] = seedObj.width
            seedDataDict['depth'] = seedObj.depth
            seedDataDict['pn_code'] = seedObj.pn_code
            seedDataDict['tag_id'] = seedObj.tag_id
            seedDataDict['rack_model'] = seedObj.rack_model
            '''
            seedDataDict['tag_id'] = seedObj.tag_id
            seedDataDict['device_id'] = seedObj.device_id
            seedDataDict['ne_ip_address'] = seedObj.ne_ip_address
            seedDataDict['device_ru'] = seedObj.device_ru
            seedDataDict['department'] = seedObj.department
            seedDataDict['section'] = seedObj.section
            seedDataDict['criticality'] = seedObj.criticality
            seedDataDict['function'] = seedObj.function
            seedDataDict['cisco_domain'] = seedObj.cisco_domain
            seedDataDict['virtual'] = seedObj.virtual
            seedDataDict['authentication'] = seedObj.authentication
            seedDataDict['subrack_id_number'] = seedObj.subrack_id_number
            seedDataDict['hostname'] = seedObj.hostname
            seedDataDict['site_type'] = seedObj.site_type
            seedDataDict['sw_type'] = seedObj.sw_type
            seedDataDict['vendor'] = seedObj.vendor
            seedDataDict['asset_type'] = seedObj.asset_type
            seedDataDict['operation_status'] = seedObj.operation_status
            seedDataDict['onboard_status'] = seedObj.onboard_status
            seedDataDict['contract_number'] = seedObj.contract_number
            seedDataDict['contract_expiry'] = seedObj.contract_expiry
            seedDataDict['item_code'] = seedObj.item_code
            seedDataDict['item_desc'] = seedObj.item_desc
            seedDataDict['clei'] = seedObj.clei

            seedObjList.append(seedDataDict)

        return jsonify(seedObjList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


def dismantleOnBoardDeviceFun(ip, user_data, reonboard=False):
    seedObj = db.session.query(Seed).filter_by(ne_ip_address=ip).first()
    if seedObj:
        seedObj.onboard_status = 'false'
        seedObj.operation_status='Dismantle'
        seedObj.modified_by = user_data['user_id']
        
        UpdateData(seedObj)

    deviceObj = db.session.query(Device_Table).filter_by(ne_ip_address=ip).first()

    #change status to Dismantle in device table
    if deviceObj:
        deviceObj.status = 'Dismantle'
        deviceObj.ims_status = 'Decommissioned'
        deviceObj.modification_date= datetime.now(tz)
        deviceObj.modified_by = user_data['user_id']
        
        time= datetime.now(tz)
        if not reonboard:
            deviceObj.dismantle_date = time
        UpdateData(deviceObj)  
    
    if deviceObj:
        #change all board status
        boardObjs = db.session.query(Board_Table).filter_by(device_id=deviceObj.device_id)
        if boardObjs and deviceObj: 
            for boardObj in boardObjs:
                boardObj.status = 'Dismantle'
                boardObj.modification_date= datetime.now(tz)
                boardObj.modified_by = user_data['user_id']
                if not reonboard:
                    boardObj.dismantle_date = time
                UpdateData(boardObj) 
            
        #change all sub-board status
        subboardObjs = db.session.query(Subboard_Table).filter_by(device_id=deviceObj.device_id)
        if subboardObjs and deviceObj:
            for subboardObj in subboardObjs:
                subboardObj.status = 'Dismantle'
                subboardObj.modification_date= datetime.now(tz)
                subboardObj.modified_by = user_data['user_id']
                if not reonboard:
                    subboardObj.dismantle_date = time
                UpdateData(subboardObj) 
                
        # change all SFP status 
        sfpObjss = db.session.query(SFP_Table).filter_by(device_id=deviceObj.device_id)
        if sfpObjss and deviceObj:
            for sfpObjs in sfpObjss:
                sfpObjs.status = 'Dismantle'
                sfpObjs.modification_date= datetime.now(tz)
                sfpObjs.modified_by = user_data['user_id']
                if not reonboard:
                    sfpObjs.dismantle_date = time
                UpdateData(sfpObjs)

        powerObj = db.session.query(POWER_FEEDS_TABLE).filter_by(device_id=deviceObj.device_id).first()
        if powerObj and deviceObj:
            powerObj.status = 'Dismantle'
            powerObj.modification_date= datetime.now(tz)
            powerObj.modified_by = user_data['user_id']
            
            UpdateData(powerObj)
        
        licenseObjs = db.session.query(License_Table).filter_by(ne_name=deviceObj.device_name)
        if deviceObj and licenseObjs:
            for licenseObj in licenseObjs:
                licenseObj.status = 'Dismantle'
                licenseObj.modification_date= datetime.now(tz)
                licenseObj.modified_by = user_data['user_id']
                if not reonboard:
                    licenseObj.dismantle_date = time
                UpdateData(licenseObj)        


@app.route("/dismantleOnBoardedDevice", methods = ['POST'])
@token_required
def DismantleOnBoardDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        deviceIDs = request.get_json()
        print(deviceIDs, file=sys.stderr)
        for ip in deviceIDs['ips']:
            dismantleOnBoardDeviceFun(ip, user_data)
            
        return jsonify("success"), 200
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/exportInventory", methods = ['GET'])
@token_required
def ExportInventory(user_data):
    #if request.headers.get('X-Auth-Key') == session['token']:
    if True:#session.get('token', None):
        phyObjList=[]
        phyObjs = Phy_Table.query.all()

        for phyObj in phyObjs:

            phyDataDict= {}
            phyDataDict['site_id'] = phyObj.site_id
            phyDataDict['region'] = phyObj.region
            phyDataDict['site_name'] = phyObj.site_name
            phyDataDict['latitude'] = phyObj.latitude
            phyDataDict['longitude'] = phyObj.longitude
            phyDataDict['city'] = phyObj.city
            phyDataDict['creation_date'] = phyObj.creation_date
            phyDataDict['modification_date'] = phyObj.modification_date
            phyDataDict['status'] = phyObj.status
            # phyDataDict['floor'] = phyObj.floor

            phyObjList.append(phyDataDict)

        #Get All Rack Data
        rackObjList=[]
        rackObjs = Rack_Table.query.all()

        for rackObj in rackObjs:
            rackDataDict= {}
            rackDataDict['rack_id'] = rackObj.rack_id
            rackDataDict['site_id'] = rackObj.site_id
            rackDataDict['rack_name'] = rackObj.rack_name
            rackDataDict['serial_number'] = rackObj.serial_number
            rackDataDict['manufactuer_date'] = rackObj.manufactuer_date
            rackDataDict['unit_position'] = rackObj.unit_position
            rackDataDict['creation_date'] = rackObj.creation_date
            rackDataDict['modification_date'] = rackObj.modification_date
            rackDataDict['status'] = rackObj.status
            rackDataDict['ru'] = rackObj.ru
            rackDataDict['rfs_date'] = rackObj.rfs_date
            rackDataDict['height'] = rackObj.height
            rackDataDict['width'] = rackObj.width
            rackDataDict['depth'] = rackObj.depth
            rackDataDict['pn_code'] = rackObj.pn_code
            rackDataDict['tag_id'] = rackObj.tag_id
            rackDataDict['rack_model'] = rackObj.rack_model
            rackDataDict['floor'] = rackObj.floor
            
            rackObjList.append(rackDataDict)

        #Get All Device Data
        deviceObjList=[]
        deviceObjs = Device_Table.query.all()

        for deviceObj in deviceObjs:
            deviceDataDict= {}
            deviceDataDict['device_id'] = deviceObj.device_id
            deviceDataDict['device_name'] = deviceObj.device_name
            deviceDataDict['site_id'] = deviceObj.site_id
            deviceDataDict['rack_id'] = deviceObj.rack_id
            deviceDataDict['ne_ip_address'] = deviceObj.ne_ip_address
            deviceDataDict['software_version'] = deviceObj.software_version
            deviceDataDict['patch_version'] = deviceObj.patch_version
            deviceDataDict['creation_date'] = deviceObj.creation_date
            deviceDataDict['modification_date'] = deviceObj.modification_date
            deviceDataDict['status'] = deviceObj.status
            deviceDataDict['device_ru'] = deviceObj.ru
            deviceDataDict['department'] = deviceObj.department
            deviceDataDict['section'] = deviceObj.section
            deviceDataDict['criticality'] = deviceObj.criticality
            deviceDataDict['function'] = deviceObj.function
            deviceDataDict['cisco_domain'] = deviceObj.cisco_domain
            deviceDataDict['manufacturer'] = deviceObj.manufacturer
            deviceDataDict['hw_eos_date'] = deviceObj.hw_eos_date
            deviceDataDict['hw_eol_date'] = deviceObj.hw_eol_date
            deviceDataDict['sw_eos_date'] = deviceObj.sw_eos_date
            deviceDataDict['sw_eol_date'] = deviceObj.sw_eol_date
            deviceDataDict['virtual'] = deviceObj.virtual
            deviceDataDict['rfs_date'] = deviceObj.rfs_date
            deviceDataDict['authentication'] = deviceObj.authentication
            deviceDataDict['serial_number'] = deviceObj.serial_number
            deviceDataDict['pn_code'] = deviceObj.pn_code
            deviceDataDict['tag_id'] = deviceObj.tag_id
            deviceDataDict['subrack_id_number'] = deviceObj.subrack_id_number
            deviceDataDict['manufactuer_date'] = deviceObj.manufactuer_date
            deviceDataDict['hardware_version'] = deviceObj.hardware_version
            deviceDataDict['max_power'] = deviceObj.max_power
            deviceDataDict['site_type'] = deviceObj.site_type
            deviceDataDict['source'] = deviceObj.source
            deviceDataDict['stack'] = deviceObj.stack
            deviceDataDict['contract_number'] = deviceObj.contract_number
            deviceDataDict['contract_expiry'] = deviceObj.contract_expiry
            deviceDataDict['item_code'] = deviceObj.item_code
            deviceDataDict['item_desc'] = deviceObj.item_desc
            deviceDataDict['clei'] = deviceObj.clei
            
            #deviceDataDict['site_name'] = Phy_Table.query.with_entities(Phy_Table.site_name).filter_by(site_id=deviceObj.site_id).first()[0]
            #deviceDataDict['rack_name'] = Rack_Table.query.with_entities(Rack_Table.rack_name).filter_by(rack_id=deviceObj.rack_id).first()[0]
            
            deviceObjList.append(deviceDataDict)

        #Get All Boards Data
        boardObjList=[]
        boardObjs = Board_Table.query.all()

        for boardObj in boardObjs:
            boardDataDict= {}
            boardDataDict['board_id'] = boardObj.board_id
            boardDataDict['device_id'] = boardObj.device_id
            boardDataDict['board_name'] = boardObj.board_name
            boardDataDict['device_slot_id'] = boardObj.device_slot_id
            boardDataDict['hardware_version'] = boardObj.hardware_version
            boardDataDict['software_version'] = boardObj.software_version
            boardDataDict['serial_number'] = boardObj.serial_number
            boardDataDict['manufactuer_date'] = boardObj.manufactuer_date
            boardDataDict['creation_date'] = boardObj.creation_date
            boardDataDict['modification_date'] = boardObj.modification_date
            boardDataDict['status'] = boardObj.status
            boardDataDict['eos_date'] = boardObj.eos_date
            boardDataDict['eol_date'] = boardObj.eol_date
            boardDataDict['rfs_date'] = boardObj.rfs_date
            boardDataDict['pn_code'] = boardObj.pn_code
            boardDataDict['tag_id'] = boardObj.tag_id
            boardDataDict['item_code'] = boardObj.item_code
            boardDataDict['item_desc'] = boardObj.item_desc
            boardDataDict['clei'] = boardObj.clei
            #boardDataDict['device_ip'] = Device_Table.query.with_entities(Device_Table.ne_ip_address).filter_by(device_id=boardObj.device_id).first()[0]
        
            boardObjList.append(boardDataDict)

        #Get All Sub-Board Data
        subboardObjList=[]
        subboardObjs = Subboard_Table.query.all()

        for subboardObj in subboardObjs:
            subboardDataDict= {}
            subboardDataDict['subboard_id'] = subboardObj.subboard_id
            subboardDataDict['device_id'] = subboardObj.device_id
            subboardDataDict['subboard_name'] = subboardObj.subboard_name
            subboardDataDict['subboard_type'] = subboardObj.subboard_type
            subboardDataDict['subrack_id'] = subboardObj.subrack_id
            subboardDataDict['slot_number'] = subboardObj.slot_number
            subboardDataDict['subslot_number'] = subboardObj.subslot_number
            subboardDataDict['hardware_version'] = subboardObj.hardware_version
            subboardDataDict['software_version'] = subboardObj.software_version
            subboardDataDict['serial_number'] = subboardObj.serial_number
            subboardDataDict['creation_date'] = subboardObj.creation_date
            subboardDataDict['modification_date'] = subboardObj.modification_date
            subboardDataDict['status'] = subboardObj.status
            subboardDataDict['eos_date'] = subboardObj.eos_date
            subboardDataDict['eol_date'] = subboardObj.eol_date
            subboardDataDict['rfs_date'] = subboardObj.rfs_date
            subboardDataDict['tag_id'] = subboardObj.tag_id
            subboardDataDict['pn_code'] = subboardObj.pn_code
            subboardDataDict['item_code'] = subboardObj.item_code
            subboardDataDict['item_desc'] = subboardObj.item_desc
            subboardDataDict['clei'] = subboardObj.clei
            #subboardDataDict['device_ip'] = Device_Table.query.with_entities(Device_Table.ne_ip_address).filter_by(device_id=subboardObj.device_id).first()[0]
            
            subboardObjList.append(subboardDataDict)

        #Get All SFPs Data
        sfpObjList=[]
        sfpObjs = SFP_Table.query.all()

        for sfpObj in sfpObjs:
            sfpDataDict= {}

            sfpDataDict['sfp_id'] = sfpObj.sfp_id
            sfpDataDict['device_id'] = sfpObj.device_id
            sfpDataDict['media_type'] = sfpObj.media_type
            sfpDataDict['port_name'] = sfpObj.port_name
            sfpDataDict['port_type'] = sfpObj.port_type
            sfpDataDict['connector'] = sfpObj.connector
            sfpDataDict['mode'] = sfpObj.mode
            sfpDataDict['speed'] = sfpObj.speed
            sfpDataDict['wavelength'] = sfpObj.wavelength
            sfpDataDict['manufacturer'] = sfpObj.manufacturer
            sfpDataDict['optical_direction_type'] = sfpObj.optical_direction_type
            sfpDataDict['pn_code'] = sfpObj.pn_code
            sfpDataDict['creation_date'] = sfpObj.creation_date
            sfpDataDict['modification_date'] = sfpObj.modification_date
            sfpDataDict['status'] = sfpObj.status
            sfpDataDict['eos_date'] = sfpObj.eos_date
            sfpDataDict['eol_date'] = sfpObj.eol_date
            sfpDataDict['rfs_date'] = sfpObj.rfs_date
            sfpDataDict['tag_id'] = sfpObj.tag_id
            sfpDataDict['serial_number'] = sfpObj.serial_number
            sfpDataDict['item_code'] = sfpObj.item_code
            sfpDataDict['item_desc'] = sfpObj.item_desc
            sfpDataDict['clei'] = sfpObj.clei
            #sfpDataDict['device_ip'] = Device_Table.query.with_entities(Device_Table.ne_ip_address).filter_by(device_id=sfpObj.device_id).first()[0]
    
            sfpObjList.append(sfpDataDict)

        #Get All License Data
        licenseObjList=[]
        licenseObjs = License_Table.query.all()

        for licenseObj in licenseObjs:
            licenseDataDict= {}

            licenseDataDict['license_id'] = licenseObj.license_id
            licenseDataDict['license_name'] = licenseObj.license_name
            licenseDataDict['license_description'] = licenseObj.license_description
            licenseDataDict['ne_name'] = licenseObj.ne_name
            licenseDataDict['rfs_date'] = licenseObj.rfs_date
            licenseDataDict['activation_date'] = licenseObj.activation_date
            licenseDataDict['expiry_date'] = licenseObj.expiry_date
            licenseDataDict['grace_period'] = licenseObj.grace_period
            licenseDataDict['serial_number'] = licenseObj.serial_number
            licenseDataDict['creation_date'] = licenseObj.creation_date
            licenseDataDict['modification_date'] = licenseObj.modification_date
            licenseDataDict['status'] = licenseObj.status
            licenseDataDict['tag_id'] = licenseObj.tag_id
            licenseDataDict['capacity'] = licenseObj.capacity
            licenseDataDict['usage'] = licenseObj.usage
            licenseDataDict['pn_code'] = licenseObj.pn_code
            licenseDataDict['item_code'] = licenseObj.item_code
            licenseDataDict['item_desc'] = licenseObj.item_desc
            licenseDataDict['clei'] = licenseObj.clei
            
            licenseObjList.append(licenseDataDict)

        objDict = {}

        objDict['phy'] = phyObjList
        objDict['rack'] = rackObjList
        objDict['device'] = deviceObjList
        objDict['board'] = boardObjList
        objDict['subboard'] = subboardObjList
        objDict['sfp'] = sfpObjList
        objDict['license'] = licenseObjList

        '''
        dfPhy = pd.DataFrame(phyObjList)
        dfRack = pd.DataFrame(rackObjList)
        dfDevice = pd.DataFrame(deviceObjList)
        dfBoard = pd.DataFrame(boardObjList)
        dfSubBoard = pd.DataFrame(subboardObjList)
        dfSFP = pd.DataFrame(sfpObjList)
        dfLicense = pd.DataFrame(licenseObjList)


        dfPhy.to_excel('PhysicalInventory.xlsx')
        dfRack.to_excel('RackInventory.xlsx')
        dfDevice.to_excel('DeviceInventory.xlsx')
        dfBoard.to_excel('BoardInventory.xlsx')
        dfSubBoard.to_excel('SubBoardInventory.xlsx')
        dfSFP.to_excel('SFPInventory.xlsx')
        dfLicense.to_excel('LicenseInventory.xlsx')
        
        print('Data is written successfully to Excel File.',file=sys.stderr)
        '''
        return objDict, 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addSNTC", methods = ['POST'])
@token_required
def AddSntc(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()

        #print(postData,file=sys.stderr)

        for sntcObj in postData:

            sntc = SNTC_Table()

            print(sntcObj,file=sys.stderr)
            sntc.pn_code = sntcObj['pn_code']
            if 'hw_eos_date' in sntcObj:
                if sntcObj['hw_eos_date'] != 'NA':
                    try:
                        sntc.hw_eos_date = datetime.strptime((sntcObj['hw_eos_date']),"%d/%m/%Y")            
                    except:
                        print("Incorrect formatting in hw_eos_date",file=sys.stderr)
            if 'hw_eol_date' in sntcObj:
                if sntcObj['hw_eol_date'] != 'NA':
                    try:
                        sntc.hw_eol_date = datetime.strptime((sntcObj['hw_eol_date']),"%d/%m/%Y")     
                    except:
                        print("Incorrect formatting in hw_eol_date",file=sys.stderr)
            if 'sw_eos_date' in sntcObj:
                if sntcObj['sw_eos_date'] != 'NA':
                    try:
                        sntc.sw_eos_date = datetime.strptime((sntcObj['sw_eos_date']),"%d/%m/%Y")            
                    except:
                        print("Incorrect formatting in sw_eos_date",file=sys.stderr)
            if 'sw_eol_date' in sntcObj:
                if sntcObj['sw_eol_date'] != 'NA':
                    try:
                        sntc.sw_eol_date = datetime.strptime((sntcObj['sw_eol_date']),"%d/%m/%Y")        
                    except:
                        print("Incorrect formatting in sw_eol_date",file=sys.stderr)
            if 'manufactuer_date' in sntcObj:
                 if sntcObj['manufactuer_date'] != 'NA':
                    try:
                        sntc.manufactuer_date =  datetime.strptime((sntcObj['manufactuer_date']),"%d/%m/%Y")        
                        #print(sntc.manufacture_date, file=sys.stderr)
                    except:
                        print("Incorrect formatting in manufactuer_date", file=sys.stderr)
            if 'item_desc' in sntcObj:
                 if sntcObj['item_desc'] != 'NA':
                    try:
                        sntc.item_desc =sntcObj['item_desc']           
                        #print(sntc.manufacture_date, file=sys.stderr)
                    except:
                        print("Incorrect Value in item description", file=sys.stderr)
            if 'item_code' in sntcObj:
                 if sntcObj['item_code'] != 'NA':
                    try:
                        sntc.item_code =sntcObj['item_code']           
                        #print(sntc.manufacture_date, file=sys.stderr)
                    except:
                        print("Incorrect Value in item description", file=sys.stderr)

            if 'vuln_fix_plan_status' in sntcObj:
                 if sntcObj['vuln_fix_plan_status'] != 'NA':
                    try:
                        sntc.vuln_fix_plan_status =sntcObj['vuln_fix_plan_status']           
                        #print(sntc.manufacture_date, file=sys.stderr)
                    except:
                        print("Incorrect Value in vuln_fix_plan_status", file=sys.stderr)

            if 'vuln_ops_severity' in sntcObj:
                 if sntcObj['vuln_ops_severity'] != 'NA':
                    try:
                        sntc.vuln_ops_severity =sntcObj['vuln_ops_severity']           
                        #print(sntc.manufacture_date, file=sys.stderr)
                    except:
                        print("Incorrect Value in vuln_ops_severity", file=sys.stderr)
            
           

            if SNTC_Table.query.with_entities(SNTC_Table.sntc_id).filter_by(pn_code=sntcObj['pn_code']).first() is not None:
                sntc.sntc_id = SNTC_Table.query.with_entities(SNTC_Table.sntc_id).filter_by(pn_code=sntcObj['pn_code']).first()[0]
                sntc.modified_by= user_data['user_id']
                print("Updated " + sntcObj['pn_code'],file=sys.stderr)
                sntc.modification_date= (datetime.now(tz))
                UpdateData(sntc)
            else:
                print("Inserted " +sntcObj['pn_code'],file=sys.stderr)
                sntc.creation_date= datetime.now(tz)
                sntc.modification_date= datetime.now(tz)
                sntc.created_by= user_data['user_id']
                sntc.modified_by= user_data['user_id']
                InsertData(sntc)
            
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getSNTC", methods = ['GET'])
@token_required
def getSntc(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        sntcList=[]
        sntcObjs = SNTC_Table.query.all()

        for sntcObj in sntcObjs:

            sntcDataDict= {}
            sntcDataDict['sntc_id'] = sntcObj.sntc_id
            sntcDataDict['pn_code'] = sntcObj.pn_code
            sntcDataDict['hw_eos_date'] = FormatDate(sntcObj.hw_eos_date)
            sntcDataDict['hw_eol_date'] = FormatDate(sntcObj.hw_eol_date)
            sntcDataDict['sw_eos_date'] = FormatDate(sntcObj.sw_eos_date)
            sntcDataDict['sw_eol_date'] = FormatDate(sntcObj.sw_eol_date)
            sntcDataDict['manufactuer_date'] = FormatDate(sntcObj.manufactuer_date)
            sntcDataDict['creation_date'] = FormatDate(sntcObj.creation_date)
            sntcDataDict['modification_date'] = FormatDate(sntcObj.modification_date)
            sntcDataDict['item_desc'] = sntcObj.item_desc
            sntcDataDict['item_code'] = sntcObj.item_code
            sntcDataDict['created_by'] = sntcObj.created_by
            sntcDataDict['modified_by'] = sntcObj.modified_by
            sntcDataDict['vuln_fix_plan_status']= sntcObj.vuln_fix_plan_status
            sntcDataDict['vuln_ops_severity']= sntcObj.vuln_ops_severity

            sntcList.append(sntcDataDict)
        return jsonify(sntcList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getPhy", methods = ['GET'])
@token_required
def GetPhy(user_data):
    """
        Get Physical DataCenter inforamtion from table based on filter provided
        ---
        summary: "Filter Physical Table"
        description: "Get Physical DataCenter inforamtion from table based on filter provided"
        produces:
        - "application/json"
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true
          
        -   in: "query"
            name: "site_name"
            type: "string"
            required: "true"

        responses:
            200:
                description: "Success"
                schema:
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

        site = request.args.get('site_name')
        #site = request.args.to_dict(flat=False)
        print(f"SITEEEEEEEEEEEEEEEEEEE IS",site, file=sys.stderr)

        #site_name=site
        phyObj = Phy_Table.query.with_entities(Phy_Table).filter_by(site_name=site).first()
        phyDataDict= {}

        if phyObj:

            phyDataDict['site_id'] = phyObj.site_id
            phyDataDict['region'] = phyObj.region
            phyDataDict['site_name'] = phyObj.site_name
            phyDataDict['latitude'] = phyObj.latitude
            phyDataDict['longitude'] = phyObj.longitude
            phyDataDict['city'] = phyObj.city
            phyDataDict['creation_date'] = FormatDate(phyObj.creation_date)
            phyDataDict['modification_date'] = FormatDate(phyObj.modification_date)
            phyDataDict['status'] = phyObj.status
            phyDataDict['total_devices'] = phyObj.total_count
            
        return jsonify(phyDataDict), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getRack", methods = ['GET'])
@token_required
def GetRack(user_data):
    """
        Get Racks inforamtion from rack table based on filter provided
        ---
        summary: "Filter Rack Table"
        description: "Get inforamtion from rack table based on filter provided"
        produces:
        - "application/json"
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true

        -   in: "query"
            name: "rack_name"
            type: "string"
            required: "true"

        responses:
            200:
                description: "Success"
                schema:
                    type: object
                    properties:
                        rack_id:
                            type: integer
                        site_id:
                            type: string
                        rack_name:
                            type: string
                        serial_number:
                            type: string
                        manufactuer_date:
                            type: date
                            example: "2019-05-17"
                        unit_position:
                            type: number
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
                        rfs_date:
                            type: date
                            example: "2019-05-17"
                        height:
                            type: integer
                        width:
                            type: integer
                        depth:
                            type: integer
                        pn_code:
                            type: string
                        tag_id:
                            type: string
                        rack_model:
                            type: string
                        floor:
                            type: string  
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        rack = request.args.get('rack_name')

        rackObj = Rack_Table.query.with_entities(Rack_Table).filter_by(rack_name=rack).first()
        rackDataDict= {}

        if rackObj:

            rackDataDict['rack_id'] = rackObj.rack_id
            rackDataDict['site_id'] = rackObj.site_id
            rackDataDict['rack_name'] = rackObj.rack_name
            rackDataDict['serial_number'] = rackObj.serial_number
            rackDataDict['manufactuer_date'] = FormatDate(rackObj.manufactuer_date)
            rackDataDict['unit_position'] = rackObj.unit_position
            rackDataDict['creation_date'] = FormatDate(rackObj.creation_date)
            rackDataDict['modification_date'] = FormatDate(rackObj.modification_date)
            rackDataDict['status'] = rackObj.status
            rackDataDict['ru'] = rackObj.ru
            rackDataDict['rfs_date'] = FormatDate(rackObj.rfs_date)
            rackDataDict['height'] = rackObj.height
            rackDataDict['width'] = rackObj.width
            rackDataDict['depth'] = rackObj.depth
            rackDataDict['pn_code'] = rackObj.pn_code
            rackDataDict['tag_id'] = rackObj.tag_id
            rackDataDict['rack_model'] = rackObj.rack_model
            rackDataDict['floor'] = rackObj.floor
            rackDataDict['total_count']=rackObj.total_count
            
        return jsonify(rackObj), 200
            
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
 
@app.route("/getDevice", methods = ['GET'])
@token_required
def getDevice(user_data):
    """
        Get Device inforamtion from table based on filter provided
        ---
        summary: "Filter Device Table"
        description: "Get inforamtion from Device table based on filter provided"
        produces:
        - "application/json"
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true
          
        -   in: "query"
            name: "device_name"
            type: "string"
            required: "true"

        responses:
            200:
                description: "Success"
                schema:
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
                        item_code:
                            type: string
                        item_desc:
                            type: string
                        clei:
                            type: string
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):

        device = request.args.get('device_name')

        deviceObj = Device_Table.query.with_entities(Device_Table).filter_by(device_name=device).first()
        deviceDataDict= {}

        if deviceObj:

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
            deviceDataDict['device_ru'] = deviceObj.ru
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
            deviceDataDict['item_code'] = deviceObj.item_code
            deviceDataDict['item_desc'] = deviceObj.item_desc
            deviceDataDict['clei'] = deviceObj.clei
            
        return jsonify(deviceDataDict), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getBoard", methods = ['GET'])
@token_required
def GetBoard(user_data):
    """
        Get Board inforamtion from table based on filter provided
        ---
        summary: "Filter Board Table"
        description: "Get inforamtion from Board table based on filter provided"
        produces:
        - "application/json"
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true

        -   in: "query"
            name: "board_name"
            type: "string"
            required: "true"

        responses:
            200:
                description: "Success"
                schema:
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
                        item_code:
                            type: string
                        item_desc:
                            type: string
                        clei:
                            type: string   
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):

        board = request.args.get('board_name')

        boardObj = Board_Table.query.with_entities(Board_Table).filter_by(board_name=board).first()
        boardDataDict= {}

        if boardObj:

            boardDataDict['board_id'] = boardObj.board_id
            boardDataDict['device_id'] = boardObj.device_id
            boardDataDict['board_name'] = boardObj.board_name
            boardDataDict['device_slot_id'] = boardObj.device_slot_id
            boardDataDict['hardware_version'] = boardObj.hardware_version
            boardDataDict['software_version'] = boardObj.software_version
            boardDataDict['serial_number'] = boardObj.serial_number
            boardDataDict['manufactuer_date'] = FormatDate(boardObj.manufactuer_date)
            boardDataDict['creation_date'] = FormatDate(boardObj.creation_date)
            boardDataDict['modification_date'] = FormatDate(boardObj.modification_date)
            boardDataDict['status'] = boardObj.status
            boardDataDict['eos_date'] = FormatDate(boardObj.eos_date)
            boardDataDict['eol_date'] = FormatDate(boardObj.eol_date)
            boardDataDict['rfs_date'] = FormatDate(boardObj.rfs_date)
            boardDataDict['pn_code'] = boardObj.pn_code
            boardDataDict['tag_id'] = boardObj.tag_id
            boardDataDict['item_code'] = boardObj.item_code
            boardDataDict['item_desc'] = boardObj.item_desc
            boardDataDict['clei'] = boardObj.clei
            
        return jsonify(boardDataDict), 200

    else:

        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getSubboard", methods = ['GET'])
@token_required
def GetSubboard(user_data):
    """
        Get Subboard inforamtion from table based on filter provided
        ---
        summary: "Filter Subboard Table"
        description: "Get inforamtion from subbtable based on filter provided"
        produces:
        - "application/json"
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true

        -   in: "query"
            name: "subboard_name"
            type: "string"
            required: "true"

        responses:
            200:
                description: "Success"
                schema:
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
                        item_code:
                            type: string
                        item_desc:
                            type: string
                        clei:
                            type: string   
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):

        subboard = request.args.get('subboard_name')

        subboardObj = Subboard_Table.query.with_entities(Subboard_Table).filter_by(subboard_name=subboard).first()
        subboardDataDict= {}

        if subboardObj:
            
            subboardDataDict['subboard_id'] = subboardObj.subboard_id
            subboardDataDict['device_id'] = subboardObj.device_id
            subboardDataDict['subboard_name'] = subboardObj.subboard_name
            subboardDataDict['subboard_type'] = subboardObj.subboard_type
            subboardDataDict['subrack_id'] = subboardObj.subrack_id
            subboardDataDict['slot_number'] = subboardObj.slot_number
            subboardDataDict['hardware_version'] = subboardObj.hardware_version
            subboardDataDict['software_version'] = subboardObj.software_version
            subboardDataDict['serial_number'] = subboardObj.serial_number
            subboardDataDict['creation_date'] = FormatDate(subboardObj.creation_date)
            subboardDataDict['modification_date'] = FormatDate(subboardObj.modification_date)
            subboardDataDict['status'] = subboardObj.status
            subboardDataDict['eos_date'] = FormatDate(subboardObj.eos_date)
            subboardDataDict['eol_date'] = FormatDate(subboardObj.eol_date)
            subboardDataDict['rfs_date'] = FormatDate(subboardObj.rfs_date)
            subboardDataDict['tag_id'] = subboardObj.tag_id
            subboardDataDict['pn_code'] = subboardObj.pn_code
            subboardDataDict['item_code'] = subboardObj.item_code
            subboardDataDict['item_desc'] = subboardObj.item_desc
            subboardDataDict['clei'] = subboardObj.clei
            
        return jsonify(subboardDataDict), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getSfp", methods = ['GET'])
@token_required
def GetSfp(user_data):
    """
        Get ports inforamtion from table based on filter provided
        ---
        summary: "Filter SFP Table"
        description: "Get inforamtion from SFP table based on filter provided"
        produces:
        - "application/json"
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true

        -   in: "query"
            name: "port_name"
            type: "string"
            required: "true"

        responses:
            200:
                description: "Success"
                schema:
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
                        item_code:
                            type: string
                        item_desc:
                            type: string
                        clei:
                            type: string
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):

        sfp = request.args.get('port_name')

        sfpObj = SFP_Table.query.with_entities(SFP_Table).filter_by(port_name=sfp).first()
        sfpDataDict= {}

        if sfpObj:

            sfpDataDict['sfp_id'] = sfpObj.sfp_id
            sfpDataDict['device_id'] = sfpObj.device_id
            sfpDataDict['media_type'] = sfpObj.media_type
            sfpDataDict['port_name'] = sfpObj.port_name
            sfpDataDict['port_type'] = sfpObj.port_type
            sfpDataDict['connector'] = sfpObj.connector
            sfpDataDict['mode'] = sfpObj.mode
            sfpDataDict['speed'] = sfpObj.speed
            sfpDataDict['wavelength'] = sfpObj.wavelength
            sfpDataDict['manufacturer'] = sfpObj.manufacturer
            sfpDataDict['optical_direction_type'] = sfpObj.optical_direction_type
            sfpDataDict['pn_code'] = sfpObj.pn_code
            sfpDataDict['creation_date'] = sfpObj.creation_date
            sfpDataDict['modification_date'] = sfpObj.modification_date
            sfpDataDict['status'] = sfpObj.status
            sfpDataDict['eos_date'] = FormatDate(sfpObj.eos_date)
            sfpDataDict['eol_date'] = FormatDate(sfpObj.eol_date)
            sfpDataDict['rfs_date'] = FormatDate(sfpObj.rfs_date)
            sfpDataDict['tag_id'] = sfpObj.tag_id
            sfpDataDict['serial_number'] = sfpObj.serial_number
            sfpDataDict['item_code'] = sfpObj.item_code
            sfpDataDict['item_desc'] = sfpObj.item_desc
            sfpDataDict['clei'] = sfpObj.clei
            
        return jsonify(sfpDataDict), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getLicense", methods = ['GET'])
@token_required
def GetLicense(user_data):
    """
        Get Racks inforamtion from table based on filter provided
        ---
        summary: "Filter Rack Table"
        description: "Get inforamtion from table based on filter provided"
        produces:
        - "application/json"
        parameters:
        - 
          name: X-Auth-Key
          in: header
          type: string
          required: true

        -   in: "query"
            name: "license_name"
            type: "string"
            required: "true"

        responses:
            200:
                description: "Success"
                schema:
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
                        item_code:
                            type: string
                        item_desc:
                            type: string
                        clei:
                            type: string 
    """
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        license = request.args.get('license_name')

        licenseObj = License_Table.query.with_entities(License_Table).filter_by(license_name=license).first()
        licenseDataDict= {}

        if licenseObj:

            licenseDataDict['license_id'] = licenseObj.license_id
            licenseDataDict['license_name'] = licenseObj.license_name
            licenseDataDict['license_description'] = licenseObj.license_description
            licenseDataDict['ne_name'] = licenseObj.ne_name
            licenseDataDict['rfs_date'] = licenseObj.rfs_date
            licenseDataDict['activation_date'] = licenseObj.activation_date
            licenseDataDict['expiry_date'] = licenseObj.expiry_date
            licenseDataDict['grace_period'] = licenseObj.grace_period
            licenseDataDict['serial_number'] = licenseObj.serial_number
            licenseDataDict['creation_date'] = FormatDate(licenseObj.creation_date)
            licenseDataDict['modification_date'] = FormatDate(licenseObj.modification_date)
            licenseDataDict['status'] = licenseObj.status
            licenseDataDict['tag_id'] = licenseObj.tag_id
            licenseDataDict['capacity'] = licenseObj.capacity
            licenseDataDict['usage'] = licenseObj.usage
            licenseDataDict['pn_code'] = licenseObj.pn_code
            licenseDataDict['item_code'] = licenseObj.item_code
            licenseDataDict['item_desc'] = licenseObj.item_desc
            licenseDataDict['clei'] = licenseObj.clei

        return jsonify(licenseDataDict), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addUnboardedDevice",methods = ['POST'])
@token_required
def addUnboardedDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        deviceObj = request.get_json()

        print(deviceObj,file=sys.stderr)

        if Phy_Table.query.with_entities(Phy_Table.site_id).filter_by(site_id=deviceObj['site_id']).first() != None and Rack_Table.query.with_entities(Rack_Table.rack_id).filter_by(rack_id=deviceObj['rack_id'] ).first() != None:
            device = Device_Table()
            device.site_id = deviceObj['site_id']
            device.rack_id = deviceObj['rack_id'] 
            seed = Seed.query.filter_by(ne_ip_address = deviceObj['ne_ip_address']).first()
            if not seed:
                print("Ip is not in seed",file=sys.stderr)
                return jsonify({'response': "Not in seed"}), 500
                
            seed.onboard_status = 'true'
            seed.modified_by= user_data['user_id']
            UpdateData(seed)
            
            device.device_id = deviceObj['device_id']
            
            device.ne_ip_address = deviceObj['ne_ip_address']
            device.device_name = deviceObj['device_name']#
            if deviceObj['software_version']:
                device.software_version = deviceObj['software_version']
            if deviceObj['patch_version']:
                device.patch_version = deviceObj['patch_version']    
            if deviceObj['status']:
                device.status = 'Production'
            if deviceObj['device_ru']:
                device.ru = deviceObj['device_ru']
            #if deviceObj['department']:
            #    device.department= deviceObj['department']
            #if deviceObj['section']:
            #    device.section = deviceObj['section']
            if deviceObj['criticality']:
                device.criticality= deviceObj['criticality']
            if deviceObj['function']:
                device.function= deviceObj['function']
            if deviceObj['cisco_domain']:
                device.cisco_domain= deviceObj['cisco_domain']
            if deviceObj['manufacturer']:
                device.manufacturer= deviceObj['manufacturer']
            #if  deviceObj['hw_eos_date']:
            #    device.hw_eos_date = FormatStringDate(deviceObj['hw_eos_date']) 
            #if  deviceObj['hw_eol_date']:
            #    device.hw_eol_date = FormatStringDate(deviceObj['hw_eol_date'])        
            #if  deviceObj['sw_eos_date']:
            #    device.sw_eos_date = FormatStringDate(deviceObj['sw_eos_date'])
            #if  deviceObj['sw_eol_date']:
            #    device.sw_eol_date = FormatStringDate(deviceObj['sw_eol_date'])
            if  deviceObj['virtual']:
                device.virtual= deviceObj['virtual']
            if  'rfs_date' in deviceObj:
                device.rfs_date=FormatStringDate(deviceObj['rfs_date'])
            if  deviceObj['authentication']:
                device.authentication = deviceObj['authentication']
            if  deviceObj['serial_number']:
                device.serial_number = deviceObj['serial_number']
            if  'pn_code' in deviceObj:
                device.pn_code = deviceObj['pn_code']
            if  deviceObj['tag_id']:
                device.tag_id = deviceObj['tag_id']
            if  deviceObj['subrack_id_number']:
                device.subrack_id_number = deviceObj['subrack_id_number']
            #if  deviceObj['manufactuer_date']:
            #    device.manufactuer_date = FormatStringDate(deviceObj['manufactuer_date'])
            if  deviceObj['hardware_version']:
                device.hardware_version = deviceObj['hardware_version']
            if  deviceObj['max_power']:
                device.max_power = deviceObj['max_power']
            if  deviceObj['site_type']:
                device.site_type = deviceObj['site_type']
            if  deviceObj['stack']:
                device.stack = deviceObj['stack']
            if  deviceObj['contract_number']:
                device.contract_number = deviceObj['contract_number']
            if  deviceObj['contract_expiry']:
                device.contract_expiry = FormatStringDate(deviceObj['contract_expiry'])
            #if  deviceObj['item_code']:
            #    device.item_code = deviceObj['item_code']
            #if  deviceObj['item_desc']:
            #    device.item_desc = deviceObj['item_desc']
            if  deviceObj['clei']:
                device.clei = deviceObj['clei']
            
            device.parent = deviceObj['parent']
            device.vuln_fix_plan_status = deviceObj['vuln_fix_plan_status']
            device.vuln_ops_severity = deviceObj['vuln_ops_severity']
            device.integrated_with_aaa = deviceObj['integrated_with_aaa']
            device.integrated_with_paam = deviceObj['integrated_with_paam']
            device.approved_mbss = deviceObj['approved_mbss']
            device.mbss_implemented = deviceObj['mbss_implemented']
            device.mbss_integration_check = deviceObj['mbss_integration_check']
            device.integrated_with_siem = deviceObj['integrated_with_siem']
            device.threat_cases = deviceObj['threat_cases']
            device.vulnerability_scanning = deviceObj['vulnerability_scanning']
            if "vulnerability_severity" in deviceObj:
                device.vulnerability_severity = deviceObj['vulnerability_severity']


            device.source = 'Static'
            
            try:
                
                domainsnObj = DOMAINS_TABLE.query.filter_by(cisco_domain=seed.cisco_domain).first() 
                if domainsnObj:
                    device.department= domainsnObj.department
                    device.section= domainsnObj.section
                    seed.department= domainsnObj.department
                    seed.section= domainsnObj.section
                
            except Exception as e:
                print(f"Exception Occured in Getting Domains Information {e}", file=sys.stderr)
            ######ADDITIONS BY HAMZA###########
            
            
            if 'pn_code' in deviceObj:
                if deviceObj['pn_code']:

                    sntcDevice = SNTC_Table.query.filter_by(pn_code=deviceObj['pn_code']).first()
                    
                    if sntcDevice:

                        if sntcDevice.hw_eos_date is not None:
                            device.hw_eos_date = sntcDevice.hw_eos_date
                        if sntcDevice.hw_eol_date is not None:
                            device.hw_eol_date = sntcDevice.hw_eol_date
                        if sntcDevice.sw_eos_date is not None:
                            device.sw_eos_date = sntcDevice.sw_eos_date
                        if sntcDevice.sw_eol_date is not None:
                            device.sw_eol_date = sntcDevice.sw_eol_date
                        if sntcDevice.item_desc is not None:
                            device.item_desc = sntcDevice.item_desc
                        if sntcDevice.item_code is not None:
                            device.item_code = sntcDevice.item_code
                        # if sntcDevice.rfs_date is not None:
                        #     device.rfs_date = sntcDevice.rfs_date
            
            if deviceObj['cisco_domain'] is not None:                
                if "EDN" in str(deviceObj['cisco_domain']):
                    device.domain= "ENT"
                if "IGW" in str(deviceObj['cisco_domain']):
                    device.domain= "IGW"
                if "SOC" in str(deviceObj['cisco_domain']):
                    device.domain= "Security"
            device.ims_status= "Active"
            
            try:
                imsFunction= str(device.device_id).split('-') 
                imsFunction= imsFunction[1] 
                
                imsFunctionObj = FUNCTIONS_TABLE.query.with_entities(FUNCTIONS_TABLE.function).filter_by(tfun=imsFunction).first() 
                if imsFunctionObj:
                    device.ims_function= imsFunctionObj[0]
                else:
                    device.ims_function= imsFunction
            except Exception as e:
                print(f"Exception Occured in Getting IMS Function {e}", file=sys.stderr)


            #print(device.sw_eol_date,file=sys.stderr)
            
            if Device_Table.query.with_entities(Device_Table.device_id).filter_by(ne_ip_address=deviceObj['ne_ip_address']).first() is not None:
                device.device_id = Device_Table.query.with_entities(Device_Table.device_id).filter_by(ne_ip_address=deviceObj['ne_ip_address']).first()[0]
                print("Updated " + deviceObj['ne_ip_address'],file=sys.stderr)
                device.modification_date= datetime.now(tz)
                device.modified_by= user_data['user_id']
                UpdateData(device)
                
            else:
                print("Inserted " +deviceObj['ne_ip_address'],file=sys.stderr)
                device.creation_date= datetime.now(tz)
                device.modification_date= datetime.now(tz)
                device.created_by= user_data['user_id']
                device.modified_by= user_data['user_id']
                InsertData(device)
            ######ADDITIONS BY HAMZA###########
            power= POWER_FEEDS_TABLE()

            if POWER_FEEDS_TABLE.query.with_entities(POWER_FEEDS_TABLE).filter_by(device_id=deviceObj['device_id']).first() is not None:

                row= POWER_FEEDS_TABLE.query.with_entities(POWER_FEEDS_TABLE.device_id,POWER_FEEDS_TABLE.power_id).filter_by(device_id=deviceObj['device_id']).first()

                power.device_id = row[0]

                power.power_id= row[1]
                power.status= device.status
                print("Updated Power Feed ",file=sys.stderr)
                power.modified_by= user_data['user_id']

                UpdateData(power)
            else:
                power.device_id =deviceObj['device_id']
                power.status= 'Production'
                print("Inserted Power Feed" ,file=sys.stderr)
                power.created_by= user_data['user_id']
                power.modified_by= user_data['user_id']
                InsertData(power)
            
            '''
            power= POWER_FEEDS_TABLE()
            if POWER_FEEDS_TABLE.query.with_entities(POWER_FEEDS_TABLE).filter_by(device_id=deviceObj['device_id']).first() is not None:
                row= POWER_FEEDS_TABLE.query.with_entities(POWER_FEEDS_TABLE.device_id,POWER_FEEDS_TABLE.power_id).filter_by(device_id=deviceObj['device_id']).first()
                power.device_id = row[0]
                power.power_id= row[1]

                print("Updated Power Feed ",file=sys.stderr)
                UpdateData(power)
            else:
                
                power.device_id =deviceObj['device_id']
                power.status= deviceObj.status

                print("Inserted Power Feed" ,file=sys.stderr)
                InsertData(power)
            '''


            return jsonify({'response': "success","code":"200"})
        else:
            print("Rack ID or Site ID does not exists", file=sys.stderr)   
            return jsonify({'response': "Rack Id or Site Id does not Exists"}), 500


    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
      
# @app.route("/addUnboardedDevices",methods = ['POST'])
# @token_required
# def addUnboardedDevices(user_data):
#     if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
#         postData = request.get_json()

#         print(postData,file=sys.stderr)
        

#         for deviceObj in postData:
#             if Rack_Table.query.with_entities(Rack_Table.rack_id).filter_by(rack_id=deviceObj['rack_id'] ).first() != None and Phy_Table.query.with_entities(Phy_Table.site_id).filter_by(site_id=deviceObj['site_id']).first() != None:

#                 seed = Seed.query.filter_by(ne_ip_address = deviceObj['ne_ip_address']  ).first()
#                 if not seed:
#                     continue
                
#                 seed.onboard_status = 'true'
#                 UpdateData(seed)

#                 device = Device_Table()
#                 if 'device_id' in deviceObj:
#                     device.device_id = deviceObj['device_id']
#                 if 'site_id' in deviceObj:
#                     device.site_id = deviceObj['site_id']
#                 if 'rack_id' in deviceObj:
#                     device.rack_id = deviceObj['rack_id']   
#                 if 'ne_ip_address' in deviceObj:
#                     device.ne_ip_address = deviceObj['ne_ip_address']          
#                 if 'software_version' in deviceObj:
#                     device.software_version = deviceObj['software_version']
#                 if 'patch_version' in deviceObj:
#                     device.patch_version = deviceObj['patch_version']    
#                 if 'status' in deviceObj:
#                     device.status = deviceObj['status']
#                 if 'device_ru' in deviceObj:
#                     device.device_id = deviceObj['device_ru']
#                 if 'department' in deviceObj:
#                     device.department= deviceObj['department']
#                 if 'section' in deviceObj:
#                     device.section = deviceObj['section']
#                 if 'criticality' in deviceObj:
#                     device.criticality= deviceObj['criticality']
#                 if 'function' in deviceObj:
#                     device.function= deviceObj['function']
#                 if 'cisco_domain' in deviceObj:
#                     device.cisco_domain= deviceObj['cisco_domain']
#                 if 'manufacturer' in deviceObj:
#                     device.manufacturer= deviceObj['manufacturer']
#                 if 'hw_eos_date' in deviceObj:
#                     device.hw_eos_date = FormatStringDate(deviceObj['hw_eos_date']) 
#                 if 'hw_eol_date' in deviceObj:
#                     device.hw_eol_date = FormatStringDate(deviceObj['hw_eol_date']) 
#                 if 'sw_eos_date' in deviceObj:
#                     device.sw_eos_date =FormatStringDate(deviceObj['sw_eos_date']) 
#                 if 'sw_eol_date' in deviceObj:
#                     device.sw_eol_date = FormatStringDate(deviceObj['sw_eol_date']) 
#                 if 'virtual' in deviceObj:
#                     device.virtual= deviceObj['virtual']
#                 if 'rfs_date' in deviceObj:
#                     device.rfs_date = FormatStringDate(deviceObj['rfs_date']) 
#                 if 'authentication' in deviceObj:
#                     device.authentication = deviceObj['authentication']
#                 if 'serial_number' in deviceObj:
#                     device.serial_number = deviceObj['serial_number']
#                 if 'pn_code' in deviceObj:
#                     device.pn_code = deviceObj['pn_code']
#                 if 'tag_id' in deviceObj:
#                     device.tag_id = deviceObj['tag_id']
#                 if 'subrack_id_number' in deviceObj:
#                     device.subrack_id_number = deviceObj['subrack_id_number']
#                 if 'manufactuer_date' in deviceObj:
#                     device.manufactuer_date = FormatStringDate(deviceObj['manufactuer_date'])
#                 if 'hardware_version' in deviceObj:
#                     device.hardware_version = deviceObj['hardware_version']
#                 if 'max_power' in deviceObj:
#                     device.max_power = deviceObj['max_power']
#                 if 'device_name' in deviceObj:
#                     device.device_name = deviceObj['device_name']
#                 if 'site_type' in deviceObj:
#                     device.site_type = deviceObj['site_type']
#                 if 'stack' in deviceObj:
#                     device.stack = deviceObj['stack']
#                 if 'contract_number' in deviceObj:
#                     device.contract_number = deviceObj['contract_number']
#                 if 'contract_expiry' in deviceObj:
#                     device.contract_expiry = FormatStringDate(deviceObj['contract_expiry'])
#                 if 'item_code' in deviceObj:
#                     device.item_code = deviceObj['item_code']
#                 if 'item_desc' in deviceObj:
#                     device.item_desc = deviceObj['item_desc']
#                 if 'clei' in deviceObj:
#                     device.clei = deviceObj['clei']
#                 if 'parent' in deviceObj:
#                     device.parent = deviceObj['parent']

#                 device.source = "Static"

                
            
#                 if Device_Table.query.with_entities(Device_Table.device_id).filter_by(ne_ip_address=deviceObj['ne_ip_address']).first() is not None:
#                     print("Updated " + deviceObj['ne_ip_address'],file=sys.stderr)
#                     device.modification_date= datetime.now(tz)
#                     UpdateData(device)
#                 else:
#                     print("Inserted " + deviceObj['ne_ip_address'],file=sys.stderr)
#                     device.creation_date= datetime.now(tz)
#                     device.modification_date= datetime.now(tz)
#                     InsertData(device)
#             else:
#                 print("Rack ID or Site ID does not exists", file=sys.stderr)   
#                 return jsonify({'response': "Rack Id or Site Id does not Exists"}),500
#         return jsonify({'response': "success","code":"200"})
#     else: 
#         print("Authentication Failed", file=sys.stderr)
#         return jsonify({'message': 'Authentication Failed'}), 401
 
@app.route("/getFailedDevices", methods = ['POST'])
@token_required
def getFailedDevices(user_data):
    filename =  time.strftime("%d-%m-%Y")+'.txt'
    filename = 'app/failed/ims/'+filename
    print(filename, file=sys.stderr)
    failed_device=[]
    try:
        with open(filename) as fd:
            failed_device = json.loads(fd.read())
        #with open('app/failed/ims/'+filename, 'r') as fd:
        #    failed_device= json.load(fd)
        #failed_device = json.load(open('app/failed/ims/'+filename, encoding='utf-8'))
        return jsonify(failed_device), 200
    except Exception as e:
        print(e, file=sys.stderr)
        #fo= open('app/failed/ims/'+filename, "w")
        #fo.close()
        return jsonify(failed_device), 200

@app.route('/getPNCodeStatsPerCiscoDomain',methods = ['GET'])
@token_required    
def PnCodePerCiscoDomain(user_data):
    if True:#session.get('token', None):
        
        objDict = {}
        queryString = f"select PN_CODE,count(PN_CODE),CISCO_DOMAIN from device_table where status = 'Production' and PN_CODE is not null group by PN_CODE,CISCO_DOMAIN;"
        result = db.session.execute(queryString)
         
        for row in result:                  
        
            pnCode = (row[0])
            pnCodeCount = row[1]
            cisco_domain = row[2]
            
            if pnCode in objDict:
                objDict[pnCode][cisco_domain] = pnCodeCount

            else:
                
                objDict[pnCode] = {}
                objDict[pnCode]["IGW-NET"]=0
                objDict[pnCode]["IGW-SYS"]=0
                objDict[pnCode]["EDN-NET"]=0
                objDict[pnCode]["EDN-SYS"]=0
                objDict[pnCode]["EDN-IPT"]=0
                objDict[pnCode]["EDN-IPT-Endpoints"]=0
                objDict[pnCode]["SOC"]=0
                objDict[pnCode]["CDN"]=0
                objDict[pnCode]["POS"]=0
                objDict[pnCode]["REBD"]=0
                objDict[pnCode][cisco_domain] = pnCodeCount    

        queryString = f"select PN_CODE,count(PN_CODE) from board_table where status = 'Production' and PN_CODE like '%WS-C3750%' or PN_CODE like '%WS-C3850%' or (PN_CODE not LIKE '%C9300-NM%' and PN_CODE LIKE '%C9300%') group by PN_CODE;"
        result = db.session.execute(queryString)

        for row in result:              

            pnCode = (row[0])
            pnCodeCount = row[1] 
            if pnCode in objDict:
                objDict[pnCode]["EDN-NET"] = objDict[pnCode]["EDN-NET"]+pnCodeCount
            else:
                objDict[pnCode] = {}
                objDict[pnCode]["EDN-NET"] = pnCodeCount
                
        queryString1 = f"select TECHNOLOGY,COUNT from cdn_table;"
        result1 = db.session.execute(queryString1)
        for row in result1:

            pnCode = (row[0])
            pnCodeCount = row[1] 
            if pnCode in objDict:
                objDict[pnCode]["CDN"] = objDict[pnCode]["CDN"]+pnCodeCount
            else:
                objDict[pnCode] = {}
                objDict[pnCode]["CDN"] = pnCodeCount
                objDict[pnCode]["IGW-NET"]=0
                objDict[pnCode]["IGW-SYS"]=0
                objDict[pnCode]["EDN-NET"]=0
                objDict[pnCode]["EDN-SYS"]=0
                objDict[pnCode]["EDN-IPT"]=0
                objDict[pnCode]["EDN-IPT-Endpoints"]=0
                objDict[pnCode]["SOC"]=0
                objDict[pnCode]["POS"]=0
                objDict[pnCode]["REBD"]=0

        queryString2 = "select PRODUCT_ID,COUNT(PRODUCT_ID) from ipt_endpoints_table where PRODUCT_ID not like '%Client Services Framework%' and PRODUCT_ID!='' group by PRODUCT_ID;"
        result2 = db.session.execute(queryString2)
        for row in result2:
            pnCode = (row[0])
            pnCodeCount = row[1] 
            if pnCode in objDict:
                objDict[pnCode]["CDN"] = objDict[pnCode]["CDN"]+pnCodeCount
            else:
                objDict[pnCode] = {}
                objDict[pnCode]["CDN"] = 0
                objDict[pnCode]["IGW-NET"]=0
                objDict[pnCode]["IGW-SYS"]=0
                objDict[pnCode]["EDN-NET"]=0
                objDict[pnCode]["EDN-SYS"]=0
                objDict[pnCode]["EDN-IPT"]=0
                objDict[pnCode]["EDN-IPT-Endpoints"]=pnCodeCount
                objDict[pnCode]["SOC"]=0
                objDict[pnCode]["POS"]=0
                objDict[pnCode]["REBD"]=0
        
        queryString3 = f"select pn_code,count(pn_code) from pos_table group by pn_code;"
        result3 = db.session.execute(queryString3)
        for row in result3:

            pnCode = (row[0])
            pnCodeCount = row[1] 
            if pnCode in objDict:
                objDict[pnCode]["POS"] = objDict[pnCode]["POS"]+pnCodeCount
            else:
                objDict[pnCode] = {}
                objDict[pnCode]["CDN"] = 0
                objDict[pnCode]["IGW-NET"]=0
                objDict[pnCode]["IGW-SYS"]=0
                objDict[pnCode]["EDN-NET"]=0
                objDict[pnCode]["EDN-SYS"]=0
                objDict[pnCode]["EDN-IPT"]=0
                objDict[pnCode]["EDN-IPT-Endpoints"]=0
                objDict[pnCode]["SOC"]=0
                objDict[pnCode]["POS"]=pnCodeCount
                objDict[pnCode]["REBD"]=0
        
        queryString4 = f"select pn_code,count(pn_code) from rebd_table group by pn_code;"
        result4 = db.session.execute(queryString4)
        for row in result4:

            pnCode = (row[0])
            pnCodeCount = row[1] 
            if pnCode in objDict:
                objDict[pnCode]["REBD"] = objDict[pnCode]["REBD"]+pnCodeCount
            else:
                objDict[pnCode] = {}
                objDict[pnCode]["CDN"] = 0
                objDict[pnCode]["IGW-NET"]=0
                objDict[pnCode]["IGW-SYS"]=0
                objDict[pnCode]["EDN-NET"]=0
                objDict[pnCode]["EDN-SYS"]=0
                objDict[pnCode]["EDN-IPT"]=0
                objDict[pnCode]["EDN-IPT-Endpoints"]=0
                objDict[pnCode]["SOC"]=0
                objDict[pnCode]["POS"]=0
                objDict[pnCode]["REBD"]=pnCodeCount
        objList = []
        for pn_code in objDict:
            dict = objDict[pn_code]
            dict['pn_code']=pn_code
            objList.append(dict)
     
        #print(objList,file=sys.stderr)   
        return jsonify(objList), 200
        

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
               
@app.route('/exportPNCodeStats',methods=['GET'])
@token_required
def ExportPnCodePerCiscoDomain(user_Data):
    """
        Export all Pn Codes Per Domain endpoint
        ---
        description: Export all Pn Codes Per Domain in Excel format
        responses:
            200:
                description: All Pn Codes Per Domain Information from Device_Table DB exported in an excel file       
    """
    if True:#session.get('token', None):
        
        objDict = {}
        queryString = f"select PN_CODE,count(PN_CODE),CISCO_DOMAIN from device_table where PN_CODE is not null group by PN_CODE,CISCO_DOMAIN;"
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],row[1],row[2],file=sys.stderr)         
            pnCode = (row[0])
            pnCodeCount = row[1]
            cisco_domain = row[2]
            
            if pnCode in objDict:
                objDict[pnCode][cisco_domain] = pnCodeCount
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
                objDict[pn_code]["CDN"]=0
                objDict[pnCode][cisco_domain] = pnCodeCount        
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
      

@app.route('/getAllPNCodeDates',methods=['GET'])
@token_required
def GetAllPNCodeDates(user_data):

    if True:#session.get('token', None):
        dates = []
        queryString = "select distinct(creation_date) from  pncode_snap_table ORDER BY creation_date DESC;"
        
        result = db.session.execute(queryString)
         
        for row in result:                  
            print(row[0],file=sys.stderr)     
            dates.append(row[0])    

        return jsonify(dates), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/getPnCodeByDate", methods = ['POST'])
@token_required
def GetPnCodeByDate(user_data):
    
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        dateObj = request.get_json()
        print(type(dateObj['date']),file=sys.stderr)  

        utc = datetime.strptime(dateObj['date'], '%a, %d %b %Y %H:%M:%S GMT')
        print(utc,file=sys.stderr)
        current_time = utc.strftime("%Y-%m-%d %H:%M:%S")
        print(current_time,file=sys.stderr)
        dictList = []

        pnObjs = db.session.query(PnCode_SNAP_Table).filter_by(creation_date=current_time).all()
        for pnObj in pnObjs:

            objDict = {}
            
            print(pnObj.pn_code, file=sys.stderr)
            
            objDict['pn_code']=pnObj.pn_code
            objDict["IGW-NET"]=pnObj.igw_net
            objDict["IGW-SYS"]=pnObj.igw_sys
            objDict["EDN-NET"]=pnObj.edn_net
            objDict["EDN-SYS"]=pnObj.edn_sys
            objDict["EDN-IPT"]=pnObj.edn_ipt
            objDict["EDN-IPT-Endpoints"]=pnObj.edn_ipt_endpoints
            objDict["SOC"]=pnObj.soc
            objDict["CDN"]=pnObj.cdn
            objDict['POS']=pnObj.pos
            objDict['REBD'] = pnObj.rebd
            dictList.append(objDict)
        print(dictList,file=sys.stderr)
        return jsonify(dictList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401   

@app.route("/syncFromInventory", methods = ['GET'])
@token_required
def SyncFromInventory(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        queryString = "SELECT DISTINCT(pn_code) FROM device_table WHERE pn_code NOT IN (SELECT pn_code FROM sntc_table) UNION select distinct(pn_code) from board_table where pn_code not in (select pn_code from sntc_table) UNION select distinct pn_code from subboard_table where pn_code not in (select pn_code from sntc_table) UNION SELECT DISTINCT(pn_code) FROM sfp_table WHERE pn_code NOT IN (SELECT pn_code FROM sntc_table);"
        result = db.session.execute(queryString)
        
        print(result,file=sys.stderr)
        
        for row in result:
            pn_code = row[0]
            sntc = SNTC_Table()
            
            sntc.pn_code = pn_code
            
            if SNTC_Table.query.with_entities(SNTC_Table.sntc_id).filter_by(pn_code=pn_code).first() is None:
                print("Inserted " +pn_code,file=sys.stderr)
                sntc.creation_date= datetime.now(tz)
                sntc.modification_date= datetime.now(tz)
                InsertData(sntc)
            else:
                print("Updated " + pn_code,file=sys.stderr)
                sntc.modification_date= datetime.now(tz)
                UpdateData(sntc)
        return ("SUCCESS"), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/syncToInventory", methods = ['GET'])
@token_required
def SyncToInventory(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        try:
            queryString = "select PN_CODE,HW_EOS_DATE,HW_EOL_DATE,SW_EOS_DATE,SW_EOL_DATE, ITEM_DESC, ITEM_CODE, VULN_FIX_PLAN_STATUs, VULN_OPS_SEVERITY from sntc_table where PN_CODE in (select PN_CODE from device_table);"
            result = db.session.execute(queryString)
            
            for row in result:
                pn_code = row[0]
                hw_eos_date = row[1]
                hw_eol_date = row[2]
                sw_eos_date = row[3]
                sw_eol_date = row[4]
                item_desc = row[5]
                item_code = row[6]
                vuln_status= row[7]
                vuln_severity= row[8]
                db.session.execute(f"update device_table set HW_EOS_DATE='{hw_eos_date}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('Device Table: HW_EOS_DATE',hw_eos_date,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)
                db.session.execute(f"update device_table set HW_EOL_DATE='{hw_eol_date}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('Device Table: HW_EOL_DATE',hw_eol_date,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)
                db.session.execute(f"update device_table set SW_EOS_DATE='{sw_eos_date}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('Device Table: SW_EOS_DATE',sw_eos_date,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)
                db.session.execute(f"update device_table set SW_EOL_DATE='{sw_eol_date}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('Device Table: SW_EOL_DATE',sw_eol_date,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)
                db.session.execute(f"update device_table set ITEM_DESC='{item_desc}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('Device Table: ITEM_DESC',item_desc,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)
                db.session.execute(f"update device_table set ITEM_CODE='{item_code}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('Device Table: ITEM_CODE',item_code,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)
                if vuln_status:
                    db.session.execute(f"update device_table set VULN_FIX_PLAN_STATUS='{vuln_status}' where PN_CODE='{pn_code}';")
                    db.session.commit()
                    print('Device Table: Vuln Fix Plan Status ',vuln_status,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)
                    
                    queryString = f"select device_id from device_table where PN_CODE='{pn_code}';"
                    #print(queryString, file=sys.stderr)
                    result = db.session.execute(queryString)
                    for row in result:
                        if row[0]:
                            db.session.execute(f"update seed_table set VULN_FIX_PLAN_STATUS='{vuln_status}' where device_id='{row[0]}';")
                            db.session.commit()
                            print('Seed Table: Vuln Fix Plan Status ',vuln_status,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)

                if vuln_severity:
                    db.session.execute(f"update device_table set VULN_OPS_SEVERITY='{vuln_severity}' where PN_CODE='{pn_code}';")
                    db.session.commit()
                    print('Device Table: Vuln Ops Severity ',vuln_severity,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)
                    
                    queryString = f"select device_id from device_table where PN_CODE='{pn_code}';"
                    #print(queryString, file=sys.stderr)
                    result = db.session.execute(queryString)
                    for row in result:
                        if row[0]:
                            db.session.execute(f"update seed_table set VULN_OPS_SEVERITY='{vuln_severity}' where device_id='{row[0]}';")
                            db.session.commit()
                            print('Seed Table: Vuln Ops Severity ',vuln_severity,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)


            queryString1 = "select PN_CODE,HW_EOS_DATE,HW_EOL_DATE, ITEM_DESC, ITEM_CODE from sntc_table where PN_CODE in (select PN_CODE from board_table);" 
            result1 = db.session.execute(queryString1)
            for row in result1:
                pn_code = row[0]
                hw_eos_date = row[1]
                hw_eol_date = row[2]
                item_desc = row[3]
                item_code = row[4]
    
                db.session.execute(f"update board_table set EOS_DATE='{hw_eos_date}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('Board Table: HW_EOS_DATE',hw_eos_date,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)
                db.session.execute(f"update board_table set EOL_DATE='{hw_eol_date}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('Board Table: HW_EOL_DATE',hw_eol_date,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)          
                db.session.execute(f"update board_table set ITEM_DESC='{item_desc}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('Board Table: ITEM_DESC',item_desc,' against PN CODE',pn_code,' updated successfully',file=sys.stderr) 
                db.session.execute(f"update board_table set ITEM_CODE='{item_code}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('Board Table: ITEM_CODE',item_code,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)          
            
            queryString2 = "select PN_CODE,HW_EOS_DATE,HW_EOL_DATE, ITEM_DESC, ITEM_CODE from sntc_table where PN_CODE in (select PN_CODE from subboard_table);" 
            result2 = db.session.execute(queryString2)
            for row in result2:
                pn_code = row[0]
                hw_eos_date = row[1]
                hw_eol_date = row[2]
                item_desc = row[3]
                item_code = row[4]
                
                db.session.execute(f"update subboard_table set EOS_DATE='{hw_eos_date}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('SUbBoard Table: HW_EOS_DATE',hw_eos_date,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)
                db.session.execute(f"update subboard_table set EOL_DATE='{hw_eol_date}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('SUbBoard Table: HW_EOL_DATE',hw_eol_date,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)        
                db.session.execute(f"update subboard_table set ITEM_DESC='{item_desc}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('SUbBoard Table: ITEM_DESC',item_desc,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)        
                db.session.execute(f"update subboard_table set ITEM_CODE='{item_code}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('SUbBoard Table: ITEM_CODE',item_code,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)        


            queryString3 = "select PN_CODE,HW_EOS_DATE,HW_EOL_DATE, ITEM_DESC, ITEM_CODE from sntc_table where PN_CODE in (select PN_CODE from sfp_table);"
            result3 = db.session.execute(queryString3)
            for row in result3:
                pn_code = row[0]
                hw_eos_date = row[1]
                hw_eol_date = row[2]
                item_desc = row[3]
                item_code = row[4]
                
                db.session.execute(f"update sfp_table set EOS_DATE='{hw_eos_date}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('SFP Table: HW_EOS_DATE',hw_eos_date,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)
                db.session.execute(f"update sfp_table set EOL_DATE='{hw_eol_date}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('SFP Table: HW_EOL_DATE',hw_eol_date,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)
                db.session.execute(f"update sfp_table set ITEM_DESC='{item_desc}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('SFP Table: ITEM_DESC',item_desc,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)
                db.session.execute(f"update sfp_table set ITEM_CODE='{item_code}' where PN_CODE='{pn_code}';")
                db.session.commit()
                print('SFP Table: ITEM_CODE',item_code,' against PN CODE',pn_code,' updated successfully',file=sys.stderr)
            
            return jsonify("Success"), 200  

        except Exception as e:
            print(f"SNTC error occured {e}", file=sys.stderr)
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/fetchPnCodeSnap", methods = ['GET'])
@token_required
def FetchPnCodeSnap(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        FetchPnCodeSnapFunc()
            
        return jsonify("Success"), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
def FetchPnCodeSnapFunc():
    objDict = {}
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    queryString = f"select PN_CODE,count(PN_CODE),CISCO_DOMAIN from device_table where status = 'Production' and PN_CODE is not null group by PN_CODE,CISCO_DOMAIN;"
    result = db.session.execute(queryString)
        
    for row in result:                  
        print(row[0],row[1],row[2],file=sys.stderr)         
        pnCode = (row[0])
        pnCodeCount = row[1]
        cisco_domain = row[2]
        
        if pnCode in objDict:
            objDict[pnCode][cisco_domain] = pnCodeCount
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
            objDict[pnCode]["CDN"]=0
            objDict[pnCode]['POS']=0
            objDict[pnCode]['REBD']=0

            objDict[pnCode][cisco_domain] = pnCodeCount

    #queryString = f"select PN_CODE,count(PN_CODE) from board_table where status = 'Production' and BOARD_NAME like '%9300%' or BOARD_NAME like '%3850%' or BOARD_NAME like '%3750%' group by PN_CODE;"
    queryString = f"select PN_CODE,count(PN_CODE) from board_table where status = 'Production' and PN_CODE like '%WS-C3750%' or PN_CODE like '%WS-C3850%' or (PN_CODE not LIKE '%C9300-NM%' and PN_CODE LIKE '%C9300%') group by PN_CODE;"
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
            objDict[pnCode]["IGW-NET"]=0
            objDict[pnCode]["IGW-SYS"]=0
            objDict[pnCode]["EDN-SYS"]=0
            objDict[pnCode]["EDN-IPT"]=0
            objDict[pnCode]["EDN-IPT-Endpoints"]=0
            objDict[pnCode]["SOC"]=0
            objDict[pnCode]["CDN"]=0
            objDict[pnCode]['POS']=0
            objDict[pnCode]['REBD']=0        
    
    
    
    queryString1 = f"select TECHNOLOGY,COUNT from cdn_table;"
    result1 = db.session.execute(queryString1)
    for row1 in result1:
        pnCode1 = row1[0]
        pnCodeCount1 = row1[1]
        if pnCode1 in objDict:
            objDict[pnCode1]["CDN"] = objDict[pnCode1]["CDN"]+pnCodeCount1
            
        else:
            objDict[pnCode1] = {}
            objDict[pnCode1]["EDN-NET"]=0
            objDict[pnCode1]["IGW-NET"]=0
            objDict[pnCode1]["IGW-SYS"]=0
            objDict[pnCode1]["EDN-SYS"]=0
            objDict[pnCode1]["EDN-IPT"]=0
            objDict[pnCode1]["EDN-IPT-Endpoints"]=0
            objDict[pnCode1]["SOC"]=0
            objDict[pnCode1]["CDN"]= pnCodeCount1
            objDict[pnCode1]['POS']=0
            objDict[pnCode1]['REBD']=0
    
    queryString2 = f"select PRODUCT_ID,COUNT(PRODUCT_ID) from ipt_endpoints_table where PRODUCT_ID not like '%Client Services Framework%' and PRODUCT_ID!='' group by PRODUCT_ID;"
    result2 = db.session.execute(queryString2)
    for row in result2:
        pnCode1 = row[0]
        pnCodeCount1 = row[1]
        if pnCode1 in objDict:
            objDict[pnCode1]["EDN-IPT-Endpoints"] = objDict[pnCode1]["EDN-IPT-Endpoints"]+pnCodeCount1
            
        else:
            objDict[pnCode1] = {}
            objDict[pnCode1]["EDN-NET"]=0
            objDict[pnCode1]["IGW-NET"]=0
            objDict[pnCode1]["IGW-SYS"]=0
            objDict[pnCode1]["EDN-SYS"]=0
            objDict[pnCode1]["EDN-IPT"]=0
            objDict[pnCode1]["EDN-IPT-Endpoints"]=pnCodeCount1
            objDict[pnCode1]["SOC"]=0
            objDict[pnCode1]["CDN"]= 0        
            objDict[pnCode1]['POS']=0
            objDict[pnCode1]['REBD']=0
    
    queryString3 = f"select pn_code,count(pn_code) from pos_table group by pn_code;"
    result3 = db.session.execute(queryString3)
    for row1 in result3:
        pnCode1 = row1[0]
        pnCodeCount1 = int(row1[1])
        if pnCode1 in objDict:
            objDict[pnCode1]["POS"] = objDict[pnCode1]["POS"]+pnCodeCount1
            
        else:
            objDict[pnCode1] = {}
            objDict[pnCode1]["EDN-NET"]=0
            objDict[pnCode1]["IGW-NET"]=0
            objDict[pnCode1]["IGW-SYS"]=0
            objDict[pnCode1]["EDN-SYS"]=0
            objDict[pnCode1]["EDN-IPT"]=0
            objDict[pnCode1]["EDN-IPT-Endpoints"]=0
            objDict[pnCode1]["SOC"]=0
            objDict[pnCode1]["CDN"]= 0
            objDict[pnCode1]['POS']=pnCodeCount1
            objDict[pnCode1]['REBD']=0
    
    queryString4 = f"select pn_code,count(pn_code) from rebd_table group by pn_code;"
    result4 = db.session.execute(queryString4)
    for row1 in result4:
        pnCode1 = row1[0]
        pnCodeCount1 = int(row1[1])
        if pnCode1 in objDict:
            objDict[pnCode1]["REBD"] = objDict[pnCode1]["REBD"]+pnCodeCount1
            
        else:
            objDict[pnCode1] = {}
            objDict[pnCode1]["EDN-NET"]=0
            objDict[pnCode1]["IGW-NET"]=0
            objDict[pnCode1]["IGW-SYS"]=0
            objDict[pnCode1]["EDN-SYS"]=0
            objDict[pnCode1]["EDN-IPT"]=0
            objDict[pnCode1]["EDN-IPT-Endpoints"]=0
            objDict[pnCode1]["SOC"]=0
            objDict[pnCode1]["CDN"]= 0
            objDict[pnCode1]['POS']=0
            objDict[pnCode1]['REBD']=pnCodeCount1
    
    for key in objDict:
        snap = PnCode_SNAP_Table()
        print("key is:",key,file=sys.stderr)
        snap.pn_code = key
        snap.igw_net = objDict[key]["IGW-NET"]
        snap.igw_sys = objDict[key]["IGW-SYS"]
        snap.edn_net = objDict[key]["EDN-NET"]
        snap.edn_sys = objDict[key]["EDN-SYS"]
        snap.edn_ipt = objDict[key]["EDN-IPT"]
        snap.edn_ipt_endpoints = objDict[key]["EDN-IPT-Endpoints"]
        snap.soc = objDict[key]["SOC"]
        snap.cdn = objDict[key]["CDN"]
        snap.pos = objDict[key]["POS"]
        snap.rebd = objDict[key]["REBD"]
        
        snap.creation_date = current_time
        snap.modification_date = current_time

        print("Inserted " +key,"into pnCode-SNAP-Table",file=sys.stderr)
        InsertData(snap)

@app.route("/addPnCodeSnap", methods = ['POST'])
@token_required
def AddPnCodeSnap(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()
        print(postData, file=sys.stderr)
        #print(postData,file=sys.stderr)
        date= postData['date']
        pnCodeData= postData['data']
        if pnCodeData and date:
            for pnCode in pnCodeData:
                try:
                    snap = PnCode_SNAP_Table()
                    if 'pn_code' in pnCode:
                        snap.pn_code = pnCode["pn_code"]
                    if 'IGW-NET' in pnCode:
                        snap.igw_net = pnCode.get("IGW-NET", 0)
                    if 'IGW-SYS' in pnCode:    
                        snap.igw_sys = pnCode.get("IGW-SYS", 0)
                    if 'EDN-NET' in pnCode:
                        snap.edn_net = pnCode.get("EDN-NET", 0)
                    if 'EDN-SYS' in pnCode:
                        snap.edn_sys = pnCode.get("EDN-SYS", 0)
                    if 'EDN-IPT' in pnCode:
                        snap.edn_ipt = pnCode.get("EDN-IPT", 0)
                    if 'EDN-IPT-Endpoints' in pnCode:
                        snap.edn_ipt_endpoints = pnCode.get("EDN-IPT-Endpoints", 0)
                    if 'SOC' in pnCode:
                        snap.soc = pnCode.get("SOC", 0)
                    if 'CDN' in pnCode:
                        snap.cdn = pnCode.get("CDN",0)
                    if 'POS' in pnCode:
                        snap.pos = pnCode.get("POS",0)
                    if 'REBD' in pnCode:
                        snap.rebd = pnCode.get("REBD",0)
                    snap.creation_date = date
                    snap.modification_date = date
                                        
                    InsertData(snap)
                        
                except Exception as e:
                    print(f"Exception occured while importing pncode snap {e}", file=sys.stderr)
                    return jsonify({'response': f"Exception occured while importing pncode snap {e}",}), 500 
                
            return jsonify({'response': "success","code":"200"})
                
        else: 
            print("Empty Excel data", file=sys.stderr)
            return jsonify({'response': "Empty Excel data",}), 500 

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/editSntc',methods = ['POST'])
@token_required
def EditSntc(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        sntcObj = request.get_json()
        print(sntcObj,file=sys.stderr)
         
        sntc = SNTC_Table()
        sntc.sntc_id = sntcObj['sntc_id']           
        sntc.pn_code = sntcObj['pn_code']
        sntc.hw_eos_date = FormatStringDate(sntcObj['hw_eos_date'])
        sntc.hw_eol_date = FormatStringDate(sntcObj['hw_eol_date'])
        sntc.sw_eos_date = FormatStringDate(sntcObj['sw_eos_date'])
        sntc.sw_eol_date = FormatStringDate(sntcObj['sw_eol_date'])    
        sntc.manufactuer_date = FormatStringDate(sntcObj['manufactuer_date'])
        sntc.item_desc = sntcObj['item_desc']
        sntc.item_code = sntcObj['item_code']
        sntc.modified_by =user_data['user_id']
        sntc.vuln_fix_plan_status = sntcObj['vuln_fix_plan_status']
        sntc.vuln_ops_severity = sntcObj['vuln_ops_severity']
        
        #sntc.creation_date = FormatStringDate(sntcObj['creation_date'])
        
        #SNTC_Table.sntc_id = SNTC_Table.query.with_entities(SNTC_Table.sntc_id).filter_by(pn_code=sntcObj['pn_code']).first()[0]
        print("Updated " + sntcObj['pn_code'],file=sys.stderr)
        sntc.modification_date= datetime.now(tz)
        UpdateData(sntc)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addSite", methods = ['POST'])
@token_required
def AddSite(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        siteObj = request.get_json()

        print(siteObj,file=sys.stderr)

        site = Phy_Table()
        site.site_id = siteObj['site_id']
        site.region = siteObj['region']
        site.site_name = siteObj['site_name']
        site.latitude = siteObj['latitude']
        site.longitude = siteObj['longitude']
        site.city = siteObj['city']
        site.site_type = siteObj['site_type']
        site.status = siteObj['status']
        
        if Phy_Table.query.with_entities(Phy_Table.site_id).filter_by(site_name=siteObj['site_name']).first() is not None:
            site.site_id = Phy_Table.query.with_entities(Phy_Table.site_id).filter_by(site_name=siteObj['site_name']).first()[0]
            print("Updated " + siteObj['site_name'],file=sys.stderr)
            site.creation_date= datetime.now(tz)
            site.modification_date= datetime.now(tz)
            site.modification_date= datetime.now(tz)
            site.modified_by= user_data['user_id']
            UpdateData(site)
        else:
            print("Inserted " +siteObj['site_name'],file=sys.stderr)
            site.creation_date= datetime.now(tz)
            site.modification_date= datetime.now(tz)
            site.created_by= user_data['user_id']
            site.modified_by= user_data['user_id']
            InsertData(site)
        
        return jsonify({'response': "success","code":"200"})
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addRacks", methods = ['POST'])
@token_required
def AddRack(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        rackObj = request.get_json()

        print(rackObj,file=sys.stderr)
        
        if Phy_Table.query.with_entities(Phy_Table.site_id).filter_by(site_id=rackObj['site_id']).first() is not None:

            rack = Rack_Table()
            rack.site_id = rackObj['site_id']
            rack.floor = rackObj['floor']
            rack.rack_name = rackObj['rack_name']
            rack.serial_number = rackObj['serial_number']
            rack.manufactuer_date = FormatStringDate(rackObj['manufactuer_date'])
            rack.unit_position = rackObj['unit_position']
            rack.status = rackObj['status']
            if str(rackObj['ru']).isdigit():  #isinstance(rackObj['ru'],int ):
                rack.ru = rackObj['ru']
            else:
                rack.ru = 0
            rack.rfs_date = FormatStringDate(rackObj['rfs_date'])
            if rackObj['height']:  #isinstance(rackObj['height'],int ):
                rack.height = rackObj['height']
            else:
                rack.height = 0
            if rackObj['width']:  #isinstance(rackObj['width'],int ):
                rack.width = rackObj['width']
            else:
                rack.width = 0
            if rackObj['depth']:  #isinstance(rackObj['depth'],int ):
                rack.depth = rackObj['depth']
            else:
                rack.depth = 0
            rack.pn_code = rackObj['pn_code']
            rack.tag_id = rackObj['tag_id']
            rack.rack_model = rackObj['rack_model']
            if Rack_Table.query.with_entities(Rack_Table.rack_id).filter_by(rack_id=rackObj['rack_id']).first() is not None:
                rack.rack_id = rackObj['rack_id'] #Rack_Table.query.with_entities(Rack_Table.rack_id).filter_by(rack_name=rackObj['rack_name']).first()[0]
                print("Updated " + rackObj['rack_name'],file=sys.stderr)
                rack.modification_date= datetime.now(tz)
                rack.modified_by= user_data['user_id']
                UpdateData(rack)
            else:
                print("Inserted " +rackObj['rack_name'],file=sys.stderr)
                rack.creation_date= datetime.now(tz)
                rack.modification_date= datetime.now(tz)
                rack.created_by= user_data['user_id']
                rack.modified_by= user_data['user_id']
                InsertData(rack)
            return jsonify({'response': "success","code":"200"})

        else:
            print("Site ID do not exists", file=sys.stderr)
            #return jsonify({'response': "Site ID do not exists","code":"500"})
            return jsonify({'response': 'Site ID do not exists'}), 500
        
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getDevicesByRackId", methods = ['GET'])
@token_required
def GetDevicesByRackId(user_data):
    rack_id= request.args.get('rackid')
    devicesList= []
    if rack_id:
        deviceObj= Device_Table.query.with_entities(Device_Table.ne_ip_address, Device_Table.device_id, Device_Table.status).filter_by(rack_id=rack_id).filter(Device_Table.status!="Dismantle").all()
        if deviceObj:
            for device in deviceObj:
                deviceDataDict={}
                deviceDataDict['ne_ip_address']= device.ne_ip_address
                deviceDataDict['device_id']= device.device_id
                deviceDataDict['status']=  device.status
                devicesList.append(deviceDataDict)
            
            return jsonify(devicesList), 200
        else: 
            print("Rack Data not found in DB", file=sys.stderr)
            return jsonify({'response': "Rack Data not found in DB"}), 500 
    else:
        print("Can not Get Rack ID from URL", file=sys.stderr)
        return jsonify({'response': "Can not Get Rack ID from URL"}), 500

@app.route("/getDevicesBySiteId", methods = ['GET'])
@token_required
def GetDevicesBySiteId(user_data):
    site_id= request.args.get('siteid')
    devicesList= []
    if site_id:
        deviceObj= Device_Table.query.with_entities(Device_Table.ne_ip_address, Device_Table.device_id, Device_Table.status).filter_by(site_id=site_id).filter(Device_Table.status !="Dismantle").all()
        if deviceObj:
            for device in deviceObj:
                deviceDataDict={}
                deviceDataDict['ne_ip_address']= device.ne_ip_address
                deviceDataDict['device_id']= device.device_id
                deviceDataDict['status']=  device.status
                devicesList.append(deviceDataDict)
            
            return jsonify(devicesList), 200
        else: 
            print("Site Data not found in DB", file=sys.stderr)
            return jsonify({'response': "Site Data not found in DB"}), 500 
    else:
        print("Can not Get Site ID from URL", file=sys.stderr)
        return jsonify({'response': "Can not Get Site ID from URL"}), 500

@app.route("/getRacksBySiteId",methods=['GET'])
@token_required
def GetRacksBySiteId(user_data):
    site_id = request.args.get('siteid')
    rackList  = []
    if True:
        rackObj = Rack_Table.query.with_entities(Rack_Table.rack_id,Rack_Table.status).filter_by(site_id=site_id).filter(Rack_Table.status !="Dismantle").all()
        if rackObj:
            for rack in rackObj:
                rackDataDict = {}
                rackDataDict['rack_id'] = rack.rack_id
                rackDataDict['status'] = rack.status
                rackList.append(rackDataDict)
            return jsonify(rackList),200
        else:
            print("Rack Data not found in DB", file=sys.stderr)
            return jsonify({'response': "Rack Data not found in DB"}), 500 
    else:
        print("Can not Get Site ID from URL", file=sys.stderr)
        return jsonify({'response': "Can not Get Site ID from URL"}), 500

@app.route("/getAllSiteIDs", methods = ['GET'])
@token_required
def GetAllSiteIDs(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        phyObjList=[]
        phyObjs = Phy_Table.query.with_entities(Phy_Table.site_id).all()

        for phyObj in phyObjs:
            phyObjList.append(phyObj.site_id)
            #phyDataDict= {}
            #phyDataDict['site_name'] = phyObj.site_name
            #phyObjList.append(phyDataDict)

        return jsonify(phyObjList), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

        
@app.route("/getAllRackIDs", methods = ['GET'])
@token_required
def GetAllRackIDs(user_Data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        rackObjList=[]
        rackObjs = Rack_Table.query.with_entities(Rack_Table.rack_id, Rack_Table.rack_name).all()

        for rackObj in rackObjs:
            rackObjList.append(str(rackObj.rack_id)+" | "+str(rackObj.rack_name))
            #rackObjList.append(str(rackObj.rack_id))
            #rackDataDict= {}
            #rackDataDict['rack_id'] = rackObj.rack_id   
            #rackObjList.append(rackDataDict)

        return jsonify(rackObjList), 200

@app.route("/getAllCDN", methods = ['GET'])
@token_required
def GetAllCDN(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        cdnList= []
        
        cdnObjs= CDN_Table.query.all()
        for cdnObj in cdnObjs:
                
            cdnDataDict={}
            cdnDataDict['technology']= cdnObj.technology
            cdnDataDict['count']= cdnObj.count
            cdnDataDict['creation_date']=  cdnObj.creation_date
            cdnDataDict['modification_date']=  cdnObj.modification_date
            cdnDataDict['created_by'] = cdnObj.created_by
            cdnDataDict['modified_by'] = cdnObj.modified_by
            cdnList.append(cdnDataDict)
                
        return jsonify(cdnList), 200
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addCDNDevice",methods = ['POST'])
@token_required
def AddCDNDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        cdnObj = request.get_json()

        print(cdnObj,file=sys.stderr)
        cdn = CDN_Table()
        if cdnObj['count'] and cdnObj['technology'] :
            cdn.count = cdnObj['count']
            cdn.technology = cdnObj['technology']
            
                    
            if CDN_Table.query.with_entities(CDN_Table.technology).filter_by(technology=cdnObj['technology']).first() is not None:
                cdn.technology = CDN_Table.query.with_entities(CDN_Table.technology).filter_by(technology=cdnObj['technology']).first()[0]
                print(f"Updated {cdnObj['technology']}",file=sys.stderr)
                cdn.modification_date= datetime.now(tz)
                cdn.modified_by= user_data['user_id']
                UpdateData(cdn)
                
            else:
                print("Inserted Record",file=sys.stderr)
                cdn.creation_date= datetime.now(tz)
                cdn.created_by= user_data['user_id']
                cdn.modified_by= user_data['user_id']
                InsertData(cdn)
            
            return jsonify({'response': "success","code":"200"})
        else:
            return jsonify({'message': 'Empty Row found'}), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addCDNDevices", methods = ['POST'])
@token_required
def AddCDNDevices(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()

        print(postData,file=sys.stderr)
        print(f"CDN Data received is:  {postData}", file=sys.stderr)
        for cdnObj in postData:
            if 'count' in cdnObj and  'technology' in cdnObj:
                cdn = CDN_Table()
                cdn.technology = cdnObj['technology']
                if 'count' in cdnObj:
                    cdn.count = cdnObj['count']
                    
                if CDN_Table.query.with_entities(CDN_Table.technology).filter_by(technology=cdnObj['technology']).first() is not None:
                    cdn.technology = CDN_Table.query.with_entities(CDN_Table.technology).filter_by(technology=cdnObj['technology']).first()[0]
                    print("Updated " + cdnObj['technology'],file=sys.stderr)
                    cdn.modification_date= datetime.now(tz)
                    cdn.modified_by= user_data['user_id']
                    UpdateData(cdn)
                else:
                    print("Inserted " +cdnObj['technology'],file=sys.stderr)
                    cdn.creation_date= datetime.now(tz)
                    cdn.modification_date= datetime.now(tz)
                    cdn.created_by= user_data['user_id']
                    cdn.modified_by= user_data['user_id']
                    InsertData(cdn)

        return jsonify({'response': "success","code":"200"})

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteCDNDevice",methods = ['POST'])
@token_required
def DeleteCDNDevice(user_data):
    if True:#session.get('token', None):
        cdnObj = request.get_json()
        print(cdnObj,file = sys.stderr)
        print(f"CDN   Dataa received is:  {cdnObj}", file=sys.stderr)

        for obj in cdnObj.get("technology"):
            cdnID = CDN_Table.query.filter(CDN_Table.technology==obj).first()
            print(cdnID,file=sys.stderr)
            if obj:
                db.session.delete(cdnID)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addCountRackIdDevices",methods =['GET'])
#@token_required
def AddCountRackIdDevices():
    if True:
        
        AddCountRackIdDevicesFunc()

        return jsonify({"RESPONSE":"OK"}),200
        
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
def AddCountRackIdDevicesFunc():
        '''
        queryString = f"select RACK_ID,count(DEVICE_ID) from device_table where RACK_ID in (select RACK_ID from phy_table) group by RACK_ID;"
        result = db.session.execute(queryString)
        
        obj = Rack_Table.query.all()
        if obj:
            for rack in obj:
                rack.total_count=0
                UpdateData(rack)
                print("Updated " + str(rack.rack_id)+ "with 0 value",file=sys.stderr)



        for row in result:
            rack_id = row[0]
            total_count = row[1]
            rack = Rack_Table()
            obj = Rack_Table.query.with_entities(Rack_Table.rack_id).filter_by(rack_id=rack_id).first()
            print(obj,file=sys.stderr)
            if  obj:
                rack.rack_id = obj.rack_id
                rack.total_count = total_count
                UpdateData(rack)
                print("Updated " + str(rack_id),file=sys.stderr)
        '''

        obj = Rack_Table.query.all()
        if obj:
            for rack in obj:
                queryString = f"select count(*) from device_table where RACK_ID='{rack.rack_id}' and STATUS!= 'Dismantle';"
                result = db.session.execute(queryString)
                count=0
                for row in result:
                    count = row[0]
                if count!= rack.total_count:
                    rack.total_count= count
                    rack.modification_date= datetime.now(tz)   
                    UpdateData(rack)
                    print("Updated Rack " + str(rack.rack_id),file=sys.stderr)

@app.route("/addCountSiteIdDevices",methods =['GET'])

def AddCountSiteIdDevices():
    if True:
        
        AddCountSiteIdDevicesFunc()
                

        return jsonify({"RESPONSE":"OK"}),200
        
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllDeviceIDs", methods = ['GET'])
@token_required
def GetAllDeviceIDs(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        deviceObjList=[]
        deviceObjs = Device_Table.query.with_entities(Device_Table.device_id).all()

        for deviceObj in deviceObjs:
            deviceObjList.append(str(deviceObj.device_id))

        return jsonify(deviceObjList), 200

@app.route("/addPowerData", methods = ['POST'])
@token_required
def AddPowerData(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        failed=False
        postData = request.get_json()

        print(postData,file=sys.stderr)

        for powerObj in postData:

            if Device_Table.query.with_entities(Device_Table.device_id).filter_by(device_id=powerObj['device_id']).first() != None:
                power = POWER_FEEDS_TABLE()

                if 'power_source_type' in powerObj:
                    power.power_source_type = powerObj['power_source_type']
                
                if 'number_of_power_sources' in powerObj:
                    power.number_of_power_sources = powerObj['number_of_power_sources']

                if 'psu1_fuse' in powerObj:
                    power.psu1_fuse = powerObj['psu1_fuse']

                if 'psu2_fuse' in powerObj:
                    power.psu2_fuse = powerObj['psu2_fuse']
                
                if 'psu3_fuse' in powerObj:
                    power.psu3_fuse = powerObj['psu3_fuse']

                if 'psu4_fuse' in powerObj:
                    power.psu4_fuse = powerObj['psu4_fuse']
                
                if 'psu5_fuse' in powerObj:
                    power.psu5_fuse = powerObj['psu5_fuse']

                if 'psu6_fuse' in powerObj:
                    power.psu6_fuse = powerObj['psu6_fuse']

                if 'psu1_pdu_details' in powerObj:
                    power.psu1_pdu_details = powerObj['psu1_pdu_details']

                if 'psu2_pdu_details' in powerObj:
                    power.psu2_pdu_details = powerObj['psu2_pdu_details']
                
                if 'psu3_pdu_details' in powerObj:
                    power.psu3_pdu_details = powerObj['psu3_pdu_details']

                if 'psu4_pdu_details' in powerObj:
                    power.psu4_pdu_details = powerObj['psu4_pdu_details']
                
                if 'psu5_pdu_details' in powerObj:
                    power.psu5_pdu_details = powerObj['psu5_pdu_details']

                if 'psu6_pdu_details' in powerObj:
                    power.psu6_pdu_details = powerObj['psu6_pdu_details']

                if 'psu1_dcdp_details' in powerObj:
                    power.psu1_dcdp_details = powerObj['psu1_dcdp_details']

                if 'psu2_dcdp_details' in powerObj:
                    power.psu2_dcdp_details = powerObj['psu2_dcdp_details']
                
                if 'psu3_dcdp_details' in powerObj:
                    power.psu3_dcdp_details = powerObj['psu3_dcdp_details']

                if 'psu4_dcdp_details' in powerObj:
                    power.psu4_dcdp_details = powerObj['psu4_dcdp_details']
                
                if 'psu5_dcdp_details' in powerObj:
                    power.psu5_dcdp_details = powerObj['psu5_dcdp_details']

                if 'psu6_dcdp_details' in powerObj:
                    power.psu6_dcdp_details = powerObj['psu6_dcdp_details']
                         
                deviceObj= Device_Table.query.with_entities(Device_Table.status).filter_by(device_id=powerObj['device_id']).first()
                if deviceObj:
                    power.status=  deviceObj[0]

                if POWER_FEEDS_TABLE.query.with_entities(POWER_FEEDS_TABLE).filter_by(device_id=powerObj['device_id']).first() is not None:
                    row= POWER_FEEDS_TABLE.query.with_entities(POWER_FEEDS_TABLE.device_id, POWER_FEEDS_TABLE.power_id).filter_by(device_id=powerObj['device_id']).first()
                    
                    power.device_id = row[0]
                    power.power_id= row[1]
                    power.modified_by= user_data['user_id']

                    print("Updated Power",file=sys.stderr)
                    UpdateData(power)

                #else:
                    
                #    if 'device_id' in powerObj:
                #        power.device_id = powerObj['device_id']

                #    print("Inserted " ,file=sys.stderr)
                #    InsertData(power)

            else:
                print("Device does not exists in devic table", file=sys.stderr)   
                failed= True
                    
        if failed:
            return jsonify({'response': "Some Devices does not exists in devic table",}), 500 
        else:
            return jsonify({'response': "success","code":"200"})
           
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
 
@app.route("/addPower", methods = ['POST'])
@token_required
def AddPower(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        failed=False
        powerObj = request.get_json()

        print(powerObj,file=sys.stderr)

        if Device_Table.query.with_entities(Device_Table.device_id).filter_by(device_id=powerObj['device_id']).first() != None:
            power = POWER_FEEDS_TABLE()

            if 'power_source_type' in powerObj:
                power.power_source_type = powerObj['power_source_type']
            
            if 'number_of_power_sources' in powerObj:
                power.number_of_power_sources = powerObj['number_of_power_sources']

            if 'psu1_fuse' in powerObj:
                power.psu1_fuse = powerObj['psu1_fuse']

            if 'psu2_fuse' in powerObj:
                power.psu2_fuse = powerObj['psu2_fuse']
            
            if 'psu3_fuse' in powerObj:
                power.psu3_fuse = powerObj['psu3_fuse']

            if 'psu4_fuse' in powerObj:
                power.psu4_fuse = powerObj['psu4_fuse']
            
            if 'psu5_fuse' in powerObj:
                power.psu5_fuse = powerObj['psu5_fuse']

            if 'psu6_fuse' in powerObj:
                power.psu6_fuse = powerObj['psu6_fuse']

            if 'psu1_pdu_details' in powerObj:
                power.psu1_pdu_details = powerObj['psu1_pdu_details']

            if 'psu2_pdu_details' in powerObj:
                power.psu2_pdu_details = powerObj['psu2_pdu_details']
            
            if 'psu3_pdu_details' in powerObj:
                power.psu3_pdu_details = powerObj['psu3_pdu_details']

            if 'psu4_pdu_details' in powerObj:
                power.psu4_pdu_details = powerObj['psu4_pdu_details']
            
            if 'psu5_pdu_details' in powerObj:
                power.psu5_pdu_details = powerObj['psu5_pdu_details']

            if 'psu6_pdu_details' in powerObj:
                power.psu6_pdu_details = powerObj['psu6_pdu_details']

            if 'psu1_dcdp_details' in powerObj:
                power.psu1_dcdp_details = powerObj['psu1_dcdp_details']

            if 'psu2_dcdp_details' in powerObj:
                power.psu2_dcdp_details = powerObj['psu2_dcdp_details']
            
            if 'psu3_dcdp_details' in powerObj:
                power.psu3_dcdp_details = powerObj['psu3_dcdp_details']

            if 'psu4_dcdp_details' in powerObj:
                power.psu4_dcdp_details = powerObj['psu4_dcdp_details']
            
            if 'psu5_dcdp_details' in powerObj:
                power.psu5_dcdp_details = powerObj['psu5_dcdp_details']

            if 'psu6_dcdp_details' in powerObj:
                power.psu6_dcdp_details = powerObj['psu6_dcdp_details']

            deviceObj= Device_Table.query.with_entities(Device_Table.status).filter_by(device_id=powerObj['device_id']).first()
            if deviceObj:
               power.status=  deviceObj[0]

            if POWER_FEEDS_TABLE.query.with_entities(POWER_FEEDS_TABLE).filter_by(device_id=powerObj['device_id']).first() is not None:
                row= POWER_FEEDS_TABLE.query.with_entities(POWER_FEEDS_TABLE.device_id,POWER_FEEDS_TABLE.power_id).filter_by(device_id=powerObj['device_id']).first()
            
                power.device_id = row[0]
                power.power_id= row[1]

                print("Updated ",file=sys.stderr)
                power.modified_by= user_data['user_id']
                UpdateData(power)
            #else:
            #    
            #    if 'device_id' in powerObj:
            #        power.device_id = powerObj['device_id']

            #    print("Inserted " +powerObj['device_id'],file=sys.stderr)
            #    InsertData(power)

        else:
            print("Error occured in Adding Power", file=sys.stderr)   
            failed= True
                
        if failed:
            return jsonify({'response': "Error occured in Adding Power",}), 500 
        else:
            return jsonify({'response': "success","code":"200"})
           
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401
 
@app.route("/getPower", methods = ['GET'])
@token_required
def GetAllPower(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        powerObjList=[]
        powerObjs = POWER_FEEDS_TABLE.query.all()

        for powerObj in powerObjs:
            if powerObj.status!='Dismantle':
                powerDataDict= {}
                powerDataDict['power_id'] = powerObj.power_id
                powerDataDict['device_id'] = powerObj.device_id
                #powerDataDict['site_id'] = powerObj.site_id
                #powerDataDict['rack_id'] = powerObj.rack_id
                powerDataDict['power_source_type'] = powerObj.power_source_type
                powerDataDict['number_of_power_sources'] = powerObj.number_of_power_sources
                powerDataDict['psu1_fuse'] = powerObj.psu1_fuse
                powerDataDict['psu2_fuse'] = powerObj.psu2_fuse
                powerDataDict['psu3_fuse'] = powerObj.psu3_fuse
                powerDataDict['psu4_fuse'] = powerObj.psu4_fuse
                powerDataDict['psu5_fuse'] = powerObj.psu5_fuse
                powerDataDict['psu6_fuse'] = powerObj.psu6_fuse
                powerDataDict['psu1_pdu_details'] = powerObj.psu1_pdu_details
                powerDataDict['psu2_pdu_details'] = powerObj.psu2_pdu_details
                powerDataDict['psu3_pdu_details'] = powerObj.psu3_pdu_details
                powerDataDict['psu4_pdu_details'] = powerObj.psu4_pdu_details
                powerDataDict['psu5_pdu_details'] = powerObj.psu5_pdu_details
                powerDataDict['psu6_pdu_details'] = powerObj.psu6_pdu_details
                powerDataDict['psu1_dcdp_details'] = powerObj.psu1_dcdp_details
                powerDataDict['psu2_dcdp_details'] = powerObj.psu2_dcdp_details
                powerDataDict['psu3_dcdp_details'] = powerObj.psu3_dcdp_details
                powerDataDict['psu4_dcdp_details'] = powerObj.psu4_dcdp_details
                powerDataDict['psu5_dcdp_details'] = powerObj.psu5_dcdp_details
                powerDataDict['psu6_dcdp_details'] = powerObj.psu6_dcdp_details
                powerDataDict['status'] = powerObj.status
                powerDataDict['created_by'] = powerObj.created_by
                powerDataDict['modified_by'] = powerObj.modified_by
                        
                powerObjList.append(powerDataDict)

        content = gzip.compress(json.dumps(powerObjList).encode('utf8'), 5)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deletePower",methods = ['POST'])
@token_required
def DeletePower(user_data):
    if True:#session.get('token', None):
        cdnObj = request.get_json()
        print(cdnObj,file = sys.stderr)
        print(f"Power Dataa received is:  {cdnObj}", file=sys.stderr)

        for obj in cdnObj.get("power_ids"):
            powerId = POWER_FEEDS_TABLE.query.filter(POWER_FEEDS_TABLE.power_id==obj).first()
            print(powerId,file=sys.stderr)
            if obj:
                db.session.delete(powerId)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

def AddCountSiteIdDevicesFunc():
    #queryString = f"select SITE_ID,count(DEVICE_ID) from device_table group by SITE_ID;"
    #result = db.session.execute(queryString)

    obj = Phy_Table.query.all()
    if obj:
        for site in obj:
            #if site.site_id=="ADAM":
            #site.total_count=0
            queryString = f"select count(*) from device_table where SITE_ID='{site.site_id}' and STATUS!= 'Dismantle';"
            result = db.session.execute(queryString)
            count=0
            for row in result:
                count = row[0]
            if count!= site.total_count:
                site.total_count= count
                site.modification_date= datetime.now(tz)   
                UpdateData(site)
                print("Updated site " + str(site.site_id),file=sys.stderr)


    '''
    for row in result:
        site_id = row[0]
        total_count = row[1]
        site = Phy_Table()
        obj = Phy_Table.query.with_entities(Phy_Table.site_id).filter_by(site_id=site_id).first()
        if obj:
            site.site_id=obj.site_id
            site.total_count = total_count
            UpdateData(site)
            print("Updated "+ site_id,file=sys.stderr)
    '''
@app.route("/powerOffOnBoardedDevice", methods = ['POST'])
@token_required
def PowerOffOnBoardDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        deviceIDs = request.get_json()
        print(deviceIDs, file=sys.stderr)
        for ip in deviceIDs['ips']:
            
            seedObj = db.session.query(Seed).filter_by(ne_ip_address=ip).first()
            if seedObj:
                seedObj.onboard_status = 'false'
                seedObj.operation_status='Powered Off'
                seedObj.modified_by = user_data['user_id']
                UpdateData(seedObj)

            deviceObj = db.session.query(Device_Table).filter_by(ne_ip_address=ip).first()

            #change status to Dismantle in device table
            if deviceObj:
                deviceObj.status = 'Powered Off'
                deviceObj.ims_status = 'Offline'
                deviceObj.modification_date= datetime.now(tz)
                deviceObj.modified_by = user_data['user_id']
                UpdateData(deviceObj)  
            
            if deviceObj:
                #change all board status
                boardObjs = db.session.query(Board_Table).filter_by(device_id=deviceObj.device_id)
                if boardObjs:
                    for boardObj in boardObjs:
                        boardObj.status = 'Powered Off'
                        boardObj.modification_date= datetime.now(tz)
                        boardObj.modified_by = user_data['user_id']
                        UpdateData(boardObj) 

                
                #change all sub-board status
                subboardObjs = db.session.query(Subboard_Table).filter_by(device_id=deviceObj.device_id)
                if subboardObjs:
                    for subboardObj in subboardObjs:
                        subboardObj.status = 'Powered Off'
                        subboardObj.modification_date= datetime.now(tz)
                        subboardObj.modified_by = user_data['user_id']
                        UpdateData(subboardObj) 
                        
                # change all SFP status 
                sfpObjs = db.session.query(SFP_Table).filter_by(device_id=deviceObj.device_id)
                if sfpObjs:
                    for sfpObjs in sfpObjs:
                        sfpObjs.status = 'Powered Off'
                        sfpObjs.modification_date= datetime.now(tz)
                        sfpObjs.modified_by = user_data['user_id']
                        UpdateData(sfpObjs)
                
                powerObj = db.session.query(POWER_FEEDS_TABLE).filter_by(device_id=deviceObj.device_id).first()
                if powerObj:
                    powerObj.status = 'Powered Off'
                    powerObj.modified_by = user_data['user_id']
                    UpdateData(powerObj)
                
                licenseObjs = db.session.query(License_Table).filter_by(ne_name=deviceObj.device_name)
                if deviceObj and licenseObjs:
                    for licenseObj in licenseObjs:
                        licenseObj.status = 'Powered Off'
                        licenseObj.modification_date= datetime.now(tz)
                        licenseObj.modified_by = user_data['user_id']
                        UpdateData(licenseObj) 

        return jsonify("success"), 200
    
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/offloadOnBoardedDevice", methods = ['POST'])
@token_required
def OffloadOnBoardDevice(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        deviceIDs = request.get_json()
        print(deviceIDs, file=sys.stderr)
        for ip in deviceIDs['ips']:

            seedObj = db.session.query(Seed).filter_by(ne_ip_address=ip).first()
            if seedObj:
                seedObj.onboard_status = 'false'
                seedObj.operation_status='Offloaded'
                seedObj.modified_by = user_data['user_id']
                UpdateData(seedObj)

            deviceObj = db.session.query(Device_Table).filter_by(ne_ip_address=ip).first()
            if deviceObj:
                #change status to Dismantle in device table
                deviceObj.status = 'Offloaded'
                deviceObj.ims_status = 'Active'
                deviceObj.modification_date= datetime.now(tz)
                deviceObj.modified_by = user_data['user_id']
                UpdateData(deviceObj)  

            if deviceObj:
            #change all board status
                boardObjs = db.session.query(Board_Table).filter_by(device_id=deviceObj.device_id)
                if boardObjs:
                    for boardObj in boardObjs:
                        boardObj.status = 'Offloaded'
                        boardObj.modification_date= datetime.now(tz)
                        boardObj.modified_by = user_data['user_id']
                        UpdateData(boardObj) 

                
                #change all sub-board status
                subboardObjs = db.session.query(Subboard_Table).filter_by(device_id=deviceObj.device_id)
                if subboardObjs:
                    for subboardObj in subboardObjs:
                        subboardObj.status = 'Offloaded'
                        subboardObj.modification_date= datetime.now(tz)
                        subboardObj.modified_by = user_data['user_id']
                        UpdateData(subboardObj) 
                    
                # change all SFP status 
                sfpObjs = db.session.query(SFP_Table).filter_by(device_id=deviceObj.device_id)
                if sfpObjs:
                    for sfpObjs in sfpObjs:
                        sfpObjs.status = 'Offloaded'
                        sfpObjs.modification_date= datetime.now(tz)
                        sfpObjs.modified_by = user_data['user_id']
                        UpdateData(sfpObjs)
                    
                powerObj = db.session.query(POWER_FEEDS_TABLE).filter_by(device_id=deviceObj.device_id).first()
                if powerObj:
                    powerObj.status = 'Offloaded'
                    powerObj.modified_by = user_data['user_id']
                    UpdateData(powerObj)
                
                licenseObjs = db.session.query(License_Table).filter_by(ne_name=deviceObj.device_name)
                if deviceObj and licenseObjs:
                    for licenseObj in licenseObjs:
                        licenseObj.status = 'Offloaded'
                        licenseObj.modification_date= datetime.now(tz)
                        licenseObj.modified_by = user_data['user_id']
                        UpdateData(licenseObj)   

        return jsonify("success"), 200
    
@app.route("/syncFromInventoryPowerFeed", methods = ['GET'])
@token_required
def SyncFromInventoryPowerFeed(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        queryString = "select DEVICE_ID, status from device_table where `FUNCTION`!='Access Point';"
        result = db.session.execute(queryString)
        
        print(result,file=sys.stderr)
        
        for row in result:
            device_id = row[0]
            #rack_id = row[1]
            #site_id = row[2]
            status= row[1]
            power_feed = POWER_FEEDS_TABLE()
            power_feed.device_id = device_id
            power_feed.status = status
            #power_feed.rack_id = rack_id
            #power_feed.site_id = site_id
            if POWER_FEEDS_TABLE.query.with_entities(POWER_FEEDS_TABLE.power_id).filter_by(device_id=device_id).first() is None:        
                print("Inserted " +device_id,file=sys.stderr)
                power_feed.creation_date= datetime.now(tz)
                power_feed.modification_date= datetime.now(tz)
                InsertData(power_feed)
            else:
                powerObj=  POWER_FEEDS_TABLE.query.with_entities(POWER_FEEDS_TABLE.power_id).filter_by(device_id=device_id).first()[0]
                power_feed.power_id = powerObj
                print("Updated " + device_id,file=sys.stderr)
                power_feed.modification_date= datetime.now(tz)
                UpdateData(power_feed)
        return ("SUCCESS"), 200

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route('/addDeviceToSeed',methods = ['GET'])
def AddDeviceToSeed():
    if True:
        try:
            count=0
            ips = []
            queryString = f"select NE_IP_ADDRESS from device_table where NE_IP_ADDRESS not in (select NE_IP_ADDRESS from seed_table);"
            result = db.session.execute(queryString)
            for row in result:
                ips.append(row[0])
            for ne_ip_address in ips:
                seed = Seed()
                deviceObjs = Device_Table.query.filter(Device_Table.ne_ip_address==ne_ip_address).all()
                for deviceObj in deviceObjs:
                    try:
                        print(deviceObj.site_id,file=sys.stderr)
                        seed.site_id = deviceObj.site_id
                        seed.rack_id = deviceObj.rack_id
                        seed.rfs_date = deviceObj.rfs_date
                        seed.tag_id = deviceObj.tag_id
                        seed.device_id = deviceObj.device_id
                        seed.ne_ip_address = deviceObj.ne_ip_address
                        seed.device_ru = deviceObj.ru
                        seed.department = deviceObj.department
                        seed.section = deviceObj.section
                        seed.criticality = deviceObj.criticality
                        seed.function = deviceObj.function
                        seed.cisco_domain = deviceObj.cisco_domain
                        seed.virtual = deviceObj.virtual
                        seed.authentication = deviceObj.authentication
                        seed.subrack_id_number = deviceObj.subrack_id_number
                        seed.hostname = deviceObj.device_name
                        # seed.sw_type = deviceObj.sw_type
                        seed.vendor = deviceObj.manufacturer
                        seed.asset_type = ''
                        if deviceObj.status!='Production':
                            seed.onboard_status = 'false'
                        else:
                            seed.onboard_status = 'true'
                        seed.operation_status = deviceObj.status
                        seed.site_type = deviceObj.site_type
                        seed.contract_number = deviceObj.contract_number
                        seed.contract_expiry = deviceObj.contract_expiry
                        seed.item_code = deviceObj.item_code
                        seed.item_desc = deviceObj.item_desc
                        seed.clei = deviceObj.clei
                        seed.parent = deviceObj.parent
                        #seed.vuln_fix_plan_status = deviceObj.vuln_fix_plan_status
                        #seed.vuln_ops_severity = deviceObj.vuln_ops_severity
                        seed.integrated_with_aaa = deviceObj.integrated_with_aaa
                        seed.integrated_with_paam = deviceObj.integrated_with_paam
                        seed.approved_mbss =  deviceObj.approved_mbss 
                        seed.mbss_implemented = deviceObj.mbss_implemented
                        seed.mbss_integration_check = deviceObj.mbss_integration_check
                        seed.integrated_with_siem = deviceObj.integrated_with_siem
                        seed.threat_cases = deviceObj.threat_cases
                        seed.vulnerability_scanning = deviceObj.vulnerability_scanning
                        seed.vulnerability_severity = deviceObj.vulnerability_severity
                        
 
                        InsertData(seed)
                        count+=1
                        print(f"{seed.ne_ip_address} INSERTED SUCCESSFULLY IN DB FROM DEVICE",file=sys.stderr)

                    except Exception as e:
                        print("Exception Occured", file=sys.stderr)                
            print(f"Final COunt Updated is {count}" ,file=sys.stderr)
            return jsonify({"Response":"OK"}),200
        except Exception as e:
            print(str(e),file=sys.stderr)
            traceback.print_exc()
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route('/addRebd',methods = ['POST'])
@token_required
def AddRebd(user_data):
    if True:
        try:
            response = False
            rebdObj = request.get_json()
            print(rebdObj,file=sys.stderr)
            #if Phy_Table.query.with_entities(Phy_Table.site_id).filter_by(site_id=rebdObj['site_id']).first() != None and Rack_Table.query.with_entities(Rack_Table.rack_id).filter_by(rack_id=rebdObj['rack_id']).first() != None:
            rebd = Rebd_Table()
            rebd.site_id = rebdObj['site_id']  
            rebd.rack_id = rebdObj['rack_id']
            rebd.region = rebdObj['region']
            rebd.latitude = rebdObj['latitude']
            rebd.longitude = rebdObj['longitude']
            rebd.city = rebdObj['city']
            rebd.floor = rebdObj['floor']
            rebd.serial_number = rebdObj['serial_number']
            rebd.pn_code = rebdObj['pn_code']
            rebd.tag_id = rebdObj['tag_id']
            rebd.rfs_date = FormatStringDate(rebdObj['rfs_date'])
            rebd.device_id = rebdObj['device_id']
            rebd.ne_ip_address = rebdObj['ne_ip_address']
            if str(rebdObj['device_ru']).isdigit():
                rebd.device_ru = (rebdObj['device_ru'])
            rebd.department = rebdObj['department']
            rebd.section = rebdObj['section']
            rebd.criticality = rebdObj['criticality']
            rebd.function = rebdObj['function']
            rebd.domain = rebdObj['domain']
            rebd.virtual = rebdObj['virtual']
            rebd.authentication = rebdObj['authentication']
            rebd.hostname = rebdObj['hostname']
            rebd.sw_type = rebdObj['sw_type']
            rebd.vendor = rebdObj['vendor']
            rebd.operation_status = rebdObj['operation_status']
            rebd.site_type = rebdObj['site_type']
            rebd.contract_expiry = FormatStringDate(rebdObj['contract_expiry'])
            rebd.contract_number = rebdObj['contract_number']
            if str(rebdObj['stack']).isdigit():
                rebd.stack = rebdObj['stack']
            if Rebd_Table.query.with_entities(Rebd_Table.rebd_id).filter_by(ne_ip_address=rebdObj['ne_ip_address']).first() is not None:
                rebd.rebd_id = Rebd_Table.query.with_entities(Rebd_Table.rebd_id).filter_by(ne_ip_address=rebdObj['ne_ip_address']).first()[0]
                rebd.modification_date= datetime.now(tz)
                rebd.modified_by= user_data['user_id']
                UpdateData(rebd)
                print(f"Updated {rebd.ne_ip_address} Successfully",file=sys.stderr)
                response = True
            else:
                print(f"Inserted {rebd.ne_ip_address} Successfully",file=sys.stderr)

                rebd.modification_date= datetime.now(tz)
                rebd.creation_date= datetime.now(tz)
                rebd.created_by= user_data['user_id']
                rebd.modified_by= user_data['user_id']
                InsertData(rebd)
                print(f"Inserted {rebd.ne_ip_address} Successfully",file=sys.stderr)
                response =  True
            
            return jsonify({'response': "success"}),200
            #else:
            #    print("Rack ID or Site ID does not exists", file=sys.stderr)   
            #if response==True:
            #    return jsonify({'response': "Rack Id or Site Id does not Exists"}), 500 
                
        except Exception as e:
            print(str(e),file=sys.stderr)
            traceback.print_exc()
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/addRebds',methods = ['POST'])
@token_required
def AddRebds(user_data):
    if True:
        try:
            rebdObjs = request.get_json()
            response = False
            for rebdObj in rebdObjs:

            #if Phy_Table.query.with_entities(Phy_Table.site_id).filter_by(site_id=rebdObj['site_id']).first() != None and Rack_Table.query.with_entities(Rack_Table.rack_id).filter_by(rack_id=rebdObj['rack_id']).first() != None:
                rebd = Rebd_Table()
                if 'site_id' in rebdObj:
                    rebd.site_id = rebdObj['site_id']
                if 'rack_id' in rebdObj:
                    rebd.rack_id = rebdObj['rack_id']
                if 'region' in rebdObj:
                    rebd.region = rebdObj['region']
                if 'latitude' in rebdObj:
                    rebd.latitude = rebdObj['latitude']
                if 'longitude' in rebdObj:    
                    rebd.longitude = rebdObj['longitude']
                if 'city' in rebdObj:    
                    rebd.city = rebdObj['city']
                if 'floor' in rebdObj:    
                    rebd.floor = rebdObj['floor']
                if 'serial_number' in rebdObj:    
                    rebd.serial_number = rebdObj['serial_number']
                if 'pn_code' in rebdObj:    
                    rebd.pn_code = rebdObj['pn_code']
                if 'tag_id' in rebdObj:
                    rebd.tag_id = rebdObj['tag_id']
                if 'rfs_date' in rebdObj:
                    rebd.rfs_date = FormatStringDate(rebdObj['rfs_date'])
                if 'device_id' in rebdObj:
                    rebd.device_id = rebdObj['device_id']
                if 'ne_ip_address' in rebdObj:
                    rebd.ne_ip_address = rebdObj['ne_ip_address']
                if 'device_ru' in rebdObj:
                    if str(rebdObj['device_ru']).isdigit():
                        rebd.device_ru = (rebdObj['device_ru'])
                if 'department' in rebdObj:
                    rebd.department = rebdObj['department']
                if 'section' in rebdObj:
                    rebd.section = rebdObj['section']
                if 'criticality' in rebdObj:
                    rebd.criticality = rebdObj['criticality']
                if 'function' in rebdObj:
                    rebd.function = rebdObj['function']
                if 'domain' in rebdObj:
                    rebd.domain = rebdObj['domain']
                if 'virtual' in rebdObj:
                    rebd.virtual = rebdObj['virtual']
                if 'authentication' in rebdObj:
                    rebd.authentication = rebdObj['authentication']
                if 'hostname' in rebdObj:
                    rebd.hostname = rebdObj['hostname']
                if 'sw_type' in rebdObj:
                    rebd.sw_type = rebdObj['sw_type']
                if 'vendor' in rebdObj:
                    rebd.vendor = rebdObj['vendor']
                if 'operation_status' in rebdObj:
                    rebd.operation_status = rebdObj['operation_status']
                if 'site_type' in rebdObj:
                    rebd.site_type = rebdObj['site_type']
                if 'contract_expiry' in rebdObj:
                    rebd.contract_expiry = FormatStringDate(rebdObj['contract_expiry'])
                if 'contract_number' in rebdObj:
                    rebd.contract_number = rebdObj['contract_number']
                if 'stack' in rebdObj:
                    if str(rebdObj['stack']).isdigit():
                        rebd.stack = rebdObj['stack']
                
                if Rebd_Table.query.with_entities(Rebd_Table.rebd_id).filter_by(ne_ip_address=rebdObj['ne_ip_address']).first() is not None:
                    rebd.rebd_id = Rebd_Table.query.with_entities(Rebd_Table.rebd_id).filter_by(ne_ip_address=rebdObj['ne_ip_address']).first()[0]
                    rebd.modification_date= datetime.now(tz)
                    rebd.modified_by= user_data['user_id']
                    UpdateData(rebd)
                    print(f"Updated {rebd.ne_ip_address} Successfully",file=sys.stderr)
                    response = True
                else:
                    rebd.modification_date= datetime.now(tz)
                    rebd.creation_date= datetime.now(tz)
                    rebd.created_by= user_data['user_id']
                    rebd.modified_by= user_data['user_id']
                    InsertData(rebd)
                    print(f"Inserted {rebd.ne_ip_address} Successfully",file=sys.stderr)
                    response = True
                
                #else:
                #    print("Rack ID or Site ID does not exists", file=sys.stderr)   
                #    return jsonify({'response': "Rack Id or Site Id does not Exists"}), 500 
            if response==True:
                return jsonify({'response': "success"}),200
        except Exception as e:
            print(str(e),file=sys.stderr)
            traceback.print_exc()
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route('/getAllRebds',methods = ['GET'])
@token_required
def GetAllRebds(user_data):
    if True:
        try:
            objList = []
            rebdObj  = Rebd_Table.query.all()
            for rebdObj in rebdObj:
                objDict = {}
                objDict['site_id'] = rebdObj.site_id
                objDict['rack_id'] = rebdObj.rack_id
                objDict['region'] = rebdObj.region
                objDict['latitude'] = rebdObj.latitude
                objDict['longitude'] = rebdObj.longitude
                objDict['city'] = rebdObj.city
                objDict['floor'] = rebdObj.floor
                objDict['serial_number'] = rebdObj.serial_number
                objDict['pn_code'] = rebdObj.pn_code
                objDict['tag_id'] = rebdObj.tag_id
                objDict['rfs_date'] = FormatDate(rebdObj.rfs_date)
                objDict['device_id'] = rebdObj.device_id
                objDict['ne_ip_address'] = rebdObj.ne_ip_address
                objDict['device_ru'] = rebdObj.device_ru
                objDict['department'] = rebdObj.department
                objDict['section'] = rebdObj.section
                objDict['criticality'] = rebdObj.criticality
                objDict['function'] = rebdObj.function
                objDict['domain'] = rebdObj.domain
                objDict['virtual'] = rebdObj.virtual
                objDict['authentication'] = rebdObj.authentication
                objDict['hostname'] = rebdObj.hostname
                objDict['sw_type'] = rebdObj.sw_type
                objDict['vendor'] = rebdObj.vendor
                objDict['operation_status'] = rebdObj.operation_status
                objDict['site_type'] = rebdObj.site_type
                objDict['contract_expiry'] = FormatDate(rebdObj.contract_expiry)
                objDict['contract_number'] = rebdObj.contract_number
                objDict['stack'] = rebdObj.stack
                objDict['modification_date'] = rebdObj.modification_date
                objDict['creation_date'] = rebdObj.creation_date
                objDict['created_by'] = rebdObj.created_by
                objDict['modified_by'] = rebdObj.modified_by

                objList.append(objDict)
            return jsonify(objList),200
        except Exception as e:
            print(str(e),file=sys.stderr)
            traceback.print_exc()
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteRebd",methods = ['POST'])
@token_required
def DeleteRebd(user_data):
    if True:#session.get('token', None):
        rebdObj = request.get_json()
        print(rebdObj,file = sys.stderr)
        print(f"Rebd Data received is:  {rebdObj}", file=sys.stderr)

        for obj in rebdObj.get("ne_ip_address"):
            rebdID = Rebd_Table.query.filter(Rebd_Table.ne_ip_address==obj).first()
            print(rebdID,file=sys.stderr)
            if obj:
                db.session.delete(rebdID)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/addPos',methods = ['POST'])
@token_required
def AddPos(user_data):
    if True:
        try:
            posObj = request.get_json()
            #if Phy_Table.query.with_entities(Phy_Table.site_id).filter_by(site_id=posObj['site_id']).first() != None and Rack_Table.query.with_entities(Rack_Table.rack_id).filter_by(rack_id=posObj['rack_id']).first() != None:
            pos = Pos_Table()
            pos.site_id = posObj['site_id']
            pos.region = posObj['region']
            pos.latitude = posObj['latitude']
            pos.longitude = posObj['longitude']
            pos.city = posObj['city']
            pos.floor = posObj['floor']
            pos.serial_number= posObj['serial_number']
            pos.pn_code  = posObj['pn_code']
            pos.rack_id = posObj['rack_id']
            pos.tag_id = posObj['tag_id']
            pos.rfs_date = FormatStringDate(posObj['rfs_date'])
            pos.device_id = posObj['device_id']
            pos.ne_ip_address = posObj['ne_ip_address']
            if str(posObj['device_ru']).isdigit():
                pos.device_ru = (posObj['device_ru'])
            pos.department = posObj['department']
            pos.section = posObj['section']
            pos.criticality = posObj['criticality']
            pos.function = posObj['function']
            pos.domain = posObj['domain']
            pos.virtual = posObj['virtual']
            pos.authentication = posObj['authentication']
            pos.hostname = posObj['hostname']
            pos.sw_type = posObj['sw_type']
            pos.vendor = posObj['vendor']
            pos.operation_status = posObj['operation_status']
            pos.site_type = posObj['site_type']
            pos.contract_expiry = FormatStringDate(posObj['contract_expiry'])
            pos.contract_number = posObj['contract_number']
            #pos.subrack_id_number = posObj['subrack_id_number']
            #pos.asset_type = posObj['asset_type']
            if str(posObj['stack']).isdigit():
                pos.stack = posObj['stack']
            
            
            if Pos_Table.query.with_entities(Pos_Table.pos_id).filter_by(ne_ip_address=posObj['ne_ip_address']).first() is not None:
                pos.pos_id = Pos_Table.query.with_entities(Pos_Table.pos_id).filter_by(ne_ip_address=posObj['ne_ip_address']).first()[0]
                pos.modification_date= datetime.now(tz)
                pos.modified_by= user_data['user_id']
                UpdateData(pos)
                print(f"Updated {pos.ne_ip_address} Successfully",file=sys.stderr)
            else:
                print(f"Inserted {pos.ne_ip_address} Successfully",file=sys.stderr)
                pos.modification_date= datetime.now(tz)
                pos.creation_date= datetime.now(tz)
                pos.created_by= user_data['user_id']
                pos.modified_by= user_data['user_id']
                InsertData(pos)
            return jsonify({'response': "success"}),200
        # else:
        #         print("Rack ID or Site ID does not exists", file=sys.stderr)   
        #         return jsonify({'response': "Rack Id or Site Id does not Exists"}), 500 

        except Exception as e:
            print(str(e),file=sys.stderr)
            traceback.print_exc()
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route('/addPoss',methods = ['POST'])
@token_required
def AddPoss(user_data):
    if True:
        try:
            posObjs = request.get_json()
            print(posObjs,file=sys.stderr)
            response = False
            for posObj in posObjs:

                #if Phy_Table.query.with_entities(Phy_Table.site_id).filter_by(site_id=posObj['site_id']).first() != None and Rack_Table.query.with_entities(Rack_Table.rack_id).filter_by(rack_id=posObj['rack_id']).first() != None:
                pos = Pos_Table()
                if 'site_id' in posObj:
                    pos.site_id = posObj['site_id']
                
                if 'rack_id' in posObj:
                    pos.rack_id = posObj['rack_id']
                if 'region' in posObj:
                    pos.region = posObj['region']
                if 'latitude' in posObj:
                    pos.latitude = posObj['latitude']
                if 'longitude' in posObj:
                    pos.longitude = posObj['longitude']
                if 'city' in posObj:
                    pos.city = posObj['city']
                if 'floor' in posObj:
                    pos.floor = posObj['floor']
                if 'serial_number' in posObj:
                    pos.serial_number= posObj['serial_number']
                if 'pn_code' in posObj:
                    pos.pn_code  = posObj['pn_code']
                if 'tag_id' in posObj:
                    pos.tag_id = posObj['tag_id']
                if 'rfs_date' in posObj:
                    pos.rfs_date = FormatStringDate(posObj['rfs_date'])
                if 'device_id' in posObj:
                    pos.device_id = posObj['device_id']
                if 'ne_ip_address' in posObj:
                    pos.ne_ip_address = posObj['ne_ip_address']
                if 'device_ru' in posObj:
                    if str(posObj['device_ru']).isdigit():
                        pos.device_ru = (posObj['device_ru'])
                if 'department' in posObj:
                    pos.department = posObj['department']
                if 'section' in posObj:
                    pos.section = posObj['section']
                if 'criticality' in posObj:
                    pos.criticality = posObj['criticality']
                if 'function' in posObj:
                    pos.function = posObj['function']
                if 'domain' in posObj:
                    pos.domain = posObj['domain']
                if 'virtual' in posObj:
                    pos.virtual = posObj['virtual']
                if 'authentication' in posObj:
                    pos.authentication = posObj['authentication']
                if 'hostname' in posObj:
                    pos.hostname = posObj['hostname']
                if 'sw_type' in posObj:
                    pos.sw_type = posObj['sw_type']
                if 'vendor' in posObj:
                    pos.vendor = posObj['vendor']
                if 'operation_status' in posObj:
                    pos.operation_status = posObj['operation_status']
                if 'site_type' in posObj:
                    pos.site_type = posObj['site_type']
                if 'contract_expiry' in posObj:
                    pos.contract_expiry = FormatStringDate(posObj['contract_expiry'])
                if 'contract_number' in posObj:
                    pos.contract_number = posObj['contract_number']
                # if 'subrack_id_number' in posObj:
                #     pos.subrack_id_number = posObj['subrack_id_number']
                # if 'asset_type' in posObj:
                #     pos.asset_type = posObj['asset_type']
                if 'stack' in posObj:

                    if str(posObj['stack']).isdigit():
                        pos.stack = posObj['stack']
                    
                else:
                    pos.stack = 0
                if Pos_Table.query.with_entities(Pos_Table.pos_id).filter_by(ne_ip_address=posObj['ne_ip_address']).first() is not None:
                    pos.pos_id = Pos_Table.query.with_entities(Pos_Table.pos_id).filter_by(ne_ip_address=posObj['ne_ip_address']).first()[0]
                    pos.modification_date= datetime.now(tz)
                    pos.modified_by= user_data['user_id']
                    UpdateData(pos)
                    print(f"Updated {pos.ne_ip_address} Successfully",file=sys.stderr)
                    response = True
                    
                else:
                    print(f"Inserted {pos.ne_ip_address} Successfully",file=sys.stderr)
                    pos.modification_date= datetime.now(tz)
                    pos.creation_date= datetime.now(tz)
                    pos.created_by= user_data['user_id']
                    pos.modified_by= user_data['user_id']
                    InsertData(pos)
                    response = True
                
            # else:
            #     print("Rack ID or Site ID does not exists", file=sys.stderr)   
            #     return jsonify({'response': "Rack Id or Site Id does not Exists"}), 500 
            if response==True:

                return jsonify({'response': "success"}),200
        except Exception as e:
            print(str(e),file=sys.stderr)
            traceback.print_exc()
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route('/getAllPoss',methods = ['GET'])
@token_required
def GetAllPoss(user_data):
    if True:
        try:
            objList = []
            posObjs  = Pos_Table.query.all()
            for posObj in posObjs:
                objDict = {}
                objDict['site_id'] = posObj.site_id
                objDict['rack_id'] = posObj.rack_id
                objDict['region'] = posObj.region
                objDict['latitude'] = posObj.latitude
                objDict['longitude'] = posObj.longitude
                objDict['city'] = posObj.city
                objDict['floor'] = posObj.floor
                objDict['serial_number'] = posObj.serial_number
                objDict['pn_code'] = posObj.pn_code
                objDict['tag_id'] = posObj.tag_id
                objDict['rfs_date'] = FormatDate(posObj.rfs_date)
                objDict['device_id'] = posObj.device_id
                objDict['ne_ip_address'] = posObj.ne_ip_address
                objDict['device_ru'] = posObj.device_ru
                objDict['department'] = posObj.department
                objDict['section'] = posObj.section
                objDict['criticality'] = posObj.criticality
                objDict['function'] = posObj.function
                objDict['domain'] = posObj.domain
                objDict['virtual'] = posObj.virtual
                objDict['authentication'] = posObj.authentication
                objDict['hostname'] = posObj.hostname
                objDict['sw_type'] = posObj.sw_type
                objDict['vendor'] = posObj.vendor
                objDict['operation_status'] = posObj.operation_status
                objDict['site_type'] = posObj.site_type
                objDict['contract_expiry'] = FormatDate(posObj.contract_expiry)
                objDict['contract_number'] = posObj.contract_number
                objDict['stack'] = posObj.stack
                #objDict['asset_type'] = posObj.asset_type
                objDict['modification_date'] = posObj.modification_date
                objDict['creation_date'] = posObj.creation_date
                objDict['created_by'] = posObj.created_by
                objDict['modified_by'] = posObj.modified_by
                objList.append(objDict)
            return jsonify(objList),200
        except Exception as e:
            print(str(e),file=sys.stderr)
            traceback.print_exc()
            return str(e),500
    else:
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deletePos",methods = ['POST'])
@token_required
def DeletePos(user_data):
    if True:#session.get('token', None):
        posObj = request.get_json()
        print(posObj,file = sys.stderr)
        print(f"Pos Data received is:  {posObj}", file=sys.stderr)

        for obj in posObj.get("ne_ip_address"):
            posID = Pos_Table.query.filter(Pos_Table.ne_ip_address==obj).first()
            print(posID,file=sys.stderr)
            if obj:
                db.session.delete(posID)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addFunction",methods = ['POST'])
@token_required
def AddFunction(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        funObj = request.get_json()

        print(funObj, file=sys.stderr)
        fun = FUNCTIONS_TABLE()
        if funObj['tfun'] and funObj['function'] :
            fun.tfun = funObj['tfun']
            fun.function = funObj['function']
            
                    
            if FUNCTIONS_TABLE.query.with_entities(FUNCTIONS_TABLE.tfun).filter_by(tfun=funObj['tfun']).first() is not None:
                fun_id = FUNCTIONS_TABLE.query.with_entities(FUNCTIONS_TABLE.function_id).filter_by(tfun=funObj['tfun']).first()
                fun.function_id = fun_id[0]
                print(f"Updated {funObj['tfun']}",file=sys.stderr)
                fun.modification_date= datetime.now(tz)
                fun.modified_by= user_data['user_id']
                UpdateData(fun)
                
            else:
                print("Inserted Record",file=sys.stderr)
                fun.creation_date= datetime.now(tz)
                fun.modification_date= datetime.now(tz)
                fun.created_by= user_data['user_id']
                fun.modified_by= user_data['user_id']
                InsertData(fun)
            
            return jsonify({'response': "success","code":"200"})
        else:
            return jsonify({'message': 'Empty Row found'}), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addFunctions", methods = ['POST'])
@token_required
def AddFunctions(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()

        print(postData,file=sys.stderr)
        print(f"Function Data received is:  {postData}", file=sys.stderr)
        for funObj in postData:
            fun = FUNCTIONS_TABLE()
            if funObj['tfun'] and funObj['function'] :
                fun.tfun = funObj['tfun']
                fun.function = funObj['function']
                
                        
                if FUNCTIONS_TABLE.query.with_entities(FUNCTIONS_TABLE.tfun).filter_by(tfun=funObj['tfun']).first() is not None:
                    fun_id = FUNCTIONS_TABLE.query.with_entities(FUNCTIONS_TABLE.function_id).filter_by(tfun=funObj['tfun']).first()
                    fun.function_id = fun_id[0]
                    print(f"Updated {funObj['tfun']}",file=sys.stderr)
                    fun.modification_date= datetime.now(tz)
                    fun.modified_by= user_data['user_id']
                    UpdateData(fun)
                    
                else:
                    print("Inserted Record",file=sys.stderr)
                    fun.created_by= user_data['user_id']
                    fun.modified_by= user_data['user_id']
                    fun.creation_date= datetime.now(tz)
                    fun.modification_date= datetime.now(tz)
                    InsertData(fun)

        return jsonify({'response': "success","code":"200"})

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteFunctions",methods = ['POST'])
@token_required
def DeleteFunctions(user_data):
    if True:#session.get('token', None):
        funObj = request.get_json()
        print(funObj,file = sys.stderr)
        print(f"Function   Dataa received is:  {funObj}", file=sys.stderr)

        for obj in funObj.get("function_id"):
            funID = FUNCTIONS_TABLE.query.filter(FUNCTIONS_TABLE.function_id==obj).first()
            print(funID,file=sys.stderr)
            if funID:
                db.session.delete(funID)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllFunctions",methods = ['GET'])
@token_required
def GetAllFunctions(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        funList= []
        
        funObjs = FUNCTIONS_TABLE().query.all()
        for funObj in funObjs:
                
            funDataDict={}
            funDataDict['function_id']= funObj.function_id
            funDataDict['function']= funObj.function
            funDataDict['tfun']= funObj.tfun
            funDataDict['created_by'] = funObj.created_by
            funDataDict['modified_by'] = funObj.modified_by

            #funDataDict['creation_date']=  funObj.creation_date
            #funDataDict['modification_date']=  funObj.modification_date
            funList.append(funDataDict)
                
        return jsonify(funList), 200


@app.route("/syncImsFunction", methods = ['GET'])
def PopulateIMSFunction():
    print("Populating Power feeds from device table")
    c=0
    count=0
    failed=0
    devices = Device_Table.query.all()
    if devices:
        
        for device in devices:
            c+=1
            
            try:
                imsFunction= str(device.device_id).split('-') 
                imsFunction= imsFunction[1] 
                imsFunctionObj = FUNCTIONS_TABLE.query.with_entities(FUNCTIONS_TABLE.function).filter_by(tfun=imsFunction).first() 
                if imsFunctionObj:
                    device.ims_function= imsFunctionObj[0]
                else:
                    device.ims_function= imsFunction
                    
                UpdateData(device)
                count+=1
                print(f"Added IMS Function For Device  ID {device.device_id}", file=sys.stderr)
            except Exception as e:
                failed+=1
                print(f"Filed to Add IMS Function For Device  ID {device.device_id}", file=sys.stderr)
            
    return str(f"Success  {c}   {count}    {failed}"), 200

@app.route("/syncImsDomain", methods = ['GET'])
def PopulateImsDomain():
    print("Populating Power feeds from device table")
    c=0
    count=0
    failed=0
    devices = Device_Table.query.all()
    if devices:
        
        for device in devices:
            c+=1
            
            try:
                imsdomain=device.cisco_domain 
                imsDomainObj = DOMAINS_TABLE.query.with_entities(DOMAINS_TABLE.section, DOMAINS_TABLE.department).filter_by(cisco_domain=imsdomain).first() 
                if imsDomainObj:
                    device.section= imsDomainObj[0]
                    device.department= imsDomainObj[1]
                else:
                    device.section= imsdomain
                    device.department= imsdomain
                    
                UpdateData(device)
                count+=1
                print(f"Added IMS Domain For Device  ID {device.device_id}", file=sys.stderr)
            except Exception as e:
                failed+=1
                print(f"Filed to Add IMS Domain For Device  ID {device.device_id} {e}", file=sys.stderr)
            
    return str(f"Success  {c}   {count}    {failed}"), 200


@app.route("/getDviceIdConflicts", methods = ['GET'])
def GetDviceIdConflicts():
    print("Populating Power feeds from device table")
    count=0
    devices = Device_Table.query.all()
    missing =[]
    if devices:
        
        for device in devices:            
            try:
                imsFunctionObj = Seed.query.with_entities(Seed.device_id).filter_by(ne_ip_address=device.ne_ip_address).first() 
                if imsFunctionObj:
                    device_id= imsFunctionObj[0]
                    if device_id != device.device_id:
                        missing.append(device_id)
                
                print(f"Added IMS Function For Device  ID {device.device_id}", file=sys.stderr)
            except Exception as e:
                print(f"Filed to Add IMS Function For Device  ID {device.device_id}", file=sys.stderr)
            
    return str(f"Success  {missing}"), 200


@app.route("/deletePnCode",methods = ['POST'])
@token_required
def DeletePnCode(user_data):


    if True:#session.get('token', None):
        posObj = request.get_json()
        print(posObj,file = sys.stderr)
        print(f"PnCode Data received is:  {posObj}", file=sys.stderr)

        for obj in posObj.get("user_ids"):
            posID = SNTC_Table.query.filter(SNTC_Table.pn_code==obj).first()
            print(posID,file=sys.stderr)
            if obj:
                db.session.delete(posID)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401


@app.route("/addDomain",methods = ['POST'])
@token_required
def AddDomain(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        domainObj = request.get_json()

        print(domainObj, file=sys.stderr)
        dom= DOMAINS_TABLE()
        if domainObj['domain']:
            dom.cisco_domain= domainObj['domain']
            dom.department= domainObj['department']
            dom.section = domainObj['section']
            
                    
            if DOMAINS_TABLE.query.with_entities(DOMAINS_TABLE.cisco_domain).filter_by(cisco_domain=domainObj['domain']).first() is not None:
                dom_id = DOMAINS_TABLE.query.with_entities(DOMAINS_TABLE.domain_id).filter_by(cisco_domain=domainObj['domain']).first()
                dom.domain_id = dom_id[0]
                print(f"Updated {domainObj['domain']}",file=sys.stderr)
                dom.modification_date= datetime.now(tz)
                dom.modified_by= user_data['user_id']
                UpdateData(dom)
                
            else:
                print("Inserted Record",file=sys.stderr)
                dom.creation_date= datetime.now(tz)
                dom.modification_date= datetime.now(tz)
                dom.created_by= user_data['user_id']
                dom.modified_by= user_data['user_id']
                InsertData(dom)
            
            return jsonify({'response': "success","code":"200"})
        else:
            return jsonify({'message': 'Empty Row found'}), 500

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/addDomains", methods = ['POST'])
@token_required
def AddDomains(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        postData = request.get_json()

        print(postData,file=sys.stderr)
        print(f"Domain Data received is:  {postData}", file=sys.stderr)
        for domainObj in postData:
            dom= DOMAINS_TABLE()
            if domainObj['domain']:
                dom.cisco_domain= domainObj['domain']
                dom.department= domainObj['department']
                dom.section = domainObj['section']
                
                        
                if DOMAINS_TABLE.query.with_entities(DOMAINS_TABLE.cisco_domain).filter_by(cisco_domain=domainObj['domain']).first() is not None:
                    dom_id = DOMAINS_TABLE.query.with_entities(DOMAINS_TABLE.cisco_domain).filter_by(cisco_domain=domainObj['domain']).first()
                    dom.domain_id = dom_id[0]
                    print(f"Updated {domainObj['domain']}",file=sys.stderr)
                    dom.modification_date= datetime.now(tz)
                    dom.modified_by= user_data['user_id']
                    UpdateData(dom)
                    
                else:
                    print("Inserted Record",file=sys.stderr)
                    dom.created_by= user_data['user_id']
                    dom.modified_by= user_data['user_id']
                    dom.creation_date= datetime.now(tz)
                    dom.modification_date= datetime.now(tz)
                    InsertData(dom)

        return jsonify({'response': "success","code":"200"})

    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/deleteDomain",methods = ['POST'])
@token_required
def DeleteDomain(user_data):
    if True:#session.get('token', None):
        domainObj = request.get_json()
        print(domainObj,file = sys.stderr)
        print(f"Domain   Dataa received is:  {domainObj}", file=sys.stderr)

        for obj in domainObj.get("domain_id"):
            funID = DOMAINS_TABLE.query.filter(DOMAINS_TABLE.domain_id==obj).first()
            print(funID,file=sys.stderr)
            if funID:
                db.session.delete(funID)
                db.session.commit()
        return jsonify({'response': "success","code":"200"})
    else: 
        print("Authentication Failed", file=sys.stderr)
        return jsonify({'message': 'Authentication Failed'}), 401

@app.route("/getAllDomain",methods = ['GET'])
@token_required
def GetAllDomain(user_data):
    if True:#request.headers.get('X-Auth-Key') == session.get('token', None):
        funList= []
        
        domainObjs = DOMAINS_TABLE().query.all()
        for domainObj in domainObjs:
                
            domDataDict={}
            domDataDict['domain_id']= domainObj.domain_id
            domDataDict['domain']= domainObj.cisco_domain
            domDataDict['department']= domainObj.department
            domDataDict['section']= domainObj.section
            domDataDict['created_by'] = domainObj.created_by
            domDataDict['modified_by'] = domainObj.modified_by

            #funDataDict['creation_date']=  domainObj.creation_date
            #funDataDict['modification_date']=  domainObj.modification_date
            funList.append(domDataDict)
                
        return jsonify(funList), 200
