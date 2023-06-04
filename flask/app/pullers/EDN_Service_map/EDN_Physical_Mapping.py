# -*- coding: utf-8 -*-
"""
Created on Fri Dec 24 16:21:14 2021

@author: HP
"""

from netmiko import Netmiko
import re, sys, json, time
from time import datetime
import pandas as pd

def MacArp(ip, user, pwd, type, hostname):
    login_tries = 3
    c = 0
    is_login = False
    login_exception = None

    host = {
            "host": ip,
            "user": user,
            "pwd": pwd,
            "hostname": hostname,
            "type":type
            }

    sw_type = host['type'].lower()
    sw_type = sw_type.strip()

    if sw_type=='ios':
        sw_type = 'cisco_ios'
    elif sw_type=='nx-os':
        sw_type='cisco_nxos'
    elif sw_type=='ios-xe':
        sw_type='cisco_ios'
    else:
        sw_type = ""
                
    deviceA_name = host['hostname']
    deviceA_interface = ""
    deviceA_Trunk = ""
    deviceA_IP = host['host']
    deviceB_IP = ""
    deviceA_mac=""
    deviceB_mac=""
    deviceA_interface_description = ""

    dfObj = pd.DataFrame(columns=['Device A Name', 'Device A Interface', 'Device A Trunk Name',	'Device A IP',	'Device B System Name',	'Device B Interface',	'Device B IP',	'Device B Type', 'Device B Port Description', 'Device A MAC', 'Device B MAC', 'Device A Interface Description'])
    index=0


    while c < login_tries :
        try:
                        
            device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type=sw_type, timeout=800)
            print(f"Success: logged in {host['host']}")
            is_login = True
            break
        except Exception as e:
            c +=1
            login_exception = e
    if is_login==False:
        print(f"Falied to login {host['host']}")

    if is_login==True:
        try:
            device.send_command("terminal length 0")
        except:
            pass
        if deviceA_IP:
            print("getting mac address-table")
            macs = device.send_command("show mac address-table dynamic", use_textfsm=True)
            #print(macs)
            dfInterface = pd.DataFrame(columns=['Interface Name', 'Mac', 'Desc', 'Members'])
            trunk_index=0
            for mac in macs:
                deviceB_mac = mac['mac']
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
                            dfObj.loc[index,'Device A Interface Description'] = deviceA_interface_description
                            index+=1
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
                            dfObj.loc[index,'Device A Interface Description'] = deviceA_interface_description
                            index+=1
                        except:
                            print("error writing df")
            
        #except:
        #   print("address-table not found")
        #   mac=''
            
    writer = pd.ExcelWriter('sampleEDN.xlsx', engine='xlsxwriter')
    # write dataframe to excel
    dfObj.to_excel(writer, sheet_name='MAC-ARP')
    writer.save()
    print('DataFrame is written successfully to Excel File.')
    return dfObj
    
    

MacArp('10.64.1.204','ciscotac','C15c0@mob1ly', 'ios','RYD-MLG-ENT-ITD-AC9')