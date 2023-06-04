import traceback
from turtle import update
from typing import Set
from netmiko import Netmiko
from app import db
from datetime import datetime
import re, sys, time, json 
import threading
from collections import Counter
import pandas as pd
from app.models.inventory_models import EDN_EXCHANGE, VRF_ROUTES, FAILED_DEVICES_EDN_EXCHANGE
from textfsm import clitable

from app.models.inventory_models import VRF_OWNERS

class EDNEXCHANGE(object):
    def __init__(self):
        self.connections_limit = 50
        self.failed_devices=[]

    def add_failed_devices_to_db(self, host, reason):
        pmFailedDb = FAILED_DEVICES_EDN_EXCHANGE()
        
        try:
            pmFailedDb.ip_address = host['device_ip']
            pmFailedDb.device_id = host['device_id']
            pmFailedDb.reason =reason
            pmFailedDb.date = host['time']
            
            self.InsertData(pmFailedDb)

            print('Successfully added Failed device to the Database', file = sys.stderr)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error while inserting failed device data into DB {e}", file=sys.stderr)    
    
    def InsertData(self, obj):
        #add data to db
        try:        
            db.session.rollback()
            db.session.add(obj)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong in Database Insertion {e}", file=sys.stderr)

        return True
    
    def UpdateData(obj):
    #add data to db
    #print(obj, file=sys.stderr)
        try:
            # db.session.flush()

            db.session.merge(obj)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Update {e}", file=sys.stderr)
        
        return True
  
    def addInventoryToDB(self, host, ednExchanges):          
        #for ednExchange in ednExchange_data:
        ednExchangeDb=''
        
        for ednExchange in ednExchanges:
            ednExchangeDb = EDN_EXCHANGE()
           
            try:
                if ednExchange.get('name')== "OOB-MGMT":
                    continue
                
                ednExchangeDb.device_ip = host['device_ip']
                ednExchangeDb.device_id = host['device_id']
                ednExchangeDb.vrf_name= ednExchange.get('name')
                ednExchangeDb.rd= ednExchange.get('default_rd')
                ednExchangeDb.interfaces= ','.join(ednExchange.get('interfaces'))
                ednExchangeDb.ibgp_ip= ednExchange.get('ibgp_ip')
                ednExchangeDb.ibgp_as=  ednExchange.get('ibgp_as')
                ednExchangeDb.ibgp_up_time= ednExchange.get('ibgp_up_time')
                ednExchangeDb.ibgp_prefix= ednExchange.get('ibgp_prefix')
                ednExchangeDb.ebgp_ip= ednExchange.get('ebgp_ip')
                ednExchangeDb.ebgp_as=  ednExchange.get('ebgp_as')
                ednExchangeDb.ebgp_up_time= ednExchange.get('ebgp_up_time')
                ednExchangeDb.ebgp_prefix= ednExchange.get('ebgp_prefix')
                ednExchangeDb.ebgp_advertised_routes=  ednExchange.get('ebgp_advertised_routes').rstrip(',') if ednExchange.get('ebgp_advertised_routes') else ednExchange.get('ebgp_advertised_routes')
                ednExchangeDb.creation_date = host['time']
                ednExchangeDb.modification_date = host['time']
                ednExchangeDb.region = host['region']
                ednExchangeDb.site_id = host['site_id']
                ednExchangeDb.created_by = host['user_id']
                ednExchangeDb.modified_by = host['user_id']

                self.InsertData(ednExchangeDb)
                print('Successfully added to the Database',file = sys.stderr)

                try:
                    #print(f"%%% {ednExchange.get('routes')}", file=sys.stderr)
                    for route in ednExchange.get('routes'):
                        #print(f"@@@@@ Weight is: {route['weight']}", file=sys.stderr)
                        if 'i' not in route.get('network') and '0.0.0.0' not in route.get('network') and route['weight']!="32768" :
                            try:
                                vrfRoutesDb = VRF_ROUTES()
                                vrfRoutesDb.device_ip = host['device_ip']
                                vrfRoutesDb.device_id = host['device_id']
                                vrfRoutesDb.vrf_name= ednExchange.get('name')
                                network= route.get('network')
                                if '/' in network:
                                    network= network.split('/')
                                    network= network[0]
                                vrfRoutesDb.route= network
                                vrfRoutesDb.next_hop= route.get('next_hop')
                                vrfRoutesDb.as_path= route.get('as_path')
                                origin= route.get('origin')
                                if origin== '?':
                                    vrfRoutesDb.origin= "Incomplete"
                                elif origin== 'i':
                                    vrfRoutesDb.origin= "IGP"
                                else:
                                    vrfRoutesDb.origin= origin

                                vrfRoutesDb.creation_date = host['time']
                                vrfRoutesDb.modification_date = host['time']
                                vrfRoutesDb.created_by = host['user_id']
                                vrfRoutesDb.modified_by = host['user_id']

                                self.InsertData(vrfRoutesDb)
                            except Exception as e:
                                #db.session.rollback()
                                print(f"Error while inserting routes data into DB {e}", file=sys.stderr)
                                self.add_failed_devices_to_db(host, f"Error while inserting data into DB {e}")
                                #self.add_to_failed_devices(host['device_ip'], f"Failed to insert Data to DB "+str(e))
                                #failedDB
                except Exception as e:
                    #db.session.rollback()
                    print(f"Error while inserting routes data into DB {e}", file=sys.stderr)
                    #self.add_to_failed_devices(host['device_ip'], f"Failed to insert Data to DB "+str(e))
                    #failedDB
                    self.add_failed_devices_to_db(host, f"Error while inserting data into DB {e}")

            except Exception as e:
                #db.session.rollback()
                print(f"Error while inserting data into DB {e}", file=sys.stderr)
                #self.add_to_failed_devices(host['device_ip'], f"Failed to insert Data to DB "+str(e))

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
            return ""
      
    def poll(self, host):
        print(f"Connecting to {host['device_ip']}", file=sys.stderr)
        login_tries = 10
        c = 0
        is_login = False
        sw_type = str(host['sw_type']).lower()
        sw_type = sw_type.strip()
        while c < login_tries :
            try:
                device_type= host['sw_type']
                device = Netmiko(host=host['device_ip'], username=host['user'], password=host['pwd'], device_type=device_type, timeout=600, global_delay_factor=2)
                print(f"Success: logged in {host['device_ip']}")
                is_login = True
                break
            except Exception as e:
                c +=1
                login_exception = str(e)
                
        if is_login==False:
            print(f"Falied to login {host['device_ip']}", file=sys.stderr)
            #self.add_to_failed_devices(host['device_ip'], "Failed to login to host")
            #failedDB
            self.add_failed_devices_to_db(host, f"Failed to Login")
                  
        if is_login==True:    
            print(f"Successfully Logged into device {host['device_ip']}", file=sys.stderr) 
            ednExchangeData={}
            try:
                vrfs=""
                print("getting VRFS", file=sys.stderr)
                if host['sw_type']== "cisco_ios":
                    vrfs = device.send_command('show vrf', use_textfsm=True)
                if host['sw_type']== "cisco_xr": 
                    vrfs = device.send_command('show vrf all ipv4 detail', textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/cisco_ios_xr_show_vrf_ipv4_detail.textfsm", use_textfsm=True)
            
                #print(f"Output is {vrfs}", file=sys.stderr)
                if isinstance(vrfs,str):
                    print(f"Device data not found {vrfs} {host['device_ip']}", file=sys.stderr)
                    raise Exception(f"Device data not found "+str(vrfs))
                #print(vrfs)

                print("Getting device Unique AS")
                systemAS = device.send_command('Show  run | include router bgp')
                systemAS= re.findall(r'router\s+bgp\s+(\d*)', systemAS)[0]
                #print(f"AS is: {systemAS}", file=sys.stderr)
                
                for vrf in vrfs:
                    routes=[]
                    print("getting VRFS neighbours", file=sys.stderr)

                    if host['sw_type']== "cisco_ios":
                        neighbors = device.send_command(f"show ip bgp vpnv4 vrf {vrf['name']} summary", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/cisco_ios_show_ip_bgp_vpnv4_vrf_summary.textfsm", use_textfsm=True)
                        routes = device.send_command(f"show bgp vpnv4 unicast vrf  {vrf['name']}", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/cisco_ios_show_ip_bgp.textfsm", use_textfsm=True)
                        #print(routes, file=sys.stderr)
                    if host['sw_type']== "cisco_xr":
                        neighbors = device.send_command(f"show bgp vrf {vrf['name']} summary", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/cisco_ios_show_ip_bgp_vpnv4_vrf_summary.textfsm", use_textfsm=True)
                        routes = device.send_command(f"show bgp vrf {vrf['name']}", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/cisco_xr_show_bgp.textfsm", use_textfsm=True)
                        #print(f"Routes are {routes}", file=sys.stderr)

                    #print(neighbors, file=sys.stderr)
                    if  isinstance(routes,list):
                        vrf['routes']= routes
                    else:
                        vrf['routes']= []


                    if not isinstance(neighbors,str):
                        ebgpIp=""
                        for neighbor in neighbors:
                            if neighbor['as']== systemAS:

                                vrf['ibgp_ip']= neighbor['neighbor']
                                vrf['ibgp_as']= neighbor['as']
                                vrf['ibgp_up_time']= neighbor['uptime']
                                vrf['ibgp_prefix']= neighbor['status']
                            else:
                                vrf['ebgp_ip']= neighbor['neighbor']
                                vrf['ebgp_as']= neighbor['as']
                                vrf['ebgp_up_time']= neighbor['uptime']
                                vrf['ebgp_prefix']= neighbor['status']
                                ebgpIp=neighbor['neighbor']

                        if ebgpIp:
                            print("getting VRFS neighbours Advertised Routes", file=sys.stderr)
                            if host['sw_type']== "cisco_ios":
                                ebgpRoutes = device.send_command(f"show ip bgp vpnv4 vrf {vrf['name']} neighbor {ebgpIp} advertised-routes", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/cisco_ios_show_ip_bgp_vpnv4_vrf_advertised_routes.textfsm", use_textfsm=True)
                            if host['sw_type']== "cisco_xr":
                                ebgpRoutes = device.send_command(f"show bgp vrf  {vrf['name']} neighbors {ebgpIp} advertised-routes", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/cisco_ios_show_ip_bgp_vpnv4_vrf_advertised_routes.textfsm", use_textfsm=True)

                            #print(ebgpRoutes)
                            
                            if not isinstance(ebgpRoutes,str):
                                advertisedRoutes=""
                                for route in ebgpRoutes:
                                    route= route.get('route')
                                    if route== "0.0.0.0":
                                        route= "0.0.0.0/0"
                                    if route== "10.0.0.0":
                                       route= "10.0.0.0/8"
                                    advertisedRoutes+=f"{route},"
                                vrf['ebgp_advertised_routes']= advertisedRoutes
                    #print(vrf, file=sys.stderr)
                ##Print to Excel
                '''
                dfObj = pd.DataFrame(columns=['DEVICE IP', 'Device ID', 'VRF Name',	'RD', 'Interfaces',	'IBGP IP',	'IBGP AS',	'IBGP Uptime', 'IBGP Status', 'EBGP IP', 'EBGP AS',	'EBGP Uptime', 'EBGP Status', 'EBGP Advertised Routes'])
                obj_in=0
   
                try:
                    for vrf in vrfs:
                        print(vrf, file=sys.stderr)
                        dfObj.loc[obj_in,'DEVICE IP'] = host['device_ip']
                        dfObj.loc[obj_in,'DEVICE ID'] = host['device_id']

                        dfObj.loc[obj_in,'VRF Name'] = vrf.get('name')
                        dfObj.loc[obj_in,'RD'] = vrf.get('default_rd')
                        dfObj.loc[obj_in,'Interfaces'] = str(vrf.get('interfaces'))

                        dfObj.loc[obj_in,'IBGP IP'] = vrf.get('ibgp_ip')
                        dfObj.loc[obj_in,'IBGP AS'] = vrf.get('ibgp_as')
                        dfObj.loc[obj_in,'IBGP Uptime'] = vrf.get('ibgp_up_time')
                        dfObj.loc[obj_in,'IBGP Status'] = vrf.get('ibgp_prefix')

                        dfObj.loc[obj_in,'EBGP IP'] = vrf.get('ebgp_ip')
                        dfObj.loc[obj_in,'EBGP AS'] = vrf.get('ebgp_as')
                        dfObj.loc[obj_in,'EBGP Uptime'] = vrf.get('ebgp_up_time')
                        dfObj.loc[obj_in,'EBGP Status'] = vrf.get('ebgp_prefix')

                        dfObj.loc[obj_in,'EBGP Advertised Routes'] = vrf.get('ebgp_advertised_routes')
                        obj_in+=1
                except Exception as e:
                    print("error writing df")
                    print(e, file=sys.stderr)

                try:
                    writer = pd.ExcelWriter(host['device_ip']+".xlsx")
                    #write dataframe to excel
                    dfObj.to_excel(writer, sheet_name="Exchanges", index=False)
                    writer.save()
                    
                    print('DataFrame is written successfully to CSV File.', file=sys.stderr)
                except Exception as e:
                    print(f'Error While writied data to CSV file {e}', file=sys.stderr)                          
                '''
                self.addInventoryToDB(host, vrfs)
            except Exception as e:
                print(f" detail not found {host['device_ip']}, {str(e)}", file=sys.stderr)
                ##self.add_to_failed_devices(host['device_ip'], "Failed to get EDN EXCHANGE data "+str(e))
                traceback.print_exc()
                #failedDB
                self.add_failed_devices_to_db(host, f"Error while inserting data into DB {e}")
  
    def FormatStringDate(self, date):
        #print(date, file=sys.stderr)
        try:

            if date is not None:
                result = datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
                return result
           
        except:
            result=datetime(2000, 1,1)
            print("date format exception", file=sys.stderr)
            return result

    def populateVrfOwners(self):
        print("Populating VRF Owners", file=sys.stderr)

        try:
            ednExchangeData = db.session.execute('SELECT edn_exchange_id, vrf_name FROM edn_exchange WHERE creation_date = (SELECT max(creation_date) FROM edn_exchange)')
            vrfOwners= VRF_OWNERS.query.all()
            if VRF_OWNERS:
                for ednExchange in ednExchangeData:
                    vrf= list(filter(lambda vrf: vrf.vrf_name == ednExchange[1], vrfOwners))
                    if vrf:
                        db.session.execute(f"update edn_exchange set owner_name='{vrf[0].owner_name }', owner_email='{vrf[0].owner_email}', owner_contact='{vrf[0].owner_contact}' where edn_exchange_id='{ednExchange[0]}';")
                        db.session.commit()
                       
                #self.UpdateData(ednExchange)  
            
        except Exception as e:
            print(f"Exception occured in Populating VRF Owners {e}", file=sys.stderr)

    def getEdnExchange(self, devices):
        puller = EDNEXCHANGE()
        hosts = []
        with open('app/cred.json') as inventory:
            inv = json.loads(inventory.read())
        for device in devices:
            
            user_name = inv['EDN']['user']
            password = inv['EDN']['pwd']

            sw_type = str(device['sw_type']).lower()
            sw_type = sw_type.strip()
            #print(sw_type,file=sys.stderr)
            
            if sw_type=='ios':
                sw_type = 'cisco_ios'
  
            elif sw_type == 'ios-xr':
                sw_type = 'cisco_xr'
           
            else:
                sw_type=''

            
            host={
                "device_ip": device["device_ip"],
                "user": user_name,
                "pwd": password,
                "sw_type": sw_type,
                'device_id':device['device_id'],
                'region':device['region'],
                'site_id':device['site_id'],
                'time': self.FormatStringDate(device["time"]),
                'user_id': device['user_id']

            }
            hosts.append(host)
                  
        puller.get_inventory_data(hosts)
        #puller.print_failed_devices()
        print("EDN Fetch Completed", file=sys.stderr)
        print("Populating VRF Owner Details", file=sys.stderr)
        self.populateVrfOwners()
        print("EDN Exchange Completed", file=sys.stderr)
        #print(f"Unique descriptions are:   {puller.dv_ip}", file=sys.stderr)

if __name__ == '__main__':

    hosts=[]

    host={
        "device_ip": "10.66.0.21",
        "user": "ciscotac",
        "pwd": "C15c0@mob1ly",
        "sw_type": "cisco_xr",
        'site_id': "MLQA",
        'device_id': "Dev1",
        'time': "11111"
    }
                
    hosts.append(host)

    puller = EDNEXCHANGE()
    puller.get_inventory_data(hosts)