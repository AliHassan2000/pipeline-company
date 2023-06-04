import threading

import mac_arp_ios
import mac_arp_nxox
from pandas import read_excel
import queue
import pandas as pd

dfFW = read_excel('EDN_NE_IPs_Puller.xlsx', sheet_name = 'EDN_NE')

host = {
        "host": "",
        "user": "",
        "pwd": "",
        "hostname": "",
        "type": ""
        }
threads = []
connections_limit = 15
que = queue.Queue()
dfObj = pd.DataFrame(columns=['Device A Name', 'Device A Interface', 'Device A Trunk Name',	'Device A IP',	'Device B System Name',	'Device B Interface', 'VLAN-ID',	'Device B IP',	'Device B Type', 'Device B Port Description', 'Device A MAC', 'Device B MAC', 'Device A Interface Description'])
for index, ip in dfFW['Switch IP-Address'].iteritems():
    
    host['host'] = ip
    
    if dfFW.loc[index,'sw_type'] == 'IOS' or dfFW.loc[index,'sw_type']=='IOS-XE':
        host['user'] = 'ciscotac'
        host['pwd'] = 'C15c0@mob1ly'
        host['type'] = 'cisco_ios'
        host['hostname'] = dfFW.loc[index,'Switch Name']
        
        th = threading.Thread(target=mac_arp_ios.mac_arp_ios, args=(host, que, dfObj))
        th.start()
        threads.append(th)
        if len(threads) == connections_limit: 
            for t in threads:
                t.join()
            threads =[]
            
    elif dfFW.loc[index,'sw_type'] == 'NX-OS':
        host['user'] = 'ciscotac'
        host['pwd'] = 'C15c0@mob1ly'
        host['type'] = 'cisco_nxos'
        host['hostname'] = dfFW.loc[index,'Switch Name']
        
        th = threading.Thread(target=mac_arp_nxox.mac_arp_nxos, args=(host, que, dfObj))
        th.start()
        threads.append(th)
        
        if len(threads) == connections_limit: 
            for t in threads:
                t.join()
            threads =[]
            
print("Waiting to compelte threads")         
for t in threads: 
    t.join()

# all_dataframes = [] 
# # arp_dataframe = pd.DataFrame()
# while not que.empty():
#     all_dataframes.append(que.get())
    

# arp_dataframe = pd.concat(all_dataframes,ignore_index=True)
print('Writing DataFrame to Excel File.')
writer = pd.ExcelWriter('MAC-ARP-switches.xlsx', engine='xlsxwriter')
# write dataframe to excel
dfObj.to_excel(writer, sheet_name='MAC-ARP')
writer.save()
print('DataFrame is written successfully to Excel File.')
    
    
        
    
    
        
    