import os, sys
from netmiko import Netmiko
from datetime import datetime
import re, json, time

class NXOSPullerOpr(object):
    
    def __init__(self):
        self.inv_data = {}
    
    def get_operational_data(self, hosts):
        for host in hosts:
            print(f"Connecting to {host['host']}")
            login_tries = 3
            c = 0
            is_login = False
            login_exception= None
            while c < login_tries :
                try:
                    device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type='cisco_nxos', timeout=600, global_delay_factor=2)
                    print(f"Success: logged in {host['host']}")
                    is_login=True
                    break
                except Exception as e:
                    c +=1
                    login_exception= str(e)
                    print(f"Falied to login {host['host']}")
                    

            if is_login==False:
                self.inv_data[host['host']] = {"error":"Login Failed"}
                file_name = time.strftime("%d-%m-%Y")+".txt"
                failed_device=[]
                #Read existing file
                
                try:
                    with open('app/failed/ims/'+file_name,'r',encoding='utf-8') as fd:
                        if os.stat(file_name).st_size != 0:
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

                continue
            try:
                print("getting Cpu ")
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                cpu_data = []
                cpu = device.send_command("show system resources", use_textfsm=True)
                for cp in cpu:
                    cpu_data.append({'cpu_1_min':cp['one_minute'],
                                    'cpu_5_min':cp['five_minute'],
                                    'cpu_15_min':cp['fifteen_minute']
                                    })
                self.inv_data[host['host']].update({'cpu':cpu_data})
            except:
                print("cpu not found")
                self.inv_data[host['host']].update({'cpu':[]})

            try:
                print("getting memory")
                mem_data = []
                memory = device.send_command("show system resources", use_textfsm=True)
                for m in memory:
                    mem_data.append({
                                    'total_memory':m['total'],
                                    'free_memory':m['free'],
                                    'memory_state':m.get('memory_state'),
                                    'used':m['used']
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
                                    "dest_host":x['dest_host'],
                                    "sysname":x['sysname'],
                                    "mgmt_ip":x['mgmt_ip'],
                                    "platform":x['platform'],
                                    "remote_port":x['remote_port'],
                                    "local_port":x['local_port'],                       
                                    "version":x['version']                  
                                    })
                self.inv_data[host['host']].update({'cdp':cdp_data})
            except Exception as e:
                print(f"cdp neighbors not found")
                self.inv_data[host['host']].update({'cdp':[]})
            
            # try:
            #     print("Getting ldp neighbor...")
            #     ldp_data = []
            #     ldp = device.send_command("show mpls ldp neighbour", use_textfsm=True) #need fsm
            #     for x in ldp:
            #         ldp.append({
            #                     "peer": x['peer'],
            #                     "gr": x['gr'],
            #                     "nsr": x['nsr'],
            #                     "uptime": x['uptime'],
            #                     "discovery_ipv4": x['discovery_ipv4'],
            #                     "discovery_ipv6": x['discovery_ipv6'],
            #                     "addresses_ipv4": x['addresses_ipv4'],
            #                     "addresses_ipv6": x['addresses_ipv6'],
            #                     "labels_ipv4":x['labels_ipv4'] ,
            #                     "labels_ipv6":x['labels_ipv6']
            #                 })
            #     self.inv_data[host['host']].update({'ldp':ldp_data})
            # except Exception as e:
            #     print(f"ldp neighbors not found")
            #     self.inv_data[host['host']].update({'ldp':[]})
            
            c = 0
            print("getting interfaces")
            while c < 3:      #trying 3 times of interfaces if gets failed
                try:
                    interf_data = []
                    interfaces = device.send_command("show interface", use_textfsm=True)
                    for x in interfaces:
                        interf_data.append({
                                        "interface": x['interface'],
                                        "link_status": x['link_status'],
                                        "admin_state": x['admin_state'],
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
                                        "input_rate": x.get('input_rate')+'bits/sec',
                                        "output_rate": x.get('output_rate')+'bits/sec',
                                        "input_errors": x.get('input_errors'),
                                        "output_errors": x.get('output_errors')
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
            #     fib = device.send_command("show resource", use_textfsm=True)
            #     for x in fib:
            #         fib_data.append({'resourse': x['resourse'],
            #                         'min': x['min'], 
            #                         'max': x['max'],
            #                         'used':x['used'],
            #                         'unsed':x['unsed'],
            #                         'avail':x['avail']
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
                bgp_data = []
                print("getting bgp neighbors")
                bgp_neib = device.send_command("show ip bgp neighbors", use_textfsm=True) #fsm error
                for x in bgp_neib:
                    bgp_data.append({
                                    "neighbor":x.get('neighbor'),
                                    "remote_as": x.get('remote_as'),
                                    "remote_router_id": x.get('remote_router_id'),
                                    "state": x.get('bgp_state'),
                                    "local_address": x.get('localhost_ip'),
                                    "local_port": x.get('localhost_port'),
                                    "remote_address": x.get('remote_ip'),
                                    "remote_port": x.get('remote_port')
                                    })
                self.inv_data[host['host']].update({'bgp_neighbours':bgp_data})
            except Exception:
                print("bgp neighbors not found")
                self.inv_data[host['host']].update({'bgp_neighbours':[]})

            # try:
            #     print("getting isis neighbors")
            #     isis_nei = device.send_command("show isis neighbors", use_textfsm=True)  #need fsm 
            #     # isis_metric = device.send_command("show isis interface brief vrf all", use_textfsm=True)# fsm need to build
            #     self.inv_data[host['host']].update({'isis_neighbours':isis_nei})
            # except Exception:
            #     print("isis neighbors not found")
            #     self.inv_data[host['host']].update({'isis_neighbours':[]})
                
            try:
                ospf_data = []
                print("getting ospf neighbors")
                ospf_nei = device.send_command("show ip ospf neighbor", use_textfsm=True) 
                # ospf_metric = device.send_command("show ip ospf interface brief", use_textfsm=True)  #cost=metric
                for x in ospf_nei:
                    ospf_data.append({
                                    "neighbor_id": x.get('neighbor_ipaddr'),
                                    "priority": x.get('priority'),
                                    "state": x.get('state'),
                                    "dead_time": x.get('dead_time'),
                                    "address": x.get('local_ipaddr'),
                                    "interface": x.get('interface')
                                    })
                self.inv_data[host['host']].update({'ospf_neighbours':ospf_data})
            except Exception:
                print("ospf neighbors not found")
                self.inv_data[host['host']].update({'ospf_neighbours':[]})

        if is_login: device.disconnect()
        return json.dumps(self.inv_data)



if __name__ == '__main__':
    hosts = [
        {
            "host": "10.8.161.4",
            "user": "srv00047",
            "pwd": "5FPB4!!1c9&g*iJ9"
        }]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = NXOSPullerOpr()
    print(puller.get_operational_data(hosts))