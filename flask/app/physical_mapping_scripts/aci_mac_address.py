from tkinter.messagebox import NO
import traceback
import requests
import json, sys, re, time
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
from app.models.inventory_models import FAILED_DEVICES_EDN_LLDP, FAILED_DEVICES_IGW_LLDP, FAILED_DEVICES_EDN_MAC, FAILED_DEVICES_IGW_MAC
from app import db

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class MacAddressPuller(object):
    
    def __init__(self):
        self.inv_data = {}
        self.failed_devices=[]

    # def add_to_failed_devices(self, host, reason):
    #     failed_device= {}
    #     failed_device["ip_address"]= host
    #     failed_device["date"]= time.strftime("%d-%m-%Y")
    #     failed_device["time"]= time.strftime("%H-%M-%S")
    #     failed_device["reason"]= reason
    #     self.failed_devices.append(failed_device)
          
    # def print_failed_devices(self,):
    #     file_name = time.strftime("%d-%m-%Y")+"-LLDP.txt"
    #     failed_device=[]
    #     #Read existing file
    #     try:
    #         with open('app/failed/ims/'+file_name,'r',encoding='utf-8') as fd:
    #             failed_device= json.load(fd)
    #     except:
    #         pass
    #     #Update failed devices list    
    #     failed_device.append(self.failed_devices)
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

    def add_failed_devices_to_db(self, host, reason):

        
        if host["type"]=="EDN-LLDP":
            pmFailedDb = FAILED_DEVICES_EDN_LLDP()
        
        if host["type"]=="EDN-MAC":
            pmFailedDb = FAILED_DEVICES_EDN_MAC()

        if host["type"]== "IGW-MAC":
            pmFailedDb = FAILED_DEVICES_IGW_MAC()

        if host["type"]== "IGW-LLDP":
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

    def get_mac_address_table_data(self, hosts):
        for host in hosts:
           
            print(f"Connecting to {host['host']} from mac script", file=sys.stderr)
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
                    print(f"Success: logged in {host['host']} from mac script", file=sys.stderr)
                    is_login = True
                    break
                except Exception as e:
                    c +=1
                    login_exception= str(e)
                    
                    
            if is_login==False:
                #failedDB
                self.add_failed_devices_to_db(host, f"Failed to Login")
                self.inv_data[host['host']] = {"error":"Login Failed"}
                print(f"Failed to login {host['host']} from mac script", file=sys.stderr)
                #self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to login to host" + login_exception)    
                continue
            try:
                print("getting lldp node data from mac", file=sys.stderr)
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
                                    ldp_data.append({'local':{'node_id':'node-'+single_node,'pathep':name, 'vlan':fvCEp['encap'], 'data_type':"mac"},'remote':{'ip':fvCEp.get('ip'),'mac':fvCEp['mac']}})
                                if node_ids:
                                    for nod in node_ids:
                                        ldp_data.append({'local':{'node_id':'node-'+nod,'pathep':name, 'vlan':fvCEp['encap'], 'data_type':"mac"},'remote':{'ip':fvCEp.get('ip'),'mac':fvCEp['mac']}})
                    
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    #self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get LLDP Node Data "+str(e))
                    print(f"error detail =>{e}", file=sys.stderr)
                    traceback.print_exc()
                
                #Get Remote Ip Address
                #/api/node/class/fvCEp.json?rsp-subtree=children&rsp-subtree-class=fvCEp,fvIp,fvRsCEpToPathEp&rsp-subtree-include=required&order-by=fvCEp.name|desc 
                #Get local IP
                
                try:
                    ## TX URL
                    fvRsPath_url = f'{host_url}/api/node/class/eqptIngrTotalHist5min.json?&order-by=eqptIngrTotalHist5min.modTs|desc'
                    tx_get_response = requests.get(fvRsPath_url, headers=headers, cookies=cookie, verify=False)
                    
                    # RX URL
                    fvRsPath_url = f'{host_url}/api/node/class/eqptEgrTotalHist5min.json?&order-by=eqptEgrTotalHist5min.modTs|desc'
                    rx_get_response = requests.get(fvRsPath_url, headers=headers, cookies=cookie, verify=False)
        
                except Exception as e:
                    pass
                try:
                    print("Getting Local IP OLD API", file=sys.stderr)
                    host_url = f"https://{host['host']}:{port}"
                    mgmtRsOoBStNode_url = f'{host_url}/api/node/class/fvCEp.json?rsp-subtree=children&rsp-subtree-class=fvCEp,fvIp,fvRsCEpToPathEp&rsp-subtree-include=required&order-by=fvCEp.name|desc'
                    headers = {'cache-control': "no-cache"}
                    get_response = requests.get(mgmtRsOoBStNode_url, headers=headers, cookies=cookie, verify=False)
                    if get_response.ok:
                        get_response= get_response.json()
                        imdata = get_response['imdata']
                        
                        for fv in imdata:
                            try: 
                                
                                #print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", file=sys.stderr)
                                #print(f"######## {fvCEp}" , file=sys.stderr)
                                fvCEp =fv['fvCEp']['attributes']
                                fv_child = fv['fvCEp']['children']
                                for ch in fv_child:
                                    if 'fvIp' in ch:
                                        fvRsCEp = ch['fvIp']['attributes']
                                        #print(f"aaaa{ch}", file=sys.stderr)
                                        for l_node in ldp_data:
                                            if l_node['remote']['mac']== fvCEp.get('mac'):
                                                if l_node['remote']['ip'] is None or l_node['remote']['ip']=="" or l_node['remote']['ip']=="0.0.0.0":
                                                    ipAddr= fvRsCEp.get('addr')
                                                    l_node['remote'].update({'ip':ipAddr})
                            except Exception as e: 
                                print("Exception Occured in Updating IP {e]", file=sys.stderr)    
                        
                        # mgmtRsOoBStNode_imdata = get_response['imdata']
                        # print("@@@@@@@@ {}", file=sys.s)
                        # if mgmtRsOoBStNode_imdata:
                        #     for l_node in ldp_data:
                        #         for x in mgmtRsOoBStNode_imdata:
                        #             mgmtRsOoBStNode = x['fvip']['attributes']
                        #             node = re.findall(r'node-(\d+)', mgmtRsOoBStNode['tDn'])  
                        #             mg_node = 'node-'+node[0] if node else None
                        #             if mg_node and (mg_node.strip()==l_node['local']['node_id'].strip()):
                        #                 addr = re.findall(r'(.*)\/', mgmtRsOoBStNode['addr'])
                        #                 l_node['local'].update({'ip':addr[0]})
                        
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    #self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get IP Address "+str(e))
                    print(f"error detail =>{e}", file=sys.stderr)
                    traceback.print_exc()
                

                
                #Get local IP
                try:
                    print("Getting Local IP New IP", file=sys.stderr)
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
                    #self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get IP Address "+str(e))
                    print(f"error detail =>{e}", file=sys.stderr)
                    traceback.print_exc()
                
                # getting local hostname
                print("Getting Local Host Name", file=sys.stderr)
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
                    #self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get local hostname "+str(e))
                    print(f"error detail =>{e}", file=sys.stderr)
                    traceback.print_exc()
                

                # getting interface
                try:
                    print("Getting Local Interface", file=sys.stderr)
                    infraHPortS_url = f'{host_url}/api/node/class/infraHPortS.json?rsp-subtree=children&rsp-subtree-class=infraHPortS,infraRsAccBaseGrp,infraPortBlk&rsp-subtree-include=required&order-by=infraHPortS.name|desc'
                    get_response = requests.get(infraHPortS_url, headers=headers, cookies=cookie, verify=False)
                    if get_response.ok:
                        get_response= get_response.json()
                        imdata = get_response['imdata']
                        #print(f"@@  {imdata}", file=sys.stderr)
                        for ld in ldp_data:
                            if 'eth1' in ld['local']['pathep']:
                                #print(f"interfaces = > {ld['local']['pathep']}", file=sys.stderr)
                                ld['local'].update({'interface':ld['local']['pathep']})
                            else:
                                for infra in imdata:
                                    #print("DDDDDDDDDDDDDDDDDDDDDDD", file=sys.stderr)
                                    infraHPortS_child = infra['infraHPortS']['children']
                                    for ch in infraHPortS_child:
                                        infraRsAccBaseGrp = ch.get('infraRsAccBaseGrp')
                                        if infraRsAccBaseGrp:
                                            #if str(infraRsAccBaseGrp['attributes']['tDn'])== "uni/infra/funcprof/accbundle-NOKIA_GEOLOCATION_LF303-P7_LF304-P21_VPC":
                                                node_name = re.findall(r'uni\/infra\/funcprof\/accportgrp|-(.*)', infraRsAccBaseGrp['attributes']['tDn']) 
                                                #print(f"@@@ {node_name}", file=sys.stderr)
                                                node_name = node_name[0] if node_name else None
                                                node_id= re.findall(r'Profile-(\d+)', infra['infraHPortS']['attributes']['dn'])
                                                node_id= node_id[0] if node_id else None
                                                node_id= f"node-{node_id}"
                                                #print(f"2222 {node_name}", file=sys.stderr)
                                                if node_name and node_name==ld['local']['pathep'] and ld['local']['node_id']== node_id:
                                                    for blk in infraHPortS_child:
                                                        infraPortBlk = blk.get('infraPortBlk')
                                                        #print(f"3333 {infraPortBlk}", file=sys.stderr)
                                                        if infraPortBlk:
                                                            fromport = infraPortBlk['attributes']['fromPort']
                                                            toport = infraPortBlk['attributes']['toPort']
                                                            port= ''
                                                            if fromport==toport:
                                                                port = 'eth1/'+fromport
                                                            else:
                                                                port = 'eth1/'+fromport+'-'+toport
                                                            #print(f"444 {port}", file=sys.stderr)
                                                            ld['local'].update({'interface':port})
                                                            # if ld['remote']['mac']== 'F4:03:43:53:8E:28':
                                                            #     print("#######################", file=sys.stderr)
                                                            #     print(f"TDN is: {infraRsAccBaseGrp['attributes']['tDn']}", file=sys.stderr)
                                                            #     print(f"Node is {node_name}", file=sys.stderr)
                                                            #     print(f"Port is {port}", file=sys.stderr)
                                                            #     print(ld, file=sys.stderr)
                                                            #     print("%%%%%%%%%%%%%%%%%%%%%%%%%", file=sys.stderr)
                                                            
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    #self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get Interfaces "+str(e))
                    print(f"error detail =>{e}", file=sys.stderr)
                    traceback.print_exc()

    
                # getting Device A Mac
                print("Getting Device A MAC", file=sys.stderr)
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
                                    
                                    inter=l_node['local']['interface'].strip()
                                    int1=""
                                    int2="eth1/"
                                    int= inter.split('-')
                                    int1= int[0]
                                    if len(int)>1:
                                        int2+=int[1]


                                    if (intf == int1 or intf== int2) and (l_node['local']['node_id']==ethpm_node):
                                        l_node['local'].update({'mac':ethpmAggrIf['backplaneMac']})
                                        
                        else:
                            raise Exception(str(get_response.text))
                except Exception as e:
                    #self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get Device A MAC "+str(e))
                    print(f"error detail ==>{e}", file=sys.stderr)
                    traceback.print_exc()

                #getting device A Port description
                try:
                    print("Getting LDevie A Port Descriptin", file=sys.stderr)
                    print("Getting Device A Port Descriptions", file=sys.stderr)
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

                                    inter=l_node['local']['interface'].strip()
                                    int1=""
                                    int2="eth1/"
                                    int= inter.split('-')
                                    int1= int[0]
                                    if len(int)>1:
                                        int2+=int[1]

                                    
                                    if (intf == int1 or intf==int2) and (l_node['local']['node_id']==l1PhysIf_node):
                                        l_node['local'].update({'description':l1PhysIf['descr']})

                                        # if l_node['remote']['mac']== 'F4:03:43:53:8E:28':
                                        #     print("######### In Device A Port Desc ##############", file=sys.stderr)
                                        #     #print(f"TDN is: {infraRsAccBaseGrp['attributes']['tDn']}", file=sys.stderr)
                                        #     #print(f"Node is {node_name}", file=sys.stderr)
                                        #     print(f"Node Int is {l_node['local']['interface'].strip()}", file=sys.stderr)
                                        #     print(f"Int is  {intf}", file=sys.stderr)
                                        #     print(l_node, file=sys.stderr)
                                        #     print("%%%%%%%%%%%%%%%%%%%%%%%%%", file=sys.stderr)
                                   
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    #self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get Device A port Description "+str(e))
                    print(f"error detail =>{e}", file=sys.stderr)
                    traceback.print_exc()

                
                # getting trunk
                try:
                    print("Getting Trunk", file=sys.stderr)
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
                                        inter=l_node['local']['interface'].strip()
                                        int1=""
                                        int2="eth1/"
                                        int= inter.split('-')
                                        int1= int[0]
                                        if len(int)>1:
                                            int2+=int[1]

                                        if (intf == int1 or intf==int2) and (l_node['local']['node_id']==ethpm_node):
                                            port_channel = re.findall(r'\[po(\d+)', ethpmAggrIf['dn'])  
                                            port_channel = 'po'+port_channel[0] if port_channel else None
                                            l_node['local'].update({'trunk':port_channel})

                                            # if l_node['remote']['mac']== 'F4:03:43:53:8E:28':
                                            #     print("######### In Device A Port Channel ##############", file=sys.stderr)
                                            #     #print(f"TDN is: {infraRsAccBaseGrp['attributes']['tDn']}", file=sys.stderr)
                                            #     #print(f"Node is {node_name}", file=sys.stderr)
                                            #     #print(f"Port is {port}", file=sys.stderr)
                                            #     print(l_node, file=sys.stderr)
                                            #     print("%%%%%%%%%%%%%%%%%%%%%%%%%", file=sys.stderr)
                                    
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    #self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get Device A Trunk "+str(e))
                    print(f"error detail =>{e}", file=sys.stderr)
                    traceback.print_exc()
                
                # getting vlan name/epg
                try:
                    print("Getting VLAN Names", file=sys.stderr)
                    fvRsPath_url = f'{host_url}/api/node/class/fvRsPathAtt.json?&order-by=fvRsPathAtt.modTs|desc'
                    get_response = requests.get(fvRsPath_url, headers=headers, cookies=cookie, verify=False)
                    if get_response.ok:
                        get_response= get_response.json()
                        imdata = get_response['imdata']
                        if imdata:                            
                            for l_node in ldp_data:
                                for x in imdata:
                                    fvRsPathAtt = x['fvRsPathAtt']['attributes']
                                    ethpm_node = re.findall(r'paths-(\d+)', fvRsPathAtt['dn'])
                                    ethpm_node = 'node-'+ethpm_node[0] if fvRsPathAtt else None

                                    node_name = re.findall(r'pathep-\[(.*)\]', fvRsPathAtt['tDn']) 
                                    #print(f"@@@ {node_name}", file=sys.stderr)
                                    node_name = node_name[0] if node_name else None
                                    
                                    if (l_node['local']['vlan']==fvRsPathAtt.get('encap')) and  (l_node['local']['pathep']==node_name):  #(l_node['local']['node_id']==ethpm_node):
                                        description= fvRsPathAtt['dn'].split('/')
                                        description=description[3]
                                        l_node['local'].update({'vlan_name':description})

                                        # if l_node['remote']['mac']== 'F4:03:43:53:8E:28':
                                        #     print("######### In Device A Port Vlan ##############", file=sys.stderr)
                                        #     #print(f"TDN is: {infraRsAccBaseGrp['attributes']['tDn']}", file=sys.stderr)
                                        #     #print(f"Node is {node_name}", file=sys.stderr)
                                        #     #print(f"Port is {port}", file=sys.stderr)
                                        #     print(l_node, file=sys.stderr)
                                        #     print("%%%%%%%%%%%%%%%%%%%%%%%%%", file=sys.stderr)
                                
                                
                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    #self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get Device A Vlan Name "+str(e))
                    print(f"VLan Nameerror detail =>{e}", file=sys.stderr)
                    traceback.print_exc()
                #f9.write(str(ldp_data))

                
                try:
                    print("Getting TX Bandwidth", file=sys.stderr)
                    
                    if tx_get_response.ok:
                        get_response= tx_get_response.json()
                        imdata = get_response['imdata']
                        #print(imdata, file=sys.stderr)
                        if imdata:                            
                            for l_node in ldp_data:
                                for x in imdata:
                                    fvRsPathAtt = x['eqptIngrTotalHist5min']['attributes']
                                    
                                    ethpm_node = re.findall(r'node-(\d+)', fvRsPathAtt['dn'])
                                    ethpm_node = 'node-'+ethpm_node[0] if ethpm_node else None

                                    intf = re.findall(r'(eth\d+\/\d+)', fvRsPathAtt['dn'])
                                    intf = intf[0].strip() if intf else None

                                    port_channel = re.findall(r'\[po(\d+)', fvRsPathAtt['dn'])  
                                    port_channel = 'po'+port_channel[0] if port_channel else None
                                   
                                    if '-' not in l_node['local']['interface'] :
                                        if (l_node['local']['interface'] == intf) and (l_node['local']['node_id']==ethpm_node):
                                            l_node['local'].update({'device_a_tx': fvRsPathAtt['bytesRate']})
                                    else:
                                        if (l_node['local']['trunk'] == port_channel) and (l_node['local']['node_id']==ethpm_node):
                                            l_node['local'].update({'device_a_tx': fvRsPathAtt['bytesRate']})

                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    #self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get Device A Vlan Name "+str(e))
                    print(f"Bandwidth TX Error detail =>{e}", file=sys.stderr)
                    traceback.print_exc()


                try:
                    print("Getting RX Bandwidth", file=sys.stderr)
                    
                    if rx_get_response.ok:
                        get_response= rx_get_response.json()
                        imdata = get_response['imdata']
                        #print(imdata, file=sys.stderr)
                        if imdata:                            
                            for l_node in ldp_data:
                                for x in imdata:
                                    fvRsPathAtt = x['eqptEgrTotalHist5min']['attributes']
                                    
                                    ethpm_node = re.findall(r'node-(\d+)', fvRsPathAtt['dn'])
                                    ethpm_node = 'node-'+ethpm_node[0] if ethpm_node else None

                                    intf = re.findall(r'(eth\d+\/\d+)', fvRsPathAtt['dn'])
                                    intf = intf[0].strip() if intf else None

                                    port_channel = re.findall(r'\[po(\d+)', fvRsPathAtt['dn'])  
                                    port_channel = 'po'+port_channel[0] if port_channel else None
                                   
                                    if '-' not in l_node['local']['interface'] :
                                        if (l_node['local']['interface'] == intf) and (l_node['local']['node_id']==ethpm_node):
                                            l_node['local'].update({'device_a_rx': fvRsPathAtt['bytesRate']})
                                    else:
                                        if (l_node['local']['trunk'] == port_channel) and (l_node['local']['node_id']==ethpm_node):
                                            l_node['local'].update({'device_a_rx': fvRsPathAtt['bytesRate']})

                    else:
                        raise Exception(str(get_response.text))
                except Exception as e:
                    #self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get Device A Vlan Name "+str(e))
                    print(f"Bandwidth RX Error detail =>{e}", file=sys.stderr)
                    traceback.print_exc()


                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                self.inv_data[host['host']].update({'lldp': ldp_data})
                self.inv_data[host['host']].update({'status': 'success'})

            

            except Exception as e:
                #failedDB
                self.add_failed_devices_to_db(host, f"Error Occured when getting MAC ACI data {e}")

                ###self.add_to_failed_devices(host['host'], "(LLDP MAC) Failed to get Mac address or Interface "+str(e))
                print(f"mac address or interface not found", file=sys.stderr)
                traceback.print_exc()
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})
                    self.inv_data[host['host']].update({'lldp': []})
                    
        # if is_login: device.disconnect()
        #self.print_failed_devices()
        return self.inv_data