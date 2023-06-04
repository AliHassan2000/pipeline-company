import sys
import json
from numpy import std
import requests
#import imp
from logging import exception
import traceback
import requests
import json, sys, re, time
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from app import db
import urllib3
from app.models.inventory_models import EDN_DC_CAPACITY, IGW_DC_CAPACITY, Seed, FAILED_DEVICES_EDN_DC_CAPACITY, FAILED_DEVICES_IGW_DC_CAPACITY

from collections import Counter



class DCCAPACITYAPIC(object):
    def __init__(self):
        self.connections_limit = 50
        self.failed_devices=[]
        self.cookie = {}
        self.base_url= None
        self.headers = None

    def add_failed_devices_to_db(self, host, reason):
        if host['type']=='EDN':
            dccapacityFailedDb = FAILED_DEVICES_EDN_DC_CAPACITY()
        if host['type']=='IGW':
            dccapacityFailedDb = FAILED_DEVICES_IGW_DC_CAPACITY()
        
        try:
            dccapacityFailedDb.ip_address = host['host']
            dccapacityFailedDb.device_id = host['device_id']
            dccapacityFailedDb.reason =reason
            dccapacityFailedDb.date = host['time']
            
            self.InsertData(dccapacityFailedDb)
            print('Successfully added Failed device to the Database', file = sys.stderr)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error while inserting failed device data into DB {e}", file=sys.stderr)


    def InsertData(self,obj):
        #add data to db
        db.session.rollback()
        db.session.add(obj)
        db.session.commit()
        return True

    def getDCCapacity(self, datacenters):
        print(f"DEVICES APIC RECEIVED: {datacenters}", file=sys.stderr)
        puller = DCCAPACITYAPIC()
        with open('app/cred.json') as inventory:
            inv = json.loads(inventory.read())
        for dc in datacenters:
            hosts = []
            for apic in datacenters[dc]:
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
                    'time': str(apic["time"]),
                    'type': apic["type"]  , 
                    'user_id': apic['user_id'],  
                    'device_id': apic['device_id']             
                }
                self.time= host.get("time")
                hosts.append(host)                
            print(f"DEVICES APIC DAA: {hosts}", file=sys.stderr)
            try:
                puller.getDCCapacityData(hosts)
            except Exception as e: 
                print("Exception occured")
        #puller.print_failed_devices()
        print("DC Capacity Completed", file=sys.stderr)

    def addInventoryToDB(self, host, dcCapacity):   
        #for dcCapacity in dcCapacity_data:
        dcCapacityDb=''
        if host['type']=='EDN':
            dcCapacityDb = EDN_DC_CAPACITY()
        if host['type']=='IGW':
            dcCapacityDb = IGW_DC_CAPACITY()
        
        
        query_string = f"select site_id, device_id, sw_type from seed_table where ne_ip_address= '{dcCapacity['ip_address']}' and site_type='DC';" 
        result = db.session.execute(query_string)
        try:
            for row in result:
                ednDcCapacityDict = {}
                dcCapacityDb.site_id = row[0]
                dcCapacityDb.device_id = row[1]
                dcCapacityDb.os_version = row[2]
                dcCapacityDb.device_ip = dcCapacity['ip_address']
        
                dcCapacityDb.total_1g_ports = dcCapacity.get('total_1g_ports','') if dcCapacity.get('total_1g_ports','') is not None else 0
                dcCapacityDb.total_10g_ports = dcCapacity.get('total_10g_ports','') if dcCapacity.get('total_10g_ports','') is not None else 0
                dcCapacityDb.total_25g_ports = dcCapacity.get('total_25g_ports','') if dcCapacity.get('total_25g_ports','') is not None else 0
                dcCapacityDb.total_40g_ports = dcCapacity.get("total_40g_ports",'') if dcCapacity.get('total_40g_ports','') is not None else 0
                dcCapacityDb.total_100g_ports = dcCapacity.get("total_100g_ports",'') if dcCapacity.get('total_100g_ports','') is not None else 0
                dcCapacityDb.total_fast_ethernet_ports = dcCapacity.get('total_fast_ethernet_ports','') if dcCapacity.get('total_fast_ethernet_ports','') is not None else 0

                dcCapacityDb.connected_1g = dcCapacity.get('connected_1g','') if dcCapacity.get('connected_1g','') is not None else 0
                dcCapacityDb.connected_10g = dcCapacity.get('connected_10g','') if dcCapacity.get('connected_10g','') is not None else 0
                dcCapacityDb.connected_25g = dcCapacity.get('connected_25g','') if dcCapacity.get('connected_25g','') is not None else 0
                dcCapacityDb.connected_40g = dcCapacity.get('connected_40g','') if dcCapacity.get('connected_40g','') is not None else 0
                dcCapacityDb.connected_100g = dcCapacity.get('connected_100g','') if dcCapacity.get('connected_100g','') is not None else 0
                dcCapacityDb.connected_fast_ethernet = dcCapacity.get('connected_fast_ethernet','') if dcCapacity.get('connected_fast_ethernet','') is not None else 0


                dcCapacityDb.not_connected_1g = dcCapacity.get('not_connected_1g','') if dcCapacity.get('not_connected_1g','') is not None else 0
                dcCapacityDb.not_connected_10g = dcCapacity.get('not_connected_10g','') if dcCapacity.get('not_connected_10g','') is not None else 0
                dcCapacityDb.not_connected_25g = dcCapacity.get('not_connected_25g','') if dcCapacity.get('not_connected_25g','') is not None else 0
                dcCapacityDb.not_connected_40g = dcCapacity.get('not_connected_40g','') if dcCapacity.get('not_connected_40g','') is not None else 0
                dcCapacityDb.not_connected_100g = dcCapacity.get('not_connected_100g','') if dcCapacity.get('not_connected_100g','') is not None else 0
                dcCapacityDb.not_connected_fast_ethernet = dcCapacity.get('not_connected_fast_ethernet','') if dcCapacity.get('not_connected_fast_ethernet','') is not None else 0


                dcCapacityDb.unused_sfps_1g = dcCapacity.get('unused_sfps_1g','')
                dcCapacityDb.unused_sfps_10g = dcCapacity.get('unused_sfps_10g','')
                dcCapacityDb.unused_sfps_25g = dcCapacity.get('unused_sfps_25g','')
                dcCapacityDb.unused_sfps_40g = dcCapacity.get('unused_sfps_40g','')
                dcCapacityDb.unused_sfps_100g = dcCapacity.get('unused_sfps_100g','')
                
                dcCapacityDb.creation_date = host['time']
                dcCapacityDb.modification_date = host['time']
                dcCapacityDb.created_by = host['user_id']
                dcCapacityDb.modified_by = host['user_id']

                if dcCapacityDb.os_version !="APIC":
                    self.InsertData(dcCapacityDb)
                print('Successfully added to the Database',file = sys.stderr)
                #failedDB
                #self.add_failed_devices_to_db(host, f"Error while inserting data into DB {e}")
                print('Successfully added to the Database',file = sys.stderr)
        
        except Exception as e:
            #failedDB
            self.add_failed_devices_to_db(host, f"Error while inserting data into DB {e}")
            
            print('Successfully added to the Database',file = sys.stderr)
            #db.session.rollback()
            print(f"Error while inserting data into DB {e}", file=sys.stderr)
            #self.add_to_failed_devices(host['device_ip'], f"Failed to insert Data to DB "+str(e))

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
    
    def getDCCapacityData(self, hosts):    
        for host in hosts:
            login = self.connectACI(host)
            
            if login==False:
                #inv_data[host['host']] = {"error":"Login Failed"} 
                #add_to_failed_devices(host['host'], "Failed to login to host")   
                print(f"Failed to login to host {host['host']}", file=sys.stderr)  
                #failedDB
                self.add_failed_devices_to_db(host, f"Failed To Login")
                continue
            #getting lldp data
            else:
                
                leafIpAddresses= []
                leafInterfacesSpeed= []
                leafSfpStatus= []
                portCapStatus= []

                print(f"Sucessfully Logged in to host {host['host']}", file=sys.stderr)
                try:
                    print("getting APIC Node Ip Address data", file=sys.stderr)
      
                    ip_url = f'{self.base_url}/api/node/class/mgmtRsOoBStNode.json?&order-by=mgmtRsOoBStNode.modTs|desc'
                    
                    ip_response = requests.get(ip_url, headers=self.headers, cookies=self.cookie, verify=False)
                    
                   
                    if ip_response.ok:
                        ip_response= ip_response.json()
                        ipdata = ip_response['imdata']
                        
                        if ipdata:
                            for x in ipdata:
                                ip_addresses= {}
                                lldpIf = x['mgmtRsOoBStNode']['attributes']
                                ip_addresses["tdn"]= lldpIf.get('tDn')
                                ip_addresses["ip_address"]= lldpIf.get('addr').split('/')[0]
                                leafIpAddresses.append(ip_addresses)
                
                    
                    ip_url = f'{self.base_url}/api/node/class/ethpmPhysIf.json?&order-by=ethpmPhysIf.modTs|desc'
                    speed_response = requests.get(ip_url, headers=self.headers, cookies=self.cookie, verify=False)                    
                    if speed_response.ok:
                        speed_response= speed_response.json()
                        speeddata = speed_response['imdata']

                        if speeddata:
                            for x in speeddata:
                                interface_Speed= {}
                                lldpIf = x['ethpmPhysIf']['attributes']

                                interface_Speed["speed"]= lldpIf.get('operSpeed')
                                interface_Speed["status"]= lldpIf.get('operSt')
                                interface_Speed["dn"]= lldpIf.get('dn')
                                interface_Speed["name"]= re.findall(r'\S+\[(.*)\]',lldpIf.get('dn'))[0]
                                leafInterfacesSpeed.append(interface_Speed)
                                 
                                ####
                                #if lldpIf.get('operSpeed').lower()== "unknown":
                                #    print(f"APIC: {host['host']},  DN: {lldpIf.get('dn')},  Interface: {interface_Speed['name']}, Status: {lldpIf.get('operSpeed')}", file=sys.stderr)
                   

                
                    ip_url = f'{self.base_url}/api/node/class/ethpmFcot.json?&order-by=ethpmFcot.modTs|desc'
                    sfp_state = requests.get(ip_url, headers=self.headers, cookies=self.cookie, verify=False)
                    if sfp_state.ok:
                        sfp_state= sfp_state.json()   
                        speeddata = sfp_state['imdata']
                        #print(speeddata, file=sys.stderr)
                        if speeddata:
                            for x in speeddata:
                                sfp_status={}
                                lldpIf = x['ethpmFcot']['attributes']
                                sfp_status["state"]= lldpIf.get('state')
                                sfp_status["sfp_type"]= lldpIf.get('typeName')
                                sfp_status["dn"]= lldpIf.get('dn')
                                sfp_status["name"]= re.findall(r'\S+\[(.*)\]',lldpIf.get('dn'))[0]
                                leafSfpStatus.append(sfp_status)
                    
                    ip_url = f'{self.base_url}/api/node/class/ethpmPortCap.json?&order-by=ethpmPortCap.modTs|desc'
                    port_cap = requests.get(ip_url, headers=self.headers, cookies=self.cookie, verify=False)
                    if port_cap.ok:
                        port_cap= port_cap.json()   
                        port_cap_data = port_cap['imdata']
                        if port_cap_data:
                            for x in port_cap_data:
                                port_cap_status={}
                                lldpIf = x['ethpmPortCap']['attributes']
                                port_cap_status["portcap_status"]= lldpIf.get('speed')
                                port_cap_status["dn"]= lldpIf.get('dn')
                                port_cap_status["name"]= re.findall(r'\S+\[(.*)\]',lldpIf.get('dn'))[0]
                                portCapStatus.append(port_cap_status)

                    
                    #parse all data
                    #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^", file=sys.stderr)
                    #print(f"@@@@  {u_speed}", file=sys.stderr)
                    #print(f"####  {u_status}", file=sys.stderr)
                    #print(f"$$$$  {u_sfp_state}", file=sys.stderr)
                    #print("+++++++++++++++++++++++++++++++++++++++", file=sys.stderr)

                    #merge state and interface speed
                    for int in leafInterfacesSpeed:
                        for sfp in leafSfpStatus :
                            if int['name']== sfp['name'] and int['dn']== sfp['dn'][:-5]:
                                int['sfp_state']= sfp['state']
                    
                    #parse unknown
                    #print(portCapStatus, file=sys.stderr)
                    for int in leafInterfacesSpeed:
                        if int['speed'].lower()== "unknown":
                            print(f"#### {int}", file=sys.stderr)
                            #print(int, file=sys.stderr)
                            try:
                                pcapdevice=[]
                                #print(leafSfpStatus, file=sys.stderr)
                                sfpState= list(filter(lambda node: node['name']== int['name'] and node['dn'][:-5]== int['dn'] , leafSfpStatus))[0]
                                #print(f"@@@@ {sfp_state}")
                                #if len(sfp_state)>0:
                                if sfpState['sfp_type']:
                                    if '1G' in sfpState['sfp_type'] or '1000' in sfpState['sfp_type']:
                                        speed= '1G'
                                    if '10G' in sfpState['sfp_type']:
                                        speed= '10G'
                                    if '25G' in sfpState['sfp_type']:
                                        speed= '25G'
                                    if '40G' in sfpState['sfp_type']:
                                        speed= '40G'
                                    if '100G' in sfpState['sfp_type']:
                                        speed= '100G'
                                else:
                                    pcapdevice= list(filter(lambda node: int['name']== node['name'] and int['dn']== node['dn'][:-8] , portCapStatus))
                                    #print(f"$$$ {pcapdevice}")
                                    if len(pcapdevice)>0:
                                        speed= pcapdevice[0]['portcap_status']
                                        speed=speed.split(',')
                                        tempSpeed=[]
                                        for item in speed:
                                            if(item.isdigit()):
                                                tempSpeed.append(item)
                                        speed=max(tempSpeed)
                                        if speed=="1000":
                                            speed='1G'
                                        if speed=="10000":
                                            speed='10G'
                                        if speed=="25000":
                                            speed='25G'
                                        if speed=="40000":
                                            speed='40G'
                                        if speed=="100000":
                                            speed='100G'
                                        
                                        int['speed']=speed
                                    else:
                                        int['speed']="25G"
                                        #print(f"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ {speed}  {int}", file=sys.stderr)
                                
                                '''
                                pcapdevice= list(filter(lambda node: int['name']== node['name'] and int['dn']== node['dn'][:-8] , portCapStatus))
                                print(pcapdevice, file=sys.stderr)
                                if len(pcapdevice)>0:
                                    sfpState= list(filter(lambda node: node['name']== pcapdevice[0]['name'] and node['dn'][:-4]== pcapdevice[0]['dn'][:-7] , leafSfpStatus))
                                    
                                    if len(sfpState)>0:
                                        if sfpState[0].get('state')== "inserted":
                                            print(sfpState, file=sys.stderr)
                                            print("-------------", file=sys.stderr)
                                            #print(sfpState[0].get('sfp_type'), file=sys.stderr)
                                            #print(sfpState[0].get('status'), file=sys.stderr)
                                            
                                            #print(f"@@@ {pcapdevice}", file=sys.stderr)
                                            #print(f"??? {sfpState}", file=sys.stderr)
                                    
                                    speed= pcapdevice[0]['portcap_status']
                                    speed=speed.split(',')
                                    tempSpeed=[]
                                    for item in speed:
                                        if(item.isdigit()):
                                            tempSpeed.append(item)
                                    speed=max(tempSpeed)
                                    if speed=="1000":
                                        speed='1G'
                                    if speed=="10000":
                                        speed='10G'
                                    if speed=="25000":
                                        speed='25G'
                                    if speed=="40000":
                                        speed='40G'
                                    if speed=="100000":
                                        speed='100G'
                                    
                                    int['speed']=speed
                                else:
                                    int['speed']="25G"
                                '''  
                            except Exception as e:
                                
                                print(f"Error in Parsing Unknown  for Node {e} {int['dn']} APIC: {host['host']}", file=sys.stderr)
                                traceback.print_exc()

                    #print(leafIpAddresses, file=sys.stderr)      
                    dataFounf=0
                    for leaf in leafIpAddresses:
                        dcCapacityData={}
                        dcCapacityData["ip_address"]= leaf['ip_address']
                        #device_interfaces= next(item for item in leafInterfacesSpeed if item["dn"]=="opology/pod-1/node-339/sys/phys-[eth1/94]/phys/fco")
                        device_interfaces= list(filter(lambda node: leaf["tdn"] in node['dn'], leafInterfacesSpeed))
                        interfaces_count= Counter(int['speed'] for int in device_interfaces  )
                        dcCapacityData["total_1g_ports"]= interfaces_count.get('1G')
                        dcCapacityData["total_10g_ports"]= interfaces_count.get('10G')
                        dcCapacityData["total_25g_ports"]= interfaces_count.get('25G')
                        dcCapacityData["total_40g_ports"]= interfaces_count.get('40G')
                        dcCapacityData["total_100g_ports"]= interfaces_count.get('100G')
                        dcCapacityData["total_fast_ethernet_ports"]= interfaces_count.get('100M')

                        status_1g_connected= Counter(int['status'] for int in device_interfaces if int['speed']=="1G" and int['status'].lower()=='up')
                        status_1g_not_connected = Counter(int['status'] for int in device_interfaces if int['speed']=="1G" and int['status'].lower()!='up')
                        dcCapacityData["connected_1g"]= status_1g_connected.get('up')
                        dcCapacityData["not_connected_1g"]= status_1g_not_connected.get('down')

                        status_10g_connected= Counter(int['status'] for int in device_interfaces if int['speed']=="10G" and int['status'].lower()=='up')
                        status_10g_not_connected = Counter(int['status'] for int in device_interfaces if int['speed']=="10G" and int['status'].lower()!='up')
                        dcCapacityData["connected_10g"]= status_10g_connected.get('up')
                        dcCapacityData["not_connected_10g"]= status_10g_not_connected.get('down')

                        status_25g_connected= Counter(int['status'] for int in device_interfaces if int['speed']=="25G" and int['status'].lower()=='up')
                        status_25g_not_connected = Counter(int['status'] for int in device_interfaces if int['speed']=="25G" and int['status'].lower()!='up')
                        dcCapacityData["connected_25g"]= status_25g_connected.get('up')
                        dcCapacityData["not_connected_25g"]= status_25g_not_connected.get('down')

                        status_40g_connected= Counter(int['status'] for int in device_interfaces if int['speed']=="40G" and int['status'].lower()=='up')
                        status_40g_not_connected = Counter(int['status'] for int in device_interfaces if int['speed']=="40G" and int['status'].lower()!='up')
                        dcCapacityData["connected_40g"]= status_40g_connected.get('up')
                        dcCapacityData["not_connected_40g"]= status_40g_not_connected.get('down')

                        status_100g_connected= Counter(int['status'] for int in device_interfaces if int['speed']=="100G" and int['status'].lower()=='up')
                        status_100g_not_connected = Counter(int['status'] for int in device_interfaces if int['speed']=="100G" and int['status'].lower()!='up')
                        dcCapacityData["connected_100g"]= status_100g_connected.get('up')
                        dcCapacityData["not_connected_100g"]= status_100g_not_connected.get('down')

                        status_fast_ethernet_connected= Counter(int['status'] for int in device_interfaces if int['speed']=="100M" and int['status'].lower()=='up')
                        status_fast_ethernet_not_connected = Counter(int['status'] for int in device_interfaces if int['speed']=="100M" and int['status'].lower()!='up')
                        dcCapacityData["connected_fast_ethernet"]= status_fast_ethernet_connected.get('up')
                        dcCapacityData["not_connected_fast_ethernet"]= status_fast_ethernet_not_connected.get('down')

                        unused_sfps_1g= Counter(int['status'] for int in device_interfaces if int['speed']=="1G" and int['status'].lower()!='up' and int['sfp_state'].lower()=="inserted")
                        unused_sfps_1g = sum(unused_sfps_1g[item] for item in unused_sfps_1g if item.lower()!='up')
                        dcCapacityData["unused_sfps_1g"]= unused_sfps_1g

                        unused_sfps_10g= Counter(int['status'] for int in device_interfaces if int['speed']=="10G" and int['status'].lower()!='up' and int['sfp_state'].lower()=="inserted")
                        unused_sfps_10g = sum(unused_sfps_10g[item] for item in unused_sfps_10g if item.lower()!='up')
                        dcCapacityData["unused_sfps_10g"]= unused_sfps_10g

                        unused_sfps_25g= Counter(int['status'] for int in device_interfaces if int['speed']=="25G" and int['status'].lower()!='up' and int['sfp_state'].lower()=="inserted")
                        unused_sfps_25g = sum(unused_sfps_25g[item] for item in unused_sfps_25g if item.lower()!='up')
                        dcCapacityData["unused_sfps_25g"]= unused_sfps_25g

                        unused_sfps_40g= Counter(int['status'] for int in device_interfaces if int['speed']=="40G" and int['status'].lower()!='up' and int['sfp_state'].lower()=="inserted")
                        unused_sfps_40g = sum(unused_sfps_40g[item] for item in unused_sfps_40g if item.lower()!='up')
                        dcCapacityData["unused_sfps_40g"]= unused_sfps_40g

                        unused_sfps_100g= Counter(int['status'] for int in device_interfaces if int['speed']=="100G" and int['status'].lower()!='up' and int['sfp_state'].lower()=="inserted")
                        unused_sfps_100g = sum(unused_sfps_100g[item] for item in unused_sfps_100g if item.lower()!='up')
                        dcCapacityData["unused_sfps_100g"]= unused_sfps_100g

                        self.addInventoryToDB(host, dcCapacityData)
                        if dcCapacityData:
                            dataFound=1
                    if dataFound==1:
                        break
                except Exception as e:
                    #failedDB
                    self.add_failed_devices_to_db(host, f"Error while inserting data into DB {e}")
                    #self.add_to_failed_devices(host['device_ip'], "Failed to get DC Capacity data "+str(e))
                    traceback.print_exc()
                    print(f"Failed to get data from APIC {e}", file=sys.stderr)

'''

hosts=[]

host={}
host['host']= "10.42.211.175"
host['user']= "srv00047"
host['pwd']= "5FPB4!!1c9&g*iJ8"


hosts.append(host)

getDCCapacityData(hosts)


'''
