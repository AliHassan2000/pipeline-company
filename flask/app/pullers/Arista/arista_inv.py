from netmiko import Netmiko
from datetime import datetime
import re, sys, time, json
import threading

class AristaPuller(object):
    
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
        print(f"Connecting to {host['host']}")
        login_tries = 3
        c = 0
        is_login = False
        login_exception = None
        while c < login_tries :
            try:
                device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type='arista_eos', timeout=600, global_delay_factor=2)
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
                print("getting version and inventory")
                device.enable()
                time.sleep(2)
                version = device.send_command("show version", use_textfsm=True)
                time.sleep(2)
                inventory = device.send_command("show inventory", use_textfsm=True)
                serial = None
                
                for index, data in enumerate(inventory):
                    for x in version:
                        if x.get('serial_number') and x.get('serial_number')==data['sn']:
                            inventory.pop(index)
                            break
                        
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                    
                ver = None
                
                for data in version:
                    pid = data.get('model')
                    hw_version = data.get('hw_version')
                    serial = data.get('serial_number')
                    soft_ver = data.get('image')
                    ver = soft_ver
                    self.inv_data[host['host']].update({'device':
                                                {'ip_addr': host['host'], 
                                                'serial_number': serial, 
                                                'pn_code': pid, 
                                                'hw_version': hw_version, 
                                                "software_version": soft_ver, 
                                                "desc": None, 
                                                "max_power": None, 
                                                "manufecturer": "Arista", 
                                                "status": "Production", 
                                                "authentication": "AAA"},
                                                'sub_board':[],
                                                'license':[],
                                                'status':'success'})
                
                self.get_boards(host, inventory, ver)   
                self.get_sfps(host,inventory, device)
                self.inv_data[host['host']].update({'status': 'success'})
            except Exception as e:
                print(f"Inventory not found Exception detail==>{e}", file=sys.stderr)
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})

            if is_login: device.disconnect()

    def get_boards(self,host, inventory, sw):
        try:
            sfp_sub_modules = ['sfp','gls','cpak','cfp', 'mpa' ,'glc','qsfp','cab']
            board_data = []
            for inv in inventory:
                is_sfp = False
                for sf in sfp_sub_modules:
                    if (sf in inv['pid'].lower()) or (sf in inv['descr'].lower()):
                        is_sfp = True
                        
                if is_sfp==False:
                    board_data.append({
                                        "board_name": inv['name'],
                                        "serial_number": inv['sn'],
                                        "pn_code":inv.get('pid'),
                                        "hw_version": None if not inv['vid'] else inv['vid'],
                                        "slot_id": inv.get('name'),
                                        "status": "Production",
                                        "software_version": sw,
                                        "description": inv.get('descr')
                                        })
            
            self.inv_data[host['host']].update({'board': board_data})
        except Exception:
            self.inv_data[host['host']].update({'board': []})
      

    def get_sfps(self, host,inventory, device):
        
        try:
            sfps=['sfp','gls','cpak','cfp', 'mpa' ,'glc','qsfp','cab']
            sfps_data = []
            print(f"Getting sfp optics data..." ,file=sys.stderr)
            for inv in inventory:
                is_sfp = False
                for sfp in sfps:
                    pid = inv['pid'].lower()
                    if (sfp in pid):
                        is_sfp =True
                        break
                    
                if is_sfp:
                    optics_data = self.get_sfp_optics_data(inv, device)
                    modes= {'LR':'single-mode','SR':'multimode','LH':'single-mode','LX':'single-mode', 'SX':'multimode', '3M':'multimode'}
                    mode = ''
                    for key, value in modes.items():
                        if key in inv['pid']:
                            mode = value
                            break
                    
                    speed = re.findall(r'(\d+)', inv.get('pid'))
                    speed = speed[0]+'G' if speed else None
                    sfp_data = {'port_name': inv.get('name'),
                        'mode': None if not mode else mode,
                        'speed': speed,
                        'hw_version': inv.get('vid'),
                        'serial_number': inv.get('sn'),
                        'port_type': optics_data.get('port_type'),
                        'connector': optics_data.get('connector'),
                        'wavelength':None if not optics_data.get('wavelength') else optics_data.get('wavelength'),
                        'optical_direction_type':None,
                        'pn_code':inv.get('pid', '').lstrip('0'),
                        'status':'Production',
                        'description': None,
                        'manufacturer': 'Arista',
                        'media_type': optics_data.get('media_type')}
                    sfps_data.append(sfp_data)

            self.inv_data[host['host']].update({"sfp":sfps_data})
        except Exception:
            self.inv_data[host['host']].update({"sfp":[]})


   
    def get_sfp_optics_data(self, inv, device):
        
        try:
            
            if("3/" in inv['name']): 
                cmd = 'show interfaces '+inv['name']+'/1 transceiver eeprom | i Connector|Wavelength|EEPROM'
            else:
                cmd = 'show interfaces '+inv['name']+' transceiver eeprom | i Connector|Wavelength|EEPROM'
            
            print(f'send command {cmd}')
            optics_data = device.send_command(cmd, textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/arista_eos_show_interfaces_transceiver_eeprom.textfsm',use_textfsm=True)
            
            for optics in optics_data:
                optics_data = {'connector':optics.get('connector'),'wavelength':optics.get('wavelength'), 'port_type':optics.get('port_type')}
            return optics_data
        except:
            return {}

if __name__ == '__main__':
    hosts = [
        {
            "host": "10.73.211.61",
            "user": "srv00282",
            "pwd": "99maAF5smUt61397"
        }]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = AristaPuller()
    print(json.dumps(puller.get_inventory_data(hosts)))