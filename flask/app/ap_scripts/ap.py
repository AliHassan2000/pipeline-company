from turtle import update
from netmiko import Netmiko
import sys
import threading
from app.models.inventory_models import Access_Points_Table, Seed, FAILED_DEVICES_ACCESS_POINTS
from app import app ,db , tz
from datetime import datetime
from ..routes.inventory_routes import InsertData, UpdateData
import traceback

class ACCESSPOINTSPuller(object):
    def __init__(self):
        self.connections_limit = 50
        self.failed_devices=[]

    
    def FormatStringDate(self, date):
        print(date, file=sys.stderr)

        try:
            if date is not None:
                if '-' in date:
                    result = datetime.strptime(date,'%d-%m-%Y')
                elif '/' in date:
                    result = datetime.strptime(date,'%d/%m/%Y')
                else:
                    print("incorrect date format", file=sys.stderr)
                    result = datetime(2000, 1, 1)
            else:
                #result = datetime(2000, 1, 1)
                result = datetime(2000, 1, 1)
        except:
            result=datetime(2000, 1,1)
            print("date format exception", file=sys.stderr)

        return result

    def InsertData(obj):
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

    def UpdateData(obj):
        #add data to db
        #print(obj, file=sys.stderr)
        try:
            #obj.modification_date= datetime.now(tz)
            db.session.merge(obj)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong in Database Updation {e}", file=sys.stderr)
        
        return True

    
    def add_failed_devices_to_db(self, ip, device, reason, time):
        apFailedDb = FAILED_DEVICES_ACCESS_POINTS()
        try:
            apFailedDb.ip_address = ip
            apFailedDb.device_id = device
            apFailedDb.reason =reason
            apFailedDb.date = time
            
            InsertData(apFailedDb)
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
            return ""
  
    def addInventoryToDB(self, host, ap): 
        
        try:
            apObj= Access_Points_Table()

            apObj.ne_ip_address= ap['ip_addr']
            apObj.device_name= ap['ap_name']
            apObj.serial_number= ap['serial_number']
            apObj.pn_code= ap['pn_code']
            apObj.hardware_version= ap['hw_version']
            apObj.software_version= ap['software_version']
            apObj.manufacturer = ap['manufecturer']
            apObj.status= "Registered" #ap['status']
            apObj.wlc_name= host['device'].device_id
            
            apObj.modification_date = host['time']
           
            apObj.modified_by =  host['login_user']

            sitInfo= ap['ap_name'].split('-')

            apObj.site_id= sitInfo[0]
            if len(sitInfo)>3:
                apObj.site_type= sitInfo[3]
            else:
                apObj.site_type= 'NA'
            apObj.criticality= "High"
            apObj.function= "Access Point" 
            apObj.section= "End point Protection"
            apObj.department= "Security Operations Center"
            apObj.authentication= "AAA"
            apObj.rfs_date= self.FormatStringDate("01-01-2012")

            ###### Get Values From Seed
            seedObj= Seed.query.with_entities(Seed).filter_by(hostname=apObj.device_name).first()
            if seedObj:
                #apObj.site_id= seedObj.site_id
                apObj.device_id= seedObj.device_id
                #apObj.rfs_date= seedObj.rfs_date
                #apObj.site_type= seedObj.site_type
                #apObj.criticality= seedObj.criticality
                #apObj.function= seedObj.function 
                #apObj.section= seedObj.section
                #apObj.department= seedObj.department
                #apObj.authentication= seedObj.authentication

            else:
                apObj.device_id= apObj.device_name
            ap = Access_Points_Table.query.with_entities(Access_Points_Table.access_point_id).filter_by(serial_number=apObj.serial_number).filter_by(wlc_name=apObj.wlc_name).first()
            if ap:
                apObj.access_point_id= ap[0]
                UpdateData(apObj)
            else:
                apObj.creation_date = host['time']
                apObj.created_by = host['login_user']
                InsertData(apObj)
            
            print("Successfully Added AP Data in DB ", file=sys.stderr)
        except Exception as e:
            traceback.print_exc()
            print(host, file=sys.stderr)
            self.add_failed_devices_to_db( ap['serial_number'], host['device_id'], f"Error while inserting data into DB {e}", host['time'])
            print(f"Failed in Database Operation {e}", file=sys.stderr)
            #failedDB

    def poll(self, host):
        #dfObj = pd.DataFrame(columns=['IP', 'AP Name', 'Serial Number',	'PN Code',	'Hardware Version',	'Software Version',	'Description',	'Manufacturer'])
        #obj_in=0
        try:
            print(f"Connecting to {host['ip']}", file=sys.stderr)
            login_tries = 10
            c = 0
            is_login = False
            while c < login_tries :
                try:
                    device = Netmiko(host=host['ip'], username=host['user'], password=host['pwd'], device_type='cisco_wlc_ssh', timeout=600, global_delay_factor=2)
                    #print(f"Success: logged in {host['ip']}", file=sys.stderr)
                    is_login = True
                    break
                except Exception as e:
                    c +=1
                    login_exception = str(e)
                    print(f"failed to login {e}", file=sys.stderr)
                    
            if is_login==False:
                print(f"Falied to login {host['ip']}", file=sys.stderr)
                #self.add_to_failed_devices(host['ip'], "Failed to login to host")
                #failedDB
                self.add_failed_devices_to_db(host['ip'], host['device_id'], f"Failed to Login WLC", host['time'])
                    
            if is_login==True:    
                print(f"Successfully Logged into device {host['ip']}", file=sys.stderr) 
                try:
                    print("Getting Aps data", file=sys.stderr)
                    all_aps=[]
                    print("Sending command: show ap summary", file=sys.stderr)
                    #cisco_wlc_ssh_show_ap_summary.textfsm

                    ap_summary = device.send_command('show ap summary',  use_textfsm=True) #textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_wlc_ssh_show_ap_summary.textfsm',
                    #if host['device'].device_id == "SULM-EWLC-CI-EXC-001":
                    #    print(f"AP summary is {ap_summary}", file=sys.stderr)
                    print("Sending command: show ap inventory all", file=sys.stderr)
                    
                    ap_inv = device.send_command('show ap inventory all', textfsm_template='app/pullers/ntc-templates/ntc_templates/templates/cisco_wlc_ssh_show_ap_inventory_all.textfsm', use_textfsm=True)
                    #if host['device'].device_id == "SULM-EWLC-CI-EXC-001":
                    #    print(f"AP INV is {ap_inv}", file=sys.stderr)
                    print("Sending command: show ap image all", file=sys.stderr)
                    ap_image = device.send_command('show ap image all', use_textfsm=True)
                    if host['device'].device_id == "SULM-EWLC-CI-EXC-001":
                        print(f"AP Image is {ap_image}", file=sys.stderr)
            
                    for ap in ap_summary:
                        
                        for inv in ap_inv:
                            if not inv['sn']:
                                self.add_failed_devices_to_db(host['ip'], host['device_id'], f"Failed to get AP Data from WLC {e}", host['time'])
                            if inv['ap_name'].strip()==ap['ap_name'].strip():
                                for ver in ap_image:
                                    if ver['ap_name'].strip()==ap['ap_name'].strip():
                                        # all_aps.append({'aps':
                                        ap_data = {'ip_addr': ap['ip'], 
                                            'ap_name':ap['ap_name'],
                                            'serial_number': inv['sn'], 
                                            'pn_code': ap['ap_model'], 
                                            'hw_version': inv['vid'], 
                                            "software_version": ver['primary_image'], 
                                            "desc": inv['description'], 
                                            "max_power": None, 
                                            "manufecturer": "Cisco", 
                                            "status": "production", 
                                            "authentication": None}
                                    
                                        self.addInventoryToDB(host, ap_data)
                                        break #ap_image loop breal
                                break #ap_inv loop break
                    
                    
                except Exception as e:
                    traceback.print_exc()
                    print("Aps data not found", file=sys.stderr)
                    #self.inv_data[host['ip']].update({"aps":[]})
                    self.add_failed_devices_to_db(host['ip'], host['device_id'], f"Failed to get AP Data from WLC {e}", host['time'])
        except Exception as e:
            self.add_failed_devices_to_db(host['ip'], host['device_id'], f"Failed to get AP Data from WLC {e}", host['time'])
            print(f"Exception Occured, {e}", file=sys.stderr)
            
            #failedDB


            