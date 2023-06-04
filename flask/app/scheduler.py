from app import app, db, tz, phy_engine
from app.models.inventory_models import PnCode_SNAP_Table
import sys, json
from app.models.phy_mapping_models import SCRIPT_STATUS
from app.physical_mapping_scripts.cdp import CDPLegacy
from app.physical_mapping_scripts.arp import EdnMacLegacy
from app.models.inventory_models import EDN_IPAM_TABLE, IGW_IPAM_TABLE, EDN_HANDOVER_TRACKER
from app.models.inventory_models import EDN_NET_Seed
from app.physical_mapping_scripts.aci_lldp import LLDPPuller
from app.physical_mapping_scripts.arp_table import Arp
from app.models.inventory_models import EDN_SEC_Seed,Rack_Table,Phy_Table
from app.routes.physical_mapping_routes import FetchEdnArpFunc, FetchEdnCdpLegacyFunc, FetchEdnLldpLegacyFunc, FetchEdnMacLegacyFunc, FetchEdnLLDPACIFunc, FetchIGWCdpLegacyFunc, FetchIGWLldpLegacyFunc, FetchIGWLLDPACIFunc, getAllIgwMappingsFunc, GetAllEdnMappingsFunc, FetchIgwMacLegacyFunc
from app.routes.ipam_routes import FetchEdnIpamFunc, FetchIgwIpamFunc, FetchSocIpCollectorFunc
from app.routes.ipt_endpoints_routes import FetchIPTEndpointsFunc, iptEndPointsExcelBackup
from app.routes.dc_capacity_routes import FetchEdnDcCapacityFunc, FetchIgwDcCapacityFunc
from app.routes.edn_exchange_routes import FetchEdnExchangeFunc
from app.routes.edn_core_routing_routes import FetchEdnCoreRoutingFunc
from app.routes.access_points_routes import FetchAccesspointsFunc
from app.routes.f5_routes import FetchF5Func
from influxdb_client import Point, WritePrecision
from app import app, write_operational
from random import randint
from app.physical_mapping_scripts.addFWIP import AddFwIP
from app.physical_mapping_scripts.addSericeMapping import AddServiceMapping
from flask_apscheduler import APScheduler
from datetime import datetime
import logging
from app.pullers.opr_netconf_xr import Puller
import smtplib
from smtplib import SMTPException
from email.message import EmailMessage
import pandas as pd
import os
import atexit
import pysftp
from app.routes.edn_exchange_dashboard_routes import GetUnusedVrfsTableFunc, GetSpofVrfsTableFunc, GetVrfsWithMissingRoutesFunc, GetIntranetVrfsWithMissingRoutesTableFunc 
from app.routes.inventory_routes import FetchPnCodeSnapFunc, AddCountRackIdDevicesFunc, AddCountSiteIdDevicesFunc
from apscheduler.schedulers.background import BackgroundScheduler

#######scheduler intialiation
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()


#fileName="SchedulerLogs.log"
#logging.basicConfig(filename=fileName, filemode='w',
                    #level=logging.INFO, format='%(message)s')
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
    #print(obj, file=sys.stderr)
    try:
        # db.session.flush()

        db.session.merge(obj)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong during Database Update {e}", file=sys.stderr)
    
    return True

