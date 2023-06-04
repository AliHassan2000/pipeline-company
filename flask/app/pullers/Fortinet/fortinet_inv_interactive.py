
from datetime import datetime
import re, sys, time, json
import threading



# from app.pullers.Prime.parsing import Parse
from parsing import Parse

class Fortinet2Puller(object):
    
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
        yes = {"command":"y \n","sleep":2, "template":None}
        pwd = {"command":f"{host['pwd']} \n","sleep":2, "template":None}
        ver = {"command":"get system status \n","sleep":5, "template":"fortinet_get_system_status"}
        sfps = {"command":"get system interface transceiver \n","sleep":5, "template":"fortinet_get_system_interface_transceiver"}
        license = {"command":"diag auto update versions \n","sleep":5, "template":"fortinet_diag_auto_update_versions"}
        
        command_list.append(yes)
        command_list.append(pwd)
        command_list.append(ver)
        command_list.append(sfps)
        command_list.append(license)
        
        data = parse_output.perform(host['host'], host['user'], host['pwd'], command_list)
        import pdb;pdb.set_trace()
        ver = None
        for x in data:
            if x.get('show version'):
                ver = x['show version'][0]
                    
        try:        
            if host['host'] not in self.inv_data:
                self.inv_data[host['host']] = {}
                data = []
                
                self.inv_data[host['host']].update({'device':
                                            {'ip_addr': host['host'], 
                                            'serial_number': ver[12], 
                                            'pn_code': ver[1], 
                                            'hw_version': None, 
                                            "software_version": ver[3] if ver else None, 
                                            "desc": ver[0], 
                                            "max_power": None, 
                                            "manufecturer": 'FireEye',
                                            "patch":None,
                                            "status": "Production", 
                                            "authentication": "AAA"},
                                            'board':[],
                                            'sub_board':[],
                                            'sfp':[],
                                            'license':[],
                                            'status':'success'})

            print("fireeye data is below", file=sys.stderr)
            print(f"{self.inv_data}", file=sys.stderr)
            self.inv_data[host['host']].update({'status': 'success'})
        except Exception as e:
            print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
            if host['host'] in self.inv_data:
                self.inv_data[host['host']].update({'status': 'error'})

           

 
if __name__ == '__main__':
    hosts = [
        {
            "host": "10.14.93.27",
            "user": "srv00280",
            "pwd": "1a3X#eEW3$40vPN%"
        }
        ]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = Fortinet2Puller()
    print(json.dumps(puller.get_inventory_data(hosts)))