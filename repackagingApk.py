import os
import shutil
from zipfile import ZipFile
import glob
import platform
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
from colors import *
import subprocess

class Packaging:
    def __init__(self, key, file_name) -> None:
        self.key = key
        self.output_apk = file_name

    def find_sdk_directory(self) -> str:
        print(f'{GREEN}[*]{RESET} Finding Android SDK Directory')
        for root, dirs, files in os.walk('/Users'):
            if 'Android' in root.split(os.sep) and any(dir.lower() == 'sdk' for dir in dirs):
                sdkDir = os.path.join(root, next(dir for dir in dirs if dir.lower() == 'sdk'))
                buildToolsPath = os.path.join(sdkDir, 'build-tools')
                if os.path.exists(buildToolsPath):
                    subDirs = os.listdir(buildToolsPath)
                    if subDirs:
                        print(f'{BLUE}[+]{RESET} Successfully find the Android SDK Directory')
                        return os.path.join(buildToolsPath, subDirs[0])
        print(f"{RED}[-]{RESET} Couldn't find Android SDK Directory")
        return None

    def make_folder(self, name:str) -> str:
        path = os.path.join(os.getcwd(), name)
        if not os.path.exists(path):
            print(f'{GREEN}[*]{RESET} Creating directory: {path}')
            os.mkdir(path)
        else:
            print(f'{YELLOW}[!]{RESET} Directory already exists: {path}')
        return path

    def delete_folder(self, rootPath:str):
        print(f'{BLUE}[+]{RESET} Delete {rootPath}')
        shutil.rmtree(rootPath)

    def copy_file(self, source:str, destination:str):
        try:
            shutil.copy2(source, destination)
            print(f'{BLUE}[+]{RESET} Successfully copied from {source} to {destination}')
        except FileNotFoundError:
            print(f'{RED}[-]{RESET} No such file or directory {source}')

    def change_extension_to_zip(self, originalPath:str):
        for apk in glob.glob(f'{originalPath}/*.apk'):
            if not os.path.isdir(apk):
                print(f'{GREEN}[*]{RESET} Changing extension of {apk} to zip')
                zipName = f'{os.path.splitext(apk)[0]}.zip'
                os.rename(apk, zipName)

    def change_extension_to_apk(self, originalPath:str):
        for zip in glob.glob(f'{originalPath}/*.zip'):
            if not os.path.isdir(zip):
                print(f'{GREEN}[*]{RESET} Changing extension of {zip} to apk')
                apkName = f'{os.path.splitext(zip)[0]}.apk'
                os.rename(zip, apkName)

    def list_zip_files(self, originalPath:str):
        return [file for file in os.listdir(originalPath) if file.endswith('.zip')]

    def extract_dex(self, originalPath:str, dexPath:str):
        print(f'{GREEN}[*]{RESET} Extracting dex file')
        for zipFile in self.list_zip_files(originalPath):
            with ZipFile(os.path.join(originalPath, zipFile), 'r') as zipObj:
                for fileName in zipObj.namelist():
                    if fileName.endswith('.dex'):
                        zipObj.extract(fileName, dexPath)

    def aes_128_ecb_decode(self, fileName:str, fileData:bytes):
        cipher = AES.new(self.key, AES.MODE_ECB)
        try:
            decryptedData = unpad(cipher.decrypt(fileData), AES.block_size)
            with open(os.path.join(os.getcwd(), fileName),'wb') as file:
                file.write(decryptedData)
            print(f'{BLUE}[+]{RESET} Decode complete: {fileName}')
        except ValueError:
            print(f'{RED}[-]{RESET} Decryption or padding error: {fileName}')

    def file_signature(self, path:str):
        decompiledFiles = []
        print(f'{GREEN}[*]{RESET} Checking file signatures')
        for fileName in os.listdir(path):
            with open(os.path.join(path, fileName), 'rb') as file:
                fileHeader = file.read(3)
                file.seek(0)
                fileData = file.read()
                if fileHeader == b'dex':
                    print(f'{BLUE}[*]{RESET} {fileName} is a .dex file')
                else:
                    print(f'{RED}[*]{RESET} {fileName} is not a .dex file')
                    decompiledFiles.append(fileName)
                    self.aes_128_ecb_decode(fileName, fileData)
        return decompiledFiles

    def decompile_apk(self, apkPath:str, outputDir:str):
        print(f'{GREEN}[*]{RESET} Decompiling APK: {apkPath}')
        if platform.system() == 'Windows':
            subprocess.run(['cmd', '/c', 'echo.', '|', 'apktool.bat', 'd', apkPath, '-o', outputDir], shell=True)
        else:
            subprocess.run(['apktool', 'd', apkPath, '-o', outputDir])

    def recompile_apk(self, repackagingPath:str, apkName:str):
        print(f'{GREEN}[*]{RESET} Recompiling APK: {apkName}')
        if platform.system() == 'Windows':
            subprocess.run(['cmd', '/c', 'echo.', '|', 'apktool.bat', 'b', repackagingPath, '-o', f'repackaged_{apkName}'], shell=True)
        else:
            subprocess.run(['apktool', 'b', repackagingPath, '-o', f'repackaged_{apkName}'])

    def create_keystore(self, keystore:str, alias:str, storepass:str, keypass:str, dname:str):
        command = [
            'keytool', '-genkey', '-v', '-keystore', keystore,
            '-alias', alias, '-keyalg', 'RSA', '-keysize', '2048',
            '-validity', '10000', '-storepass', storepass, '-keypass', keypass, '-dname', dname
        ]
        print(f'{GREEN}[*]{RESET} Creating keystore: {keystore}')
        subprocess.run(command, check=True)

    def sign_apk(self, sdkPath:str, keystore:str, alias:str, storepass:str, keypass:str, inputApk:str, outputApk:str):
        apksigner = 'apksigner.bat' if platform.system() == 'Windows' else 'apksigner'
        command = [
            os.path.join(sdkPath, apksigner), 'sign', '--ks', keystore,
            '--ks-key-alias', alias, '--ks-pass', f'pass:{storepass}',
            '--key-pass', f'pass:{keypass}', '--out', outputApk, inputApk
        ]
        print(f'{GREEN}[*]{RESET} Signing APK: {inputApk}')
        subprocess.run(command, check=True)

    def verify_apk(self, sdkPath:str, apkPath:str):
        apksigner = 'apksigner.bat' if platform.system() == 'Windows' else 'apksigner'
        command = [os.path.join(sdkPath, apksigner), 'verify', apkPath]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print(f'{BLUE}[+]{RESET} APK is valid: {apkPath}')
        else:
            print(f'{RED}[-]{RESET} APK  is not valid: {apkPath}')

    def delete_smali_and_copy_dex(self, repackagingPath:str, decompiledFiles:list, dexFile:str):
        for file in decompiledFiles:
            smaliPath = os.path.join(repackagingPath, f"smali_{file.split('.')[0]}")
            if os.path.exists(smaliPath):
                print(f'{GREEN}[*]{RESET} Deleting smali directory: {smaliPath}')
                self.delete_folder(smaliPath)
            else:
                print(f'{RED}[-]{RESET} Not exist smali directory: {smaliPath}')
            self.copy_file(os.path.join(repackagingPath, '..', dexFile, file), repackagingPath+'/')
    
    def notice_apk_path(self, currentPath:str):
        for apk in glob.glob(f'{currentPath}/repackaged_*.apk'):
            print(f'{GREEN}[*]{RESET} Your apk => {YELLOW}{os.path.join(currentPath, apk)}{RESET}')
            

    def absolute_to_relative(self, absPath, currentPath):
        return os.path.relpath(absPath, currentPath)
    
    def get_apks(self, currentPath:str):
        apks = []
        for apk in glob.glob(f'{currentPath}/*.apk'):
            apks.append(os.path.join(currentPath, apk))
        return apks

    def process(self, path:str):
        currentPath = os.getcwd()
        apkPath = self.absolute_to_relative(path, currentPath)

        sdkPath = self.find_sdk_directory()
        tmpFolderPath = self.make_folder('tmp')
        
        os.chdir(tmpFolderPath)
        self.create_keystore(
            keystore='release-key.jks',
            alias='key-alias',
            storepass='password',
            keypass='password',
            dname='CN=., OU=., O=., ST=., C=.'
        )
        originalPath = self.make_folder('original')
        repackagingPath = os.path.join(tmpFolderPath, 'repackaging')
        
        self.copy_file(path, originalPath)
        self.change_extension_to_zip(originalPath)
        
        dexPath = os.path.join(tmpFolderPath, 'dex_files')
        self.extract_dex(originalPath, 'dex_files')
        self.change_extension_to_apk(originalPath)
        
        os.chdir(dexPath)
        decompiledFiles = self.file_signature(dexPath)

        os.chdir(tmpFolderPath)
        self.decompile_apk(os.path.join('original', os.path.basename(apkPath)), 'repackaging')
        
        
        originalAssetsPath = self.make_folder(os.path.join('original', 'assets'))
        repackAssetsPath = os.path.join(repackagingPath, 'assets')
        self.copy_file(os.path.join(repackAssetsPath, 'pgsHZz.apk'), originalAssetsPath)
        
        repackagingPath2 = os.path.join(tmpFolderPath, 'repackaging2')
        self.change_extension_to_zip(originalAssetsPath)
        
        assetsDexPath = os.path.join(tmpFolderPath, 'assets_dex_files')
        self.extract_dex(originalAssetsPath, 'assets_dex_files')
        self.change_extension_to_apk(originalAssetsPath)
        
        os.chdir(assetsDexPath)
        decompiledFiles2 = self.file_signature(assetsDexPath)
        
        os.chdir(tmpFolderPath)
        self.decompile_apk(os.path.join(originalAssetsPath, 'pgsHZz.apk'),'repackaging2')
        
        os.chdir(repackagingPath2)
        self.delete_smali_and_copy_dex(repackagingPath2,decompiledFiles2, 'assets_dex_files')

        os.chdir(repackAssetsPath)
        self.recompile_apk(repackagingPath2, 'pgsHZz.apk')
        os.remove(os.path.join(repackAssetsPath, 'pgsHZz.apk'))
        

        self.copy_file(os.path.join(repackAssetsPath, 'repackaged_pgsHZz.apk'), tmpFolderPath)
        os.chdir(tmpFolderPath)
        self.sign_apk(
            sdkPath=sdkPath,
            keystore='release-key.jks',
            alias='key-alias',
            storepass='password',
            keypass='password',
            inputApk='repackaged_pgsHZz.apk',
            outputApk='repackaged_pgsHZz.apk'
        )
        self.verify_apk(sdkPath=sdkPath,apkPath='repackaged_pgsHZz.apk')
        self.copy_file(os.path.join(tmpFolderPath, 'repackaged_pgsHZz.apk'), repackAssetsPath)
        
        os.chdir(repackagingPath)
        self.delete_smali_and_copy_dex(repackagingPath, decompiledFiles, 'dex_files')
        
        os.chdir(tmpFolderPath)
        self.recompile_apk('repackaging', self.output_apk)
        

        self.sign_apk(
            sdkPath=sdkPath,
            keystore='release-key.jks',
            alias='key-alias',
            storepass='password',
            keypass='password',
            inputApk='repackaged_'+self.output_apk,
            outputApk='repackaged_'+self.output_apk
        )
        
        self.verify_apk(sdkPath=sdkPath,apkPath='repackaged_'+self.output_apk)
        self.copy_file(os.path.join(tmpFolderPath, 'repackaged_'+self.output_apk),os.path.join(currentPath, '..'))
        self.copy_file(os.path.join(repackAssetsPath, 'repackaged_pgsHZz.apk'), os.path.join(currentPath, '..'))
        os.chdir(currentPath)
        self.delete_folder(tmpFolderPath)
        self.notice_apk_path(os.path.join(currentPath, '..'))
        return self.get_apks(os.path.join(currentPath, '..'))
        
