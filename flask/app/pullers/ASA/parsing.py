import re
import paramiko
import traceback
import time, os , datetime, sys
import textfsm, json

class Parse(object):
    def __init__(self):
        
        self.remote_conn = None
        
        
    def connect(self, ip, port, username, password, remote_conn_pre):
        try:
            time.sleep(3)
            remote_conn_pre.connect(ip, username=username, password=password,timeout=5,allow_agent=False,look_for_keys=False)
        except paramiko.AuthenticationException as e:
            raise e
        except Exception as e:
            print('Connect Failed on 1st try for ip: ' +ip+' Error:'+ str(e))
            print(e)
            time.sleep(2)
            try:
                remote_conn_pre.connect(ip, username=username, password=password,timeout=5,allow_agent=False,look_for_keys=False)
            except paramiko.AuthenticationException as e:
                raise e
            except Exception as e:
                print('Connect Failed on 2nd try for ip: ' +ip+' Error:'+ str(e))
                print(e)
                time.sleep(2)
                try:
                    remote_conn_pre.connect(ip, username=username, password=password,timeout=5,allow_agent=False,look_for_keys=False)
                except paramiko.AuthenticationException as e:
                    print('Connect Failed on 3rd try for ip: ' +ip+' Error:'+ str(e))
            
                    raise e
                except Exception as e:
                    print('Connect Failed on 3rd try for ip: ' +ip+' Error:'+ str(e))
                    file_name = time.strftime("%d-%m-%Y")+".txt"
                    failed_device=[]
                    #Read existing file
                    try:
                        with open('app/failed/ims/'+file_name,'r', encoding='utf-8') as fd:
                            failed_device= json.load(fd)
                    except:
                        print("Failed devices list is empty", file=sys.stderr)
                        pass
                    #Update failed devices list
                    
                    failed_device.append({"ip_address": ip, "date":  time.strftime("%d-%m-%Y"), "time": time.strftime("%H-%M-%S"), "reason":str(e)})
                    try:
                        with open('app/failed/ims/'+file_name, 'w', encoding='utf-8') as fd:
                            fd.write(json.dumps(failed_device))
                    except Exception as e:
                        print(e)
                        print("Failed to update failed devices list", file=sys.stderr)
            
                    raise e
                   
                    
    def connectShell(self, ip,username, password):
        remote_conn_pre = paramiko.SSHClient()
        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print('Now Connecting to: '+ip)    
        
        try:
            self.connect(ip, 22, username, password,remote_conn_pre)
        except Exception as e:
            print('SSH Exception for ip: '+ip)
            print(str(e))
            if str(e) == 'timed out' or '[Errno None] Unable to connect to port 22' in  str(e):
                raise e
                
        print('Connected to: '+ip, file=sys.stderr)  
        remote_conn = remote_conn_pre.invoke_shell()
        return remote_conn

    def getCommandOutputs(self, command_list,ip):
        try:
            respList = self.executeUsingShellWithConn(ip,self.remote_conn,command_list)
            return respList
        except Exception as e:
            print('Exception occured for ip: '+str(e))
            print(traceback.format_exc())
            raise e
    
    def executeUsingShellWithConn(self, ip,remote_conn,command_list):
        try:
            outputs = []
            
            for x in command_list:
                print('Sending command: '+x.get('command'), file=sys.stderr)
                remote_conn.send(x.get('command'))
                time.sleep(x.get('sleep'))
                output = remote_conn.recv(1048576)
                op = str(output,'utf-8')
                print(op)
                formattedOP = self.getFormattedResponse(ip,op)
                if x['template']:
                    if formattedOP !='':
                        cmd = x.get('command').replace('\n','')
                        cmd = cmd.strip()
                        outputs.append({'version':self.parse_output(formattedOP, x.get('template') , cmd)})
                while True:
                    print("serial not found try again")
                    if not 'Serial Number' in op:
                        remote_conn.send('\n\n\n')
                        time.sleep(x.get('sleep'))
                        output = remote_conn.recv(1048576)
                        op = str(output,'utf-8')
                        print(op)
                    else:
                        break
                formattedOP = self.getFormattedResponse(ip,op)
                # outputs.append(formattedOP)
                if x['template']:
                    if formattedOP !='':
                        cmd = x.get('command').replace('\n','')
                        cmd = cmd.strip()
                        outputs.append({'serial':self.parse_output(formattedOP, x.get('template') , cmd)})
                
            return outputs
            
        except Exception as e:
            
            print('Exception occured : '+str(e))
            raise e
        
    
    def parse_output(self, raw_text_data, template, command):
        print(f'command is {template}')
        try:
            template = open("app/pullers/ASA/"+template+".textfsm")
            # template = open(template+".textfsm")
            re_table = textfsm.TextFSM(template)
            fsm_results = re_table.ParseText(raw_text_data)
            print(f"{command} => {fsm_results}")
            return fsm_results
        except Exception as e:
            print(f"{command}  template not found", file=sys.stderr)
            return ''
        
       
    
    def getFormattedResponse(self, ip,resp):
        filename = self.getTempFileName(ip)
        f = open(filename, "w")
        f.write(resp)
        f.close()
        content = open(filename, encoding='utf-8').read()  
        os.remove(filename)
        return content
        # return self.removeBlanksLinesFromResp(content)

    def removeBlanksLinesFromResp(self, respList):
        newRespList = []
        for x in respList:
            if x != '\n':
                newRespList.append(x)

        return newRespList

    def generateFileName(self, ip,fileNamePrefix,now):
            filename = fileNamePrefix+ip +'-'+str(now.year)+'-'+str(now.month)+'-'+str(now.day)+'--'+str(now.hour)+'-'+str(now.minute)+'-'+str(now.second)+'.txt'
            return filename
        
        
    def getTempFileName(self ,ip):
        sourceDir = os.path.dirname(__file__)
        now = datetime.datetime.now()
        filename = os.path.join(sourceDir, self.generateFileName(ip,'temp',now))
        # print(filename)
        return filename
    
    
    def perform(self, ip, username, password, command_list):
        try:
            
            self.remote_conn = self.connectShell(ip, username, password)
            
            respList = self.getCommandOutputs(command_list,ip)
            print(respList)
            return respList
        except Exception as e:
            raise e
        finally:
            if self.remote_conn is not None:
                self.remote_conn.close()
                

if __name__=='__main__':
    puller = Parse()
    
    puller.perform('10.64.194.244','ciscoadmin','M0b1lyy@3Dn@790')