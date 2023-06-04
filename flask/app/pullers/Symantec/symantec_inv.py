
from datetime import datetime
import re, sys, time, json
import threading
from app.pullers.Symantec.parsing import Parse
#from parsing import Parse

class SymantecPuller(object):
    
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
        parse_output = Parse()
        command_list = []

        system_version = {"command":"show version \n","sleep":2, "template":"symantec_show_version"}
        system_licenses = {"command":"show licenses \n","sleep":4, "template":"symantec_show_licenses"}
        system_configuration = {"command":"show hardware-configuration \n","sleep":4, "template":"symantec_show_hardware_configuration"}
        
        command_list.append(system_version)
        command_list.append(system_licenses)
        command_list.append(system_configuration)
        
        data = parse_output.perform(host['host'], host['user'], host['pwd'], command_list)
        license = []
        sfps = []
        for x in data:
            if x.get('show version'):
                inventory = x['show version'][0]
            if x.get('show licenses'):
                license = x['show licenses']
            if x.get('show hardware-configuration'):
                sfps = x['show hardware-configuration']
                    
        try:        
            if host['host'] not in self.inv_data:
                self.inv_data[host['host']] = {}
               
                self.inv_data[host['host']].update({'device':
                                            {'ip_addr': host['host'], 
                                            'serial_number': inventory[0], 
                                            'pn_code': None, 
                                            'hw_version': None, 
                                            "software_version": inventory[1], 
                                            "desc": None, 
                                            "max_power": None, 
                                            "manufecturer": "Symantec",
                                            "patch_version":None ,
                                            "status": "Production", 
                                            "authentication": "AAA"},
                                            'board':[],
                                            'sub_board':[],
                                            'sfp':[],
                                            'status':'success'})

            self.get_license(host, license)
            self.get_sfps(host, sfps)
            self.inv_data[host['host']].update({'status': 'success'})
        except Exception as e:
            print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
            if host['host'] in self.inv_data:
                self.inv_data[host['host']].update({'status': 'error'})

    def get_license(self, host, license): 
        try:
            print("Getting license")
            all_license = []
            for lic in license:
                all_license.append({
                                    "name": lic[2],
                                    "description":  lic[2],
                                    "activation_date": lic[3],
                                    "expiry_date": "2030-01-01",
                                    "grace_period": None,
                                    "serial_number": lic[0],
                                    "status": 'Production' if lic[4]=="Perpetual" else 'decommissioned',
                                    "capacity": None,
                                    "usage": None,
                                    "pn_code": lic[1]
                                })
            self.inv_data[host['host']].update({"license":all_license})
        except Exception as e:
            print("License not found")
            print(e)
            self.inv_data[host['host']].update({"license":[]})
    
    def get_sfps(self, host, inventory):
        try:
            optics_data={}
            sfps_data = []
            print(f"Getting sfp data..." ,file=sys.stderr)
            for inv in inventory:
                speed = inv[2]
                if speed:
                    speed = re.findall(r'(\d+)', inv[2])
                    speed = int(speed[0]) if speed else None
                    speed = '1G' if speed and speed >=1000 and speed <=2000 else None
                sfp_data = {'port_name': inv[0],
                            'mode': None ,
                            'speed': None if not speed else speed,
                            'hw_version': None,
                            'port_type': inv[3],   
                            'connector': None,
                            'wavelength':None,
                            'optical_direction_type':None,
                            'pn_code':None,
                            'status':None,
                            'description': None,
                            'manufacturer': inv[1],
                            'media_type': None,
                            'serial_number': None #inv['sn']
                            }
                sfps_data.append(sfp_data)

            self.inv_data[host['host']].update({"sfp":sfps_data})
        except Exception:
            self.inv_data[host['host']].update({"sfp":[]})
    
if __name__ == '__main__':
    hosts = [
        {
            "host": "10.64.93.12",
            "host": "10.64.93.11",
            "user": "srv00280",
            "pwd": "1a3X#eEW3$40vPN%"
        }
        ]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = SymantecPuller()
    print(json.dumps(puller.get_inventory_data(hosts)))
    
    