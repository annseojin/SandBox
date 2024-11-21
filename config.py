import os

USER_HOME = os.path.expanduser("~")

DEVICE = 'android'
EMULATOR_NAME = 'Pixel_5_API_25'
EMULATOR_PATH = os.path.join(USER_HOME, r'AppData\Local\Android\Sdk\emulator\emulator.exe')
MOBSF_NAME = 'Mobile-Security-Framework-MobSF-master'

SERVER = 'http://127.0.0.1:8000'

AES_KEY = b'dbcdcfghijklmaop'
APK_PATH = os.path.join(os.getcwd(), '..', 'sample.apk')

FRIDA_PATH = 'frida_script.js'