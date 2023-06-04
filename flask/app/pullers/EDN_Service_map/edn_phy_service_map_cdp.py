from netmiko import Netmiko
from netmiko.ssh_autodetect import SSHDetect
from datetime import datetime
import re, sys, time, json
import threading
import pandas as pd

class IOSPuller(object):
    
    def __init__(self):
        self.inv_data = {}
        self.connections_limit = 10

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
        sw_type = host['sw_type'].lower()
        sw_type = sw_type.strip()
        login_exception = None
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
                print(f"Falied to login {host['host']}")
                login_exception = e
        if is_login==False:
            self.inv_data[host['host']] = {"error":"Login Failed"}
            
        if is_login==True:    
            try:
                cdp_data = []
                print("getting local hostname")
                device.send_command('terminal len 0')
                hostname = device.send_command("show running | i hostname")
                hostname = re.findall(r'hostname\s+(.*)', hostname)
                local_hostname = hostname[0] 
            except:
                print("local hostname not found")
                local_hostname = ''
               
            try:
                print("getting cdp neighbours detail")
                output = device.send_command("show cdp neighbors detail", use_textfsm=True)
                print(f"CDP data =>{output}")
                remote_ip_port = {}
                
                for cdp in output:
                    sys_name = cdp['destination_host'].split('.')
                    sys_name = sys_name[0] if sys_name else ''
                    is_ip = remote_ip_port.get(cdp['management_ip'], None)
                    if is_ip:
                        remote_ip_port[cdp['management_ip']]['interfaces'].append(cdp['remote_port'])
                    else:
                        remote_ip_port[cdp['management_ip']] = {'interfaces':[cdp['remote_port']], 'version':cdp['software_version']}
                        
                        
                    cdp_data.append({'local':{
                                            'hostname': local_hostname,
                                            'interface':cdp.get('local_port'),
                                            'ip':host['host'],
                                            'mac': self.get_mac(cdp.get('local_port'), device),
                                            'trunk':None,
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
                print(f"cdp neighbours detail not found {e} {host['host']}")
                cdp = None

            
            if sw_type=='cisco_ios': 
                try:
                    print("show etherchannel summary")
                    gig_type = {'Gi':'GigabitEthernet','Te':'TenGigabitEthernet', 'Eth':'Ethernet'}
                    etherchannel = device.send_command("show etherchannel summary", use_textfsm=True) 
                    print(f"Etherchannel data => {etherchannel}")
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
                    print("show etherchannel summary not found")
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
                
            # try:
            #     print("show ip interface breif")
            #     breif = device.send_command("show ip interface brief", use_textfsm=True) 
            #     for cdp in cdp_data:
            #         for br in breif:
            #             if br['intf']==cdp['local']['interface']:
            #                 cdp['local'].update({'ip':br['ipaddr']})
            #             # else:
            #             #     cdp['local'].update({'ip':host['host']})
            # except Exception as e:
            #     print("show ip interface breif not found")
            #     breif = None
            
            
            # try:
            #     print("show ip arp")
                
            #     arp = device.send_command("show ip arp", use_textfsm=True) 
            #     for cdp in cdp_data:
            #         for ar in arp:
            #             if cdp['local']['interface']==ar['interface']:
            #                 cdp['local'].update({'mac':ar['mac']})
            #             if cdp['remote']['interface']==ar['interface']:
            #                 cdp['remote'].update({'mac':ar['mac']})
            # except Exception as e:
            #     print(f"show ip arp not found {host['host']}")
            #     arp = None
            
            # if sw_type=='cisco_nxos':
            #     try:
            #         print("show port-channel summary")
            #         gig_type = {'Gi':'GigabitEthernet','Te':'TenGigabitEthernet', 'Eth':'Ethernet'}
            #         etherchannel = device.send_command("show port-channel summary", use_textfsm=True) 
            #         for prt in etherchannel:
            #             for intf in prt['phys_iface']:
            #                 for key, value in gig_type.items():
            #                     if key in intf:
            #                         port = intf.replace(key, value)
            #                         break
            #                 for cdp in cdp_data:
            #                     if port==cdp['local']['interface']:
            #                         cdp['local'].update({'trunk':prt['bundle_iface']})
            #     except Exception as e:
            #         print("show port-channel summary not found")
            #         etherchannel = None
                    
            
            
            try:
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                self.inv_data[host['host']].update({'cdp': cdp_data})
                self.inv_data[host['host']].update({'status': 'success'})
            except Exception as e:
                print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})
                    self.inv_data[host['host']].update({'cdp': []})

            if is_login: device.disconnect()
  
    def get_mac(self, intf , device):
        try:
            time.sleep(2)
            print(f'send command {"show interface "+intf+" | i Hardware"}')
            mac = device.send_command('show interface '+intf+' | i \(bia')
            print(f'mac output {mac}')
            mac_adr = re.findall(r'address\s+is\s+([a-zA-Z0-9.]*)', mac)
            mac_adr = mac_adr[0] if mac_adr else None
            print(f'grabbed mac is {mac_adr}')
            return mac_adr
        except Exception  as e:
            print(f"error while getting mac {e}")
            return None
    
    def get_mac_desc_B(self, host, remote_ips):
        
        for ip, interfaces in remote_ips.items():
            login_tries = 3
            c = 0
            is_login = False
            sw_type = remote_ips[ip]['version']
            if 'IOS' in sw_type:
                sw_type = 'cisco_ios'
            elif 'NXOS' in sw_type:
                sw_type='cisco_nxos'
            elif 'IOS XE' in sw_type:
                sw_type='cisco_ios'
            else:
                sw_type = ""
                continue
            print(f"Now connecting to {ip}")
            
            while c < login_tries :
                try:
                    
                    device = Netmiko(host=ip, username=host['user'], password=host['pwd'], device_type=sw_type, timeout=600, global_delay_factor=2)
                    print(f"Connected : {ip}")
                    is_login = True
                    break
                except Exception as e:
                    c +=1
            if is_login:
                intf_output = []
                for interface in interfaces['interfaces']:
                    print(f"show interfaces {interface} | i \(bia | Description")
                    mac_desc = device.send_command('show interfaces '+interface+' | i \(bia | Description')
                    mac_adr = re.findall(r'address\s+is\s+([a-zA-Z0-9.]*)', mac_desc)
                    mac_adr = mac_adr[0] if mac_adr else None
                    desc = re.findall(r'Description:\s+(.*)', mac_desc)
                    description = desc[0] if desc else None
                    intf_output.append({interface:{'mac':mac_adr,'intf_desc':description}})
                device.disconnect()
                remote_ips[ip].update({'output':intf_output})
                
        return remote_ips
            
            
            
if __name__ == '__main__':
    hosts = [
        # {
        #     "host": "10.83.90.6",
        #     "user": "ciscotac",
        #     "pwd": "C15c0@mob1ly",
        #     "sw_type":"NX-OS"
        # },
        {
            "host": "10.64.1.207",
            "user": "ciscotac",
            "pwd": "C15c0@mob1ly",
            "sw_type":"NX-OS"
        }]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = IOSPuller()
    # print(json.dumps(puller.get_inventory_data(hosts)))
    df = pd.DataFrame()
    # edn_dmz = pd.read_excel(open('DMZ all v2.1.xlsx', 'rb'), sheet_name ='Sheet1', dtype=str)
    # hosts = []
    # for ip , sw_type in zip(edn_dmz['IP Address'], edn_dmz['SW_Type']):
    #     host={
    #         "host": ip,
    #         "user": "ciscotac",
    #         "pwd": "C15c0@mob1ly",
    #         "sw_type":sw_type
    #     }
    #     hosts.append(host)
        
    res = puller.get_inventory_data(hosts)
    for x in hosts:
        data = res[x['host']].get('cdp')
        if data:
            for cdp in data:
                local = cdp['local']
                remote = cdp['remote']
                df =df.append([{'Device A Name':local.get('hostname',''),'Device A Interface':local.get('interface',''),'Device A Trunk Name':local.get('trunk',''),'Device A IP':local.get('ip',''), 'Device B System Name':remote.get('system_name',''),'Device B Interface':remote.get('interface',''),'Device B IP':remote.get('ip',''),'Device B Type':remote.get('type',''),'Device B Port Description':remote.get('desc',''),'Device A MAC':local.get('mac',''),'Device B MAC':remote.get('mac','')}], ignore_index=True)
    
    writer = pd.ExcelWriter('EDN_physical_map.xlsx', engine='openpyxl')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()