'''

def CreatePullersDictList(postData):
    hosts = []
    
    with open('app/cred.json') as inventory:
        inv = json.loads(inventory.read())

    for ip in postData:
        #print(ip, file=sys.stderr)
        hostDict = {}
        hostDict["host"] = ip
        hostDict["user"] = inv['IGW']['user']
        hostDict["pwd"] = inv['IGW']['pwd']

        hosts.append(hostDict)

@scheduler.task('interval', id='AddOperationStatus', minutes=5)
def AddOperationStatus():
    print('OperationStatus pullers execution started '+datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S'), file=sys.stderr)
    #logging.info("Info message "+datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S'))
    org = "mobily"
    bucket = "operational_status"

    opr_inv = Puller()
    pullerData =opr_inv.get_operational_data([
        {
            "host": "10.66.211.30",
            "user": "srv00047",
            "pwd": "5FPB4!!1c9&g*iJ9"
        }])
    print (pullerData, file=sys.stderr)
    host = '10.66.211.30'

    if 'error' not in pullerData[host]:
        print("Puller Contain Data",file=sys.stderr)

        for cpu in pullerData[host]['cpu']:
            print (cpu, file=sys.stderr)
            point = Point("cpu").tag("host", host).tag("node", cpu['node-name'])\
                .field("total-cpu-one-minute", cpu['total-cpu-one-minute'])\
                .field("total-cpu-five-minute", cpu['total-cpu-five-minute'])\
                .field("total-cpu-fifteen-minute", cpu['total-cpu-fifteen-minute'])\
                .time(datetime.now(tz), WritePrecision.MS)
            write_operational.write(bucket, org, point)

        print('OperationStatus CPU added '+datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S'), file=sys.stderr)
        #logging.info("OperationStatus CPU added "+datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S'))

        if 'neighbors' in pullerData[host]['cdp_data']:
            for cdpData in pullerData[host]['cdp_data']:
                print (cdpData, file=sys.stderr)
                cdpPoint = Point("cdp").tag("host", host).tag("node-name", cdpData['node-name']).tag("interface-name", cdpData['neighbors']['details']['detail']['interface-name'])\
                    .field("device-id", cdpData['neighbors']['details']['detail']['device-id'])\
                    .field("port-id", cdpData['neighbors']['details']['detail']['cdp-neighbor']['port-id'])\
                    .field("platform", cdpData['neighbors']['details']['detail']['cdp-neighbor']['platform'])\
                    .field("neighbor-ipv4-address", cdpData['neighbors']['details']['detail']['cdp-neighbor']['detail']['network-addresses']['cdp-addr-entry']['ipv4-address'])\
                    .time(datetime.now(tz), WritePrecision.MS)
                write_operational.write(bucket, org, cdpPoint)

        print('OperationStatus cdp_data added '+datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S'), file=sys.stderr)
        #logging.info("OperationStatus cdp_data added "+datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S'))

        if 'neighbors' in pullerData[host]['lldp_data']:
            for lldpData in pullerData[host]['lldp_data']:
                    print (lldpData, file=sys.stderr)
                    ldpPoint = Point("lldp").tag("host", host).tag("node", lldpData['name'])\
                        .field("id", lldpData['neighbors']['neighbor']['id'])\
                        .field("chassis-id", lldpData['neighbors']['neighbor']['state']['chassis-id'] )\
                        .field("port-id", lldpData['neighbors']['neighbor']['state']['port-id'])\
                        .field("system-name", lldpData['neighbors']['neighbor']['state']['system-name'])\
                        .field("management-address", lldpData['neighbors']['neighbor']['state']['management-address'])\
                        .time(datetime.now(tz), WritePrecision.MS)
                    write_operational.write(bucket, org, ldpPoint)
    
    print('OperationStatus ldp_data added '+datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S'), file=sys.stderr)
    #logging.info("OperationStatus ldp_data added "+datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S'))

'''
'''
    ### Get Data from sample file
    pullerData = json.load(open('temp/opr_data.json',))

    host = "sandbox-iosxr-1.cisco.com"

    for cpu in pullerData[host]['cpu']:
        print (cpu, file=sys.stderr)
        point = Point("cpu").tag("host", host).tag("node", cpu['node-name'])\
            .field("total-cpu-one-minute", randint(1,10))\
            .field("total-cpu-five-minute", randint(15,30))\
            .field("total-cpu-fifteen-minute", randint(30,50))\
            .time(datetime.now(tz), WritePrecision.MS)
        write_operational.write(bucket, org, point)

    for interface in pullerData[host]['interfaces']:
        print (interface, file=sys.stderr)
        interfacePoint = Point("interface").tag("host", host).tag("interface-name", interface['interface-name'])\
            .field("speed", interface['speed'])\
            .field("input-drops", randint(1,30))\
            .field("output-drops", randint(10,40))\
            .field("input-errors", randint(1,10))\
            .field("output-errors", randint(1,10))\
            .field("mtu", randint(600,1000))\
            .time(datetime.now(tz), WritePrecision.MS)
        write_operational.write(bucket, org, interfacePoint)

    for memory in pullerData[host]['memory_data']:
        print (memory, file=sys.stderr)
        memoryPoint = Point("memory").tag("host", host).tag("node", memory['node-name'])\
            .field("physical-memory",  randint(10000000,20000000))\
            .field("free-memory",  randint(10000000,20000000))\
            .field("memory-state", memory['memory-state']['memory-state'])\
            .time(datetime.now(tz), WritePrecision.MS)
        write_operational.write(bucket, org, memoryPoint)

    for lldpData in pullerData[host]['lldp_data']:
        print (lldpData, file=sys.stderr)
        ldpPoint = Point("lldp").tag("host", host).tag("node", lldpData['name'])\
            .field("id", "ITDC-PR-BLEAF-149#Eth1/26")\
            .field("chassis-id",  "dc77.4c78.2692")\
            .field("port-id", "Eth1/26")\
            .field("system-name", "ITDC-PR-BLEAF-149")\
            .field("management-address", "10.254.2.149")\
            .time(datetime.now(tz), WritePrecision.MS)
        write_operational.write(bucket, org, ldpPoint)
        
    
    #get all active devices from db
    deviceObjs = Device_Table.query.filter_by(status='active').all()
    
    for deviceObj in deviceObjs:
        #call puller
        #check if puller has connected successfully

        for cpu in pullerData['sandbox-iosxr-1.cisco.com']['cpu']:
            print (cpu, file=sys.stderr)
            point = Point("cpu").tag("host", host).tag("node", cpu['node-name'])\
                .field("total-cpu-one-minute", cpu['total-cpu-one-minute'])\
                .field("total-cpu-five-minute", cpu['total-cpu-five-minute'])\
                .field("total-cpu-fifteen-minute", cpu['total-cpu-fifteen-minute'])\
                .time(datetime.now(tz), WritePrecision.MS)
            write_operational.write(bucket, org, point)

        for interface in pullerData['sandbox-iosxr-1.cisco.com']['interfaces']:
            print (interface, file=sys.stderr)
            interfacePoint = Point("interface").tag("host", host).tag("interface-name", interface['interface-name'])\
                .field("speed", interface['speed'])\
                .field("input-drops", interface['utilization']['drops']['input-drops'])\
                .field("output-drops", interface['utilization']['drops']['output-drops'])\
                .field("input-errors", interface['utilization']['errors']['input-errors'])\
                .field("output-errors", interface['utilization']['errors']['output-errors'])\
                .field("mtu", interface['mtu'])\
                .field("interface_status", interface['status'])\
                .time(datetime.now(tz), WritePrecision.MS)
            write_operational.write(bucket, org, interfacePoint)

        for memory in pullerData['sandbox-iosxr-1.cisco.com']['memory_data']:
            print (memory, file=sys.stderr)
            memoryPoint = Point("memory").tag("host", host).tag("node", memory['node-name'])\
                .field("physical-memory", memory['memory-state']['physical-memory'])\
                .field("free-memory", memory['memory-state']['free-memory'])\
                .field("memory-state", memory['memory-state']['memory-state'])\
                .time(datetime.now(tz), WritePrecision.MS)
            write_operational.write(bucket, org, memoryPoint)

        for cdpData in pullerData[host]['cdp_data']:
            print (cdpData, file=sys.stderr)
            cdpPoint = Point("cdp").tag("host", host).tag("node-name", cdpData['node-name']).tag("interface-name", cdpData['neighbors']['details']['detail']['interface-name'])\
                .field("device-id", cdpData['neighbors']['details']['detail']['device-id'])\
                .field("port-id", cdpData['neighbors']['details']['detail']['cdp-neighbor']['port-id'])\
                .field("platform", cdpData['neighbors']['details']['detail']['cdp-neighbor']['platform'])\
                .field("neighbor-ipv4-address", cdpData['neighbors']['details']['detail']['cdp-neighbor']['detail']['network-addresses']['cdp-addr-entry']['ipv4-address'])\
                .time(datetime.now(tz), WritePrecision.MS)
            write_operational.write(bucket, org, cdpPoint)

        for lldpData in pullerData[host]['lldp_data']:
            print (lldpData, file=sys.stderr)
            ldpPoint = Point("lldp").tag("host", host).tag("node", lldpData['name'])\
                .field("id", lldpData['neighbors']['neighbor']['id'])\
                .field("chassis-id", lldpData['neighbors']['neighbor']['state']['chassis-id'] )\
                .field("port-id", lldpData['neighbors']['neighbor']['state']['port-id'])\
                .field("system-name", lldpData['neighbors']['neighbor']['state']['system-name'])\
                .field("management-address", lldpData['neighbors']['neighbor']['state']['management-address'])\
                .time(datetime.now(tz), WritePrecision.MS)
            write_operational.write(bucket, org, ldpPoint)
'''

#@scheduler.task('interval', id='testOperation', seconds=1)
#def testOperation():
#    print('Test executed', file=sy
@scheduler.task(trigger='cron', id='SchedulePNCodeSnap', year='*', month='*', day='last')
def SchedulePNCodeSnap():
    '''
    Fetching PnCode Snap
    '''

    try:
        print("Fetching PnCode Snap", file=sys.stderr)
        
        FetchPnCodeSnapFunc()
    except Exception as e:
        print(f"Error Occured When Fetching PnCode Snap {e}", file=sys.stderr)
    print("PnCode Snap Finished", file=sys.stderr)
        
@scheduler.task(trigger='interval', id='ScheduleIptEndpoints', hours=3)
def ScheduleIptEndpoints():
    print("Started IPT Endpoints Fetch Every 6 Hours",file=sys.stderr)
    try:
        user={}
        user['user_id']= "Scheduler"
        FetchIPTEndpointsFunc(user)
    except Exception as e:
        print(f"Error Occured When Fetching IPT Endpoints {e}", file=sys.stderr)
    
    print("Finished IPT Endpoints Fetch every Saturday at 1 AM",file=sys.stderr)

