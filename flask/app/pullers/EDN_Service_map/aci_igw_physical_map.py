import requests
import json, sys, re,time
from datetime import datetime
from time import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from ldp_cdp import ACIServicePuller

class ACIPhysicalMapPuller(object):
    
    def __init__(self):
        self.inv_data = {}
    
    def get_lldp_data(self, hosts):
        for host in hosts:
            print(f"Connecting to {host['host']}")
            login_tries = 3
            c = 0
            is_login = False
            port =443
            login_exception = None
            while c < login_tries :
                try:
                    url = f"https://{host['host']}:{port}/api/aaaLogin.json"
                    payload = {
                        "aaaUser": {
                            "attributes": {
                                "name": host['user'],
                                "pwd": host['pwd']
                            }
                        }
                    }
                    headers = {
                        'Content-Type': "application/json"
                    }

                    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False).json()
                    token = response['imdata'][0]['aaaLogin']['attributes']['token']
                    cookie = {}
                    cookie['APIC-cookie'] = token
                    print(f"Success: logged in {host['host']}")
                    is_login = True
                    break
                except Exception as e:
                    c +=1
                    login_exception = e
                    print(f"Falied to login {host['host']}")
                    
            if is_login==False:
                self.inv_data[host['host']] = {"error":"Login Failed"}
                continue
            
            try:
                print("getting lldp node data")
                local_node_data = []
                host_url = f"https://{host['host']}:{port}"
                lldpIf_url = f'{host_url}/api/node/class/lldpIf.json?rsp-subtree=children&rsp-subtree-class=lldpIf,lldpAdjEp&rsp-subtree-include=required&order-by=lldpIf.name|desc'
                headers = {'cache-control': "no-cache"}
                get_response = requests.get(lldpIf_url, headers=headers, cookies=cookie, verify=False)
                if get_response.ok:
                    get_response= get_response.json()
                    imdata = get_response['imdata']
                    if imdata:
                        for x in imdata:
                            lldpIf = x['lldpIf']['attributes']
                            lldpAdjEp = x['lldpIf']['children']
                            node = re.findall(r'paths-(\d+)', lldpIf['portDesc'])
                            node = node[0] if node else None
                            if node:
                                for y in lldpAdjEp:
                                    adj = y['lldpAdjEp']['attributes']
                                    if adj['capability']:
                                        b_type= adj['capability'].replace('bridge,','')
                                    else:
                                        if 'APIC' in  adj['sysName'].replace('.ee.mobily.com.sa',''):
                                            b_type = 'APIC'
                                            
                                    if 'unspecified' not in adj['mgmtIp']:
                                        local_node_data.append({'local':{
                                                                'hostname': 'node-'+node,
                                                                'interface':lldpIf['id'],
                                                                'ip':None,
                                                                'mac':lldpIf['mac'],
                                                                'trunk':None,
                                                                'description':None
                                                                },
                                                                'remote':{
                                                                    'system_name':adj['sysName'].replace('.ee.mobily.com.sa',''),
                                                                    'interface':adj['portIdV'],
                                                                    'ip':adj['mgmtIp'],
                                                                    'description':adj['portDesc'],
                                                                    'type':b_type,
                                                                    'mac':adj['chassisIdV']
                                                                }})
            except Exception as e:
                print(f"lldp node data not found {e}")
                lldpIf = None
                
            #getting device A Port description
            try:
                ethpmAggrIf_url = f'{host_url}/api/node/class/l1PhysIf.json?&order-by=l1PhysIf.modTs|desc'
                get_response = requests.get(ethpmAggrIf_url, headers=headers, cookies=cookie, verify=False)
                if get_response.ok:
                    get_response= get_response.json()
                    imdata = get_response['imdata']
                    if imdata:
                        for l_node in local_node_data:
                            for x in imdata:
                                ethpmAggrIf = x['l1PhysIf']['attributes']
                                ethpm_node = re.findall(r'node-(\d+)', ethpmAggrIf['dn'])
                                ethpm_node = 'node-'+ethpm_node[0] if ethpm_node else None
                                intf = re.findall(r'(eth\d+\/\d+)', ethpmAggrIf['dn'])
                                intf = intf[0].strip() if intf else None
                                
                                if (l_node['local']['interface'].strip()==intf) and (l_node['local']['hostname']==ethpm_node):
                                    l_node['local'].update({'description':ethpmAggrIf['descr']})
                                
            except Exception as e:
                print(f"error detail =>{e}")
                    
            try:
                host_url = f"https://{host['host']}:{port}"
                ethpmAggrIf_url = f'{host_url}/api/node/class/ethpmAggrIf.json?&order-by=ethpmAggrIf.modTs|desc'
                headers = {'cache-control': "no-cache"}
                get_response = requests.get(ethpmAggrIf_url, headers=headers, cookies=cookie, verify=False)
            
                if get_response.ok:
                    get_response= get_response.json()
                    imdata = get_response['imdata']
                    if imdata:
                        for l_node in local_node_data:
                            for x in imdata:
                                ethpmAggrIf = x['ethpmAggrIf']['attributes']
                                ethpm_node = re.findall(r'node-(\d+)', ethpmAggrIf['dn'])
                                ethpm_node = 'node-'+ethpm_node[0] if ethpm_node else None
                                intf = re.findall(r'eth(\d+\/\d+)', ethpmAggrIf['activeMbrs'])
                                interfaces = ['eth'+x for x in intf] 
                                for intf in interfaces:
                                    if (l_node['local']['interface'].strip()==intf) and (l_node['local']['hostname']==ethpm_node):
                                        port_channel = re.findall(r'\[po(\d+)', ethpmAggrIf['dn'])  
                                        port_channel = 'po'+port_channel[0] if port_channel else None
                                        l_node['local'].update({'trunk':port_channel})
                                
            except Exception as e:
                print(f"error=> {e}")
                
            try:
                host_url = f"https://{host['host']}:{port}"
                mgmtRsOoBStNode_url = f'{host_url}/api/node/class/mgmtRsOoBStNode.json?&order-by=mgmtRsOoBStNode.modTs|desc'
                headers = {'cache-control': "no-cache"}
                get_response = requests.get(mgmtRsOoBStNode_url, headers=headers, cookies=cookie, verify=False)
                if get_response.ok:
                    get_response= get_response.json()
                    mgmtRsOoBStNode_imdata = get_response['imdata']
                    if mgmtRsOoBStNode_imdata:
                        for l_node in local_node_data:
                            for x in mgmtRsOoBStNode_imdata:
                                mgmtRsOoBStNode = x['mgmtRsOoBStNode']['attributes']
                                node = re.findall(r'node-(\d+)', mgmtRsOoBStNode['tDn'])  
                                mg_node = 'node-'+node[0] if node else None
                                if mg_node and (mg_node.strip()==l_node['local']['hostname'].strip()):
                                    addr = re.findall(r'(.*)\/', mgmtRsOoBStNode['addr'])
                                    l_node['local'].update({'ip':addr[0]})
            
                
            except Exception as e:
                print(f"error=> {e}")
                
            
            try:
                host_url = f"https://{host['host']}:{port}"
                fabricNode_url = f'{host_url}/api/node/class/fabricNode.json?&order-by=fabricNode.modTs|desc'
                headers = {'cache-control': "no-cache"}
                get_response = requests.get(fabricNode_url, headers=headers, cookies=cookie, verify=False)
                if get_response.ok:
                    get_response= get_response.json()
                    fabricNode_imdata = get_response['imdata']
                    if fabricNode_imdata:
                        for l_node in local_node_data:
                            for x in fabricNode_imdata:
                                fabricNode = x['fabricNode']['attributes']
                                node = re.findall(r'node-(\d+)', fabricNode['dn']) 
                                node = node[0] if node else None
                                if node and (l_node['local']['hostname']=='node-'+node):
                                    l_node['local'].update({'hostname':fabricNode['name']})
                                    
                
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                puller = ACIServicePuller()
                res = puller.get_mac_address_table_data([host])
                data = res[host['host']]['lldp']
                for x in data:
                    for y in local_node_data:
                        if (x['local']['hostname']==y['local']['hostname']) and (x['local']['interface']==y['local']['interface']):
                            x['local'].update({'ip':y['local']['ip']})
                local_node_data.extend(data)
                # local_node_data.extend(mac_data)
                self.inv_data[host['host']].update({'lldp': local_node_data})
                self.inv_data[host['host']].update({'status': 'success'})
            except Exception as e:
                print(f"error=> {e}")
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})
                    self.inv_data[host['host']].update({'lldp': []})
        
        return self.inv_data

          
