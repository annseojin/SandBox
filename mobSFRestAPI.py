import requests
import os
import json
from datetime import datetime
from requests_toolbelt import MultipartEncoder
from colors import *

class Analysis:
    def __init__(self, server, filePath, apks, apiKey, device, fridaPath) -> None:
        self.server = server
        self.path = filePath
        self.apks = apks
        self.apiKey=apiKey
        self.scanHash=''
        self.device=device
        self.fridaPath = fridaPath
        
    def upload_apk(self, filePath):
        print(f'{GREEN}[*]{RESET} Uploading APK: {YELLOW}{os.path.basename(filePath)}{RESET}')
        multipartData = MultipartEncoder(
            fields = {'file':(filePath, open(filePath,'rb'),'application/octet-stream')}
        )
        headers = {
            'Content-Type':multipartData.content_type,
            'Authorization':self.apiKey
        }
        response = requests.post(f'{self.server}/api/v1/upload',data=multipartData, headers=headers)
        result = response.json()
        if 'hash' in result:
            self.scanHash = result['hash']
            print(f'{BLUE}[+]{RESET} Upload completed: {YELLOW}{os.path.basename(filePath)}{RESET}')
        else:
            print(f'{RED}[-]{RESET} Not upload completed')

    def scan_apk(self, filePath):
        print(f'{GREEN}[*]{RESET} Scanning Started: {YELLOW}{os.path.basename(filePath)}{RESET}')
        data = {
            'hash':self.scanHash,
            'scan_type':filePath.split('.')[-1],
            'file_name':os.path.basename(filePath)
            }
        headers = {
            'Authorization':self.apiKey
        }
        response = requests.post(f'{self.server}/api/v1/scan',data=data, headers=headers)
        if response.status_code == 200:
            print(f'{BLUE}[+]{RESET} Scanning completed')
        else:
            print(f'{RED}[-]{RESET} Not scanning completed')

    def static_json(self, filePath):
        print(f"{GREEN}[*]{RESET} Generating Static json: {YELLOW}{os.path.basename(filePath)}{RESET}")
        data = {
            "hash":self.scanHash
        }
        headers = {
            "Authorization":self.apiKey
        }
        response = requests.post(f"{self.server}/api/v1/report_json",data=data,headers=headers)
        date = datetime.now().strftime("%Y-%m-%d")
        with open(self.path+f'/static_report-{os.path.basename(filePath)}-{date}.json','w+') as f:
            json.dump(response.json(),f, indent=4)
        return response

    def download_pdf(self, filePath):
        print(f'{GREEN}[*]{RESET} Downloading the pdf: {filePath}')
        data = {
            'hash':self.scanHash,
        }
        headers = {
            'Authorization':self.apiKey
        }
        response = requests.post(f'{self.server}/api/v1/download_pdf',data=data,headers=headers)
        date = datetime.now().strftime("%Y-%m-%d")
        with open(self.path+f'/static_analysis_report-{os.path.basename(filePath)}-{date}.pdf','wb') as f:
            f.write(response.content)
        print(f'{BLUE}[+]{RESET} Download complete')
        print(f'{BLUE}[+]{RESET} Result of static analyze is at {YELLOW}{self.path+"/static_analysis_report.pdf"}{RESET}')

    def delete(self):
        print(f"{RED}[*]{RESET} Deleting")
        data = {
            "hash":self.scanHash
        }
        headers = {
            "Authorization":self.apiKey
        }
        response = requests.post(f"{self.server}/api/v1/delete_scan",data=data,headers=headers)
        return response

    def get_apps(self):
        print(f"{GREEN}[*]{RESET} Connecting to Emulator")
        headers = {
            'Authorization':self.apiKey
        }
        response = requests.get(f"{self.server}/api/v1/dynamic/get_apps",headers=headers)
        return response

    def start_dynamic_analysis(self):
        print(f"{GREEN}[*]{RESET} Starting Dynamic Analysis")
        data = {
            "hash":self.scanHash
        }
        headers = {
            "Authorization":self.apiKey
        }
        response = requests.post(f"{self.server}/api/v1/dynamic/start_analysis",data=data,headers=headers)
        return response

    def stop_dynamic_analysis(self):
        print(f"{RED}[*]{RESET} Stop Dynamic Analysis")
        data = {
            "hash":self.scanHash
        }
        headers = {
            "Authorization":self.apiKey
        }
        response = requests.post(f"{self.server}/api/v1/dynamic/stop_analysis",data=data,headers=headers)
        return response

    def dynamic_report_json(self):
        print(f"{GREEN}[*]{RESET} Making Dynamic json report")
        data = {
            "hash":self.scanHash
        }
        headers = {
            "Authorization":self.apiKey
        }
        response = requests.post(f"{self.server}/api/v1/dynamic/report_json",data=data,headers=headers)
        date = datetime.now().strftime("%Y-%m-%d")
        with open(self.path+f'/dynamic_report-{date}.json','w+') as f:
            json.dump(response.json(),f, indent=4)
        return response
    
    def dynamic_act_tester(self, test):
        print(f"{GREEN}[*]{RESET} Dynamic Act Tester {test}")
        data = {
            "hash":self.scanHash,
            "test":test
        }
        headers = {
            "Authorization":self.apiKey
        }
        response = requests.post(f"{self.server}/api/v1/android/activity",data=data,headers=headers)
        return response
    
    def dynamic_start_activity(self,activity):
        print(f"{BLUE}[*]{RESET} Dynamic Start Activiry")
        data = {
            "hash":self.scanHash,
            "activity":activity
        }
        headers = {
            "Authorization":self.apiKey
        }
        response = requests.post(f"{self.server}/api/v1/android/start_activity",data=data,headers=headers)
        return response
    
    def dynamic_tls_test(self):
        print(f"{GREEN}[*]{RESET} Dynamic TLS Test")
        data = {
            "hash":self.scanHash
        }
        headers = {
            "Authorization":self.apiKey
        }
        response = requests.post(f"{self.server}/api/v1/android/tls_tests",data=data,headers=headers)
        return response
    
    def frida_instrument(self,default_hooks='',auxiliary_hooks='',frida_code='',class_name=None,class_search=None,class_trace=None):
        print(f"{GREEN}[*]{RESET} frida instrument")
        data = {
            'hash':self.scanHash,
            'default_hooks':default_hooks,
            'auxiliary_hooks':auxiliary_hooks,
            'frida_code':frida_code
        }
        if class_name:
            data['class_name']=class_name
        if class_search:
            data['class_search']=class_search
        if class_trace:
            data['class_trace']=class_trace
        headers = {
            'Authorization':self.apiKey
        }
        response = requests.post(f"{self.server}/api/v1/frida/instrument",data=data,headers=headers)
        return response
    
    def frida_monitor(self):
        print(f"{GREEN}[*]{RESET} frida api monitor")
        data = {
            'hash':self.scanHash
        }
        headers = {
            'Authorization':self.apiKey
        }
        response = requests.post(f"{self.server}/api/v1/frida/api_monitor",data=data,headers=headers)
        return response
    
    def frida_get_dependencies(self):
        print(f"{GREEN}[*]{RESET} frida get dependencies")
        data = {
            'hash':self.scanHash
        }
        headers = {
            'Authorization':self.apiKey
        }
        response = requests.post(f"{self.server}/api/v1/frida/get_dependencies",data=data,headers=headers)
        return response
    
    def frida_logs(self):
        print(f"{GREEN}[*]{RESET} frida logs")
        data = {
            'hash':self.scanHash
        }
        headers = {
            'Authorization':self.apiKey
        }
        response = requests.post(f"{self.server}/api/v1/frida/logs",data=data,headers=headers)
        return response
    
    def frida_list_script(self):
        data = {
            'device':self.device
        }
        headers = {
            'Authorization':self.apiKey
        }
        response = requests.post(f"{self.server}/api/v1/frida/list_script",data=data,headers=headers)
        return response
    
    def frida_get_script(self,scripts):
        data = {
            'scripts[]':scripts,
            'device':self.device
        }
        headers = {
            'Authorization':self.apiKey
        }
        response = requests.post(f"{self.server}/api/v1/frida/get_script",data=data,headers=headers)
        return response
    
    def get_frida_code(self):
        try:
            with open(self.fridaPath, 'r') as file:
                frida_code = file.read()
            return frida_code
        except Exception as e:
            print(f"Error reading the Frida script: {e}")
            return
    
    
    def Analysis(self):
        for apk in self.apks: # 정적 분석 리패키징 apk
            if 'repackaged_' in apk:
                self.upload_apk(apk)
                self.scan_apk(apk)
                self.static_json(apk)
                self.download_pdf(apk)

        self.apks = [apk for apk in self.apks if 'repackaged_' not in apk]
        
        for apk in self.apks: # 동적 분석 본 apk
            self.upload_apk(apk)
            self.scan_apk(apk)
            self.static_json(apk)
            self.get_apps()
            
            while True:
                if self.start_dynamic_analysis().status_code == 200:
                    break

            
            self.frida_instrument(True, frida_code=self.get_frida_code())
            #self.frida_get_dependencies()

            self.dynamic_act_tester("activity")
            self.dynamic_act_tester("exported")
            
            self.frida_monitor()

            self.frida_instrument(True, frida_code=self.get_frida_code())
            self.dynamic_tls_test()
            self.frida_logs()

            self.stop_dynamic_analysis()
            self.dynamic_report_json()
            self.download_pdf(apk)
            self.delete()