@scheduler.task(trigger='cron', id='ScheduleIpam', day_of_week='sat', hour=2, minute=30)
def ScheduleIpam():
    print("Started Ipam Script every Saturday at 2:30 AM",file=sys.stderr)

    '''
    Fetching EDN IPAM
    '''

    try:
        print("Fetching EDN IPAM", file=sys.stderr)
        user={}
        user['user_id']= "Scheduler"
        FetchEdnIpamFunc(user)
    except Exception as e:
        print(f"Error Occured When Fetching EDN IPAM {e}", file=sys.stderr)
    print("EDN IPAM Finished", file=sys.stderr)
    
    '''
    Fetching IGW IPAM
    '''

    try:
        user={}
        user['user_id']= "Scheduler"
        print("Fetching IGW IPAM", file=sys.stderr)
        FetchIgwIpamFunc(user)
    except Exception as e:
        print(f"Error Occured When Fetching IGW IPAM {e}", file=sys.stderr)
    print("IGW IPAM Finished", file=sys.stderr)
    
    '''
    Fetching SOC IPAM
    '''

    try:
        user={}
        user['user_id']= "Scheduler"
        print("Fetching SOC IPAM", file=sys.stderr)
        FetchSocIpCollectorFunc(user)
    except Exception as e:
        print(f"Error Occured When Fetching SOC IPAM {e}", file=sys.stderr)
    print("SOC IPAM Finished", file=sys.stderr)

@scheduler.task(trigger='cron', id='SchedulePhyMapping', day_of_week='sat', hour=5, minute=0)
def SchedulePhyMapping():
    print("Started Physical Mapping Script every Saturday at 5 AM",file=sys.stderr)

    '''
    Fetching FireWall ARP
    '''

    try:
        print("Fetching FireWall ARP", file=sys.stderr)
        
        FetchEdnArpFunc("")
    except Exception as e:
        print(f"Error Occured When Fetching FireWall ARP {e}", file=sys.stderr)
    print("FireWall ARP Finished", file=sys.stderr)
    
    '''
    Fetching EDN MAC Legacy
    '''

    try:
        print("Fetching Edn MAC Legacy", file=sys.stderr)
        FetchEdnMacLegacyFunc("")

    except Exception as e:
        print(f"Error Occurred When Fetching EDN MAC Legacy {e}", file=sys.stderr)
    print("EDN MAC Legacy Finished", file=sys.stderr)

    
    '''
    Fetching EDN CDP Legacy
    '''

    try:
        print("Fetching Edn CDP Legacy", file=sys.stderr)
        FetchEdnCdpLegacyFunc("")
    except Exception as e:
        print(f"Error Occured When Fetching EDN CDP Legacy {e}", file=sys.stderr)
    print("Edn CDP Legacy Finished", file=sys.stderr)    


    '''
    Fetching EDN LLDP Legacy
    '''

    try:
        print("Fetching Edn LLDP Legacy", file=sys.stderr)
        FetchEdnLldpLegacyFunc("")
    except Exception as e:
        print(f"Error Occured When Fetching EDN LLDP Legacy {e}", file=sys.stderr)
    print("Edn LLDP Legacy Finished", file=sys.stderr)    

    
    '''
    Fetching EDN LLDP ACI
    '''

    try:
        pass
        #print("Fetching LLDP Mac Legacy", file=sys.stderr)
        #FetchEdnLLDPACIFunc("")

    except Exception as e:
        print(f"Error Occured When Fetching EDN LLDP ACI {e}", file=sys.stderr)
    
    print("EDN LLDP ACI Finished", file=sys.stderr)

    
    '''
    Fetching IGW CDP Legacy
    '''

    try:
        print("Fetching IGW CDP Legacy", file=sys.stderr)
        FetchIGWCdpLegacyFunc("")
    
    except Exception as e:
        print(f"Error Occured When Fetching IGW CDP Legacy {e}", file=sys.stderr)
    print("IGW CDP Legacy Finished", file=sys.stderr)  

    '''
    Fetching IGW LLDP Legacy
    '''

    try:
        print("Fetching IGW LLDP Legacy", file=sys.stderr)
        FetchIGWLldpLegacyFunc("")
    
    except Exception as e:
        print(f"Error Occured When Fetching IGW LLDP Legacy {e}", file=sys.stderr)
    print("IGW LLDP Legacy Finished", file=sys.stderr)  
    
    '''
    Fetching IGW LLDP ACI
    '''

    # try:
    #     pass
    #     #print("Fetching IGW LLDP ACI", file=sys.stderr)
        
    #     #FetchIGWLLDPACIFunc("")
    # except Exception as e:
    #     print(f"Error Occured When Fetching IGW LLDP ACI {e}", file=sys.stderr)
    # print("IGW LLDP ACI Finished", file=sys.stderr)

    try:
        
        print("Fetching IGW MAC ", file=sys.stderr)
        
        FetchIgwMacLegacyFunc("")
    except Exception as e:
        print(f"Error Occured When Fetching IGW MAC ACI {e}", file=sys.stderr)
    print("IGW MAC  Finished", file=sys.stderr)

    print("Completed Execution of Physical Mapping Script every Saturday",file=sys.stderr)

@scheduler.task(trigger='cron', id='SendPhysicalMappingReports', hour=0,  minute=1)
def SendPhysicalMappingReports():
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
    
