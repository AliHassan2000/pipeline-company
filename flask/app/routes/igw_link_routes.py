from ipaddress import ip_address
import json, sys, time
from logging import raiseExceptions
from socket import timeout
from app import app,db, tz, phy_engine
from flask import request, make_response, Response
import gzip
from flask_jsonpify import jsonify
from app.models.phy_mapping_models import *
from app.middleware import token_required
from datetime import datetime
import traceback
########

def FormatStringDate(date):
    #print(date, file=sys.stderr)
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

def FormatDate(date):
    #print(date, file=sys.stderr)
    if date is not None:
        result = date.strftime('%d-%m-%Y')
    else:
        #result = datetime(2000, 1, 1)
        result = datetime(1, 1, 2000)

    return result

def InsertData(obj):
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

def UpdateData(obj):
    #add data to db
    try:
        #obj.modification_date= datetime.now(tz)
        db.session.merge(obj)
        db.session.commit()
        #print(obj.site_name, file=sys.stderr)
    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong {e}", file=sys.stderr)
    
    return True

@app.route('/addIgwLinks', methods=['POST'])
@token_required
def AddIgwLink(user_data):
    try:
        linkObj = request.get_json()
        
        for obj in linkObj:
            try:
                if obj:
                    igwLink = IGW_LINKS()
                    if 'service_type' in obj:
                        igwLink.service_type = obj['service_type']

                    if 'provider' in obj:
                        igwLink.provider = obj['provider']

                    if 'router' in obj:
                        igwLink.router = obj['router']

                    if 'interface' in obj:
                        igwLink.interface = obj['interface']

                    if 'local_ipv4' in obj:
                        igwLink.local_ipv4 = obj['local_ipv4']

                    if 'neighbor_ipv4' in obj:
                        igwLink.neighbor_ipv4 = obj['neighbor_ipv4']

                    if 'local_ipv6' in obj:
                        igwLink.local_ipv6 = obj['local_ipv6']

                    if 'neighbor_ipv6' in obj:
                        igwLink.neighbor_ipv6 = obj['neighbor_ipv6']

                    if 'neighbor_asn' in obj:
                        igwLink.neighbor_asn = obj['neighbor_asn']

                    if 'ipv4_egress_policy' in obj:
                        igwLink.ipv4_egress_policy = obj['ipv4_egress_policy']

                    if 'community' in obj:
                        igwLink.community = obj['community']

                    if 'ipv4_ingress_policy' in obj:
                        igwLink.ipv4_ingress_policy = obj['ipv4_ingress_policy']

                    if 'ipv4_local_preference' in obj:
                        igwLink.ipv4_local_preference = obj['ipv4_local_preference']

                    if 'ipv6_egress_policy' in obj:
                        igwLink.ipv6_egress_policy = obj['ipv6_egress_policy']

                    if 'ipv6_ingress_policy' in obj:
                        igwLink.ipv6_ingress_policy = obj['ipv6_ingress_policy']

                    if 'ipv6_local_preference' in obj:
                        igwLink.ipv6_local_preference = obj['ipv6_local_preference']

                    if 'ipv4_advertised_routes_count' in obj:
                        igwLink.ipv4_advertised_routes_count = obj['ipv4_advertised_routes_count']
                    
                    if 'ipv4_received_routes_count' in obj:
                        igwLink.ipv4_received_routes_count = obj['ipv4_received_routes_count']

                    if 'ipv6_advertised_routes_count' in obj:
                        igwLink.ipv6_advertised_routes_count = obj['ipv6_advertised_routes_count']

                    if 'ipv6_received_routes_count' in obj:
                        igwLink.ipv6_received_routes_count = obj['ipv6_received_routes_count']

                    igwLink.created_by= user_data['user_id']
                    igwLink.modified_by= user_data['user_id']
                    InsertData(igwLink)
                    print("Data Inserted Into DB", file=sys.stderr)
        

            except Exception as e:
                traceback.print_exc()
                print(f"Error Adding Data: {e}", file=sys.stderr)
        return jsonify({'Response': f"Link Successfully Inserted"}),200
    except Exception as e:
        traceback.print_exc()
        return jsonify({f"Response": f"Failed to Insert {e}"}),500

