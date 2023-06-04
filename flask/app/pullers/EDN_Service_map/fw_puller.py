from netmiko import Netmiko
from datetime import datetime
import re, sys, json, time
import pandas as pd
import threading

class FWPuller(object):
    
    def __init__(self):
        self.inv_data = {}
        self.connections_limit = 20

    def get_arp_table(self, hosts):
        threads =[]
        for host in hosts:
            # self.poll(host)
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

    def poll(self,host):
        print(f"Connecting to {host['host']}")
        login_tries = 3
        c = 0
        is_login = False
        login_exception = None
        if host['sw_type']=='asa':
            sw_type = 'cisco_asa'
        elif host['sw_type']=='srx':
            sw_type='juniper_junos'
        elif host['sw_type']=='fortinet':
            sw_type='fortinet'
        else:
            sw_type = ""

        
        if sw_type:
            while c < login_tries :
                try:
                    
                    device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type=sw_type, timeout=800)
                    print(f"Success: logged in {host['host']}")
                    is_login = True
                    break
                except Exception as e:
                    c +=1
                    login_exception = e
                
        if is_login==False:
            print(f"Falied to login {host['host']}")
            self.inv_data[host['host']] = {"error":"Login Failed"}
            
        if is_login==True:
            
            try:
                data = []
                print("getting arp table")
                if sw_type=='cisco_asa':
                    arp = device.send_command("show arp", use_textfsm=True)
                    for x in arp:data.append({'address':x['address'],'mac':x['mac']})
                if sw_type=='fortinet':
                    arp = device.send_command("get system arp", use_textfsm=True)
                    for x in arp:data.append({'address':x['address'],'mac':x['mac']})
                if sw_type=='juniper_junos':
                    arp = device.send_command("show arp no-resolve", use_textfsm=True)
                    for x in arp:data.append({'address':x['ip_address'],'mac':x['mac']})
                
                    
                self.inv_data[host['host']].update({'arp-table': data})
                self.inv_data[host['host']].update({'status': 'success'})
            except Exception as e:
                print(f"arp table data not found")
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})
                    self.inv_data[host['host']].update({'arp-table': []})

        if is_login: device.disconnect()
    

if __name__ == '__main__':
    
    puller = FWPuller()
    hosts = [{
                "host": '',
                "user": "ciscotac",
                "pwd": "C15c0@mob1ly",
                "sw_type":'asa'
            }]

    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    import pdb;pdb.set_trace()
    print(puller.get_arp_table(hosts))