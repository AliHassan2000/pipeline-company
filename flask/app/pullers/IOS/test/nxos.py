from netmiko import Netmiko
from datetime import datetime


class NXOSPuller(object):
    
    def __init__(self):
        self.inv_data = {}

    def get_inventory_data(self, hosts):
        
        for host in hosts:
            print(f"Connecting to {host['host']}")
            try:
                device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type='cisco_nxos')
                print(f"Success: logged in {host['host']}")
            except Exception as e:
                print(f"Falied to login {host['host']}")
                self.inv_data[host['host']] = {"error":"Login Failed"}
                continue

            try:
                board_data =[]
                inv = device.send_command("show inventory", use_textfsm=True)
                version = device.send_command("show version", use_textfsm=True)
                version = version[0]['os'] if version else ''
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                for data in inv:
                    if 'chassis' in data['descr'].lower():
                        self.inv_data[host['host']].update({'device':
                                                    {'ip_addr': host['host'], 'serial_number': data['sn'], 'pn_code': data['pid'], 'hw_version': data['vid'], "software_version": version, "desc": data['descr'], "max_power": "", "manufecturer": "", "status": "active", "authentication": ""}})
                        continue
                    modules_data = self.board_data_parser(data, version)
                    if modules_data:board_data.append(modules_data)
                
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'board': board_data})
                    self.inv_data[host['host']].update({'sfp': []})
                    self.inv_data[host['host']].update({'sub_board': []})
                    self.get_sfp_sub_module(host['host'])

            except Exception as e:
                print(f"Exception in device_details==> {e}")
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'device_detail': {}})

            try:
                license = device.send_command("show license usage", use_textfsm=True)
                license_data = []
                for l in license:
                    l_info = {
                                "name": l.get('feature',''),
                                "description": l.get('comments',''),
                                "activation_date": '',
                                "expiry_date": l.get('expiry_date',''),
                                "grace_period": "",
                                "serial_number": "",
                                "status": l.get('status',''),
                                "capacity": "",
                                "usage": "",
                                "pn_code": ""
                                }
                    license_data.append(l_info)
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'license': license_data})
            except Exception as ex:
                print("Exception in license_details ==>"+str(ex))
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'license': []})

        return self.inv_data

    def board_data_parser(self, info, version):
        try:
            data = {
                "board_name": info['name'],
                "serial_number": info.get('sn',''),
                "pn_code": info['pid'],
                "hw_version": info.get('vid',''),
                "slot_id": info['name'],
                "status": "active",
                "software_version": version,
                "description": info['descr']
            }
            return data
        except:
            return None

    def get_sfp_sub_module(self, host):
        sfps=['SFP','GLC','CPAK','CFP']
        sub_modules=['MPA']
        for sfp in sfps:
            for index, brd in enumerate(self.inv_data[host]['board']):
                if sfp in brd['pn_code']:
                    get_sfp = self.inv_data[host]['board'].pop(index)
                    sfp_data = {'port_name': get_sfp['board_name'],
                                'mode': '',
                                'speed': '100G' if '100G' in get_sfp['pn_code'] else '',
                                'hw_version': get_sfp['hw_version'],
                                'serial_number': get_sfp['serial_number'],
                                'port_type': '',
                                'connector': '',
                                'wavelength':'',
                                'optical_direction_type':'',
                                'pn_code':get_sfp['pn_code'],
                                'status':'',
                                'description': get_sfp['description'],
                                'model-name': get_sfp['board_name'],
                                'manufacturer': '',
                                'media_type': ''}
                    self.inv_data[host]['sfp'].append(sfp_data)

            self.inv_data # 2nd loop gets new data on each iteration
        
        for sub_m in sub_modules:
            for index, brd in enumerate(self.inv_data[host]['board']):
                if sub_m in brd['pn_code']:
                    get_sub_m = self.inv_data[host]['board'].pop(index)
                    sub_m_data = {'subboard_name': get_sub_m['board_name'],
                                'subboard_type':'',
                                'slot_number':'',
                                'subslot_number':"",
                                'hw_version': get_sub_m['hw_version'],
                                'serial_number': get_sub_m['serial_number'],
                                'pn_code':get_sub_m['pn_code'],
                                'status':'',
                                'description': get_sub_m['description'],
                                'model-name': get_sub_m['board_name'],
                                }
                    self.inv_data[host]['sub_board'].append(sub_m_data)

            self.inv_data # 2nd loop gets new data on each iteration

if __name__ == '__main__':
    hosts = [
        {
            "host": "10.42.1.132",
            "user": "srv00047",
            "pwd": "5FPB4!!1c9&g*iJ9"
        }]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = Puller()
    print(puller.get_inventory_data(hosts))