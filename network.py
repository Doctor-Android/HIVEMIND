import socket
import threading
import ssl
import os
import json
import random
from OpenSSL import crypto
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from PyQt5 import QtWidgets, QtCore

class DHTNode:
    def __init__(self, node_id, address):
        self.node_id = node_id
        self.address = address
        self.peers = {}

    def add_peer(self, node_id, address):
        self.peers[node_id] = address

    def join_network(self, bootstrap_node):
        try:
            with socket.create_connection(bootstrap_node) as s:
                s.sendall(json.dumps({'action': 'join', 'node_id': self.node_id, 'address': self.address}).encode())
                response = s.recv(4096)
                self.peers.update(json.loads(response.decode()))
                print(f"Joined network, current peers: {self.peers}")
        except Exception as e:
            print(f"Error joining network: {e}")

class Node:
    def __init__(self, role='relay', port=9000, dht_node=None, use_ssl=True):
        self.role = role
        self.port = port
        self.dht_node = dht_node or DHTNode(node_id=random.randint(0, 1000), address=('localhost', port))
        self.use_ssl = use_ssl
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.blocked_websites = set()

        # Generate RSA key pair for asymmetric encryption
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

        # Automatically generate SSL certificate and key if they don't exist
        certfile = "server.crt"
        keyfile = "server.key"
        if not os.path.exists(certfile) or not os.path.exists(keyfile):
            self.generate_self_signed_cert(certfile, keyfile)

        if self.use_ssl:
            self.server_socket = ssl.wrap_socket(
                self.server_socket,
                server_side=True,
                certfile=certfile,
                keyfile=keyfile
            )

        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        print(f"{self.role} node listening on port {self.port}")

        # Start the node server
        self.start_node()

    def generate_self_signed_cert(self, certfile, keyfile):
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)

        cert = crypto.X509()
        cert.get_subject().C = "US"
        cert.get_subject().ST = "California"
        cert.get_subject().L = "San Francisco"
        cert.get_subject().O = "My Company"
        cert.get_subject().OU = "My Organization"
        cert.get_subject().CN = "localhost"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10*365*24*60*60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, 'sha256')

        with open(certfile, "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        with open(keyfile, "wb") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    def start_node(self):
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"Connected to {client_address}")
                if self.use_ssl:
                    client_socket = ssl.wrap_socket(client_socket, server_side=False)
                threading.Thread(target=self.handle_connection, args=(client_socket,)).start()
            except Exception as e:
                print(f"Error accepting connections: {e}")

    def handle_connection(self, client_socket):
        try:
            data = client_socket.recv(4096)
            if data:
                print(f"Received data: {data}")
                decrypted_data = self.decrypt_layer(data)
                print(f"Decrypted data: {decrypted_data}")
                if not self.is_blocked(decrypted_data):
                    self.forward_data(decrypted_data, client_socket)
                else:
                    print("Blocked website access attempt.")
        except Exception as e:
            print(f"Error handling connection: {e}")
        finally:
            client_socket.close()

    def encrypt_layer(self, data, public_key):
        encrypted_data = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_data

    def decrypt_layer(self, encrypted_data):
        decrypted_data = self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_data

    def forward_data(self, data, client_socket):
        path = self.select_path()
        for node_id, node_address in path:
            try:
                with socket.create_connection(node_address) as next_socket:
                    encrypted_data = self.encrypt_layer(data, self.dht_node.get_peer(node_id).public_key)
                    next_socket.sendall(encrypted_data)
            except Exception as e:
                print(f"Error forwarding data to {node_address}: {e}")

    def select_path(self):
        return random.sample(self.dht_node.peers.items(), 3)

    def is_blocked(self, data):
        # Check if the data contains a request to a blocked website
        for website in self.blocked_websites:
            if website in data.decode():
                return True
        return False