@app.route('/addIgwLink', methods=['POST'])
@token_required
def UpdateIgwLink(user_data):
    try:
        linkObj = request.get_json()
        objs = IGW_LINKS.query.with_entities(IGW_LINKS).filter_by(igw_links_id= linkObj['igw_links_id']).first()

        if objs:

            if 'service_type' in linkObj:
                objs.service_type = linkObj['service_type']

            if 'provider' in linkObj:
                objs.provider = linkObj['provider']

            if 'router' in linkObj:
                objs.router = linkObj['router']

            if 'interface' in linkObj:
                objs.interface = linkObj['interface']

            if 'local_ipv4' in linkObj:
                objs.local_ipv4 = linkObj['local_ipv4']

            if 'neighbor_ipv4' in linkObj:
                objs.neighbor_ipv4 = linkObj['neighbor_ipv4']

            if 'local_ipv6' in linkObj:
                objs.local_ipv6 = linkObj['local_ipv6']

            if 'neighbor_ipv6' in linkObj:
                objs.neighbor_ipv6 = linkObj['neighbor_ipv6']

            if 'neighbor_asn' in linkObj:
                objs.neighbor_asn = linkObj['neighbor_asn']

            if 'ipv4_egress_policy' in linkObj:
                objs.ipv4_egress_policy = linkObj['ipv4_egress_policy']

            if 'community' in linkObj:
                objs.community = linkObj['community']

            if 'ipv4_ingress_policy' in linkObj:
                objs.ipv4_ingress_policy = linkObj['ipv4_ingress_policy']

            if 'ipv4_local_preference' in linkObj:
                objs.ipv4_local_preference = linkObj['ipv4_local_preference']

            if 'ipv6_egress_policy' in linkObj:
                objs.ipv6_egress_policy = linkObj['ipv6_egress_policy']

            if 'ipv6_ingress_policy' in linkObj:
                objs.ipv6_ingress_policy = linkObj['ipv6_ingress_policy']

            if 'ipv6_local_preference' in linkObj:
                objs.ipv6_local_preference = linkObj['ipv6_local_preference']

            if 'ipv4_advertised_routes_count' in linkObj:
                objs.ipv4_advertised_routes_count = linkObj['ipv4_advertised_routes_count']
            
            if 'ipv4_received_routes_count' in linkObj:
                objs.ipv4_received_routes_count = linkObj['ipv4_received_routes_count']

            if 'ipv6_advertised_routes_count' in linkObj:
                objs.ipv6_advertised_routes_count = linkObj['ipv6_advertised_routes_count']

            if 'ipv6_received_routes_count' in linkObj:
                objs.ipv6_received_routes_count = linkObj['ipv6_received_routes_count']

            objs.modified_by= user_data['user_id']

            #INSERT TO DB

            db.session.flush()

            db.session.merge(objs)
            db.session.commit()
            print(f"Data Updated For Link: {linkObj['igw_links_id']}", file=sys.stderr)
            return jsonify({'response': "success","code":"200"})
            
        else:
            print("NO MATCH", file = sys.stderr)
            return "Link Not Found", 404
    except Exception as e:
        print(f"Something else went wrong during Database Update {e.args}", file=sys.stderr)
        return str(e),500

@app.route('/getAllIgwLinks', methods=['GET'])
@token_required
def GetIgwLink(user_data):
    try:
        objList = []
        linkObj = IGW_LINKS.query.all()
        for obj in linkObj:
            objDict = {}
            objDict['igw_links_id'] = obj.igw_links_id
            objDict['service_type'] = obj.service_type
            objDict['provider'] = obj.provider
            objDict['router'] = obj.router
            objDict['interface'] = obj.interface
            objDict['local_ipv4'] = obj.local_ipv4
            objDict['neighbor_ipv4'] = obj.neighbor_ipv4
            objDict['local_ipv6'] = obj.local_ipv6
            objDict['neighbor_ipv6'] = obj.neighbor_ipv6
            objDict['neighbor_asn'] = obj.neighbor_asn
            objDict['ipv4_egress_policy'] = obj.ipv4_egress_policy
            objDict['community'] = obj.community
            objDict['ipv4_ingress_policy'] = obj.ipv4_ingress_policy
            objDict['ipv4_local_preference'] = obj.ipv4_local_preference
            objDict['ipv6_egress_policy'] = obj.ipv6_egress_policy
            objDict['ipv6_ingress_policy'] = obj.ipv6_ingress_policy
            objDict['ipv6_local_preference'] = obj.ipv6_local_preference
            objDict['ipv4_advertised_routes_count'] = obj.ipv4_advertised_routes_count
            objDict['ipv4_received_routes_count'] = obj.ipv4_received_routes_count
            objDict['ipv6_advertised_routes_count'] = obj.ipv6_advertised_routes_count
            objDict['ipv6_received_routes_count'] = obj.ipv6_received_routes_count
            if user_data['user_role'] == 'Admin':
                objDict['created_by'] = obj.created_by
                objDict['modified_by'] = obj.modified_by
            objDict['creation_date'] = FormatDate(obj.creation_date)
            objDict['modification_date'] = FormatDate(obj.modification_date)

            objList.append(objDict)

        return jsonify(objList),200

    except Exception as e:
        return str(e),500

@app.route('/deleteIgwLinks', methods=['POST'])
@token_required
def RemoveIgwLink(user_data):
    
    try:
        ids = request.get_json()
        for id in ids['ips']:
            IGW_LINKS.query.filter_by(igw_links_id= id).delete()

        db.session.commit()

        return jsonify({'response': "success", "code": "200"})
        
    except Exception as e:
        db.session.rollback()
        print(f"Something else went wrong during Database Delete {e}", file=sys.stderr)
        return str(e),500

