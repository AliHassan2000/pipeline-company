import requests
import json, sys, re, time
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class ACIServicePuller(object):
    
    def __init__(self):
        self.inv_data = {}
    
    def get_address_table_data(self, hosts):
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
                    print(f"Falied to login {host['host']}")
                    login_exception = e
                    
            if is_login==False:
                self.inv_data[host['host']] = {"error":"Login Failed"}
                continue
            try:
                print("getting mac address-table")
                host_url = f"https://{host['host']}:{port}"
                fvCEp_url = f'{host_url}/api/node/class/fvCEp.json?&order-by=fvCEp.modTs|desc'
                headers = {'cache-control': "no-cache"}
                get_response = requests.get(fvCEp_url, headers=headers, cookies=cookie, verify=False)
                if get_response.ok:
                    get_response= get_response.json()
                    imdata = get_response['imdata']
                    if imdata:
                        fvCEp = imdata
            except:
                print("mac address-table not found")
                fvCEp = ''

            try:
                data = []
                print("Getting interface description...")
                host_url = f"https://{host['host']}:{port}"
                fvRsCEpToPathEp_url = f'{host_url}/api/node/class/fvRsCEpToPathEp.json?&order-by=fvRsCEpToPathEp.modTs|desc'
                headers = {'cache-control': "no-cache"}
                get_response = requests.get(fvRsCEpToPathEp_url, headers=headers, cookies=cookie, verify=False)
                if get_response.ok:
                    get_response= get_response.json()
                    imdata = get_response['imdata']
                    if imdata:
                        fvRsCEpToPathEp = imdata

                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                
                if fvCEp and fvRsCEpToPathEp:
                    for fvc in fvCEp:
                        for fv in fvRsCEpToPathEp:
                            fvcep_info  = fvc['fvCEp']['attributes']
                            fv_info = fv['fvRsCEpToPathEp']['attributes']
                            fvcep_mac = fvcep_info['mac']
                            fvRsep_mac = re.findall(r'cep-(.*)\/rscEpToPathEp', fv_info['dn'])
                            fvRsep_mac = fvRsep_mac[0] if fvRsep_mac else None
                            
                            if fvRsep_mac and  (fvRsep_mac.strip()==fvcep_mac.strip()):
                                desc = re.findall(r'^uni\/tn-(.*)\/cep', fv_info['dn'])
                                node = re.findall(r'paths-(\d+)', fv_info['dn'])
                                port = re.findall(r'pathep-\[(.*)\]]', fv_info['dn'])
                                data.append({'node':'node-'+node[0],'vlan':fvcep_info['encap'], 'mac':fvRsep_mac,'ip':fvcep_info['ip'], 'interface':port[0], 'description':desc[0]})
                                
                else:
                    raise Exception
                self.inv_data[host['host']].update({'address-table': data})
                self.inv_data[host['host']].update({'status': 'success'})
            except Exception as e:
                print(f"mac addree or interface not found")
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})
                    self.inv_data[host['host']].update({'address-table': []})
                    
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
    puller = ACIServicePuller()
    print(json.dumps(puller.get_address_table_data(hosts)))

