
from datetime import datetime
import re, sys, time, json
import threading
import traceback


from app.pullers.Wirefilter.parsing import Parse
# from parsing import Parse

class WirefilterPuller(object):
    
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
        print(f"Connecting to {host['host']} {host['master']['device_name']}", file=sys.stderr)
        
        try:   
            parse_output = Parse()
            command_list = []
            connection  = parse_output.connectShell(host['host'], host['user'], host['pwd'])
            
            print(f"Connected: to {host['host']} {host['master']['device_name']}", file=sys.stderr)
            platfrom = {"command":"platformMgmt \n ","sleep":5, "template":None}
            command_list.append(platfrom)
            front_output = []
            for x in range(1 , 7):
                if x==2:continue #skip front 2 
                front = {"command":"front "+str(x)+" \n","sleep":2, "template":None}
                system_sh = {"command":"show info \n","sleep":10, "template":"wirefilter_show_info"}
                exit = {"command":"exit \n\n","sleep":3, "template":None}

                command_list.append(front)
                command_list.append(system_sh)
                command_list.append(exit)

                data = parse_output.perform(connection, host['host'], command_list,)
                command_list = []
                for output in data:
                    if output.get('show info'):
                        front_output.append({'front':'FB'+str(x) ,'show info':output['show info'][0]})
                            
            print(front_output)     
            if host['host'] not in self.inv_data:
                self.inv_data[host['host']] = {}
                
            for index , inventory in enumerate(front_output):
                if inventory['front']=='FB1':
                    self.add_inventory_data(host['host'], inventory['show info'], inventory['front'], host['master']['device_name'])
                    front_output.pop(index)
                    break
            
            for output, slave in zip(front_output , host['slave']):
                self.add_inventory_data(slave['ip'], output['show info'], inventory['front'], slave['device_name'])
                # else:
                #     for x in host['slave']:
                          
                #         if inventory['front'] in x['device_name']:
                #             print(f"front is matched {inventory['front']}=={x['device_name']}")
                #             self.add_inventory_data(x['ip'], inventory['show info'], inventory['front'], x['device_name'])

            print("Wirefilter data is below", file=sys.stderr)
            # print(f"{self.inv_data}", file=sys.stderr)
            self.inv_data[host['host']].update({'status': 'success'})
        except Exception as e:
            print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
            traceback.print_exc()
            if host['host'] in self.inv_data:
                self.inv_data[host['host']].update({'status': 'error'})
            

    def add_inventory_data(self, ip ,inv, front, hostname):
        if ip not in self.inv_data:
                self.inv_data[ip] = {}
                
        self.inv_data[ip].update({'device':
                                        {'ip_addr': ip, 
                                        'serial_number': inv[1], 
                                        'pn_code': inv[2], 
                                        'hw_version': inv[4], 
                                        "software_version": None, 
                                        "desc": inv[0], 
                                        "max_power": None, 
                                        "manufecturer": inv[3],
                                        "patch_version":None,
                                        "status": "Production", 
                                        "authentication": "AAA"},
                                        'front':front,
                                        'hostname':hostname,
                                        'board':[],
                                        'sub_board':[],
                                        'sfp':[],
                                        'license':[],
                                        'status':'success'})
  
 
if __name__ == '__main__':
    hosts = [
        {
                'host':'10.83.213.142',
                'user':'srv00282',
                'pwd':'99maAF5smUt61397',
                'master':{
                        'ip': '10.83.213.140',
                        'device_name': 'FYH-WF01-SCB01'
                    },
                'slave':[
                    {
                        'ip': '10.83.213.141',
                        'device_name': 'FYH-WF01-FB01'
                    },
                    {
                        'ip': '10.83.213.150',
                        'device_name': 'FYH-WF01-FB02'
                    },
                    {
                        'ip': '10.83.213.152',
                        'device_name': 'FYH-WF01-FB03'
                    },
                    {
                        'ip': '10.83.213.154',
                        'device_name': 'FYH-WF01-FB04'
                    },
                    
                    
                ]
            }
        ]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = WirefilterPuller()
    print(json.dumps(puller.get_inventory_data(hosts)))