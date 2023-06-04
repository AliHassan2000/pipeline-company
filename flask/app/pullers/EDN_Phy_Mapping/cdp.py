from netmiko import Netmiko
from netmiko.ssh_autodetect import SSHDetect
from datetime import datetime
import re, sys, time, json
import threading
import pandas as pd

class IOSPuller(object):
    
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
        print(f"Connecting to {host['host']}")
        login_tries = 3
        c = 0
        is_login = False
        login_exception = None
        sw_type = host['sw_type'].lower()
        sw_type = sw_type.strip()
        
        if sw_type=='ios':
            sw_type = 'cisco_ios'
        elif sw_type=='nx-os':
            sw_type='cisco_nxos'
        elif sw_type=='ios-xe':
            sw_type='cisco_ios'
        else:
            sw_type = ""
            
        while c < login_tries :
            try:
                device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type=sw_type, timeout=600, global_delay_factor=2)
                print(f"Success: logged in {host['host']}")
                is_login = True
                break
            except Exception as e:
                c +=1
                login_exception = str(e)
                
        if is_login==False:
            print(f"Falied to login {host['host']}")
            
        if is_login==True:    
            try:
                cdp_data = []
                print("getting local hostname")
                # device.send_command('terminal len 0')
                # hostname = device.send_command("show running | i hostname")
                # hostname = re.findall(r'hostname\s+(.*)', hostname)
                # local_hostname = hostname[0] 
                local_hostname =host['hostname']
            except:
                print("local hostname not found")
                local_hostname = ''
               
            try:
                print("getting cdp neighbours detail")
               
                output = device.send_command("show cdp neighbors detail", use_textfsm=True)
                
                print(f"CDP data found")
                if isinstance(output,str):
                    print(f"CDP data not found {output} {host['host']}")
                remote_ip_port = {}
                
                for cdp in output:
                    sys_name = cdp['destination_host'].split('.')
                    sys_name = sys_name[0] if sys_name else ''
                    is_ip = remote_ip_port.get(cdp['management_ip'], None)
                    if is_ip:
                        
                        remote_ip_port[cdp['management_ip']]['interfaces'].append(cdp['remote_port'])
                    else:
                        version = cdp.get('software_version') if cdp.get('software_version') else cdp.get('version')
                        remote_ip_port[cdp['management_ip']] = {'interfaces':[cdp['remote_port']], 'version':version}
                    
                    mac_A, desc_A = self.get_mac_desc_A(cdp.get('local_port'), device, sw_type)
                    
                    cdp_data.append({'local':{
                                            'hostname': local_hostname,
                                            'interface':cdp.get('local_port'),
                                            'ip':host['host'],
                                            'mac': mac_A,
                                            'trunk':None,
                                            'desc':desc_A
                                            },
                                            'remote':{
                                                'system_name':sys_name,
                                                'interface':cdp['remote_port'],
                                                'ip':cdp['management_ip'],
                                                'mac':None,
                                                'type':cdp['platform'],
                                                'desc':None,
                                            }})
            except Exception as e:
                print(f"cdp neighbours detail not found {host['host']}")
                cdp = None

            
            if sw_type=='cisco_ios': 
                try:
                    print("show etherchannel summary")
                    gig_type = {'Gi':'GigabitEthernet','Te':'TenGigabitEthernet', 'Eth':'Ethernet'}
                    etherchannel = device.send_command("show etherchannel summary", use_textfsm=True) 
                    print(f"Etherchannel data found")
                    if isinstance(etherchannel,str):
                        print(f"Etherchannel data not found {etherchannel} {host['host']}")
                    for prt in etherchannel:
                        for intf in prt['interfaces']:
                            port =''
                            for key, value in gig_type.items():
                                if key in intf:
                                    port = intf.replace(key, value)
                                    break
                            for cdp in cdp_data:
                                if port==cdp['local']['interface']:
                                    cdp['local'].update({'trunk':prt['po_name']})
                except Exception as e:
                    print(f"show etherchannel summary not found {host['host']}")
                    etherchannel = None
                    
            data = self.get_mac_desc_B(host, remote_ip_port)
            
            for r_ip, value in data.items():
                for z in cdp_data:
                    remote = z['remote']
                    if value.get('output'):
                        for out in value['output']:
                            for r_intf, mac_desc in out.items():
                                if remote['ip']==r_ip and remote['interface']==r_intf:
                                    remote['mac'] = mac_desc['mac']
                                    remote['desc'] = mac_desc['intf_desc']
                    else:
                        break
                    
            
            if sw_type=='cisco_nxos':
                try:
                    print("show port-channel summary")
                    gig_type = {'Gi':'GigabitEthernet','Te':'TenGigabitEthernet', 'Eth':'Ethernet', 'Fa':'FastEthernet'}
                    etherchannel = device.send_command("show port-channel summary", use_textfsm=True) 
                    if isinstance(etherchannel,str):
                        print(f"port-channel summary data not found {etherchannel} {host['host']}")
                    for prt in etherchannel:
                        for intf in prt['phys_iface']:
                            for key, value in gig_type.items():
                                if key in intf:
                                    port = intf.replace(key, value)
                                    break
                            for cdp in cdp_data:
                                if port==cdp['local']['interface']:
                                    cdp['local'].update({'trunk':prt['bundle_iface']})
                except Exception as e:
                    print(f"show port-channel summary not found {host['host']}")
                    etherchannel = None
                    
            
            
            try:
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                self.inv_data[host['host']].update({'cdp': cdp_data})
                self.inv_data[host['host']].update({'status': 'success'})
            except Exception as e:
                print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error', "hostname":host['hostname'], 'ip':host['host'],'sw_type':host['sw_type']})
                    self.inv_data[host['host']].update({'cdp': []})

            if is_login: device.disconnect()
  
    def get_mac_desc_A(self, intf , device, sw_type):
        try:
            time.sleep(2)
            if sw_type=='cisco_nxos':
                cmd = 'show interface '+intf+' | i \(bia|Description'
            if sw_type=='cisco_ios':
                cmd = 'show interfaces '+intf+' | i \(bia|Description'
            print(cmd)
            mac_desc = device.send_command(cmd)
            mac_adr = re.search(r'(address:\s+|address\s+is\s+)([a-zA-Z0-9.]*)', mac_desc)
            mac_adr = mac_adr.group(2) if mac_adr else mac_adr
            desc = re.findall(r'Description:\s+(.*)', mac_desc)
            description = desc[0] if desc else None
            return mac_adr, description
        except Exception  as e:
            print(f"error while getting mac {e}")
            return None, None
    
    def get_mac_desc_B(self, host, remote_ips):
        
        for ip, interfaces in remote_ips.items():
            login_tries = 3
            c = 0
            is_login = False
            print(f"Now connecting to {ip}")
            print(f"device version {remote_ips[ip]['version']}")
            sw_type = remote_ips[ip]['version']
            if 'IOS' in sw_type:
                sw_type = 'cisco_ios'
            elif 'NX-OS' in sw_type:
                sw_type='cisco_nxos'
            elif 'IOS-XE' in sw_type:
                sw_type='cisco_ios'
            else:
                sw_type = ""
                continue
            # print(f"Getting device B Mac and Port description for interfaces {interfaces['interfaces']}")
            
            while c < login_tries :
                try:
                    
                    device = Netmiko(host=ip, username=host['user'], password=host['pwd'], device_type=sw_type, timeout=600, global_delay_factor=2)
                    print(f"Connected : {ip}")
                    is_login = True
                    break
                except Exception as e:
                    c +=1
                    
            if is_login==False:print(f"Device B {ip} Login failed ")
            
            if is_login:
                intf_output = []
                for interface in interfaces['interfaces']:
                    if sw_type=='cisco_nxos':
                        cmd = 'show interface '+interface+' | i \(bia|Description'
                    if sw_type=='cisco_ios':
                        cmd = 'show interfaces '+interface+' | i \(bia|Description'
                    print(cmd)
                    mac_desc = device.send_command(cmd)
                    mac_adr = re.search(r'(address:\s+|address\s+is\s+)([a-zA-Z0-9.]*)', mac_desc)
                    mac_adr = mac_adr.group(2) if mac_adr else None
                    desc = re.findall(r'Description:\s+(.*)', mac_desc)
                    description = desc[0] if desc else None
                    intf_output.append({interface:{'mac':mac_adr,'intf_desc':description}})
                    # print(f"Device B-interface({interface}) mac and desc {mac_adr} {description}")
                device.disconnect()
                remote_ips[ip].update({'output':intf_output})
                
        return remote_ips
            
            
            
