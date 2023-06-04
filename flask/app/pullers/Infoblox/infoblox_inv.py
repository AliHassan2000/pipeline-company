import requests
import json, sys, json, re, time
from datetime import datetime
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import threading

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'

class InfoboxPuller(object):
    
    def __init__(self):
        self.inv_data = {}
        self.connections_limit = 50

    def get_inventory_data(self, hosts):
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

    def poll(self, host):
        print(f"Connecting to {host['host']}", file=sys.stderr)

        try:
            base_url = f"https://{host['host']}/wapi/v2.9.7/member?_return_fields%2B=node_info&_return_as_object=1"
            print('getting Inventory ',file=sys.stderr)
            response = requests.request('GET', base_url, auth=(host['user'], host['pwd']), verify=False, timeout=50)
            if response.ok:
                try:
                    data = response.json()
                except Exception:
                    print(f"Login failed {host['host']}", file=sys.stderr)
                    raise Exception
                
                if host['host'] not in self.inv_data:
                    for member in data['result']:
                        for node in member['node_info']:
                            mgmt = node.get('mgmt_network_setting',{})
                            mgmt_ip = mgmt.get('address')
                            if not mgmt_ip:
                                service_status = node.get('service_status')
                                for srv in service_status:
                                    if srv.get('service') and srv.get('service')=='ENET_LAN':
                                        mgmt_ip = srv.get('description').split(' ')
                                        mgmt_ip = mgmt_ip[0]
                                        break
                            if mgmt_ip:
                                self.inv_data[mgmt_ip]= {'device':
                                                                {'ip_addr': mgmt_ip, 
                                                                'serial_number': node.get('hwid'), 
                                                                'pn_code': node.get('hwtype'), 
                                                                'hw_version': node.get('hwmodel') , 
                                                                "software_version": None , 
                                                                "desc": member.get('host_name'), 
                                                                "max_power": None, 
                                                                "manufecturer": 'Infoblox', 
                                                                "status": 'Production',
                                                                "authentication": "AAA"},
                                                                'board':[],
                                                                'sub_board':[],
                                                                'sfp':[],
                                                                'license':[],
                                                                'status':'success',
                                                                'server_ip':host['host']}

                  
                print(f"{self.inv_data}", file=sys.stderr)
            else:
                print(f"Connection failed {host['host']}", file=sys.stderr)

                raise Exception
        except Exception as e:
            print(f"Inventory not found {host['host']} Exception detail==>{e}", file=sys.stderr)
            if host['host'] in self.inv_data:
                self.inv_data[host['host']].update({'status': 'error'})
            file_name = time.strftime("%d-%m-%Y")+".txt"
            failed_device=[]
                #Read existing file
                
            try:
                with open('app/failed/ims/'+file_name,'r',encoding='utf-8') as fd:
                    failed_device= json.load(fd)
            except:
                pass
            #Update failed devices list
                
            failed_device.append({"ip_address": host['host'],"date":  time.strftime("%d-%m-%Y"), "time": time.strftime("%H-%M-%S"), "reason":"GET request failed"})
            try:
                with open('app/failed/ims/'+file_name, 'w', encoding='utf-8') as fd:
                    fd.write(json.dumps(failed_device))
            except Exception as e:
                print(e)
                print("Failed to update failed devices list: "+str(e), file=sys.stderr)

   
      

if __name__ == '__main__':
    hosts = [
        {
            "host": "10.73.211.20",
            "user": "srv00282",
            "pwd": "99maAF5smUt61397"
        }]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = InfoboxPuller()
    print(json.dumps(puller.get_inventory_data(hosts)))

