# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:23:08 2021

@author: HP
"""

from netmiko import Netmiko
import re, sys, json,time
import pandas as pd
from pandas import read_excel
from time import datetime
#dfIp = read_excel('EDN_NE_IPs_Puller.xlsx', sheet_name = 'EDN_NE')
dfIp = read_excel('test.xlsx', sheet_name = 'EDN_NE')

dfObj = pd.DataFrame(columns=['Device A Name', 'Device A Interface', 'Device A Trunk Name',	'Device A IP',	'Device B System Name',	'Device B Interface', 'VLAN-ID',	'Device B IP',	'Device B Type', 'Device B Port Description', 'Device A MAC', 'Device B MAC', 'Device A Interface Description'])
obj_in=0

host = {
        "host": "",
        "user": "",
        "pwd": "",
        "hostname": "",
        "type": ""
        }

for index, frame in dfIp['Switch IP-Address'].iteritems():
    
    host['host'] = frame
    host['hostname'] = dfIp['Switch Name']
    
    if dfIp.loc[index,'sw_type'] == 'IOS':
        host['user'] = 'ciscotac'
        host['pwd'] = 'C15c0@mob1ly'
        host['type'] = 'cisco_ios'
        
    elif dfIp.loc[index,'sw_type'] == 'NX-OS':
        host['user'] = 'ciscotac'
        host['pwd'] = 'C15c0@mob1ly'
        host['type'] = 'cisco_nxos'
        
    elif dfIp.loc[index,'sw_type'] == 'IOS-XE':
        host['user'] = 'ciscotac'
        host['pwd'] = 'C15c0@mob1ly'
        host['type'] = 'cisco_ios'
        
    deviceA_name = host['hostname']
    deviceA_interface = ""
    deviceA_Trunk = ""
    deviceA_IP = host['host']
    deviceB_IP = ""
    deviceA_mac=""
    deviceB_mac=""
    deviceA_interface_description = ""
    vlan = ""
        
    login_tries = 3
    c = 0
    is_login = False
    login_exception = None
    while c < login_tries :
        try:
                        
            device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type=host['type'], timeout=800, global_delay_factor=2)
            print(f"Success: logged in {host['host']} at index {index}")
            
            is_login = True
            break
        except Exception as e:
            c +=1
            login_exception = str(e)
    if is_login==False:
        print(f"Falied to login {host['host']}")
    
    if is_login==True:
        
        if host['type'] == 'cisco_nxos':
            try:
                device.send_command("terminal length 0")
            except:
                pass
            
            ##########get all arp
            dfArp = pd.DataFrame(columns=['mac', 'ip'])
            print("getting arp table")
                
            arps = device.send_command("show ip arp", use_textfsm=True)
            i=0
       
            for arp in arps:
                if (arp['mac'] == dfArp['mac']).any():
                    locindex = dfArp[dfArp['mac'] == arp['mac']].index.item()
                    if arp['address'] in dfArp.loc[locindex, 'ip']:
                        continue
                    else:
                        dfArp.loc[locindex, 'ip'] = dfArp.loc[locindex, 'ip']+','+arp['ip_address']
                        
                else:
                    dfArp.loc[i, 'ip'] = arp['address']
                    dfArp.loc[i, 'mac'] = arp['mac']
                    i+=1
                    
            print("getting mac address-table")
            macs = device.send_command("show mac address-table dynamic", use_textfsm=True)
            #print(macs)
    
            dfInterface = pd.DataFrame(columns=['Interface Name', 'Mac', 'Desc', 'Members'])
            trunk_index=0
            for mac in macs:
                deviceB_mac = mac['mac']
                vlan = mac['vlan']
                
                deviceB_IP=""
                if (deviceB_mac == dfArp['mac']).any():
                        locindex = dfArp[dfArp['mac']== deviceB_mac].index.item()
                        deviceB_IP = dfArp.loc[locindex,'ip']
                else:
                    print("get IP from firewall")
                                   
                if 'Po' in mac['ports']:
                    deviceA_Trunk = mac['ports']
                    if (deviceA_Trunk == dfInterface['Interface Name']).any():
                        locindex = dfInterface[dfInterface['Interface Name'] == deviceA_Trunk].index.item()
                        deviceA_mac = dfInterface.loc[locindex,'Mac']
                        deviceA_interface_description = dfInterface.loc[locindex, 'Desc']
                        deviceA_interface = dfInterface.loc[locindex, 'Members']
                    else:
                        interface = device.send_command(f"show interface {deviceA_Trunk}", textfsm_template='../ntc-templates/ntc_templates/templates/cisco_nxos_show_interface.textfsm', use_textfsm=True)
                        print(deviceA_Trunk)
                        print(interface)
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
                        
                    if 'INFRA-LINK' in deviceA_interface_description:
                        continue
                    else:
                        
                        splitInter = deviceA_interface.split(',')
                        for split in splitInter:
                            dfObj.loc[index,'Device A Name'] = deviceA_name
                            dfObj.loc[index,'Device A Interface'] = split
                            dfObj.loc[index,'Device A Trunk Name'] = deviceA_Trunk
                            dfObj.loc[index,'Device A IP'] = deviceA_IP
                            dfObj.loc[index,'Device A MAC'] = deviceA_mac
                            dfObj.loc[index,'Device B MAC'] = deviceB_mac
                            dfObj.loc[index,'Device B IP'] = deviceB_IP
                            dfObj.loc[index,'Device A Interface Description'] = deviceA_interface_description
                            dfObj.loc[index,'VLAN-ID'] = vlan
                            obj_in+=1
                else:
                    deviceA_interface = mac['ports']
                    if (deviceA_interface == dfInterface['Interface Name']).any():
                        locindex = dfInterface[dfInterface['Interface Name'] == deviceA_interface].index.item()
                        deviceA_mac = dfInterface.loc[locindex,'Mac']
                        deviceA_interface_description = dfInterface.loc[locindex,'Desc']
                    
                    else:
                        interface = device.send_command(f"show interface {deviceA_interface}", use_textfsm=True)
                        print(deviceA_interface)
                        print(interface)
                        if 'Invalid interface format' in interface:
                            continue
                        deviceA_mac = interface[0]['address']
                        deviceA_interface_description = interface[0]['description']
                        
                        dfInterface.loc[trunk_index,'Interface Name'] = deviceA_interface
                        dfInterface.loc[trunk_index,'Mac'] = interface[0]['address']
                        dfInterface.loc[trunk_index,'Desc'] = interface[0]['description']
                        trunk_index+=1
                        
                    if 'INFRA-LINK' in deviceA_interface_description:
                        continue
                    else:
                        try:
                            dfObj.loc[index,'Device A Name'] = deviceA_name
                            dfObj.loc[index,'Device A Interface'] = deviceA_interface
                            #dfObj.loc[index,'Device A Trunk Name'] = deviceA_Trunk
                            dfObj.loc[index,'Device A IP'] = deviceA_IP
                            dfObj.loc[index,'Device A MAC'] = deviceA_mac
                            dfObj.loc[index,'Device B MAC'] = deviceB_mac
                            dfObj.loc[index,'Device B IP'] = deviceB_IP
                            dfObj.loc[index,'Device A Interface Description'] = deviceA_interface_description
                            dfObj.loc[index,'VLAN-ID'] = vlan
                            obj_in+=1
                        except:
                            print("error writing df")
        
            
        elif host['type'] == 'IOS' or host['type'] == 'IOS-XE':
            try:
                device.send_command("terminal length 0")
            except:
                pass
            
            ##########get all arp
            dfArp = pd.DataFrame(columns=['mac', 'ip'])
            print("getting arp table")
                
            arps = device.send_command("show ip arp", use_textfsm=True)
            i=0
       
            for arp in arps:
                if (arp['mac'] == dfArp['mac']).any():
                    locindex = dfArp[dfArp['mac'] == arp['mac']].index.item()
                    if arp['address'] in dfArp.loc[locindex, 'ip']:
                        continue
                    else:
                        dfArp.loc[locindex, 'ip'] = dfArp.loc[locindex, 'ip']+','+arp['ip_address']
                        
                else:
                    dfArp.loc[i, 'ip'] = arp['address']
                    dfArp.loc[i, 'mac'] = arp['mac']
                    i+=1
                    
            print("getting mac address-table")
            macs = device.send_command("show mac address-table dynamic", use_textfsm=True)
            #print(macs)
    
            dfInterface = pd.DataFrame(columns=['Interface Name', 'Mac', 'Desc', 'Members'])
            trunk_index=0
            for mac in macs:
                deviceB_mac = mac['destination_address']
                vlan = mac['vlan']
                
                deviceB_IP=""
                if (deviceB_mac == dfArp['mac']).any():
                        locindex = dfArp[dfArp['mac']== deviceB_mac].index.item()
                        deviceB_IP = dfArp.loc[locindex,'ip']
                else:
                    print("get IP from firewall")
                                   
                if 'Po' in mac['destination_port']:
                    deviceA_Trunk = mac['destination_port']
                    if (deviceA_Trunk == dfInterface['Interface Name']).any():
                        locindex = dfInterface[dfInterface['Interface Name'] == deviceA_Trunk].index.item()
                        deviceA_mac = dfInterface.loc[locindex,'Mac']
                        deviceA_interface_description = dfInterface.loc[locindex, 'Desc']
                        deviceA_interface = dfInterface.loc[locindex, 'Members']
                    else:
                        interface = device.send_command(f"show interface {deviceA_Trunk}", textfsm_template='C:/Users/HP/Desktop/Mobily NMS/test-repo/flask/app/pullers/ntc-templates/ntc_templates/templates/cisco_nxos_show_interface.textfsm', use_textfsm=True)
                        print(deviceA_Trunk)
                        print(interface)
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
                        
                    if 'INFRA-LINK' in deviceA_interface_description:
                        continue
                    else:
                        
                        splitInter = deviceA_interface.split(',')
                        for split in splitInter:
                            dfObj.loc[index,'Device A Name'] = deviceA_name
                            dfObj.loc[index,'Device A Interface'] = split
                            dfObj.loc[index,'Device A Trunk Name'] = deviceA_Trunk
                            dfObj.loc[index,'Device A IP'] = deviceA_IP
                            dfObj.loc[index,'Device A MAC'] = deviceA_mac
                            dfObj.loc[index,'Device B MAC'] = deviceB_mac
                            dfObj.loc[index,'Device B IP'] = deviceB_IP
                            dfObj.loc[index,'Device A Interface Description'] = deviceA_interface_description
                            dfObj.loc[index,'VLAN-ID'] = vlan
                            obj_in+=1
                else:
                    deviceA_interface = mac['destination_port']
                    if (deviceA_interface == dfInterface['Interface Name']).any():
                        locindex = dfInterface[dfInterface['Interface Name'] == deviceA_interface].index.item()
                        deviceA_mac = dfInterface.loc[locindex,'Mac']
                        deviceA_interface_description = dfInterface.loc[locindex,'Desc']
                    
                    else:
                        interface = device.send_command(f"show interface {deviceA_interface}", use_textfsm=True)
                        print(deviceA_interface)
                        print(interface)
                        if 'Invalid interface format' in interface:
                            continue
                        deviceA_mac = interface[0]['address']
                        deviceA_interface_description = interface[0]['description']
                        
                        dfInterface.loc[trunk_index,'Interface Name'] = deviceA_interface
                        dfInterface.loc[trunk_index,'Mac'] = interface[0]['address']
                        dfInterface.loc[trunk_index,'Desc'] = interface[0]['description']
                        trunk_index+=1
                        
                    if 'INFRA-LINK' in deviceA_interface_description:
                        continue
                    else:
                        try:
                            dfObj.loc[index,'Device A Name'] = deviceA_name
                            dfObj.loc[index,'Device A Interface'] = deviceA_interface
                            #dfObj.loc[index,'Device A Trunk Name'] = deviceA_Trunk
                            dfObj.loc[index,'Device A IP'] = deviceA_IP
                            dfObj.loc[index,'Device A MAC'] = deviceA_mac
                            dfObj.loc[index,'Device B MAC'] = deviceB_mac
                            dfObj.loc[index,'Device B IP'] = deviceB_IP
                            dfObj.loc[index,'Device A Interface Description'] = deviceA_interface_description
                            dfObj.loc[index,'VLAN-ID'] = vlan
                            obj_in+=1
                        except:
                            print("error writing df")
            
writer = pd.ExcelWriter('testNXOS.xlsx', engine='xlsxwriter')
# write dataframe to excel
dfObj.to_excel(writer, sheet_name='MAC-ARP')
writer.save()
print('DataFrame is written successfully to Excel File.')