if __name__ == '__main__':
    hosts = [
        # {
        #     "host": "10.64.0.5",
        #     "user": "ciscotac",
        #     "pwd": "C15c0@mob1ly",
        #     "sw_type":"IOS"
        # }
        # {
        #     "host": "10.84.1.10",
        #     "user": "ciscotac",
        #     "pwd": "C15c0@mob1ly",
        #     "sw_type":"NX-OS"
        # }
        ]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = IOSPuller()
    # print(json.dumps(puller.get_inventory_data(hosts)))
    df = pd.DataFrame()
    df2 = pd.DataFrame()
    df3 = pd.DataFrame()
    edn_dmz = pd.read_excel(open('EDN_login_failed.xlsx', 'rb'), sheet_name ='Sheet1', dtype=str)
    hosts = []
    for ip , sw_type, hostname in zip(edn_dmz['ip'], edn_dmz['sw_type'], edn_dmz['hostname']):
        host={
            "host": ip,
            "user": "ciscotac",
            "pwd": "C15c0@mob1ly",
            "sw_type":sw_type,
            'hostname':hostname
        }
        hosts.append(host)
        
    res = puller.get_inventory_data(hosts)
    for x in hosts:
        data = res.get(x['host'],{}).get('cdp')
        if data:
            for cdp in data:
                local = cdp['local']
                remote = cdp['remote']
                df =df.append([{'Device A Name':local.get('hostname',''),'Device A Interface':local.get('interface',''),'Device A Trunk Name':local.get('trunk',''),'Device A IP':local.get('ip',''), 'Device B System Name':remote.get('system_name',''),'Device B Interface':remote.get('interface',''),'Device B IP':remote.get('ip',''),'Device B Type':remote.get('type',''),'Device B Port Description':remote.get('desc',''),'Device A MAC':local.get('mac',''),'Device B MAC':remote.get('mac',''), 'Device A Port Description':local.get('desc','')}], ignore_index=True)
    
    print("Writing all data to exel")
    writer = pd.ExcelWriter('EDN_CDP_physical_map_final_V5.0.xlsx', engine='openpyxl')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    
    for x in hosts:
        data = res.get(x['host'],{}).get('error')
        if data:
            df2 = df2.append([res[x['host']]])
            
        status_error = res.get(x['host'],{}).get('status')
        if status_error and status_error=='error':
            df3 = df3.append([res[x['host']]])
            
    writer = pd.ExcelWriter('EDN_login_failed.xlsx', engine='openpyxl')
    df2.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    
    writer = pd.ExcelWriter('EDN_status_error.xlsx', engine='openpyxl')
    df3.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()