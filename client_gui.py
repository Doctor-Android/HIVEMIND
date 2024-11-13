import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, QTextEdit, QMessageBox, QFileDialog, QColorDialog, QFormLayout, QDialog, QDialogButtonBox, QListWidget, QInputDialog
from PyQt5.QtGui import QFont
import json
import os

class ClientGUI(QMainWindow):
    def __init__(self, network, user, community, privacy, data_manager):
        super().__init__()
        self.setWindowTitle("HIVEMIND Client")
        self.setGeometry(100, 100, 800, 600)

        # Assign components
        self.network = network
        self.user = user
        self.community = community
        self.privacy = privacy
        self.data_manager = data_manager

        # Load default vaporwave aesthetic
        self.load_default_style()

        # Setup GUI
        self.setup_ui()

    def load_default_style(self):
        # Set default vaporwave colors and fonts
        self.setStyleSheet("background-color: #ff77ff;")
        self.default_font = QFont("Comic Sans MS", 10, QFont.Bold)
        self.text_color = "#00ffcc"
        self.button_color = "#ff00ff"

    def setup_ui(self):
        layout = QVBoxLayout()

        # Network Info
        self.network_label = QLabel("Network: Not connected")
        self.network_label.setFont(self.default_font)
        self.network_label.setStyleSheet(f"color: {self.text_color};")
        layout.addWidget(self.network_label)

        # User Info
        self.user_label = QLabel(f"User: {self.user.username}")
        self.user_label.setFont(self.default_font)
        self.user_label.setStyleSheet(f"color: {self.text_color};")
        layout.addWidget(self.user_label)

        # Community Info
        self.community_label = QLabel(f"Community: {self.community.name}")
        self.community_label.setFont(self.default_font)
        self.community_label.setStyleSheet(f"color: {self.text_color};")
        layout.addWidget(self.community_label)

        # Chat area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(self.default_font)
        self.chat_display.setStyleSheet(f"color: {self.text_color}; background-color: #000000;")
        layout.addWidget(self.chat_display)

        # Message input
        self.message_input = QLineEdit()
        self.message_input.setFont(self.default_font)
        self.message_input.setStyleSheet(f"color: {self.text_color}; background-color: #000000;")
        layout.addWidget(self.message_input)

        # Send button
        send_button = QPushButton("Send")
        send_button.setFont(self.default_font)
        send_button.setStyleSheet(f"background-color: {self.button_color}; color: {self.text_color};")
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

        # Connect to network button
        connect_network_button = QPushButton("Connect to Network")
        connect_network_button.setFont(self.default_font)
        connect_network_button.setStyleSheet(f"background-color: {self.button_color}; color: {self.text_color};")
        connect_network_button.clicked.connect(self.connect_to_network)
        layout.addWidget(connect_network_button)

        # Discover networks button
        discover_networks_button = QPushButton("Discover Networks")
        discover_networks_button.setFont(self.default_font)
        discover_networks_button.setStyleSheet(f"background-color: {self.button_color}; color: {self.text_color};")
        discover_networks_button.clicked.connect(self.discover_networks)
        layout.addWidget(discover_networks_button)

        # Create network button
        create_network_button = QPushButton("Create Network")
        create_network_button.setFont(self.default_font)
        create_network_button.setStyleSheet(f"background-color: {self.button_color}; color: {self.text_color};")
        create_network_button.clicked.connect(self.create_network)
        layout.addWidget(create_network_button)

        # Join network button
        join_network_button = QPushButton("Join Network")
        join_network_button.setFont(self.default_font)
        join_network_button.setStyleSheet(f"background-color: {self.button_color}; color: {self.text_color};")
        join_network_button.clicked.connect(self.join_network)
        layout.addWidget(join_network_button)

        # Edit network button
        edit_network_button = QPushButton("Edit Network")
        edit_network_button.setFont(self.default_font)
        edit_network_button.setStyleSheet(f"background-color: {self.button_color}; color: {self.text_color};")
        edit_network_button.clicked.connect(self.edit_network)
        layout.addWidget(edit_network_button)

        # Load texture pack button
        load_texture_pack_button = QPushButton("Load Texture Pack")
        load_texture_pack_button.setFont(self.default_font)
        load_texture_pack_button.setStyleSheet(f"background-color: {self.button_color}; color: {self.text_color};")
        load_texture_pack_button.clicked.connect(self.load_texture_pack_dialog)
        layout.addWidget(load_texture_pack_button)

        # Customize theme button
        customize_theme_button = QPushButton("Customize Theme")
        customize_theme_button.setFont(self.default_font)
        customize_theme_button.setStyleSheet(f"background-color: {self.button_color}; color: {self.text_color};")
        customize_theme_button.clicked.connect(self.customize_theme)
        layout.addWidget(customize_theme_button)

        # Ban website button
        ban_website_button = QPushButton("Ban Website")
        ban_website_button.setFont(self.default_font)
        ban_website_button.setStyleSheet(f"background-color: {self.button_color}; color: {self.text_color};")
        ban_website_button.clicked.connect(self.ban_website)
        layout.addWidget(ban_website_button)

        # Main widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            self.chat_display.append(f"You: {message}")
            self.message_input.clear()

    def connect_to_network(self):
        peer_address = "localhost"
        try:
            self.network.start_server()
            QMessageBox.information(self, "Network", f"Connected to network at {peer_address}")
        except Exception as e:
            QMessageBox.critical(self, "Network", f"Failed to connect: {e}")

    def discover_networks(self):
        networks = self.network.discover_networks()
        dialog = NetworkDiscoveryDialog(networks, self)
        dialog.exec_()

    def create_network(self):
        dialog = NetworkCreationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            network_name, password, rules, description, laws = dialog.get_network_details()
            if not network_name or not password:
                QMessageBox.warning(self, "Create Network", "Network name and password cannot be empty.")
                return
            if self.network.create_network(network_name, password, rules, description, laws, self.user.username):
                QMessageBox.information(self, "Create Network", f"Network '{network_name}' created successfully.")
            else:
                QMessageBox.critical(self, "Create Network", "Failed to create network. It may already exist.")

    def join_network(self):
        dialog = NetworkJoinDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            network_name, password = dialog.get_network_details()
            if not network_name or not password:
                QMessageBox.warning(self, "Join Network", "Network name and password cannot be empty.")
                return
            if self.network.join_network(network_name, password):
                QMessageBox.information(self, "Join Network", f"Successfully joined network '{network_name}'")
            else:
                QMessageBox.critical(self, "Join Network", "Failed to join network. Check the name and password.")

    def edit_network(self):
        dialog = NetworkEditDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            network_name, new_rules, new_description, new_laws = dialog.get_network_details()
            if not network_name:
                QMessageBox.warning(self, "Edit Network", "Network name cannot be empty.")
                return
            if self.network.edit_network(network_name, new_rules, new_description, new_laws, self.user.username):
                QMessageBox.information(self, "Edit Network", f"Network '{network_name}' updated successfully.")
            else:
                QMessageBox.critical(self, "Edit Network", "Failed to update network. Only the owner can edit.")

    def load_texture_pack_dialog(self):
        pack_path, _ = QFileDialog.getOpenFileName(self, "Select Texture Pack", "", "JSON files (*.json)")
        if pack_path:
            self.load_texture_pack(pack_path)
            QMessageBox.information(self, "Texture Pack", "Texture pack loaded successfully!")

    def customize_theme(self):
        bg_color = QColorDialog.getColor(title="Choose Background Color").name()
        text_color = QColorDialog.getColor(title="Choose Text Color").name()
        button_color = QColorDialog.getColor(title="Choose Button Color").name()

        if bg_color and text_color and button_color:
            self.setStyleSheet(f"background-color: {bg_color};")
            self.text_color = text_color
            self.button_color = button_color
            self.update_gui_colors()
            QMessageBox.information(self, "Customize Theme", "Theme customized successfully!")

    def update_gui_colors(self):
        self.network_label.setStyleSheet(f"color: {self.text_color};")
        self.user_label.setStyleSheet(f"color: {self.text_color};")
        self.community_label.setStyleSheet(f"color: {self.text_color};")
        self.chat_display.setStyleSheet(f"color: {self.text_color}; background-color: #000000;")
        self.message_input.setStyleSheet(f"color: {self.text_color}; background-color: #000000;")

    def ban_website(self):
        if self.community.is_admin(self.user.username):
            website, ok = QInputDialog.getText(self, "Ban Website", "Enter the website to ban:")
            if ok and website:
                self.community.ban_website(self.user.username, website)
                for node in self.network.nodes:  # Assuming self.network.nodes is a list of Node instances
                    node.blocked_websites.add(website)
                print(f"Website {website} banned across the network.")
        else:
            QMessageBox.warning(self, "Permission Denied", "You are not authorized to ban websites.")

    def run(self):
        self.show()

class NetworkCreationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Network")
        self.setGeometry(100, 100, 400, 500)

        self.layout = QFormLayout(self)

        self.network_name_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.rules_input = QTextEdit(self)
        self.description_input = QTextEdit(self)
        self.laws_input = QTextEdit(self)

        self.layout.addRow("Network Name:", self.network_name_input)
        self.layout.addRow("Password:", self.password_input)
        self.layout.addRow("Rules:", self.rules_input)
        self.layout.addRow("Description:", self.description_input)
        self.layout.addRow("Laws (e.g., banned URLs, key terms):", self.laws_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.validate_inputs)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def validate_inputs(self):
        if not self.network_name_input.text().strip() or not self.password_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Network name and password cannot be empty.")
        else:
            self.accept()

    def get_network_details(self):
        return (self.network_name_input.text(), self.password_input.text(), self.rules_input.toPlainText(), self.description_input.toPlainText(), self.laws_input.toPlainText())

class NetworkJoinDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Join Network")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QFormLayout(self)

        self.network_name_input = QLineEdit(self)
        self.password_input = QLineEdit(self)

        self.layout.addRow("Network Name:", self.network_name_input)
        self.layout.addRow("Password:", self.password_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.validate_inputs)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def validate_inputs(self):
        if not self.network_name_input.text().strip() or not self.password_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Network name and password cannot be empty.")
        else:
            self.accept()

    def get_network_details(self):
        return (self.network_name_input.text(), self.password_input.text())

class NetworkEditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Network")
        self.setGeometry(100, 100, 400, 400)

        self.layout = QFormLayout(self)

        self.network_name_input = QLineEdit(self)
        self.new_rules_input = QTextEdit(self)
        self.new_description_input = QTextEdit(self)
        self.new_laws_input = QTextEdit(self)
        self.banned_urls_input = QTextEdit(self)

        self.layout.addRow("Network Name:", self.network_name_input)
        self.layout.addRow("New Rules:", self.new_rules_input)
        self.layout.addRow("New Description:", self.new_description_input)
        self.layout.addRow("New Laws:", self.new_laws_input)
        self.layout.addRow("Banned URLs (comma-separated):", self.banned_urls_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.validate_inputs)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def validate_inputs(self):
        if not self.network_name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Network name cannot be empty.")
        else:
            self.accept()

    def get_network_details(self):
        return (self.network_name_input.text(), self.new_rules_input.toPlainText(), self.new_description_input.toPlainText(), self.new_laws_input.toPlainText(), self.banned_urls_input.toPlainText().split(','))

class NetworkDiscoveryDialog(QDialog):
    def __init__(self, networks, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Discover Networks")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout(self)

        self.network_list = QListWidget(self)
        self.network_list.addItems(networks)
        self.layout.addWidget(self.network_list)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok, self)
        self.button_box.accepted.connect(self.accept)
        self.layout.addWidget(self.button_box)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientGUI()
    window.run()
    sys.exit(app.exec_()) 