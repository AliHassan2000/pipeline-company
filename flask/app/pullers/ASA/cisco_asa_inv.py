import json
from netmiko import Netmiko
from datetime import datetime
import re, sys, time
import threading

class ASAPuller(object):
    
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
        login_exception = None
        while c < login_tries :
            try:
                device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type='cisco_asa', timeout=600, global_delay_factor=2)
                print(f"Success: logged in {host['host']}")
                is_login = True
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
                with open('app/failed/ims/'+file_name,'r', encoding='utf-8') as fd:
                    failed_device= json.load(fd)
            except:
                print("Failed devices list is empty", file=sys.stderr)
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
                device.send_command("terminal pager 0")
                print("getting version")
                ver = device.send_command("show version \n\n\n", use_textfsm=True)
                version = ver[0]['version'] if ver else ''
            except:
                print("version not found", file=sys.stderr)
                version = ''
                
            
            print("getting inventory....", file=sys.stderr)
            c = 0
            inv = None
            while c < 3:      #trying 3 times of inventory if gets failed
                print(f"Inventory try {c}")
                try:
                    inv = device.send_command('show inventory', use_textfsm=True)
                    if isinstance(inv, str): 
                        print("show chassis detail", file=sys.stderr)
                        inv = device.send_command('show chassis detail')
                        inv = re.findall(r'Chassis Serial Number\s+:\s+(.*)', inv)
                        
                    break
                except:
                    print(f"show inventory command failed try {c}", file=sys.stderr)
                    c +=1
                    time.sleep(1.5)

            try:
                print("Inventory fetched...")
                if not inv:
                    inv = device.send_command('show chassis detail')
                    inv = re.findall(r'Chassis Serial Number\s+:\s+(.*)', inv)
                    inv = [{'name':'chassis','descr':'', 'sn':inv[0]}] if inv else None
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                for index, data in enumerate(inv):
                    if ('chassis' in data.get('descr').lower()) or ('chassis' in data.get('name').lower()):
                        self.inv_data[host['host']].update({'device':
                                                    {'ip_addr': host['host'], 
                                                    'serial_number': data.get('sn').strip(), 
                                                    'pn_code': data.get('pid'), 
                                                    'hw_version': data.get('vid'), 
                                                    "software_version": version, 
                                                    "desc": data.get('descr'), 
                                                    "max_power": None, 
                                                    "manufecturer": "Cisco", 
                                                    "status": "Production", 
                                                    "authentication": None}})
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
                                                    "max_power": '', 
                                                    "manufecturer": "Cisco", 
                                                    "status": "active", 
                                                    "authentication": ""}})
                inv =[x for x in inv if x['sn']]
                self.get_boards(host, inv, version)   
                self.get_sub_boards(host, inv)
                self.get_sfps(host, inv)
                self.get_license(host, device)
                self.inv_data[host['host']].update({'status': 'success'})
            except Exception as e:
                print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})

            if is_login: device.disconnect()

    def get_boards(self,host, inventory, sw):
        try:
            sfp_sub_modules = ['sfp','gls','cpak','cfp', 'mpa' ,'glc', 'sx']
            board_data = []
            for inv in inventory:
                is_sfp = False
                for sf in sfp_sub_modules:
                    if (sf in inv['pid'].lower()) or (sf in inv['descr'].lower() and 'mpa' not in inv['descr'].lower()):
                        is_sfp = True
                        
                if is_sfp==False:
                    board_data.append({
                                        "board_name": inv['descr'],
                                        "serial_number": inv['sn'],
                                        "pn_code": inv['pid'],
                                        "hw_version": inv['vid'],
                                        "slot_id": inv['name'],
                                        "status": "active",
                                        "software_version": sw,
                                        "description": inv['descr']
                                        })
            
            self.inv_data[host['host']].update({'board': board_data})
        except Exception:
            self.inv_data[host['host']].update({'board': []})
        

    def get_sub_boards(self, host, inventory):
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
                                            'subboard_type':sub_board_type[0].upper() if sub_board_type else '',
                                            'slot_number':slot_number,
                                            'subslot_number':sub_slot_n[-1] if sub_slot_n else '',
                                            'hw_version': inv['vid'],
                                            'serial_number': inv['sn'],
                                            'pn_code':inv['pid'],
                                            'status':'active',
                                            'description': inv['descr']
                                            })
            self.inv_data[host['host']].update({'sub_board': sub_board_data})
        except Exception:
            self.inv_data[host['host']].update({'sub_board': []})


    def get_sfps(self, host, inventory):
        try:
            sfps=['sfp','gls','cpak','cfp', 'glc', 'sx']
            sfps_data = []
            for inv in inventory:
                is_sfp = False
                for sfp in sfps:
                    pid = inv['pid'].lower()
                    if (sfp in pid) or (sfp in inv['descr'].lower() and 'mpa' not in inv['descr'].lower()):
                        is_sfp =True
                        break
                if is_sfp:
                    speed = re.findall(r'-(\w+)-',pid)
                    sfp_data = {'port_name': inv['descr'],
                                'mode': '',
                                'speed': '',
                                'hw_version': inv['vid'],
                                'serial_number': inv['sn'].lstrip('0'),
                                'port_type': '',
                                'connector': '',
                                'wavelength':'',
                                'optical_direction_type':'',
                                'pn_code':inv['pid'],
                                'status':'active',
                                'description': inv['descr'],
                                'manufacturer': 'Cisco',
                                'media_type': ''}
                    sfps_data.append(sfp_data)

            self.inv_data[host['host']].update({"sfp":sfps_data})
        except Exception:
            self.inv_data[host['host']].update({"sfp":[]})


    def get_license(self, host, device):
        try:
            print("Getting license", file=sys.stderr)
            license = device.send_command('show license all', use_textfsm=True)
            all_license = []
            for lic in license:
                all_license.append({
                                    "name": lic['license'],
                                    "description": lic['license_description'],
                                    "activation_date": lic['registration_initial_date'],
                                    "expiry_date": lic['registration_expiration_date'],
                                    "grace_period": None,
                                    "serial_number": lic['sn'],
                                    "status": lic['license_status'],
                                    "capacity":None,
                                    "usage": None,
                                    "pn_code": lic['pid']
                                })
            self.inv_data[host['host']].update({"license":all_license})
        except Exception:
            print("License not found")
            self.inv_data[host['host']].update({"license":[]})

if __name__ == '__main__':
    hosts = [
        {
            "host": "10.14.93.56",
            "user": "srv00280",
            "pwd": "1a3X#eEW3$40vPN%"
        }]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = ASAPuller()
    print(puller.get_inventory_data(hosts))