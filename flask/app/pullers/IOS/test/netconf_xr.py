from ncclient import manager
import xml.dom.minidom
import json, sys
import xmltodict
from datetime import datetime
from collections import OrderedDict

class XRPuller(object):

    def __init__(self):
        self.inv_data = {}
        

    def get_inventory_data(self, hosts):
        print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), file=sys.stderr)
        
        for host in hosts:
            print(f"Connecting to {host['host']}", file=sys.stderr)
            try:
                m = manager.connect(host=host['host'],
                                    port=830,
                                    username=host['user'],
                                    password=host['pwd'],
                                    timeout=600,
                                    device_params={'name': "iosxr"})
                print(f"Success: logged in {host['host']}", file=sys.stderr)
            except Exception as e:
                print(f"Falied to login {host['host']}", file=sys.stderr)
                self.inv_data[host['host']] = {"error":"Login falied"}
                continue
            try:
                # device deatils
                print("Fetching device details...", file=sys.stderr)
                hostname_filter = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                                  <platform-inventory xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-plat-chas-invmgr-oper">
                                    <racks>
                                        <rack>
                                        <attributes>
                                            <basic-info/>
                                        </attributes>
                                        <name/>
                                        </rack>
                                    </racks>
                                    </platform-inventory>
                              </filter>
                          '''
                response = m.get(hostname_filter)
                xml_json = xmltodict.parse(response.xml)["rpc-reply"]["data"]
                # xmlDom = xml.dom.minidom.parseString( str( response))
                # print(xmlDom.toprettyxml( indent = "  " ))
                inv = dict(xml_json['platform-inventory'])
                inv = json.loads(json.dumps(inv))
                data = inv['racks']['rack']['attributes']['basic-info']
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                self.inv_data[host['host']].update({'device':
                                               {'ip_addr': host['host'], 'serial_number': data['serial-number'], 'pn_code': data['model-name'], 'hw_version': data['hardware-revision'], "software_version": data['software-revision'], "desc": data['description'], "max_power": "", "manufecturer": "", "status": "active", "authentication": ""}})
            except Exception as e:
                print(f"Exception in device_details==> {e}", file=sys.stderr)
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'device_detail': {}})

            try:
                # board details
                print("Fetching board details...", file=sys.stderr)
                board_data = []
                
                hostname_filter = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                                   <platform-inventory xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-plat-chas-invmgr-oper">
                                      <racks>
                                        <rack>
                                          <slots>
                                            <slot>
                                              <cards/>
                                              <name/>
                                            </slot>
                                          </slots>
                                          <name/>
                                        </rack>
                                      </racks>
                                    </platform-inventory>
                                        
                                  </filter>
                              '''
                response = m.get(hostname_filter)
                xml_json = xmltodict.parse(response.xml)["rpc-reply"]["data"]
                platform_data = dict(xml_json['platform-inventory'])
                platform_data = json.loads(json.dumps(platform_data))
                for m in platform_data['racks']['rack']['slots']['slot']:
                    card_data = m.get('cards', {}).get('card', {})
                    basic_info = card_data.get('attributes', {}).get(
                        'basic-info') if card_data else None
                    if basic_info:
                        board_data.append(self.board_data_parser(basic_info))
                    modules = card_data.get('modules', {})
                    m_data = modules.get('attributes', {}).get(
                        'basic-info') if modules else None
                    if m_data:
                        m_info = self.board_data_parser(m_data)
                        if m_info:
                            board_data.append(m_info)
                    if modules.get('module') and isinstance(modules.get('module'), list):
                        for sub_m in modules['module']:
                            sub_modules = sub_m.get(
                                'sub-modules').get('sub-module') if sub_m.get('sub-modules') else None
                            if sub_modules and isinstance(sub_modules, dict):
                                sub_modules_data = sub_modules.get(
                                    'attributes', {}).get('basic-info')
                                sub_module_info = self.board_data_parser(
                                    sub_modules_data) if sub_modules_data else None
                                if sub_module_info:
                                    board_data.append(sub_module_info)

                    # getting modules data from sub-slots
                    sub_slots = card_data.get('sub-slots').get('sub-slot') if card_data.get('sub-slots') else None
                    if sub_slots:
                        for ps in sub_slots:
                            port = ps.get('module',{})
                            if port:
                                ps_data = port.get('attributes',{}).get('basic-info')
                                ps_info = self.board_data_parser(ps_data) if ps_data else None
                                if ps_info: board_data.append(ps_info)

                            module_port_slots = port.get('port-slots',{}).get('port-slot') if port.get('port-slots',{}) else None
                            if module_port_slots:
                                for x in module_port_slots:
                                    sm_p = x.get('port',{})
                                    sm_p_data = sm_p.get('attributes', {}).get('basic-info') if sm_p else None
                                    sm_p_info = self.board_data_parser(sm_p_data) if sm_p_data else None
                                if sm_p_info:
                                    board_data.append(sm_p_info)
                    
                    # getting modules data from port-slots
                    p_slots = card_data.get('port-slots').get('port-slot') if card_data.get('port-slots') else None
                    if p_slots:
                        for ps in p_slots:
                            port = ps.get('port',{})
                            if port:
                                ps_data = port.get('attributes',{}).get('basic-info')
                                ps_info = self.board_data_parser(ps_data) if ps_data else None
                                if ps_info: board_data.append(ps_info)


                    # getting sfp data here
                    port_slots = card_data.get(
                        'port-slots').get('port-slot') if card_data.get('port-slots') else None
                    if port_slots:
                        for p in port_slots:
                            ports = p.get('portses', {}).get('ports')
                            sfp_basic_data = ports.get('attributes', {}).get('basic-info') if ports else None
                            sfp_basic_info =  self.board_data_parser(sfp_basic_data) if sfp_basic_data else None
                            if sfp_basic_info: board_data.append(sfp_basic_info)

                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'board': board_data})
                    self.inv_data[host['host']].update({'sfp': []})
                    self.inv_data[host['host']].update({'sub_board': []})
                    self.get_sfp_sub_module(host['host'])
            except Exception as ex:
                print("Exception in board_details ==>"+str(ex), file=sys.stderr)
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'board': []})

            try:
                # license details
                print("Fetching license details...", file=sys.stderr)
                # hostname_filter = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">

                #                 </filter>
                #               '''
                # response = m.get(hostname_filter)
                # xml_json = xmltodict.parse(response.xml)["rpc-reply"]["data"]
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'license': {}})
            except Exception as ex:
                print("Exception in license_details ==>"+str(ex), file=sys.stderr)
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'license': {}})
        return self.inv_data

    def board_data_parser(self, info):
        try:
            data = {
                "board_name": info['name'],
                "serial_number": info.get('serial-number',''),
                "pn_code": info['model-name'],
                "hw_version": info.get('hardware-revision',''),
                "slot_id": info['name'],
                "status": "active",
                "software_version": info.get('software-revision', ''),
                "description": info['description']
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
    # with open('credentials.json') as inventory:
    #     inv = json.loads(inventory.read())
    hosts = [
        {
            "host": "10.66.211.30",
            "user": "srv00047",
            "pwd": "5FPB4!!1c9&g*iJ9"
        },
        {
            "host": "10.219.60.7",
            "user": "srv00047",
            "pwd": "5FPB4!!1c9&g*iJ9"
        }]
    puller = Puller()
    print(puller.get_inventory_data(hosts), file=sys.stderr)