def GeneratePhysicalMappingCsvReport(data, file_name, mapping_type): 
    #iterate over data and save to excel
    dfObj = pd.DataFrame(columns=['device_a_name', 'device_a_interface', 'device_a_trunk_name',	'device_a_ip',	'device_b_system_name',	'device_b_interface',	'device_b_ip',	'device_b_type', 'device_b_port_desc', 'device_a_mac', 'device_b_mac', 'device_a_port_desc', 'device_a_vlan', 'owner_name', 'owner_email', 'owner_contact', 'device_a_vlan_name', 'server_os', 'server_name', 'app_name', 'modified_by', 'arp_source_name', 'service_matched_by', 'creation_date','modification_date', 'arp_source_type', 'arp_source_name', 'service_vendor', 'device_b_mac_vendor', 'device_a_rx', 'device_a_tx', 'f5_node', 'f5_vip', 'f5_node_Status'])
    obj_in=0
   
    try:
        for pm_data in data:
            dfObj.loc[obj_in,'device_a_name'] = pm_data.get('device_a_name', "")
            dfObj.loc[obj_in,'device_a_interface'] = pm_data.get('device_a_interface', "")
            dfObj.loc[obj_in,'device_a_trunk_name'] = pm_data.get('device_a_trunk_name', "")
            dfObj.loc[obj_in,'device_a_ip'] = pm_data.get('device_a_ip', "") 
            dfObj.loc[obj_in,'device_b_system_name'] = pm_data.get('device_b_system_name', "")
            dfObj.loc[obj_in,'device_b_interface'] = pm_data.get('device_b_interface', "")
            dfObj.loc[obj_in,'device_b_ip'] = pm_data.get('device_b_ip', "")
            dfObj.loc[obj_in,'device_b_type'] = pm_data.get('device_b_type', "")
            dfObj.loc[obj_in,'device_b_port_desc'] = pm_data.get('device_b_port_desc', "")
            dfObj.loc[obj_in,'device_a_mac'] = pm_data.get('device_a_mac', "")
            dfObj.loc[obj_in,'device_b_mac'] = pm_data.get('device_b_mac', "")
            dfObj.loc[obj_in,'device_a_port_desc'] = pm_data.get('device_a_port_desc', "")
            dfObj.loc[obj_in,'device_a_vlan'] = pm_data.get('device_a_vlan', "")
            dfObj.loc[obj_in,'service_name'] = pm_data.get('service_name', "")
            dfObj.loc[obj_in,'owner_name'] = pm_data.get('owner_name', "")
            dfObj.loc[obj_in,'owner_email'] = pm_data.get('owner_email', "")
            dfObj.loc[obj_in,'owner_contact'] = pm_data.get('owner_contact', "")
            dfObj.loc[obj_in,'device_a_vlan_name'] = pm_data.get('device_a_vlan_name', "")
            dfObj.loc[obj_in,'server_name'] = pm_data.get('server_name', "")
            dfObj.loc[obj_in,'server_os'] = pm_data.get('server_os', "")
            dfObj.loc[obj_in,'app_name'] = pm_data.get('app_name', "")
            dfObj.loc[obj_in,'modified_by'] = pm_data.get('modified_by', "")
            dfObj.loc[obj_in,'arp_source_name'] = pm_data.get('arp_source_name', "")
            dfObj.loc[obj_in,'arp_source_type'] = pm_data.get('arp_source_type', "")
            dfObj.loc[obj_in,'device_b_mac_vendor'] = pm_data.get('device_b_mac_vendor', "")
            dfObj.loc[obj_in,'service_vendor'] = pm_data.get('service_vendor', "")
            dfObj.loc[obj_in,'service_matched_by'] = pm_data.get('service_matched_by', "")
            dfObj.loc[obj_in,'creation_date'] = pm_data.get('creation_date', "")
            dfObj.loc[obj_in,'modification_date'] = pm_data.get('modification_date', "")
            dfObj.loc[obj_in,'device_a_tx'] = pm_data.get('device_a_tx', "")
            dfObj.loc[obj_in,'device_a_rx'] = pm_data.get('device_a_rx', "")
            dfObj.loc[obj_in,'f5_lb'] = pm_data.get("f5_lb", "")
            dfObj.loc[obj_in,'f5_vip'] = pm_data.get("f5_vip", "")
            dfObj.loc[obj_in,'f5_node_status'] = pm_data.get("f5_node_status", "")
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
        #msg['Subject'] = 'IT Service Mapping Report <reporter-sw@mobily.com.sa>'
        msg['From'] = 'IGW/EDN Physical Mapping Report <reporter-sw@mobily.com.sa>'
        msg['To'] = ", ".join(receivers)
        
        try:
            with open(ednFileName+".xlsx", "rb") as f:
                file_data= f.read()
                file_name= f.name
                msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=file_name.split('/')[2])
        
        except Exception as e:
           print(f"EDN Mapping Not Found {e}", file=sys.stderr)

        try:
            with open(igwFileName+".xlsx", "rb") as f:
                file_data= f.read()
                file_name= f.name
                msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=file_name.split('/')[2])
        
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

@scheduler.task(trigger='cron', id='AddCountRackIdDevices', year='*', month='*', day='*',hour = '01',minute='0')
def AddCountRackIdDevices():
    
        
    '''
    Fetching Count of Devices w.r.t. Rack ID 
    '''

    try:
        print("Fetching Count of Devices w.r.t. Rack ID", file=sys.stderr)
        
        AddCountRackIdDevicesFunc()
    except Exception as e:
        print(f"Error Occured When Fetching Count of Devices w.r.t. Rack ID {e}", file=sys.stderr)
    print("Count of Devices w.r.t. Rack ID Finished", file=sys.stderr)

@scheduler.task(trigger='cron',id='AddCountSiteIdDevices',year='*', month='*', day='*',hour = '01',minute='0')
def AddCountSiteIdDevices():
    '''
    Fetching Count of Devices w.r.t. Site ID 
    '''

    try:
        print("Fetching Count of Devices w.r.t. Site ID", file=sys.stderr)
        
        AddCountSiteIdDevicesFunc()
    except Exception as e:
        print(f"Error Occured When Fetching Count of Devices w.r.t. Site ID {e}", file=sys.stderr)
    print("Fetching Count of Devices w.r.t. Site ID Finished", file=sys.stderr)

@scheduler.task(trigger='cron', id='PopulateEdnHandoverTracker', year='*', month='*', day='*',hour = '01',minute='10')
def PopulateEdnHandoverTracker():
    
        
    '''
    Fetching Onboard Status for HO Tracker
    '''

    try:
        print("Fetching Onboard Status for HO Tracker from Seed", file=sys.stderr)
        
        FetchOnboardStatusForHoTracker()
    except Exception as e:
        print(f"Error Occured When Fetching Onboard Status for HO Tracker {e}", file=sys.stderr)
    print("Fetch Onboard Status for HO Tracker Finished", file=sys.stderr)

def FetchOnboardStatusForHoTracker():
    try:
        objs = EDN_HANDOVER_TRACKER.query.all()
        for obj in objs:
            data = db.session.execute(f"select onboard_status from seed_table where device_id = '{obj.device_id}'").fetchall()
            if len(data) > 0:
                onboardStatus = data[0][0]
                if 'true' in onboardStatus:
                    obj.onboard_status = 'onboarded'
                elif 'false' in onboardStatus:
                    obj.onboard_status = 'not onboarded' 
            else:
                obj.onboard_status = 'not in seed'
            
            UpdateData(obj)
            print(f"Data Updated for Tracker {obj.handover_tracker_id}", file=sys.stderr)

    except Exception as e:
        return {f"response": f"Failed to Update/Insert {e}"},500

@scheduler.task(trigger='cron', id='ScheduleDCM', day_of_week='sat', hour=1, minute=10)
def ScheduleDCM():
    print("Started DCM Script every Saturday at 12:15 AM",file=sys.stderr)

    '''
    Fetching EDN DCM
    '''

    try:
        print("Fetching EDN DCM", file=sys.stderr)
        user={}
        user['user_id']= "Scheduler"
        FetchEdnDcCapacityFunc(user)
    except Exception as e:
        print(f"Error Occured When Fetching EDN DCM {e}", file=sys.stderr)
    print("EDN DCM Finished", file=sys.stderr)
    
    '''
    Fetching IGW DCM
    '''

    try:
        print("Fetching IGW DCM", file=sys.stderr)
        user={}
        user['user_id']= "Scheduler"
        FetchIgwDcCapacityFunc(user)
    except Exception as e:
        print(f"Error Occured When Fetching IGW DCM {e}", file=sys.stderr)
    print("IGW IPAM DCM", file=sys.stderr)    

@scheduler.task(trigger='cron', id='ScheduleEDNExchange', day_of_week='sat', hour=12, minute=1)
def ScheduleEDNExchange():
    print("Started EDN Exchange Script every Saturday at 12:01 AM",file=sys.stderr)

    '''
    Fetching EDN Exchange
    '''

    try:
        print("Fetching EDN Exchange", file=sys.stderr)
        user={}
        user['user_id']= "Scheduler"
        FetchEdnExchangeFunc(user)
    except Exception as e:
        print(f"Error Occured When Fetching EDN Exchange {e}", file=sys.stderr)
    print("EDN Exchange Finished", file=sys.stderr)

@scheduler.task(trigger='cron', id='ScheduleEDNCoreRouting', day_of_week='sat', hour=12, minute=30)
def ScheduleEDNCoreRouting():
    print("Started EDN Core Routing Script every Saturday at 12:30 AM",file=sys.stderr)

    '''
    Fetching EDN Core Routing
    '''

    try:
        print("Fetching EDN Core Routing", file=sys.stderr)
        user={}
        user['user_id']= "Scheduler"
        FetchEdnCoreRoutingFunc(user)
    except Exception as e:
        print(f"Error Occured When Fetching EDN Core Routing {e}", file=sys.stderr)
    print("EDN Core Routing Finished", file=sys.stderr)

