import threading
import unittest
from unittest.mock import patch
from peer_client import PeerClient
from peer_server import PeerServer
from encryption import generate_key, load_key

class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.server = PeerServer()


    # def tearDown(self):
    #     # Clean up the test environment, if needed
    #     pass

    @patch('builtins.input', side_effect=['1'])
    @patch('builtins.print')
    def test_integration_register_and_chat(self, mock_input, mock_print=None):

        # Create client instance
        client = PeerClient()

        # Simulate client registration
        client_thread = threading.Thread(target=self.server.validate_client, args=[client.messaging_port])
        client_thread.start()
        client_thread.join()
        mock_print.assert_called_with('It appears that an error has occurred, You are being reconnected with the default server')

        # Simulate client chat
        client_thread = threading.Thread(target=self.server.connected_client, args=[client.messaging_port])
        client_thread.start()
        client_thread.join()



if __name__ == '__main__':
    unittest.main()
