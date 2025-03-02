# In a file named cookie_crypto.py

from cryptography.fernet import Fernet
import json
import base64

class CookieEncryptor:
    def __init__(self, secret_key=None):
        """Initialize with a secret key or generate one"""
        if secret_key is None:
            # Generate a new key if none is provided
            self.secret_key = Fernet.generate_key()
        else:
            # Ensure the key is in the correct format for Fernet
            if isinstance(secret_key, str):
                key_bytes = secret_key.encode()
                # Make sure it's the right length and base64 URL-safe encoded
                if len(key_bytes) != 44 or not all(c in b'-_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789=' for c in key_bytes):
                    key_bytes = base64.urlsafe_b64encode(key_bytes.ljust(32)[:32])
                self.secret_key = key_bytes
            else:
                self.secret_key = secret_key
                
        self.cipher = Fernet(self.secret_key)
    
    def encrypt(self, data):
        """Encrypt data (dict) to a string suitable for cookies"""
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary")
            
        json_data = json.dumps(data).encode()
        encrypted = self.cipher.encrypt(json_data)
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_str):
        """Decrypt a cookie string back to a dictionary"""
        if not encrypted_str:
            return {}
            
        try:
            decoded = base64.b64decode(encrypted_str)
            decrypted_bytes = self.cipher.decrypt(decoded)
            return json.loads(decrypted_bytes.decode())
        except Exception as e:
            # Return empty dict on decryption failure
            return {}