@scheduler.task(trigger='cron', id='ScheduleAccessPoints', year='*', month='*', day='*', hour = '01',minute='0')
def ScheduleEDNExchange():
    print("Started Access Point Script Every Day at 12:01 AM",file=sys.stderr)

    '''
    Fetching Access Point
    '''

    try:
        print("Fetching Access Point", file=sys.stderr)
        user={}
        user['user_id']= "Scheduler"
        FetchAccesspointsFunc(user)
    except Exception as e:
        print(f"Error Occured When Fetching Access Point {e}", file=sys.stderr)
    print("Access Point Finished", file=sys.stderr)

@scheduler.task(trigger='cron', id='ScheduleF5', day_of_week='sat', hour=4, minute=0)
def ScheduleF5():
    print("Started F5 Script every Saturday at 4:00 AM",file=sys.stderr)

    '''
    Fetching F5
    '''

    try:
        print("Fetching F5", file=sys.stderr)
        user={}
        user['user_id']= "Scheduler"
        FetchF5Func(user)
    except Exception as e:
        print(f"Error Occured When Fetching F5 {e}", file=sys.stderr)
    print("F5 Finished", file=sys.stderr)
    
@scheduler.task(trigger='cron', id='scheduleEdnMacSyncs', day_of_week='sun', hour=7)
def ScheduleEdnMacSyncs():
    # print("Started EDN MAC Firewall Sync",file=sys.stderr)
    # try:
    #     date=""
        
    #     fw= AddFwIP()
    #     newTime= datetime.now(tz)
    #     ednFirewallArpObjs = phy_engine.execute('SELECT max(creation_date) FROM edn_mac_legacy')
    #     for row in ednFirewallArpObjs:
    #         date=row[0]
    #     if date:
    #         fw.addFWIPToEdnMacLegacy(date, newTime)

    # except Exception as e:
    #     print("Exception occured in EDN MAC Firewall Sync", file=sys.stderr)

    
    # print("FinishedEDN MAC Firewall Sync",file=sys.stderr)


    print("Started EDN MAC Service Mapping Sync",file=sys.stderr)
    try:
        currentTime=""
        newTime= datetime.now(tz)
        serviceMapping= AddServiceMapping()
        
        currentTimeObj = phy_engine.execute('SELECT max(creation_date) FROM edn_mac_legacy;')
        for row in currentTimeObj:
            currentTime=row[0]
        serviceMapping.AddEdnServiceMappingFunc()
        serviceMapping.addEdnMacLegacyServiceMapping(currentTime, newTime)
        
        return ""
    except Exception as e:
        print("Exception occured in EDN MAC Service Mapping Sync", file=sys.stderr)
    print("Started EDN MAC Service Mapping Sync",file=sys.stderr)

@scheduler.task(trigger='cron', id='scheduleItServicesSnapshots', day_of_week='sun', hour=5)
def ScheduleEdnMacSyncs():
    print("Started IT Services Snapshot Sync",file=sys.stderr)
    try:        
        serviceMapping= AddServiceMapping()
        
        serviceMapping.addItSnapshotServiceMapping()

    except Exception as e:
        print("Exception occured in IT Services Snapshot Sync", file=sys.stderr)
    print("Finished IT Services Snapshot Sync",file=sys.stderr)

@scheduler.task(trigger='cron', id='iptEndpointsDailyExcelBackup', year='*', month='*', day='*',hour = '6',minute='0')
def IptEndpointsDailyExcelBackup():
    
        
    '''
   GenerTING ipt eNDpoints daily excel backup
    '''

    try:
        print("Fetching Count of Devices w.r.t. Rack ID", file=sys.stderr)
        
        iptEndPointsExcelBackup()
    except Exception as e:
        print(f"Error Occured When Fetching Count of Devices w.r.t. Rack ID {e}", file=sys.stderr)
    print("Count of Devices w.r.t. Rack ID Finished", file=sys.stderr)


