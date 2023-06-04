import traceback
from typing import Set
from netmiko import Netmiko
#from app import db
from datetime import datetime
import re, sys, time, json 
import threading
from app import db
from app.models.inventory_models import F5 as F5DB, FAILED_DEVICES_F5

class F5(object):

    def __init__(self):
        self.connections_limit = 50
        self.failed_devices=[]
    
    def add_failed_devices_to_db(self, host, reason):
        f5FailedDb = FAILED_DEVICES_F5()
        
        try:
            f5FailedDb.ip_address = host['ip_address']
            f5FailedDb.device_id = host['device_id']
            f5FailedDb.reason =reason
            f5FailedDb.date = host['time']
            
            self.InsertData(f5FailedDb)

            print('Successfully added Failed device to the Database', file = sys.stderr)
            
        except Exception as e:
            traceback.print_exc()
            db.session.rollback()
            print(f"Error while inserting failed device data into DB {e}", file=sys.stderr)    
        

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
  
    def addInventoryToDB(self, host, f5Data):          
        #for ednExchange in ednExchange_data:
            
            for f5 in f5Data: 
                try:
                    f5Db = F5DB()
                    f5Db.ip_address = host['ip_address']
                    f5Db.device_id = host['device_id']
                    f5Db.site_id = host['site_id']
                    f5Db.vserver_name= f5.get('vserver_name')
                    f5Db.vip= f5.get('vip')
                    f5Db.description= f5.get('description')
                    f5Db.pool_name=  f5.get('pool_name')
                    f5Db.pool_member= f5.get('pool_member')
                    f5Db.service_port= f5.get('service_port')
                    f5Db.node= f5.get('node')
                    f5Db.monitor_value= f5.get('monitor_value')
                    f5Db.monitor_status= f5.get('monitor_status')
                    f5Db.lb_method= f5.get('lb_method')
                    f5Db.ssl_profile= f5.get('ssl_profile')
                    f5Db.monitor_name= f5.get('monitor_name')
                    f5Db.creation_date = host['time']
                    f5Db.modification_date = host['time']
                    f5Db.created_by = host['user_id']
                    f5Db.modified_by = host['user_id']

                    self.InsertData(f5Db)
                    print('Successfully added to the Database',file = sys.stderr)        

                except Exception as e:
                    #db.session.rollback()
                    self.add_failed_devices_to_db(host, f"Failed to insert Data to DB "+str(e))
                    print(f"Error while inserting data into DB {e}", file=sys.stderr)

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
        print(f"Connecting to {host['ip_address']}", file=sys.stderr)
        login_tries = 10
        c = 0
        is_login = False
        sw_type = str(host['sw_type']).lower()
        sw_type = sw_type.strip()
        while c < login_tries :
            try:
                device_type= host['sw_type']
                device = Netmiko(host=host['ip_address'], username=host['user'], password=host['pwd'], device_type=device_type, timeout=600, global_delay_factor=2)
                print(f"Success: logged in {host['ip_address']}")
                is_login = True
                break
            except Exception as e:
                c +=1
                login_exception = str(e)
                
        if is_login==False:
            print(f"Falied to login {host['ip_address']}", file=sys.stderr)
            
            self.add_failed_devices_to_db(host, "Failed to login to host")
            # #failedDB
                
        if is_login==True:    
            print(f"Successfully Logged into Device {host['ip_address']}", file=sys.stderr) 

            try:
                members=lbMode=monitorValue=[]   
                monitor=pools=lb_mode=monitor_value=vips=monitors=descriptions=[]
                
                print("Getting VIP", file=sys.stderr)
                vips = device.send_command('list ltm virtual all destination', textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/f5_ltm_list_ltm_virtual_all_destination.textfsm", use_textfsm=True)
                #print(f"Vips are: {vips}", file=sys.stderr)
                if not isinstance(vips,list):
                    vips=[]
                    print(f"VIP for {host['ip_address']} not found {vips} ", file=sys.stderr)
                    raise Exception(f"VIP data not found "+str(vips))

                #print(f"VIPS are: {vips}", file=sys.stderr)
                
                print("Getting Description", file=sys.stderr)
                descriptions = device.send_command('list ltm virtual all description', textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/f5_ltm_list_ltm_virtual_all_description.textfsm", use_textfsm=True)
                #print(f"Vips are: {vips}", file=sys.stderr)
                if not isinstance(descriptions,list):
                    descriptions=[]
                    print(f"Descriptions for {host['ip_address']} not found {descriptions} ", file=sys.stderr)
                    #raise Exception(f"VIP data not found "+str(vips))

                #print(f"VIPS are: {vips}", file=sys.stderr)

                try:
                    print(f"Getting Pools", file=sys.stderr)
                    pools = device.send_command(f"list ltm virtual", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/f5_ltm_list_ltm_virtual_pool.textfsm", use_textfsm=True)
                    if isinstance(pools,str):
                        pools=[]
                        print(f"Pool for {host['ip_address']} not found  ", file=sys.stderr)
                except Exception as e:
                    print(f"Exception Occurred in Getting Pool {e}", file=sys.stderr)
                #print(f"Pool is: {pools}", file=sys.stderr)

                try:
                    print(f"Getting Pool Members", file=sys.stderr)
                    members = device.send_command(f"list ltm pool", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/f5_ltm_list_ltm_pool_members.textfsm", use_textfsm=True)
                    
                    if isinstance(members,str):
                        members= []
                        #print(f"Members for {host['ip_address']} not found", file=sys.stderr)
                    
                    else:
                        if len(members)>0:
                            pool_name=""
                            for member in members:
                                if  member['pool_name']:
                                    pool_name= member['pool_name']
                                else: 
                                    member['pool_name']= pool_name

                        #print(f"Member is: {members}", file=sys.stderr) 
                except Exception as e:
                    print(f"Exception Occurred in Getting Pool Members{e}", file=sys.stderr)
                #print(f"Member are: {members}", file=sys.stderr)
                
                try:
                    print(f"Getting Pool Monitors", file=sys.stderr)
                    monitors = device.send_command(f"list ltm pool", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/f5_ltm_list_ltm_pool_monitors.textfsm", use_textfsm=True)
                    #print(f"Monitors are: {monitors}", file=sys.stderr)
                    if isinstance(monitors,str):
                        monitors= []
                        #print(f"Members for {host['ip_address']} not found", file=sys.stderr)
                     
                except Exception as e:
                    print(f"Exception Occurred in Getting Pool Monitors {e}", file=sys.stderr)

                
                try:
                    print(f"Getting LB Modes", file=sys.stderr)
                    lbMode = device.send_command(f"list ltm pool load-balancing-mode", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/f5_ltm_list_pool_load_balancing_mode.textfsm", use_textfsm=True)
                    #print(f"1111 LB Modesa re {lbMode}", file=sys.stderr)
                    if isinstance(lbMode,str):
                        lbMode= []
                        #print(f"Members for {host['ip_address']} not found", file=sys.stderr)
                    # else:
                    #     lb_mode= lbMode[0]['lb_mode']
                        #print(f"LB Mode is: {lbMode}")
                    #print(f"LB Modes are: {lbMode}", file=sys.stderr)
                except Exception as e:
                    print(f"Exception Occurred in Getting LB Modes {e}", file=sys.stderr)

                try:
                    print(f"Getting Monitor Values", file=sys.stderr)
                    monitorValue = device.send_command(f"list ltm monitor", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/f5_ltm_list_monitor.textfsm", use_textfsm=True)
                    if isinstance(monitorValue,str):
                        monitorValue= []
                        #monitorValue(f"Members for {host['ip_address']} not found", file=sys.stderr)
                    # else:
                    #     monitor_value= monitorValue[0][monitor_value]
                    #     #print(f"Monitor Value: {monitorValue}")
                except Exception as e:
                    print(f"Exception Occurred in Getting Monitor Value {e}", file=sys.stderr)


                # ##Parsing Data
                try:
                    f5Data=[]
                    for vip in vips:
                        f5Obj={}

                        f5Obj['vserver_name']= vip['vserver']  
                        f5Obj['vip']= vip['vip']
                        
                        vipDescriptions= list(filter(lambda descriptions: descriptions['vserver'] == vip['vserver'], descriptions))  
                        if len(vipDescriptions)>0:
                            description= vipDescriptions[0]['description']

                            # if description== "none":
                            #     description= "Not Found"
                            f5Obj['description']= description
                        else:
                            f5Obj['description']= "Description not Found"

                        vipPools= list(filter(lambda pool: pool['vserver'] == vip['vserver'], pools)) 
                        if len(vipPools)>0:
                        
                            for vipPool in vipPools:
                                mon=""
                                if vipPool['pool_name']:
                                    f5Obj['pool_name']= vipPool['pool_name']
                                else:
                                    f5Obj['pool_name']= "NA"

                                poolMembers= list(filter(lambda members: members['pool_name'] == vipPool['pool_name'], members)) 

                                monitor= list(filter(lambda monitor: monitor['pool_name'] == vipPool['pool_name'], monitors)) 

                                if len(monitor)>0:
                                    #print(f"### {monitor}", file=sys.stderr)
                                    f5Obj['monitor_name']= monitor[0]['monitor_name']
                                    mon= monitor[0]['monitor_name']
                                else:
                                    f5Obj['monitor_name']="NA"
                                    

                                # mode= list(filter(lambda mode: mode['pool_name'] == mode['pool_name'], lbMode))
                                # if len(mode)>0:
                                #     print(f"444", file=sys.stderr)
                                #     f5Obj['lb_method']= mode[0]['lb_mode']

                                mode= list(filter(lambda mode: mode['pool_name'] == vipPool['pool_name'], lbMode))
                                if len(mode)>0:
                                    f5Obj['lb_method']= mode[0]['lb_mode']
                                else:
                                    f5Obj['lb_method']="NA"

                                if mon:
                                    ssl= list(filter(lambda ssl: ssl['monitor_name'] == mon, monitorValue))
                                    if len(ssl)>0:
                                        f5Obj['monitor_value']= ssl[0]['monitor_value']
                                        f5Obj['ssl_profile']= ssl[0]['ssl_profile']
                                else:
                                    f5Obj['monitor_value']="NA"
                                    f5Obj['ssl_profile']= "NA"  
                                    # else:
                                    #     monitorValue2 = device.send_command(f"list ltm monitor {mon} {mon}", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/f5_ltm_list_monitor.textfsm", use_textfsm=True)
                                    #     if isinstance(monitorValue,str):
                                    #         monitorValue= []
                                    #         f5Obj['monitor_value']="NA"
                                    #         f5Obj['ssl_profile']= "NA"
                                    #     else:

                                    #         ssl2= list(filter(lambda ssl: ssl['monitor_name'] == mon, monitorValue2))
                                    #         if len(ssl2)>0:
                                    #             f5Obj['monitor_value']= ssl2[0]['monitor_value']
                                    #             f5Obj['ssl_profile']= ssl2[0]['ssl_profile']
                                    #         else:
                                    #             f5Obj['monitor_value']="NA"
                                    #             f5Obj['ssl_profile']= "NA"

                                    
                                    
                                

                                if len(poolMembers)>0:
                                    for member in poolMembers:
                                        #print(f"TTT Member {member}", file=sys.stderr)
                                        memberName= member['member_name']
                                        memberName= memberName.split(':')
                                        
                                        f5Obj['pool_member']= memberName[0]
                                        f5Obj['service_port']= memberName[1]
                                        f5Obj['node']= member['node']

                                        status= member['status']
                                        if not status:
                                            status= "Not Configured"

                                        f5Obj['monitor_status']= status
                                        tempDic = f5Obj.copy()
                                        f5Data.append(tempDic)
                                else:
                                    f5Obj['pool_member']= "NA"
                                    f5Obj['service_port']="NA"
                                    f5Obj['node']= "NA"
                                    f5Obj['monitor_status']= "NA"
                                    tempDic = f5Obj.copy()
                                    f5Data.append(tempDic)
                                


                        else:
                            f5Obj['pool_name']= "NA"
                            f5Obj['monitor_name']="NA"
                            f5Obj['lb_method']= "NA"
                            f5Obj['monitor_value']= "NA"
                            f5Obj['ssl_profile']= "NA"
                            f5Obj['pool_member']= "NA"
                            f5Obj['service_port']="NA"
                            f5Obj['node']= "NA"
                            f5Obj['monitor_status']="NA"
                            tempDic = f5Obj.copy()
                            f5Data.append(tempDic)
                            
                        
                    self.addInventoryToDB(host, f5Data )
                except Exception as e:
                    traceback.print_exc()
                    self.add_failed_devices_to_db(host, f"Failed to Parse Data {e}")
                    print(f"Exception in Parsing Data {e}", file=sys.stderr)
                                
                '''
                for vip in vips:
                    f5Data=[]
                    try:
                        print(f"Getting Pool for VIP {vip['vserver']}", file=sys.stderr)
                        poolObj = device.send_command(f"list ltm virtual {vip['vserver']}", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/f5_ltm_list_ltm_virtual_pool.textfsm", use_textfsm=True)
                        if isinstance(poolObj,str):
                            pool=""
                            print(f"Pool for {host['ip_address']} not found  ", file=sys.stderr)
                        
                        else:
                            #print(f"Pool is: {poolObj}", file=sys.stderr)
                            pool=poolObj[0].get('pool_name')
                        
                    except Exception as e:
                        print(f"Exception Occurred in Getting Pool {e}", file=sys.stderr)
                    
                    try:
                        if pool:    
                            print(f"Getting Pool Members for {pool}", file=sys.stderr)
                            members = device.send_command(f"list ltm pool {pool}", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/f5_ltm_list_ltm_pool_members.textfsm", use_textfsm=True)
                            #print(f"Member is: {members}", file=sys.stderr)
                            if isinstance(members,str):
                                members= []
                                #print(f"Members for {host['ip_address']} not found", file=sys.stderr)
                            
                            else:
                                if len(members)>0:
                                    if members[-1].get('monitor'):
                                        monitor= members[-1].get('monitor')   
                                        del members[-1]
                                        for  dic in members:
                                            #print(monitor)
                                            dic["monitor"]= monitor
            
                            #print(f"Member is: {members}", file=sys.stderr) 
                    except Exception as e:
                        print(f"Exception Occurred in Getting Pool Members{e}", file=sys.stderr)

                    try:
                        if pool:
                            print(f"Getting LB Modes for {pool}", file=sys.stderr)
                            lbMode = device.send_command(f"list ltm pool {pool} load-balancing-mode", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/f5_ltm_list_pool_load_balancing_mode.textfsm", use_textfsm=True)
                            if isinstance(lbMode,str):
                                lbMode= []
                                #print(f"Members for {host['ip_address']} not found", file=sys.stderr)
                            else:
                                lb_mode= lbMode[0]['lb_mode']
                                #print(f"LB Mode is: {lbMode}")
                    except Exception as e:
                        print(f"Exception Occurred in Getting LB Modes {e}", file=sys.stderr)

                    try:
                        if monitor:
                            print(f"Getting Monitor Value for {monitor}", file=sys.stderr)
                            monitorValue = device.send_command(f"list ltm monitor tcp {monitor}", textfsm_template= "app/pullers/ntc-templates/ntc_templates/templates/f5_ltm_list_pool_load_balancing_mode.textfsm", use_textfsm=True)
                            if isinstance(monitorValue,str):
                                monitorValue= []
                                #monitorValue(f"Members for {host['ip_address']} not found", file=sys.stderr)
                            else:
                                monitor_value= monitorValue[0][monitor_value]
                                #print(f"Monitor Value: {monitorValue}")
                    except Exception as e:
                        print(f"Exception Occurred in Getting Monitor Value {e}", file=sys.stderr)

                    try:
                        print("Parsing Data", file=sys.stderr)
                        for member in members:
                            f5Obj={}
                            f5Obj['vserver_name']= vip['vserver']

                            f5Obj['vip']= vip['vip']
                            memberName= member['member_name']
                            memberName= memberName.split(':')
                            f5Obj['pool_name']= pool
                            f5Obj['pool_member']= memberName[0]
                            f5Obj['service_port']= memberName[1]
                            f5Obj['node']= member['node']
                            f5Obj['monitor_status']= member['status']
                            f5Obj['lb_method']= lb_mode 
                            f5Obj['monitor_value']= monitor_value
                            #f5Obj['ssl_profile']= ssl_profile
                            #f5Obj['monitor_name']= monitor_name

                            f5Data.append(f5Obj)
                    except Exception as e:
                        self.add_failed_devices_to_db(host, f"Failed to Parse Data {e}")
                        print("Exception in Parsing Data", file=sys.stderr)
                    self.addInventoryToDB(host, f5Data )
                #print("Puller Finished")  
                #print(f5Data, file=sys.stderr)   
                '''
            except Exception as e:
                print(f"Error Occured in Getting F5 Data {e}", file=sys.stderr) 
                self.add_failed_devices_to_db(host, f"Failed to get F5 Data {e}")      



    def getF5(self, devices):
            puller = F5()
            hosts = []
            with open('app/cred.json') as inventory:
                inv = json.loads(inventory.read())
            for device in devices:
                
                user_name = inv['SYSTEMS']['user']
                password = inv['SYSTEMS']['pwd']

                sw_type = str(device['sw_type']).lower()
                sw_type = sw_type.strip()
                #print(sw_type,file=sys.stderr)
                if sw_type=='f5':
                    sw_type = 'f5_tmsh'
                else:
                    sw_type=''

                
                host={
                    "device_id": device["device_id"],
                    "ip_address":device["ip_address"],
                    "user": user_name,
                    "pwd": password,
                    #"user": "root",
                    #"pwd": "default",
                    "sw_type": sw_type,
                    
                    #'region':device['region'],
                    'site_id':device['site_id'],
                    'time': self.FormatStringDate(device["time"]),
                    'user_id': device['user_id']

                }
                hosts.append(host)
                    
            puller.get_inventory_data(hosts)
            print("F5 Fetch Completed", file=sys.stderr)



if __name__ == '__main__':

    hosts=[]

    host={
        "ip_address": "192.168.30.195",
        "user": "root",
        "pwd": "default",
        "sw_type": "f5_tmsh",
        #f5_tmsh
        #f5_ltm
        
    }
    #poll(host)
              


