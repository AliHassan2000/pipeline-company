from dis import dis
from netmiko import Netmiko
from datetime import datetime
import re, json,time

from sqlalchemy.sql.expression import true

class XRPullerOpr(object):
    
    def __init__(self):
        self.inv_data = {}
    
    def get_operational_data(self, hosts):
        for host in hosts:
            print(f"Connecting to {host['host']}")
            login_tries = 3
            c = 0
            is_login = False
            login_exception = None
            while c < login_tries :
                try:
                    device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type='cisco_xr', timeout=600, global_delay_factor=2)
                    print(f"Success: logged in {host['host']}")
                    is_login=True
                    break
                except Exception as e:
                    c +=1
                    print(f"Falied to login {host['host']}")
                    login_exception = str(e)

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

            device.disable_paging()
            
            try:
                print("getting Cpu ")
                cpu_data = []
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                cpu = device.send_command("show processes cpu", use_textfsm=True)
                for cp in cpu:
                    cpu_data.append({'cpu_1_min':cp['cpu_1_min'],
                                    'cpu_5_min':cp['cpu_5_min'],
                                    'cpu_15_min':cp['cpu_15_min']
                                    })
                self.inv_data[host['host']].update({'cpu':cpu_data})
            except:
                print("cpu not found")
                self.inv_data[host['host']].update({'cpu':[]})

            try:
                print("getting memory")
                mem_data = []
                memory = device.send_command("show watchdog memory-state", use_textfsm=True)
                for m in memory:
                    mem_data.append({
                        'total_memory':m['physical_memory'],
                        'free_memory':m['free_memory'],
                        'memory_state':m['memory_state']
                    })
                self.inv_data[host['host']].update({'memory':mem_data})
            except Exception as e:
                print("memory not found")
                self.inv_data[host['host']].update({'memory':[]})

            
            try:
                print("getting disk")
                disk_data = []
                disk = device.send_command("show media", use_textfsm=True) #need fsm for asr
                for d in disk:
                    disk_data.append({
                        'partition':d['partition'],
                        'size':d['size'],
                        'used':d['used'],
                        'available':x['available']
                    })
                self.inv_data[host['host']].update({'disk':disk_data})
            except Exception as e:
                print("disk not found")
                self.inv_data[host['host']].update({'disk':[]})

            try:
                print("getting lldp neighbors...")
                lldp_data = []
                lldp = device.send_command("show lldp neighbors", use_textfsm=True)
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
            
            try:
                print("getting ldp neighbors...")
                ldp_data = []
                ldp = device.send_command("show mpls ldp neighbor brief", use_textfsm=True)
                for x in ldp:
                    ldp.append({
                                "peer": x['peer'],
                                "gr": x['gr'],
                                "nsr": x['nsr'],
                                "uptime": x['uptime'],
                                "discovery_ipv4": x['discovery_ipv4'],
                                "discovery_ipv6": x['discovery_ipv6'],
                                "addresses_ipv4": x['addresses_ipv4'],
                                "addresses_ipv6": x['addresses_ipv6'],
                                "labels_ipv4":x['labels_ipv4'] ,
                                "labels_ipv6":x['labels_ipv6']
                            })
                self.inv_data[host['host']].update({'ldp':ldp_data})
            except Exception as e:
                print(f"ldp neighbors not found")
                self.inv_data[host['host']].update({'ldp':[]})
            
            try:
                print("getting interfaces")
                interf_data = []
                interfaces = device.send_command("show interfaces", use_textfsm=True)
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
                                        "input_rate": x['input_rate']+'bits/sec',
                                        "output_rate": x['output_rate']+'bits/sec',
                                        "input_errors": x['input_errors'],
                                        "output_errors": x['output_errors']
                                        })
                self.inv_data[host['host']].update({'interfaces':interf_data})
            except Exception as e:
                print(f"interfaces not found")
                self.inv_data[host['host']].update({'interfaces':[]})

            # try:
            #     print("getting fib")
            #     fib_data = []
            #     fib = device.send_command("show rib afi-all tables summary", use_textfsm=True)
            #     for x in fib:
            #         fib_data.append({'unicast_prefixes': x['unicast_prefixes'],
            #                         'multicast_prefixes': x['multicast_prefixes'], 
            #                         'ipv': x['ipv']
            #                         })
            #     self.inv_data[host['host']].update({'fib':fib_data})
            # except Exception as e:
            #     print(f"fib not found")
            #     self.inv_data[host['host']].update({'fib':[]})
            
            try:
                print("getting lfib")
                lfib_data = []
                lfib = device.send_command("show mpls forwarding summary", use_textfsm=True) #confirm values
                for x in lfib:
                    lfib_data.append({
                                    'label_switching': x['label_switching']
                                    })
                self.inv_data[host['host']].update({'lfib':lfib_data})
            except Exception as e:
                print(f"lfib not found")
                self.inv_data[host['host']].update({'lfib':[]})
            
            try:
                print("getting bgp neighbors")
                bgp_data = []
                bgp_neib = device.send_command("show bgp neighbors", use_textfsm=True) #fsm error
                for x in bgp_neib:
                    bgp_data.append({
                        "neighbor":x['neighbor'],
                        "remote_as": x['remote_as'],
                        # "local_as": x['local_as'],
                        # "type": x['type'],
                        # "description": x['description'],
                        "remote_router_id": x['remote_router_id'],
                        # "cluster_id": x['cluster_id'],
                        "state": x['state'],
                        # "uptime": x['uptime'],
                        # "nsr_state": x['nsr_state'],
                        # "holdtime": x['holdtime'],
                        # "keepalive": x['keepalive'],
                        # "nsr":x['nsr'],
                        # "gr": x['gr'],
                        # "connections_established": x['connections_established'],
                        # "connections_dropped": x['connections_dropped'],
                        "local_address": x['local_address'],
                        "local_port": x['local_port'],
                        "remote_address": x['remote_address'],
                        "remote_port": x['remote_port']
                    })
                self.inv_data[host['host']].update({'bgp_neighbours':bgp_data})
            except Exception:
                print("bgp neighbors not found")
                self.inv_data[host['host']].update({'bgp_neighbours':[]})
            
            try:
                print("getting isis neighbors")
                isis_data = []
                isis_nei = device.send_command("show isis neighbors", use_textfsm=True) 
                for x in isis_data:
                    isis_data.append({
                                    "system_id": x['system_id'],
                                    "interface": x['interface'],
                                    "snpa": x['snpa'],
                                    "state": x['state'],
                                    "hold_time": x['hold_time'],
                                    "type": x['type'],
                                    "ietf_nsf": x['ietf_nsf']
                                    })
                self.inv_data[host['host']].update({'isis_neighbours':isis_data})
                
            except Exception:
                print("isis neighbors not found")
                self.inv_data[host['host']].update({'isis_neighbours':[]})

            
                

        if is_login: device.disconnect()
        return json.dumps(self.inv_data)



if __name__ == '__main__':
    hosts = [
        {
            "host": "10.219.60.3",
            "user": "srv00047",
            "pwd": "5FPB4!!1c9&g*iJ9"
        }]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = XRPullerOpr()
    print(puller.get_operational_data(hosts))