from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

class Privacy:
    def __init__(self):
        self.private_key = x25519.X25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

    def generate_shared_key(self, peer_public_key_bytes):
        peer_public_key = x25519.X25519PublicKey.from_public_bytes(peer_public_key_bytes)
        shared_key = self.private_key.exchange(peer_public_key)
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
        ).derive(shared_key)
        return derived_key

    def encrypt_data(self, data, key):
        iv = os.urandom(12)
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
        ).encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        return iv, ciphertext, encryptor.tag

    def decrypt_data(self, iv, ciphertext, tag, key):
        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
        ).decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()

    def set_privacy_level(self, level):
        self.privacy_level = level
        print(f"Privacy level set to {level} hops")

    def create_onion_routing_path(self, nodes):
        path = []
        current_data = b"Initial message"
        for node in nodes:
            node_key = os.urandom(32)
            iv, encrypted_data, tag = self.encrypt_data(current_data, node_key)
            path.append((iv, encrypted_data, tag, node_key))
            current_data = encrypted_data
        return path

    def decrypt_onion_layer(self, iv, encrypted_data, tag, key):
        return self.decrypt_data(iv, encrypted_data, tag, key)

    def process_onion_path(self, path):
        current_data = None
        for iv, encrypted_data, tag, key in reversed(path):
            current_data = self.decrypt_onion_layer(iv, encrypted_data, tag, key)
        return current_data

    def manage_keys(self, node_id, key=None):
        if key:
            self.key_store[node_id] = key
            print(f"Key stored for node {node_id}")
        else:
            return self.key_store.get(node_id, None)

    def enhanced_encryption(self, data, key):
        return self.encrypt_data(data, key)