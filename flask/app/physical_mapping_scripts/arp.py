# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:23:08 2021

@author: HP
"""
#from mac_vendor_lookup import MacLookup, MacVendorLookupError
from netmiko import Netmiko
import re, sys, json, time
from numpy import std
import pandas as pd
from pandas import read_excel
import traceback
from app import db,tz
from app.models.phy_mapping_models import EDN_MAC_LEGACY
import numpy as np
import threading
from app.physical_mapping_scripts.addFWIP import AddFwIP
from app.physical_mapping_scripts.addSericeMapping import AddServiceMapping
from app.models.inventory_models import FAILED_DEVICES_EDN_MAC
from datetime import date, datetime
from netaddr import EUI
from netaddr.core import NotRegisteredError

class EdnMacLegacy(): 

    def __init__(self):
        self.connections_limit = 50
        self.failed_devices=[]
        self.time=None

    def add_failed_devices_to_db(self, host, reason):
        pmFailedDb = FAILED_DEVICES_EDN_MAC()
        
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

    # def add_to_failed_devices(self, host, reason):
    #     failed_device= {}
    #     failed_device["ip_address"]= host
    #     failed_device["date"]= time.strftime("%d-%m-%Y")
    #     failed_device["time"]= time.strftime("%H-%M-%S")
    #     failed_device["reason"]= reason
    #     self.failed_devices.append(failed_device)   
    
    # def print_failed_devices(self,):
    #     print("Printing Failed Devices")
    #     file_name = time.strftime("%d-%m-%Y")+"-CDP.txt"
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
    #         print(e)
    #         print("Failed to update failed devices list"+ str(e), file=sys.stderr)

    def InsertData(self, obj):
        #add data to db
        db.session.add(obj)
        db.session.commit()
        return True

    def normalizeInterface(self, host, interface):
        match = re.search(r'\d', interface)
        prefix=""
        postfix=""

        if match:
            first_int_index = match.start()
            prefix = interface[:first_int_index]
            suffix = interface[first_int_index:]
            #print(prefix, suffix)

        if  prefix== "ethernet":
            #interface=interface.split('ethernet')[1]
            interface= 'eth'+str(suffix)
        if prefix== "gigabitethernet":
            #interface=interface.split('gigabitethernet')[1]
            interface= 'gi'+str(suffix)
        if prefix== "tengigabitethernet":
            #interface=interface.split('tengigabitethernet')[1]
            interface= 'te'+str(suffix)
        if prefix== "fastethernet ":
            #interface=interface.split('fastethernet')[1]
            interface= 'fa'+str(suffix)
        if prefix== "management":
            #interface=interface.split('fastethernet')[1]
            interface= 'mgmt'+str(suffix)
        else:
            pass
            #failedDB
            #self.add_failed_devices_to_db(host, f"Can not normalize interface {interface}")
        print(f"Interface is : {interface}", file=sys.stderr)
        return interface
    
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
    def addInventoryToDB(self, host, data):
        data= data.replace(np.nan, '', regex=True)
        for index in data.index:
            try:
                EDNLegacy = EDN_MAC_LEGACY()
                EDNLegacy.device_a_name = data['Device A Name'][index]
                EDNLegacy.device_a_interface= data['Device A Interface'][index]
                EDNLegacy.device_a_trunk_name = data['Device A Trunk Name'][index]
                EDNLegacy.device_a_ip = data['Device A IP'][index]
                EDNLegacy.device_b_system_name = data['Device B System Name'][index]
                EDNLegacy.device_b_interface =  data['Device B Interface'][index]
                EDNLegacy.device_b_ip =data['Device B IP'][index]
                EDNLegacy.device_b_type =  data['Device B Type'][index]
                EDNLegacy.device_b_port_desc =  data['Device B Port Description'][index]
                EDNLegacy.device_a_mac = data['Device A MAC'][index]
                EDNLegacy.device_b_mac = data['Device B MAC'][index]
                EDNLegacy.device_b_mac_vendor = self.getMacVendor(data['Device B MAC'][index])
                EDNLegacy.device_a_port_desc =  data['Device A Interface Description'][index]
                EDNLegacy.device_a_vlan = data['VLAN-ID'][index]
                EDNLegacy.device_a_vlan_name = data['VLAN-NAME'][index]
                EDNLegacy.device_a_tx = data['DEVICE_A_TX'][index]
                EDNLegacy.device_a_rx = data['DEVICE_A_RX'][index]
                EDNLegacy.creation_date = host["time"]
                EDNLegacy.modification_date = host["time"]


                self.InsertData(EDNLegacy)
                print("Successfully inserted data into DB", file=sys.stderr)           
            except Exception as e:
                #failedDB
                self.add_failed_devices_to_db(host, f"Error while inserting data into DB {e}")
                db.session.rollback()
                print(f"Error while inserting data into DB {e}", file=sys.stderr)
                #self.add_to_failed_devices(host['host'], f"Failed to insert Data to DB "+str(e))

    def getPhysicalMapping(self, hosts):
        threads =[]
        self.time= hosts[0].get("time")
        for host in hosts:
            th = threading.Thread(target=self.poll, args=(host,))
            th.start()
            threads.append(th)
            if len(threads) == self.connections_limit: 
                for t in threads:
                    t.join()
                threads =[]
        
        else:
            for t in threads: # if request is less than connections_limit then join the threads and then return data
                t.join()
      
    def poll(self, device):

        dfObj = pd.DataFrame(columns=['Device A Name', 'Device A Interface', 'Device A Trunk Name',	'Device A IP',	'Device B System Name',	'Device B Interface',	'Device B IP',	'Device B Type', 'Device B Port Description', 'Device A MAC', 'Device B MAC', 'Device A Interface Description', 'VLAN-ID', 'VLAN-NAME', 'DEVICE_A_TX', 'DEVICE_A_RX'])
        obj_in=0
        
        host = {
                "host": "",
                "user": "",
                "pwd": "",
                "hostname": ""
                }
        with open('app/cred.json') as inventory:
            cred = json.loads(inventory.read())
            
        #for index, frame in dfIp['Switch IP-Address'].iteritems():
        if device['sw_type'] == 'IOS':
            device_type = 'cisco_ios'
            
        elif device['sw_type'] == 'NX-OS':
            device_type = 'cisco_nxos'
                            
        elif device['sw_type'] == 'IOS-XE':
            device_type = 'cisco_ios'
            
        elif device['sw_type'] == 'IOS-XR':
            device_type = 'cisco_ios'

        host={
                "host": device["ip"],
                "user": cred['EDN']['user'],
                "pwd": cred['EDN']['pwd'],
                "sw_type": device_type,
                'hostname':device["hostname"],
                'time':device["time"]                
            }
            
        deviceA_name = host['hostname']
        deviceA_interface = ""
        deviceA_Trunk = ""
        deviceA_IP = host['host']
        deviceB_IP = ""
        deviceA_mac=""
        deviceB_mac=""
        deviceA_interface_description = ""
        vlan = ""
            
        login_tries = 10
        c = 0
        is_login = False
        while c < login_tries :
            
            try:
                            
                device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type=host['sw_type'], timeout=800, global_delay_factor=2)
                print(f"Success: logged in {host['host']}")
                
                is_login = True
                break
            except Exception as e:
                c +=1
        
        if is_login==False:
            #failedDB
            self.add_failed_devices_to_db(host, f"Failed to Login")
            print(f"Failed to login {host['host']}", file=sys.stderr)
            #self.add_to_failed_devices(host['host'], "failed to login to device")
            
        
        if is_login==True:
            print(f"Sucessfully logged into {host['host']}", file=sys.stderr)
            vlan_names= []
            try:
                vlan_names = device.send_command('show vlan', use_textfsm=True)
                    #print(vlans, file=sys.stderr)
                if isinstance(vlan_names,str):
                        print(f"VLAN detail not found {output} {host['host']}", file=sys.stderr)
                        raise Exception(f"Vlan detail not found "+str(output))
            except Exception as e:
                print(f"Failed to get Vlans {e}", file=sys.stderr)
                #self.add_to_failed_devices(host['host'], "Failed to get vlan detail "+str(e))

             
            if host['sw_type'] == 'cisco_nxos':
                    
                try:
                    output= device.send_command("terminal length 0")
                    if("Invalid command" in str(output)):
                        raise Exception("Failed to send Command, terminal length 0"+str(output))
                    
                except Exception as e:
                    print("Failed to send Command, terminal length "+ str(e), file=sys.stderr)
                    #self.add_to_failed_devices(host['host'], str(e))
                try:    
                    ##########get all arp
                    dfArp = pd.DataFrame(columns=['mac', 'ip'])
                    print("getting arp table", file=sys.stderr)
                    arps={}
                    try:    
                        
                        arps = device.send_command("show ip arp", use_textfsm=True)
                        if isinstance(arps, str):
                            print("Error in show ip arp", file=sys.stderr)
                            #raise Exception("Failed to send Command, show ip arp"+str(arps))
                    except Exception as e:
                        print("failed to send arp command"+ str(e), file=sys.stderr)
                        #self.add_to_failed_devices(host['host'], str(e))
                        
                    i=0
            
                    for arp in arps:
                        if type(arps) == str:
                            x= 0
                        else:
                            try:
                                if (arp['mac'] == dfArp['mac']).any():
                                    locindex = dfArp[dfArp['mac'] == arp['mac']].index.item()
                                    if arp['address'] in dfArp.loc[locindex, 'ip']:
                                        continue
                                    else:
                                        dfArp.loc[locindex, 'ip'] = dfArp.loc[locindex, 'ip']+','+arp['address']
                                        
                                else:
                                    dfArp.loc[i, 'ip'] = arp['address']
                                    dfArp.loc[i, 'mac'] = arp['mac']
                                    i+=1
                            except Exception as e:
                                print("error in getting arp "+arp, file=sys.stderr)
                                #self.add_to_failed_devices(host['host'], str(e)+" "+str(arp))
                            
                    print("getting mac address-table", file=sys.stderr)
                    macs={}
                    try:
                        macs = device.send_command("show mac address-table dynamic", use_textfsm=True)
                        if isinstance(macs, str):
                            raise Exception("Failed to send Command, show mac address-table dynamic "+str(macs))
                    except Exception as e:
                        print("failed to send command mac address table dynamic"+ str(e), file=sys.stderr)
                        #self.add_to_failed_devices(host['host'], str(e))
                    dfInterface = pd.DataFrame(columns=['Interface Name', 'Mac', 'Desc', 'Members'])
                    trunk_index=0
                    for mac in macs:
                        if type(mac) == str:
                            continue
                        deviceB_mac = mac['mac']
                        vlan = mac['vlan']
                        vlan_name= list(filter(lambda vl: vl['vlan_id']== vlan, vlan_names))
                        if len(vlan_name)>0:
                            vlan_name= vlan_name[0].get('name') 
                        else:
                            vlan_name=""
                        deviceB_IP=""
                        if (deviceB_mac == dfArp['mac']).any():
                                locindex = dfArp[dfArp['mac']== deviceB_mac].index.item()
                                deviceB_IP = dfArp.loc[locindex,'ip']
                        #else:
                        #    print("get IP from firewall")
                                        
                        if 'Po' in mac['ports']:
                            deviceA_Trunk = mac['ports']
                            if (deviceA_Trunk == dfInterface['Interface Name']).any():
                                locindex = dfInterface[dfInterface['Interface Name'] == deviceA_Trunk].index.item()
                                deviceA_mac = dfInterface.loc[locindex,'Mac']
                                deviceA_interface_description = dfInterface.loc[locindex, 'Desc']
                                deviceA_interface = dfInterface.loc[locindex, 'Members']
                            else:
                                interface={}
                                try:
                                    print(f"Getting interface {deviceA_Trunk}", file=sys.stderr)
                                    interface = device.send_command(f"show interface {deviceA_Trunk}", textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_nxos_show_interface.textfsm', use_textfsm=True)
                                    
                                    if isinstance(interface, str):
                                        raise Exception(f"Failed to send Command, show interface {deviceA_Trunk}"+str(interface))
                                    #print(deviceA_Trunk)
                                except Exception as e:
                                    print("Failed to send command show interface"+ str(e), file=sys.stderr)
                                    #self.add_to_failed_devices(host['host'], "Failed to send command show interface"+ str(e))
                                #print(interface)
                                if 'Invalid ' in interface:
                                    continue
                                else:
                                    deviceA_mac = interface[0]['address']
                                    deviceA_interface_description = interface[0]['description']
                                    deviceA_interface = interface[0]['member_interface']
                                    
                                    dfInterface.loc[trunk_index, 'Interface Name'] = deviceA_Trunk
                                    dfInterface.loc[trunk_index, 'Mac'] = interface[0]['address']
                                    dfInterface.loc[trunk_index, 'Desc'] = interface[0]['description']
                                    dfInterface.loc[trunk_index, 'Members'] = interface[0]['member_interface']
                                    trunk_index+=1
                                
                            if 'infra-link' in deviceA_interface_description.lower() or 'tunnel' in deviceA_interface.lower():
                                continue
                            else:
                                splitInter = deviceA_interface.split(' ')
                                
                                for split in splitInter:
                                    split= split.replace(",", "")
                                    if split == "":
                                        continue
                                    else:
                                        dfObj.loc[obj_in,'Device A Name'] = deviceA_name
                                        dfObj.loc[obj_in,'Device A Interface'] = self.normalizeInterface(host, split.lower())
                                        dfObj.loc[obj_in,'Device A Trunk Name'] = deviceA_Trunk
                                        dfObj.loc[obj_in,'Device A IP'] = deviceA_IP
                                        dfObj.loc[obj_in,'Device A MAC'] = deviceA_mac
                                        dfObj.loc[obj_in,'Device B MAC'] = deviceB_mac
                                        dfObj.loc[obj_in,'Device B IP'] = deviceB_IP
                                        dfObj.loc[obj_in,'Device A Interface Description'] = deviceA_interface_description
                                        dfObj.loc[obj_in,'VLAN-ID'] = vlan
                                        dfObj.loc[obj_in,'VLAN-NAME'] = vlan_name
                                        obj_in+=1
                        else:
                            deviceA_interface = mac['ports']
                            
                            if (deviceA_interface == dfInterface['Interface Name']).any():
                                locindex = dfInterface[dfInterface['Interface Name'] == deviceA_interface].index.item()
                                deviceA_mac = dfInterface.loc[locindex,'Mac']
                                deviceA_interface_description = dfInterface.loc[locindex,'Desc']
                            
                            elif ("vpc" in deviceA_interface.lower()):
                                continue
                            else:
                                interface={}
                                try:
                                    print(f"Getting interface {deviceA_interface}", file=sys.stderr)
                                    interface = device.send_command(f"show interface {deviceA_interface}", use_textfsm=True)
                                    
                                    if isinstance(interface, str):
                                        raise Exception(f"Failed to send Command, show interface {deviceA_Trunk}"+str(interface))
                                except Exception as e:
                                    print("failed to send command"+ str(e), file=sys.stderr)
                                #print(deviceA_interface)
                                #print(interface)
                                if 'Invalid interface format' in interface:
                                    continue
                                deviceA_mac = interface[0]['address']
                                deviceA_interface_description = interface[0]['description']
                                
                                dfInterface.loc[trunk_index,'Interface Name'] = deviceA_interface
                                dfInterface.loc[trunk_index,'Mac'] = interface[0]['address']
                                dfInterface.loc[trunk_index,'Desc'] = interface[0]['description']
                                trunk_index+=1
                                
                            if 'infra-link' in deviceA_interface_description.lower() or 'tunnel' in deviceA_interface:
                                continue
                            else:
                                try:
                                    dfObj.loc[obj_in,'Device A Name'] = deviceA_name
                                    dfObj.loc[obj_in,'Device A Interface'] = self.normalizeInterface(host, deviceA_interface.lower())
                                    #dfObj.loc[obj_in,'Device A Trunk Name'] = deviceA_Trunk
                                    dfObj.loc[obj_in,'Device A IP'] = deviceA_IP
                                    dfObj.loc[obj_in,'Device A MAC'] = deviceA_mac
                                    dfObj.loc[obj_in,'Device B MAC'] = deviceB_mac
                                    dfObj.loc[obj_in,'Device B IP'] = deviceB_IP
                                    dfObj.loc[obj_in,'Device A Interface Description'] = deviceA_interface_description
                                    dfObj.loc[obj_in,'VLAN-ID'] = vlan
                                    dfObj.loc[obj_in,'VLAN-NAME'] = vlan_name
                                    obj_in+=1
                                except Exception as e:
                                    print("error writing df")
                                    print(e, file=sys.stderr)
                                    #self.add_to_failed_devices(host['host'], "error writing df"+ str(e))
                    #adding extra interfaces            
                    
                    try:
                        print("Getting all interfacs", file=sys.stderr)
                        interfaces = device.send_command("show interface", use_textfsm=True)
                        if isinstance(interfaces, str):
                            raise Exception("Failed to send Command, show interface"+str(interfaces))
                        
                        for interface in interfaces: 
                            interface['interface']= self.normalizeInterface(host, interface['interface'].lower())
                            if interface['address'] and interface['address'] not in dfObj['Device A MAC'].values  and interface['interface'] not in dfObj['Device A Interface'].values and "vlan" not in interface['interface'].lower() and "loopback" not in interface['interface'].lower() and "tunnel" not in interface['interface'].lower() and "up" in interface["link_status"].lower() and "(out-of-service)" not in interface["link_status"].lower() and interface.get("mode") !="trunk" and "port" not in interface['interface'].lower():

                                dfObj.loc[obj_in,'Device A Name'] = deviceA_name
                                dfObj.loc[obj_in,'Device A Interface'] =interface['interface'].lower()
                                dfObj.loc[obj_in,'Device A IP'] = deviceA_IP
                                dfObj.loc[obj_in,'Device A MAC'] = interface['address']
                                dfObj.loc[obj_in,'Device A Interface Description']= interface["description"]
                                if "infra" in interface["description"].lower():
                                    if "infra-link" in interface["description"].lower():
                                        dfObj.loc[obj_in,'Device B MAC']= "Infra Link"
                                    elif "infra-fw" in interface["description"].lower():
                                        dfObj.loc[obj_in,'Device B MAC']= "Infra Firewall"
                                    else:
                                        dfObj.loc[obj_in,'Device B MAC']= "Infra"
                                else:
                                    dfObj.loc[obj_in,'Device B MAC']= "No Mac"
                                obj_in+=1  
                        
                    except Exception as e:
                        print("failed to send command"+str(e), file=sys.stderr)
                        #self.add_to_failed_devices(host['host'], "Failed to get all interfaces"+ str(e))       

                    try:
                        print(f"Getting all interface Bandwidth", file=sys.stderr)
                        speed = device.send_command("show interface", textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_nxos_show_interface.textfsm', use_textfsm=True)
                        if isinstance(interfaces, str):
                            raise Exception("Failed to send Command, show interface "+str(interfaces))
                        
                        for interface in speed: 
                            interface['interface']= self.normalizeInterface(host, interface['interface'].lower())
                        
                        #Append Bandwidth
                        dfObj= dfObj.replace(np.nan, '', regex=True)
                        for index in dfObj.index:
                            try:
                                
                                interface= list(filter(lambda intf: intf['interface']== dfObj['Device A Interface'][index], speed))
                                if len(interface) >0:
                                    dfObj['DEVICE_A_TX'][index]= interface[0]['input_rate']
                                    dfObj['DEVICE_A_RX'][index]= interface[0]['output_rate']

                            except Exception as e:
                                traceback.print_exc()
                                print("Failed to parse Interface Bandwidth", file=sys.stderr)
                                        
                    except Exception as e:
                        print("failed to get Interface Bandwidth "+str(e), file=sys.stderr)
                        #self.add_to_failed_devices(host['host'], "Failed to get all interfaces"+ str(e))       
                    
                    
                except Exception as e:
                    #failedDB
                    self.add_failed_devices_to_db(host, f"Error When gettinf EDN MAC data {e}")
                    print(f"Failed to get physical mapping detail for device {host['host']} {str(e)}", file=sys.stderr)
                    #self.add_to_failed_devices(host['host'], "Failed to get all interfaces"+ str(e)) 
            
            elif host['sw_type'] == 'cisco_ios':
                try:
                    output= device.send_command("terminal length 0")
                    if("Invalid command" in str(output)):
                        raise Exception("Failed to send Command, terminal length 0"+str(output))
                    
                except Exception as e:
                    print("Failed to send Command, terminal length 0"+ str(e), file=sys.stderr)
                    #self.add_to_failed_devices(host['host'], str(e))
                try:
                    ##########get all arp
                    dfArp = pd.DataFrame(columns=['mac', 'ip'])
                    print("getting arp table", file=sys.stderr)
                    arps={}    
                    try:
                        arps = device.send_command("show ip arp", use_textfsm=True)
                        if isinstance(arps, str):
                            print("Error in show ip arp", file=sys.stderr)
                            #raise Exception("Failed to send Command, show ip arp"+str(arps))
                        
                    except Exception as e:
                        print("Failed to send Command, show ip arp "+ str(e), file=sys.stderr)
                        #self.add_to_failed_devices(host['host'], str(e))
                    i=0
            
                    for arp in arps:
                        try:
                            if (arp['mac'] == dfArp['mac']).any():
                                locindex = dfArp[dfArp['mac'] == arp['mac']].index.item()
                                if arp['address'] in dfArp.loc[locindex, 'ip']:
                                    continue
                                else:
                                    dfArp.loc[locindex, 'ip'] = dfArp.loc[locindex, 'ip']+','+arp['address']
                                    
                            else:
                                dfArp.loc[i, 'ip'] = arp['address']
                                dfArp.loc[i, 'mac'] = arp['mac']
                                i+=1
                        except Exception as e:
                            print("error in getting arp "+arp, file=sys.stderr)
                            #self.add_to_failed_devices(host['host'], "error in getting arp "+str(arp))
                            
                    print("getting mac address-table", file=sys.stderr)
                    macs={}
                    try:
                        macs = device.send_command("show mac address-table dynamic", textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_ios_show_mac-address-table.textfsm', use_textfsm=True)
                        if isinstance(macs, str):
                            raise Exception("Failed to send Command, show mac address-table dynamic "+str(macs))
                        
                    except Exception as e:
                        print("Failed to send Command,  show mac address-table dynamic"+ str(e), file=sys.stderr)
                        #self.add_to_failed_devices(host['host'], str(e))
            
                    dfInterface = pd.DataFrame(columns=['Interface Name', 'Mac', 'Desc', 'Members'])
                    trunk_index=0
                
                    for mac in macs:
                        if type(mac) == str:
                            continue
                        deviceB_mac = mac['destination_address']
                        
                        vlan = mac['vlan']
                        vlan_name= list(filter(lambda vl: vl['vlan_id']== vlan, vlan_names))
                        if len(vlan_name)>0:
                            vlan_name= vlan_name[0].get('name') 
                        else:
                            vlan_name=""

                        deviceB_IP=""
                        if (deviceB_mac == dfArp['mac']).any():
                                locindex = dfArp[dfArp['mac']== deviceB_mac].index.item()
                                deviceB_IP = dfArp.loc[locindex,'ip']
                        #else:
                        #   print("get IP from firewall")
                                        
                        if 'Po' in mac['destination_port']:
                            deviceA_Trunk = mac['destination_port']
                            if (deviceA_Trunk == dfInterface['Interface Name']).any():
                                locindex = dfInterface[dfInterface['Interface Name'] == deviceA_Trunk].index.item()
                                deviceA_mac = dfInterface.loc[locindex,'Mac']
                                deviceA_interface_description = dfInterface.loc[locindex, 'Desc']
                                deviceA_interface = dfInterface.loc[locindex, 'Members']
                            else:
                                interface={}
                                try:
                                    print(f"Getting interface {deviceA_Trunk}", file=sys.stderr)
                                    interface = device.send_command(f"show interface {deviceA_Trunk}", textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_nxos_show_interface.textfsm', use_textfsm=True)
                                    if isinstance(interface, str):
                                        raise Exception(f"Failed to send Command, show interface {deviceA_Trunk}"+str(interface))
                                except Exception as e:
                                    print("Failed to send command show interface"+ str(e), file=sys.stderr)
                                    #self.add_to_failed_devices(host['host'], "Failed to send command show interface"+ str(e))
                                #print(deviceA_Trunk)
                                #print(interface)
                                if 'Invalid interface format' in interface:
                                    continue
                                deviceA_mac = interface[0]['address']
                                deviceA_interface_description = interface[0]['description']
                                deviceA_interface = interface[0]['member_interface']
                                
                                dfInterface.loc[trunk_index, 'Interface Name'] = deviceA_Trunk
                                dfInterface.loc[trunk_index, 'Mac'] = interface[0]['address']
                                dfInterface.loc[trunk_index, 'Desc'] = interface[0]['description']
                                dfInterface.loc[trunk_index, 'Members'] = interface[0]['member_interface']
                                trunk_index+=1
                                
                            if 'infra-link' in deviceA_interface_description.lower() or 'tunnel' in deviceA_interface:
                                continue
                            else:
                                
                                splitInter = deviceA_interface.split(' ')
                                

                                for split in splitInter:
                                    split= split.replace(",", "")

                                    if split == "":
                                        continue
                                    else:
                                        dfObj.loc[obj_in,'Device A Name'] = deviceA_name
                                        dfObj.loc[obj_in,'Device A Interface'] = self.normalizeInterface(host, split.lower())
                                        dfObj.loc[obj_in,'Device A Trunk Name'] = deviceA_Trunk
                                        dfObj.loc[obj_in,'Device A IP'] = deviceA_IP
                                        dfObj.loc[obj_in,'Device A MAC'] = deviceA_mac
                                        dfObj.loc[obj_in,'Device B MAC'] = deviceB_mac
                                        dfObj.loc[obj_in,'Device B IP'] = deviceB_IP
                                        dfObj.loc[obj_in,'Device A Interface Description'] = deviceA_interface_description
                                        dfObj.loc[obj_in,'VLAN-ID'] = vlan
                                        dfObj.loc[obj_in,'VLAN-NAME'] = vlan_name
                                        obj_in+=1
                        else:
                            deviceA_interface = mac['destination_port']
                            
                            if (deviceA_interface == dfInterface['Interface Name']).any():
                                locindex = dfInterface[dfInterface['Interface Name'] == deviceA_interface].index.item()
                                deviceA_mac = dfInterface.loc[locindex,'Mac']
                                deviceA_interface_description = dfInterface.loc[locindex,'Desc']
                            
                            else:
                                interface={}
                                try:
                                    print(f"Getting interface {deviceA_interface}", file=sys.stderr)
                                    interface = device.send_command(f"show interface {deviceA_interface}", use_textfsm=True)
                                    if isinstance(interface, str):
                                        raise Exception(f"Failed to send Command, show interface {deviceA_Trunk}"+str(interface))
                                except Exception as e:
                                    print("Failed to send command show interface"+ str(e), file=sys.stderr)
                                    #self.add_to_failed_devices(host['host'], "Failed to send command show interface"+ str(e))
                                if 'Invalid ' in interface:
                                    continue
                                else:
                                    deviceA_mac = interface[0]['address']
                                    deviceA_interface_description = interface[0]['description']
                                    
                                    dfInterface.loc[trunk_index,'Interface Name'] = deviceA_interface
                                    dfInterface.loc[trunk_index,'Mac'] = interface[0]['address']
                                    dfInterface.loc[trunk_index,'Desc'] = interface[0]['description']
                                    trunk_index+=1
                                
                            if 'infra-link' in deviceA_interface_description.lower() or 'tunnel' in deviceA_interface:
                                continue
                            else:
                                try:
                                    dfObj.loc[obj_in,'Device A Name'] = deviceA_name
                                    dfObj.loc[obj_in,'Device A Interface'] = self.normalizeInterface(host, deviceA_interface.lower())
                                    #dfObj.loc[obj_in,'Device A Trunk Name'] = deviceA_Trunk
                                    dfObj.loc[obj_in,'Device A IP'] = deviceA_IP
                                    dfObj.loc[obj_in,'Device A MAC'] = deviceA_mac
                                    dfObj.loc[obj_in,'Device B MAC'] = deviceB_mac
                                    dfObj.loc[obj_in,'Device B IP'] = deviceB_IP
                                    dfObj.loc[obj_in,'Device A Interface Description'] = deviceA_interface_description
                                    dfObj.loc[obj_in,'VLAN-ID'] = vlan
                                    dfObj.loc[obj_in,'VLAN-NAME'] = vlan_name
                                    obj_in+=1
                                except Exception as e:
                                    traceback.print_exc()

                                    print(f"error writing df {e}", file=sys.stderr)
                                    #self.add_to_failed_devices(host['host'], "error writing df"+str(e))
                    
                    try:
                        print(f"Getting all interfaces", file=sys.stderr)
                        interfaces = device.send_command("show interface", textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_nxos_show_interface.textfsm', use_textfsm=True)
                        if isinstance(interfaces, str):
                            raise Exception("Failed to send Command, show interface "+str(interfaces))
                        
                        for interface in interfaces: 
                            interface['interface']= self.normalizeInterface(host, interface['interface'].lower())
                            if  interface['address'] and interface['address'] not in dfObj['Device A MAC'].values and interface['interface'] not in dfObj['Device A Interface'].values and "vlan" not in interface['interface'].lower() and "loopback" not in interface['interface'].lower() and "tunnel" not in interface['interface'].lower() and "up" in interface["link_status"].lower() and "(out-of-service)" not in interface["link_status"].lower() and interface.get("mode") !="trunk" and "port" not in interface['interface'].lower():
                                dfObj.loc[obj_in,'Device A Name'] = deviceA_name
                                dfObj.loc[obj_in,'Device A Interface'] =interface['interface'].lower()
                                dfObj.loc[obj_in,'Device A IP'] = deviceA_IP
                                dfObj.loc[obj_in,'Device A MAC'] = interface['address']
                                dfObj.loc[obj_in,'Device A Interface Description']= interface["description"]
                                if "infra" in interface["description"].lower():
                                    if "infra-link" in interface["description"].lower():
                                        dfObj.loc[obj_in,'Device B MAC']= "Infra Link"
                                    elif "infra-fw" in interface["description"].lower():
                                        dfObj.loc[obj_in,'Device B MAC']= "Infra Firewall"
                                    else:
                                        dfObj.loc[obj_in,'Device B MAC']= "Infra"
                                else:
                                    dfObj.loc[obj_in,'Device B MAC']= "No Mac"
                                obj_in+=1
                        
                    except Exception as e:
                        print("failed to send command "+str(e), file=sys.stderr)
                        #self.add_to_failed_devices(host['host'], "Failed to get all interfaces"+ str(e))       
                    
                    try:
                        print(f"Getting all interface Bandwidth", file=sys.stderr)
                        speed = device.send_command("show interface", use_textfsm=True)
                        if isinstance(interfaces, str):
                            raise Exception("Failed to send Command, show interface "+str(interfaces))
                        
                        for interface in speed: 
                            interface['interface']= self.normalizeInterface(host, interface['interface'].lower())
                        
                        #Append Bandwidth
                        dfObj= dfObj.replace(np.nan, '', regex=True)
                        for index in dfObj.index:
                            try:
                                
                                interface= list(filter(lambda intf: intf['interface']== dfObj['Device A Interface'][index], speed))
                                if len(interface) >0:
                                    dfObj['DEVICE_A_TX'][index]= interface[0]['input_rate']
                                    dfObj['DEVICE_A_RX'][index]= interface[0]['output_rate']

                            except Exception as e:
                                traceback.print_exc()
                                print("Failed to parse Interface Bandwidth", file=sys.stderr)
                                        
                    except Exception as e:
                        print("failed to get Interface Bandwidth "+str(e), file=sys.stderr)
                        #self.add_to_failed_devices(host['host'], "Failed to get all interfaces"+ str(e))       
                    
                except Exception as e:
                    traceback.print_exc()
                    #failedDB
                    self.add_failed_devices_to_db(host, f"Error When get tinf EDN MAC data {e}")
                    print(f"Failed to get physical mapping detail for device {host['host']} {str(e)}", file=sys.stderr)
                    #self.add_to_failed_devices(host['host'], "Failed to get all interfaces"+ str(e)) 

        self.addInventoryToDB(host, dfObj)
        
