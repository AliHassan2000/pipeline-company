from pysnmp.hlapi import *
import pandas as pd

def snmp(ip, oids):
    print(f'Connecting to {ip}')
    engn = SnmpEngine()
    community = UsmUserData('SWV3', 'snM9v3m08', '3Nt56m08', authProtocol=usmHMACSHAAuthProtocol, privProtocol=usmAesCfb128Protocol)# snmp community
    transport = UdpTransportTarget((ip, 161))
    cnxt = ContextData()
    print("Connected")
    data = get_Vms_name(engn, community, transport, cnxt)
    # for x in oids:
    # oid = ObjectType(ObjectIdentity('iso.3.6.1.2.1.25.6.3.1.2.25'))
    # errorIndication, errorStatus, errorIndex, varBinds = next(
    #     getCmd(engn, community, transport, cnxt, oid, ))
    
    # iterator = getCmd(
    #     SnmpEngine(),
    #     UsmUserData('SWV3', 'snM9v3m08', '3Nt56m08',
    #                 authProtocol=usmHMACSHAAuthProtocol,
    #                 privProtocol=usmAesCfb128Protocol),
    #     UdpTransportTarget((ip, 161)),
    #     ContextData(),
    #     ObjectType(ObjectIdentity('mib-2.47.1.1.1.1.2.1'))
    # )
    
        # errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    # login = ''
    # if errorIndication:
    #     print(f'Login failed::{ip} error=>{errorIndication}')
    #     login='fail'
    # elif errorStatus:
    #     print('%s at %s' % (errorStatus.prettyPrint(),
    #                         errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))

    # else:
    #     login='succcess'
    #     print(f'Login success::{ip}')
    #     for varBind in varBinds:
    #         print(' = '.join([x.prettyPrint() for x in varBind]))
    
    return data

def get_Vms_name(engn, community, transport, cnxt):
    try:
        vms_hostname = []
        for x in range(0, 100):
            oid = ObjectType(ObjectIdentity('iso.3.6.1.4.1.6876.2.1.1.2.'+str(x)))
            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(engn, community, transport, cnxt, oid, ))
            login = ''
            if errorIndication:
                print(f'Login failed:: error=>{errorIndication}')
                login='fail'
                break
            elif errorStatus:
                print('%s at %s' % (errorStatus.prettyPrint(),
                                    errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))

            else:
                for varBind in varBinds:
                    res = ' = '.join([x.prettyPrint() for x in varBind])
                    print(res)
                    if 'No Such Instance' not in res:
                        vms_hostname.append(res.split('=')[1].strip())
                    
                   
        print(vms_hostname)
        return vms_hostname
    except Exception as e:
        pass
    
# snmp('10.64.180.52')

# 'SNMPv2-MIB', 'sysName'
# iso.3.6.1.2.1.1.5.0 hostname
# iso.3.6.1.2.1.1.1.0 host version and build
# iso.3.6.1.4.1.6876.2.1.1.2.12 for vms name
# iso.3.6.1.2.1.47.1.1.1.1.2.1  descr
# iso.3.6.1.2.1.47.1.1.1.1.11.1  serial
# iso.3.6.1.2.1.47.1.1.1.1.12.1  vendor
# iso.3.6.1.2.1.47.1.1.1.1.13.1  pid
# iso.3.6.1.4.1.6876.1.2.0  hw_version

oids = ['iso.3.6.1.2.1.1.5.0','iso.3.6.1.2.1.1.1.0','iso.3.6.1.2.1.47.1.1.1.1.2.1','iso.3.6.1.2.1.47.1.1.1.1.2.1','iso.3.6.1.2.1.47.1.1.1.1.12.1','iso.3.6.1.2.1.47.1.1.1.1.13.1','iso.3.6.1.4.1.6876.1.2.0']

igw_sys = pd.read_excel(open('Mobily_Operations_Inventory_Seed_File_latest.xlsx', 'rb'), sheet_name ='EDN IPT Servers', dtype=str)
df = pd.DataFrame()

for ip, function in zip(igw_sys['ne_ip_address'],igw_sys['function']):
    if function=="ESXi Hypervisor":
        res = snmp(ip, oids)
        df = df.append(res, ignore_index=True)

writer = pd.ExcelWriter('ipt_vms_name2.xlsx', engine='openpyxl')
df.to_excel(writer, sheet_name='Sheet1', index=False)
writer.save()

# oids = {
#     'hostname':{'oid':'NMPv2-MIB::sysName.0'},
#     'descr':{'oid':'SNMPv2-MIB::sysDescr.0'},
#     'pid':{'oid':'SNMPv2-SMI::mib-2.47.1.1.1.1.13.1'},
#     'serial':{'oid':'SNMPv2-SMI::mib-2.47.1.1.1.1.11.1'},
#     'vendor':{'oid':'SNMPv2-SMI::mib-2.47.1.1.1.1.12.1'},
#     'version':{'oid':'SNMPv2-SMI::enterprises.6876.1.2.0'},
#     'vms_hostname':{'oid':'iso.3.6.1.4.1.6876.2.1.1.2.'}
# }

# SNMPv2-SMI::mib-2.47.1.1.1.1.11.1 seril
# iso.3.6.1.2.1.47.1.1.1.1.11.1 serial no
# SNMPv2-MIB::sysName.0 = JED-OBHR-IPT-ESX1.prod.mobily.lan
# Login success::10.78.158.28
# SNMPv2-MIB::sysDescr.0 = VMware ESXi 6.5.0 build-16207673 VMware, Inc. x86_64
# Login success::10.78.158.28
# SNMPv2-SMI::mib-2.47.1.1.1.1.2.1 = Cisco Systems Inc BE7H-M5-K9
# Login success::10.78.158.28
# SNMPv2-SMI::mib-2.47.1.1.1.1.2.1 = Cisco Systems Inc BE7H-M5-K9
# Login success::10.78.158.28
# SNMPv2-SMI::mib-2.47.1.1.1.1.12.1 = Cisco Systems Inc
# Login success::10.78.158.28
# SNMPv2-SMI::mib-2.47.1.1.1.1.13.1 = BE7H-M5-K9
# Login success::10.78.158.28
# SNMPv2-SMI::enterprises.6876.1.2.0 = 6.5.0