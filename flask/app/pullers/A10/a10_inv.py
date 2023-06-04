import os
from netmiko import Netmiko
from datetime import datetime
import re, sys, time, json
import threading


class A10Puller(object):
    
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
        print(f"Connecting to {host['host']}", file=sys.stderr)
        login_tries = 3
        c = 0
        is_login = False
        login_exception = None
        while c < login_tries :
            try:
                device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type='a10', timeout=600, global_delay_factor=2)
                print(f"Success: logged in {host['host']}")
                is_login = True
                break
            except Exception as e:
                c+=1
                login_exception = str(e)
                
        if is_login==False:
            print(f"Failed to login {host['host']}", file=sys.stderr)
            self.inv_data[host['host']] = {"error":"Login Failed"}
            file_name = time.strftime("%d-%m-%Y")+".txt"
            failed_device=[]
            #Read existing file
            try:
                with open('app/failed/ims/'+file_name,'r',encoding='utf-8') as fd:
                    failed_device= json.load(fd)
            except:
                pass
            #Update failed devices list
            
            failed_device.append({"ip_address": host['host'],"date":  time.strftime("%d-%m-%Y"), "time": time.strftime("%H-%M-%S"), "reason":login_exception})
            try:
                with open('app/failed/ims/'+file_name, 'w', encoding='utf-8') as fd:
                    fd.write(json.dumps(failed_device))
            except Exception as e:
                print(e)
                print("Failed to update failed devices list", file=sys.stderr)

        if is_login==True:
            try:       
                print("getting version", file=sys.stderr)
                ver = device.send_command("show version", textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/a10_show_version.textfsm', use_textfsm=True)
                print(f"data is {ver}", file=sys.stderr)
                
                version = ver[0]['version']
                patch = ver[0]['build']
                serial = ver[0]['serial'] 
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                    
                    self.inv_data[host['host']].update({'device':
                                                {'ip_addr': host['host'], 
                                                'serial_number': serial, 
                                                'pn_code': None, 
                                                'hw_version': None, 
                                                "software_version": version, 
                                                "desc": None, 
                                                "max_power": None, 
                                                "manufecturer": "Cisco",
                                                "patch_version":patch ,
                                                "status": "Production", 
                                                "authentication": "AAA"},
                                                'board':[],
                                                'sub_board':[],
                                                'sfp':[],
                                                'license':[],
                                                'status':'success'})

                print("A10 data is below", file=sys.stderr)
                print(f"{self.inv_data}", file=sys.stderr)
                self.inv_data[host['host']].update({'status': 'success'})
            except Exception as e:
                print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})
                    
        if is_login:device.disconnect()

           

 
if __name__ == '__main__':
    hosts = [
        {
            "host": "10.42.192.4",
            "user": "srv00282",
            "pwd": "99maAF5smUt61397"
        }
        ]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = A10Puller()
    print(json.dumps(puller.get_inventory_data(hosts)))