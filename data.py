import json
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hmac

class DataManager:
    def __init__(self, storage_path='data_storage'):
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        print(f"Data storage initialized at '{self.storage_path}'.")

    def _get_file_path(self, key):
        # Generate a file path for storing data based on a key
        return os.path.join(self.storage_path, f"{key}.json")

    def store_data(self, key, data, encrypt=False, password=None):
        # Store data in a file, optionally encrypting it
        file_path = self._get_file_path(key)
        if encrypt and password:
            data = self._encrypt_data(json.dumps(data), password)
        with open(file_path, 'w') as file:
            file.write(data)
        print(f"Data stored under key '{key}'.")

    def retrieve_data(self, key, decrypt=False, password=None):
        # Retrieve data from a file, optionally decrypting it
        file_path = self._get_file_path(key)
        if not os.path.exists(file_path):
            print(f"No data found for key '{key}'.")
            return None
        with open(file_path, 'r') as file:
            data = file.read()
        if decrypt and password:
            data = self._decrypt_data(data, password)
        return json.loads(data)

    def _encrypt_data(self, data, password):
        # Encrypt data using a password
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password.encode())
        iv = os.urandom(12)
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
        ).encryptor()
        ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
        return json.dumps({"salt": salt.hex(), "iv": iv.hex(), "data": ciphertext.hex(), "tag": encryptor.tag.hex()})

    def _decrypt_data(self, encrypted_data, password):
        # Decrypt data using a password
        encrypted_data = json.loads(encrypted_data)
        salt = bytes.fromhex(encrypted_data["salt"])
        iv = bytes.fromhex(encrypted_data["iv"])
        ciphertext = bytes.fromhex(encrypted_data["data"])
        tag = bytes.fromhex(encrypted_data["tag"])
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password.encode())
        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
        ).decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()

    def delete_data(self, key):
        # Delete data associated with a key
        file_path = self._get_file_path(key)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Data under key '{key}' deleted.")
        else:
            print(f"No data found for key '{key}' to delete.")

    def list_data_keys(self):
        # List all data keys stored
        return [f.split('.')[0] for f in os.listdir(self.storage_path) if f.endswith('.json')]

    def verify_data_integrity(self, data, key):
        # Verify data integrity using HMAC
        h = hmac.HMAC(key, hashes.SHA256())
        h.update(data.encode())
        return h.finalize()