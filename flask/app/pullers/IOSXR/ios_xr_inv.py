from netmiko import Netmiko
from datetime import datetime
import re, sys, json, time
import threading

class XRPuller(object):
    
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
        e_detail = ''
        login_exception = None
        while c < login_tries :
            try:
                device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type='cisco_xr', global_delay_factor=2)
                print(f"Success: logged in {host['host']}", file=sys.stderr)
                is_login = True
                break
            except Exception as e:
                c +=1
                e_detail = e
                login_exception = str(e)
                
                
        if is_login==False:
            print(f"Falied to login {host['host']} \n Exception detail=>{e_detail}", file=sys.stderr)
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
            
        try:
            device.send_command("terminal length 0")
        except:
            pass
        if is_login==True:
            try:
                print("getting version", file=sys.stderr)
                ver = device.send_command("show version", use_textfsm=True)
                version = ver[0]['version'] if ver else None
            
            except:
                print("version not found")
                version = None
                
            try:
                print("getting max_power", file=sys.stderr)
                max_power = device.send_command("admin show environment power", use_textfsm=True)
                max_power = max_power[0]['power_capacity_one'] if max_power else None
            except Exception as e:
                print("Power not found")
                max_power = None

            print("getting inventory....", file=sys.stderr)
            c = 0
            while c < 6:      #trying 3 times of inventory if gets failed
                print(f"Inventory try {c}", file=sys.stderr)
                try:
                    print("show inventory", file=sys.stderr)
                    inv = device.send_command('show inventory', use_textfsm=True, delay_factor=5)
                    if isinstance(inv, str): 
                        print("Send show inventory all", file=sys.stderr)
                        inv = device.send_command('show inventory all', use_textfsm=True)
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
                self.get_sfps(host, inv, device)
                self.get_license(host, device)
                self.inv_data[host['host']].update({'status': 'success'})
            except Exception as e:
                print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})

            if is_login: device.disconnect()

    def get_boards(self,host, inventory, sw):
        try:
            sfp_sub_modules = ['sfp','gls','cpak','cfp', 'mpa', 'glc']
            board_data = []
            for inv in inventory:
                is_sfp = False
                for sf in sfp_sub_modules:
                    if (sf in inv['pid'].lower()) or (sf in inv['descr'].lower() and 'mpa' not in inv['descr'].lower()) or "transceiver" in inv['name'].lower() :
                        is_sfp = True
                        
                if is_sfp==False and inv.get('descr'):
                    board_data.append({
                                        "board_name": inv['descr'],
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
            for index, inv in enumerate(inventory):
                is_sub_board = False
                pid = inv['pid'].lower()
                for sm in sub_modules:
                    if sm in pid:
                        is_sub_board=True
                        
                if is_sub_board:
                    sub_board_type = re.findall(r'mpa-(\w+)',pid) 
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


    def get_sfps(self, host, inventory, device):
        try:
            sfps=['sfp','gls','cpak','cfp', 'glc']
            print(f"Getting sfp optics data...." ,file=sys.stderr)
            sfps_data = []
            for inv in inventory:
                is_sfp = False
                for sfp in sfps:
                    pid = inv['pid'].lower()
                    if (sfp in pid) or (sfp in inv['descr'].lower() and 'mpa' not in inv['descr'].lower()):
                        is_sfp =True
                        break
                if is_sfp:
                    optics_data = self.get_sfp_optics_data(device, inv)
                    speed = optics_data.get('speed')
                    if speed:
                        speed = re.findall(r'(\d+)', optics_data.get('speed'))
                        speed = int(speed[0]) if speed else None
                        if speed:
                            speed = int(speed/1024)
                            speed = str(speed)+'G' if speed >=1 else None
                    sfp_data = {'port_name': optics_data.get('port_name'),
                                'mode': None if not optics_data.get('mode') else optics_data.get('mode'),
                                'speed': None if not speed else speed,
                                'hw_version': inv['vid'],
                                'serial_number': inv['sn'].lstrip('0'),
                                'port_type': optics_data.get('port_type'),
                                'connector': None if not optics_data.get('connector') else optics_data.get('connector'),
                                'wavelength':None if not optics_data.get('wavelength') else optics_data.get('wavelength'),
                                'optical_direction_type':None,
                                'pn_code':None if ('Unspecified' in inv.get('pid')) or ('N/A' in inv.get('pid')) or (inv.get('pid')=='') else inv.get('pid',None),
                                'status':'Production',
                                'description': inv['descr'],
                                'manufacturer': optics_data.get('vendor'),
                                'media_type': optics_data.get('media_type') if optics_data.get('media_type') and ('Unspecified' not in optics_data.get('media_type')) else None}
                    sfps_data.append(sfp_data)

            self.inv_data[host['host']].update({"sfp":sfps_data})
        except Exception:
            self.inv_data[host['host']].update({"sfp":[]})


    def get_license(self, host, device):
        try:
            print("Getting license")
            license = device.send_command('show license', use_textfsm=True)
            all_license = []
            for lic in license:
                desc = re.findall(r'([a-zA-Z0-9 ]*)', lic['featureid'])
                desc = "".join([x for x in desc if x])
                if lic.get('featureid'):
                    all_license.append({
                                        "name": lic['featureid'],
                                        "description": None if desc=='' else desc,
                                        "activation_date": "2000-01-01",
                                        "expiry_date": "2000-01-01",
                                        "grace_period":None,
                                        "serial_number":None,
                                        "status": 'Production' if lic['active']=='1' else 'decommissioned',
                                        "capacity":None,
                                        "usage":None,
                                        "pn_code":None
                                    })
            self.inv_data[host['host']].update({"license":all_license})
        except Exception:
            print("License not found")
            self.inv_data[host['host']].update({"license":[]})

    def get_sfp_optics_data(self, device, inv):
        gig_types = {"100":"HundredGigE","10":"TenGigE","25":"TwentyFiveGigE","50":"FiftyGigE","40":"FortyGigE","400":"FourHundredGigE"}
        
        gig_type = re.findall(r'-(\d+)',inv['pid'].lower())
        try:
            g = gig_types.get(gig_type[0]) if gig_type else ""
            
            module_name = inv['name'].split(" ")[-1]
            if 'CPU' in module_name:
                module_name = module_name.replace("CPU","")
            if 'Gi' in module_name:
                g = ""
           
            sfp_optics = device.send_command(f"show controllers {g} {module_name} all", textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_xr_show_controller.textfsm',use_textfsm=True)
            
            modes= {'LR':'single-mode','SR':'multimode','LH':'single-mode','LX':'single-mode', 'SX':'multimode'}
            mode = ''
            for key, value in modes.items():
                if key in inv['pid']:
                    mode = value
                    break
            port_type = re.findall(r'([a-zA-Z]*)', module_name) if not g else g
            port_type = port_type[0] if isinstance(port_type, list) else port_type
            for optics in sfp_optics:
                optics_data = {'mode':mode,'connector':optics['connector_type'],'wavelength':optics['wavelength'],'media_type':optics['media_type'],'vendor':optics['vendor'],'speed':optics['speed'],'port_name':module_name, 'port_type':port_type}
            return optics_data
        except:
            return {}

        

if __name__ == '__main__':
    hosts = [
        {
            "host": "10.64.150.152",
            "user": "ciscotac",
            "pwd": "C15c0@mob1ly"
        }]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = XRPuller()
    print(json.dumps(puller.get_inventory_data(hosts)))