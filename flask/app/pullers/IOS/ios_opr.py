import sys
from netmiko import Netmiko
from datetime import datetime
import re, json,time

class IOSPullerOpr(object):
    
    def __init__(self):
        self.inv_data = {}
    
    def get_operational_data(self, hosts):
        for host in hosts:
            print(f"Connecting to {host['host']}")
            login_tries = 3
            c = 0
            is_login = False
            while c < login_tries :
                try:
                    device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type='cisco_ios', timeout=600, global_delay_factor=2)
                    print(f"Success: logged in {host['host']}")
                    is_login=True
                    break
                except Exception as e:
                    c +=1
                    print(f"Falied to login {host['host']}")
                    login_exception = e

            if is_login==False:
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
                    print("Failed to update failed devices list:"+str(e), file=sys.stderr)

                continue

            try:
                print("getting Cpu ")
                cpu_data = []
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                cpu = device.send_command("show processes cpu", use_textfsm=True)
                for cp in cpu:
                    cpu_data.append({'cpu_1_min':cp['cpu_5_sec'],
                                    'cpu_5_min':cp['cpu_1_min'],
                                    'cpu_15_min':cp['cpu_5_min']
                                    })
                self.inv_data[host['host']].update({'cpu':cpu_data})
            except:
                print("cpu not found")
                self.inv_data[host['host']].update({'cpu':[]})

            try:
                print("getting memory")
                mem_data = []
                memory = device.send_command("show processes memory sorted", use_textfsm=True)
                for m in memory:
                    mem_data.append({
                                    'total_memory':m['memory_total'],
                                    'free_memory':m['memory_free'],
                                    'memory_state':m.get('memory_state')
                                    })
                self.inv_data[host['host']].update({'memory':mem_data})
            except Exception as e:
                print("memory not found")
                self.inv_data[host['host']].update({'memory':[]})

            # try:
            #     print("getting disk")
            #     disk = device.send_command("show media", use_textfsm=True) #need confirmation
            #     self.inv_data[host['host']].update({'disk':disk})
            # except Exception as e:
            #     print("disk not found")
            #     self.inv_data[host['host']].update({'disk':[]})

            try:
                print("getting lldp neighbors...")
                lldp_data = []
                lldp = device.send_command("show lldp neighbors detail", use_textfsm=True) #need confirmation
                for x in lldp:
                    lldp_data.append({
                                    'neighbor':x['neighbor'],
                                    'local_interface':x['local_interface'],
                                    'neighbor_interface':x['neighbor_interface']   
                                    })
                self.inv_data[host['host']].update({'lldp':lldp_data})
            except Exception as e:
                print(f"lldp neighbors not found")
                self.inv_data[host['host']].update({'lldp':[]})
            
            try:
                print("getting cdp neighbors...")
                cdp_data = []
                cdp = device.send_command("show cdp neighbors detail", use_textfsm=True)
                for x in cdp:
                    cdp_data.append({
                                    "dest_host":x['destination_host'],
                                    "sysname":x.get('sysname'),
                                    "mgmt_ip":x['management_ip'],
                                    "platform":x['platform'],
                                    "remote_port":x['remote_port'],
                                    "local_port":x['local_port'],                       
                                    "version":x['software_version']                  
                                    })
                self.inv_data[host['host']].update({'cdp':cdp_data})
            except Exception as e:
                print(f"cdp neighbors not found")
                self.inv_data[host['host']].update({'cdp':[]})
            
            # try:
            #     print("getting ldp neighbors...")
            #     ldp = device.send_command("show mpls ldp neighbour", use_textfsm=True) #need fsm and output
            #     self.inv_data[host['host']].update({'ldp':ldp})
            # except Exception as e:
            #     print(f"ldp neighbors not found")
            #     self.inv_data[host['host']].update({'ldp':[]})
            
            c = 0
            print("getting interfaces")
            while c < 3:      #trying 3 times of interfaces if gets failed
                try:
                    interf_data = []
                    interfaces = device.send_command("show interfaces", use_textfsm=True)
                    for x in interfaces:
                        interf_data.append({
                                        "interface": x['interface'],
                                        "link_status": x['link_status'],
                                        "admin_state": x['protocol_status'],
                                        "hardware_type": x['hardware_type'],
                                        "address": x['address'],
                                        "bia": x['bia'],
                                        "description": x['description'],
                                        "ip_address": x['ip_address'],
                                        "mtu": x['mtu'],
                                        "duplex": x['duplex'],
                                        "speed": x['speed'],
                                        "bandwidth": x['bandwidth'],
                                        "encapsulation": x['encapsulation'],
                                        "input_rate": x['input_rate']+'bits/sec',
                                        "output_rate": x['output_rate']+'bits/sec',
                                        "input_errors": x['input_errors'],
                                        "output_errors": x['output_errors']
                                        })
                    self.inv_data[host['host']].update({'interfaces':interf_data})
                    break
                except Exception as e:
                    print(f"interfaces not found")
                    self.inv_data[host['host']].update({'interfaces':[]})
                    c +=1

            # try:
            #     print("getting fib")
            #     fib_data = []
            #     fib = device.send_command("show ip cef", use_textfsm=True) #need fib summary like in xr
            #     for x in fib:
            #         fib_data.append({'prefix': x['prefix'],
            #                         'nexthop': x['nexthop'], 
            #                         'interface': x['interface']
            #                         })
            #     self.inv_data[host['host']].update({'fib':fib_data})
            # except Exception as e:
            #     print(f"fib not found")
            #     self.inv_data[host['host']].update({'fib':[]})
            
            # try:
            #     print("getting lfib")
            #     lfib = device.send_command("show mpls forwarding summary", use_textfsm=True) #need confirmation
            #     self.inv_data[host['host']].update({'lfib':lfib})
            # except Exception as e:
            #     print(f"lfib not found")
            #     self.inv_data[host['host']].update({'lfib':[]})
            
            try:
                print("getting protocols")
                prot = device.send_command("show ip protocols | i Routing Protocol is")
                try:
                    if 'bgp' in prot.lower():
                        bgp_data = []
                        print("getting bgp neighbors")
                        bgp_neib = device.send_command("show ip bgp neighbors", use_textfsm=True)
                        for x in bgp_neib:
                            bgp_data.append({
                                            "neighbor":x['neighbor'],
                                            "remote_as": x['remote_as'],
                                            "remote_router_id": x['remote_router_id'],
                                            "state": x['bgp_state'],
                                            "local_address": x['localhost_ip'],
                                            "local_port": x['localhost_port'],
                                            "remote_address": x['remote_ip'],
                                            "remote_port": x['remote_port']
                                            })
                        self.inv_data[host['host']].update({'bgp_neighbours':bgp_data})
                except Exception:
                    print("bgp neighbors not found")
                    self.inv_data[host['host']].update({'bgp_neighbours':[]})
                try:
                    if 'isis' in prot.lower():
                        print("getting isis neighbors")
                        isis_data = []
                        isis_nei = device.send_command("show isis neighbors", use_textfsm=True) 
                        # isis_metric = device.send_command("show clns interface", use_textfsm=True)# fsm need to build
                        for x in isis_nei:
                            isis_data.append({
                                            "system_id": x['system_id'],
                                            "interface": x['interface'],
                                            "snpa": x.get('snpa'),
                                            "state": x['state'],
                                            "hold_time": x['hold_time'],
                                            "type": x['type'],
                                            "ietf_nsf": x.get('ietf_nsf')
                                            })
                        self.inv_data[host['host']].update({'isis_neighbours':isis_data})
                except Exception:
                    print("isis neighbors not found")
                    self.inv_data[host['host']].update({'isis_neighbours':[]})
                
                try:
                    if 'ospf' in prot.lower():
                        print("getting ospf neighbors")
                        ospf_data = []
                        ospf_nei = device.send_command("show ip ospf neighbor", use_textfsm=True) 
                        # ospf_metric = device.send_command("show ip ospf interface brief", use_textfsm=True)  #cost=metric
                        for x in ospf_nei:
                            ospf_data.append({
                                            "neighbor_id": x['neighbor_id'],
                                            "priority": x['priority'],
                                            "state": x['state'],
                                            "dead_time": x['dead_time'],
                                            "address": x['address'],
                                            "interface": x['interface']
                                            })
                        self.inv_data[host['host']].update({'ospf_neighbours':ospf_data})
                except Exception:
                    print("isis neighbors not found")
                    self.inv_data[host['host']].update({'ospf_neighbours':[]})

            except Exception as e:
                print(f"protocols not found")
                

        if is_login: device.disconnect()
        return json.dumps(self.inv_data)



if __name__ == '__main__':
    hosts = [
        {
            "host": "10.25.17.161",
            "user": "srv00047",
            "pwd": "5FPB4!!1c9&g*iJ9"
        }]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = IOSPullerOpr()
    print(puller.get_operational_data(hosts))