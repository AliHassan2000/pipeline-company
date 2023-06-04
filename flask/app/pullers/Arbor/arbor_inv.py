
from datetime import datetime
import re, sys, time, json
import threading
import textfsm


from app.pullers.Arbor.parsing import Parse
# from parsing import Parse

class ArborPuller(object):
    
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
        
        system_sh = {"command":"system show \n","sleep":10, "template":"arbor_system_show"}
        
        
        command_list.append(system_sh)
        
        data = parse_output.perform(host['host'], host['user'], host['pwd'], command_list)
        
        
        for x in data:
            if x.get('system show'):
                inventory = x['system show'][0]
        
        try:        
            if host['host'] not in self.inv_data:
                self.inv_data[host['host']] = {}

                self.inv_data[host['host']].update({'device':
                                            {'ip_addr': host['host'], 
                                            'serial_number': inventory[0], 
                                            'pn_code': inventory[4], 
                                            'hw_version': None, 
                                            "software_version": inventory[1], 
                                            "desc": inventory[2], 
                                            "max_power": None, 
                                            "manufecturer": "Arbor",
                                            "patch_version":inventory[3] ,
                                            "status": "Production", 
                                            "authentication": "AAA"},
                                            'board':[],
                                            'sub_board':[],
                                            'sfp':[],
                                            'license':[],
                                            'status':'success'})

            print("Arbor data is below", file=sys.stderr)
            print(f"{self.inv_data}", file=sys.stderr)
            self.inv_data[host['host']].update({'status': 'success'})
        except Exception as e:
            print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
            if host['host'] in self.inv_data:
                self.inv_data[host['host']].update({'status': 'error'})

           

 
if __name__ == '__main__':
    hosts = [
        {
            "host": "10.64.93.57",
            "user": "srv00280",
            "pwd": "1a3X#eEW3$40vPN%"
        }
        ]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = ArborPuller()
    print(json.dumps(puller.get_inventory_data(hosts)))