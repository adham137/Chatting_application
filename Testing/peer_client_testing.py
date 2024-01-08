import threading
import time
import unittest
from unittest.mock import patch, MagicMock

from encryption import encrypt_message
from peer_client import PeerClient

class TestPeerClient(unittest.TestCase):

    def setUp(self):
        self.client = PeerClient()

    def tearDown(self):
        # Shutdown the client to stop the infinite loop
        self.client.shutdown_client()

    @patch('builtins.input', side_effect=['Hello, server!', ''])
    @patch('your_client_module.PeerClient.messaging_port')
    @patch('your_client_module.PeerClient.client_send_udp')
    def test_client_send(self, mock_client_send_udp, mock_messaging_port, mock_input):
        # Test the client_send method

        # Mock the messaging port
        mock_messaging_port.return_value = MagicMock()

        # Start the client thread
        client_thread = threading.Thread(target=self.client.client_send, args=[self.client.shutdown_flag])
        client_thread.start()

        # Wait for the thread to start
        time.sleep(0.1)

        # Allow time for the client to process the input
        time.sleep(0.1)

        # Stop the client thread
        self.client.shutdown_client()
        client_thread.join()

        # Assertions
        mock_input.assert_called()
        mock_messaging_port.assert_called_with(encrypt_message('Hello, server!', self.client.key))
        mock_client_send_udp.assert_called_with('Hello, server!')

if __name__ == '__main__':
    unittest.main()
