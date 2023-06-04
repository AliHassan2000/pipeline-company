import json
import os
from netmiko import Netmiko
from datetime import datetime
import re, sys, time
import threading


class PaloAltoPuller(object):
    
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
        login_exception= None
        while c < login_tries :
            try:
                
                device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type='paloalto_panos', timeout=600, global_delay_factor=2)
                print(f"Success: logged in {host['host']}")
                is_login = True
                break
            except Exception as e:
                c +=1
                login_exception= str(e)
                
                
        if is_login==False:
            print(f"Falied to login {host['host']}")
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

            print("getting inventory....", file=sys.stderr)
            c = 0
            while c < 3:      #trying 3 times of inventory if gets failed
                print(f"Inventory try {c}")
                try:
                    inv = device.send_command('show system info', use_textfsm=True)
                    break
                except:
                    print(f"show inventory command failed try {c}", file=sys.stderr)
                    c +=1
                    time.sleep(1.5)

            try:
                print("Inventory fetched...")
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                for data in inv:
                        self.inv_data[host['host']].update({'device':
                                                    {'ip_addr': host['host'], 
                                                    'serial_number': data['serial'], 
                                                    'pn_code': None, 
                                                    'hw_version': None, 
                                                    "software_version": data['os'], 
                                                    "desc": data['hostname'], 
                                                    "max_power": None, 
                                                    "manufecturer": "PaltoAlto", 
                                                    "status": "Production", 
                                                    "authentication": ""},
                                                    "board":[],
                                                    "sub_board":[]
                                                    })
                        

                
                
                self.get_sfps(host, device)
                self.get_license(host, device)
                self.inv_data[host['host']].update({'status': 'success'})
            except Exception as e:
                print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})

            if is_login: device.disconnect()

 
    def get_sfps(self, host, device):
        try:
            sfps_data = []
            data = device.send_command("show interface hardware", use_textfsm=True)
            for inv in data:
                if "vlan" in inv['intf'].lower() or "tunnel" in inv['intf'].lower() or "loopback" in inv['intf'].lower():
                    continue
                else:
                    sfp_data = {'port_name': inv['intf'],
                                'mode': 'duplex ' + inv['duplex'],
                                'speed': inv['speed'],
                                'hw_version': None,
                                'serial_number': None,
                                'port_type': None,
                                'connector': None,
                                'wavelength':None,
                                'optical_direction_type':None,
                                'pn_code':None,
                                'status':'Production' if 'up' in inv['state'] else 'decommissioned',
                                'description': None,
                                'manufacturer': 'PaloAlto',
                                'media_type': None}
                    sfps_data.append(sfp_data)

            self.inv_data[host['host']].update({"sfp":sfps_data})
        except Exception:
            self.inv_data[host['host']].update({"sfp":[]})


    def get_license(self, host, device):
        try:
            print("Getting license", file=sys.stderr)
            license = device.send_command("request license info", textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/paloalto_panos_request_license_info.textfsm',use_textfsm=True)
            all_license = []
            for lic in license:
                all_license.append({
                                    "name": lic['feature'],
                                    "description": lic['desc'],
                                    "activation_date": lic['issue'],
                                    "expiry_date": lic['expire'],
                                    "grace_period": None,
                                    "serial_number": None,
                                    "status": None,
                                    "capacity": None,
                                    "usage": None,
                                    "pn_code": None
                                })
            self.inv_data[host['host']].update({"license":all_license})
        except Exception:
            print("License not found")
            self.inv_data[host['host']].update({"license":[]})

if __name__ == '__main__':
    hosts = [
        {
            "host": "10.64.93.148",
            "user": "srv00280",
            "pwd": "1a3X#eEW3$40vPN%"
        }]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = PaloAltoPuller()
    print(puller.get_inventory_data(hosts))