import sys
from PyQt5.QtWidgets import QApplication
from network import Node, DHTNode, NodeGUI
from client_gui import ClientGUI
from community import Community
from user import User
from privacy import Privacy
from data import DataManager
import random

def main():
    app = QApplication(sys.argv)

    # Initialize components
    user = User(username="test_user", password="securepassword")
    community = Community(name="Test Community", description="A test community", creator=user.username)
    privacy = Privacy()
    data_manager = DataManager()

    # Set up the network
    bootstrap_node = ('localhost', 9000)
    dht_node = DHTNode(node_id=random.randint(0, 1000), address=bootstrap_node)
    dht_node.join_network(bootstrap_node)

    # Create nodes
    entry_node = Node(role='entry', port=9001, dht_node=dht_node)
    relay_node = Node(role='relay', port=9002, dht_node=dht_node)
    exit_node = Node(role='exit', port=9003, dht_node=dht_node)

    # Create GUI components
    entry_gui = NodeGUI(entry_node)
    relay_gui = NodeGUI(relay_node)
    exit_gui = NodeGUI(exit_node)
    client_gui = ClientGUI(network=entry_node, user=user, community=community, privacy=privacy, data_manager=data_manager)

    # Show the GUI
    entry_gui.show()
    relay_gui.show()
    exit_gui.show()
    client_gui.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 