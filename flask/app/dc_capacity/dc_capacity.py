import traceback
from typing import Set
from netmiko import Netmiko
from app import db
from datetime import datetime
import re, sys, time, json 
import threading
from collections import Counter
from app.models.inventory_models import EDN_DC_CAPACITY, IGW_DC_CAPACITY, FAILED_DEVICES_EDN_DC_CAPACITY, FAILED_DEVICES_IGW_DC_CAPACITY
from textfsm import clitable

class DCCAPACITY(object):
    def __init__(self):
        self.connections_limit = 50
        self.failed_devices=[]
        self.spfs= ['sx', 'lx', 'lh', 'ex', 'zx', 'glc', 'bx10', 't-x', 'lr', 'er', 'zr', 'cu', 'aoc', 'sl', 'sfp', 'qsfp', 'sr', 'cwdm', 'cpak', 'fr', 'psm', 'gls', 'cfp', 'xfp', 'ftl', 'mpa']

    
    def add_to_failed_devices(self, host, reason):
        failed_device= {}
        failed_device["ip_address"]= host
        failed_device["date"]= time.strftime("%d-%m-%Y")
        failed_device["time"]= time.strftime("%H-%M-%S")
        failed_device["reason"]= reason
        self.failed_devices.append(failed_device)
           
    def print_failed_devices(self,):
        print("Printing Failed Devices")
        file_name = time.strftime("%d-%m-%Y")+"-DC Capacity.txt"
        failed_device=[]
        #Read existing file
        try:
            with open('app/failed/ims/'+file_name,'r',encoding='utf-8') as fd:
                failed_device= json.load(fd)
        except:
            pass
        #Update failed devices list    
        failed_device= failed_device+self.failed_devices
        try:
            with open('app/failed/ims/'+file_name, 'w', encoding='utf-8') as fd:
                fd.write(json.dumps(failed_device))
        except Exception as e:
            print(e)
            print("Failed to update failed devices list"+ str(e), file=sys.stderr)
    
    def add_failed_devices_to_db(self, host, reason):
        if host['type']=='EDN':
            dccapacityFailedDb = FAILED_DEVICES_EDN_DC_CAPACITY()
        if host['type']=='IGW':
            dccapacityFailedDb = FAILED_DEVICES_IGW_DC_CAPACITY()
        
        try:
            dccapacityFailedDb.ip_address = host['device_ip']
            dccapacityFailedDb.device_id = host['device_id']
            dccapacityFailedDb.reason =reason
            dccapacityFailedDb.date = host['time']
            
            self.InsertData(dccapacityFailedDb)
            print('Successfully added Failed device to the Database', file = sys.stderr)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error while inserting failed device data into DB {e}", file=sys.stderr)


    def InsertData(self, obj):
        #add data to db
        db.session.add(obj)
        db.session.commit()
        return True
      
    def addInventoryToDB(self, host, dcCapacity):          
        #for dcCapacity in dcCapacity_data:
        dcCapacityDb=''
        if host['type']=='EDN':
            dcCapacityDb = EDN_DC_CAPACITY()
        if host['type']=='IGW':
            dcCapacityDb = IGW_DC_CAPACITY()
        try:
            dcCapacityDb.device_ip = host['device_ip']
            dcCapacityDb.site_id = host['site_id']
            dcCapacityDb.device_id = host['device_id']
            dcCapacityDb.os_version = host['os_version']
            
            dcCapacityDb.total_1g_ports = dcCapacity.get('total_1g_ports','') if dcCapacity.get('total_1g_ports','') is not None else 0
            dcCapacityDb.total_10g_ports = dcCapacity.get('total_10g_ports','') if dcCapacity.get('total_10g_ports','') is not None else 0
            dcCapacityDb.total_25g_ports = dcCapacity.get('total_25g_ports','') if dcCapacity.get('total_25g_ports','') is not None else 0
            dcCapacityDb.total_40g_ports = dcCapacity.get("total_40g_ports",'') if dcCapacity.get('total_40g_ports','') is not None else 0
            dcCapacityDb.total_100g_ports = dcCapacity.get("total_100g_ports",'') if dcCapacity.get('total_100g_ports','') is not None else 0
            dcCapacityDb.total_fast_ethernet_ports =dcCapacity.get('total_fast_ethernet_ports','') if dcCapacity.get('total_fast_ethernet_ports','') is not None else 0

            dcCapacityDb.connected_1g = dcCapacity.get('connected_1g','') if dcCapacity.get('connected_1g','') is not None else 0
            dcCapacityDb.connected_10g = dcCapacity.get('connected_10g','') if dcCapacity.get('connected_10g','') is not None else 0
            dcCapacityDb.connected_25g =  dcCapacity.get('connected_25g','') if dcCapacity.get('connected_25g','') is not None else 0
            dcCapacityDb.connected_40g = dcCapacity.get('connected_40g','') if dcCapacity.get('connected_40g','') is not None else 0
            dcCapacityDb.connected_100g = dcCapacity.get('connected_100g','') if dcCapacity.get('connected_100g','') is not None else 0
            dcCapacityDb.connected_fast_ethernet = dcCapacity.get('connected_fast_ethernet','') if dcCapacity.get('connected_fast_ethernet','') is not None else 0


            dcCapacityDb.not_connected_1g = dcCapacity.get('not_connected_1g','') if dcCapacity.get('not_connected_1g','') is not None else 0
            dcCapacityDb.not_connected_10g = dcCapacity.get('not_connected_10g','') if dcCapacity.get('not_connected_10g','') is not None else 0
            dcCapacityDb.not_connected_25g = dcCapacity.get('not_connected_25g','') if dcCapacity.get('not_connected_25g','') is not None else 0
            dcCapacityDb.not_connected_40g = dcCapacity.get('not_connected_40g','') if dcCapacity.get('not_connected_40g','') is not None else 0
            dcCapacityDb.not_connected_100g = dcCapacity.get('not_connected_100g','') if dcCapacity.get('not_connected_100g','') is not None else 0
            dcCapacityDb.not_connected_fast_ethernet =dcCapacity.get('not_connected_fast_ethernet','') if dcCapacity.get('not_connected_fast_ethernet','') is not None else 0


            dcCapacityDb.unused_sfps_1g = dcCapacity.get('unused_sfps_1g','')
            dcCapacityDb.unused_sfps_10g = dcCapacity.get('unused_sfps_10g','')
            dcCapacityDb.unused_sfps_25g = dcCapacity.get('unused_sfps_25g','')
            dcCapacityDb.unused_sfps_40g = dcCapacity.get('unused_sfps_40g','')
            dcCapacityDb.unused_sfps_100g = dcCapacity.get('unused_sfps_100g','')
                
            
            dcCapacityDb.creation_date = host['time']
            dcCapacityDb.modification_date = host['time']
            dcCapacityDb.created_by = host['user_id']
            dcCapacityDb.modified_by = host['user_id']
            

            self.InsertData(dcCapacityDb)
            #failedDB
            #self.add_failed_devices_to_db(host, f"Error while inserting data into DB {e}")
            print('Successfully added to the Database',file = sys.stderr)
    
        except Exception as e:
            #db.session.rollback()
            #failedDB
            self.add_failed_devices_to_db(host, f"Error while inserting data into DB {e}")
            print(f"Error while inserting data into DB {e}", file=sys.stderr)
            self.add_to_failed_devices(host['device_ip'], f"Failed to insert Data to DB "+str(e))

    def get_inventory_data(self, hosts):
        threads =[]
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
            return ""
      
    def poll(self, host):
        print(f"Connecting to {host['device_ip']}", file=sys.stderr)
        login_tries = 10
        c = 0
        is_login = False
        sw_type = str(host['sw_type']).lower()
        sw_type = sw_type.strip()
        while c < login_tries :
            try:
                device_type= host['sw_type']
                device = Netmiko(host=host['device_ip'], username=host['user'], password=host['pwd'], device_type=device_type, timeout=600, global_delay_factor=2)
                print(f"Success: logged in {host['device_ip']}")
                is_login = True
                break
            except Exception as e:
                c +=1
                login_exception = str(e)
                
        if is_login==False:
            print(f"Falied to login {host['device_ip']}", file=sys.stderr)
            self.add_to_failed_devices(host['device_ip'], "Failed to login to host")
            self.add_failed_devices_to_db(host, f"Failed To Login")
            #failedDB
                  
        if is_login==True:    
            print(f"Successfully Logged into device {host['device_ip']}", file=sys.stderr) 
            dcCapacityData={}
            try:
                    
                print("getting ip interface detail", file=sys.stderr)
                #output = device.send_command('show interface status', use_ttp=True)

                output = device.send_command('show interface status', textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/cisco_nxos_show_interface_status.textfsm", use_textfsm=True)
                #print(f"Output is {output}", file=sys.stderr)
                if isinstance(output,str):
                    print(f"Device data not found {output} {host['device_ip']}", file=sys.stderr)
                    raise Exception(f"Device data not found "+str(output))
                

                output = list(filter(lambda int: "po" not in int['port'].lower() and "vlan" not in int['port'].lower() and "mgmt" not in int['port'].lower() and "lo" not in int['port'].lower() and "ap" not in int['port'].lower(), output))
                #print(output, file=sys.stderr)
                total_1g=total_10g=total_25g=total_40g=total_100g=total_fast_ethernet=0
                status_fast_ethernet_connected=status_1g_connected=status_10g_connected=status_25g_connected=status_40g_connected=status_100g_connected=0
                status_fast_ethernet_not_connected=status_1g_not_connected=status_10g_not_connected=status_25g_not_connected=status_40g_not_connected=status_100g_not_connected=0
                unused_sfps_1g=unused_sfps_10g=unused_sfps_25g=unused_sfps_40g=unused_sfps_100g=0
                
                int_detail=""
                if host['sw_type']=="cisco_nxos":
                    int_detail = device.send_command(f"show interface", use_textfsm=True)
                
                #parse duplex                
                ##Populate Speed
                for interface in output:
                    if interface['speed'] != "100" and interface['speed'] != "a-100" and interface['speed'] != "1000" and interface['speed'] != "a-1000" and interface['speed'] != "1G" and interface['speed'] != "a-1G" and interface['speed'] != "10000" and interface['speed'] != "a-10000" and interface['speed'] != "10G" and interface['speed'] != "a-10G" and interface['speed'] != "25000" and interface['speed'] != "a-25000" and interface['speed'] != "25G" and interface['speed'] != "a-25G" and interface['speed'] != "40000" and interface['speed'] != "a-40000" and interface['speed'] != "40G" and interface['speed'] != "a-40G" and interface['speed'] != "100000" and interface['speed'] != "a-100000" and interface['speed'] != "100G" and interface['speed'] != "a-100G":
                        if host['sw_type']=="cisco_ios":
                            if 'Gi' in interface['port'][:2]:
                                interface['speed']="1G"
                            if 'Te' in interface['port'][:2]:
                                interface['speed']="10G"
                            if 'Fa' in interface['port'][:2]:
                                interface['speed']="100"
                            
                        if host['sw_type']=="cisco_nxos":
                            if not isinstance(output,str):                                
                                sub_interface_number= re.findall(r'[A-Za-z]*(.*)', interface["port"])[0]
                                sub_int= list(filter(lambda inter: sub_interface_number == re.findall(r'[A-Za-z]*(.*)', inter["interface"])[0], int_detail))[0]
                                hardware= sub_int['hardware_type']
                                speed= max(re.findall(r'\d+', hardware))
                                interface['speed']=speed

                #print(output, file=sys.stderr)
                for interface in output:
                    speed= str(interface['speed'])
                    #get Total Count + connected ports + not connected ports
                    if speed== "100" or speed=="a-100":
                        total_fast_ethernet+= 1
                        if interface['status']=="connected":
                            status_fast_ethernet_connected+=1
                        else:
                            status_fast_ethernet_not_connected+=1

                    elif speed== "1000" or speed=="a-1000" or speed== "1G" or speed=="a-1G" :
                        total_1g += 1
                        if interface['status']=="connected":
                            status_1g_connected+=1
                        else:
                            status_1g_not_connected+=1
                            isSfp = [sfp for sfp in  self.spfs if sfp in str(interface['type']).lower()]
                            if isSfp:
                            #if interface['type'] != "No Connector" and interface['type'] != "No Transceiver" and interface['type'] != "" and interface['type'] != "10/100/1000BaseTX" and interface['type'] != "unknown" and interface['type'] != "--" and interface['type'] != "sfpabsent" and 'No' not in interface['type']:
                                unused_sfps_1g+=1
                            
                    elif speed== "10G" or speed=="a-10G" or speed=="10000" or speed=="a-10000":
                        total_10g += 1
                        if interface['status']=="connected":
                            status_10g_connected+=1
                        else:
                            status_10g_not_connected+=1
                            #if interface['type'] != "No Connector" and interface['type'] != "No Transceiver" and interface['type'] != "" and interface['type'] != "10/100/1000BaseTX" and interface['type'] != "unknown" and interface['type'] != "--" and interface['type'] != "sfpabsent" and 'No' not in interface['type']:
                            isSfp = [sfp for sfp in  self.spfs if sfp in str(interface['type']).lower()]
                            if isSfp:
                                unused_sfps_10g+=1
                    
                    elif speed== "25G" or speed=="a-25G" or speed=="25000" or speed=="a-25000":
                        total_25g += 1
                        if interface['status']=="connected":
                            status_25g_connected+=1
                        else:
                            status_25g_not_connected+=1
                            #if interface['type'] != "No Connector" and interface['type'] != "No Transceiver" and interface['type'] != "" and interface['type'] != "10/100/1000BaseTX" and interface['type'] != "unknown" and interface['type'] != "--" and interface['type'] != "sfpabsent" and 'No' not in interface['type']:
                            isSfp = [sfp for sfp in  self.spfs if sfp in str(interface['type']).lower()]
                            if isSfp:
                                unused_sfps_25g+=1

                    elif speed== "40G" or speed=="a-40G" or  speed== "40000" or speed=="a-40000":
                        total_40g += 1
                        if interface['status']=="connected":
                            status_40g_connected+=1
                        else:
                            status_40g_not_connected+=1
                            #if interface['type'] != "No Connector" and interface['type'] != "No Transceiver" and interface['type'] != "" and interface['type'] != "10/100/1000BaseTX" and interface['type'] != "unknown" and interface['type'] != "--" and interface['type'] != "sfpabsent" and 'No' not in interface['type']:
                            isSfp = [sfp for sfp in  self.spfs if sfp in str(interface['type']).lower()]
                            if isSfp:
                                unused_sfps_40g+=1
                    
                            
                    elif speed== "100G" or speed=="a-100G" or speed== "100000" or speed=="a-100000":
                        total_100g += 1
                        if interface['status']=="connected":
                            status_100g_connected+=1          
                        else:
                            status_100g_not_connected+=1
                            #if interface['type'] != "No Connector" and interface['type'] != "No Transceiver" and interface['type'] != "" and interface['type'] != "10/100/1000BaseTX" and interface['type'] != "unknown" and interface['type'] != "--" and interface['type'] != "sfpabsent" and 'No' not in interface['type']:
                            isSfp = [sfp for sfp in self.spfs if sfp in str(interface['type']).lower()]
                            if isSfp:
                                unused_sfps_100g+=1
                    
                    
                #print("####################", file=sys.stderr)
                #print( self.speed, file=sys.stderr)
                #print("!!!!!!!!!!!!!!!!!!", file=sys.stderr)

                ## Populate Data
                dcCapacityData={}

                dcCapacityData["total_1g_ports"]= total_1g
                dcCapacityData["total_10g_ports"]= total_10g
                dcCapacityData["total_25g_ports"]= total_25g
                dcCapacityData["total_40g_ports"]= total_40g
                dcCapacityData["total_100g_ports"]= total_100g
                dcCapacityData["total_fast_ethernet_ports"]= total_fast_ethernet

                dcCapacityData["connected_fast_ethernet"]= status_fast_ethernet_connected
                dcCapacityData["not_connected_fast_ethernet"]= status_fast_ethernet_not_connected
                dcCapacityData["connected_1g"]= status_1g_connected
                dcCapacityData["not_connected_1g"]= status_1g_not_connected
                dcCapacityData["connected_10g"]= status_10g_connected
                dcCapacityData["not_connected_10g"]= status_10g_not_connected
                dcCapacityData["connected_25g"]= status_25g_connected
                dcCapacityData["not_connected_25g"]= status_25g_not_connected
                dcCapacityData["connected_40g"]= status_40g_connected
                dcCapacityData["not_connected_40g"]= status_40g_not_connected
                dcCapacityData["connected_100g"]= status_100g_connected
                dcCapacityData["not_connected_100g"]= status_100g_not_connected

                dcCapacityData["unused_sfps_1g"]= unused_sfps_1g
                dcCapacityData["unused_sfps_10g"]= unused_sfps_10g
                dcCapacityData["unused_sfps_25g"]= unused_sfps_25g
                dcCapacityData["unused_sfps_40g"]= unused_sfps_40g
                dcCapacityData["unused_sfps_100g"]= unused_sfps_100g

                self.addInventoryToDB(host, dcCapacityData)


                '''
                interfaces_count= Counter(int['speed'] for int in output  )
                #total_1g= interfaces_count.get('1000') if "1000" in interfaces_count['1000'] else 0
                print("------------ ***** ------------")
                
                print(interfaces_count)
                
                total_1g=total_10g=total_40g=total_100g=total_fast_ethernet=0
                interfaces_keys= dict.keys(interfaces_count)

                for key in interfaces_keys:
                    if "1000" in str(key): #or "auto" in str(key):
                        total_1g += interfaces_count[key]
                    if "10G" in str(key):
                        total_10g += interfaces_count[key]
                    if "40G" in str(key):
                        total_40g += interfaces_count[key]
                    if "100G" in str(key):
                        total_100g += interfaces_count[key]
                    if str(key)=="100" or str(key)=="a-100":
                        total_fast_ethernet=total_fast_ethernet+1
                    
                    if str(key)== "auto":
                        if host['sw_type']== "cisco_ios":


                dcCapacityData["total_1g_ports"]= total_1g
                dcCapacityData["total_10g_ports"]= total_10g
                dcCapacityData["total_40g_ports"]= total_40g
                dcCapacityData["total_100g_ports"]= total_100g
                dcCapacityData["total_fast_ethernet_ports"]= total_fast_ethernet

                #print("Total 1G: ", total_1g)
                #print("Total 10G: ", total_10g)
                #print("Total 40G: ", total_40g)
                #print("Total 100G: ", total_100g)

                status_1g= Counter(int['status'] for int in output  if ("100" in int['speed'] or "auto" in int['speed'].lower()))
                status_1g_not_connected = sum(status_1g[item] for item in status_1g if item!='connected')
                status_1g_connected= status_1g.get('connected') if status_1g['connected'] else 0
                #print("------------ ***** ------------")
                #print("Connected 1G", status_1g_connected)
                #print("Not Connected 1G", status_1g_not_connected)
                dcCapacityData["connected_1g"]= status_1g_connected
                dcCapacityData["not_connected_1g"]= status_1g_not_connected

                status_10g= Counter(int['status'] for int in output  if "10G" in int['speed'])
                status_10g_not_connected = sum(status_10g[item] for item in status_10g if item!='connected')
                status_10g_connected= status_10g.get('connected') if status_10g['connected'] else 0
                #print("Connected 10G", status_10g_connected)
                #print("Not Connected 10G", status_10g_not_connected)
                dcCapacityData["connected_10g"]= status_10g_connected
                dcCapacityData["not_connected_10g"]= status_10g_not_connected


                status_40g= Counter(int['status'] for int in output  if "40G" in int['speed'])
                status_40g_not_connected = sum(status_40g[item] for item in status_40g if item!='connected')
                status_40g_connected= status_40g.get('connected') if status_40g['connected'] else 0
                #print("Connected 40G", status_40g_connected)
                #print("Not Connected 40G", status_40g_not_connected)
                dcCapacityData["connected_40g"]= status_40g_connected
                dcCapacityData["not_connected_40g"]= status_40g_not_connected


                status_100g= Counter(int['status'] for int in output if "100G" in int['speed'])
                status_100g_not_connected = sum(status_100g[item] for item in status_100g if item!='connected')
                status_100g_connected= status_100g.get('connected') if status_100g['connected'] else 0
                #print("Connected 100G", status_100g_connected)
                #print("Not Connected 100G", status_100g_not_connected)
                dcCapacityData["connected_100g"]= status_100g_connected
                dcCapacityData["not_connected_100g"]= status_100g_not_connected


                print("------------ ***** ------------")
                unused_sfps_1g= Counter(int['status'] for int in output if ("100" in int['speed'] or "auto" in int['speed'].lower())  and (int['type']!="No Connector" and int['type']!="No Transceiver" and int['type']!="" and int["type"]!= "10/100/1000BaseTX" and int["type"].lower() != "unknown" and int['type']!="--") and "sfpabsent" not in int['status'].lower())
                unused_sfps_1g = sum(unused_sfps_1g[item] for item in unused_sfps_1g if item!='connected')
                #print("Unused SFPS IG ", unused_sfps_1g)
                dcCapacityData["unused_sfps_1g"]= unused_sfps_1g

                unused_sfps_10g= Counter(int['status'] for int in output if "10G" in int['speed'] and (int['type']!="No Connector" and int['type']!="No Transceiver" and int['type']!="") and "sfpabsent" not in int['status'].lower() and int["type"].lower() != "unknown" and int['type']!="--")
                unused_sfps_10g = sum(unused_sfps_10g[item] for item in unused_sfps_10g if item!='connected')
                #print("Unused SFPS I0G ", unused_sfps_10g)
                dcCapacityData["unused_sfps_10g"]= unused_sfps_10g


                unused_sfps_40g= Counter(int['status'] for int in output if "40G" in int['speed'] and (int['type']!="No Connector" and int['type']!="No Transceiver" and int['type']!="") and "sfpabsent" not in int['status'].lower() and int["type"].lower() != "unknown" and int['type']!="--")
                unused_sfps_40g = sum(unused_sfps_40g[item] for item in unused_sfps_40g if item!='connected')
                #print("Unused SFPS 40G ", unused_sfps_40g)
                dcCapacityData["unused_sfps_40g"]= unused_sfps_40g

                unused_sfps_100g= Counter(int['status'] for int in output if "100G" in int['speed'] and (int['type']!="No Connector" and int['type']!="No Transceiver" and int['type']!="") and "sfpabsent" not in int['status'].lower() and int["type"].lower() != "unknown" and int['type']!="--")
                unused_sfps_100g = sum(unused_sfps_100g[item] for item in unused_sfps_100g if item!='connected')
                #print("Unused SFPS 100G ", unused_sfps_100g)
                dcCapacityData["unused_sfps_100g"]= unused_sfps_100g

                #print("------------ ***** ------------")

                #print("Total Interfaces are:", len(output))
                '''
                
                
            except Exception as e:
                print(f" detail not found {host['device_ip']}, {str(e)}", file=sys.stderr)
                self.add_to_failed_devices(host['device_ip'], "Failed to get DC Capacity data "+str(e))
                self.add_failed_devices_to_db(host, f"Failed to get Dc Capacity Data {str(e)}")
                #failedDB
                traceback.print_exc()
  
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
       
    def getDCCapacity(self, devices):
        
        puller = DCCAPACITY()
        hosts = []
        with open('app/cred.json') as inventory:
            inv = json.loads(inventory.read())
        for device in devices:
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

            
            host={
                "device_ip": device["device_ip"],
                "user": user_name,
                "pwd": password,
                "sw_type": sw_type,
                'site_id':device['site_id'],
                'device_id':device['device_id'],
                'type':device['type'],
                'time': self.FormatStringDate(device["time"]),
                'os_version': os_version,
                'user_id': device['user_id']

            }
            hosts.append(host)
                  
        puller.get_inventory_data(hosts)
        puller.print_failed_devices()
        print("DC Capacity Completed", file=sys.stderr)


if __name__ == '__main__':

    hosts=[]

    host={
        "device_ip": "10.35.7.253",
        "user": "ciscotac",
        "pwd": "C15c0@mob1ly",
        "sw_type": "cisco_ios",
        'site_id': "MLQA",
        'device_id': "Dev1",
        'time': "11111"
    }
                
    hosts.append(host)

    puller = DCCAPACITY()
    puller.get_inventory_data(hosts)