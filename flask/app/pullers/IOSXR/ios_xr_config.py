from netmiko import Netmiko
from datetime import datetime
import re, json, sys, time
import difflib
import xmltodict
from collections import OrderedDict

class XRConfigPuller(object):
    
    def __init__(self):
        self.inv_data = {}
    
    def connect(self,host):
        print(f"Connecting to {host['host']}")
        login_tries = 3
        c = 0
        is_login = False
        while c < login_tries :
            try:
                device = Netmiko(host=host['host'], username=host['user'], password=host['pwd'], device_type='cisco_xr',global_delay_factor=2, timeout=600)
                print(f"Success: logged in {host['host']}")
                is_login = True
                break
            except Exception as e:
                c +=1
                print(f"Falied to login {host['host']}")
                file_name = time.strftime("%d-%m-%Y")
                
                try:
                    #file = open(r'D:/test-repo/flask/app/failed/ims/'+file_name+'.txt','a',encoding='utf-8')
                    file = open(r'app/failed/ims/'+file_name+'.txt','a',encoding='utf-8')
                    file.write(host['host']+'\t')
                    
                    file.write(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
                    file.write('\t')
                    file.write(e)
                    file.write('\n')
                    file.close()
                except Exception as e:
                    print(e)
                    print('Error! ',file_name,' file cannot be created.')

        return device, is_login
            
    def get_config_commit_list(self, hosts):
        for host in hosts:
            device, is_login = self.connect(host)
                    
            if is_login==False:
                self.inv_data[host['host']] = {"error":"Login Failed"}
                file_name = time.strftime("%d-%m-%Y")+".txt"
                failed_device=[]
                #Read existing file
                        
                try:
                    with open('app/failed/ims/'+file_name,'r',encoding='utf-8') as fd:
                        failed_device= json.load(fd)
                except:
                    pass
                #Update failed devices list
                        
                failed_device.append({"ip_address": host['host'],"date":  time.strftime("%d-%m-%Y"), "time": time.strftime("%H-%M-%S"), "reason":"Failed to login to deice"})
                try:
                    with open('app/failed/ims/'+file_name, 'w', encoding='utf-8') as fd:
                        fd.write(json.dumps(failed_device))
                except Exception as e:
                    print(e)
                    print("Failed to update failed devices list:"+str(e), file=sys.stderr)
                continue
            try:
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                print("getting configuration commit list")
                config_list = device.send_command("show configuration commit list", use_textfsm=True)
                self.inv_data[host['host']].update({'configration': config_list})
                self.inv_data[host['host']].update({'status': 'success'})
            except:
                print("configuration commit list not found")
                self.inv_data[host['host']].update({'configration': []})
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})    
    
        if is_login: device.disconnect()

        return self.inv_data

    def get_last_n_config(self, host, commit_range):
        device, is_login = self.connect(host)
        if is_login==False:
            self.inv_data[host['host']] = {"error":"Login Failed"}
            return self.inv_data
        try:
            if host['host'] not in self.inv_data:
                self.inv_data[host['host']] = {}
            print(f"getting configuration chnages upto {commit_range}")
            config_list = device.send_command("show configuration commit changes last "+str(commit_range))
            self.inv_data[host['host']].update({'configration': config_list})
            self.inv_data[host['host']].update({'status': 'success'})
        except:
            print("configuration chnages not found")
            self.inv_data[host['host']].update({'configration': []})
            if host['host'] in self.inv_data:
                self.inv_data[host['host']].update({'status': 'error'})    
    
        if is_login: device.disconnect()

        return self.inv_data
    
    def get_config_by_commitID(self, host, commitid):
        device, is_login = self.connect(host)
        if is_login==False:
            self.inv_data[host['host']] = {"error":"Login Failed"}
            return self.inv_data
        try:
            if host['host'] not in self.inv_data:
                self.inv_data[host['host']] = {}
            print("getting configuration commit changes by commit id")
            config_list = device.send_command("show configuration commit changes "+str(commitid))
            self.inv_data[host['host']].update({'configration': config_list})
            self.inv_data[host['host']].update({'status': 'success'})
        except:
            print("configuration commit changes by commit id not found")
            self.inv_data[host['host']].update({'configration': []})
            if host['host'] in self.inv_data:
                self.inv_data[host['host']].update({'status': 'error'})    
    
        if is_login: device.disconnect()

        return self.inv_data

    def get_config_rollback_last_n(self, host, commit_range):
        device, is_login = self.connect(host)
        if is_login==False:
            self.inv_data[host['host']] = {"error":"Login Failed"}
            return self.inv_data
        try:
            if host['host'] not in self.inv_data:
                self.inv_data[host['host']] = {}
            print(f"starting rollback configration upto {commit_range}")
            config_list = device.send_command("show configuration rollback changes last "+str(commit_range))
            self.inv_data[host['host']].update({'configration': config_list})
            self.inv_data[host['host']].update({'status': 'success'})
        except:
            print("error while rollback configuration")
            self.inv_data[host['host']].update({'configration': []})
            if host['host'] in self.inv_data:
                self.inv_data[host['host']].update({'status': 'error'})    
    
        if is_login: device.disconnect()

        return self.inv_data

    def do_config_rollback_last_n(self, host, commit_range):
        device, is_login = self.connect(host)
        if is_login==False:
            self.inv_data[host['host']] = {"error":"Login Failed"}
            return self.inv_data
        try:
            if host['host'] not in self.inv_data:
                self.inv_data[host['host']] = {}
            print(f"starting rollback configration upto {commit_range}")
            config_list = device.send_command("rollback configuration last "+str(commit_range))
            self.inv_data[host['host']].update({'configration': config_list})
            self.inv_data[host['host']].update({'status': 'success'})
        except:
            print("error while rollback configuration")
            self.inv_data[host['host']].update({'configration': []})
            if host['host'] in self.inv_data:
                self.inv_data[host['host']].update({'status': 'error'})    
    
        if is_login: device.disconnect()

        return self.inv_data

    def get_config_rollback_by_commitID(self, host, commitid):
        device, is_login = self.connect(host)
        if is_login==False:
            self.inv_data[host['host']] = {"error":"Login Failed"}
            return self.inv_data
        try:
            if host['host'] not in self.inv_data:
                self.inv_data[host['host']] = {}
            print(f"starting rollback configration by commit id={commitid}")
            config_list = device.send_command("show configuration rollback changes "+str(commitid))
            self.inv_data[host['host']].update({'configration': config_list})
            self.inv_data[host['host']].update({'status': 'success'})
        except:
            print("error while rollback configration by commit id")
            self.inv_data[host['host']].update({'configration': []})
            if host['host'] in self.inv_data:
                self.inv_data[host['host']].update({'status': 'error'})    
    
        if is_login: device.disconnect()

        return self.inv_data

    def do_config_rollback_by_commitID(self, host, commitid):
        device, is_login = self.connect(host)
        if is_login==False:
            self.inv_data[host['host']] = {"error":"Login Failed"}
            return self.inv_data
        try:
            if host['host'] not in self.inv_data:
                self.inv_data[host['host']] = {}
            print(f"starting rollback configration by commit id={commitid}")
            config_list = device.send_command("rollback configuration "+str(commitid))
            self.inv_data[host['host']].update({'configration': config_list})
            self.inv_data[host['host']].update({'status': 'success'})
        except:
            print("error while rollback configration by commit id")
            self.inv_data[host['host']].update({'configration': []})
            if host['host'] in self.inv_data:
                self.inv_data[host['host']].update({'status': 'error'})    
    
        if is_login: device.disconnect()

        return self.inv_data 

    def config_backup(self, hosts):
        for host in hosts:
            device, is_login = self.connect(host)
                    
            if is_login==False:
                self.inv_data[host['host']] = {"error":"Login Failed"}
                continue
            try:
                if host['host'] not in self.inv_data:
                    self.inv_data[host['host']] = {}
                print("getting configuration backup")
                set_terminal_0 = device.send_command("terminal length 0")
                get_backup = device.send_command("show running-config | xml")
                now = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
                strip = re.findall(r'(.*\nBuilding configuration...\n)',get_backup)
                get_backup = get_backup.replace(strip[0],'')
                file_path = host['host']+'_'+str(now)+'.xml'
                with open(file_path,'w') as c_backup:
                    c_backup.write(get_backup)
                with open(file_path, 'r') as b_file:
                    json_backup= b_file.read()
                xml_json = xmltodict.parse(json_backup)
                xml_json = self.recursive_ordered_dict_to_dict(xml_json)
                while True:
                    option = input("Please select option to see configration..\n1 for all\n2 for interface\n3 for bgp\n 4 exit\n")
                    if option=='1':
                        print(xml_json)
                    elif option=='2':
                        print(xml_json['data']['interface-configurations'])
                    elif  option=='3':
                        print(xml_json['data']['bgp'])
                    elif option=='4':
                        break
                        
                print(f"configration backup of host {host['host']} has been done successfully...")
                self.inv_data[host['host']].update({'status': 'success'})
            except:
                print("error while getting configration backup")
                self.inv_data[host['host']].update({'configration': []})
                if host['host'] in self.inv_data:
                    self.inv_data[host['host']].update({'status': 'error'})    
    
        if is_login: device.disconnect()

        return self.inv_data

    def compare_config_file(self, input_file1, input_file2):
        # Open File in Read Mode
        file_1 = open(input_file1, 'r')
        file_2 = open(input_file2, 'r')
        
        print("Comparing files ", " @ " + input_file1, " # " + input_file2, sep='\n')
        
        file_1_line = file_1.readline()
        file_2_line = file_2.readline()
        
        # Use as a COunter
        line_no = 1
        
        print()
        
        with open(input_file1) as file1:
            with open(input_file2) as file2:
                same = set(file1).intersection(file2)
        
        print("Common Lines in Both Files")
        
        for line in same:
            print(line, end='')
        
        print('\n')
        print("Difference Lines in Both Files")
        while file_1_line != '' or file_2_line != '':
        
            # Removing whitespaces
            file_1_line = file_1_line.rstrip()
            file_2_line = file_2_line.rstrip()
        
            # Compare the lines from both file
            if file_1_line != file_2_line:
                
                # otherwise output the line on file1 and use @ sign
                if file_1_line == '':
                    print("@", "Line-%d" % line_no, file_1_line)
                else:
                    print("@-", "Line-%d" % line_no, file_1_line)
                    
                # otherwise output the line on file2 and use # sign
                if file_2_line == '':
                    print("#", "Line-%d" % line_no, file_2_line)
                else:
                    print("#+", "Line-%d" % line_no, file_2_line)
        
                # Print a empty line
                print()
        
            # Read the next line from the file
            file_1_line = file_1.readline()
            file_2_line = file_2.readline()
        
            line_no += 1
  
        file_1.close()
        file_2.close()

    def recursive_ordered_dict_to_dict(self, ordered_dict):
        simple_dict = {}

        for key, value in ordered_dict.items():
            if isinstance(value, OrderedDict):
                simple_dict[key] = self.recursive_ordered_dict_to_dict(value)
            elif isinstance(value, list):
                new_value = []
                for x in value:
                        if isinstance(x, OrderedDict):
                            item = self.recursive_ordered_dict_to_dict(x)
                            new_value.append(item)
                simple_dict[key] = new_value
            else:
                simple_dict[key] = value

        return simple_dict

if __name__ == '__main__':
    hosts = [{"host": "sandbox-iosxr-1.cisco.com","user": "admin","pwd": "C1sco12345"}]
    print('Started at: '+datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
    puller = XRConfigPuller()
    import pdb;pdb.set_trace()
    puller.config_backup(hosts)
    # puller.compare_config_file('sandbox-iosxr-1.cisco.com_2021-10-28T15-03-21.xml', 'sandbox-iosxr-1.cisco.com_2021-10-28T15-03-59.xml')
    # puller.get_config_rollback_by_commitID(hosts, '1000000116')
    
    # puller.get_config_commit_list(hosts)
    # puller.get_config_by_commitID(hosts, '1000000114')
    # puller.get_last_n_config(hosts, 2)
    # puller.get_config_rollback_last_n(hosts, 2)
    # puller.do_config_rollback_by_commitID(hosts, '1000000116')
    # puller.do_config_rollback_last_n(hosts, 4)
    # print(json.dumps(puller.get_config_by_commitID(hosts, 1000027003)))



    #compare two configration using config files=>use python diff library
    #and show difference of configration