def sendItServiceAlretsEmail(noOwnerFileName, noMacIpFileName): 
    try:
        sender = 'IT Service Mapping Report <reporter-sw@mobily.com.sa>'
        #receivers = ['sohaib.ajmal@nets-international.com']
        receivers = ['a.harras@mobily.com.sa', 'a.abdulrahman01@mobily.com.sa', 'k.mustafa@mobily.com.sa', 'edn-bo@mobily.com.sa', 'y.maqbool.emr@mobily.com.sa', 'm.alardhi@mobily.com.sa', 'n.yarramilli@mobily.com.sa', 'ka.kumar@mobily.com.sa', 'b.shaik@mobily.com.sa']


        msg = EmailMessage()
 
        msg.set_content('''
        Dear Team,

        Please Find VM's with no Owner Info and No IP, MAC Address in IT Service Mapping Data.
        
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
        msg['Subject'] = 'IT Service Mapping Weekly Report <reporter-sw@mobily.com.sa>'
        msg['From'] = 'IT Service Mapping Report <reporter-sw@mobily.com.sa>'
        msg['To'] = ", ".join(receivers)
        
        try:
            with open(noOwnerFileName+".xlsx", "rb") as f:
                file_data= f.read()
                file_name= f.name
                msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=file_name.split('/')[2])
        
        except Exception as e:
           print(f"EDN Mapping Not Found {e}", file=sys.stderr)

        try:
            with open(noMacIpFileName+".xlsx", "rb") as f:
                file_data= f.read()
                file_name= f.name
                msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=file_name.split('/')[2])
        
        except Exception as e:
           print(f"IGW Mapping Not Found {e}", file=sys.stderr)  

        smtpObj.sendmail(sender, receivers, msg.as_string())
        print("Successfully Sent email", file=sys.stderr)
        return "Success"
    except SMTPException:
        print(f"Error: unable to send email {e}", file=sys.stderr)
        

@scheduler.task(trigger='cron', id='sendITServiceMappingAlerts',  day_of_week='sun', hour=8, minute=0)
def SendITServiceMappingAlerts():
    print("Sending IT Service Mapping Alerts in Email", file=sys.stderr)

    print("Generating Reports", file=sys.stderr)
    noOwnerFileName= "app/physical_mapping_reports/Owner-Missing-Info-"+datetime.now().strftime("%d-%m-%Y")
    noMacIpFileName= "app/physical_mapping_reports/VM-With-No-IP-MAC"+datetime.now().strftime("%d-%m-%Y")
    if not os.path.exists('app/physical_mapping_reports'):
        os.makedirs('app/physical_mapping_reports')
    try:
        print("Generating No Owner", file=sys.stderr)
        noOwnerMapping= GetAllNoOwnerFunc()
        GenerateAlertReport(noOwnerMapping, noOwnerFileName, "No Owner")

        print("Generating Vm with No Mac and IP", file=sys.stderr)
        missingVmInfo= GetAllNoVmInfoFunc()
        GenerateAlertReport(missingVmInfo, noMacIpFileName, "No MAC-IP")
    except Exception as e:
        print(f"Exception Occured in Generating Reports {e}", file=sys.stderr)
    
    try:
        sendItServiceAlretsEmail(noOwnerFileName, noMacIpFileName)
    except Exception as e:
        print(f"Exception Occured in Sending Mail Reports {e}", file=sys.stderr)


def GenerateAlertReport(data, file_name, mapping_type): 
    #iterate over data and save to excel
    dfObj = pd.DataFrame(columns=['vm_name', 'missing_info'])
    obj_in=0
   
    try:
        for pm_data in data:
            dfObj.loc[obj_in,'vm_name'] = pm_data.get('vm_name', "")
            dfObj.loc[obj_in,'missing_info'] = pm_data.get('missing_info', "")
            
            obj_in+=1

    except Exception as e:
        print("error writing df")
        print(e, file=sys.stderr)

    try:
        writer = pd.ExcelWriter(file_name+".xlsx")
        #write dataframe to excel
        dfObj.to_excel(writer, sheet_name=mapping_type, index=False)
        writer.save()
        
        # #Write CSV
        # dfObj.to_csv(file_name+".csv",index=False)
        # print('DataFrame is written successfully to CSV File.', file=sys.stderr)
    except Exception as e:
        print(f'Error While writing data to CSV file {e}', file=sys.stderr)


def GetAllNoOwnerFunc():
    noOwnerList=[]
    try:
        #ednCdpLegacyObjs = EDN_CDP_LEGACY.query.all()
        noownerObjs = phy_engine.execute("SELECT * FROM edn_service_mapping WHERE (SERVICE_VENDOR = 'IT') AND (OWNER_NAME='' or OWNER_NAME=' ' or OWNER_NAME='NE' or OWNER_NAME='#N/A' or OWNER_NAME='NA' or OWNER_EMAIL='' or OWNER_EMAIL=' ' or OWNER_EMAIL='NE' or OWNER_EMAIL='#N/A' or OWNER_EMAIL='NA' or APP_NAME='' or APP_NAME=' ' or APP_NAME='NE' or APP_NAME='#N/A' or APP_NAME='NA');")
        for noownerObj in noownerObjs:
            missingString=""
            noOwnerDict= {}
            if noownerObj.OWNER_NAME  in ('',' ','NE','#N/A','NA'):
                missingString= "Owner Name, "
            if noownerObj.OWNER_EMAIL  in ('',' ','NE','#N/A','NA'):
                missingString+= "Owner Email, "
            if noownerObj.APP_NAME  in ('',' ','NE','#N/A','NA'):
                missingString+= "App Name, "
            if missingString.endswith(', '):
                missingString = missingString[:-2]

            noOwnerDict['vm_name']=noownerObj.SERVER_NAME
            noOwnerDict['missing_info']=missingString
                

            noOwnerList.append(noOwnerDict)
        
        return noOwnerList
    except Exception as e:
        print("Error Occured {e}", file=sys.stderr)
        return []

def GetAllNoVmInfoFunc():
    noOwnerList=[]
    try:
        #ednCdpLegacyObjs = EDN_CDP_LEGACY.query.all()
        noownerObjs = phy_engine.execute("SELECT * FROM edn_service_mapping WHERE (SERVICE_VENDOR = 'IT') AND (DEVICE_B_MAC='' or DEVICE_B_MAC=' ' or DEVICE_B_MAC='NE' or DEVICE_B_MAC='#N/A' or DEVICE_B_MAC='NA' or DEVICE_B_IP='' or DEVICE_B_IP=' ' or DEVICE_B_IP='NE' or DEVICE_B_IP='#N/A' or DEVICE_B_IP='NA');")
        for noownerObj in noownerObjs:
            missingString=""
            noOwnerDict= {}
            if noownerObj.DEVICE_B_MAC  in ('',' ','NE','#N/A','NA'):
                missingString= "MAC, "
            if noownerObj.DEVICE_B_IP  in ('',' ','NE','#N/A','NA'):
                missingString+= "IP, "
            
            if missingString.endswith(', '):
                missingString = missingString[:-2]

            noOwnerDict['vm_name']=noownerObj.SERVER_NAME
            noOwnerDict['missing_info']=missingString
                

            noOwnerList.append(noOwnerDict)
        
        return noOwnerList
    except Exception as e:
        print("Error Occured {e}", file=sys.stderr)
        return []
    
@scheduler.task(trigger='cron', id='sendImsInventoryReports',  day_of_week='sun', hour=8, minute=10)
def SendImsInventoryReports():
    print("Send IMS Inventory Report in Email", file=sys.stderr)

    print("Generating Reports", file=sys.stderr)
    notOnboardedFileName= "app/physical_mapping_reports/Not-Onboarded-Devices-"+datetime.now().strftime("%d-%m-%Y")
    if not os.path.exists('app/physical_mapping_reports'):
        os.makedirs('app/physical_mapping_reports')
    try:
        print("Generating Not Onboarded Devices Report", file=sys.stderr)
        notOnboarded= GetAllNoTOnboardedDevicesFunc()
        GenerateAlertReportForNotOnboardedDevices(notOnboarded, notOnboardedFileName)

    except Exception as e:
        print(f"Exception Occured in Generating Reports {e}", file=sys.stderr)
    
    try:
        sendImsInventoryReportEmail(notOnboardedFileName)
    except Exception as e:
        print(f"Exception Occured in Sending Mail Reports {e}", file=sys.stderr)
    
def sendImsInventoryReportEmail(notOnboardedFileName): 
    try:
        sender = 'IMS Inventory Report <reporter-sw@mobily.com.sa>'
        #receivers = ['nulhassan@mobily.com.sa']
        receivers = ['edn-bo@mobily.com.sa', 'snoc-fo@mobily.com.sa', 'fsn_systems_cis@mobily.com.sa', 'fsn-igw-ops@mobily.com.sa', 'nulhassan@mobily.com.sa', 'a.harras@mobily.com.sa']


        msg = EmailMessage()
 
        msg.set_content('''
        Dear Team,

        Please Find Production Devices which are not onboarded.
        
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
        msg['Subject'] = 'IMS Inventory Weekly Report <reporter-sw@mobily.com.sa>'
        msg['From'] = 'IMS Inventory Weekly Report <reporter-sw@mobily.com.sa>'
        msg['To'] = ", ".join(receivers)
        
        try:
            with open(notOnboardedFileName+".xlsx", "rb") as f:
                file_data= f.read()
                file_name= f.name
                msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=file_name.split('/')[2])
        
        except Exception as e:
           print(f"EDN Mapping Not Found {e}", file=sys.stderr) 

        smtpObj.sendmail(sender, receivers, msg.as_string())
        print("Successfully Sent email", file=sys.stderr)
        return "Success"
    except SMTPException as e:
        print(f"Error: unable to send email {e}", file=sys.stderr)

def GetAllNoTOnboardedDevicesFunc():
    notOnboardedList=[]
    try:
        #ednCdpLegacyObjs = EDN_CDP_LEGACY.query.all()
        notOnboardedObjs = db.session.execute("SELECT device_id, ne_ip_address, onboard_status, operation_status, cisco_domain FROM seed_table WHERE onboard_status = 'false' AND operation_status = 'production';")
        for notOnboardedObj in notOnboardedObjs:
            notOnboardedDict= {}
            notOnboardedDict['device_id'] = notOnboardedObj[0]
            notOnboardedDict['ne_ip_address'] = notOnboardedObj[1]
            notOnboardedDict['onboard_status'] = notOnboardedObj[2]
            notOnboardedDict['operation_status'] = notOnboardedObj[3]
            notOnboardedDict['cisco_domain'] = notOnboardedObj[4]

            notOnboardedList.append(notOnboardedDict)
        
        return notOnboardedList
    except Exception as e:
        print(f"Error Occured {e}", file=sys.stderr)
        return []
    
