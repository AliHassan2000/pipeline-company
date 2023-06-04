from logging import exception
import traceback
import requests
import json, sys, re, time
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import urllib3

from aci_mac_address import MacAddressPuller

class LLDPPuller(object):
    
    def __init__(self):
        self.inv_data = {}
        self.cookie = {}
        self.base_url = None
        self.headers = None
        self.failed_devices=[]
    
    def add_to_failed_devices(self, host, reason):
        failed_device= {}
        failed_device["ip_address"]= host
        failed_device["date"]= time.strftime("%d-%m-%Y")
        failed_device["time"]= time.strftime("%H-%M-%S")
        failed_device["reason"]= reason
        self.failed_devices.append(failed_device)
        
    
    def print_failed_devices(self,):
        print("Printing Failed Devices")
        file_name = time.strftime("%d-%m-%Y")+"-LLDP.txt"
        failed_device=[]
        #Read existing file
        try:
            with open('flask/app/failed/ims/'+file_name,'r',encoding='utf-8') as fd:
                failed_device= json.load(fd)
        except:
            pass
        #Update failed devices list    
        failed_device= failed_device+self.failed_devices
        try:
            with open('flask/app/failed/ims/'+file_name, 'w', encoding='utf-8') as fd:
                fd.write(json.dumps(failed_device))
        except Exception as e:
            print(e)
            print("Failed to update failed devices list"+ str(e), file=sys.stderr)

        
    def connectACI(self, host):
        requests.packages.urllib3.disable_warnings()
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        try:
            requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        except AttributeError:
            # no pyopenssl support used / needed / available
            pass
                
        print(f"Connecting to {host['host']}")
        login_tries = 3
        c = 0
        port =443
        is_login = False
        self.base_url = f"https://{host['host']}:{port}"
        while c < login_tries :
            try:
                url = self.base_url+"/api/aaaLogin.json"
                payload = {
                    "aaaUser": {
                        "attributes": {
                            "name": host['user'],
                            "pwd": host['pwd']
                        }
                    }
                }
                self.headers = {'cache-control': "no-cache"}
                response = requests.post(url, data=json.dumps(payload), headers={'Content-Type': "application/json"}, verify=False).json()
                token = response['imdata'][0]['aaaLogin']['attributes']['token']                
                self.cookie['APIC-cookie'] = token
                print(f"Success: logged in {host['host']}")
                is_login = True
                break
            except Exception as e:
                print(e)
                c +=1
    
        return is_login
        
    def get_lldp_data(self, hosts):
        
        for host in hosts:
            login = self.connectACI(host)
            
            if login==False:
                self.inv_data[host['host']] = {"error":"Login Failed"} 
                self.add_to_failed_devices(host['host'], "Failed to login to host")     
                continue
            
            #getting lldp data
            else:
                try:
                    print("getting lldp node data")
                    local_node_data = []
                    
                    lldpIf_url = f'{self.base_url}/api/node/class/lldpIf.json?rsp-subtree=children&rsp-subtree-class=lldpIf,lldpAdjEp&rsp-subtree-include=required&order-by=lldpIf.name|desc'
                    
                    get_response = requests.get(lldpIf_url, headers=self.headers, cookies=self.cookie, verify=False)

                    if get_response.ok:
                        get_response= get_response.json()
                        '''
                        try:
                            with open('flask/app/failed/ims/lldp_data','w',encoding='utf-8') as fd:
                                failed_device= fd.write(json.dumps(get_response))
                        except:
                            pass
            
                        exit()
                        '''
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
                                                                    'description':None,
                                                                    'data_type':"lldp"
                                                                    },
                                                                    'remote':{
                                                                        'system_name':adj['sysName'].replace('.ee.mobily.com.sa',''),
                                                                        'interface':adj['portIdV'],
                                                                        'ip':adj['mgmtIp'],
                                                                        'description':adj['portDesc'],
                                                                        'type':b_type,
                                                                        'mac':adj['chassisIdV']
                                                                    }})
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    self.add_to_failed_devices(host['host'], "Failed to get LLDP data "+str(e))
                    print(f"lldp node data not found {e}", file=sys.stderr)
                    lldpIf = None
                    
                #getting device A Port description
                try:
                    ethpmAggrIf_url = f'{self.base_url}/api/node/class/l1PhysIf.json?&order-by=l1PhysIf.modTs|desc'
                    get_response = requests.get(ethpmAggrIf_url, headers=self.headers, cookies=self.cookie, verify=False)
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
                                    
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    self.add_to_failed_devices(host['host'], "Failed to get Device A port description "+str(e))
                    print(f"error detail =>{e}", file=sys.stderr)
                
                #getting Device A trunk         
                try:
                    ethpmAggrIf_url = f'{self.base_url}/api/node/class/ethpmAggrIf.json?&order-by=ethpmAggrIf.modTs|desc'
                    get_response = requests.get(ethpmAggrIf_url, headers=self.headers, cookies=self.cookie, verify=False)
                
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
                    else:
                        raise Exception(str(get_response.text))                    
                except Exception as e:
                    self.add_to_failed_devices(host['host'], "Failed to get Device A Trunk "+str(e))
                    print(f"error=> {e}", file=sys.stderr)
                    traceback.print_exc()
                
                #getting Device A IP
                try:
                    mgmtRsOoBStNode_url = f'{self.base_url}/api/node/class/mgmtRsOoBStNode.json?&order-by=mgmtRsOoBStNode.modTs|desc'
                    get_response = requests.get(mgmtRsOoBStNode_url, headers=self.headers, cookies=self.cookie, verify=False)
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
                    else:
                        raise Exception(str(get_response.text))                    
                except Exception as e:
                    self.add_to_failed_devices(host['host'], "Failed to get Device A IP "+str(e))
                    print(f"error=> {e}", file=sys.stderr)
                    traceback.print_exc()
                    
                #getting Device A hostname
                try:
                    fabricNode_url = f'{self.base_url}/api/node/class/fabricNode.json?&order-by=fabricNode.modTs|desc'
                    get_response = requests.get(fabricNode_url, headers=self.headers, cookies=self.cookie, verify=False)
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
                    
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    self.add_to_failed_devices(host['host'], "Failed to get Device A Hostname "+str(e))
                    print(f"error=> {e}", file=sys.stderr)     
                    traceback.print_exc()               
                
                try:
                
                    if host['host'] not in self.inv_data:
                        self.inv_data[host['host']] = {}
                    
                    puller = MacAddressPuller()
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
                    self.add_to_failed_devices(host['host'], "Failed to get MAC Address Data "+str(e))
                    print(f"error=> {e}", file=sys.stderr)
                    traceback.print_exc()
                    if host['host'] in self.inv_data:
                        self.inv_data[host['host']].update({'status': 'error'})
                        self.inv_data[host['host']].update({'lldp': []})
            
            return self.inv_data

          