if __name__ == '__main__':
    hosts = [
        {
            "host": "10.14.106.4",
            "user": "ciscotac",
            "pwd": "C15c0@mob1ly"
        },
        {
            "host": "10.64.150.4",
            "user": "ciscotac",
            "pwd": "C15c0@mob1ly"
        }
        ]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = ACIPhysicalMapPuller()
    df = pd.DataFrame()
    # print(json.dumps(puller.get_lldp_data(hosts)))
    res = puller.get_lldp_data(hosts)
    for x in hosts:
        data = res[x['host']]['lldp']
        for ldp in data:
            local = ldp['local']
            remote = ldp['remote']
            df =df.append([{'Device A Name':local.get('hostname',''),'Device A Interface':local.get('interface',''),'Device A Trunk Name':local.get('trunk',''),'Device A IP':local.get('ip',''), 'Device B System Name':remote.get('system_name',''),'Device B Interface':remote.get('interface',''),'Device B IP':remote.get('ip',''),'Device B Type':remote.get('type',''),'Device B Port Description':remote.get('description',''),'Device A MAC':local.get('mac',''),'Device B MAC':remote.get('mac',''),'Device A Port Description':local.get('description', '')}], ignore_index=True)

print("Writing data to exel")
writer = pd.ExcelWriter('EDN_LLDP_V2.0.xlsx', engine='openpyxl')
df.to_excel(writer, sheet_name='Sheet1', index=False)
writer.save()