def GenerateAlertReportForNotOnboardedDevices(data, file_name): 
    #iterate over data and save to excel
    dfObj = pd.DataFrame(columns=['device_id', 'ne_ip_address', 'onboard_status', 'operation_status', 'cisco_domain'])
    obj_in=0
   
    try:
        for pm_data in data:
            dfObj.loc[obj_in,'device_id'] = pm_data.get('device_id', "")
            dfObj.loc[obj_in,'ne_ip_address'] = pm_data.get('ne_ip_address', "")
            dfObj.loc[obj_in,'onboard_status'] = pm_data.get('onboard_status', "")
            dfObj.loc[obj_in,'operation_status'] = pm_data.get('operation_status', "")
            dfObj.loc[obj_in,'cisco_domain'] = pm_data.get('cisco_domain', "")
            
            obj_in+=1

    except Exception as e:
        print("error writing df")
        print(e, file=sys.stderr)

    try:
        writer = pd.ExcelWriter(file_name+".xlsx")
        #write dataframe to excel
        dfObj.to_excel(writer, sheet_name='notOnboarded', index=False)
        writer.save()
        
        # #Write CSV
        # dfObj.to_csv(file_name+".csv",index=False)
        # print('DataFrame is written successfully to CSV File.', file=sys.stderr)
    except Exception as e:
        print(f'Error While writing data to CSV file {e}', file=sys.stderr)

@scheduler.task(trigger='cron', id='sendWeeklyReportOfMobilyUsers',  day_of_week='sun', hour=8, minute=20)
def SendWeeklyReportOfMobilyUsers():
    print("Send Weekly Report of Mobily Users in Email", file=sys.stderr)

    print("Generating Reports", file=sys.stderr)
    mobilyUsersReport= "app/physical_mapping_reports/Mobily-Users-Reports-"+datetime.now().strftime("%d-%m-%Y")
    if not os.path.exists('app/physical_mapping_reports'):
        os.makedirs('app/physical_mapping_reports')
    try:
        print("Generating Mobily Users Weekly Report", file=sys.stderr)
        weeklyReport= GetAllMobilyUsersWeeklyReport()
        GenerateWeeklyReportOfMobilyUsers(weeklyReport, mobilyUsersReport)

    except Exception as e:
        print(f"Exception Occured in Generating Reports {e}", file=sys.stderr)
    
    try:
        sendMobilyUsersWeeklyEmail(mobilyUsersReport)
    except Exception as e:
        print(f"Exception Occured in Sending Mail Reports {e}", file=sys.stderr)

