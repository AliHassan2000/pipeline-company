import traceback
from turtle import update
from typing import Set
from netmiko import Netmiko
from app import db
from datetime import datetime
import re, sys, time, json 
import threading
from collections import Counter
# import pandas as pd
from app.models.inventory_models import EDN_CORE_ROUTING, FAILED_DEVICES_EDN_EXCHANGE
from textfsm import clitable

# from app.models.inventory_models import VRF_OWNERS

class EDNCOREROUTING(object):
    def __init__(self):
        self.connections_limit = 50
        self.failed_devices=[]

    # def add_failed_devices_to_db(self, host, reason):
    #     pmFailedDb = FAILED_DEVICES_EDN_EXCHANGE()
        
    #     try:
    #         pmFailedDb.ip_address = host['device_ip']
    #         pmFailedDb.device_id = host['device_id']
    #         pmFailedDb.reason =reason
    #         pmFailedDb.date = host['time']
            
    #         self.InsertData(pmFailedDb)

    #         print('Successfully added Failed device to the Database', file = sys.stderr)
            
    #     except Exception as e:
    #         db.session.rollback()
    #         print(f"Error while inserting failed device data into DB {e}", file=sys.stderr)    
    
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
  
    def addInventoryToDB(self, host, ednCoreRouting):          
        ednDb=''
        
        for edn in ednCoreRouting:
            ednDb = EDN_CORE_ROUTING()
           
            try:
                ednDb.device_ip = host['device_ip']
                ednDb.device_id = host['device_id']
                ednDb.subnet= edn.get('subnet')
                ednDb.route_type= edn.get('route_type')
                ednDb.next_hop= edn.get('next_hop')
                ednDb.originated_from_ip= edn.get('originated_from_ip')
                ednDb.route_age= edn.get('route_age')
                ednDb.process_id= edn.get('process_id')
                ednDb.cost= edn.get('cost')
                ednDb.out_going_interface=  edn.get('out_going_interface')
                ednDb.creation_date = host['time']
                ednDb.modification_date = host['time']
                ednDb.region = host['region']
                ednDb.site_id = host['site_id']
                ednDb.created_by = host['user_id']
                ednDb.modified_by = host['user_id']
                try:
                    if edn['originated_from_ip']:
                        originatorName = db.session.execute(f"select device_id from edn_ipam_table where ip_address = '{edn['originated_from_ip']}' AND creation_date = (SELECT max(creation_date) FROM edn_ipam_table)").fetchall()[0][0]
                    else:
                        originatorName = ''
                except Exception as e:
                    traceback.print_exc()
                    print(f"Error in Parsing {e}", file=sys.stderr)

                ednDb.originator_name=  originatorName

                self.InsertData(ednDb)
                print('Successfully added to the Database',file = sys.stderr)

            except Exception as e:
                #db.session.rollback()
                traceback.print_exc()
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
            # self.add_failed_devices_to_db(host, f"Failed to Login")
                  
        if is_login==True:    
            print(f"Successfully Logged into device {host['device_ip']}", file=sys.stderr) 
            ednExchangeData={}
            try:
                ospf=""
                print("getting route ospf", file=sys.stderr)
                ospf = device.send_command('show route ospf', use_textfsm=True)
                # print("$$$$$$$$$$$$$$$", ospf[0] ,  len(ospf), file=sys.stderr)
            
                if isinstance(ospf,str):
                    print(f"Device data not found {ospf} {host['device_ip']}", file=sys.stderr)
                    raise Exception(f"Device data not found "+str(ospf))
                # print(ospf, file=sys.stderr)
                new_ospf = []
                for i in range(len(ospf)):
                    try:
                        temp = {}
                        # if ospf[i]['network'] == '0.0.0.0':
                        #     continue
                        # print("@@@@@@@@@@", ospf[i], len(ospf), file=sys.stderr)
                        if i<len(ospf)-1 and ospf[i]['network'] == ospf[i+1]['network']:
                            temp['subnet'] = ospf[i]['network'] + "/" + ospf[i]['mask']
                            temp['route_type'] = ospf[i]['protocol']
                            temp['next_hop'] = ospf[i]['next_hop']+", "+ospf[i+1]['next_hop']
                            temp['out_going_interface'] = ospf[i]['interface']+", "+ospf[i+1]['interface']
                            temp['route_age'] = ospf[i]['uptime']+", "+ospf[i+1]['uptime']
                            temp['network'] = ospf[i]['network']
                            new_ospf.append(temp)
                            continue
                        else:
                            if not any(net['network'] == ospf[i]['network'] for net in new_ospf):
                                temp['subnet'] = ospf[i]['network'] + "/" + ospf[i]['mask']
                                temp['route_type'] = ospf[i]['protocol']
                                temp['next_hop'] = ospf[i]['next_hop']
                                temp['out_going_interface'] = ospf[i]['interface']
                                temp['route_age'] = ospf[i]['uptime']
                                temp['network'] = ospf[i]['network']
                                new_ospf.append(temp)
                    except Exception as e:
                        traceback.print_exc()
                        print(f"Error in Parsing {e}", file=sys.stderr)
                    # print(temp, file=sys.stderr)
                    
                    
                    # print(new_ospf, file=sys.stderr)

                for obj in new_ospf:
                    try:
                        osp = device.send_command(f"show route {obj['subnet']}", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/cisco_xr_show_route_subnet.textfsm", use_textfsm=True)
                        # print(osp, file=sys.stderr)
                        osp = osp[0]
                        if isinstance(osp,str):
                            print(f"Device data not found {osp} {host['device_ip']}", file=sys.stderr)
                            raise Exception(f"Device data not found "+str(ospf))
                        obj['process_id'] = osp.get("process_id", "")
                        obj['cost'] = osp.get("cost", "")
                        obj['originated_from_ip'] = osp.get("originated_from_ip", "")
                        self.addInventoryToDB(host, [obj])
                    except Exception as e:
                        traceback.print_exc()
                        print(f"Error in Parsing {e}", file=sys.stderr)
                #print(new_ospf, file=sys.stderr)

                
            except Exception as e:
                print(f" detail not found {host['device_ip']}, {str(e)}", file=sys.stderr)
                ##self.add_to_failed_devices(host['device_ip'], "Failed to get EDN EXCHANGE data "+str(e))
                # traceback.print_exc()
                #failedDB
                # self.add_failed_devices_to_db(host, f"Error while inserting data into DB {e}")
  
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

    def getEdnCoreRouting(self, devices):
        puller = EDNCOREROUTING()
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
        print("EDN Core Routing Fetch Completed", file=sys.stderr)
        # print("Populating VRF Owner Details", file=sys.stderr)
        # self.populateVrfOwners()
        # print("EDN Core Routing Completed", file=sys.stderr)
        #print(f"Unique descriptions are:   {puller.dv_ip}", file=sys.stderr)

if __name__ == '__main__':

    hosts=[]

    host={
        "device_ip": "10.64.150.151",
        "user": "ciscotac",
        "pwd": "C15c0@mob1ly",
        "sw_type": "cisco_xr",
        'site_id': "MLQA",
        'device_id': "Dev1",
        'time': "11111"
    }
                
    hosts.append(host)

    puller = EDNCOREROUTING()
    puller.get_inventory_data(hosts)