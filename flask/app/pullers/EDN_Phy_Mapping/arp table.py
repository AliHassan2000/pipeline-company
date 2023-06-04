# -*- coding: utf-8 -*-
"""
Created on Sun Dec 26 15:28:55 2021

@author: HP
"""

from netmiko import Netmiko
import re, sys, json, time
from time import datetime
import pandas as pd
from pandas import read_excel

dfFW = read_excel('EDN_SEC_IPs_Puller.xlsx', sheet_name = 'SW')

dfArp = pd.DataFrame(columns=['mac', 'ip'])
i=0

host = {
        "host": "",
        "user": "",
        "pwd": "",
        "hostname": "",
        "type": ""
        }

for index, frame in dfFW['FW IP-Address'].iteritems():
    
    host['host'] = frame
    
    if dfFW.loc[index,'OS Type'] == 'IOS':
        host['user'] = 'ciscotac'
        host['pwd'] = 'C15c0@mob1ly'
        host['type'] = 'cisco_ios'
        
    elif dfFW.loc[index,'OS Type'] == 'NX-OS':
        host['user'] = 'ciscotac'
        host['pwd'] = 'C15c0@mob1ly'
        host['type'] = 'cisco_nxos'
        
    elif dfFW.loc[index,'OS Type'] == 'FOS':
        host['user'] = 'srv00280'
        host['pwd'] = '1a3X#eEW3$40vPN%'
        host['type'] = 'fortinet'
        
    elif dfFW.loc[index,'OS Type'] == 'Junos':
        host['user'] = 'srv00280'
        host['pwd'] = '1a3X#eEW3$40vPN%'
        host['type'] = 'juniper_junos'
        
    elif dfFW.loc[index,'OS Type'] == 'ASA':
        host['user'] = 'srv00280'
        host['pwd'] = '1a3X#eEW3$40vPN%'
        host['type'] = 'cisco_asa'

    login_tries = 3
    c = 0
    is_login = False
    login_exception = None
    
    while c < login_tries :
        try:
            print(f"Connectng {host['host']} {host['type']}")
            device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type=host['type'], timeout=800, global_delay_factor=2)
            print(f"Success: logged in {host['host']} at index {index}")
            
            is_login = True
            break
        except Exception as e:
            c +=1
            login_exception= str(e)
    if is_login==False:
        print(f"Falied to login {host['host']} {host['type']}")
        
    if is_login==True:
        
        if host['type'] == 'juniper_junos':
            
                print("getting arp table")
                arps = device.send_command("show arp no-resolve", use_textfsm=True)
                
                #print(arps)
                
                for arp in arps:
                    try:
                        mac_str =  ""
                        strFW = arp['mac'].split(':')
                        for s in strFW:
                            mac_str = mac_str + s
                        if ( mac_str== dfArp['mac']).any():
                            locindex = dfArp[dfArp['mac'] == mac_str].index.item()
                            dfArp.loc[locindex, 'ip'] = dfArp.loc[locindex, 'ip']+','+arp['ip_address']
                        else:
                            dfArp.loc[i, 'ip'] = arp['ip_address']
                            dfArp.loc[i, 'mac'] = mac_str
                            i+=1
                    except:
                        print("Exception")
                        print(arps)
                        
        if host['type'] == 'fortinet':
            
                print("getting arp table")
                config = device.send_config_set(["config vdom",
                                            "edit root"])
                arps = device.send_command("get system arp", use_textfsm=True)
                
                #print(arps)
                
                for arp in arps:
                    try:
                        mac_str =  ""
                        strFW = arp['mac'].split(':')
                        for s in strFW:
                            mac_str = mac_str + s
                        if ( mac_str== dfArp['mac']).any():
                            locindex = dfArp[dfArp['mac'] == mac_str].index.item()
                            dfArp.loc[locindex, 'ip'] = dfArp.loc[locindex, 'ip']+','+arp['address']
                        else:
                            dfArp.loc[i, 'ip'] = arp['address']
                            dfArp.loc[i, 'mac'] = mac_str
                            i+=1
                    except:
                        print("Exception")
                        print(arps)
                        
        if host['type'] == 'cisco_asa':
            
                print("getting arp table")
                arps = device.send_command("show arp", use_textfsm=True)
                
                #print(arps)
                
                for arp in arps:
                    try:
                        mac_str =  ""
                        strFW = arp['mac'].split('.')
                        for s in strFW:
                            mac_str = mac_str + s
                        if ( mac_str== dfArp['mac']).any():
                            locindex = dfArp[dfArp['mac'] == mac_str].index.item()
                            dfArp.loc[locindex, 'ip'] = dfArp.loc[locindex, 'ip']+','+arp['address']
                        else:
                            dfArp.loc[i, 'ip'] = arp['address']
                            dfArp.loc[i, 'mac'] = mac_str
                            i+=1
                    except:
                        print("Exception")
                        print(arps)
                        
        if host['type'] == 'cisco_ios' or host['type'] == 'cisco_nxos':
            
                print("getting arp table")
                len = device.send_command("terminal length 0")
                arps = device.send_command("show ip arp", use_textfsm=True)
                
                #print(arps)
                
                for arp in arps:
                    try:
                        mac_str =  ""
                        strFW = arp['mac'].split('.')
                        for s in strFW:
                            mac_str = mac_str + s
                        if ( mac_str== dfArp['mac']).any():
                            locindex = dfArp[dfArp['mac'] == mac_str].index.item()
                            dfArp.loc[locindex, 'ip'] = dfArp.loc[locindex, 'ip']+','+arp['address']
                        else:
                            dfArp.loc[i, 'ip'] = arp['address']
                            dfArp.loc[i, 'mac'] = mac_str
                            i+=1
                    except:
                        print("Exception")
                        print(arps)
            
writer = pd.ExcelWriter('MAC-ARP.xlsx', engine='xlsxwriter')
# write dataframe to excel
dfArp.to_excel(writer, sheet_name='MAC-ARP')
writer.save()
print('DataFrame is written successfully to Excel File.')