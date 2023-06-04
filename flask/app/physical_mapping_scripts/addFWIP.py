# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 22:05:49 2021

@author: HP
"""
#from asyncio.windows_events import NULL
from operator import or_
import re, sys, json
import traceback
import pandas as pd
from pandas import read_excel
from app import db, phy_engine
from app.models.phy_mapping_models import EDN_MAC_LEGACY,EDN_FIREWALL_ARP, IGW_LLDP_ACI, EDN_LLDP_ACI
from app.models.phy_mapping_models import SCRIPT_STATUS
from datetime import date, datetime
from multiprocessing.pool import ThreadPool
import concurrent.futures

class AddFwIP():
    def matchEdnMacLegacy(self, ednFirewallArpObj, current_time,  newTime):
        print("In For Loop Matching Thread", file=sys.stderr)
        try:
            #print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%", file=sys.stderr)
            #print(f"Fire ip is, {ednFirewallArpObj}", file=sys.stderr)                
            mac = ednFirewallArpObj["MAC"]
            ip = ednFirewallArpObj["IP"]
            fw_datacenter= ednFirewallArpObj["DC"]
            firewallName= ednFirewallArpObj["FIREWALL_ID"]
            firewallSource= ednFirewallArpObj["ARP_SOURCE_TYPE"]
            parsed_ip=""
            for single_ip in ip.split(','):
                if single_ip not in parsed_ip:
                    parsed_ip+=single_ip+","

            #print(f"Parsed ip is, {parsed_ip}", file=sys.stderr) 

            fwMac=""
            index=0
            for alph in mac:
                if(index%4==0 and index!=0):
                    fwMac+="."
                fwMac+=alph
                index+=1
            #print(f"Fw Mac  is, {fwMac}", file=sys.stderr) 
            ednMacLegacyObjs = EDN_MAC_LEGACY.query.filter_by(device_b_mac=fwMac).filter_by(creation_date=current_time).all()
            #print(f"MAC Legacy Obj  is, {ednMacLegacyObjs}", file=sys.stderr) 
            
            for ednMacLegacyObj in ednMacLegacyObjs:
                try: 
                    ednIP= ednMacLegacyObj.device_b_ip
                    if ednIP is None:
                        ednIP=""
                    device_a_name= ednMacLegacyObj.device_a_name
                    #print(f"$$$$$$$$$$$$$$$$$$$$$ {device_a_name}     {ednIP}", file=sys.stderr)
                    datacenter= self.getDatacenter(device_a_name)
                    #print(f"DDDDDDDDDDDDDDD {datacenter}", file=sys.stderr)
                    
                    if(ednIP=="" or "0.0.0.0" in ednIP) and datacenter== fw_datacenter:
                        try:
                            ednIP= ednMacLegacyObj.device_b_ip
                            ednMacLegacyObj.device_b_ip= parsed_ip.rstrip(',')
                            ednMacLegacyObj.arp_source_name= firewallName
                            ednMacLegacyObj.arp_source_type= firewallSource
                            ednMacLegacyObj.modification_date= newTime
                            db.session.flush()
                            db.session.commit()
                            print(f"Successfully update Device B IP {fwMac}", file=sys.stderr)
                        except Exception as e:
                            db.session.rollback()
                            print(f"Failed to update Device B IP {e}", file=sys.stderr)
                            traceback.print_exc()
                except Exception as e:   
                    print("Exception occured in ip loop {e}", file=sys.stderr)    

        except Exception as e:   
            print(f"Exception occured in firewall loop {e}", file=sys.stderr)  

    def parseMac(self, fwMac, mac):
       
        mac_str =  ""
        if fwMac is not None:
            if not mac:
                pass
            else:    
                if "." in mac:
                    strFW = mac.split('.')
                if ":" in mac:
                    strFW = mac.split(':')
                for s in strFW:
                    if mac_str=="":
                        mac_str = s
                    else:
                        mac_str = mac_str + s
        return mac_str

    def getDatacenter(self, switch_id):
        dataCenter=""
        dataCenter= switch_id.split('-')[0]
        '''
        prefix= (re.findall(r'^(\d+.\d+)',ip))[0]
        if prefix == "10.64":
            dataCenter= "RYD-MLG-ENT"
        elif prefix == "10.73":
            dataCenter= "RYD-MLGII-ENT"
        elif prefix == "10.14":
            dataCenter= "RYD-SLY-ISR"
        elif prefix == "10.67":
            dataCenter= "RYD-MLZ-ENT"
        elif prefix == "10.66":
            dataCenter= "RYD-SLM-ENT"
        elif prefix == "10.6":
            dataCenter= "RYD-DAN-ENT"
        elif prefix == "10.32":
            dataCenter= "DAM-ALR-ENT"
        elif prefix == "10.42":
            dataCenter= "DAM-ADM-ENT"
        elif prefix == "10.41":
            dataCenter= "DAM-RAK-ENT"
        elif prefix == "10.81":
            dataCenter= "JED-SAF-ENT"
        elif prefix == "10.22":
            dataCenter= "JED-UBH-ENT"
        elif prefix == "10.82":
            dataCenter= "WES-MDN-ENT"
        elif prefix == "10.83":
            dataCenter= "JED-BSLM-ENT"
        elif prefix == "10.20":
            dataCenter= "JED-LS-ENT"
        elif prefix == "10.87":
            dataCenter= "MAK-SWQ-ENT"
        elif prefix == "10.68":
            dataCenter= "QAS-UNZ-ENT"
        elif prefix == "10.9":
            dataCenter= "RYD-BUR-ENT"
        elif prefix == "10.78":
            dataCenter= "JED-OB2-ENT"
        elif prefix == "10.8":
            dataCenter= "RYD-KHJ-ENT"
        elif prefix == "10.85":
            dataCenter= "MAK-MTB-ENT"
        elif prefix == "10.76":
            dataCenter= "DAM-AHS-ENT"
        else:
            dataCenter="" 
        '''
        return dataCenter 

    def addFWIPToEdnMacLegacy(self, current_time, newTime):

        print("In EDN Firewall Arp", file=sys.stderr)
        statusTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ednMacLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-MAC-Legacy-FW-Sync").first()
        try:
            ednMacLegacyStatus.script = "EDN-MAC-Legacy-FW-Sync"
            ednMacLegacyStatus.status = "Running"
            ednMacLegacyStatus.creation_date= statusTime
            ednMacLegacyStatus.modification_date= statusTime
            db.session.add(ednMacLegacyStatus)
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"Error while updating script status {e}", file=sys.stderr)

        try:
            ednFirewallArpObjs = phy_engine.execute('SELECT * FROM edn_firewall_arp WHERE creation_date = (SELECT max(creation_date) FROM edn_firewall_arp)')
           
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:

                for i, ednFirewallArpObj in enumerate(ednFirewallArpObjs):
                    # Submit a task to the pool, passing the current argument
                    future = executor.submit(self.matchEdnMacLegacy, ednFirewallArpObj, current_time, newTime)
                #for ednFirewallArpObj in ednFirewallArpObjs:
                #    self.matchEdnMacLegacy(ednFirewallArpObj, current_time, newTime)                 
        
        except Exception as e:
            print(f"Failed to update Device B IP for EDN Mac Legacy {e}", file=sys.stderr)  
            traceback.print_exc() 
        print("Populated Firewall IP's in Edn Mac Legacy", file=sys.stderr)        
        
        statusTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ednMacLegacyStatus = SCRIPT_STATUS.query.filter(SCRIPT_STATUS.script== "EDN-MAC-Legacy-FW-Sync").first()
        try:
            ednMacLegacyStatus.script = "EDN-MAC-Legacy-FW-Sync"
            ednMacLegacyStatus.status = "Completed"
            ednMacLegacyStatus.creation_date= statusTime
            ednMacLegacyStatus.modification_date= statusTime
            db.session.add(ednMacLegacyStatus)
            db.session.commit() 
        except Exception as e:
            db.session.rollback()
            print(f"Error while updating script status {e}", file=sys.stderr)
        return 0
    
    def addFWIPToEdnLldpAci(self, current_time):
        try:
            ednFirewallArpObjs = EDN_FIREWALL_ARP.query.filter_by(creation_date=current_time)
            ednFirewallArpObjs = phy_engine.execute('SELECT * FROM edn_firewall_arp WHERE creation_date = (SELECT max(creation_date) FROM edn_firewall_arp)')
            for ednFirewallArpObj in ednFirewallArpObjs:
                mac = ednFirewallArpObj["MAC"]
                ip = ednFirewallArpObj["IP"]
                fw_datacenter= ednFirewallArpObj["DC"]
                parsed_ip=""
                for single_ip in ip.split(','):
                    if single_ip not in parsed_ip:
                        parsed_ip+=single_ip+","

                fwMac=""
                index=0
                for alph in mac:
                    if(index%2==0 and index!=0):
                        fwMac+=":"
                    fwMac+=alph
                    index+=1
                ednLldpAciObjs = EDN_LLDP_ACI.query.filter_by(device_b_mac=fwMac).filter_by(creation_date=current_time).all()
                for ednLldpAciObj in ednLldpAciObjs:
                    ednIP= ednLldpAciObj.device_b_ip
                    device_a_name= ednLldpAciObj.device_a_name
                    datacenter= self.getDatacenter(device_a_name) 
                    if (ednIP == "" or "0.0.0.0" in ednIP) and  datacenter== fw_datacenter:
                        try:                        
                            ednLldpAciObj.device_b_ip= parsed_ip.rstrip(',')
                            db.session.flush()
                            db.session.commit()
                            print(f"Successfully update Device B IP", file=sys.stderr)

                        except Exception as e:
                            db.session.rollback()
                            print(f"Failed to update Device B IP {e}", file=sys.stderr)
        except Exception as e:
            print(f"Failed to update Device B IP for EDN LLDP ACI {e}", file=sys.stderr)   
        print("Populated Firewall IP's in Edn LLDP ACI", file=sys.stderr)        
    
    def addFWIPToIgwLldpAci(self, current_time):
        try:
            igwFirewallArpObjs = EDN_FIREWALL_ARP.query.filter_by(creation_date=current_time)
            igwLldpAciObjs = IGW_LLDP_ACI.query.all()

            for ednFirewallArpObj in igwFirewallArpObjs:
                fwMac = ednFirewallArpObj.mac
                ip = ednFirewallArpObj.ip

                fw_datacenter= ednFirewallArpObj.dc
                parsed_ip=""
                for single_ip in ip.split(','):
                    if single_ip not in parsed_ip:
                        parsed_ip+=single_ip+","

                for igwLldpAciObj in igwLldpAciObjs:
                    try:
                        ednLegacyMac= igwLldpAciObj.device_b_mac
                        ednIP= igwLldpAciObj.device_b_ip
                        device_a_name= igwLldpAciObj.device_a_name
                        datacenter= self.getDatacenter(device_a_name) 
                        if (ednIP == None or ednIP== "" or ednIP=="0.0.0.0") and  datacenter== fw_datacenter:
                            parsedMac= self.parseMac(fwMac, ednLegacyMac)
                            if (fwMac == parsedMac):
                                igwLldpAciObj.device_b_ip= parsed_ip.rstrip(',')
                                db.session.flush()
                                db.session.commit()
                                print(f"Successfully update Device B IP", file=sys.stderr)

                    except Exception as e:
                        db.session.rollback()
                        print(f"Failed to update Device B IP {e}", file=sys.stderr)
        except Exception as e:
            print(f"Failed to update Device B IP for IGW LLDP ACI {e}", file=sys.stderr)   
        print("Populated Firewall IP's in IGW LLDP ACI", file=sys.stderr)        
            