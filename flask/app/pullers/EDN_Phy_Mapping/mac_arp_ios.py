# -*- coding: utf-8 -*-
"""
Created on Fri Dec 24 16:21:14 2021

@author: HP
"""

from netmiko import Netmiko
import re, sys, json,time
import pandas as pd
from time import datetime

def mac_arp_ios(host, que):
    login_tries = 3
    c = 0
    is_login = False
    login_exception = None

    # host = {
    #         "host": "10.64.0.5",
    #         "user": "ciscotac",
    #         "pwd": "C15c0@mob1ly",
    #         "hostname": "RYD-MLG-ENT-GSM-VS1",
    #         "type": "cisco_ios"
    #         }

    deviceA_name = host['hostname']
    deviceA_interface = ""
    deviceA_Trunk = ""
    deviceA_IP = host['host']
    deviceB_IP = ""
    deviceA_mac=""
    deviceB_mac=""
    deviceA_interface_description = ""

    dfObj = pd.DataFrame(columns=['Device A Name', 'Device A Interface', 'Device A Trunk Name',	'Device A IP',	'Device B System Name',	'Device B Interface', 'VLAN-ID',	'Device B IP',	'Device B Type', 'Device B Port Description', 'Device A MAC', 'Device B MAC', 'Device A Interface Description'])
    index=0

    print(f"Connecting {host['host']} {host['type']}")
    while c < login_tries :
        try:
                        
            device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type=host['type'], timeout=800)
            print(f"Success: logged in {host['host']}")
            is_login = True
            break
        except Exception as e:
            c +=1
            login_exception = e
    if is_login==False:
        print(f"Failed to login {host['host']} {host['type']}")
        
    if is_login==True:
        try:
            device.send_command("terminal length 0")
        except:
            pass
        if deviceA_IP:
            ##########get all arp
            dfArp = pd.DataFrame(columns=['mac', 'ip'])
            print("getting arp table")
            
            arps = device.send_command("show ip arp", use_textfsm=True)
            i=0
            for arp in arps:
                if (arp['mac'] == dfArp['mac']).any():
                    continue
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
                # print(mac)
                
                deviceB_mac = mac['destination_address']
                vlan = mac['vlan']
                
                deviceB_IP=""
                if (deviceB_mac == dfArp['mac']).any():
                        locindex = dfArp[dfArp['mac']== deviceB_mac].index.item()
                        deviceB_IP = dfArp.loc[locindex,'ip']
                else:
                    # print("get IP from firewall")
                    pass
                
                        
                if 'Po' in mac['destination_port']:
                    deviceA_Trunk = mac['destination_port']
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
                        
                        splitInter = deviceA_interface.split(' ')
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
                            index+=1
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
                            index+=1
                        except:
                            print("error writing df")
    if is_login: device.disconnect()
    
    que.put(dfObj)
    
    #except:
    #   print("address-table not found")
    #   mac=''
        
# writer = pd.ExcelWriter('sampleIOSEDN.xlsx', engine='xlsxwriter')
# # write dataframe to excel
# dfObj.to_excel(writer, sheet_name='MAC-ARP')
# writer.save()
# print('DataFrame is written successfully to Excel File.')