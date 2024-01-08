import threading
import socket
import unittest
from peer_server import PeerServer

class TestStress(unittest.TestCase):

    def setUp(self):
        # Create server instance
        self.server = PeerServer()


    def test_stress_server(self):
        # Start Listening on a new thread
        server_thread = threading.Thread(target=self.server.receive_connections)
        server_thread.start()

        # Simulate multiple clients connecting to the server simultaneously
        num_clients = 10
        client_threads = []

        for i in range(num_clients):
            client_thread = threading.Thread(target=self.simulate_client, args=(i,))
            client_thread.start()
            client_threads.append(client_thread)

        # Wait for all client threads to finish
        for thread in client_threads:
            thread.join()

    def simulate_client(self, client_id):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 59990))

        # Simulate client registration
        registration_message = f"1\nTestUser{client_id}\nTestPassword{client_id}\n"
        client_socket.send(registration_message.encode())

        # Simulate client chat
        chat_message = f"6\n"
        client_socket.send(chat_message.encode())




if __name__ == '__main__':
    unittest.main()
