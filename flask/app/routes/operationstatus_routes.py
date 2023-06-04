import sys
from app import app, write_operational, read_operational
from flask_jsonpify import jsonify
from influxdb_client import Point, WritePrecision
from datetime import datetime
import json
from random import randint
from app.pullers.IOS.ios_opr import IOSPullerOpr
from app.pullers.IOSXE.ios_xe_opr import XEPullerOpr
from app.pullers.IOSXR.ios_xr_opr import XRPullerOpr
from app.pullers.NXOS.nxos_opr import NXOSPullerOpr

# ios = 10.20.0.1
# xr = 10.42.211.15
# xe = 10.26.233.216
# nxos = 10.42.1.132 

@app.route("/op/ios")
def OP():

    org = "mobily"
    bucket = "operational_status"
    opr_inv = IOSPullerOpr()
    print("IOS Oper puller started", file=sys.stderr)
    pullerData =  opr_inv.get_operational_data([
        {
            "host": "10.20.0.1",
            "user": "srv00047",
            "pwd": "5FPB4!!1c9&g*iJ9"
        }])
    print (pullerData, file=sys.stderr)
    ### Get Data from sample file
    #pullerData = json.load(open('temp/opr_data.json',))
    '''
    for cpu in pullerData['10.66.211.30']['cpu']:
           print (cpu, file=sys.stderr)
           point = Point("cpu").tag("host", "sanbox").tag("node", cpu['node-name']).field("total-cpu-one-minute", randint(1,10)).field("total-cpu-five-minute", randint(15,30)).field("total-cpu-fifteen-minute", randint(30,50)).time(datetime.now(), WritePrecision.MS)
           write_operational.write(bucket, org, point)
    '''
    '''
    #Use InfluxDB Line Protocol to write data#
    data = "mem,host=host1 used_percent=23.43234543"
    write_operational.write(bucket, org, data)

    #Use a Data Point to write data#
    point = Point("mem").tag("host", "host1").field("used_percent", 23.43234543).time(datetime.utcnow(), WritePrecision.MS)
    write_operational.write(bucket, org, point)

    #Use a Batch Sequence to write data#
    sequence = ["mem,host=host1 used_percent=23.43234543",
            "mem,host=host1 available_percent=15.856523"]
    write_operational.write(bucket, org, sequence)

    #Execute a Flux query#
    #query = f'from(bucket: \\"{bucket}\\") |> range(start: -10h)'
    #tables = query(query, org=org)

    #for table in tables:
    #    print(table, file=sys.stderr)
    #    for row in table.records:
    #        print (row.values, file=sys.stderr)

    query = 'from(bucket: "operational_status")\
        |> range(start: -1h)\
        |> filter(fn: (r) => r._measurement == "cpu")\
        |> filter(fn: (r) => r._field == "total-cpu-one-minute")\
        |> filter(fn: (r) => r.node == "0/0/CPU0")'

    result = read_operational.query(org=org, query=query)
    results = []
    for table in result:
        for record in table.records:
                results.append((record.get_value(), record.get_field()))

    print(results, file=sys.stderr)


   '''
   
    return pullerData

@app.route("/op/xe")
def OP_xe():
    opr_inv = XEPullerOpr()
    print("XE Oper puller started", file=sys.stderr)
    pullerData =  opr_inv.get_operational_data([
        {
            "host": "10.26.233.216",
            "user": "srv00047",
            "pwd": "5FPB4!!1c9&g*iJ9"
        }])
    print (pullerData, file=sys.stderr)
    return pullerData

@app.route("/op/xr")
def OP_xr():
    opr_inv = XRPullerOpr()
    print("XR Oper puller started", file=sys.stderr)
    pullerData =  opr_inv.get_operational_data([
        {
            "host": "10.42.211.15",
            "user": "srv00047",
            "pwd": "5FPB4!!1c9&g*iJ9"
        }])
    print (pullerData, file=sys.stderr)
    return pullerData

@app.route("/op/nxos")
def OP_nxos():
    opr_inv = NXOSPullerOpr()
    print("nxos Oper puller started", file=sys.stderr)
    pullerData =  opr_inv.get_operational_data([
        {
            "host": "10.42.1.132",
            "user": "srv00047",
            "pwd": "5FPB4!!1c9&g*iJ9"
        }])
    print (pullerData, file=sys.stderr)
    return pullerData