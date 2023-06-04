from asyncore import poll
from datetime import datetime
from hashlib import sha1
import re, sys, time, json
import threading
import traceback
from pysnmp.hlapi import *
import pandas as pd
from xml.etree import ElementTree
import requests
from app import app ,db , tz
from app.models.inventory_models import FAILED_DEVICES_IPT_ENDPOINTS

class IPTENDPOINTSPuller(object):
    
    def __init__(self):
        self.call_managers_data=[]
        self.connections_limit = 100

    def parse_mac_address(self, phone_name):
        if("sep" in phone_name[0:3].lower()):
            mac = phone_name[3:]
            mac= ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
            return mac
        else:
            return ""
    
    def InsertData(self, obj):
        #add data to db
        try:
            #obj.creation_date= datetime.now(tz)
            #obj.modification_date= datetime.now(tz)
            db.session.add(obj)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong in Database Insertion {e}", file=sys.stderr)

        return True


    
    def add_failed_devices_to_db(self, host, reason):
       
        pmFailedDb = FAILED_DEVICES_IPT_ENDPOINTS()
        
        try:
            pmFailedDb.ip_address = host['ip']
            pmFailedDb.device_id = host['device_id']
            pmFailedDb.reason =reason
            pmFailedDb.date = host['time']
            
            self.InsertData(pmFailedDb)

            print('Successfully added Failed device to the Database', file = sys.stderr)
            
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            print(f"Error while inserting failed device data into DB {e}", file=sys.stderr)


    
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
            return self.call_managers_data

    def poll(self, host):
        print(f"Connecting to Call Manager{host['ip']}", file=sys.stderr)
        ip_telephones_data=[]
        try:
            engn = SnmpEngine()
            community = UsmUserData(host['user'], host['pwd'], host['auth-key'], authProtocol=usmHMACSHAAuthProtocol, privProtocol=usmAesCfb128Protocol)# snmp community
            #community = UsmUserData("SWVV3", "cisco123", "cisco123", authProtocol=usmHMACSHAAuthProtocol, privProtocol=usmAesCfb128Protocol)# snmp community
            transport = UdpTransportTarget((host['ip'], 161), timeout=10.0, retries=3)
            cnxt = ContextData()
            print(f"Connected {host['ip']}", file=sys.stderr)
            
            oids = {
                    'hostname':'iso.3.6.1.4.1.9.9.156.1.2.1.1.20',
                    'ip_address':'iso.3.6.1.4.1.9.9.156.1.2.1.1.6',
                    #'mac_address':'iso.3.6.1.4.1.9.9.156.1.2.1.1.2',
                    #'user': 'iso.3.6.1.4.1.9.9.156.1.2.1.1.5',
                    #'product_id': 'iso.3.6.1.4.1.9.9.156.1.1.8.1.3',
                    #'description': 'iso.3.6.1.4.1.9.9.156.1.2.1.1.4',
                    'firmware': 'iso.3.6.1.4.1.9.9.156.1.2.1.1.25',
                    }
            
            host_names = self.get_oid_data(engn, community, transport, cnxt, oids["hostname"], host)
            ip_addresses= self.get_oid_data(engn, community, transport, cnxt, oids["ip_address"], host)
            #mac_addresses= self.get_oid_data(engn, community, transport, cnxt, oids["mac_address"])
            #users= self.get_oid_data(engn, community, transport, cnxt, oids["user"])
            #product_ids= self.get_oid_data(engn, community, transport, cnxt, oids["product_id"])
            #descriptions= self.get_oid_data(engn, community, transport, cnxt, oids["description"])
            firmwares= self.get_oid_data(engn, community, transport, cnxt, oids["firmware"], host)
            
            '''
            with concurrent.futures.ThreadPoolExecutor() as executor:
                host_names = executor.submit(self.get_oid_data, engn, community, transport, cnxt, oids["hostname"])
                ip_addresses= executor.submit(self.get_oid_data, engn, community, transport, cnxt, oids["ip_address"])
                mac_addresses= executor.submit(self.get_oid_data, engn, community, transport, cnxt, oids["mac_address"])
                users= executor.submit(self.get_oid_data, engn, community, transport, cnxt, oids["user"])
                product_ids= executor.submit(self.get_oid_data, engn, community, transport, cnxt, oids["product_id"])
                descriptions= executor.submit(self.get_oid_data, engn, community, transport, cnxt, oids["description"])
                firmwares= executor.submit(self.get_oid_data, engn, community, transport, cnxt, oids["firmware"])
            
            host_names= host_names.result()
            ip_addresses= ip_addresses.result()
            mac_addresses= mac_addresses.result()
            users= users.result()
            product_ids= product_ids.result()
            descriptions= descriptions.result()
            firmwares= firmwares.result()
            '''
            print("Populating Data", file=sys.stderr)
            
            #dfArp = pd.DataFrame(columns=['Host Name', 'IP Address', "Mac Address", "User", "Product ID", "Description", "Firmware"])
            #index=0
            for hosts in host_names:
                if("sep" not in hosts["value"][0:3].lower() and "csf" not in hosts["value"][0:3].lower()):
                    continue
                else:    
                    telephone={}
                    telephone["hostname"]= hosts["value"]
                    
                    #search IP address
                    ipaddress_exists=list(filter(lambda devices: devices['device'] == hosts["device"], ip_addresses))
                    if ipaddress_exists:
                        telephone["ip_address"]=ipaddress_exists[0].get("value")
                    else:
                        telephone["ip_address"]=""
                    '''
                    #search Mac address
                    mac_exists=list(filter(lambda devices: devices['device'] == hosts["device"], mac_addresses))
                    if mac_exists:
                        mac = ':'.join('%02X' % ((int(mac_exists[0].get("value"), 16) >> 8*i) & 0xff) for i in reversed(range(6)))
                        telephone["mac_address"]=str(mac)
                    else:
                        telephone["mac_address"]=""
                    
                    #search Users
                    user_exists=list(filter(lambda devices: devices['device'] == hosts["device"], users))
                    if user_exists:
                        telephone["user"]=user_exists[0].get("value")
                    else:
                        telephone["user"]=""
                    
                    #search Product Ids
                    product_ids_exists=list(filter(lambda devices: devices['device'] == hosts["device"], product_ids))
                    if product_ids_exists:
                        telephone["product_id"]=product_ids_exists[0].get("value")
                    else:
                        telephone["product_id"]=""
                    
                    #search Descriptions
                    description_exists=list(filter(lambda devices: devices['device'] == hosts["device"], descriptions))
                    if description_exists:
                        telephone["description"]=description_exists[0].get("value")
                    else:
                        telephone["description"]=""
                    '''
                    #search Firmware
                    firmware_exists=list(filter(lambda devices: devices['device'] == hosts["device"], firmwares))
                    if firmware_exists:
                        telephone["firmware"]=firmware_exists[0].get("value")
                    else:
                        telephone["firmware"]=""

                    #dfArp.loc[index, 'Host Name'] = telephone["host_name"]
                    #dfArp.loc[index, 'IP Address'] = telephone["ip_address"]
                    #dfArp.loc[index, 'Mac Address'] = telephone["mac_address"]
                    #dfArp.loc[index, 'User'] = telephone["user"]
                    #dfArp.loc[index, 'Product ID'] = telephone["product_id"]
                    #dfArp.loc[index, 'Description'] = telephone["description"]
                    #dfArp.loc[index, 'Firmware'] = telephone["firmware"]
                    #index+=1
                    
                    ip_telephones_data.append(telephone)
            self.call_managers_data.extend(ip_telephones_data)
            
            #writer = pd.ExcelWriter('IP Telephones.xlsx')
            #dfArp.to_excel(writer, sheet_name='ipt endpoints')
            #writer.save()
            
            #print(self.ip_telephones_data)
            return ip_telephones_data
        except Exception as e:
            traceback.print_exc()
            print(f"Ip Telephones not found Exception detail==>{e}", file=sys.stderr)
            
               
    def get_oid_data(self, engn, community, transport, cnxt, oid, host):
        try:
            #print(f"SNMP walk started for OID {oid}", file=sys.stderr)
            oid = ObjectType(ObjectIdentity(oid))
            devices_info=[]
            for( errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(engn, community, transport, cnxt, oid, lexicographicMode=False): 
                if errorIndication:
                    print(f'error=>{errorIndication}', file=sys.stderr)
                    self.add_failed_devices_to_db(host, f"Failed to run SNMP walk for OID: {oid}")
                    
                elif errorStatus:
                    print('%s at %s' % (errorStatus.prettyPrint(),
                                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                    self.add_failed_devices_to_db(host, f"Failed to run SNMP walk for OID: {oid}")
                else:
                    for varBind in varBinds:
                        device_info={}
                        print(str(varBind), file=sys.stderr)
                        res = ' = '.join([x.prettyPrint() for x in varBind])
                        if 'No Such Instance' not in res:
                            result = res.split('=')[1].strip()
                            device= re.findall(r'9.9.156.\d*.\d*.\d*.\d*.\d*.(\d*)',str(varBind))
                            device_info["device"]= device[0]
                            device_info["value"]= result
                            devices_info.append(device_info)
                        else:
                            self.add_failed_devices_to_db(host, f"Failed to run SNMP walk for OID: {oid}")
                            return None
            return devices_info
        except Exception as e:
            print(f"Failed to run SNMP walk {e}", file=sys.stderr)
            self.add_failed_devices_to_db(host, f"Failed to run SNMP walk for OID: {oid}")
            #failedDB
            
            return []

    def get_api_data(self, publisher_ip, api_user, api_password, snmp_data, host):
        print("Getting API data", file=sys.stderr)
        telephones_data=[]
        parsed_data=[]
        #Get SEP Telephones
        api_data= self.send_api_request(publisher_ip, api_user, api_password, "SEP%", host)
        if not "Exception Occured" in api_data:
            api_data = ElementTree.fromstring(api_data.content)
            for telephone in api_data.iter('phone'):
                dict={}
                dict["hostname"]= telephone[0].text
                dict["description"]= telephone[1].text
                dict["product_id"]= telephone[2].text
                dict["protocol"]= telephone[3].text
                dict["calling_search_space"]= telephone[4].text
                dict["device_pool_name"]= telephone[5].text
                dict["location_name"]= telephone[6].text
                dict["resource_list_name"]= telephone[7].text
                dict["user"]= telephone[8].text
                telephones_data.append(dict)
        else:
            print(f"Failed to get response from API {api_data}", file=sys.stderr)

        #Get CSF Telephones
        api_data= self.send_api_request(publisher_ip, api_user, api_password, "CSF%", host)
        if not "Exception Occured" in api_data:
            api_data = ElementTree.fromstring(api_data.content)
            for telephone in api_data.iter('phone'):
                dict={}
                dict["hostname"]= telephone[0].text
                dict["description"]= telephone[1].text
                dict["product_id"]= telephone[2].text
                dict["protocol"]= telephone[3].text
                dict["calling_search_space"]= telephone[4].text
                dict["device_pool_name"]= telephone[5].text
                dict["location_name"]= telephone[6].text
                dict["resource_list_name"]= telephone[7].text
                dict["user"]= telephone[8].text
                telephones_data.append(dict)
                #list phone Liens
        else:
            print(f"Failed to get response from API {api_data}", file=sys.stderr)
        
        api_data= self.send_api_request(publisher_ip, api_user, api_password, "BOT%", host)
        if not "Exception Occured" in api_data:
            api_data = ElementTree.fromstring(api_data.content)
            for telephone in api_data.iter('phone'):
                dict={}
                dict["hostname"]= telephone[0].text
                dict["description"]= telephone[1].text
                dict["product_id"]= telephone[2].text
                dict["protocol"]= telephone[3].text
                dict["calling_search_space"]= telephone[4].text
                dict["device_pool_name"]= telephone[5].text
                dict["location_name"]= telephone[6].text
                dict["resource_list_name"]= telephone[7].text
                dict["user"]= telephone[8].text
                telephones_data.append(dict)
                #list phone Liens
        else:
            print(f"Failed to get response from API {api_data}", file=sys.stderr)

        api_data= self.send_api_request(publisher_ip, api_user, api_password, "TCT%", host)
        if not "Exception Occured" in api_data:
            api_data = ElementTree.fromstring(api_data.content)
            for telephone in api_data.iter('phone'):
                dict={}
                dict["hostname"]= telephone[0].text
                dict["description"]= telephone[1].text
                dict["product_id"]= telephone[2].text
                dict["protocol"]= telephone[3].text
                dict["calling_search_space"]= telephone[4].text
                dict["device_pool_name"]= telephone[5].text
                dict["location_name"]= telephone[6].text
                dict["resource_list_name"]= telephone[7].text
                dict["user"]= telephone[8].text
                telephones_data.append(dict)
                #list phone Liens
        else:
            print(f"Failed to get response from API {api_data}", file=sys.stderr)

        api_data= self.send_api_request(publisher_ip, api_user, api_password, "TAB%", host)
        if not "Exception Occured" in api_data:
            api_data = ElementTree.fromstring(api_data.content)
            for telephone in api_data.iter('phone'):
                dict={}
                dict["hostname"]= telephone[0].text
                dict["description"]= telephone[1].text
                dict["product_id"]= telephone[2].text
                dict["protocol"]= telephone[3].text
                dict["calling_search_space"]= telephone[4].text
                dict["device_pool_name"]= telephone[5].text
                dict["location_name"]= telephone[6].text
                dict["resource_list_name"]= telephone[7].text
                dict["user"]= telephone[8].text
                telephones_data.append(dict)
                #list phone Liens
        else:
            print(f"Failed to get response from API {api_data}", file=sys.stderr)

        print("Fetched API data", file=sys.stderr)

        parsed_data= self.parse_api_and_snmp_data(snmp_data, telephones_data)
        
        return parsed_data

    def parse_api_and_snmp_data(self, snmp_data, api_data):
        final_data=[]
        phones_deleted_from_api=[]
        phones_not_found=set()
        print("Parsing SNMP and API data", file=sys.stderr)
        for phone in snmp_data:
            phone_exists= list(filter(lambda api_data: api_data['hostname'] == phone['hostname'], api_data))
            if phone_exists:
                #phone['mac_address']= phone_exists[0].get('protocol', '')
                phone['description']= phone_exists[0].get('description', '')
                phone['user']= phone_exists[0].get('user', '')
                phone['product_id']= phone_exists[0].get('product_id', '')
                phone['protocol']= phone_exists[0].get('protocol', '')
                phone['calling_search_space']=phone_exists[0].get('calling_search_space', '')
                phone['device_pool_name']=phone_exists[0].get('device_pool_name', '')
                phone['location_name']=phone_exists[0].get('location_name', '')
                phone['resource_list_name']=phone_exists[0].get('resource_list_name', '')
                #print(phone_exists, file=sys.stderr)

                phone_index = next((index for (index, api_data) in enumerate(api_data) if api_data["hostname"] == phone['hostname']), None)
                del api_data[phone_index] 
                phones_deleted_from_api.append(phone['hostname'])       
            else:
                if phone['hostname'] not in phones_deleted_from_api:
                    phones_not_found.add(phone['hostname'])
        #print(f"^^^^^^^ {phones_deleted_from_api}", file=sys.stderr)
        #print(f"&&&&&&& {phones_not_found}", file=sys.stderr)
        

            #if phone['hostname'] not in phones_deleted_from_api:
            #    print(f"$$$$$ {phone['hostname']}", file=sys.stderr)
            #    phone['status']= "Removed"
                
        print("Parsing Completed", file=sys.stderr)
        print("Poulating Data")
        for phone in snmp_data:
            phone["mac_address"]= self.parse_mac_address(phone['hostname'])
            #if not phone.get('status'):
            phone["status"]= "Registered"
            final_data.append(phone)
        for phone in api_data:
            phone["mac_address"]= self.parse_mac_address(phone['hostname'])
            phone["status"]= "Unregistered"
            final_data.append(phone)

        for phone in snmp_data:
            if phone['hostname'] in phones_not_found:
                #print(f"%%%%%%% {phone['hostname']}", file=sys.stderr)
                phone['status']= "Removed"
        
        return final_data

    def send_api_request(self, publisher_ip, api_user, api_password, saearch_pattern, host):
        url=f"https://{publisher_ip}/axl/"
        #headers = {'content-type': 'application/soap+xml'}
        headers = {'content-type': 'text/xml'}
        body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.cisco.com/AXL/API/12.5">
            <soapenv:Header/>
            <soapenv:Body>
                <ns:listPhone>
                    <searchCriteria>
                        <name>{saearch_pattern}</name>
                    </searchCriteria>
                    <returnedTags>
                        <name>%</name>
                        <description>%</description>
                        <protocol>%</protocol>
                        <product>%</product>
                        <callingSearchSpaceName>%</callingSearchSpaceName>
                        <devicePoolName>%</devicePoolName>
                        <locationName>%</locationName>
                        <mediaResourceListName>%</mediaResourceListName>
                        <ownerUserName>%</ownerUserName>
                    </returnedTags>
                </ns:listPhone>
            </soapenv:Body>
        </soapenv:Envelope>"""
        try: 
            response = requests.post(url,data=body,headers=headers, verify = False, auth=(api_user, api_password))
            return response
        except Exception as e: 
            self.add_failed_devices_to_db(host, f"Failed to Get Phones data from API for Searching  {saearch_pattern}")
            return (f"Exception Occured {e}")

    def getLine(self, publisher_ip, api_user, api_password, hostname, host):  
        
        login_tries = 10
        is_login = False
        c = 0
       
        try:
            url=f"https://{publisher_ip}/axl/"
            #headers = {'content-type': 'application/soap+xml'}
            headers = {'content-type': 'text/xml'}
            body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.cisco.com/AXL/API/10.5">
                        <soapenv:Header/>
                        <soapenv:Body>
                            <ns:getPhone>
                                <name>{hostname}</name>
                            </ns:getPhone>
                        </soapenv:Body>
                    </soapenv:Envelope>"""
            while c < login_tries :
                try: 
                    response = requests.post(url,data=body,headers=headers, verify = False, auth=(api_user, api_password))
                    api_data = ElementTree.fromstring(response.content)
                    for pattern in api_data.iter('pattern'):
                        return pattern.text
                    is_login = True
                    break
                except Exception as e:
                    c +=1
                    traceback.print_exc() 
                    print (f"Exception Occured in parsing lines api {e}", file=sys.stderr)
                    return f"Exception Occured {e}"
            if is_login == False:
                #failedDB
                self.add_failed_devices_to_db(host, f"Failed to get Extensions from API")
        
        except Exception as e: 
            traceback.print_exc()
            print (f"Exception Occured in line api request {e}", file=sys.stderr)  
            return f"Exception Occured {e}"  
        return ""
    def get_lines_data(self, publisher_ip, api_user, api_password, api_data, host):
        print("Getting Lines data", file=sys.stderr)
        index=0
        threads=[]
        for phone in api_data:    
            try:
                index+=1
                self.getExtension(phone, publisher_ip, api_user, api_password, host)
                print(f"Getting Extension of Line {index}", file=sys.stderr)
            except Exception as e:
                print("Error is lines {e}", file=sys.stderr)
            #print(f"Getting Extension of Line {index}", file=sys.stderr)
            #index+=1
            #th = threading.Thread(target=self.getExtension, args=(phone, publisher_ip, api_user, api_password,))
            #th.start()
            #threads.append(th)
            #if len(threads) == 20: 
            #    for t in threads:
            #        t.join()
            #    threads =[]
        
        #else:
        #    for t in threads: # if request is less than connections_limit then join the threads and then return data
        #        t.join()    
        print("Finished Getting Lines Data", file=sys.stderr)
        return api_data

    def getExtension(self,phone, publisher_ip, api_user, api_password, host):
        try:
            #Get Telephones Lines            
            line_data= self.getLine(publisher_ip, api_user, api_password, phone.get('hostname'), host)
            if not "Exception Occured" in line_data:
                if line_data:
                    phone.update(extensions= line_data)
                    #phone['extensions']= line_data
                else:
                    phone.update(extensions="")
            else:
                phone.update(extensions="")
            #print(f"Successfully got Line No:  host: {phone.get('hostname')}", file=sys.stderr)
        except Exception as e: 
            traceback.print_exc()

            print(f"Failed to get Line No: host: {phone.get('hostname')}", file=sys.stderr)
            print (f"Exception Occured in getting lines {e}", file=sys.stderr)  
    
        
if __name__ == '__main__':
    hosts = [{
            'ip':'10.42.158.4',
            'user':'SWVV3',
            'pwd':'cisco1234',
            'auth-key':'cisco1234',
            'ipt-list':[{
                'ip':'10.42.158.4',
                'device_name':'DAM-ADM-IPT-SUB5',
                'function':'Call Manager'},
                        {
                'ip':'10.42.158.5',
                'device_name':'DAM-ADM-IPT-IMSUB4',
                'function':'IM and Presence'},
                        {'ip':'10.42.158.6',
                         'device_name':'DAM-ADM-IPT-PCP2',
                         'function':'Prime Provisioning'}
            ]
        }]
    
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = IPTENDPOINTSPuller()
    print(json.dumps(puller.get_inventory_data(hosts)))



    '''
    with concurrent.futures.ThreadPoolExecutor() as executor:
                host_names = executor.submit(self.get_oid_data, engn, community, transport, cnxt, oids["hostname"])
                ip_addresses= executor.submit(self.get_oid_data, engn, community, transport, cnxt, oids["ip_address"])
                mac_addresses= executor.submit(self.get_oid_data, engn, community, transport, cnxt, oids["mac_address"])
                users= executor.submit(self.get_oid_data, engn, community, transport, cnxt, oids["user"])
                product_ids= executor.submit(self.get_oid_data, engn, community, transport, cnxt, oids["product_id"])
                descriptions= executor.submit(self.get_oid_data, engn, community, transport, cnxt, oids["description"])
                firmwares= executor.submit(self.get_oid_data, engn, community, transport, cnxt, oids["firmware"])
            host_names= host_names.result()
            ip_addresses= ip_addresses.result()
            mac_addresses= mac_addresses.result()
            users= users.result()
            product_ids= product_ids.result()
            descriptions= descriptions.result()
            firmwares= firmwares.result()
    '''

    #if api response failed
