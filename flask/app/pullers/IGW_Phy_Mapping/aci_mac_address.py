import traceback
import requests
import json, sys, re, time
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class MacAddressPuller(object):
    
    def __init__(self):
        self.inv_data = {}
        self.failed_devices=[]

    def add_to_failed_devices(self, host, reason):
        failed_device= {}
        failed_device["ip_address"]= host
        failed_device["date"]= time.strftime("%d-%m-%Y")
        failed_device["time"]= time.strftime("%H-%M-%S")
        failed_device["reason"]= reason
        self.failed_devices.append(failed_device)
        
    
    def print_failed_devices(self,):
        file_name = time.strftime("%d-%m-%Y")+"-LLDP.txt"
        failed_device=[]
        #Read existing file
        try:
            with open('flask/app/failed/ims/'+file_name,'r',encoding='utf-8') as fd:
                failed_device= json.load(fd)
        except:
            pass
        #Update failed devices list    
        failed_device.append(self.failed_devices)
        try:
            with open('flask/app/failed/ims/'+file_name, 'w', encoding='utf-8') as fd:
                fd.write(json.dumps(failed_device))
        except Exception as e:
            print(e)
            print("Failed to update failed devices list"+ str(e), file=sys.stderr)

    def get_mac_address_table_data(self, hosts):
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
                    login_exception= str(e)
                    
                    
            if is_login==False:
                self.inv_data[host['host']] = {"error":"Login Failed"}
                print(f"Failed to login {host['host']}", file=sys.stderr)
                self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to login to host" + login_exception)    
                continue
            try:
                print("getting lldp node data")
                ldp_data = []
                host_url = f"https://{host['host']}:{port}"
                
                try:
                    fvCEp_url = f'{host_url}/api/node/class/fvCEp.json?rsp-subtree=children&rsp-subtree-class=fvCEp,fvRsCEpToPathEp&rsp-subtree-include=required&order-by=fvCEp.name|desc'
                    headers = {'cache-control': "no-cache"}
                    get_response = requests.get(fvCEp_url, headers=headers, cookies=cookie, verify=False)
                    if get_response.ok:
                        get_response= get_response.json()
                        imdata = get_response['imdata']
                        

                        for fv in imdata:
                            fvCEp =fv['fvCEp']['attributes']
                            fv_child = fv['fvCEp']['children']
                            for ch in fv_child:
                                fvRsCEp = ch['fvRsCEpToPathEp']['attributes']
                                
                                node_id = re.findall(r'protpaths-(.*)\/', fvRsCEp['rn'])
                                single_node = re.findall(r'paths-(\d+)\/', fvRsCEp['rn'])
                                name = re.findall(r'pathep-\[(.*)\]\]', fvRsCEp['rn'])
                                name = name[0] if name else None
                                node_id = node_id[0] if node_id else None
                                
                                node_ids = node_id.split('-') if node_id else []
                                single_node =single_node[0] if single_node else None
                                if single_node:
                                    ldp_data.append({'local':{'node_id':'node-'+single_node,'pathep':name, 'vlan':fvCEp['encap'], 'data_type':"mac"},'remote':{'ip':fvCEp['ip'],'mac':fvCEp['mac']}})
                                if node_ids:
                                    for nod in node_ids:
                                        ldp_data.append({'local':{'node_id':'node-'+nod,'pathep':name, 'vlan':fvCEp['encap'], 'data_type':"mac"},'remote':{'ip':fvCEp['ip'],'mac':fvCEp['mac']}})
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get LLDP Node Data "+str(e))
                    print(f"error detail =>{e}", file=sys.stderr)
                
                try:
                    host_url = f"https://{host['host']}:{port}"
                    mgmtRsOoBStNode_url = f'{host_url}/api/node/class/mgmtRsOoBStNode.json?&order-by=mgmtRsOoBStNode.modTs|desc'
                    headers = {'cache-control': "no-cache"}
                    get_response = requests.get(mgmtRsOoBStNode_url, headers=headers, cookies=cookie, verify=False)
                    if get_response.ok:
                        get_response= get_response.json()
                        mgmtRsOoBStNode_imdata = get_response['imdata']
                        if mgmtRsOoBStNode_imdata:
                            for l_node in ldp_data:
                                for x in mgmtRsOoBStNode_imdata:
                                    mgmtRsOoBStNode = x['mgmtRsOoBStNode']['attributes']
                                    node = re.findall(r'node-(\d+)', mgmtRsOoBStNode['tDn'])  
                                    mg_node = 'node-'+node[0] if node else None
                                    if mg_node and (mg_node.strip()==l_node['local']['node_id'].strip()):
                                        addr = re.findall(r'(.*)\/', mgmtRsOoBStNode['addr'])
                                        l_node['local'].update({'ip':addr[0]})
                
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get IP Address "+str(e))
                    print(f"error detail =>{e}", file=sys.stderr)
                   
                # getting local hostname
                try:
                    fabricNode_url = f'{host_url}/api/node/class/fabricNode.json?&order-by=fabricNode.modTs|desc'
                    get_response = requests.get(fabricNode_url, headers=headers, cookies=cookie, verify=False)
                    if get_response.ok:
                        get_response= get_response.json()
                        imdata = get_response['imdata']
                        
                        for ldp in ldp_data:
                            local_node = ldp['local']['node_id']
                            for fb in imdata:
                                fbricNode = fb['fabricNode']['attributes']
                                if local_node=='node-'+fbricNode['id']:
                                    ldp['local'].update({'hostname':fbricNode['name']})
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get local hostname "+str(e))
                    print(f"error detail =>{e}", file=sys.stderr)
                
                
                # getting interface
                try:
                    infraHPortS_url = f'{host_url}/api/node/class/infraHPortS.json?rsp-subtree=children&rsp-subtree-class=infraHPortS,infraRsAccBaseGrp,infraPortBlk&rsp-subtree-include=required&order-by=infraHPortS.name|desc'
                    get_response = requests.get(infraHPortS_url, headers=headers, cookies=cookie, verify=False)
                    if get_response.ok:
                        get_response= get_response.json()
                        imdata = get_response['imdata']
                        for ld in ldp_data:
                            if 'eth1' in ld['local']['pathep']:
                                print(f"interfaces = > {ld['local']['pathep']}")
                                ld['local'].update({'interface':ld['local']['pathep']})
                            else:
                                for infra in imdata:
                                    infraHPortS_child = infra['infraHPortS']['children']
                                    for ch in infraHPortS_child:
                                        infraRsAccBaseGrp = ch.get('infraRsAccBaseGrp')
                                        if infraRsAccBaseGrp:
                                            node_name = re.findall(r'uni\/infra\/funcprof\/accportgrp|-(.*)', infraRsAccBaseGrp['attributes']['tDn']) 
                                            node_name = node_name[0] if node_name else None
                                            if node_name and node_name==ld['local']['pathep']:
                                                for blk in infraHPortS_child:
                                                    infraPortBlk = blk.get('infraPortBlk')
                                                    if infraPortBlk:
                                                        fromport = infraPortBlk['attributes']['fromPort']
                                                        toport = infraPortBlk['attributes']['toPort']
                                                        port= ''
                                                        if fromport==toport:
                                                            port = 'eth1/'+fromport
                                                        else:
                                                            port = 'eth1/'+fromport+'-'+toport
                                                        ld['local'].update({'interface':port})
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get Interfaces "+str(e))
                    print(f"error detail =>{e}", file=sys.stderr)
                
                
                # getting Device A Mac
                try:
                    ethpmAggrIf_url = f'{host_url}/api/node/class/ethpmPhysIf.json?&order-by=ethpmPhysIf.modTs|desc'
                    get_response = requests.get(ethpmAggrIf_url, headers=headers, cookies=cookie, verify=False)
                    if get_response.ok:
                        get_response= get_response.json()
                        imdata = get_response['imdata']
                        if imdata:
                            for l_node in ldp_data:
                                for x in imdata:
                                    ethpmAggrIf = x['ethpmPhysIf']['attributes']
                                    ethpm_node = re.findall(r'node-(\d+)', ethpmAggrIf['dn'])
                                    ethpm_node = 'node-'+ethpm_node[0] if ethpm_node else None
                                    intf = re.findall(r'(eth\d+\/\d+)', ethpmAggrIf['dn'])
                                    intf = intf[0].strip() if intf else None
                                    
                                    if (l_node['local']['interface'].strip()==intf) and (l_node['local']['node_id']==ethpm_node):
                                        l_node['local'].update({'mac':ethpmAggrIf['backplaneMac']})
                        else:
                            raise Exception(str(get_response.text))
                except Exception as e:
                    self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get Device A MAC "+str(e))
                    print(f"error detail ==>{e}", file=sys.stderr)

                #getting device A Port description
                try:
                    l1PhysIf_url = f'{host_url}/api/node/class/l1PhysIf.json?&order-by=l1PhysIf.modTs|desc'
                    get_response = requests.get(l1PhysIf_url, headers=headers, cookies=cookie, verify=False)
                    if get_response.ok:
                        get_response= get_response.json()
                        imdata = get_response['imdata']
                        if imdata:
                            for l_node in ldp_data:
                                for x in imdata:
                                    l1PhysIf = x['l1PhysIf']['attributes']
                                    l1PhysIf_node = re.findall(r'node-(\d+)', l1PhysIf['dn'])
                                    l1PhysIf_node = 'node-'+l1PhysIf_node[0] if l1PhysIf_node else None
                                    intf = re.findall(r'(eth\d+\/\d+)', l1PhysIf['dn'])
                                    intf = intf[0].strip() if intf else None
                                    
                                    if (l_node['local']['interface'].strip()==intf) and (l_node['local']['node_id']==l1PhysIf_node):
                                        l_node['local'].update({'description':l1PhysIf['descr']})
                                   
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get Device A port Description "+str(e))
                    print(f"error detail =>{e}", file=sys.stderr)
                    
                # getting trunk
                try:
                    ethpmAggrIf_url = f'{host_url}/api/node/class/ethpmAggrIf.json?&order-by=ethpmAggrIf.modTs|desc'
                    get_response = requests.get(ethpmAggrIf_url, headers=headers, cookies=cookie, verify=False)
                    if get_response.ok:
                        get_response= get_response.json()
                        imdata = get_response['imdata']
                        if imdata:
                            for l_node in ldp_data:
                                for x in imdata:
                                    ethpmAggrIf = x['ethpmAggrIf']['attributes']
                                    ethpm_node = re.findall(r'node-(\d+)', ethpmAggrIf['dn'])
                                    ethpm_node = 'node-'+ethpm_node[0] if ethpm_node else None
                                    intf = re.findall(r'(eth\d+\/\d+)', ethpmAggrIf['activeMbrs'])
                                    interfaces = [x for x in intf] 
                                    port_channel =''
                                    for intf in interfaces:
                                        if (l_node['local']['interface'].strip()==intf) and (l_node['local']['node_id']==ethpm_node):
                                            port_channel = re.findall(r'\[po(\d+)', ethpmAggrIf['dn'])  
                                            port_channel = 'po'+port_channel[0] if port_channel else None
                                            l_node['local'].update({'trunk':port_channel})
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get Device A Trunk "+str(e))
                    print(f"error detail =>{e}", file=sys.stderr)
                
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                self.inv_data[host['host']].update({'lldp': ldp_data})
                self.inv_data[host['host']].update({'status': 'success'})
            except Exception as e:
                self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get Mac address or Interface "+str(e))
                print(f"mac address or interface not found", file=sys.stderr)
                traceback.print_exc()
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})
                    self.inv_data[host['host']].update({'lldp': []})
                    
        # if is_login: device.disconnect()
        return self.inv_data



if __name__ == '__main__':
    hosts = [
        {
            "host": "10.42.211.177",
            "user": "srv00047",
            "pwd": "5FPB4!!1c9&g*iJ9"
        }]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = MacAddressPuller()
    df = pd.DataFrame()
    # print(json.dumps(puller.get_lldp_data(hosts)))
    res = puller.get_address_table_data(hosts)
    for x in hosts:
        data = res[x['host']]['lldp']
        for ldp in data:
            local = ldp['local']
            remote = ldp['remote']
            if "infra-link" not in local.get('description').lower():
                df =df.append([{'Device A Name':local.get('hostname',''),'Device A Interface':local.get('interface',''),'Device A Trunk Name':local.get('trunk',''),'Device A IP':local.get('ip',''), 'Device B System Name':remote.get('system_name',''),'Device B Interface':remote.get('interface',''),'Device B IP':remote.get('ip',''),'Device B Type':'','Device B Port Description':'','Device A MAC':local.get('mac',''),'Device B MAC':remote.get('mac',''), 'Device A Port Description':local.get('description', '')}], ignore_index=True)

    writer = pd.ExcelWriter('IGW_physical_map2.xlsx', engine='openpyxl')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
