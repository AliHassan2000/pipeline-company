import traceback
from netmiko import Netmiko
from datetime import datetime
import re, sys, time, json
import threading
import logging
import logging.handlers

class XEPuller(object):
    
    def __init__(self):
        self.inv_data = {}
        self.connections_limit = 50
        self.stack_priority= 0
        self.stack_switch= ""
        
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
                device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type='cisco_ios',global_delay_factor=2, timeout=600)
                print(f"Success: logged in {host['host']}", file=sys.stderr)
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

        if is_login==True:
            try:
                print("getting version")
                ver = device.send_command("show version", use_textfsm=True)
                version = ver[0]['version'] if ver else ''
            except:
                print("version not found")
                version = None
                hardware = ''
            try:
                print("getting max_power", file=sys.stderr)
                max_power = device.send_command("show environment power", use_textfsm=True) #need confirmation
                max_power = max_power[0]['power_capacity_one'] if max_power else None
            except Exception as e:
                print("Power not found")
                max_power = None

            try:
                stack=1
                print("Getting stack switches")
                stacks = device.send_command("show switch detail", use_textfsm=True)  
                for stk in stacks:
                    if(stk['state']== 'Ready'):
                        stack+=1

                if(stack>1):    
                    for stk in stacks:
                        if int(stk['priority'])> self.stack_priority:
                            self.stack_priority= int(stk['priority'])
                            self.stack_switch=stk['switch']

            except Exception as e:
                print(f"Stack switches not found {e}")

            print("getting inventory....", file=sys.stderr)
            c = 0
            while c < 3:      #trying 3 times of inventory if gets failed
                print(f"Inventory try {c}")
                try:
                    inv = device.send_command('show inventory', use_textfsm=True)
                    print(f"inv is: {inv}", file=sys.stderr)
                    break
                except:
                    c +=1
                    time.sleep(1.5)

            try:
                print("Inventory fetched...", file=sys.stderr)
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                for index, data in enumerate(inv):
                    if ('chassis' in data['descr'].lower()) or ('chassis' in data['name'].lower()) or ('c38xx' in data['name'].lower()):
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
                                                    "authentication": "AAA",
                                                    "stack":(stack-1) if stack>1 else stack}})
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
                                                    "authentication": "AAA",
                                                    "stack":(stack-1) if stack>1 else stack}})
                print(self.inv_data)
                inv =[x for x in inv if x['sn']]
                self.get_boards(host, inv, version)   
                self.get_sub_boards(host, inv, version)
                self.get_sfps(host, inv, device)
                self.get_license(host, device)
                self.inv_data[host['host']].update({'status': 'success'})
            except Exception as e:
                print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
                traceback.print_exc()
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})

            if is_login: device.disconnect()

    def get_boards(self,host, inventory, sw):
        try:
            sfp_sub_modules = ['sfp','gls','cpak','cfp','glc','xfp','ftl']
            board_data = []
            for inv in inventory:
                is_sfp = False
                for sf in sfp_sub_modules:
                    if (sf in inv['pid'].lower()) or (sf in inv['descr'].lower() and 'mpa' not in inv['descr'].lower()) or "transceiver" in inv['name'].lower() or "gi" in inv['name'].lower()  or f"switch {self.stack_switch}".strip() == inv['name'].lower():
                        is_sfp = True
                if is_sfp==False and inv.get('descr'):
                    board_data.append({
                                        "board_name": inv['name'],
                                        "serial_number": inv['sn'],
                                        "pn_code": None if ('Unspecified' in inv.get('pid')) or ('N/A' in inv.get('pid')) or (inv.get('pid')=='') else inv.get('pid',None),
                                        "hw_version": inv['vid'],
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
            sub_modules=['mpa','spa']
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
                                            'pn_code': None if ('Unspecified' in inv.get('pid')) or ('N/A' in inv.get('pid')) or (inv.get('pid')=='') else inv.get('pid',None),
                                            'status':'Production',
                                            'description': inv['descr']
                                            })
            self.inv_data[host['host']].update({'sub_board': sub_board_data})
        except Exception:
            self.inv_data[host['host']].update({'sub_board': []})


    def get_sfps(self, host, inventory, device):
        try:
            sfps_data = []
            print(f"Getting sfp data..." ,file=sys.stderr)
            for inv in inventory:
                is_sfp = False

                if ("Gi" in inv['name'] or "transceiver" in inv['name'].lower()):
                    is_sfp =True
                    #break
                if is_sfp:
                    #New
                    modes= {'LR':'single-mode','IR':'single-mode', 'SR':'multimode','LH':'single-mode','LX':'single-mode', 'SX':'multimode', 'MM':'multimode', 'GLC-T': 'single-mode', 'SFP-GE-S': 'multimode', 'SFP-GE-L': 'single-mode', 'FTLF':'multimode', 'GLR':'single-mode', 'WF-SFP':'multimode', '5798LP':"single-mode" }
                    mode = ''
                    for key, value in modes.items():
                        if key.lower() in inv['pid'].lower():
                            mode = value
                            break
                    
                    port_name= ""
                    port_type= ""
                    optics_data = self.get_sfp_optics_data(device, inv)

                    if "transceiver" in inv['name'].lower():
                        port_name= [optics_data.get('port_name', "")]
                        port_type= re.findall(r'([a-zA-Z]*)', optics_data.get('port_type', ""))
                        
                    else:
                        port_name=  [inv['name']]
                        port_type= re.findall(r'(\S*)', inv['descr'])

                    
                    speed = self.get_speed(port_name[0] if len(port_name)>0 else port_name)
                    
                    sfp_data = {'port_name': port_name[0] if len(port_name)>0 else port_name, 
                                'mode': mode,
                                'speed': speed,
                                'hw_version': None if not inv['vid'] else inv['vid'],
                                'serial_number': inv['sn'],
                                'port_type': port_type[0] if len(port_type)>0 else port_type,
                                'connector': None if not optics_data.get('connector') else optics_data.get('connector'),
                                'wavelength':None if not optics_data.get('wavelength') else optics_data.get('wavelength'),
                                'optical_direction_type':None,
                                'pn_code':None if ('Unspecified' in inv.get('pid')) or ('N/A' in inv.get('pid')) or (inv.get('pid')=='') else inv.get('pid',None),
                                'status':'Production',
                                'description': inv['descr'],
                                'serial_number': inv.get('sn').lstrip('0'),
                                'manufacturer': optics_data.get('vendor'),
                                'media_type': optics_data.get('media_type') if optics_data.get('media_type') and ('Unspecified' not in optics_data.get('media_type')) else None}
                    sfps_data.append(sfp_data)

            self.inv_data[host['host']].update({"sfp":sfps_data})
        except Exception:
            self.inv_data[host['host']].update({"sfp":[]})


    def get_license(self, host, device):
        try:
            print("Getting license")
            license = device.send_command('show license usage', use_textfsm=True)
            all_license = []
            for lic in license:
                desc = re.findall(r'([a-zA-Z0-9 ]*)', lic['descr'])
                desc = "".join([x for x in desc if x]) 
                if lic.get('feature'):
                    all_license.append({
                                        "name": lic['feature'],
                                        "description": None if desc=='' else desc,
                                        "activation_date": "2000-01-01",
                                        "expiry_date": "2000-01-01",
                                        "grace_period": None,
                                        "serial_number": None,
                                        "status": 'Production' if lic['status']=='IN USE' else 'decommissioned',
                                        "capacity": None,
                                        "usage": None,
                                        "pn_code": None
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
            
            if 'transceiver' in inv['name'].lower():
                sfp_optics = device.send_command(f"show hw-module {inv['name']} idprom", textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_ios_show_hw-module_idprom.textfsm',use_textfsm=True)
                
            else:
                # app/pullers/ntc-templates/ntc_templates/templates/
                sfp_optics = device.send_command(f"show idprom interface {g} {module_name}", textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_ios_show_idprom_interface.textfsm',use_textfsm=True)
            
            modes= {'LR':'single-mode','SR':'multimode','LH':'single-mode','LX':'single-mode', 'SX':'multimode'}
            mode = ''
            for key, value in modes.items():
                if key in inv['pid'] or key in inv['descr']:
                    mode = value
                    break

            port_type = re.findall(r'([a-zA-Z]*)', module_name) if not g else g
            port_type = port_type[0] if isinstance(port_type, list) else port_type
            for optics in sfp_optics:
                optics_data = {'mode':mode,'connector':optics['connector'],'wavelength':optics.get('wavelength'),'media_type':optics.get('media_type'),'vendor':optics['vendor'],'speed':optics['speed'],'port_name':optics.get('port_name') if optics.get('port_name') else  module_name, 'port_type':re.findall(r'([A-Za-z]*)', optics.get('port_name'))[0] if optics.get('port_name') else  port_type}
            return optics_data
        except:
            return {}

    def get_speed(self, port_name):
        speed=""
        if "gi" in port_name.lower():
            speed= "1G"
        elif "te" in port_name.lower():
            speed= "10G"
        elif "fo" in port_name.lower():
            speed= "40G"
        elif "ho" in port_name.lower():
            speed= "100G"
        return speed

if __name__ == '__main__':
    hosts = [
        {
            "host": "10.2.78.1",
            "user": "ciscotac",
            "pwd": "C15c0@mob1ly"
        }]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = XEPuller()
    print(json.dumps(puller.get_inventory_data(hosts)))