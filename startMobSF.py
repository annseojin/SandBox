import subprocess
import os
import platform
import psutil
from colors import *


class Starting:
    def __init__(self, mobsfName) -> None:
        self.process = None
        self.mobsfName = mobsfName

    def start_mobsf(self):
        print(f"{GREEN}[*]{RESET} Finding MobSF dir path")
        mobsfDirPath = os.path.join(os.getcwd(), self.mobsfName)
        runScript = ''    
        if platform.system()=='Windows':
            runScript='run.bat'
        elif platform.system()=='Darwin':
            runScript='run.sh'
        if not os.path.exists(os.path.join(mobsfDirPath, runScript)):
            print(f"{RED}[-]{RESET} Error: The {runScript} is not in this path {mobsfDirPath}")
            return
        self.process = subprocess.Popen(os.path.join(mobsfDirPath, runScript), shell=True, cwd=mobsfDirPath)
        print(f'{BLUE}[+]{RESET} MobSF Started Successfully')        
        return self.process

    def kill_mobsf(self):
        print(f'{RED}[*]{RESET} Terminating MobSF')
        if self.process and self.process.poll() is None:
            parent = psutil.Process(self.process.pid)
            for child in parent.children(recursive=True):
                child.terminate()
            self.process.terminate()
            self.process.wait()
        print(f"{RED}[*]{RESET} Byebye~")