if __name__ == '__main__':
    '''
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
    
    
    hosts = [
        
        {
            "host": "10.83.213.175",
            "user": "srv00047",
            "pwd": "5FPB4!!1c9&g*iJ8"
        }
        ]
    '''
    hosts = [
        
        {
            "host": "10.64.150.4",
            "user": "ciscotac",
            "pwd": "C15c0@mob1ly"
        }
        ]
    

    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = LLDPPuller()
    df = pd.DataFrame()
    # print(json.dumps(puller.get_lldp_data(hosts)))
    res = puller.get_lldp_data(hosts)
    try:
        for x in hosts:
            data = res[x['host']]['lldp']
            for ldp in data:
                local = ldp['local']
                remote = ldp['remote']
                if(local.get('data_type') =="lldp" or (local.get('data_type')=="mac" and  "infra-link" not in local.get('description', "").lower())):
                    df =df.append([{'Device A Name':local.get('hostname',''),'Device A Interface':local.get('interface',''),'Device A Trunk Name':local.get('trunk',''),'Device A IP':local.get('ip',''), 'Device B System Name':remote.get('system_name',''),'Device B Interface':remote.get('interface',''),'Device B IP':remote.get('ip',''),'Device B Type':remote.get('type',''),'Device B Port Description':remote.get('description',''),'Device A MAC':local.get('mac',''),'Device B MAC':remote.get('mac',''),'Device A Port Description':local.get('description', ''),  'VLAN-ID':local.get('vlan') }], ignore_index=True)
    except Exception as e:
        print(f"Failed to add data {e}", file=sys.stderr)
    puller.print_failed_devices()

writer = pd.ExcelWriter('EDN_physical_mapV2.0.xlsx', engine='openpyxl')
df.to_excel(writer, sheet_name='Sheet1', index=False)
writer.save()