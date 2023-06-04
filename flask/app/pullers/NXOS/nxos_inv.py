import json
from operator import mod
import os
import traceback
from netmiko import Netmiko
from datetime import datetime
import re, sys, time
import threading

class NXOSPuller(object):
    
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

    def poll(self,host):
        print(f"Connecting to {host['host']}", file=sys.stderr)
        login_tries = 3
        c = 0
        is_login = False
        login_exception= None
        while c < login_tries :
            try:
                device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type='cisco_nxos', timeout=600, global_delay_factor=2)
                print(f"Success: logged in {host['host']}")
                is_login = True
                break
            except Exception as e:
                c +=1
                login_exception= str(e)
                
                
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
                print("getting version")
                ver = device.send_command("show version", use_textfsm=True)
                version = ver[0]['os'] if ver else ''
            except:
                print("version not found")
                version = None
            try:
                print("getting max_power", file=sys.stderr)
                max_power = device.send_command("show environment power", use_textfsm=True)
                max_power = max_power[0]['power_capacity_one'] if max_power else None
            except Exception as e:
                print("Power not found")
                max_power = None

            print("getting inventory....", file=sys.stderr)
            c = 0
            while c < 3:      #trying 3 times of inventory if gets failed
                print(f"Inventory try {c}")
                try:
                    inv = device.send_command('show inventory', use_textfsm=True)
                    break
                except:
                    c +=1
                    time.sleep(1.5)

            try:
                print("Inventory fetched...", file=sys.stderr)
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                for index, data in enumerate(inv):
                    if ('chassis' in data['descr'].lower()) or ('chassis' in data['name'].lower()):
                        self.inv_data[host['host']].update({'device':
                                                    {'ip_addr': host['host'], 
                                                    'serial_number': data['sn'], 
                                                    'pn_code': data['pid'], 
                                                    'hw_version': data['vid'], 
                                                    "software_version": version, 
                                                    "desc": data['descr'], 
                                                    "max_power": None if not max_power else max_power, 
                                                    "manufecturer": "Cisco", 
                                                    "status": "Production", 
                                                    "authentication": "AAA"}})
                        inv.pop(index)
                        break

                if not self.inv_data[host['host']].get('device') and inv:
                    data = inv[0]
                    inv.pop(0)
                    self.inv_data[host['host']].update({'device':
                                                        {'ip_addr': host['host'], 
                                                    'serial_number': data['sn'], 
                                                    'pn_code': data['pid'], 
                                                    'hw_version': data['vid'], 
                                                    "software_version": version, 
                                                    "desc": data['descr'], 
                                                    "max_power": None if not max_power else max_power, 
                                                    "manufecturer": "Cisco", 
                                                    "status": "Production", 
                                                    "authentication": "AAA"}})
                inv =[x for x in inv if x['sn']]
                self.get_boards(host, inv, version)   
                self.get_sub_boards(host, inv, version)
                self.get_sfps(host, device)
                self.get_license(host, device)
                self.inv_data[host['host']].update({'status': 'success'})
            except Exception as e:
                print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})

            if is_login: device.disconnect()
        
    def get_boards(self,host, inventory, sw):
        try:
            sfp_sub_modules = ['sfp','gls','cpak','cfp', 'mpa']
            board_data = []
            for inv in inventory:
                is_sfp = False
                for sf in sfp_sub_modules:
                    if (sf in inv['pid'].lower()) or (sf in inv['descr'].lower()) or "transceiver" in inv['name'].lower() or "transceiver" in inv['descr'].lower():
                        is_sfp = True
                        
                if is_sfp==False and inv.get('descr'):
                    board_data.append({
                                        "board_name": inv['name'],
                                        "serial_number": inv['sn'],
                                        "pn_code": None if ('Unspecified' in inv.get('pid')) or ('N/A' in inv.get('pid')) or (inv.get('pid')=='') else inv.get('pid',None),
                                        "hw_version": None if not inv['vid'] else inv['vid'],
                                        "slot_id": inv['name'],
                                        "status": "Production",
                                        "software_version": sw,
                                        "description": inv['descr']
                                        })
            
            self.inv_data[host['host']].update({'board': board_data})
        except Exception:
            self.inv_data[host['host']].update({'board': []})
        

    def get_sub_boards(self, host, inventory, version):
        try:
            sub_modules=['mpa']
            sub_board_data = []
            for inv in inventory:
                is_sub_board = False
                pid = inv['pid'].lower()
                for sm in sub_modules:
                    if sm in pid:
                        is_sub_board=True
                        
                if is_sub_board:
                    sub_board_type = re.findall(r'mpa-(\w+)',pid) #need correction get from descr
                    slot_number = re.findall(r'[0-9a-zA-Z]*\/', inv['name'])
                    slot_number = "".join([x for index, x in enumerate(slot_number) if index<2])
                    sub_slot_n = inv['name'].split(' ')
                    sub_board_data.append({'subboard_name': inv['name'],
                                            'subboard_type':inv['descr'],
                                            'slot_number':slot_number.replace('/',''),
                                            'subslot_number':sub_slot_n[-1] if sub_slot_n else None,
                                            'hw_version': None if not inv['vid'] else inv['vid'],
                                            'software_version':version,
                                            'serial_number': inv['sn'],
                                            'pn_code':None if ('Unspecified' in inv.get('pid')) or ('N/A' in inv.get('pid')) or (inv.get('pid')=='') else inv.get('pid',None),
                                            'status':'Production',
                                            'description': inv['descr']
                                            })
            self.inv_data[host['host']].update({'sub_board': sub_board_data})

        except Exception:
            self.inv_data[host['host']].update({'sub_board': []})


    def get_sfps(self, host, device):
        try:
            print("Getting sfp...")
            interfaces = device.send_command('show interface brief', use_textfsm=True)

            sfps = device.send_command('show interface transceiver', textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_nxos_show_interface_transceiver.textfsm', use_textfsm=True)

            sfps_data = []
            for inv in sfps:
                temp_int_name= inv.get('interface', "")
                temp_int_name= temp_int_name.replace('ernet','')
                interface= ([x for x in interfaces if x['interface'] == temp_int_name])
                speed= interface[0].get("speed", "") if len(interface)>0 else ""
                if speed.lower() != "auto":
                    speed = re.findall(r'(.*)\(D\)', speed)
                    speed= speed[0] if len(speed)>0 else ""
                
                mode=""
                if "lr" in inv['type'].lower():
                    mode="single-mode"
                if "sr" in inv['type'].lower():
                    mode="multimode"

                sfp_data = {'port_name': inv['interface'],
                            'mode': mode,
                            'speed': None if not speed else speed,
                            'hw_version': None,
                            'serial_number': inv.get('serial'),
                            'port_type': inv['type'],
                            'connector': None,
                            'wavelength':None,
                            'optical_direction_type':None,
                            'pn_code':None if ('Unspecified' in inv.get('part_number')) or ('N/A' in inv.get('part_number')) or (inv.get('part_number')=='') else inv.get('part_number',None),
                            'status':'Production',
                            'description': None,
                            'manufacturer': inv['manufacturer'],
                            'media_type': None,
                            'serial_number': inv.get('serial').lstrip('0')}
                
                sfps_data.append(sfp_data)
            
            self.inv_data[host['host']].update({"sfp":sfps_data})
        except Exception as e:
            self.inv_data[host['host']].update({"sfp":[]})
            print(f"Failed to get SFPS {e}", file=sys.stderr)
            traceback.print_exc()


    def get_license(self, host, device):
        try:
            print("Getting license", file=sys.stderr)
            license = device.send_command('show license usage', use_textfsm=True)
            all_license = []
            for lic in license:
                if lic.get('feature'):
                    desc = re.findall(r'([a-zA-Z0-9 ]*)', lic['comments'])
                    desc = "".join([x for x in desc if x])
                    all_license.append({
                                        "name": lic['feature'],
                                        "description": None if desc=='' else desc,
                                        "activation_date": "01-01-2000",
                                        "expiry_date": lic['expiry_date'] if lic['expiry_date'] else '01-01-2000',
                                        "grace_period": None,
                                        "serial_number": None,
                                        "status": 'decommissioned' if 'Unused' in lic['status'] else 'Production',
                                        "capacity": None,
                                        "usage": None,
                                        "pn_code":None
                                    })
            self.inv_data[host['host']].update({"license":all_license})
        except Exception:
            print("License not found")
            self.inv_data[host['host']].update({"license":[]})

if __name__ == '__main__':
    hosts = [
        {
            "host": "10.73.0.1", #"10.83.1.133", #"10.73.0.1"
            "user": "ciscotac",
            "pwd": "C15c0@mob1ly"
        }]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = NXOSPuller()
    #puller.get_inventory_data(hosts)
    print(puller.get_inventory_data(hosts))



    