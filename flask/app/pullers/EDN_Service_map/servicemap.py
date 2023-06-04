from netmiko import Netmiko
from datetime import datetime
import re, sys, json, time
import pandas as pd
import threading
class ServicePuller(object):
    
    def __init__(self):
        self.inv_data = {}
        self.connections_limit = 20

    def get_address_table_data(self, hosts):
        threads =[]
        for host in hosts:
            # self.poll(host)
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

    def poll(self,host):
        print(f"Connecting to {host['host']}")
        login_tries = 3
        c = 0
        is_login = False
        login_exception = None
        if host['sw_type']=='NX-OS':
            sw_type = 'cisco_nxos'
        elif host['sw_type']=='IOS':
            sw_type='cisco_ios'
        elif host['sw_type']=='IOS-XE':
            sw_type='cisco_ios'
        else:
            sw_type = ""

        
        if sw_type:
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
            self.inv_data[host['host']] = {"error":"Login Failed"}
            

        if is_login==True:
            try:
                device.send_command("terminal length 0")
            except:
                pass
            try:
                print("getting mac address-table")
                mac = device.send_command("show mac address-table dynamic", use_textfsm=True)
            except:
                print("address-table not found")
                mac=''
            try:
                print("getting interface description")
                if sw_type=='cisco_ios':
                    intf_desc = device.send_command("show interfaces description", use_textfsm=True)
                if sw_type=='cisco_nxos':
                    intf_desc = device.send_command("show interface description", use_textfsm=True)
            except Exception as e:
                intf_desc = ''
                print("interface description not found")
            try:
                data = []
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                if mac and intf_desc:
                    print(f"mac and interface data found")
                    if sw_type=='cisco_nxos':
                        for m in mac:
                            if 'tunnel' in m['ports']:continue
                            for i in intf_desc:
                                if (m['ports'] in i['port']) and (m['type'].lower()=='dynamic') and ('infra-link' not in i['description'].lower()):
                                    data.append({'MAC Address':m['mac'],'Switch Interface':m['ports'], 'Interface Description':i['description'],'Vlan':m['vlan']})
                                    break
                    elif sw_type=='cisco_ios':
                        for m in mac:
                            if 'tunnel' in m['destination_port']:continue
                            for i in intf_desc:
                                if (m['destination_port'] in i['port']) and (m['type'].lower()=='dynamic') and ('infra-link' not in i['descrip'].lower()):
                                    data.append({'MAC Address':m['destination_address'],'Switch Interface':m['destination_port'], 'Interface Description':i['descrip'],'Vlan':m['vlan']})
                                    break
                else:
                    raise Exception
                self.inv_data[host['host']].update({'address-table': data})
                print(f"total macs found {len(mac)}")
                print(f"Total mac-address found: {len(data)}")
                self.inv_data[host['host']].update({'status': 'success'})
            except Exception as e:
                print(f"mac or interface data not found")
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})
                    self.inv_data[host['host']].update({'address-table': []})

        if is_login: device.disconnect()
    

if __name__ == '__main__':
    Ips = pd.read_excel(open('EDN_NE_IPs_Puller_Source.xlsx', 'rb'))
    df = pd.DataFrame()
    
    puller = ServicePuller()
    hosts = []
    for reg, seg, name, ip, os_type in zip(Ips['Region'],Ips['Segment'],Ips['Switch Name'],Ips['Switch IP-Address'],Ips['OS Type']):
        hosts.append(
            {
                "host": ip,
                "user": "ciscotac",
                "pwd": "C15c0@mob1ly",
                "sw_type":os_type,
                'reg':reg,
                'seg':seg,
                'name':name,
            })

    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    import pdb;pdb.set_trace()
    get_data = puller.get_address_table_data(hosts)
    for ip in Ips['Switch IP-Address']:
        if get_data.get(ip,{}).get('address-table'):
            df = df.append(get_data[ip]['address-table'], ignore_index=True)


    writer = pd.ExcelWriter('edn_service_map.xlsx', engine='openpyxl')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()