class NodeGUI(QtWidgets.QWidget):
    def __init__(self, node):
        super().__init__()
        self.node = node
        self.init_ui()
        self.monitoring_timer = QtCore.QTimer()
        self.monitoring_timer.timeout.connect(self.update_monitoring)

    def init_ui(self):
        self.setWindowTitle(f"{self.node.role.capitalize()} Node")
        self.setGeometry(100, 100, 500, 500)

        layout = QtWidgets.QVBoxLayout()

        self.status_label = QtWidgets.QLabel(f"Node running on port {self.node.port}")
        layout.addWidget(self.status_label)

        self.peers_label = QtWidgets.QLabel("Peers:")
        layout.addWidget(self.peers_label)

        self.peers_list = QtWidgets.QListWidget()
        layout.addWidget(self.peers_list)

        self.refresh_button = QtWidgets.QPushButton("Refresh Peers")
        self.refresh_button.clicked.connect(self.refresh_peers)
        layout.addWidget(self.refresh_button)

        self.traffic_label = QtWidgets.QLabel("Traffic:")
        layout.addWidget(self.traffic_label)

        self.traffic_list = QtWidgets.QListWidget()
        layout.addWidget(self.traffic_list)

        self.config_button = QtWidgets.QPushButton("Configure Node")
        self.config_button.clicked.connect(self.configure_node)
        layout.addWidget(self.config_button)

        self.monitor_button = QtWidgets.QPushButton("Start Monitoring")
        self.monitor_button.clicked.connect(self.start_monitoring)
        layout.addWidget(self.monitor_button)

        self.data_sent_label = QtWidgets.QLabel("Data Sent: 0 bytes")
        layout.addWidget(self.data_sent_label)

        self.data_received_label = QtWidgets.QLabel("Data Received: 0 bytes")
        layout.addWidget(self.data_received_label)

        self.block_website_button = QtWidgets.QPushButton("Block Website")
        self.block_website_button.clicked.connect(self.block_website)
        layout.addWidget(self.block_website_button)

        self.setLayout(layout)

    def refresh_peers(self):
        self.peers_list.clear()
        for peer_id, peer_address in self.node.dht_node.peers.items():
            self.peers_list.addItem(f"{peer_id}: {peer_address}")

    def update_traffic(self, data):
        self.traffic_list.addItem(data)

    def configure_node(self):
        config_dialog = QtWidgets.QDialog(self)
        config_dialog.setWindowTitle("Node Configuration")
        config_layout = QtWidgets.QVBoxLayout()

        port_label = QtWidgets.QLabel("Port:")
        config_layout.addWidget(port_label)
        port_input = QtWidgets.QLineEdit(str(self.node.port))
        config_layout.addWidget(port_input)

        role_label = QtWidgets.QLabel("Role:")
        config_layout.addWidget(role_label)
        role_input = QtWidgets.QComboBox()
        role_input.addItems(["entry", "relay", "exit"])
        role_input.setCurrentText(self.node.role)
        config_layout.addWidget(role_input)

        ssl_checkbox = QtWidgets.QCheckBox("Use SSL")
        ssl_checkbox.setChecked(self.node.use_ssl)
        config_layout.addWidget(ssl_checkbox)

        save_button = QtWidgets.QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_configuration(port_input.text(), role_input.currentText(), ssl_checkbox.isChecked()))
        config_layout.addWidget(save_button)

        config_dialog.setLayout(config_layout)
        config_dialog.exec_()

    def save_configuration(self, port, role, use_ssl):
        self.node.port = int(port)
        self.node.role = role
        self.node.use_ssl = use_ssl
        self.status_label.setText(f"Node running on port {self.node.port} as {self.node.role}")

    def start_monitoring(self):
        self.monitoring_timer.start(1000)  # Update every second
        print("Starting real-time monitoring...")

    def update_monitoring(self):
        self.data_sent_label.setText(f"Data Sent: {self.node.total_data_sent} bytes")
        self.data_received_label.setText(f"Data Received: {self.node.total_data_received} bytes")

    def block_website(self):
        website = QtWidgets.QInputDialog.getText(self, "Block Website", "Enter the website to block:")[0]
        if website:
            self.node.blocked_websites.add(website)
            print(f"Website {website} blocked.")

# Example usage
def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    # Simplified setup for nodes
    bootstrap_node = ('localhost', 9000)
    dht_node = DHTNode(node_id=random.randint(0, 1000), address=bootstrap_node)
    dht_node.join_network(bootstrap_node)

    entry_node = Node(role='entry', port=9001, dht_node=dht_node)
    relay_node = Node(role='relay', port=9002, dht_node=dht_node)
    exit_node = Node(role='exit', port=9003, dht_node=dht_node)

    entry_gui = NodeGUI(entry_node)
    relay_gui = NodeGUI(relay_node)
    exit_gui = NodeGUI(exit_node)

    entry_gui.show()
    relay_gui.show()
    exit_gui.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
