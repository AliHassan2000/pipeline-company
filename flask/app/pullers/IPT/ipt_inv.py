from datetime import datetime
import re, sys, time, json
import threading
from pysnmp.hlapi import *


class IPTPuller(object):
    
    def __init__(self):
        self.inv_data = {}
        self.connections_limit = 50

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
            return self.inv_data
        

    def poll(self, host):
        print(host, file=sys.stderr)
        print(f"Connecting to {host['host']}", file=sys.stderr)
        try:
            engn = SnmpEngine()
            community = UsmUserData(host['user'], host['pwd'], host['auth-key'], authProtocol=usmHMACSHAAuthProtocol, privProtocol=usmAesCfb128Protocol)# snmp community
            transport = UdpTransportTarget((host['host'], 161))
            cnxt = ContextData()
            print(f"Connected {host['host']}", file=sys.stderr)
            
            
            oids = {
                    'hostname':{'oid':'iso.3.6.1.2.1.1.5.0'},
                    'descr':{'oid':'iso.3.6.1.2.1.47.1.1.1.1.2.1'},
                    'pid':{'oid':'iso.3.6.1.2.1.47.1.1.1.1.13.1'},
                    'serial':{'oid':'iso.3.6.1.2.1.47.1.1.1.1.11.1'},
                    'vendor':{'oid':'iso.3.6.1.2.1.47.1.1.1.1.12.1'},
                    'version':{'oid':'iso.3.6.1.4.1.6876.1.2.0'},
                    'vms_hostname':{'oid':'iso.3.6.1.4.1.6876.2.1.1.2.'},
                    'software':{}
                    }
            
            
            functions = [{'func':'Unity Connection','oid':'iso.3.6.1.4.1.9.9.385.1.1.1.1.3.0'}]
            
            
            for key, value in oids.items():
                oid = oids[key].get('oid')
                if not oid:continue 
                print(f"Sending command {oids[key]} = {oid}", file=sys.stderr)
                if key=='vms_hostname':
                    print("Fetching VMs deatil..", file=sys.stderr)
                    data = self.get_Vms(engn, community, transport, cnxt, oid)
                    print(data, file=sys.stderr)
                    oids[key].update({'value':data})
                               
                else:
                    data = self.get_oid_data(engn, community, transport, cnxt, oid)
                    oids[key].update({'value':data})
                    
            
            print(f"oids data is {oids}", file=sys.stderr)
            for vm_name in oids['vms_hostname']['value']:
                for x in host['ipt-list']:
                    vm_name = vm_name.split('.')[0]
                    if x['device_name'].strip() in vm_name.strip():
                        for f in functions:                 #if vm exist in ipt list then get sofware version 
                            if x['function']==f['func']:
                                data = self.get_software_version_from_node(host, x['ip'], f['oid'])
                                oids['software'].update({'value':data})
                                break
                            
                        self.add_inventory_data(x['ip'], oids)
                        oids['software'].update({'value':None})  # update the software that host will not take the node software version
            
            else:
                self.add_inventory_data(host['host'], oids)
        
                
            print("IPT data is below", file=sys.stderr)
            print(f"{self.inv_data}", file=sys.stderr)
            self.inv_data[host['host']].update({'status': 'success'})
        except Exception as e:
            print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
            if host['host'] in self.inv_data:
                self.inv_data[host['host']].update({'status': 'error'})
            file_name = time.strftime("%d-%m-%Y")+".txt"
            failed_device=[]
            #Read existing file
            try:
                with open('app/failed/ims/'+file_name,'r', encoding='utf-8') as fd:
                    failed_device= json.load(fd)
            except:
                print("Failed devices list is empty", file=sys.stderr)
                pass
            #Update failed devices list
            
            failed_device.append({"ip_address": host['host'],"date":  time.strftime("%d-%m-%Y"), "time": time.strftime("%H-%M-%S"), "reason":str(e)})
            try:
                with open('app/failed/ims/'+file_name, 'w', encoding='utf-8') as fd:
                    fd.write(json.dumps(failed_device))
            except Exception as e:
                print(e)
                print("Failed to update failed devices list", file=sys.stderr)
            
    
    def add_inventory_data(self, ip ,inv):
        if ip not in self.inv_data:
                self.inv_data[ip] = {}
                
        self.inv_data[ip].update({'device':
                                {'ip_addr': ip, 
                                'serial_number': inv['serial']['value'], 
                                'pn_code': inv['pid']['value'], 
                                'hw_version': inv['version']['value'], 
                                "software_version": inv.get('software',{}).get('value'), 
                                "desc": inv['descr']['value'], 
                                "max_power": None, 
                                "manufecturer": inv['vendor']['value'],
                                "patch_version":None,
                                "status": "production", 
                                "authentication": "AAA"},
                                'board':[],
                                'sub_board':[],
                                'sfp':[],
                                'license':[],
                                'status':'success'})
        

    def get_Vms(self, engn, community, transport, cnxt, vm_oid):
        vms_hostname = []
        try:
            for x in range(1, 50):
                oid = ObjectType(ObjectIdentity(vm_oid+str(x)))
                errorIndication, errorStatus, errorIndex, varBinds = next(
                    getCmd(engn, community, transport, cnxt, oid, ))
                login = ''
                if errorIndication:
                    print(f'Login failed:: error=>{errorIndication}')
                    login='fail'
                elif errorStatus:
                    print('%s at %s' % (errorStatus.prettyPrint(),
                                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))

                else:
                    for varBind in varBinds:
                        res = ' = '.join([x.prettyPrint() for x in varBind])
                        # print(res)
                        if 'No Such Instance' not in res:
                            vms_hostname.append(res.split('=')[1].strip())
                            
            # print(vms_hostname)
            return vms_hostname
        except Exception as e:
            return vms_hostname
        
    def get_oid_data(self, engn, community, transport, cnxt, oid):
        oid = ObjectType(ObjectIdentity(oid))
                
        errorIndication, errorStatus, errorIndex, varBinds = next(getCmd(engn, community, transport, cnxt, oid, ))

        if errorIndication:
            print(f'error=>{errorIndication}')
            
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            for varBind in varBinds:
                res = ' = '.join([x.prettyPrint() for x in varBind])
                if 'No Such Instance' not in res:
                    res = res.split('=')[1].strip()
                    return res
                else:
                    return None
 
    def get_software_version_from_node(self,host,node_ip, oid):
        try:
            print(f"Connecting to node {node_ip}")
            engn = SnmpEngine()
            community = UsmUserData(host['user'], host['pwd'], host['auth-key'], authProtocol=usmHMACSHAAuthProtocol, privProtocol=usmAesCfb128Protocol)# snmp community
            transport = UdpTransportTarget((node_ip, 161))
            cnxt = ContextData()
            print(f"Connected {node_ip}", file=sys.stderr)
            print(f"getting node version" , file=sys.stderr)
            data = self.get_oid_data(engn, community, transport, cnxt, oid)
            return data
        except Exception:
            print("Error while getting node version")
            return None
        
if __name__ == '__main__':
    hosts = [{
            'host':'10.42.158.28',
            'user':'SWV3',
            'pwd':'snM9v3m08',
            'auth-key':'3Nt56m08',
            'ipt-list':[{
                'ip':'10.42.158.4',
                'device_name':'DAM-ADM-IPT-SUB5',
                'function':'Call Manager'},
                        {
                'ip':'10.42.158.5',
                'device_name':'DAM-ADM-IPT-IMSUB4',
                'function':'IM and Presence'},
                        {'ip':'10.42.158.6',
                         'device_name':'DAM-ADM-IPT-PCP2',
                         'function':'Prime Provisioning'}
            ]
        }]
    
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = IPTPuller()
    print(json.dumps(puller.get_inventory_data(hosts)))
    
    