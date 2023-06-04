import sys
import traceback
from flask_jsonpify import jsonify
import pandas as pd
from app.models.phy_mapping_models import EDN_SERVICE_MAPPING, IGW_SERVICE_MAPPING, EDN_MAC_LEGACY, EDN_LLDP_ACI, IGW_LLDP_ACI, IT_SERVICES_SNAPSHOTS_TABLE, IT_APP_TABLE, IT_IP_TABLE, IT_MAC_TABLE, IT_OS_TABLE, IT_OWNER_TABLE, IT_PHYSICAL_SERVERS_TABLE
from app import db, phy_engine, tz
from app.models.phy_mapping_models import SCRIPT_STATUS
from datetime import date, datetime

class AddServiceMapping():
    def UpdateData(self, obj):
        #add data to db
        #print(obj, file=sys.stderr)
        try:
            db.session.flush()
            db.session.merge(obj)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong during Database Update {e}", file=sys.stderr)
        
        return True

    def InsertData(self, obj):
        try: 
            # print(f"Dataa is : {obj.creation_date}", file=sys.stderr)
            #add data to db
            #obj.creation_date= datetime.now(tz)
            #obj.modification_date= datetime.now(tz)
            db.session.add(obj)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Something else went wrong {e}", file=sys.stderr)

    def AddEdnServiceMappingFunc(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cdpLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-Service-Mapping-Sync").first()
        try:
            cdpLegacyStatus.script = "EDN-Service-Mapping-Sync"
            cdpLegacyStatus.status = "Running"
            cdpLegacyStatus.creation_date= current_time
            cdpLegacyStatus.modification_date= current_time
            db.session.add(cdpLegacyStatus)
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"Error while updating script status {e}", file=sys.stderr)

        if True:
            try:
                result = IT_OWNER_TABLE.query.with_entities(IT_OWNER_TABLE.vm_name).all()
                ednList = []
                response=False
                response1=False
                for obj in result:
                    try:
                        objDict = {}
                        name = obj.vm_name

                        objDict['Device_B_Mac'] = ""
                        objDict['Device_B_SYS_Name'] = ""
                        objDict['Server_OS'] = ""
                        objDict['App_Name'] = ""
                        objDict['Owner_Name'] = ""
                        objDict['Owner_Email'] = ""
                        objDict['Owner_Contact'] = ""
                        objDict['Device_B_IP'] = ""
                        objDict['Modified_By'] = "IT Sync"
                        
                        mac = IT_MAC_TABLE.query.with_entities(IT_MAC_TABLE.mac_address).filter_by(vm_name=name).all()
                        macStr = ""
                        
                        for row in mac:
                            try:
                                macStr += str(row[0])+","
                            except Exception as e:
                                print("MAC Not found")
                        #macStr = ",".join(macStr)

                        objDict['Device_B_Mac'] = macStr

                        ip = IT_IP_TABLE.query.with_entities(IT_IP_TABLE.ip_address).filter_by(vm_name=name).all()
                        ipStr = ""
                        for row in ip:
                            try:

                                ipStr += str(row[0])+","
                            except Exception as e:
                                print("IP Not found")
                        #ipStr = ",".join(ipStr)

                        objDict['Device_B_IP'] = ipStr
                        objDict['Server_Name'] = name

                        vmName = name.split(".")
                        vmName = vmName[0]

                        server = IT_PHYSICAL_SERVERS_TABLE.query.with_entities(IT_PHYSICAL_SERVERS_TABLE.server_name).filter_by(vm_name=vmName).all()
                        os = IT_OS_TABLE.query.with_entities(IT_OS_TABLE.operating_system).filter_by(vm_name=name).all()
                        owner = IT_OWNER_TABLE.query.with_entities(IT_OWNER_TABLE.app_name, IT_OWNER_TABLE.owner_name, IT_OWNER_TABLE.owner_email, IT_OWNER_TABLE.owner_contact).filter_by(vm_name=name).all()
                            
                        for row in server:
                            objDict['Device_B_SYS_Name'] = row[0]
                        for row in os:
                            objDict['Server_OS'] = row[0]
                        for row in owner:
                            objDict['App_Name'] = row[0]
                            objDict['Owner_Name'] = row[1]
                            objDict['Owner_Email'] = row[2]
                            objDict['Owner_Contact'] = row[3]
                        objDict['Device_A_Name'] = ""
                        objDict['Device_A_Interface'] = ""
                        objDict['Device_B_Type'] = "Server"
                        ednList.append(objDict)
                    except Exception as e:
                        print(f"Some Error Occured {e}", file=sys.stderr)
                        traceback.print_exc()
                        return str(e), 500

                for objs in ednList:
                    try:
                        serviceMapping = EDN_SERVICE_MAPPING()
                        serviceMapping.device_a_name = objs['Device_A_Name']
                        serviceMapping.device_a_interface = objs['Device_A_Interface']
                        serviceMapping.server_name = objs['Server_Name']
                        serviceMapping.device_b_ip = objs['Device_B_IP']
                        serviceMapping.device_b_mac = objs['Device_B_Mac']
                        serviceMapping.modified_by = objs['Modified_By']


                        if objs["Device_B_SYS_Name"] != '':
                            serviceMapping.device_b_system_name = objs['Device_B_SYS_Name']
                        if objs["Device_B_SYS_Name"] == '':
                            serviceMapping.device_b_system_name = objs['Server_Name']
                        
                        serviceMapping.device_b_type = objs['Device_B_Type']
                        serviceMapping.server_os = objs['Server_OS']
                        if "App_Name" in objs:
                            serviceMapping.app_name = objs['App_Name']
                        if "Owner_Name" in objs:
                            serviceMapping.owner_name = objs['Owner_Name']
                        if "Owner_Email" in objs:
                            serviceMapping.owner_email = objs['Owner_Email']
                        if "Owner_Contact" in objs:
                            serviceMapping.owner_contact = objs['Owner_Contact']
                        
                        serviceMapping.service_vendor = "IT"
                        #serviceMapping.modification_date= datetime.now(tz)
                        #serviceMapping.creation_date= datetime.now(tz)


                        # if EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(server_name=objs['Server_Name']).filter_by(owner_name=objs['Owner_Name']).first() is not None:

                        # serviceMapping.edn_service_mapping_id= EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(server_name=objs['Server_Name']).filter_by(owner_name=objs['Owner_Name']).first()[0]

                        if EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(server_name=objs['Server_Name']).first() is not None:
                            serviceMapping.edn_service_mapping_id= EDN_SERVICE_MAPPING.query.with_entities(EDN_SERVICE_MAPPING.edn_service_mapping_id).filter_by(server_name=objs['Server_Name']).first()[0]
                            serviceMapping.modification_date= datetime.now(tz)
                            self.UpdateData(serviceMapping)
                            print(f"Data Updated For Device ID: {serviceMapping.edn_service_mapping_id}", file=sys.stderr)
                            response=True
                        else:
                            self.InsertData(serviceMapping)
                            serviceMapping.modification_date= datetime.now(tz)
                            serviceMapping.creation_date= datetime.now(tz)

                            print("Data Inserted Into DB", file=sys.stderr)
                            response1=True
                    except Exception as e:
                        print(f"Some Error Occured {e}", file=sys.stderr)
                        traceback.print_exc()
                        return str(e), 500
                cdpLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-Service-Mapping-Sync").first()
                try:
                    cdpLegacyStatus.script = "EDN-Service-Mapping-Sync"
                    cdpLegacyStatus.status = "Completed"
                    cdpLegacyStatus.creation_date= current_time
                    cdpLegacyStatus.modification_date= current_time
                    db.session.add(cdpLegacyStatus)
                    db.session.commit() 
                except Exception as e:
                    db.session.rollback()
                    print(f"Error while updating script status {e}", file=sys.stderr)

                # if response==True:
                #     return jsonify({"RESPONSE":"Updated Successfully"}),200
                # if response1==True:
                #     return jsonify({"RESPONSE":"Inserted Successfully"}),200
                    
            except Exception as e:
                print(f"Some Error Occured {e}", file=sys.stderr)
                traceback.print_exc()
                return str(e), 500
            
        cdpLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-Service-Mapping-Sync").first()
        try:
            cdpLegacyStatus.script = "EDN-Service-Mapping-Sync"
            cdpLegacyStatus.status = "Completed"
            cdpLegacyStatus.creation_date= current_time
            cdpLegacyStatus.modification_date= current_time
            db.session.add(cdpLegacyStatus)
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"Error while updating script status {e}", file=sys.stderr)


    def addEdnMacLegacyServiceMapping(self, current_time, newTime):
        statusTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ednMacLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-MAC-Legacy-Service-Mapping-Sync").first()
        try:
            ednMacLegacyStatus.script = "EDN-MAC-Legacy-Service-Mapping-Sync"
            ednMacLegacyStatus.status = "Running"
            ednMacLegacyStatus.creation_date= statusTime
            ednMacLegacyStatus.modification_date= statusTime
            db.session.add(ednMacLegacyStatus)
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"Error while updating script status {e}", file=sys.stderr)
        
        try:

            #print(f"@@@@@@@@@@@@@@@@ {current_time}", file=sys.stderr)
            ednMacLegacyObjs = EDN_MAC_LEGACY.query.filter_by(creation_date=current_time).all()
            
            if ednMacLegacyObjs:
               

                for ednMacLegacyObj in ednMacLegacyObjs: 
                    #print(f"@@@@@@ {dict(ednMacLegacyObj)} ",file=sys.stderr)
                    #ednServiceMappingObjectLongest = EDN_SERVICE_MAPPING.query.filter(EDN_SERVICE_MAPPING.device_a_name==ednMacLegacyObj.device_a_name).filter(EDN_SERVICE_MAPPING.device_a_interface==ednMacLegacyObj.device_a_interface).filter(EDN_SERVICE_MAPPING.device_b_ip==ednMacLegacyObj.device_b_ip).filter(EDN_SERVICE_MAPPING.device_b_mac==ednMacLegacyObj.device_b_mac).first()
                    #print(f"++++++++++ SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY FROM edn_service_mapping WHERE (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip LIKE '%%{ednMacLegacyObj.device_b_ip}%%' and device_b_ip!='' and device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac}%%' and device_b_mac!='');", file=sys.stderr)
                    #print("Before Query", file=sys.stderr)
                    try:
                        if ednMacLegacyObj.device_b_ip and ednMacLegacyObj.device_b_ip != '':
                            print("F5 Service Mapping")
                            f5Objs = db.session.execute(f"SELECT DEVICE_ID, VIP, MONITOR_STATUS FROM f5 WHERE NODE='{ednMacLegacyObj.device_b_ip}' and creation_date = (SELECT max(creation_date) FROM f5)")
                            f5_lb=f5_vip=f5_node_status=""
                            f5_flag=False
                            for f5Obj in f5Objs:
                                f5_lb+=f5Obj[0]+","
                                f5_vip+=f5Obj[1]+","
                                f5_node_status+=f5Obj[2]+","
                            
                            if f5_lb:
                                f5_lb = f5_lb[:-1]
                                values_list = f5_lb.split(",")
                                unique_values_counts = {}
                                for value in values_list:
                                    if value in unique_values_counts:
                                        unique_values_counts[value] += 1
                                    else:
                                        unique_values_counts[value] =1
                                # print("#######################", unique_values_counts, file=sys.stderr)
                                        
                                result = ""
                                for key, value in unique_values_counts.items():
                                    print("The Key IS:", key, file=sys.stderr)
                                    result += f"{key}({value}),"
                                    # remove the trailing comma and spaceprint(result)
                                    result[:-2]
                                # print("*************************" , result, file=sys.stderr)
                                ednMacLegacyObj.f5_lb= result[:-1]
                                # print("@@@@@@@@@@@@@@@@@@@@" , ednMacLegacyObj.f5_lb, file=sys.stderr)
                                f5_flag= True
                            if f5_vip:
                                ednMacLegacyObj.f5_vip= f5_vip[:-1]
                                f5_flag= True
                            if f5_node_status:
                                ednMacLegacyObj.f5_node_status= f5_node_status[:-1]
                                f5_flag= True
                            
                            if f5_flag:
                                self.UpdateData(ednMacLegacyObj)
                    except Exception as e:
                        print(f"Error Occured {e}", file=sys.stderr)                    

                    if ednMacLegacyObj.device_b_ip == '':
                        dummyIP = ednMacLegacyObj.device_b_ip 
                        dummyIP = '0.0.0.0'
                        ednServiceMappingObjectLongest = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY, SERVICE_VENDOR FROM edn_service_mapping WHERE (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip LIKE '%%{dummyIP}%%' and device_b_ip!='' and device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='');")  #and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);")                    
                        # print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY FROM edn_service_mapping WHERE (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip LIKE '%%{dummyIP}%%' and device_b_ip!='' and device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='');", file=sys.stderr)
                    else:
                        ednServiceMappingObjectLongest = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY , SERVICE_VENDOR FROM edn_service_mapping WHERE (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip LIKE '%%{ednMacLegacyObj.device_b_ip},%%' and device_b_ip!='' and device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='');")
                    #print("After Query", file=sys.stderr)
                    next=0
                    if ednServiceMappingObjectLongest:
                        #print(f"SELECT * FROM edn_service_mapping WHERE device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip= '{ednMacLegacyObj.device_b_ip}'  and device_b_mac= '{ednMacLegacyObj.device_b_mac}'" , file=sys.stderr)
                        #print("In Longest", file=sys.stderr)
                        for row in ednServiceMappingObjectLongest:
                            #print("In Row", file=sys.stderr)
                            #print(f"1111111111  {row}", file=sys.stderr)
                            ednMacLegacyObj.device_b_system_name= row[4]
                            ednMacLegacyObj.device_b_type= row[5]
                            ednMacLegacyObj.server_name= row[0]
                            ednMacLegacyObj.owner_name= row[1]
                            ednMacLegacyObj.owner_contact= row[2]
                            ednMacLegacyObj.owner_email= row[3]
                            ednMacLegacyObj.server_os= row[6]
                            ednMacLegacyObj.app_name= row[7]
                            ednMacLegacyObj.modified_by= row[8]
                            ednMacLegacyObj.service_vendor= row[9]
                            ednMacLegacyObj.service_matched_by= "Interface,Mac,IP"
                            #print("Updating Service Mapping Data")
                            next=1
                            #print(f"L {ednMacLegacyObj}  SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip= '{ednMacLegacyObj.device_b_ip}' and device_b_ip!='' and device_b_mac= '{ednMacLegacyObj.device_b_mac}' and device_b_mac!='')  and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);", file=sys.stderr)
                            #print("Before Update", file=sys.stderr)
                            print(f"Matched Service Mapping Longest Match for ID: {ednMacLegacyObj.edn_mac_legacy_id}")
                            ednMacLegacyObj.modification_date= newTime
                            self.UpdateData(ednMacLegacyObj)
                            #print("After Update", file=sys.stderr)
                            #self.addServiceDatatoDB(ednMacLegacyObj, ednServiceMappingObjectLongest)
                            break
                        if next==1:
                            continue
                    
                    
                    if ednMacLegacyObj.device_b_ip == '':
                        dummyIP = ednMacLegacyObj.device_b_ip
                        dummyIP = '0.0.0.0'
                        ednServiceMappingObjectMedium = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY, SERVICE_VENDOR FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip LIKE '%%{dummyIP}%%' and device_b_ip!='' and device_b_mac NOT LIKE'%%{ednMacLegacyObj.device_b_mac},%%')  or (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='' and  device_b_ip NOT LIKE '%%{dummyIP}%%') or (device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and  device_b_ip LIKE '%%{dummyIP}%%' and device_b_ip!='' and device_b_mac !='' and device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}'));") # and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);")
                        # print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip LIKE '%%{dummyIP}%%' and device_b_ip!='' and device_b_mac NOT LIKE'%%{ednMacLegacyObj.device_b_mac},%%')  or (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='' and  device_b_ip NOT LIKE '%%{dummyIP}%%') or (device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and  device_b_ip LIKE '%%{dummyIP}%%' and device_b_ip!='' and device_b_mac !='' and device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}'));", file=sys.stderr)
                        #ednServiceMappingObjectMedium = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY, SERVICE_VENDOR FROM edn_service_mapping WHERE ((device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and  device_b_ip LIKE '%%{dummyIP}%%' and device_b_ip!='' and device_b_mac !='' and device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}') or(device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip LIKE '%%{dummyIP}%%' and device_b_ip!='' and device_b_mac NOT LIKE'%%{ednMacLegacyObj.device_b_mac},%%')  or (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='' and  device_b_ip NOT LIKE '%%{dummyIP}%%') );") # and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);")

                    else:
                        ednServiceMappingObjectMedium = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY, SERVICE_VENDOR FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip LIKE '%%{ednMacLegacyObj.device_b_ip},%%' and device_b_ip!='' and device_b_mac NOT LIKE'%%{ednMacLegacyObj.device_b_mac},%%')  or (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='' and  device_b_ip NOT LIKE '%%{ednMacLegacyObj.device_b_ip},%%') or (device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and  device_b_ip LIKE '%%{ednMacLegacyObj.device_b_ip},%%' and device_b_ip!='' and device_b_mac !='' and device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}'));")
                        #ednServiceMappingObjectMedium = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY, SERVICE_VENDOR FROM edn_service_mapping WHERE ((device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and  device_b_ip LIKE '%%{ednMacLegacyObj.device_b_ip},%%' and device_b_ip!='' and device_b_mac !='' and device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}') or (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip LIKE '%%{ednMacLegacyObj.device_b_ip},%%' and device_b_ip!='' and device_b_mac NOT LIKE'%%{ednMacLegacyObj.device_b_mac},%%')  or (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='' and  device_b_ip NOT LIKE '%%{ednMacLegacyObj.device_b_ip},%%'));")

                    #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip= '{ednMacLegacyObj.device_b_ip}')  or (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac= '{ednMacLegacyObj.device_b_mac}') or (device_b_mac= '{ednMacLegacyObj.device_b_mac}' and  device_b_ip= '{ednMacLegacyObj.device_b_ip}');")
                    #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip= '{ednMacLegacyObj.device_b_ip}' and device_b_ip!='')  or (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac= '{ednMacLegacyObj.device_b_mac}' and device_b_mac!='') or (device_b_mac= '{ednMacLegacyObj.device_b_mac}' and  device_b_ip= '{ednMacLegacyObj.device_b_ip}' and device_b_ip!='' and device_b_mac !='')) and creation_date = (SELECT max(creation_date) FROM edn_service_mapping) ;", file=sys.stderr)
                    if ednServiceMappingObjectMedium:
                        #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip= '{ednMacLegacyObj.device_b_ip}')  or (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac= '{ednMacLegacyObj.device_b_mac}') or (device_b_mac= '{ednMacLegacyObj.device_b_mac}' and  device_b_ip= '{ednMacLegacyObj.device_b_ip}') ;")

                        for row in ednServiceMappingObjectMedium:
                            service_mapped=""
                            mappedService = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY FROM edn_service_mapping WHERE (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip LIKE '%%{ednMacLegacyObj.device_b_ip},%%' and device_b_ip!='' and device_b_mac NOT LIKE'%%{ednMacLegacyObj.device_b_mac},%%');") #and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);")                    #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' )  or device_b_ip= '{ednMacLegacyObj.device_b_ip}' or device_b_mac= '{ednMacLegacyObj.device_b_mac}') and creation_date = (SELECT max(creation_date) FROM edn_service_mapping;", file=sys.stderr)
                            for row2 in mappedService:
                                if row[0]:
                                    service_mapped+= "Interface,IP"
                                    break
          
                            mappedService = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY FROM edn_service_mapping WHERE (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='' and  device_b_ip NOT LIKE '%%{ednMacLegacyObj.device_b_ip},%%');") #and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);")                    #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' )  or device_b_ip= '{ednMacLegacyObj.device_b_ip}' or device_b_mac= '{ednMacLegacyObj.device_b_mac}') and creation_date = (SELECT max(creation_date) FROM edn_service_mapping;", file=sys.stderr)
                            for row2 in mappedService:
                                if row[0]:
                                    service_mapped+= "Interface,MAC"
                                    break
                            
                            mappedService = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY FROM edn_service_mapping WHERE (device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and  device_b_ip LIKE '%%{ednMacLegacyObj.device_b_ip},%%' and device_b_ip!='' and device_b_mac !='' and device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}');") #and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);")                    #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' )  or device_b_ip= '{ednMacLegacyObj.device_b_ip}' or device_b_mac= '{ednMacLegacyObj.device_b_mac}') and creation_date = (SELECT max(creation_date) FROM edn_service_mapping;", file=sys.stderr)
                            for row2 in mappedService:
                                if row[0]:
                                    service_mapped+= "MAC,IP"
                                    break
                            
                            #print(f"222222  {row}", file=sys.stderr)
                            ednMacLegacyObj.service_matched_by= service_mapped
                            ednMacLegacyObj.device_b_system_name= row[4]
                            ednMacLegacyObj.device_b_type= row[5]
                            ednMacLegacyObj.server_name= row[0]
                            ednMacLegacyObj.owner_name= row[1]
                            ednMacLegacyObj.owner_contact= row[2]
                            ednMacLegacyObj.owner_email= row[3]
                            ednMacLegacyObj.server_os= row[6]
                            ednMacLegacyObj.app_name= row[7]
                            ednMacLegacyObj.modified_by= row[8]
                            ednMacLegacyObj.service_vendor= row[9]
                            #ednMacLegacyObj.service_vendor= row[9]
                            
                            #print("Updating Service Mapping Data")
                            next=1
                            #print(f"M {ednMacLegacyObj} SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip= '{ednMacLegacyObj.device_b_ip}' and device_b_ip!='' and device_b_mac!='{ednMacLegacyObj.device_b_mac}')  or (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac= '{ednMacLegacyObj.device_b_mac}' and device_b_mac!='' and  device_b_ip!= '{ednMacLegacyObj.device_b_ip}') or (device_b_mac= '{ednMacLegacyObj.device_b_mac}' and  device_b_ip= '{ednMacLegacyObj.device_b_ip}' and device_b_ip!='' and device_b_mac !='' and device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}')) and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);", file=sys.stderr)  
                            # if ednMacLegacyObj.device_b_ip == '10.14.114.5' or ednMacLegacyObj.device_b_ip == '10.14.148.83':
                            # print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_ip LIKE '%%{ednMacLegacyObj.device_b_ip},%%' and device_b_ip!='' and device_b_mac NOT LIKE'%%{ednMacLegacyObj.device_b_mac},%%')  or (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='' and  device_b_ip NOT LIKE '%%{ednMacLegacyObj.device_b_ip},%%') or (device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and  device_b_ip LIKE '%%{ednMacLegacyObj.device_b_ip},%%' and device_b_ip!='' and device_b_mac !='' and device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}'));")
                            print(f"Matched Service Mapping Medium Match for ID: {ednMacLegacyObj.edn_mac_legacy_id}")
                            ednMacLegacyObj.modification_date= newTime
                            self.UpdateData(ednMacLegacyObj)
                            #self.addServiceDatatoDB(ednMacLegacyObj, ednServiceMappingObjectLongest)
                            break
                        if next==1:
                            continue
                    
                    #ednServiceMappingObjectShortest = EDN_SERVICE_MAPPING.query.filter(EDN_SERVICE_MAPPING.device_a_name==ednMacLegacyObj.device_a_name).filter(EDN_SERVICE_MAPPING.device_a_interface==ednMacLegacyObj.device_a_interface).first()
                    if ednMacLegacyObj.device_b_ip == '':
                        dummyIP = ednMacLegacyObj.device_b_ip 
                        dummyIP = '0.0.0.0'
                        ednServiceMappingObjectShortest = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY, SERVICE_VENDOR FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac NOT LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_ip NOT LIKE '%%{dummyIP}%%' )  or (device_b_ip LIKE '%%{dummyIP}%%' and device_b_ip!='' and device_b_mac NOT LIKE'%%{ednMacLegacyObj.device_b_mac},%%' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}') or (device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}' and device_b_ip NOT LIKE '%%{dummyIP}%%'));") #and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);")                    #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' )  or device_b_ip= '{ednMacLegacyObj.device_b_ip}' or device_b_mac= '{ednMacLegacyObj.device_b_mac}') and creation_date = (SELECT max(creation_date) FROM edn_service_mapping;", file=sys.stderr)
                        # print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac NOT LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_ip NOT LIKE '%%{dummyIP}%%' )  or (device_b_ip LIKE '%%{dummyIP}%%' and device_b_ip!='' and device_b_mac NOT LIKE'%%{ednMacLegacyObj.device_b_mac},%%' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}') or (device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}' and device_b_ip NOT LIKE '%%{dummyIP}%%'));", file=sys.stderr)
                        #ednServiceMappingObjectShortest = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY, SERVICE_VENDOR FROM edn_service_mapping WHERE ((device_b_ip LIKE '%%{dummyIP}%%' and device_b_ip!='' and device_b_mac NOT LIKE'%%{ednMacLegacyObj.device_b_mac},%%' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}') or (device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}' and device_b_ip NOT LIKE '%%{dummyIP}%%') or (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac NOT LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_ip NOT LIKE '%%{dummyIP}%%' ));") #and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);")                    #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' )  or device_b_ip= '{ednMacLegacyObj.device_b_ip}' or device_b_mac= '{ednMacLegacyObj.device_b_mac}') and creation_date = (SELECT max(creation_date) FROM edn_service_mapping;", file=sys.stderr)

                    else:
                        ednServiceMappingObjectShortest = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY, SERVICE_VENDOR FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac NOT LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_ip NOT LIKE '%%{ednMacLegacyObj.device_b_ip},%%' )  or (device_b_ip LIKE '%%{ednMacLegacyObj.device_b_ip},%%' and device_b_ip!='' and device_b_mac NOT LIKE'%%{ednMacLegacyObj.device_b_mac},%%' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}') or (device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}' and device_b_ip NOT LIKE '%%{ednMacLegacyObj.device_b_ip},%%'));") #and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);")                    #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' )  or device_b_ip= '{ednMacLegacyObj.device_b_ip}' or device_b_mac= '{ednMacLegacyObj.device_b_mac}') and creation_date = (SELECT max(creation_date) FROM edn_service_mapping;", file=sys.stderr)
                        #ednServiceMappingObjectShortest = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY, SERVICE_VENDOR FROM edn_service_mapping WHERE ((device_b_ip LIKE '%%{ednMacLegacyObj.device_b_ip},%%' and device_b_ip!='' and device_b_mac NOT LIKE'%%{ednMacLegacyObj.device_b_mac},%%' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}') or (device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}' and device_b_ip NOT LIKE '%%{ednMacLegacyObj.device_b_ip},%%') or (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac NOT LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_ip NOT LIKE '%%{ednMacLegacyObj.device_b_ip},%%' ));") #and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);")                    #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' )  or device_b_ip= '{ednMacLegacyObj.device_b_ip}' or device_b_mac= '{ednMacLegacyObj.device_b_mac}') and creation_date = (SELECT max(creation_date) FROM edn_service_mapping;", file=sys.stderr)


                    if ednServiceMappingObjectShortest:
                        for row in ednServiceMappingObjectShortest:
                          
                            service_mapped=""
                            mappedService = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY FROM edn_service_mapping WHERE (device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac NOT LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_ip NOT LIKE '%%{ednMacLegacyObj.device_b_ip},%%' );") #and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);")                    #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' )  or device_b_ip= '{ednMacLegacyObj.device_b_ip}' or device_b_mac= '{ednMacLegacyObj.device_b_mac}') and creation_date = (SELECT max(creation_date) FROM edn_service_mapping;", file=sys.stderr)
                            for row2 in mappedService:
                                if row[0]:
                                   service_mapped+= "Interface"
                                   break
                            
                            mappedService = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY FROM edn_service_mapping WHERE (device_b_ip LIKE '%%{ednMacLegacyObj.device_b_ip},%%' and device_b_ip!='' and device_b_mac NOT LIKE'%%{ednMacLegacyObj.device_b_mac},%%' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}');") #and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);")                    #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' )  or device_b_ip= '{ednMacLegacyObj.device_b_ip}' or device_b_mac= '{ednMacLegacyObj.device_b_mac}') and creation_date = (SELECT max(creation_date) FROM edn_service_mapping;", file=sys.stderr)
                            for row2 in mappedService:
                                if row[0]:
                                    service_mapped+= "IP"
                                    break

                            mappedService = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY FROM edn_service_mapping WHERE (device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}' and device_b_ip NOT LIKE '%%{ednMacLegacyObj.device_b_ip},%%');") #and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);")                    #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' )  or device_b_ip= '{ednMacLegacyObj.device_b_ip}' or device_b_mac= '{ednMacLegacyObj.device_b_mac}') and creation_date = (SELECT max(creation_date) FROM edn_service_mapping;", file=sys.stderr)
                            for row2 in mappedService:
                                if row[0]:
                                    service_mapped+= "MAC"
                                    break

                                                        
                          
                            #print(f"3333  {row}", file=sys.stderr)
                            ednMacLegacyObj.service_matched_by= service_mapped
                            ednMacLegacyObj.device_b_system_name= row[4]
                            ednMacLegacyObj.device_b_type= row[5]
                            ednMacLegacyObj.server_name= row[0]
                            ednMacLegacyObj.owner_name= row[1]
                            ednMacLegacyObj.owner_contact= row[2]
                            ednMacLegacyObj.owner_email= row[3]
                            ednMacLegacyObj.server_os= row[6]
                            ednMacLegacyObj.app_name= row[7]
                            ednMacLegacyObj.modified_by= row[8]
                            ednMacLegacyObj.service_vendor= row[9]
                            #print("Updating Service Mapping Data")
                            next=1
                            #print(f"S {ednMacLegacyObj} SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac!='{ednMacLegacyObj.device_b_mac}' and device_b_ip!= '{ednMacLegacyObj.device_b_ip}' )  or (device_b_ip= '{ednMacLegacyObj.device_b_ip}' and device_b_ip!='' and device_b_mac!='{ednMacLegacyObj.device_b_mac}' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}') or (device_b_mac= '{ednMacLegacyObj.device_b_mac}' and device_b_mac!='' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}' and device_b_ip!= '{ednMacLegacyObj.device_b_ip}')) and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);", file=sys.stderr)
                            # if ednMacLegacyObj.device_b_ip == '10.14.114.5' or ednMacLegacyObj.device_b_ip == '10.14.148.83':
                            # print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME, MODIFIED_BY FROM edn_service_mapping WHERE ((device_a_name= '{ednMacLegacyObj.device_a_name}' and device_a_interface= '{ednMacLegacyObj.device_a_interface}' and  device_b_mac NOT LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_ip NOT LIKE '%%{ednMacLegacyObj.device_b_ip},%%' )  or (device_b_ip LIKE '%%{ednMacLegacyObj.device_b_ip},%%' and device_b_ip!='' and device_b_mac NOT LIKE'%%{ednMacLegacyObj.device_b_mac},%%' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}') or (device_b_mac LIKE '%%{ednMacLegacyObj.device_b_mac},%%' and device_b_mac!='' and  device_a_name!= '{ednMacLegacyObj.device_a_name}' and device_a_interface!= '{ednMacLegacyObj.device_a_interface}' and device_b_ip NOT LIKE '%%{ednMacLegacyObj.device_b_ip},%%'));")
                            print(f"Matched Service Mapping Shortest Match for ID: {ednMacLegacyObj.edn_mac_legacy_id}")
                            ednMacLegacyObj.modification_date= newTime
                            self.UpdateData(ednMacLegacyObj)
                            #self.addServiceDatatoDB(ednMacLegacyObj, ednServiceMappingObjectLongest)
                            break
                        if next==1:
                            continue
                        
                    

        except Exception as e:
            print(f"Failed to update Service Mapping for EDN Mac Legacy {e}", file=sys.stderr)  
            traceback.print_exc() 
        print("Populated Service Mapping in Edn Mac Legacy", file=sys.stderr)      

        statusTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ednMacLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-MAC-Legacy-Service-Mapping-Sync").first()
        try:
            ednMacLegacyStatus.script = "EDN-MAC-Legacy-Service-Mapping-Sync"
            ednMacLegacyStatus.status = "Completed"
            ednMacLegacyStatus.creation_date= statusTime
            ednMacLegacyStatus.modification_date= statusTime
            db.session.add(ednMacLegacyStatus)
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"Error while updating script status {e}", file=sys.stderr)  


    def addEdnLldpACIServiceMapping(self, current_time):
        try:
            ednLldpACIObjs = EDN_LLDP_ACI.query.filter_by(creation_date=current_time).all()
            
            if ednLldpACIObjs:

                for ednLldpACIObj in ednLldpACIObjs: 
                    #ednServiceMappingObjectLongest = EDN_SERVICE_MAPPING.query.filter(EDN_SERVICE_MAPPING.device_a_name==ednLldpACIObj.device_a_name).filter(EDN_SERVICE_MAPPING.device_a_interface==ednLldpACIObj.device_a_interface).filter(EDN_SERVICE_MAPPING.device_b_ip==ednLldpACIObj.device_b_ip).filter(EDN_SERVICE_MAPPING.device_b_mac==ednLldpACIObj.device_b_mac).first()
                    ednServiceMappingObjectLongest = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE (device_a_name= '{ednLldpACIObj.device_a_name}' and device_a_interface= '{ednLldpACIObj.device_a_interface}' and  device_b_ip= '{ednLldpACIObj.device_b_ip}'  and device_b_mac= '{ednLldpACIObj.device_b_mac}')  and creation_date = (SELECT max(creation_date) FROM edn_service_mapping) ;")
                    
                    next=0
                    if ednServiceMappingObjectLongest:
                        #print(f"SELECT * FROM edn_service_mapping WHERE device_a_name= '{ednLldpACIObj.device_a_name}' and device_a_interface= '{ednLldpACIObj.device_a_interface}' and  device_b_ip= '{ednLldpACIObj.device_b_ip}'  and device_b_mac= '{ednLldpACIObj.device_b_mac}'" , file=sys.stderr)

                        for row in ednServiceMappingObjectLongest:
                            ednLldpACIObj.device_b_system_name= row[4]
                            ednLldpACIObj.device_b_type= row[5]
                            ednLldpACIObj.server_name= row[0]
                            ednLldpACIObj.owner_name= row[1]
                            ednLldpACIObj.owner_contact= row[2]
                            ednLldpACIObj.owner_email= row[3]
                            ednLldpACIObj.server_os= row[6]
                            ednLldpACIObj.app_name= row[7]
                            print("Updating Service Mapping Data")
                            next=1
                            self.UpdateData(ednLldpACIObj)
                            #self.addServiceDatatoDB(ednLldpACIObj, ednServiceMappingObjectLongest)
                            break
                        if next==1:
                            continue
                    
                    
                    ednServiceMappingObjectMedium = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{ednLldpACIObj.device_a_name}' and device_a_interface= '{ednLldpACIObj.device_a_interface}' and  device_b_ip= '{ednLldpACIObj.device_b_ip}')  or (device_a_name= '{ednLldpACIObj.device_a_name}' and device_a_interface= '{ednLldpACIObj.device_a_interface}' and  device_b_mac= '{ednLldpACIObj.device_b_mac}') or (device_b_mac= '{ednLldpACIObj.device_b_mac}' and  device_b_ip= '{ednLldpACIObj.device_b_ip}')) and creation_date = (SELECT max(creation_date) FROM edn_service_mapping) ;")
                    
                    #ednServiceMappingObjectMedium = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ( (device_b_mac= '{ednLldpACIObj.device_b_mac}' and  device_b_ip= '{ednLldpACIObj.device_b_ip}') or (device_a_name= '{ednLldpACIObj.device_a_name}' and device_a_interface= '{ednLldpACIObj.device_a_interface}' and  device_b_ip= '{ednLldpACIObj.device_b_ip}')  or (device_a_name= '{ednLldpACIObj.device_a_name}' and device_a_interface= '{ednLldpACIObj.device_a_interface}' and  device_b_mac= '{ednLldpACIObj.device_b_mac}')) and creation_date = (SELECT max(creation_date) FROM edn_service_mapping) ;")

                    #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE (device_a_name= '{ednLldpACIObj.device_a_name}' and device_a_interface= '{ednLldpACIObj.device_a_interface}' and  device_b_ip= '{ednLldpACIObj.device_b_ip}')  or (device_a_name= '{ednLldpACIObj.device_a_name}' and device_a_interface= '{ednLldpACIObj.device_a_interface}' and  device_b_mac= '{ednLldpACIObj.device_b_mac}') or (device_b_mac= '{ednLldpACIObj.device_b_mac}' and  device_b_ip= '{ednLldpACIObj.device_b_ip}');")

                    if ednServiceMappingObjectMedium:
                        #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE (device_a_name= '{ednLldpACIObj.device_a_name}' and device_a_interface= '{ednLldpACIObj.device_a_interface}' and  device_b_ip= '{ednLldpACIObj.device_b_ip}')  or (device_a_name= '{ednLldpACIObj.device_a_name}' and device_a_interface= '{ednLldpACIObj.device_a_interface}' and  device_b_mac= '{ednLldpACIObj.device_b_mac}') or (device_b_mac= '{ednLldpACIObj.device_b_mac}' and  device_b_ip= '{ednLldpACIObj.device_b_ip}') ;")

                        for row in ednServiceMappingObjectMedium:
                            ednLldpACIObj.device_b_system_name= row[4]
                            ednLldpACIObj.device_b_type= row[5]
                            ednLldpACIObj.server_name= row[0]
                            ednLldpACIObj.owner_name= row[1]
                            ednLldpACIObj.owner_contact= row[2]
                            ednLldpACIObj.owner_email= row[3]
                            ednLldpACIObj.server_os= row[6]
                            ednLldpACIObj.app_name= row[7]
                            print("Updating Service Mapping Data")
                            next=1
                            self.UpdateData(ednLldpACIObj)
                            #self.addServiceDatatoDB(ednLldpACIObj, ednServiceMappingObjectLongest)
                            break
                        if next==1:
                            continue
                    
                    ednServiceMappingObjectShortest =  phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{ednLldpACIObj.device_a_name}' and device_a_interface= '{ednLldpACIObj.device_a_interface}' )  or device_b_ip= '{ednLldpACIObj.device_b_ip}' or device_b_mac= '{ednLldpACIObj.device_b_mac}') and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);")

                    #ednServiceMappingObjectShortest =  phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE (device_b_ip= '{ednLldpACIObj.device_b_ip}' or device_b_mac= '{ednLldpACIObj.device_b_mac}' or (device_a_name= '{ednLldpACIObj.device_a_name}' and device_a_interface= '{ednLldpACIObj.device_a_interface}' )) and creation_date = (SELECT max(creation_date) FROM edn_service_mapping);")


                    if ednServiceMappingObjectShortest:
                        #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE (device_a_name= '{ednLldpACIObj.device_a_name}' and device_a_interface= '{ednLldpACIObj.device_a_interface}' )  or device_b_ip= '{ednLldpACIObj.device_b_ip}' or device_b_ip= '{ednLldpACIObj.device_b_ip}' ;")
                        for row in ednServiceMappingObjectShortest:
                            #print(f"3333  {row}", file=sys.stderr)
                            ednLldpACIObj.device_b_system_name= row[4]
                            ednLldpACIObj.device_b_type= row[5]
                            ednLldpACIObj.server_name= row[0]
                            ednLldpACIObj.owner_name= row[1]
                            ednLldpACIObj.owner_contact= row[2]
                            ednLldpACIObj.owner_email= row[3]
                            ednLldpACIObj.server_os= row[6]
                            ednLldpACIObj.app_name= row[7]
                            print("Updating Service Mapping Data")
                            next=1
                            self.UpdateData(ednLldpACIObj)
                            #self.addServiceDatatoDB(ednLldpACIObj, ednServiceMappingObjectLongest)
                            break
                        if next==1:
                            continue
                    

        except Exception as e:
            print(f"Failed to update Service Mapping for EDN Lldp Aci {e}", file=sys.stderr)   
        print("Populated Service Mapping in Edn Lldp Aci", file=sys.stderr)        

    def addIgwLldpACIServiceMapping(self, current_time):
            try:
                IgwLldpACIObjs = IGW_LLDP_ACI.query.filter_by(creation_date=current_time).all()
                
                if IgwLldpACIObjs:

                    for IgwLldpACIObj in IgwLldpACIObjs: 
                        #IgwServiceMappingObjectLongest = IGW_SERVICE_MAPPING.query.filter(IGW_SERVICE_MAPPING.device_a_name==IgwLldpACIObj.device_a_name).filter(IGW_SERVICE_MAPPING.device_a_interface==IgwLldpACIObj.device_a_interface).filter(IGW_SERVICE_MAPPING.device_b_ip==IgwLldpACIObj.device_b_ip).filter(IGW_SERVICE_MAPPING.device_b_mac==IgwLldpACIObj.device_b_mac).first()
                        IgwServiceMappingObjectLongest = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE (device_a_name= '{IgwLldpACIObj.device_a_name}' and device_a_interface= '{IgwLldpACIObj.device_a_interface}' and  device_b_ip= '{IgwLldpACIObj.device_b_ip}'  and device_b_mac= '{IgwLldpACIObj.device_b_mac}')  and creation_date = (SELECT max(creation_date) FROM igw_service_mapping) ;")
                        
                        next=0
                        if IgwServiceMappingObjectLongest:
                            #print(f"SELECT * FROM Igw_service_mapping WHERE device_a_name= '{IgwLldpACIObj.device_a_name}' and device_a_interface= '{IgwLldpACIObj.device_a_interface}' and  device_b_ip= '{IgwLldpACIObj.device_b_ip}'  and device_b_mac= '{IgwLldpACIObj.device_b_mac}'" , file=sys.stderr)
                            if IgwLldpACIObj.device_a_name == "ADAM-WLEF-CI-311":
                                print("333", file=sys.stderr)
                            for row in IgwServiceMappingObjectLongest:
                                #print(f"1111111111  {row}", file=sys.stderr)
                                IgwLldpACIObj.device_b_system_name= row[4]
                                IgwLldpACIObj.device_b_type= row[5]
                                IgwLldpACIObj.server_name= row[0]
                                IgwLldpACIObj.owner_name= row[1]
                                IgwLldpACIObj.owner_contact= row[2]
                                IgwLldpACIObj.owner_email= row[3]
                                IgwLldpACIObj.server_os= row[6]
                                IgwLldpACIObj.app_name= row[7]
                                print("Updating Service Mapping Data")
                                next=1
                                self.UpdateData(IgwLldpACIObj)
                                #self.addServiceDatatoDB(IgwLldpACIObj, IgwServiceMappingObjectLongest)
                                break
                            if next==1:
                                continue
                        
                        
                        IgwServiceMappingObjectMedium = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{IgwLldpACIObj.device_a_name}' and device_a_interface= '{IgwLldpACIObj.device_a_interface}' and  device_b_ip= '{IgwLldpACIObj.device_b_ip}')  or (device_a_name= '{IgwLldpACIObj.device_a_name}' and device_a_interface= '{IgwLldpACIObj.device_a_interface}' and  device_b_mac= '{IgwLldpACIObj.device_b_mac}') or (device_b_mac= '{IgwLldpACIObj.device_b_mac}' and  device_b_ip= '{IgwLldpACIObj.device_b_ip}')) and creation_date = (SELECT max(creation_date) FROM igw_service_mapping) ;")

                        #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM Igw_service_mapping WHERE (device_a_name= '{IgwLldpACIObj.device_a_name}' and device_a_interface= '{IgwLldpACIObj.device_a_interface}' and  device_b_ip= '{IgwLldpACIObj.device_b_ip}')  or (device_a_name= '{IgwLldpACIObj.device_a_name}' and device_a_interface= '{IgwLldpACIObj.device_a_interface}' and  device_b_mac= '{IgwLldpACIObj.device_b_mac}') or (device_b_mac= '{IgwLldpACIObj.device_b_mac}' and  device_b_ip= '{IgwLldpACIObj.device_b_ip}');")

                        if IgwServiceMappingObjectMedium:
                            #print(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM Igw_service_mapping WHERE (device_a_name= '{IgwLldpACIObj.device_a_name}' and device_a_interface= '{IgwLldpACIObj.device_a_interface}' and  device_b_ip= '{IgwLldpACIObj.device_b_ip}')  or (device_a_name= '{IgwLldpACIObj.device_a_name}' and device_a_interface= '{IgwLldpACIObj.device_a_interface}' and  device_b_mac= '{IgwLldpACIObj.device_b_mac}') or (device_b_mac= '{IgwLldpACIObj.device_b_mac}' and  device_b_ip= '{IgwLldpACIObj.device_b_ip}') ;")
                            if IgwLldpACIObj.device_a_name == "ADAM-WLEF-CI-311":
                                print("444", file=sys.stderr)
                            for row in IgwServiceMappingObjectMedium:
                                #(f"222222  {row}", file=sys.stderr)
                                IgwLldpACIObj.device_b_system_name= row[4]
                                IgwLldpACIObj.device_b_type= row[5]
                                IgwLldpACIObj.server_name= row[0]
                                IgwLldpACIObj.owner_name= row[1]
                                IgwLldpACIObj.owner_contact= row[2]
                                IgwLldpACIObj.owner_email= row[3]
                                IgwLldpACIObj.server_os= row[6]
                                IgwLldpACIObj.app_name= row[7]
                                print("Updating Service Mapping Data")
                                next=1
                                self.UpdateData(IgwLldpACIObj)
                                #self.addServiceDatatoDB(IgwLldpACIObj, IgwServiceMappingObjectLongest)
                                break
                            if next==1:
                                continue
                        
                        #IgwServiceMappingObjectShortest = IGW_SERVICE_MAPPING.query.filter(IGW_SERVICE_MAPPING.device_a_name==IgwLldpACIObj.device_a_name).filter(IGW_SERVICE_MAPPING.device_a_interface==IgwLldpACIObj.device_a_interface).first()
                        IgwServiceMappingObjectShortest = phy_engine.execute(f"SELECT SERVER_NAME, OWNER_NAME, OWNER_CONTACT, OWNER_EMAIL, DEVICE_B_SYSTEM_NAME, DEVICE_B_TYPE, SERVER_OS, APP_NAME FROM edn_service_mapping WHERE ((device_a_name= '{IgwLldpACIObj.device_a_name}' and device_a_interface= '{IgwLldpACIObj.device_a_interface}' )  or device_b_ip= '{IgwLldpACIObj.device_b_ip}' or device_b_mac= '{IgwLldpACIObj.device_b_mac}') and creation_date = (SELECT max(creation_date) FROM igw_service_mapping);")

                        if IgwServiceMappingObjectShortest:
                            if IgwLldpACIObj.device_a_name == "ADAM-WLEF-CI-311":
                                print("55555", file=sys.stderr)
                            for row in IgwServiceMappingObjectShortest:
                                #print(f"3333  {row}", file=sys.stderr)
                                IgwLldpACIObj.device_b_system_name= row[4]
                                IgwLldpACIObj.device_b_type= row[5]
                                IgwLldpACIObj.server_name= row[0]
                                IgwLldpACIObj.owner_name= row[1]
                                IgwLldpACIObj.owner_contact= row[2]
                                IgwLldpACIObj.owner_email= row[3]
                                IgwLldpACIObj.server_os= row[6]
                                IgwLldpACIObj.app_name= row[7]
                                print("Updating Service Mapping Data")
                                next=1
                                self.UpdateData(IgwLldpACIObj)
                                #self.addServiceDatatoDB(IgwLldpACIObj, IgwServiceMappingObjectLongest)
                                break
                            if next==1:
                                continue    

            except Exception as e:
                print(f"Failed to update Service Mapping for IGW Lldp Aci {e}", file=sys.stderr)   
            print("Populated Service Mapping in Igw Lldp Aci", file=sys.stderr)        

    def addItSnapshotServiceMapping(self):
        try:
            time = datetime.now()
            queryString = f"select count(*) from it_physical_servers_table where creation_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_app_table where creation_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result1 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_os_table where creation_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result2 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_ip_table where creation_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result3 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_mac_table where creation_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result4 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_owner_table where creation_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result5 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_physical_servers_table where modification_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result6 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_app_table where modification_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result7 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_os_table where modification_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result8 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_ip_table where modification_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result9 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_mac_table where modification_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result10 = phy_engine.execute(queryString).scalar()
            queryString = f"select count(*) from it_owner_table where modification_date >= CONVERT_TZ(DATE(NOW() - INTERVAL 7 DAY), 'UTC', 'Asia/Riyadh');"
            result11 = phy_engine.execute(queryString).scalar()

            objList = [
                {
                    "physical_inserted": int(result),
                    "app_inserted": int(result1),
                    "os_inserted": int(result2),
                    "ip_inserted": int(result3),
                    "mac_inserted": int(result4),
                    "owner_inserted": int(result5),
                    "physical_updated": int(result6),
                    "app_updated": int(result7),
                    "os_updated": int(result8),
                    "ip_updated": int(result9),
                    "mac_updated": int(result10),
                    "owner_updated": int(result11)
                }
            ]

            for obj in objList:
                try:
                    snapshots = IT_SERVICES_SNAPSHOTS_TABLE()

                    snapshots.physical_servers_inserted = obj['physical_inserted']
                    snapshots.apps_inserted = obj['app_inserted']
                    snapshots.os_inserted = obj['os_inserted']
                    snapshots.ips_inserted = obj['ip_inserted']
                    snapshots.macs_inserted = obj['mac_inserted']
                    snapshots.owners_inserted = obj['owner_inserted']
                    snapshots.physical_servers_updated = obj['physical_updated']
                    snapshots.apps_updated = obj['app_updated']
                    snapshots.os_updated = obj['os_updated']
                    snapshots.ips_updated = obj['ip_updated']
                    snapshots.macs_updated = obj['mac_updated']
                    snapshots.owners_updated = obj['owner_updated']
                    snapshots.creation_date= time
                    snapshots.modification_date= time

                    self.InsertData(snapshots)
                    print("Data Inserted for It Snapshot Service Mapping Into DB", file=sys.stderr)

                except Exception as e:
                    traceback.print_exc()
                    print(f"Error Adding Data: {e}", file=sys.stderr)
                    
        except Exception as e:
            traceback.print_exc()
            return str(e), 500