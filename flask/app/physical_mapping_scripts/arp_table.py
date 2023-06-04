# -*- coding: utf-8 -*-
"""
Created on Sun Dec 26 15:28:55 2021

@author: HP
"""

import datetime
from logging import exception
import time
import traceback
from netmiko import Netmiko
import re, sys, json
import numpy as np
import pandas as pd
from pandas import read_excel
from app import db
from app.models.phy_mapping_models import EDN_FIREWALL_ARP
from app.physical_mapping_scripts.addFWIP import AddFwIP
from app.models.inventory_models import FAILED_DEVICES_EDN_FIREWALL
import threading

class Arp():
    def __init__(self):
        self.connections_limit = 50
        self.failed_devices=[]
        self.time= None
        self.host_arps={}
    
    def add_failed_devices_to_db(self, host, reason):
        pmFailedDb = FAILED_DEVICES_EDN_FIREWALL()
        
        try:
            pmFailedDb.ip_address = host['host']
            pmFailedDb.device_id = host['hostname']
            pmFailedDb.reason =reason
            pmFailedDb.date = host['time']
            
            self.InsertData(pmFailedDb)

            print('Successfully added Failed device to the Database', file = sys.stderr)
            
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
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
    #     file_name = time.strftime("%d-%m-%Y")+"-ARP.txt"
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

    def FormatStringDate(self, date):
        try:

            if date is not None:
                date = str(date)
                result = datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
                return result
           
        except:
            
            result=datetime(2000, 1,1)
            print("date format exception", file=sys.stderr)
            return result

    def getDatacenter(self, firewall_id):
        dataCenter=""
        dataCenter= firewall_id.split('-')[0]
        '''
        prefix= (re.findall(r'^(\d+.\d+)',ip))[0]
        if prefix == "10.64":
            dataCenter= "RYD-MLG-ENT"
        elif prefix == "10.73":
            dataCenter= "RYD-MLGII-ENT"
        elif prefix == "10.14":
            dataCenter= "RYD-SLY-ISR"
        elif prefix == "10.67":
            dataCenter= "RYD-MLZ-ENT"
        elif prefix == "10.66":
            dataCenter= "RYD-SLM-ENT"
        elif prefix == "10.6":
            dataCenter= "RYD-DAN-ENT"
        elif prefix == "10.32":
            dataCenter= "DAM-ALR-ENT"
        elif prefix == "10.42":
            dataCenter= "DAM-ADM-ENT"
        elif prefix == "10.41":
            dataCenter= "DAM-RAK-ENT"
        elif prefix == "10.81":
            dataCenter= "JED-SAF-ENT"
        elif prefix == "10.22":
            dataCenter= "JED-UBH-ENT"
        elif prefix == "10.82":
            dataCenter= "WES-MDN-ENT"
        elif prefix == "10.83":
            dataCenter= "JED-BSLM-ENT"
        elif prefix == "10.20":
            dataCenter= "JED-LS-ENT"
        elif prefix == "10.87":
            dataCenter= "MAK-SWQ-ENT"
        elif prefix == "10.68":
            dataCenter= "QAS-UNZ-ENT"
        elif prefix == "10.9":
            dataCenter= "RYD-BUR-ENT"
        elif prefix == "10.78":
            dataCenter= "JED-OB2-ENT"
        elif prefix == "10.8":
            dataCenter= "RYD-KHJ-ENT"
        elif prefix == "10.85":
            dataCenter= "MAK-MTB-ENT"
        elif prefix == "10.76":
            dataCenter= "DAM-AHS-ENT"
        else:
            dataCenter="" 
        '''
        return dataCenter 

    def InsertData(self, obj):
        try:
            #add data to db
            db.session.add(obj)
            db.session.commit()
            return True
        except Exception as e:
            host= {}
            host['hostname']=obj.firewall_id
            host['host']=obj.ip 
            host['time']=  obj.creation_date
            self.add_failed_devices_to_db(self, host, f"Failed to Insert Data into DB {e}")

    def addInventoryToDB(self, data):
        temp_data=[]

        for host, records in data.items():
            try:
                for record in records:
                    datacenter= self.getDatacenter(record["firewall_id"])
                    record_exists=list(filter(lambda mac: mac['mac'] == record['mac'], temp_data))
                    if record_exists:
                        record_index = next((i for i, x in enumerate(record_exists) if x["datacenter"] == datacenter), None)
                        if  record_index is not None:
                            index= next((i for i, item in enumerate(temp_data) if item["mac"] == record["mac"] and item['datacenter']==datacenter), False)
                            existinips= record_exists[record_index].get("ip")
                            existing_firewall_ids= record_exists[record_index].get("firewall_id")
                            existing_arp_type= record_exists[record_index].get("source_type")
                            #existing_arp_tpe_ids= record_exists[record_index].get("firewall_id")
                            fw_ind  = [index for (index, item) in enumerate(existing_firewall_ids.split(',')) if item == record["firewall_id"]]
                            ips_ind  = [index for (index, item) in enumerate(existinips.split(',')) if item == record["ip"]]
                            matched_indexes= [i for i, (fw, ip) in enumerate(zip(fw_ind, ips_ind)) if fw==ip]
                            matched_indexes= False
                            for fw in fw_ind:
                                if any(fw in ips_ind for fw in ips_ind):
                                    matched_indexes=True
                                    break
                            if not matched_indexes:       
                                temp_data[index]= {"firewall_id": existing_firewall_ids+","+record["firewall_id"], "source_type": existing_arp_type+","+record["source_type"],  "mac": record["mac"] , "ip": existinips+","+record["ip"], "datacenter": datacenter , "host":record["host"]}
                            
                        else:
                            temp_data.append({"firewall_id": record["firewall_id"], "mac": record["mac"] ,  "source_type": record["source_type"], "mac": record["mac"] , "ip": record["ip"], "datacenter": datacenter, "host":record["host"]})
                        
                    else:
                        temp_data.append({"firewall_id": record["firewall_id"], "source_type": record["source_type"], "mac": record["mac"] , "ip": record["ip"], "datacenter": datacenter, "host":record["host"]})
                        
            except Exception as e:
                #failedDB
                self.add_failed_devices_to_db(host, f"Error while Parsing Data in Database Insertion {e}")
                print(f"Error while Parsing data {host} {e}", file =sys.stderr)
                #self.add_to_failed_devices(host['host'], "Exception occured when adding data to inventory "+str(e))  
                traceback.print_exc()

        for record in temp_data:
            try:
                fwARP = EDN_FIREWALL_ARP()
                fwARP.firewall_id=record["firewall_id"]
                fwARP.mac = record["mac"]
                fwARP.ip = record["ip"]
                fwARP.dc = record["datacenter"]
                fwARP.arp_source_type = record["source_type"]
                #fwARP.arp_source_type = record["datacenter"]
                fwARP.creation_date = self.time
                fwARP.modification_date = self.time
                self.InsertData(fwARP)
                print(f"Successfully inserted data into DB", file=sys.stderr)           
            except Exception as e:
                #failedDB
                self.add_failed_devices_to_db(record["host"], f"Error while inserting data into DB {e}")
                db.session.rollback()
                print(f"Error while inserting data to DB {e}", file =sys.stderr)
                
    def getPhysicalMapping(self, hosts):
        try:
            
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
            
            self.addInventoryToDB(self.host_arps)
            
            print("ARP Firewall Completed", file=sys.stderr)
            #self.print_failed_devices()
        except Exception as e:
            print(f"Failed to execute script arp table {e}", file=sys.stderr)
            #self.add_to_failed_devices(host['host'], "EError occureding while reading firewall arp "+str(e))  
            #self.print_failed_devices()
        #print("Populating Firewall IP's in IGW LLDP ACI", file=sys.stderr)
        #fwIp.addFWIPToIgwLldpAci(self.time)
     
        

    def poll(self, device): 
        try:
        
            with open('app/cred.json') as inventory:
                inv = json.loads(inventory.read())
        
            if device["sw_type"] == 'IOS':
                device_type = 'cisco_ios'
                username= inv['EDN']['user']
                password= inv['EDN']['pwd']
                
            elif device["sw_type"] == 'NX-OS':
                device_type = 'cisco_nxos'
                username= inv['EDN']['user']
                password= inv['EDN']['pwd']
                
            elif device["sw_type"] == 'FOS':
                device_type = 'fortinet'
                username= inv['SEC']['user']
                password= inv['SEC']['pwd']
                
            elif device["sw_type"] == 'Junos':
                device_type = 'juniper_junos'
                username= inv['SEC']['user']
                password= inv['SEC']['pwd']
                
            elif device["sw_type"] == 'ASA':
                device_type = 'cisco_asa'
                username= inv['SEC']['user']
                password= inv['SEC']['pwd']
            
            elif device["sw_type"] == 'F5':
                device_type = 'f5_tmsh'
                username= inv['SYSTEMS']['user']
                password= inv['SYSTEMS']['pwd']
            
            host={
                "host": device["ip"],
                "user": username,
                "pwd": password,
                "type": device_type,
                'hostname':device["hostname"],
                'time': device["time"], #self.FormatStringDate(device["time"])   
            }
        
            login_tries = 3
            c = 0
            is_login = False
            
            
            while c < login_tries :
                try:
                                
                    device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type=host['type'], timeout=800, global_delay_factor=2)
                    print(f"Success: logged in to host{host['host']} ", file=sys.stderr)
            
                    is_login = True
                    break
                except Exception as e:
                    c +=1
            
            if is_login==False:
                #failedDB
                self.add_failed_devices_to_db(host, f"Failed to Login")
                #self.add_to_failed_devices(host['host'], "failed to login to device")
                print(f"Faied to login {host['host']}", file=sys.stderr)
                
            
            if is_login==True:
                
                
                if host['type'] == 'juniper_junos':
                    print(f"getting arp table of {host['host']}", file=sys.stderr)
                    try:
                        arps = device.send_command("show arp no-resolve", use_textfsm=True)
                        if isinstance(arps, str):
                            print("Error in show arp no-resolve", file=sys.stderr)
                            
                            raise Exception("Failed to send Command, show arp no-resolve"+str(arps))
                        
                        device_arp=[]
                        for arp in arps:
                            arp_data={}
                            try:
                                mac_str =  ""
                                mac_str = arp['mac']
                                mac_str = mac_str.replace(".", "")
                                mac_str = mac_str.replace(":", "")

                                arp_data['firewall_id'] = host['hostname']
                                arp_data['ip'] = arp['ip_address']
                                arp_data['mac'] = mac_str
                                arp_data['host'] = host
                                arp_data['source_type'] = "Juniper"
                                device_arp.append(arp_data)
                            except Exception as e:
                                print(f"Exception occured when reading arp {e}", file=sys.stderr)
                                #self.add_to_failed_devices(host['host'], "Exception occured when reading arp "+str(e))  
                        
                        self.host_arps[host['host']]= device_arp
                    except Exception as e:
                        self.add_failed_devices_to_db(host, f"Failed to send Command, show arp no-resolve {str(arps)}")
                        print("Failed to send Command, show arp no-resolve "+ str(e), file=sys.stderr)
                        #self.add_to_failed_devices(host['host'], str(e))

                if host['type'] == 'fortinet':
                    
                    print(f"getting arp table of {host['host']}", file=sys.stderr)
                    config = device.send_config_set(["config vdom",
                                                "edit root"])

                    try:
                        arps = device.send_command("get system arp", use_textfsm=True)
                        
                        if isinstance(arps, str):
                            print("Error in get system arp", file=sys.stderr)
                            
                            raise Exception("Failed to send Command, get system arp"+str(arps))
                        
                        device_arp=[]
                        for arp in arps:
                            arp_data={}
                            try:
                                mac_str =  ""
                                mac_str = arp['mac']
                                mac_str = mac_str.replace(".", "")
                                mac_str = mac_str.replace(":", "")
                                
                                arp_data['firewall_id'] = host['hostname']
                                arp_data['ip'] = arp['address']
                                arp_data['mac'] = mac_str
                                arp_data['host'] = host
                                arp_data['source_type'] = "Fortinet"
                                device_arp.append(arp_data)
                            except Exception as e:
                                print(f"Exception occured when reading arp {e}", file=sys.stderr)
                                #self.add_to_failed_devices(host['host'], "Exception occured when reading arp "+str(e))  
                        
                        self.host_arps[host['host']]= device_arp                    
                    except Exception as e:
                        self.add_failed_devices_to_db(host, f"Failed to send Command, get system arp {str(arps)}")
                        print("Failed to send Command, get system arp "+ str(e), file=sys.stderr)
                        #self.add_to_failed_devices(host['host'], str(e))
                
                if host['type'] == 'cisco_asa':
                    print(f"getting arp table of {host['host']}", file=sys.stderr)
                    try:
                        arps = device.send_command("show arp", use_textfsm=True)
                        if isinstance(arps, str):
                            print("Error in show arp", file=sys.stderr)
                            
                            raise Exception("Failed to send Command, show arp"+str(arps))
                        #print(arps)
                        device_arp=[]
                        for arp in arps:
                            arp_data={}
                            try:
                                mac_str =  ""
                                mac_str = arp['mac']
                                mac_str = mac_str.replace(".", "")
                                mac_str = mac_str.replace(":", "")
                                
                                arp_data['firewall_id'] = host['hostname']
                                arp_data['ip'] = arp['address']
                                arp_data['mac'] = mac_str
                                arp_data['host'] = host
                                arp_data['source_type'] = "Cisco ASA"
                                device_arp.append(arp_data)
                            except Exception as e:
                                
                                print(f"Exception occured when reading arp {e}", file=sys.stderr)
                                #self.add_to_failed_devices(host['host'], "Exception occured when reading arp "+str(e))  
                        
                        self.host_arps[host['host']]= device_arp

                    except Exception as e:
                        self.add_failed_devices_to_db(host, f"Failed to send Command, show arp {str(arps)}")
                        print("Failed to send Command, show arp "+ str(e), file=sys.stderr)
                        #self.add_to_failed_devices(host['host'], str(e))        
            
                
                if host['type'] == 'cisco_ios':
                    #pass
                    
                    print(f"getting arp table of {host['host']}", file=sys.stderr)
                    try:
                        len = device.send_command("terminal length 0")
                        device.send_command(len, use_textfsm=True)
                    except Exception as e:
                        print("Failed to send Command, terminal length 0"+ str(e))
                    try:
                        arps = device.send_command("show ip arp", use_textfsm=True)
                        if isinstance(arps, str):
                            print("Error in show ip arp", file=sys.stderr)
                            
                            raise Exception("Failed to send Command, show ip arp"+str(arps))
                        #print(arps)
                        device_arp=[]
                        for arp in arps:
                            arp_data={}
                            try:
                                mac_str =  ""
                                mac_str = arp['mac']
                                mac_str = mac_str.replace(".", "")
                                mac_str = mac_str.replace(":", "")
                               
                                arp_data['firewall_id'] = host['hostname']
                                arp_data['ip'] = arp['address']
                                arp_data['mac'] = mac_str
                                arp_data['host'] = host
                                arp_data['source_type'] = "Cisco IOS"
                                device_arp.append(arp_data)
                            except Exception as e:
                                self.add_failed_devices_to_db(host, f"Failed to send Command, show ip arp  {str(arps)}")
                                print(f"Exception occured when reading arp {e}", file=sys.stderr)
                                #self.add_to_failed_devices(host['host'], "Exception occured when reading arp "+str(e))  
                        
                        self.host_arps[host['host']]= device_arp
                    except Exception as e:
                        self.add_failed_devices_to_db(host, f"Failed to send Command, show ip arp  {str(arps)}")
                        print("Failed to send Command, show ip arp "+ str(e), file=sys.stderr)
                        #self.add_to_failed_devices(host['host'], str(e))    

                if host['type'] == 'cisco_nxos':
                    #pass
                    
                    print(f"getting arp table of {host['host']}", file=sys.stderr)
                    try:
                        len = device.send_command("terminal length 0")
                        device.send_command(len, use_textfsm=True)
                    except Exception as e:
                        print("Failed to send Command, terminal length 0"+ str(e))
                    try:
                        arps = device.send_command("show ip arp", use_textfsm=True)
                        if isinstance(arps, str):
                            print("Error in show ip arp", file=sys.stderr)
                            
                            raise Exception("Failed to send Command, show ip arp"+str(arps))
                        #print(arps)
                        device_arp=[]
                        for arp in arps:
                            arp_data={}
                            try:
                                mac_str =  ""
                                mac_str = arp['mac']
                                mac_str = mac_str.replace(".", "")
                                mac_str = mac_str.replace(":", "")
                               
                                arp_data['firewall_id'] = host['hostname']
                                arp_data['ip'] = arp['address']
                                arp_data['mac'] = mac_str
                                arp_data['host'] = host
                                arp_data['source_type'] = "Cisco NXOS"
                                device_arp.append(arp_data)
                            except Exception as e:
                                self.add_failed_devices_to_db(host, f"Failed to send Command, show ip arp  {str(arps)}")
                                print(f"Exception occured when reading arp {e}", file=sys.stderr)
                                #self.add_to_failed_devices(host['host'], "Exception occured when reading arp "+str(e))  
                        
                        self.host_arps[host['host']]= device_arp
                    except Exception as e:
                        self.add_failed_devices_to_db(host, f"Failed to send Command, show ip arp  {str(arps)}")
                        print("Failed to send Command, show ip arp "+ str(e), file=sys.stderr)
                        #self.add_to_failed_devices(host['host'], str(e))    

                if host['type'] == 'f5_tmsh':
                    #pass
                    
                    print(f"getting arp table of {host['host']}", file=sys.stderr)
                    try:
                        arps = device.send_command("show net arp", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/f5_ltm_show_net_arp.textfsm", use_textfsm=True)
                        if isinstance(arps, str):
                            print("Error in show net arp", file=sys.stderr)
                            
                            raise Exception("Failed to send Command, show net arp"+str(arps))
                        #print(arps)
                        device_arp=[]
                        for arp in arps:
                            arp_data={}
                            try:
                                mac_str =  ""
                                mac_str = arp['mac']
                                mac_str = mac_str.replace(".", "")
                                mac_str = mac_str.replace(":", "")
                               
                                arp_data['firewall_id'] = host['hostname']
                                arp_data['ip'] = arp['address']
                                arp_data['mac'] = mac_str
                                arp_data['host'] = host
                                arp_data['source_type'] = "F5"
                                device_arp.append(arp_data)
                            except Exception as e:
                                self.add_failed_devices_to_db(host, f"Failed to send Command, show net arp  {str(arps)}")
                                print(f"Exception occured when reading arp {e}", file=sys.stderr)
                                #self.add_to_failed_devices(host['host'], "Exception occured when reading arp "+str(e))  
                        
                        self.host_arps[host['host']]= device_arp
                    except Exception as e:
                        self.add_failed_devices_to_db(host, f"Failed to send Command, show net arp  {str(arps)}")
                        print("Failed to send Command, show net arp "+ str(e), file=sys.stderr)
                        #self.add_to_failed_devices(host['host'], str(e))    
                    
        except Exception as e:
            #failedDB
            self.add_failed_devices_to_db(host, f"Error while getting Firewall Data {e}")
            print(f"Failed to get Information from device {device['ip']}", file=sys.stderr)
            #self.add_to_failed_devices(device['ip'], str(e))

    
        
    