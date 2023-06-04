import imp
from logging import exception
import threading
import traceback
import requests
import json, sys, re, time
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from app.models.phy_mapping_models import EDN_MAC_LEGACY, EDN_LLDP_LEGACY, IGW_LLDP_LEGACY, IGW_MAC_LEGACY
from app import db
from app.models.inventory_models import FAILED_DEVICES_EDN_LLDP, FAILED_DEVICES_IGW_LLDP, FAILED_DEVICES_EDN_MAC, FAILED_DEVICES_IGW_MAC
import urllib3
from app.physical_mapping_scripts.aci_mac_address import MacAddressPuller
from app.physical_mapping_scripts.addFWIP import AddFwIP
from app.physical_mapping_scripts.addSericeMapping import AddServiceMapping
#from mac_vendor_lookup import MacLookup, MacVendorLookupError
from netaddr import EUI
from netaddr.core import NotRegisteredError

class LLDPPuller(object):
    
    def __init__(self):
        self.inv_data = {}
        self.cookie = {}
        self.base_url = None
        self.headers = None
        self.failed_devices=[]
        self.connections_limit = 50
        self.time=None
    
    # def add_to_failed_devices(self, host, reason):
    #     failed_device= {}
    #     failed_device["ip_address"]= host
    #     failed_device["date"]= time.strftime("%d-%m-%Y")
    #     failed_device["time"]= time.strftime("%H-%M-%S")
    #     failed_device["reason"]= reason
    #     self.failed_devices.append(failed_device)
        
    # def print_failed_devices(self,):
    #     print("Printing Failed Devices")
    #     file_name = time.strftime("%d-%m-%Y")+"-LLDP.txt"
    #     failed_device=[]
    #     #Read existing file
    #     try:
    #         with open('app/failed/ims/'+file_name,'r',encoding='utf-8') as fd:
    #             failed_device= json.load(fd)
    #     except:
    #         pass
    #     #Update failed devices list    
    #     failed_device= failed_device+self.failed_devices
    #     try:
    #         with open('app/failed/ims/'+file_name, 'w', encoding='utf-8') as fd:
    #             fd.write(json.dumps(failed_device))
    #     except Exception as e:
    #         print("Failed to update failed devices list"+ str(e), file=sys.stderr)

    def InsertData(self, obj):
        #add data to db
        db.session.add(obj)
        db.session.commit()
        return True
    
    def add_failed_devices_to_db(self, host, reason):

        
        if host["type"]=="EDN-LLDP":
            pmFailedDb = FAILED_DEVICES_EDN_LLDP()
        
        if host["type"]=="EDN-MAC":
            pmFailedDb = FAILED_DEVICES_EDN_MAC()

        if host["type"]== "IGW-MAC":
            pmFailedDb = FAILED_DEVICES_IGW_MAC()

        if host["type"]== "IGW-LLDP":
            pmFailedDb = FAILED_DEVICES_IGW_LLDP()

        try:
            pmFailedDb.ip_address = host['host']
            pmFailedDb.device_id = host['hostname']
            pmFailedDb.reason =reason
            pmFailedDb.date = host['time']
            
            self.InsertData(pmFailedDb)

            print('Successfully added Failed device to the Database', file = sys.stderr)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error while inserting failed device data into DB {e}", file=sys.stderr)

    def getMacVendor(self,mac):
        try:
            if mac:
                mac = EUI(mac)
                vendor = mac.oui.registration().org
                return vendor
        except NotRegisteredError:
            print("MAC address not found in the database")
            return ""
        except ValueError:
            print("Invalid MAC address")
            return ""
        except Exception as e:
            print("An error occurred:", e)
            return ""
        return ""

    def addInventoryToDB(self, host, inventory):
        #print(f"Inventory is: {inventory}")
        script=""
        data = inventory.get(host['host']).get('lldp')
        if data:
            try:
                
                for ldp in data:
                    local = ldp['local']
                    remote = ldp['remote']
                    if(local.get('data_type') =="lldp" or (local.get('data_type')=="mac" and  "infra-link" not in local.get('description', "").lower())):
                        if host["type"]=="EDN-LLDP":
                            lldpACI = EDN_LLDP_LEGACY()
                            script="lldp"
                        if host["type"]=="EDN-MAC":
                            lldpACI = EDN_MAC_LEGACY()
                            script="mac"

                        if host["type"]== "IGW-MAC":
                            lldpACI = IGW_MAC_LEGACY()
                            script="mac"
                        if host["type"]== "IGW-LLDP":
                            lldpACI = IGW_LLDP_LEGACY()
                            script="lldp"

                        lldpACI.device_a_name = local.get('hostname','')
                        lldpACI.device_a_interface= local.get('interface','')
                        lldpACI.device_a_trunk_name = local.get('trunk','')
                        lldpACI.device_a_tx = local.get('device_a_tx','')
                        lldpACI.device_a_rx = local.get('device_a_rx','')
                        lldpACI.device_a_ip = local.get('ip','')
                        remote_system_name= remote.get('system_name','')
                        remote_system_name= remote_system_name.replace('.mobily.com.sa', '')
                        lldpACI.device_b_system_name = remote_system_name
                        lldpACI.device_b_interface = remote.get('interface','')
                        lldpACI.device_b_ip = remote.get('ip','')
                        lldpACI.device_b_type = remote.get('type','')
                        lldpACI.device_b_port_desc = remote.get('description','')
                        if script == "lldp":
                            lldpACI.service_vendor = 'LLDP'
                        
                        mac= local.get('mac','')
                        mac = mac.replace(':', '')
                        new_mac_a=""
                        index=0
                        
                        for alph in mac:
                            if(index%4==0 and index!=0):
                                new_mac_a+="."
                            new_mac_a+=alph
                            index+=1
 
                        lldpACI.device_a_mac = new_mac_a.lower()
                        
                        mac= remote.get('mac','')
                        mac = mac.replace(':', '')
                        new_mac=""
                        index=0
                        for alph in mac:
                            if(index%4==0 and index!=0):
                                new_mac+="."
                            new_mac+=alph
                            index+=1
                        lldpACI.device_b_mac = new_mac.lower() #remote.get('mac','')
                        lldpACI.device_b_mac_vendor = self.getMacVendor(new_mac.lower())
                        lldpACI.device_a_port_desc =  local.get('description','')
                        vlan=local.get('vlan','')
                        if vlan:
                            vlan= vlan.replace("vlan-", "")
                        else: 
                            vlan=""
                        lldpACI.device_a_vlan = vlan
                        lldpACI.device_a_vlan_name = local.get('vlan_name','')
                        lldpACI.creation_date = host["time"]
                        lldpACI.modification_date = host["time"]
                        
                        if script=="lldp":
                            if local.get('data_type')=="lldp":
                                db.session.add(lldpACI)
                                db.session.commit()

                        if script=="mac":
                            if local.get('data_type')=="mac":
                                db.session.add(lldpACI)
                                db.session.commit()
                    
                        print(f"Successfully Inserted Record to DB {lldpACI.device_a_ip} ", file=sys.stderr)                 
            except Exception as e:
                #failedDB
                self.add_failed_devices_to_db(host, f"Error while inserting data into DB {e}")
                print(f"Error while inserting data into DB {e}", file=sys.stderr)
                db.session.rollback()
                #self.add_to_failed_devices(host['host'], f"Failed to insert Data to DB "+str(e))

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
                self.headers = {'cache-control': "no-cache"}
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
        
    def get_lldp_data(self, hosts):
        
        for host in hosts:
            login = self.connectACI(host)
            
            if login==False:
                #failedDB
                self.add_failed_devices_to_db(host, f"Failed to Login")
                self.inv_data[host['host']] = {"error":"Login Failed"} 
                #self.add_to_failed_devices(host['host'], "Failed to login to host")   
                print(f"Failed to login to host {host['host']}", file=sys.stderr)  
                continue
            
            #getting lldp data
            else:
                print(f"Sucessfully Logged in to host {host['host']}", file=sys.stderr)
                try:
                    print(" getting lldp node data", file=sys.stderr)
                    local_node_data = []
                    
                    lldpIf_url = f'{self.base_url}/api/node/class/lldpIf.json?rsp-subtree=children&rsp-subtree-class=lldpIf,lldpAdjEp&rsp-subtree-include=required&order-by=lldpIf.name|desc'
                    
                    get_response = requests.get(lldpIf_url, headers=self.headers, cookies=self.cookie, verify=False)

                    if get_response.ok:
                        get_response= get_response.json()
                        imdata = get_response['imdata']
                        #print(f' ##  Main Nodes data is {imdata}', file=sys.stderr)
                        if imdata:
                            for x in imdata:
                                lldpIf = x['lldpIf']['attributes']
                                lldpAdjEp = x['lldpIf']['children']
                                node = re.findall(r'paths-(\d+)', lldpIf['portDesc'])
                                node = node[0] if node else None
                                if node:
                                    for y in lldpAdjEp:
                                        adj = y['lldpAdjEp']['attributes']
                                        if adj['capability']:
                                            b_type= adj['capability'].replace('bridge,','')
                                        else:
                                            if 'APIC' in  adj['sysName'].replace('.ee.mobily.com.sa',''):
                                                b_type = 'APIC'
                                                
                                        if 'unspecified' not in adj['mgmtIp']:
                                            local_node_data.append({'local':{
                                                                    'hostname': 'node-'+node,
                                                                    'interface':lldpIf['id'],
                                                                    'ip':None,
                                                                    'mac':lldpIf['mac'],
                                                                    'trunk':None,
                                                                    'description':None,
                                                                    'data_type':"lldp"
                                                                    },
                                                                    'remote':{
                                                                        'system_name':adj['sysName'].replace('.ee.mobily.com.sa',''),
                                                                        'interface':adj['portIdV'],
                                                                        'ip':adj['mgmtIp'],
                                                                        'description':adj['portDesc'],
                                                                        'type':b_type,
                                                                        'mac':adj['chassisIdV']
                                                                    }})
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    #self.add_to_failed_devices(host['host'], "Failed to get LLDP data "+str(e))
                    print(f"lldp node data not found {e}", file=sys.stderr)
                    lldpIf = None
                    
                #getting device A Port description
                try:
                    ethpmAggrIf_url = f'{self.base_url}/api/node/class/l1PhysIf.json?&order-by=l1PhysIf.modTs|desc'
                    get_response = requests.get(ethpmAggrIf_url, headers=self.headers, cookies=self.cookie, verify=False)
                    if get_response.ok:
                        get_response= get_response.json()
                        imdata = get_response['imdata']
                        if imdata:
                            for l_node in local_node_data:
                                for x in imdata:
                                    ethpmAggrIf = x['l1PhysIf']['attributes']
                                    ethpm_node = re.findall(r'node-(\d+)', ethpmAggrIf['dn'])
                                    ethpm_node = 'node-'+ethpm_node[0] if ethpm_node else None
                                    intf = re.findall(r'(eth\d+\/\d+)', ethpmAggrIf['dn'])
                                    intf = intf[0].strip() if intf else None
                                    
                                    if (l_node['local']['interface'].strip()==intf) and (l_node['local']['hostname']==ethpm_node):
                                        l_node['local'].update({'description':ethpmAggrIf['descr']})
                                    
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    #self.add_to_failed_devices(host['host'], "Failed to get Device A port description "+str(e))
                    print(f"error detail =>{e}", file=sys.stderr)
                
                #getting Device A trunk         
                try:
                    ethpmAggrIf_url = f'{self.base_url}/api/node/class/ethpmAggrIf.json?&order-by=ethpmAggrIf.modTs|desc'
                    get_response = requests.get(ethpmAggrIf_url, headers=self.headers, cookies=self.cookie, verify=False)
                
                    if get_response.ok:
                        get_response= get_response.json()
                        imdata = get_response['imdata']
                        #print(f" ## device a trunk is : {imdata}", file=sys.stderr)
                        
                        if imdata:
                            for l_node in local_node_data:
                                for x in imdata:
                                    ethpmAggrIf = x['ethpmAggrIf']['attributes']
                                    ethpm_node = re.findall(r'node-(\d+)', ethpmAggrIf['dn'])
                                    ethpm_node = 'node-'+ethpm_node[0] if ethpm_node else None
                                    intf = re.findall(r'eth(\d+\/\d+)', ethpmAggrIf['activeMbrs'])
                                    interfaces = ['eth'+x for x in intf] 
                                    for intf in interfaces:
                                        if (l_node['local']['interface'].strip()==intf) and (l_node['local']['hostname']==ethpm_node):
                                            port_channel = re.findall(r'\[po(\d+)', ethpmAggrIf['dn'])  
                                            port_channel = 'po'+port_channel[0] if port_channel else None
                                            #print(f"## {l_node['local']}    port channel is: {port_channel}", file=sys.stderr)
                                            l_node['local'].update({'trunk':port_channel})
                    else:
                        raise Exception(str(get_response.text))                    
                except Exception as e:
                    #self.add_to_failed_devices(host['host'], "Failed to get Device A Trunk "+str(e))
                    print(f"error=> {e}", file=sys.stderr)
                    traceback.print_exc()
                
                #getting Device A IP
                try:
                    mgmtRsOoBStNode_url = f'{self.base_url}/api/node/class/mgmtRsOoBStNode.json?&order-by=mgmtRsOoBStNode.modTs|desc'
                    get_response = requests.get(mgmtRsOoBStNode_url, headers=self.headers, cookies=self.cookie, verify=False)
                    if get_response.ok:
                        get_response= get_response.json()
                        mgmtRsOoBStNode_imdata = get_response['imdata']
                        if mgmtRsOoBStNode_imdata:
                            for l_node in local_node_data:
                                for x in mgmtRsOoBStNode_imdata:
                                    mgmtRsOoBStNode = x['mgmtRsOoBStNode']['attributes']
                                    node = re.findall(r'node-(\d+)', mgmtRsOoBStNode['tDn'])  
                                    mg_node = 'node-'+node[0] if node else None
                                    if mg_node and (mg_node.strip()==l_node['local']['hostname'].strip()):
                                        addr = re.findall(r'(.*)\/', mgmtRsOoBStNode['addr'])
                                        l_node['local'].update({'ip':addr[0]})
                    else:
                        raise Exception(str(get_response.text))                    
                except Exception as e:
                    #self.add_to_failed_devices(host['host'], "Failed to get Device A IP "+str(e))
                    print(f"error=> {e}", file=sys.stderr)
                    traceback.print_exc()
                    
                #getting Device A hostname
                try:
                    fabricNode_url = f'{self.base_url}/api/node/class/fabricNode.json?&order-by=fabricNode.modTs|desc'
                    get_response = requests.get(fabricNode_url, headers=self.headers, cookies=self.cookie, verify=False)
                    if get_response.ok:
                        get_response= get_response.json()
                        fabricNode_imdata = get_response['imdata']
                        if fabricNode_imdata:
                            for l_node in local_node_data:
                                for x in fabricNode_imdata:
                                    fabricNode = x['fabricNode']['attributes']
                                    node = re.findall(r'node-(\d+)', fabricNode['dn']) 
                                    node = node[0] if node else None
                                    if node and (l_node['local']['hostname']=='node-'+node):
                                        l_node['local'].update({'hostname':fabricNode['name']})    
                
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    #self.add_to_failed_devices(host['host'], "Failed to get Device A Hostname "+str(e))
                    print(f"error=> {e}", file=sys.stderr)     
                    traceback.print_exc()               
                
                try:
                
                    if host['host'] not in self.inv_data:
                        self.inv_data[host['host']] = {}
                    
                    puller = MacAddressPuller()
                    res = puller.get_mac_address_table_data([host])
                    data = res[host['host']]['lldp']
                    for x in data:
                        for y in local_node_data:
                            if (x['local']['hostname']==y['local']['hostname']) and (x['local']['interface']==y['local']['interface']):
                                x['local'].update({'ip':y['local']['ip']})
                    
                    local_node_data.extend(data)
                    
                    
                    # local_node_data.extend(mac_data)
                    self.inv_data[host['host']].update({'lldp': local_node_data})
                    self.inv_data[host['host']].update({'status': 'success'})
                                  
                except Exception as e:
                    #failedDB
                    self.add_failed_devices_to_db(host, f"Error while getting LLDP data {e}")
                    #self.add_to_failed_devices(host['host'], "Failed to get MAC Address Data "+str(e))
                    print(f"error=> {e}", file=sys.stderr)
                    traceback.print_exc()
                    if host['host'] in self.inv_data:
                        self.inv_data[host['host']].update({'status': 'error'})
                        self.inv_data[host['host']].update({'lldp': []})
                
            
            self.addInventoryToDB(host, self.inv_data)
            break
            return self.inv_data
    
    def FormatStringDate(self, date):
        #print(date, file=sys.stderr)
        try:

            if date is not None:
                result = datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
                return result
           
        except:
            result=datetime(2000, 1,1)
            print("date format exception", file=sys.stderr)
            return result
       
    def getPhysicalMapping(self, datacenters, domain):
        puller = LLDPPuller()
        
        with open('app/cred.json') as inventory:
            inv = json.loads(inventory.read())
        for dc in datacenters:
            hosts = []
            for apic in datacenters[dc]:
                if 'IGW' in apic['type']:
                    user_name = inv['IGW']['user']
                    password = inv['IGW']['pwd']

                if 'EDN' in apic['type']:
                    user_name = inv['EDN']['user']
                    password = inv['EDN']['pwd']

                host={
                    "host": apic["ip"],
                    "user": user_name,
                    "pwd": password,
                    "sw_type": apic["sw_type"],
                    'hostname':apic["hostname"],
                    'time': self.FormatStringDate(apic["time"]),
                    'type': apic["type"]                
                }
                self.time= host.get("time")
                hosts.append(host)                

            puller.get_lldp_data(hosts)
        #self.print_failed_devices()
        '''
        if domain== "EDN":
            print("Populating Firewall IP's in Edn LLDP ACI", file=sys.stderr)
            fwIp= AddFwIP()
            fwIp.addFWIPToEdnLldpAci(self.time)

            print("Populating Service Mapping in EDN MAC ACI ", file=sys.stderr)
            serviceMapping= AddServiceMapping()
            serviceMapping.addEdnLldpACIServiceMapping(self.time)
        else:
            print("Populating Service Mapping in IGW MAC ACI ", file=sys.stderr)
            serviceMapping= AddServiceMapping()
            serviceMapping.addIgwLldpACIServiceMapping(self.time)
        '''
        print("LLDP  Completed", file=sys.stderr)

