import traceback
from netmiko import Netmiko
from app import db
from datetime import datetime
import re, sys, time, json
from app.models.inventory_models import EDN_IPAM_TABLE, IGW_IPAM_TABLE, SOC_IPAM_TABLE, FAILED_DEVICES_EDN_IPAM, FAILED_DEVICES_IGW_IPAM, FAILED_DEVICES_SOC_IPAM
import threading
import socket, struct
from netaddr import IPNetwork


class IPAM(object):
    def __init__(self):
        self.connections_limit = 2
        self.failed_devices=[]
        
    def calculate_subnet_mask(self, ip_address, cidr):
        # Split the IP address into octets
        octets = ip_address.split('.')

        # Convert each octet to binary
        binary_octets = [format(int(octet), '08b') for octet in octets]

        # Create the subnet mask by setting network bits to 1
        subnet_mask = ['1' * cidr + '0' * (32 - cidr)]

        # Split the subnet mask into octets
        subnet_octets = [subnet_mask[0][i:i+8] for i in range(0, 32, 8)]

        # Convert the subnet mask octets to decimal
        decimal_subnet = [str(int(octet, 2)) for octet in subnet_octets]

        # Join the decimal octets with dots to form the subnet mask
        subnet_mask_str = '.'.join(decimal_subnet)

        return subnet_mask_str
    
    def add_failed_devices_to_db(self, host, reason):
        if host['type']=='EDN':
            ipamFailedDb = FAILED_DEVICES_EDN_IPAM()
        if host['type']=='IGW':
            ipamFailedDb = FAILED_DEVICES_IGW_IPAM()
        if host['type']=='SOC':
            ipamFailedDb = FAILED_DEVICES_SOC_IPAM()
        
        try:
            ipamFailedDb.ip_address = host['mgmt_ip']
            ipamFailedDb.device_id = host['device_id']
            ipamFailedDb.reason =reason
            ipamFailedDb.date = host['time']
            
            self.InsertData(ipamFailedDb)
            print('Successfully added Failed device to the Database', file = sys.stderr)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error while inserting failed device data into DB {e}", file=sys.stderr)


    
    def InsertData(self, obj):
        #add data to db
        db.session.add(obj)
        db.session.commit()
        return True
      
    def addInventoryToDB(self, host, ipam_data):          
        for ipam in ipam_data:
            if ipam.get('ip_address'):
                ipamDb=''
                if host['type']=='EDN':
                    ipamDb = EDN_IPAM_TABLE()
                if host['type']=='IGW':
                    ipamDb = IGW_IPAM_TABLE()
                if host['type']=='SOC':
                    ipamDb = SOC_IPAM_TABLE()
                try:
                    ipamDb.region = host['region']
                    ipamDb.site_id = host['site_id']
                    ipamDb.site_type = host['site_type']
                    ipamDb.device_id = host['device_id']
                    ipamDb.management_ip = host['mgmt_ip']
                    ipamDb.ip_address = ipam.get('ip_address','')
                    ipamDb.subnet_mask = ipam.get('subnet_mask','')
                    ipamDb.interface_name = ipam.get("interface_name","")
                    if 'fortinet' in host['sw_type']:
                        ipamDb.admin_status = 'up' if 'up'in ipam.get("admin_status","") else 'down'
                        
                        if 'up' in ipam.get("admin_status",""):
                            ipamDb.protocol_status = 'enable'
                        else:
                            ipamDb.protocol_status = 'enable' if ipam.get("protocol_status","")== 'up'else 'disable'
                    else:
                        ipamDb.protocol_status = 'up' if 'up'in ipam.get("protocol_status","") else 'down'
                        
                        if 'up' in ipam.get("protocol_status",""):
                            ipamDb.admin_status = 'enable'
                        else:
                            ipamDb.admin_status = 'enable' if ipam.get("admin_status","")== 'up'else 'disable'

                    ipamDb.vlan = ipam.get("vlan_number","")
                    ipamDb.description = ipam.get("description","")
                    ipamDb.vlan_name = ipam.get("vlan_name")
                    ipamDb.subnet = ipam.get("subnet","")
                    ipamDb.virtual_ip = ipam.get("virtual_ip","")
                    ipamDb.creation_date = host['time']
                    ipamDb.modification_date = host['time']
                    ipamDb.created_by =  host['user_id']
                    ipamDb.modified_by =  host['user_id']
                    
                    self.InsertData(ipamDb)
                    print('Successfully added to the Database',file = sys.stderr)
            
                except Exception as e:
                    db.session.rollback()
                    print(f"Error while inserting data into DB {e}", file=sys.stderr)
                    self.add_failed_devices_to_db(host, f"Error while inserting data into DB {e}")

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
        vlans= interfaces=virtualIps=ipamData=secondary_ips=[]
        print(f"Connecting to {host['mgmt_ip']}", file=sys.stderr)
        #print("Connecting", host['user'], host['pwd'], host['sw_type'], file=sys.stderr)
        login_tries = 3
        c = 0
        is_login = False
        sw_type = str(host['sw_type']).lower()
        sw_type = sw_type.strip()
        while c < login_tries :
            try:
                device_type= host['sw_type']
                device_type= device_type.split('-')[0] if 'leaf' in device_type else device_type
                device = Netmiko(host=host['mgmt_ip'], username=host['user'], password=host['pwd'], device_type=device_type, timeout=600, global_delay_factor=2)
                print(f"Success: logged in {host['mgmt_ip']}")
                is_login = True
                break
            except Exception as e:
                c +=1
                login_exception = str(e)
                #print(login_exception, file=sys.stderr)
                
        if is_login==False:
            print(f"Falied to login {host['mgmt_ip']}", file=sys.stderr)
            self.add_failed_devices_to_db(host, "Failed to Login")
                  
        if is_login==True:    
            print(f"Successfully Logged into device {host['mgmt_ip']}", file=sys.stderr) 
            
            try:
                    
                print("getting ip interface detail", file=sys.stderr)
                
                if sw_type=="cisco_nxos-leaf":
                    try:
                        output = device.send_command('show ip interface brief', textfsm_template="app/pullers/ntc-templates/ntc_templates/templates/aci_leaf_show_ip_interface_brief.textfsm", use_textfsm=True)
                        parsed_vrfs= self.parseAcileafData(output, host)
                        interfaces=list(filter(lambda int: 'overlay' not in int['vrf'], parsed_vrfs))
                        interfaces= self.parseInterfaceKeys(interfaces, host['sw_type'], host)
                        ipam_data= self.getSubnetMask(interfaces, host)
                        print(ipam_data, file=sys.stderr)
                        self.addInventoryToDB(host, ipam_data)
                    
                    except Exception as e:
                        print(f"Ipam detail not found {host['mgmt_ip']}, {str(e)}", file=sys.stderr)
                        self.add_failed_devices_to_db(host, f"Failed to get IPAM data {e}")
                        traceback.print_exc()
                    return
                
                if sw_type=="f5_tmsh":
                    try:
                        print("getting data for F5 IP Collector", file=sys.stderr)
                        data = []
                        output1 = device.send_command('show net self all', textfsm_template="app/pullers/ntc-templates/ntc_templates/templates/f5_ltm_show_net_self_all.textfsm", use_textfsm=True)
                        output2 = device.send_command('list net self vlan address', textfsm_template="app/pullers/ntc-templates/ntc_templates/templates/f5_ltm_list_net_self_vlan_address.textfsm", use_textfsm=True)
                        for row in output1:
                            dict = {}
                            dict['ip_address'] = row['ip_address']
                            dict['vlan_name'] = row['vlan_name']
                            dict['description'] = row['interface_description']
                            dict['vlan_number'] = row['vlan_id']
                            dict['admin_status'] = row['admin_status']
                            interfaces=list(filter(lambda int: int['ip_address'] == row['ip_address'] , output2))
                            if len(interfaces)>0:
                                cidr = interfaces[0].get("cidr")
                                temp_address = row['ip_address']+"/"+cidr
                                ip = IPNetwork(temp_address)
                                # interface['subnet']= str(ip.network)+"/"+str(temp_address).split('/')[1]
                                # interface['ip_address'] = ip.ip
                                dict['subnet_mask'] = ip.netmask
                                dict['subnet']= str(ip.network)+"/"+str(temp_address).split('/')[1]
                            data.append(dict)

                        # parsed_vrfs= self.parseAcileafData(output, host)
                        # interfaces=list(filter(lambda int: 'overlay' not in int['vrf'], parsed_vrfs))
                        # interfaces= self.parseInterfaceKeys(interfaces, host['sw_type'], host)
                        
                        # ipam_data= self.getSubnetMask(interfaces, host)
                        self.addInventoryToDB(host, data)
                    
                    except Exception as e:
                        print(f"Ipam detail not found {host['mgmt_ip']}, {str(e)}", file=sys.stderr)
                        self.add_failed_devices_to_db(host, f"Failed to get IPAM data {e}")
                        traceback.print_exc()
                    return
                
                if sw_type=='fortinet':
                    print("getting System Detail")
                    try:
                        systemArps = device.send_command('get system interface',use_textfsm=True,textfsm_template = "app/pullers/ntc-templates/ntc_templates/templates/fortigate_get_system_interface.textfsm")
                        interfaces1=list(filter(lambda int: (int['ip_address'] != '' and int['ip_address'].lower() != 'unassigned' and int['ip_address'].lower() != 'unknown' and int['ip_address']!='0.0.0.0'), systemArps))
                        print(interfaces1,file=sys.stderr)
                        tempList = []
                        
                        interfaces = device.send_command('show system interface',use_textfsm=True,textfsm_template = "app/pullers/ntc-templates/ntc_templates/templates/fortigate_show_system_interface.textfsm")
                        # interfaces=list(filter(lambda int: (int['ip_address'] != '' and int['ip_address'].lower() != 'unassigned' and int['ip_address'].lower() != 'unknown' and int['ip_address']!='0.0.0.0'), systemArps))
                        print(interfaces,file=sys.stderr)
                        for interface in interfaces1:
                            #print("First Command", interface, file=sys.stderr)
                            temp = {}
                            interface2=list(filter(lambda int: int['vlan_name'] == interface['vlan_name'], interfaces))
                            if len(interface2)>0:
                                temp['ip_address'] = interface.get('ip_address')
                                temp['admin_status'] = interface.get('status')
                                temp['subnet_mask'] = interface.get('subnet')
                                temp['vlan_name'] = interface.get('vlan_name')
                                cidr = sum(bin(int(x)).count('1') for x in temp['subnet_mask'].split('.'))
                                ipsubnet = temp['ip_address']+"/"+str(cidr)
                                ip = IPNetwork(ipsubnet)
                                temp['subnet'] = str(ip.network)+"/"+str(ip).split('/')[1]
                                temp['description'] = interface2[0].get('description')
                                # if (interface2[0].get('status')).lower()!='down':
                                #     temp['protocol_status'] = 'up'
                                # else:
                                #     temp['protocol_status'] = interface2[0].get('status')
                                temp['vlan_number'] = interface2[0].get('vlan_id')
                                
                                tempList.append(temp)
                        
                        
                        self.addInventoryToDB(host,tempList)
                    except Exception as e:
                        print(f"Ipam detail not found {host['mgmt_ip']}, {str(e)}", file=sys.stderr)
                        self.add_failed_devices_to_db(host, f"Failed to get IPAM data {e}")
                        traceback.print_exc()
                    return
                
                if sw_type=='juniper':
                    print("getting System Detail")
                    try:
                        systemArps = device.send_command('show interface terse | display xml',use_textfsm=True,textfsm_template = "app/pullers/ntc-templates/ntc_templates/templates/juniper_show_interface_terse_display_xml.textfsm")
                        interfaces1=list(filter(lambda int: (int['ip_address'] != '' and int['ip_address'].lower() != 'unassigned' and int['ip_address'].lower() != 'unknown' and int['ip_address']!='0.0.0.0'), systemArps))
                        print(interfaces1,file=sys.stderr)
                        tempList = []
                        
                        for interface in interfaces1:
                            if "em" in interface['interface_name'] or "fab" in interface['interface_name']:
                              continue
                            temp = {}
                            temp['ip_address'] = interface.get('ip_address')
                            temp['admin_status'] = interface.get('admin_status')
                            tempCidr = interface.get('subnet')
                            newMask = int(tempCidr[1:])
                            #print(newMask, file=sys.stderr)
                            subnet_mask = self.calculate_subnet_mask(temp['ip_address'], newMask)
                            #print(subnet_mask, file=sys.stderr)
                            temp['subnet_mask'] = subnet_mask
                            cidr = sum(bin(int(x)).count('1') for x in temp['subnet_mask'].split('.'))
                            ipsubnet = temp['ip_address']+"/"+str(cidr)
                            ip = IPNetwork(ipsubnet)
                            temp['subnet'] = str(ip.network)+"/"+str(ip).split('/')[1]
                            if (interface.get('protocol')).lower()!='down':
                                temp['protocol_status'] = 'up'
                            else:
                                temp['protocol_status'] = interface.get('protocol')
                            temp['description'] = interface.get('description')
                            temp['interface_name'] = interface.get('interface_name')
                            
                            tempList.append(temp)
                        
                        
                        self.addInventoryToDB(host,tempList)
                    except Exception as e:
                        print(f"Ipam detail not found {host['mgmt_ip']}, {str(e)}", file=sys.stderr)
                        self.add_failed_devices_to_db(host, f"Failed to get IPAM data {e}")
                        traceback.print_exc()
                    return
                
                if sw_type=='cisco_asa':
                    print("getting Interface")
                    try:
                        systemArps = device.send_command('sho interface',use_textfsm=True,textfsm_template = "app/pullers/ntc-templates/ntc_templates/templates/cisco_asa_soc_sho_interface.textfsm")
                        interfaces=list(filter(lambda int: (int['ip_address'] != '' and int['ip_address'].lower() != 'unassigned' and int['ip_address'].lower() != 'unknown' and int['ip_address']!='0.0.0.0'), systemArps))
                        print(interfaces,file=sys.stderr)
                        tempList = []
                        
                        for interface in interfaces:
                            temp = {}
                            temp['admin_status'] = interface.get('admin_status')
                            temp['ip_address'] = interface.get('ip_address')
                            temp['subnet_mask'] = interface.get('subnet')

                            cidr = sum(bin(int(x)).count('1') for x in temp['subnet_mask'].split('.'))
                            ipsubnet = temp['ip_address']+"/"+str(cidr)
                            ip = IPNetwork(ipsubnet)
                            temp['subnet'] = str(ip.network)+"/"+str(ip).split('/')[1]

                            if (interface.get('protocol')).lower()!='down':
                                temp['protocol_status'] = 'up'
                            else:
                                temp['protocol_status'] = interface.get('protocol')
                            temp['description'] = interface.get('description')
                            temp['interface_name'] = interface.get('interface_name')
                            
                            tempList.append(temp)
                        
                        
                        self.addInventoryToDB(host,tempList)
                    except Exception as e:
                        print(f"Ipam detail not found {host['mgmt_ip']}, {str(e)}", file=sys.stderr)
                        self.add_failed_devices_to_db(host, f"Failed to get IPAM data {e}")
                        traceback.print_exc()
                    return

                if sw_type=="cisco_nxos":
                    
                    output = device.send_command('show interface', textfsm_template="app/pullers/ntc-templates/ntc_templates/templates/cisco_nxos_show_interface.textfsm", use_textfsm=True)
                else:
                    output = device.send_command('show interface',use_textfsm=True)
                
                if isinstance(output,str):
                    print(f"Device data not found {output} {host['mgmt_ip']}", file=sys.stderr)
                    raise Exception(f"Device data not found "+str(output))
                
                interfaces=list(filter(lambda int: (int['ip_address'] != '' and int['ip_address'].lower() != 'unassigned' and int['ip_address'].lower() != 'unknown'), output))
                if len(interfaces)== 0:
                    print("No Valid Interface found",file=sys.stderr)
                    return
                interfaces= self.parseInterfaceKeys(interfaces, host['sw_type'], host)
                print(" Valid Interface found", file=sys.stderr)

                # adding network detail
                interfaces= self.getSubnetMask(interfaces, host)

                #getting vlans
                try:
                    print("getting Vlans detail", file=sys.stderr)
                    if sw_type == 'cisco_ios' or sw_type == 'cisco_nxos': 
                        vlans = device.send_command('show vlan',use_textfsm=True)
                        #print(vlans, file=sys.stderr)
                        try:
                            secondary_ips = device.send_command('show run | begin interface', textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_ios_show_secondary_vlan_ip.textfsm', use_textfsm=True)
                            if not isinstance(output,list):
                                secondary_ips=[]
                            #print(f"##  {secondary_ips}", file=sys.stderr)
                        except Exception as e:
                            print(f"Error in getting secondary ips {e}",  file=sys.stderr)
                    if isinstance(output,str):
                        print(f"VLAN detail not found {output} {host['mgmt_ip']}", file=sys.stderr)
                        raise Exception(f"Vlan detail not found "+str(output))
                    vlans= self.parseValnKeys(vlans, host['sw_type'], host)
                except Exception as e:
                    print("Failed to get Vlans", file=sys.stderr)

                #getting virtual ip
                try:
                    print("getting Virtual IPS", file=sys.stderr)
                    if sw_type == 'cisco_ios':
                        virtualIps = device.send_command('show standby', textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_ios_show_standby.textfsm', use_textfsm=True)
                        #print(f"%%% {virtualIps}")
                    if sw_type == 'cisco_nxos':
                        virtualIps = device.send_command('show hsrp all', textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_nxos_show_hsrp_all.textfsm', use_textfsm=True)
                        #print(virtualIps)
                    if isinstance(output,str):
                        print(f"Virtual IPS detail not found {output} {host['mgmt_ip']}", file=sys.stderr)
                        raise Exception(f"Virtual IPS detail not found "+str(output))
                    virtualIps= self.parseVirtualIpKeys(virtualIps, host['sw_type'], host)
                except Exception as e:
                    print("Failed to get Virtual IPS", file=sys.stderr)

               
                #Merging All Dictionaries
                
                for interface in interfaces:
                    secondary_ip={} 
                    try:
                        if "vlan" in interface['interface_name'].lower():
                            vlan_id= interface['interface_name'][4:]
                            if isinstance(vlans, list):
                                matched_vlan =list(filter(lambda vlan: vlan['vlan_id'] == vlan_id, vlans))
                                if matched_vlan:
                                    interface.update(matched_vlan[0])

                            if isinstance(virtualIps, list):
                                matched_virtualIps =list(filter(lambda vir: vir['vlan_id'] == vlan_id, virtualIps))
                                #print(matched_virtualIps, file=sys.stderr)
                                if matched_virtualIps:
                                    interface.update(matched_virtualIps[0])
                            ###
                        secondary_interface=[]
                        try:
                            if len(secondary_ips)>0 and type(secondary_ips) == list:
                                secondary_interface=list(filter(lambda int: int.get('vlan_id')==interface['interface_name'], secondary_ips))
                                # print(f"secondaryint fond {secondary_interface} ", file=sys.stderr)
                                
                        except Exception as e:
                            traceback.print_exc()
                            print(f"Exception in finding Secondary IP host: {host['mgmt_ip']} error: {e}", file=sys.stderr)
                        
                        if len(secondary_interface)>0:
                            if secondary_interface[0].get('secondary_ip'):

                                secondary_ip= interface.copy()
                                secondary_ip['ip_address']= secondary_interface[0].get('secondary_ip')
                                try:
                                    secondary_ip['virtual_ip']= interface.get('secondary_virtual_ip')
                                    ip = IPNetwork(secondary_ip['ip_address'])
                                    secondary_ip['subnet_mask']= secondary_interface[0].get('secondary_subnet_mask')
                                    ip.netmask = secondary_interface[0].get('secondary_subnet_mask')
                                    secondary_ip['subnet']= str(ip)
                                except Exception as e:
                                    print("Failed to get secondary virtual ip", file=sys.stderr)
                                
                                ipamData.append(secondary_ip)

                        ipamData.append(interface)  
                    except Exception as e:
                        print("Failed to Parse IPAM data"+str(e), file=sys.stderr)        
                        self.add_failed_devices_to_db(host, f"Failed to Parse IPAM data {e}")
                        traceback.print_exc()

                #print(f"Final IPAM Data is : {ipamData}", file=sys.stderr)
                self.addInventoryToDB(host, ipamData)
                
            except Exception as e:
                print(f"Ipam detail not found {host['mgmt_ip']}, {str(e)}", file=sys.stderr)

                self.add_failed_devices_to_db(host, f"Failed to get IPAM data {e}")
                traceback.print_exc()

    def getSubnetMask(self, interfaces, host):
        try:
            for interface in interfaces:
                ip = IPNetwork(interface['ip_address'])
                interface['subnet']= str(ip.network)+"/"+str(interface['ip_address']).split('/')[1]
                interface['ip_address'] = ip.ip
                interface['subnet_mask'] = ip.netmask
                
        except Exception as e:
            print(f"Exception Occured while Getting Subnet Mask {e}", file=sys.stderr)
            traceback.print_exc()
        return interfaces              

    def parseInterfaceKeys(self, interfaces, sw_type, host):
        try:
            for interface in interfaces:
                if sw_type=='cisco_ios':
                    interface['vlan_number']= interface['interface'][4:] if 'vlan' in interface['interface'].lower() else ''
                    interface['interface_name']= interface.pop('interface')
                    interface['admin_status']= interface.pop('link_status')
                
                elif sw_type=='cisco_xr':
                    interface['vlan_number']= interface['interface'][4:] if 'vlan' in interface['interface'].lower() else ''
                    interface['interface_name']= interface.pop('interface')
                    interface['protocol_status']= interface.pop('link_status')
                    interface['admin_status']= interface.pop('admin_state')

                elif sw_type=='cisco_nxos':
                    interface['vlan_number']= interface['interface'][4:] if 'vlan' in interface['interface'].lower() else ''
                    interface['interface_name']= interface.pop('interface')
                    interface['protocol_status']= interface.pop('link_status') 
                    interface['admin_status']= interface.pop('admin_state')
                
                elif sw_type=='cisco_nxos-leaf':
                    interface['vlan_number']= interface['interface_name'][4:] if 'vlan' in interface['interface_name'].lower() else ''
                    interface['vlan_name']= interface['vrf'] if 'vlan' in interface['interface_name'].lower() else ''
                    interface['description']= interface['vrf']
                
        except Exception as e:
            print(f"Exception Occured while Parsing Interfaces Keys {e}", file=sys.stderr)
            traceback.print_exc()

       
        return interfaces 

    def parseValnKeys(self, vlans, sw_type, host):
        try:
            for vlan in vlans:
                if sw_type=='cisco_ios' or sw_type=='cisco_nxos':
                    vlan['vlan_name']= vlan.pop('name')
        except Exception as e:
            print(f"Exception Occured while Parsing Vlan Keys {e}", file=sys.stderr)

        return vlans        

    def parseVirtualIpKeys(self, virtualIps, sw_type, host):
        try:
            for virtualIp in virtualIps:
                if sw_type=='cisco_ios':
                    virtualIp['virtual_ip']= virtualIp.pop('virtual_ip')
                if sw_type=='cisco_nxos':
                    virtualIp['virtual_ip']= virtualIp.pop('primary_ipv4_address')
                    virtualIp['group']= virtualIp.pop('group_number')
        except Exception as e:
            print(f"Exception Occured while Parsing Vitual IP Keys {e}", file=sys.stderr)
        return virtualIps

    def parseAcileafData(self, interfaces, host):
        try:
            interfaces= self.parseVrfs(interfaces, host)
        
        except Exception as e:
                print(f"Exception Occured While Parsing ACI Leaf data {e}", file=sys.stderr)
        return interfaces

    def parseVrfs(self, interfaces, host):
        vrf=""
        for interface in interfaces:
            try:
                if interface['vrf'] != "" and interface['vrf'] != ":":
                    vrf= interface['vrf']
                interface['vrf']= vrf
            except Exception as e:
                print(f"Exception Occured While Parsing VRFS {e}", file=sys.stderr)
        
        return interfaces

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
       
    def getIpam(self, devices):
        print("In the puller", devices, file=sys.stderr)
        puller = IPAM()
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
            
            if device['type'] == 'SOC':
                user_name = inv['SEC']['user']
                password = inv['SEC']['pwd']

            sw_type = str(device['sw_type']).lower()
            sw_type = sw_type.strip()
            print(sw_type,file=sys.stderr)

            if sw_type=='ios':
                sw_type = 'cisco_ios'
            elif sw_type=='ios-xe':
                sw_type = 'cisco_ios'
            elif sw_type == 'ios-xr':
                sw_type = 'cisco_xr'
            elif sw_type == 'nx-os':
                sw_type = 'cisco_nxos'
            elif sw_type=='aci-leaf':
                sw_type = 'cisco_nxos-leaf'
            elif sw_type=='f5':
                sw_type = 'f5_tmsh'
            elif sw_type=='fortinet-sec':
                sw_type='fortinet'
            elif sw_type=='juniper-sec':
                sw_type='juniper'
            elif sw_type=='ASA-SOC':
                sw_type='cisco_asa'
            elif sw_type=='ASA96':
                sw_type='cisco_asa'
            else:
                sw_type=''

            host={
                "mgmt_ip": device["mgmt_ip"],
                "user": user_name,
                "pwd": password,
                "sw_type": sw_type,
                "type": device["type"],
                'region':device["region"],
                'site_id':device['site_id'],
                'site_type':device['site_type'],
                'device_id':device['device_id'],
                'user_id': device['user_id'],
                'time': self.FormatStringDate(device["time"])

            }
            #print("HOST inside loop", host, file=sys.stderr)
            hosts.append(host)
        puller.get_inventory_data(hosts)
        #puller.print_failed_devices()
        print("IPAM Completed", file=sys.stderr)