def sendMobilyUsersWeeklyEmail(mobilyUsersReport): 
    try:
        sender = 'IMS Inventory Report <reporter-sw@mobily.com.sa>'
        #receivers = ['nulhassan@mobily.com.sa']
        receivers = ['l.odetallah@mobily.com.sa', 'o.bamahdi@mobily.com.sa', 'nat@mobily.com.sa', 'a.harras@mobily.com.sa', 's.mohamad@mobily.com.sa']


        msg = EmailMessage()
 
        msg.set_content('''
        Dear Team,

        Please Find Mobily Vendors Weekly Report.
        
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
        msg['Subject'] = 'Cisco IMS users access weekly report <reporter-sw@mobily.com.sa>'
        msg['From'] = 'IMS Inventory Weekly Report <reporter-sw@mobily.com.sa>'
        msg['To'] = ", ".join(receivers)
        
        try:
            with open(mobilyUsersReport+".xlsx", "rb") as f:
                file_data= f.read()
                file_name= f.name
                msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=file_name.split('/')[2])
        
        except Exception as e:
           print(f"EDN Mapping Not Found {e}", file=sys.stderr) 

        smtpObj.sendmail(sender, receivers, msg.as_string())
        print("Successfully Sent email", file=sys.stderr)
        return "Success"
    except SMTPException as e:
        print(f"Error: unable to send email {e}", file=sys.stderr)

def GetAllMobilyUsersWeeklyReport():
    reportList=[]
    try:
        Objs = db.session.execute("SELECT user_id, email, name, role, account_type, status, team, vendor, last_login, creation_date FROM user_table WHERE vendor = 'Mobily';")
        for Obj in Objs:
            dict= {}
            dict['user_id'] = Obj[0]
            dict['email'] = Obj[1]
            dict['name'] = Obj[2]
            dict['role'] = Obj[3]
            dict['account_type'] = Obj[4]
            dict['status'] = Obj[5]
            dict['team'] = Obj[6]
            dict['vendor'] = Obj[7]
            dict['last_login'] = Obj[8]
            dict['creation_date'] = Obj[9]

            reportList.append(dict)
        
        return reportList
    except Exception as e:
        print(f"Error Occured {e}", file=sys.stderr)
        return []
    
def GenerateWeeklyReportOfMobilyUsers(data, file_name): 
    #iterate over data and save to excel
    dfObj = pd.DataFrame(columns=['user_id', 'email', 'name', 'role', 'account_type', 'status', 'team', 'vendor', 'last_login', 'creation_date'])
    obj_in=0
   
    try:
        for pm_data in data:
            dfObj.loc[obj_in,'user_id'] = pm_data.get('user_id', "")
            dfObj.loc[obj_in,'email'] = pm_data.get('email', "")
            dfObj.loc[obj_in,'name'] = pm_data.get('name', "")
            dfObj.loc[obj_in,'role'] = pm_data.get('role', "")
            dfObj.loc[obj_in,'account_type'] = pm_data.get('account_type', "")
            dfObj.loc[obj_in,'status'] = pm_data.get('status', "")
            dfObj.loc[obj_in,'team'] = pm_data.get('team', "")
            dfObj.loc[obj_in,'vendor'] = pm_data.get('vendor', "")
            dfObj.loc[obj_in,'last_login'] = pm_data.get('last_login', "")
            dfObj.loc[obj_in,'creation_date'] = pm_data.get('creation_date', "")
            
            obj_in+=1

    except Exception as e:
        print("error writing df")
        print(e, file=sys.stderr)

    try:
        writer = pd.ExcelWriter(file_name+".xlsx")
        #write dataframe to excel
        dfObj.to_excel(writer, sheet_name='MobilyVendorWeeklyReport', index=False)
        writer.save()
        
        # #Write CSV
        # dfObj.to_csv(file_name+".csv",index=False)
        # print('DataFrame is written successfully to CSV File.', file=sys.stderr)
    except Exception as e:
        print(f'Error While writing data to CSV file {e}', file=sys.stderr)

    
####
#Scheduler to Send Weekly Report of Vrf Analysis 
####

@scheduler.task(trigger='cron', id='sendWeeklyReportOfVrfAnalysis',  day_of_week='sun', hour=7, minute=50)
def sendWeeklyReportOfVrfAnalysis():
    print("Send Weekly Report of Vrf Analysis in Email", file=sys.stderr)

    print("Generating Reports", file=sys.stderr)
    vrfAnalysisReport= "app/physical_mapping_reports/Exchange-Vrf-Analysis-Report-"+datetime.now().strftime("%d-%m-%Y")
    if not os.path.exists('app/physical_mapping_reports'):
        os.makedirs('app/physical_mapping_reports')
    try:
        print("Generating Vrf Analysis Weekly Report", file=sys.stderr)
        spof_extranet_vrfs= GetSpofVrfsTableFunc("")
        unsused_extranet_vrfs= GetUnusedVrfsTableFunc("")
        extranet_vrfs_with_missing_routes= GetVrfsWithMissingRoutesFunc("")
        intranet_vrfs_with_missing_routes= GetIntranetVrfsWithMissingRoutesTableFunc("")
        
        intranet_vrfs_with_missing_routes= GetIntranetVrfsWithMissingRoutesTableFunc("")
        GenerateWeeklyReportOfVrfAnalysis(spof_extranet_vrfs, unsused_extranet_vrfs, extranet_vrfs_with_missing_routes, intranet_vrfs_with_missing_routes, vrfAnalysisReport)

    except Exception as e:
        print(f"Exception Occured in Generating Reports {e}", file=sys.stderr)
    
    try:
        sendVrfAnalysisWeeklyEmail(vrfAnalysisReport)
    except Exception as e:
        print(f"Exception Occured in Sending Mail Reports {e}", file=sys.stderr)


def GenerateWeeklyReportOfVrfAnalysis(spof_extranet_vrfs, unsused_extranet_vrfs, extranet_vrfs_with_missing_routes, intranet_vrfs_with_missing_routes, fileName): 
    #iterate over data and save to excel
    spofExtranetObj = pd.DataFrame(columns=['vrf_name', 'primary_site', 'secondary_site'])
    spofExtranetObjIn=0
   
    try:
        for spof in spof_extranet_vrfs:
            spofExtranetObj.loc[spofExtranetObjIn,'vrf_name'] = spof.get('vrf_name', "")
            spofExtranetObj.loc[spofExtranetObjIn,'primary_site'] = spof.get('primary_site', "")
            spofExtranetObj.loc[spofExtranetObjIn,'secondary_site'] = spof.get('secondary_site', "")
                       
            spofExtranetObjIn+=1

    except Exception as e:
        print("error writing df")
        print(e, file=sys.stderr)

    unusedExtranetObj = pd.DataFrame(columns=['vrf_name', 'primary_site', 'secondary_site'])
    unusedExtranetObjIn=0
    try:
        for unused in unsused_extranet_vrfs:
            unusedExtranetObj.loc[unusedExtranetObjIn,'vrf_name'] = unused.get('vrf_name', "")
            unusedExtranetObj.loc[unusedExtranetObjIn,'primary_site'] = unused.get('primary_site', "")
            unusedExtranetObj.loc[unusedExtranetObjIn,'secondary_site'] = unused.get('secondary_site', "")
                       
            unusedExtranetObjIn+=1

    except Exception as e:
        print("error writing df")
        print(e, file=sys.stderr)
    
    missingExtranetObj = pd.DataFrame(columns=['vrf_name', 'primary_site', 'secondary_site', 'no_of_received_routes', 'missing_routes_in_secondary_site'])
    missingExtranetObjIn=0
    try:
        for missing in extranet_vrfs_with_missing_routes:
            missingExtranetObj.loc[missingExtranetObjIn,'vrf_name'] = missing.get('vrf_name', "")
            missingExtranetObj.loc[missingExtranetObjIn,'primary_site'] = missing.get('primary_site', "")
            missingExtranetObj.loc[missingExtranetObjIn,'secondary_site'] = missing.get('secondary_site', "")
            missingExtranetObj.loc[missingExtranetObjIn,'no_of_received_routes'] = missing.get('no_of_received_routes', "")
            missingExtranetObj.loc[missingExtranetObjIn,'missing_routes_in_secondary_site'] = missing.get('missing_routes_in_secondary_site', "")
            missingExtranetObjIn+=1

    except Exception as e:
        print("error writing df")
        print(e, file=sys.stderr)
    
    missingIntranetObj = pd.DataFrame(columns=['vrf_name', 'region', 'primary_site', 'secondary_site', 'no_of_received_routes', 'missing_routes_in_secondary_site', 'missing_sites_in_secondary_site'])
    missingIntranetObjIn=0
    try:
        for missing in intranet_vrfs_with_missing_routes:
            missingIntranetObj.loc[missingIntranetObjIn,'vrf_name'] = missing.get('vrf', "")
            missingIntranetObj.loc[missingIntranetObjIn,'region'] = missing.get('region', "")
            missingIntranetObj.loc[missingIntranetObjIn,'primary_site'] = missing.get('primary_site', "")
            missingIntranetObj.loc[missingIntranetObjIn,'secondary_site'] = missing.get('secondary_site', "")
            missingIntranetObj.loc[missingIntranetObjIn,'no_of_received_routes'] = missing.get('number_of_received_routes', "")
            missingIntranetObj.loc[missingIntranetObjIn,'missing_routes_in_secondary_site'] = missing.get('missing_routes_in_secondary_site', "")
            missingIntranetObj.loc[missingIntranetObjIn,'missing_sites_in_secondary_site'] = missing.get('missing_sites_in_secondary_site', "")
            missingIntranetObjIn+=1

    except Exception as e:
        print("error writing df")
        print(e, file=sys.stderr)
    
    try:
        writer = pd.ExcelWriter(fileName+".xlsx")
        #write dataframe to excel
        spofExtranetObj.to_excel(writer, sheet_name='SPOF Extranet Vrfs', index=False)
        unusedExtranetObj.to_excel(writer, sheet_name='Unused Extranet Vrfs', index=False)
        missingExtranetObj.to_excel(writer, sheet_name='Extranet Vrfs Missing Routes', index=False)
        missingIntranetObj.to_excel(writer, sheet_name='Intranet Vrfs Missing Routes', index=False)

        writer.save()
        
        # #Write CSV
        # dfObj.to_csv(file_name+".csv",index=False)
        # print('DataFrame is written successfully to CSV File.', file=sys.stderr)
    except Exception as e:
        print(f'Error While writing data to CSV file {e}', file=sys.stderr)

def sendVrfAnalysisWeeklyEmail(vrfAnalysisReport): 
    try:
        sender = 'IMS Inventory Report <reporter-sw@mobily.com.sa>'
        #receivers = ['majmal@mobily.com.sa']
        receivers = ['edn-bo@mobily.com.sa']


        msg = EmailMessage()
 
        msg.set_content('''
        Dear Team,

        Please Find Exchange Vrf Analysis Weekly Report.
        
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
        msg['Subject'] = 'Exchange VRFs Analysis Report <reporter-sw@mobily.com.sa>'
        msg['From'] = 'IMS Inventory Weekly Report <reporter-sw@mobily.com.sa>'
        msg['To'] = ", ".join(receivers)
        
        try:
            with open(vrfAnalysisReport+".xlsx", "rb") as f:
                file_data= f.read()
                file_name= f.name
                msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=file_name.split('/')[2])
        
        except Exception as e:
           print(f"EDN Mapping Not Found {e}", file=sys.stderr) 

        smtpObj.sendmail(sender, receivers, msg.as_string())
        print("Successfully Sent email", file=sys.stderr)
        return "Success"
    except SMTPException as e:
        print(f"Error: unable to send email {e}", file=sys.stderr)
