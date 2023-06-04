import requests
import json, sys, json, re, time
from datetime import datetime
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import threading

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'

class FirePowerPuller(object):
    
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
            base_url = f"https://{host['host']}"
            r = None
            headers = {'Content-Type': 'application/json'}
            api_auth_path = "/api/fmc_platform/v1/auth/generatetoken"
            auth_url = base_url + api_auth_path
            try:
                r = requests.post(auth_url, headers=headers, auth=requests.auth.HTTPBasicAuth(
                    host['user'], host['pwd']), verify=False)
                auth_headers = r.headers
                print(auth_headers, file=sys.stderr)
                auth_token = auth_headers.get('X-auth-access-token', default=None)
                if auth_token == None:
                    print("auth_token not found. Exiting...", file=sys.stderr)
                    sys.exit()
            except Exception as err:
                print("Error in generating auth token --> "+str(err), file=sys.stderr)
                sys.exit()

            headers['X-auth-access-token'] = auth_token

            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/devices/devicerecords?expanded=true"    # param
            url = base_url + api_path
            if (url[-1] == '/'):
                url = url[:-1]

            # GET OPERATION

            r = requests.get(url, headers=headers, verify=False)
            status_code = r.status_code
            resp = r.text
            if (status_code == 200):
                print("GET successful. Response data --> ", file=sys.stderr)
                json_resp = json.loads(resp)
                
                print(json.dumps(json_resp, sort_keys=True,
                                indent=4, separators=(',', ': ')))
                for data in json_resp['items']:
                    if data['hostName'] not in self.inv_data:
                        self.inv_data[data['hostName']]= {'device':
                                                    {'ip_addr': data['hostName'], 
                                                    'serial_number': None, 
                                                    'hw_version':  None, 
                                                    "software_version": data['sw_version'] , 
                                                    "patch_version": None,
                                                    'pn_code': data['model'], 
                                                    "status": 'Production',
                                                    "desc": data['model'], 
                                                    "max_power": None,
                                                    "manufecturer": "Firepower",
                                                    "authentication": "AAA"},
                                                    'board':[],
                                                    'sub_board':[],
                                                    'sfp':[],
                                                    'license':[],
                                                    'status':'success'}
                print(self.inv_data, file=sys.stderr)
            else:
                r.raise_for_status()
                print("Error occurred in GET --> "+resp, file=sys.stderr)
                
            if r:r.close()
            
        except Exception as e:
            print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
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
                    
            failed_device.append({"ip_address": host['host'], "date":  time.strftime("%d-%m-%Y"), "time": time.strftime("%H-%M-%S"), "reason":str(e)})
            try:
                with open('app/failed/ims/'+file_name, 'w', encoding='utf-8') as fd:
                    fd.write(json.dumps(failed_device))
            except Exception as e:
                print(e)
                print("Failed to update failed devices list", file=sys.stderr)

if __name__ == '__main__':
    hosts = [
        {
            "host": "10.64.165.132",
            "user": "srv00280",
            "pwd": "1a3X#eEW3$40vPN%"
        }]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = FirePowerPuller()
    print(json.dumps(puller.get_inventory_data(hosts)))


