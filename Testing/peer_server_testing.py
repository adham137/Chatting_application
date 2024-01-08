import unittest
from unittest.mock import patch, MagicMock
import socket
import threading
import time
from your_server_module import PeerServer  # Replace with the actual import

class TestPeerServer(unittest.TestCase):

    def setUp(self):
        self.server = PeerServer()

    def tearDown(self):
        # Add any cleanup code here, such as closing the server socket
        self.server.listening_port.close()

    def mock_client(self, message):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 59990))
        client_socket.send(message.encode('utf-8'))
        time.sleep(0.1)  # Allow time for server processing
        client_socket.close()

    @patch('builtins.print')
    def test_receive_connections(self, mock_print):
        # Test the receive_connections function
        # Start the server in a separate thread
        server_thread = threading.Thread(target=self.server.receive_connections)
        server_thread.start()

        # Simulate a client connection
        self.mock_client('1\n')  # Simulate user input '1'

        # Allow time for the server to process the connection
        time.sleep(0.1)

        # Stop the server thread
        self.server.listening_port.close()
        server_thread.join()

        # Assertions based on the expected print statements
        mock_print.assert_called_with('Server is running and listening')
        mock_print.assert_called_with('127.0.0.1 is trying to connect')

    # Add other test cases as needed
