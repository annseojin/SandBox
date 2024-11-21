import os
import logging
import shutil
import hashlib
logger = logging.getLogger(__name__)

class key:
    def __init__(self, userHome) -> None:
        self.userHome = userHome

    def api_key(self):
        """Print REST API Key."""
        if os.environ.get('MOBSF_API_KEY'):
            logger.info('\nAPI Key read from environment variable')
            return os.environ['MOBSF_API_KEY']
    
        secretFile = os.path.join(self.userHome, '.MobSF', 'secret')
        if self.is_file_exists(secretFile):
            try:
                apiKey = open(secretFile).read().strip()
                return self.gen_sha256_hash(apiKey)
            except Exception:
                logger.exception('Cannot Read API Key')
    
    def is_file_exists(self, filePath):
        if os.path.isfile(filePath):
            return True
        # This fix situation where a user just typed "adb" or another executable
        # inside settings.py/config.py
        if shutil.which(filePath):
            return True
        else:
            return False
    
    def gen_sha256_hash(self,msg):
        """Generate SHA 256 Hash of the message."""
        if isinstance(msg, str):
            msg = msg.encode('utf-8')
        hashObject = hashlib.sha256(msg)
        return hashObject.hexdigest()

