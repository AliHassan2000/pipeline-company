from ncclient import manager
import xml.dom.minidom
import json
import xmltodict
from datetime import datetime
from collections import OrderedDict

class Puller(object):

    def __init__(self):
        self.inv_data = {}

    def get_operational_data(self, hosts):
        
        for host in hosts:
            print(f"Connecting to {host['host']}")
            try:
                m = manager.connect(host=host['host'],
                                    port=830,
                                    username=host['user'],
                                    password=host['pwd'],
                                    timeout=600,
                                    device_params={'name': "iosxr"})
                print(f"Success: logged in {host['host']}")
            except Exception as e:
                print(f"Falied to login {host['host']}")
                self.inv_data[host['host']]={"error":"Login failed"}
                continue


            # cpu details 
            try:
                cpu_data = []
                print("Fetching cpu details...")
                hostname_filter = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                                    <system-monitoring xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-wdsysmon-fd-oper">
                                        <cpu-utilization>
                                        <node-name></node-name>
                                        <total-cpu-one-minute></total-cpu-one-minute>
                                        <total-cpu-five-minute></total-cpu-five-minute>
                                        <total-cpu-fifteen-minute></total-cpu-fifteen-minute>
                                        </cpu-utilization>
                                    </system-monitoring>
                                    </filter>
                                '''
                response = m.get(hostname_filter)
                xml_json = xmltodict.parse(response.xml)["rpc-reply"]["data"]
                cpu_d = dict(xml_json['system-monitoring'])
                cpu_detalis = json.loads(json.dumps(cpu_d['cpu-utilization']))
                if isinstance(cpu_detalis, list):
                    for cpu in cpu_detalis:
                        cpu_data.append(cpu)
                elif isinstance(cpu_detalis, dict):
                    cpu_data.append(cpu_detalis)

                if host['host'] not in self.inv_data:
                        self.inv_data[host['host']] = {}
                        self.inv_data[host['host']].update({"cpu":cpu_data})
            except Exception as ex:
                print("Exception in cpu_details ==>"+str(ex))
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'cpu':[]})
        

            
            # memory details ==> 
            try:
                mem_data = []
                print("Fetching memory details...")
                hostname_filter = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                                    <watchdog xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-wd-oper">
                                        <nodes>
                                        <node>
                                            <node-name></node-name>
                                            <memory-state>
                                            </memory-state>
                                        </node>
                                        </nodes>
                                    </watchdog>
                                    </filter>
                            '''
                response = m.get(hostname_filter)
                xml_json = xmltodict.parse(response.xml)["rpc-reply"]["data"]
                if isinstance(xml_json, OrderedDict):
                    mem_details = self.recursive_ordered_dict_to_dict(xml_json)
                    if isinstance(mem_details, list):
                            for m in mem_details['watchdog']['nodes']['node']:
                                    if isinstance(m, OrderedDict):
                                        memory_info = self.recursive_ordered_dict_to_dict(m)
                                        mem_data.append(memory_info)
                    elif isinstance(mem_details, dict):
                        mem_data.append(mem_details['watchdog']['nodes']['node'])
                                
                    if host['host'] in self.inv_data:
                            self.inv_data[host['host']].update({'memory_data':mem_data})
            except Exception as ex:
                if host['host'] in self.inv_data:
                        self.inv_data[host['host']].update({'memory_data':[]})
                print("Exception in memory_details ==>"+str(ex))

            # cdp details 
            try:
                cdp_data = []
                print("Fetching cdp details...")
                hostname_filter = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                                <cdp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-cdp-oper">
                                    <nodes>
                                    <node>
                                        <neighbors>
                                        <details>
                                            <detail/>
                                        </details>
                                        </neighbors>
                                        <node-name/>
                                    </node>
                                    </nodes>
                                </cdp>
                                </filter>
                            '''
                response = m.get(hostname_filter)
                xml_json = xmltodict.parse(response.xml)["rpc-reply"]["data"]
                if isinstance(xml_json, OrderedDict):
                    cdp_details = self.recursive_ordered_dict_to_dict(xml_json)
                    for c in cdp_details['cdp']['nodes']['node']:
                            if isinstance(c, OrderedDict):
                                cdp = self.recursive_ordered_dict_to_dict(c)
                                cdp_data.append(cdp)
                            if isinstance(c, dict):
                                cdp_data.append(c)

                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'cdp_data':cdp_data})
            except Exception as ex:
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'cdp_data':[]})
                print("Exception in cdp_details ==>"+str(ex))

            try:
                # lldp details
                lldp_data = []
                print("Fetching lldp details...")
                hostname_filter = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                                <lldp xmlns="http://openconfig.net/yang/lldp">
                                <interfaces>
                                    <interface>
                                    <neighbors>
                                        <neighbor>
                                        <state>
                                        </state>
                                        </neighbor>
                                    </neighbors>
                                    </interface>
                                </interfaces>
                                </lldp>
                                </filter>
                            '''
                response = m.get(hostname_filter)
                ldp_n = []
                xml_json = xmltodict.parse(response.xml)["rpc-reply"]["data"]
                if isinstance(xml_json, OrderedDict):
                    lldp_details = self.recursive_ordered_dict_to_dict(xml_json)
                    for l in lldp_details['lldp']['interfaces']['interface']:
                            if isinstance(l, OrderedDict):
                                lldp = self.recursive_ordered_dict_to_dict(l)
                                lldp_neighbour = lldp['neighbors']['neighbor']
                                if isinstance(lldp_neighbour, list):
                                        for x in lldp_neighbour:
                                            if isinstance(x, OrderedDict):
                                                lldp_dict = self.recursive_ordered_dict_to_dict(x)
                                                ldp_n.append(lldp_dict)
                                        lldp['neighbors'].update({'neighbor':ldp_n})
                                lldp_data.append(lldp)
                            if isinstance(l, dict):
                                lldp_data.append(l)
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'lldp_data':lldp_data})
            except Exception as ex:
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'lldp_data':[]})
                print("Exception in lldp_details ==>"+str(ex))


            # # fib(operational data) 
            # try:
            #     print("Fetching fib details...")
            #     hostname_filter = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            #                     <fib xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-fib-common-oper">
            #                         <nodes>
            #                         <node>
            #                             <protocols>
            #                             <protocol>
            #                                 <fib-summaries>
            #                                 <fib-summary>
            #                                     <routes/>
            #                                     <vrf-name/>
            #                                 </fib-summary>
            #                                 </fib-summaries>
            #                                 <protocol-name/>
            #                             </protocol>
            #                             </protocols>
            #                             <node-name/>
            #                         </node>
            #                         </nodes>
            #                     </fib>
            #                     </filter>
            #                 '''
            #     response = m.get(hostname_filter)
            #     xml_json = xmltodict.parse(response.xml)["rpc-reply"]["data"]
            #     fib_details = self.recursive_ordered_dict_to_dict(xml_json)
            #     fib_details = fib_details['fib']['nodes']['node']
            #     if host['host'] in self.inv_data:
            #         self.inv_data[host['host']].update({'fib_data':fib_details})
            # except Exception as ex:
            #     if host['host'] in self.inv_data:
            #         self.inv_data[host['host']].update({'fib_data':{}})
            #     print("Exception in fib_details ==>"+str(ex))
            
            # # lfib
            # try:
            #     print("Fetching lfib details...")
            #     hostname_filter = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            #                         <mpls-forwarding xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-fib-common-oper">
            #                         <nodes>
            #                             <node>
            #                             <forwarding-summary>
            #                             <label-switched-entries/>
            #                             </forwarding-summary>
            #                             </node>
            #                             </nodes>
            #                         </mpls-forwarding>
            #                         </filter>
            #                         '''
            #     response = m.get(hostname_filter)
            #     xml_json = xmltodict.parse(response.xml)["rpc-reply"]["data"]
            #     lfib_details = self.recursive_ordered_dict_to_dict(xml_json)
            #     lfib_details = lfib_details['mpls-forwarding']['nodes']['node']
            #     if host['host'] in self.inv_data:
            #         self.inv_data[host['host']].update({'lfib_data':lfib_details})
            # except Exception as ex:
            #     if host['host'] in self.inv_data:
            #         self.inv_data[host['host']].update({'lfib_data':{}})
            #     print("Exception in fib_details ==>"+str(ex))


            
            # # ldp details(operational data)
            # try:
            #     print("Fetching ldp details...")
            #     hostname_filter = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            #                         <mpls-ldp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-mpls-ldp-oper">
            #                         <nodes>
            #                         <node>
            #                             <default-vrf>
            #                             <neighbors>
            #                                 <neighbor/>
            #                             </neighbors>
            #                             </default-vrf>
            #                             <node-name/>
            #                         </node>
            #                         </nodes>
            #                     </mpls-ldp>
            #                     </filter>
            #                     '''
            #     response = m.get(hostname_filter)
            #     xml_json = xmltodict.parse(response.xml)["rpc-reply"]["data"]
            #     ldp_details = self.recursive_ordered_dict_to_dict(xml_json)
            #     ldp_details = ldp_details['mpls-ldp']['nodes']['node']
            #     if host['host'] in self.inv_data:
            #         self.inv_data[host['host']].update({'ldp_data':ldp_details})
            # except Exception as ex:
            #     if host['host'] in self.inv_data:
            #         self.inv_data[host['host']].update({'ldp_data':{}})
            #     print("Exception in fib_details ==>"+str(ex))

            # # isis-oper details(operational data) 
            # try:
            #     print("Getting isis details....")
            #     hostname_filter = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            #                         <isis xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-clns-isis-oper">
            #                             <instances>
            #                             <instance>
            #                                 <instance-name></instance-name>
            #                                 <neighbors>
            #                                     <neighbor>
            #                                     </neighbor>
            #                                 </neighbors>
            #                                 </instance>
            #                             </instances>
            #                         </isis>
            #                     </filter>
            #                 '''
            #     response = m.get(hostname_filter)
            #     xml_json = xmltodict.parse(response.xml)["rpc-reply"]["data"]
            #     isis_details = self.recursive_ordered_dict_to_dict(xml_json)
            #     isis_details = isis_details['isis']['instances']['instance']
            #     if host['host'] in self.inv_data:
            #         self.inv_data[host['host']].update({'isis_data':isis_details})

            # except Exception as ex:
            #     if host['host'] in self.inv_data:
            #         self.inv_data[host['host']].update({'isis_data':{}})
            #     print("Exception in isis_details ==>"+str(ex))


            # # interface stats details(operational data)

            # interfaces_data = {}
            # try:
                
            #     print("Fetching interface stats details...")
            #     hostname_filter = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            #                     <infra-statistics xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-infra-statsd-oper">
            #                         <interfaces>
            #                             <interface>
            #                             <interface-name/>
            #                             <data-rate></data-rate>
            #                             <generic-counters></generic-counters>
            #                             </interface>
            #                         </interfaces>
            #                         </infra-statistics>
            #                     </filter>
            #                 '''
            #     response = m.get(hostname_filter)
            #     xml_json = xmltodict.parse(response.xml)["rpc-reply"]["data"]
            #     stats = dict(xml_json['infra-statistics'])
            #     statistics = json.loads(json.dumps(stats))
            #     interfaces_data['interface_stats'] = statistics
            # except Exception as ex:
            #     print("Exception in interface_stats_details ==>"+str(ex))

            # try:
            #     # interfaces details
            #     print("Fetching interface details...")
            #     hostname_filter = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            #                     <interfaces xmlns="http://openconfig.net/yang/interfaces">
            #                         <interface>
            #                         <subinterfaces>
            #                         </subinterfaces>
            #                         <state>
            #                         </state>
            #                         </interface>
            #                     </interfaces>
            #                     </filter>
            #                 '''
            #     response = m.get(hostname_filter)
            #     xml_json = xmltodict.parse(response.xml)["rpc-reply"]["data"]
            #     intf_state_data = dict(xml_json['interfaces'])
            #     intf_state_data = json.loads(json.dumps(intf_state_data))
            #     intf_state_data = self.recursive_ordered_dict_to_dict(intf_state_data)
            #     interfaces_data['interfaces'] = intf_state_data
            # except Exception as ex:           
            #     print("Exception in interface_details ==>"+str(ex))

            # try:
            #     final_data =[]
            #     get_infra_data = interfaces_data['interface_stats']['interfaces']['interface']
            #     for i in get_infra_data:
            #             intf_stats =       {'interface-name':i['interface-name'],
            #                             'utilization':{'input-data-rate':i.get('data-rate',{}).get('input-data-rate',''),
            #                                             'input-packet-rate':i.get('data-rate',{}).get('input-packet-rate',''),
            #                                             'output-data-rate':i.get('data-rate',{}).get('output-data-rate',''),
            #                                             'output-packet-rate':i.get('data-rate',{}).get('output-packet-rate','')} if i.get('data-rate') else {},
            #                                 'speed':i.get('data-rate',{}).get('bandwidth',''),
            #                                 'drops':{'input-drops':i.get('generic-counters',{}).get('input-drops',''),
            #                                         'output-drops':i.get('generic-counters',{}).get('output-drops','')} if i.get('generic-counters') else {},
            #                                 'errors':{'input-errors':i.get('generic-counters',{}).get('input-errors',''),
            #                                             'output-errors':i.get('generic-counters',{}).get('output-errors','')} if i.get('generic-counters') else {},
            #                                     }
            #             for x in interfaces_data['interfaces']['interface']:
            #                 if x['name']==i['interface-name']:
            #                         intf_stats2 = {'mtu':x['state']['mtu'] if x.get('state') else '',
            #                                         'status':x['state'].get('oper-status') if x.get('state') else '',
            #                                         'description':x['state'].get('description','') if x.get('state') else ''}
            #                         intf_stats.update(intf_stats2)
            #             final_data.append(intf_stats)
            #     if host['host'] in self.inv_data:
            #         self.inv_data[host['host']].update({'interfaces':final_data})
            # except Exception as e:
            #     if host['host'] in self.inv_data:
            #         self.inv_data[host['host']].update({'interfaces':[]})
            #     print("Exception "+str(e))

        return self.inv_data   

    def recursive_ordered_dict_to_dict(self, ordered_dict):
        simple_dict = {}

        for key, value in ordered_dict.items():
            if isinstance(value, OrderedDict):
                simple_dict[key] = self.recursive_ordered_dict_to_dict(value)
            elif isinstance(value, list):
                new_value = []
                for x in value:
                        if isinstance(x, OrderedDict):
                            item = self.recursive_ordered_dict_to_dict(x)
                            new_value.append(item)
                simple_dict[key] = new_value
            else:
                simple_dict[key] = value

        return simple_dict




if __name__ == '__main__':
    hosts = [
        {
            "host": "10.66.211.30",
            "user": "srv00047",
            "pwd": "5FPB4!!1c9&g*iJ9"
        }]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = Puller()
    print(puller.get_operational_data(hosts))
