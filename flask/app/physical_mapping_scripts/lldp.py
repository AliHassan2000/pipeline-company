import traceback
from netmiko import Netmiko
from netmiko.ssh_autodetect import SSHDetect
from app import db
from datetime import datetime
import re, sys, time, json
from app.models.phy_mapping_models import EDN_LLDP_LEGACY, IGW_LLDP_LEGACY
from app.models.inventory_models import FAILED_DEVICES_EDN_LLDP, FAILED_DEVICES_IGW_LLDP
import threading
import pandas as pd
# from mac_vendor_lookup import MacLookup, MacVendorLookupError
from netaddr import EUI
from netaddr.core import NotRegisteredError

class LLDPLegacy(object):
    def __init__(self):
        self.inv_data = {}
        self.connections_limit = 50
        self.failed_devices=[]
    
    def add_failed_devices_to_db(self, host, reason):
        if host['type']=='EDN':
            pmFailedDb = FAILED_DEVICES_EDN_LLDP()
        if host['type']=='IGW':
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
    #         print(e)
    #         print("Failed to update failed devices list"+ str(e), file=sys.stderr)
    
    def InsertData(self, obj):
        #add data to db
        db.session.add(obj)
        db.session.commit()
        return True
    
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
        data = inventory.get(host['host']).get('lldp')
        if data: 
            for lldp in data:
                try:
                    if host["type"]=="EDN":
                        lldpLegacy = EDN_LLDP_LEGACY()
                    
                    if host["type"]== "IGW":
                        lldpLegacy = IGW_LLDP_LEGACY()

                    local = lldp['local']
                    remote = lldp['remote']
                    if not remote.get('system_name'):
                        continue
                    lldpLegacy.device_a_name = local.get('hostname','')
                    lldpLegacy.device_a_interface= local.get('interface','')
                    lldpLegacy.device_a_trunk_name = local.get('trunk','')
                    lldpLegacy.device_a_ip = local.get('ip','')
                    remote_system_name= remote.get('system_name','')
                    lldpLegacy.device_b_system_name = remote_system_name.replace('.mobily.com.sa', '')
                    lldpLegacy.device_b_interface = remote.get('interface','')
                    lldpLegacy.device_b_ip = remote.get('ip','')
                    lldpLegacy.device_b_type = remote.get('type','')
                    lldpLegacy.device_b_port_desc = remote.get('desc','')
                    lldpLegacy.device_a_mac = local.get('mac','')
                    lldpLegacy.device_b_mac = remote.get('mac','')
                    lldpLegacy.device_b_mac_vendor = self.getMacVendor(remote.get('mac',''))
                    lldpLegacy.device_a_port_desc =  local.get('desc','')
                    lldpLegacy.device_a_vlan = local.get('vlan','')
                    lldpLegacy.creation_date = host["time"]
                    lldpLegacy.modification_date = host["time"]
                    lldpLegacy.service_vendor = 'LLDP'
                    db.session.add(lldpLegacy)
                    db.session.commit() 
                    print("Successfully Inserted data to DB", file=sys.stderr)                 
                except Exception as e:
                    db.session.rollback()
                    print(f"Error while inserting data into DB {e}", file=sys.stderr)
                    #self.add_to_failed_devices(host['host'], f"Failed to insert Data to DB "+str(e))
                    self.add_failed_devices_to_db(host, f"Error while inserting data into DB {e}")
                    #failedDB
        

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
            return self.inv_data
      

    def poll(self, host):
        print(f"Connecting to {host['host']}")
        login_tries = 10
        c = 0
        is_login = False
        sw_type = str(host['sw_type']).lower()
        sw_type = sw_type.strip()
        
        if sw_type=='ios':
            sw_type = 'cisco_ios'
        elif sw_type=='nx-os':
            sw_type='cisco_nxos'
        elif sw_type=='ios-xe':
            sw_type='cisco_ios'
        elif sw_type=='ios-xr':
            sw_type='cisco_xr'
        else:
            sw_type = ""
            
        while c < login_tries :
            try:
                device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type=sw_type, timeout=600, global_delay_factor=2)
                print(f"Success: logged in {host['host']}")
                is_login = True
                break
            except Exception as e:
                c +=1
                login_exception = str(e)
                
        if is_login==False:
            #failedDB
            self.add_failed_devices_to_db(host, f"Failed to Login")
            print(f"Falied to login {host['host']}", file=sys.stderr)
            #self.add_to_failed_devices(host['host'], "Failed to login to host")
            
            
        if is_login==True:    
            print(f"Successfully Logged into device {host['host']}", file=sys.stderr)  
            try:
                lldp_data = []
                print("getting local hostname", file=sys.stderr)
                # device.send_command('terminal len 0')
                # hostname = device.send_command("show running | i hostname")
                # hostname = re.findall(r'hostname\s+(.*)', hostname)
                # local_hostname = hostname[0] 
                local_hostname =host['hostname']
            except:
                print("local hostname not found", file=sys.sys.stderr)
                #self.add_to_failed_devices(host['host'], "local hostname not found ")
                local_hostname = ''
               
            try:
                remote_ip_port = {}
                print("getting lldp neighbours detail", file=sys.stderr)
                if sw_type=='cisco_ios':
                    output = device.send_command("show lldp neighbors detail", use_textfsm=True)
                if sw_type=='cisco_nxos':
                    output = device.send_command("show lldp neighbors detail", textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_nxos_show_lldp_neighbors_detail.textfsm', use_textfsm=True)
                if sw_type=='cisco_xr':
                    output = device.send_command("show lldp neighbors detail", textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_ios_xr_show_lldp_neighbors_detail.textfsm', use_textfsm=True)
                
                if isinstance(output,str):
                    print(f"LLDP data not found {output} {host['host']}", file=sys.stderr)
                    raise Exception(f"LLDP data not found "+str(output))

                for lldp in output:
                    sys_name = lldp.get('neighbor').split('.')
                    sys_name = sys_name[0] if sys_name else ''
                    #if ("sep" not in sys_name.lower()):
                    if sw_type=='cisco_xr' or sw_type== 'cisco_nxos':
                        is_ip = remote_ip_port.get(lldp.get('mgmt_address'), None)
                    else:
                        is_ip = remote_ip_port.get(lldp.get('management_ip'), None)
                                       
                    if is_ip:
                        if sw_type=='cisco_xr' or sw_type== 'cisco_nxos':
                            remote_ip_port[lldp['mgmt_address']]['interfaces'].append(lldp.get('port_id'))
                        elif sw_type== 'cisco_nxos':
                            remote_ip_port[lldp['mgmt_address']]['interfaces'].append(lldp.get('neighbor_interface'))
                        else:
                            remote_ip_port[lldp['management_ip']]['interfaces'].append(lldp.get('neighbor_port_id'))
                    else:
                        if sw_type=='cisco_xr':
                            remote_ip_port[lldp['mgmt_address']] = {'interfaces':[lldp['port_id']], 'sw_type':'cisco_xr'}
                        elif sw_type== 'cisco_nxos':
                            remote_ip_port[lldp['mgmt_address']] = {'interfaces':[lldp['neighbor_interface']], 'sw_type':'cisco_nxos'}
                        else:
                            remote_ip_port[lldp['management_ip']] = {'interfaces':[lldp['neighbor_port_id']], 'sw_type':'cisco_ios'}
       
                    if not lldp.get('local_interface'):
                        try:
                            neighbors = device.send_command("show lldp neighbors", use_textfsm=True)
                            if isinstance(output,str):
                                print(f"LLDP local port not found {output}", file=sys.stderr)
                                raise Exception(f"LLDP data not found "+str(output))
                            for neigh in neighbors:
                                single_neighbor = device.send_command(f"show lldp neighbors {neigh['local_interface']} detail", use_textfsm=True)
                                neigh_ip= re.findall(r'\s*IP:\s*(.*)', single_neighbor)[0]
                                if neigh_ip== lldp.get('management_ip',""):
                                    lldp['local_interface']= neigh.get('local_interface')
                        except Exception as e:
                            traceback.print_exc()
                            print(f"LLDP local port not found {host['host']}, {str(e)}", file=sys.stderr)

                    mac_A=desc_A=""
                    if lldp.get('local_interface'):
                        mac_A, desc_A = self.get_mac_desc_A(lldp.get('local_interface'), device, sw_type, host)
                    
                    if sw_type=='cisco_xr':
                        interface = lldp.get('port_id',"")
                        ip= lldp.get('mgmt_address', "")
                        description= lldp.get('port_description', "")
                        mac=lldp.get('peer_mac_address', "")

                    elif sw_type=='cisco_ios':
                        interface = lldp.get('neighbor_port_id', "")
                        ip=lldp.get('management_ip')
                        description=lldp.get('neighbor_interface', "")
                        mac=""

                    else:
                        interface = lldp.get('neighbor_interface', "")
                        ip= lldp.get('mgmt_address')
                        description=""
                        mac=""
                    
                    lldp_data.append({'local':{
                                            'hostname': local_hostname,
                                            'interface': lldp.get('local_interface'),
                                            'ip':host['host'],
                                            'mac': mac_A,
                                            'trunk':None,
                                            'desc':desc_A
                                            },
                                            'remote':{
                                                'system_name':sys_name,
                                                'interface':interface,
                                                'ip':ip,
                                                'mac':mac,
                                                'type': None,
                                                'desc':description                                
                                            }})
            except Exception as e:
                print(f"lldp neighbours detail not found {host['host']}, {str(e)}", file=sys.stderr)
                #self.add_to_failed_devices(host['host'], "Failed to get neighbour data "+str(e))
                self.add_failed_devices_to_db(host, f"Exception Occured in Finding LLDP {e}")
                lldp = None
                #failedDB
            try:        
                data = self.get_mac_desc_B(host, remote_ip_port)
                for r_ip, value in data.items():
                    for z in lldp_data:
                        remote = z['remote']
                        if value.get('output'):
                            for out in value['output']:
                                for r_intf, mac_desc in out.items():
                                    if remote['ip']==r_ip and remote['interface']==r_intf:
                                        if(remote['mac']==""):
                                            remote['mac'] = mac_desc['mac']
                                        if(remote['desc']==""):
                                            remote['desc'] = mac_desc['intf_desc']
                        else:
                            break
            except Exception as e:
                print("failed to update device B information"+str(e), file=sys.stderr)        
                #self.add_to_failed_devices(host['host'], "Failed to update device B information"+str(e))

            if sw_type=='cisco_ios': 
                try:
                    print("show etherchannel summary", file=sys.stderr)
                    gig_type = {'Gi':'GigabitEthernet','Te':'TenGigabitEthernet', 'Eth':'Ethernet'}
                    etherchannel = device.send_command("show etherchannel summary", use_textfsm=True) 
                    print(f"Etherchannel data found")
                    if isinstance(etherchannel,str):
                        print(f"Etherchannel data not found {etherchannel} {host['host']}")
                    for prt in etherchannel:
                        for intf in prt['interfaces']:
                            port =''
                            for key, value in gig_type.items():
                                if key in intf:
                                    port = intf.replace(key, value)
                                    break
                            for lldp in lldp_data:
                                if port==lldp['local']['interface']:
                                    lldp['local'].update({'trunk':prt['po_name']})
                except Exception as e:
                    print(f"show etherchannel summary not found {host['host']}", file=sys.stderr)
                    etherchannel = None
            
            if sw_type=='cisco_nxos':
                try:
                    print("show port-channel summary", file=sys.stderr)
                    gig_type = {'Gi':'GigabitEthernet','Te':'TenGigabitEthernet', 'Eth':'Ethernet', 'Fa':'FastEthernet'}
                    etherchannel = device.send_command("show port-channel summary", use_textfsm=True) 
                    if isinstance(etherchannel,str):
                        print(f"port-channel summary data not found {etherchannel} {host['host']}")
                    
                    for prt in etherchannel:
                        for intf in prt['phys_iface']:
                            for key, value in gig_type.items():
                                if key in intf:
                                    port = intf.replace(key, value)
                                    break
                            for lldp in lldp_data:
                                if port==lldp['local']['interface']:

                                    lldp['local'].update({'trunk':prt['bundle_iface']})
                except Exception as e:
                    print(f"show port-channel summary not found {host['host']}", file=sys.stderr)
                    etherchannel = None
            if sw_type=='cisco_xr': 
                try:
                    print("show bundle", file=sys.stderr)
                    gig_type = {'Gi':'GigabitEthernet','Te':'TenGigabitEthernet', 'Eth':'Ethernet'}
                    etherchannel = device.send_command("show bundle", textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_xr_show_bundle.textfsm', use_textfsm=True) 
                    if isinstance(etherchannel,str):
                        print(f"Bundle data not found {etherchannel} {host['host']}")        
                    
                    for bndl in etherchannel:
                        for intf in bndl['phys_iface']:
                            for key, value in gig_type.items():
                                if key in intf:
                                    port = intf.replace(key, value)
                                    break
                            for lldp in lldp_data:
                                if intf==lldp['local']['interface']:
                                    lldp['local'].update({'trunk':bndl['bundle_name']})
                except Exception as e:
                    print(f"show bundle {e}", file=sys.stderr)
                    etherchannel = None    

            try:
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                self.inv_data[host['host']].update({'lldp': lldp_data})
                self.inv_data[host['host']].update({'status': 'success'})
                #Add data to DB
                self.addInventoryToDB(host, self.inv_data)
            except Exception as e:
                print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
                #self.add_to_failed_devices(host['host'], "Inventory not found Exception detail==> "+str(e))
                traceback.print_exc()
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error', "hostname":host['hostname'], 'ip':host['host'],'sw_type':host['sw_type']})
                    self.inv_data[host['host']].update({'lldp': []})
            
           
            if is_login: device.disconnect()
  
    def get_mac_desc_A(self, intf , device, sw_type, host):
        print("Getting Device A Mac and description", file=sys.stderr)
        try:
            time.sleep(2)
            if(sw_type=='cisco_xr'):
                description=""
                mac_add = 'show interfaces '+intf+' | i \(bia)'
                desc='show interfaces '+intf+' | i \(Description)'
                mac = device.send_command(mac_add)
                mac_desc = device.send_command(desc)
                mac_adr = re.search(r'(address:\s+|address\s+is\s+)([a-zA-Z0-9.]*)', mac)
                mac_adr = mac_adr.group(2) if mac_adr else mac_adr
                desc = re.findall(r'Description:\s+(.*)', mac_desc)
                description = desc[0] if desc else None
            else:
                if sw_type=='cisco_nxos':
                    cmd = 'show interface '+intf+' | i \(bia|Description' 
                if sw_type=='cisco_ios':
                    cmd = 'show interfaces '+intf+' | i \(bia|Description'
                print(cmd)
                mac_desc = device.send_command(cmd)
                if "Hardware" not in mac_desc:
                    raise Exception(f"Failed to send command show interface "+str(mac_desc))         
                mac_adr = re.search(r'(address:\s+|address\s+is\s+)([a-zA-Z0-9.]*)', mac_desc)
                mac_adr = mac_adr.group(2) if mac_adr else mac_adr
                description=""
                if "Description" in mac_desc:
                    desc = re.findall(r'Description:\s+(.*)', mac_desc)
                    description = desc[0] if desc else None
                     
                
            return mac_adr, description
        except Exception  as e:
            print(f"error while getting device a mac {e}", file=sys.stderr)
            #self.add_to_failed_devices(host['host'], "Failed to get device A mac "+str(e))
            return None, None
    
    def get_mac_desc_B(self, host, remote_ips):
        print("Getting Device B Mac and description", file=sys.stderr)
        for ip, interfaces in remote_ips.items():
            login_tries = 3
            c = 0
            is_login = False
            print(f"Now connecting to {ip}")
            print(f"device software type {remote_ips[ip]['sw_type']}")
            sw_type = remote_ips[ip]['sw_type']
            '''
            if 'IOS' in sw_type:
                sw_type = 'cisco_ios'
            elif 'NX-OS' in sw_type:
                sw_type='cisco_nxos'
            elif 'IOS-XE' in sw_type:
                sw_type='cisco_ios'
            elif 'IOS-XR' in sw_type:
                sw_type='cisco_xr'
            else:
                sw_type = ""
                continue
            '''
            # print(f"Getting device B Mac and Port description for interfaces {interfaces['interfaces']}")
            
            while c < login_tries :
                try:
                    
                    
                    device = Netmiko(host=ip, username=host['user'], password=host['pwd'], device_type=sw_type, timeout=600, global_delay_factor=2)
                    print(f"Connected : {ip}")
                    is_login = True
                    break
                except Exception as e:
                    c +=1
                    
                    
            if is_login==False:
                print(f"Device B {ip} Login failed  ", file=sys.stderr)
                #self.add_to_failed_devices(host['host'], "Failed to login to neighbor "+str(ip))
                self.add_failed_devices_to_db(host, f"Failed to Login to Device B {ip}")
                #failedDB
            
            if is_login:
                intf_output = []
                print(f"Succesfully logged into LLDP Neighbour devie {ip}", file=sys.stderr)
                try:
                    for interface in interfaces['interfaces']:
                        if(sw_type=='cisco_xr'):
                            description=""
                            mac_add = 'show interfaces '+interface+' | i \(bia)'
                            desc='show interfaces '+interface+' | i \(Description)'
                            mac = device.send_command(mac_add)
                            mac_desc = device.send_command(desc)
                            mac_adr = re.search(r'(address:\s+|address\s+is\s+)([a-zA-Z0-9.]*)', mac)
                            mac_adr = mac_adr.group(2) if mac_adr else mac_adr
                            desc = re.findall(r'Description:\s+(.*)', mac_desc)
                            description = desc[0] if desc else None
                        else:
                            if sw_type=='cisco_nxos':
                                cmd = 'show interface '+interface+' | i \(bia|Description'
                            if sw_type=='cisco_ios' or sw_type=='cisco_xr':
                                cmd = 'show interfaces '+interface+' | i \(bia|Description'
                            print(cmd)
                            mac_desc = device.send_command(cmd)
                            if "Hardware" not in mac_desc:
                                raise Exception(f"Failed to send command show interface "+str(mac_desc))
                            else:
                                mac_adr = re.search(r'(address:\s+|address\s+is\s+)([a-zA-Z0-9.]*)', mac_desc)
                                mac_adr = mac_adr.group(2) if mac_adr else None
                            description=""
                            if "Description" not in mac_desc:
                                print("Device B Interface description not found", file=sys.stderr)
                            else:
                                desc = re.findall(r'Description:\s+(.*)', mac_desc)
                                description = desc[0] if desc else None
                        intf_output.append({interface:{'mac':mac_adr,'intf_desc':description}})
                        # print(f"Device B-interface({interface}) mac and desc {mac_adr} {description}")
                    device.disconnect()
                    remote_ips[ip].update({'output':intf_output})
                except Exception as e:
                    print(f"error while getting device B mac {e}", file=sys.stderr)
                    #self.add_to_failed_devices(host['host'], f"Failed to get device B ({ip}) mac "+str(e))

        return remote_ips
            
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
       


    def getPhysicalMapping(self, devices):
        puller = LLDPLegacy()
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

            host={
                "host": device["ip"],
                "user": user_name,
                "pwd": password,
                "sw_type": device["sw_type"],
                'hostname':device["hostname"],
                'time': self.FormatStringDate(device["time"]),
                'type': device["type"]
            }
             
            hosts.append(host)
        puller.get_inventory_data(hosts)
        #puller.print_failed_devices()
        print("LLDP Legacy Completed", file=sys.stderr)
