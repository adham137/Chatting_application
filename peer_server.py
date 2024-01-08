import threading
import socket
import time
import colorama
from encryption import encrypt_message, decrypt_message, load_key
from dbfile import DB
from colorama import Back, Fore, Style
colorama.init(autoreset=True)

class PeerServer :

    def __init__(self):

        # Initialize database
        self.db = DB()

        # Initialize listening port
        self.address = ('127.0.0.1', 59990)
        self.listening_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening_port.bind(self.address)
        self.listening_port.listen()

        # Initialize arrays clients, addresses, aliases
        self.clients = []
        self.addresses = []
        self.aliases = []
        #  Initialize dictionary of chatrooms and fill it from database
        self.chatroom_dict = dict()  # { room_name : [client1, client2, ...] }
        for chatroom_name in list(self.db.get_chat_rooms()):
            self.chatroom_dict[chatroom_name] = []

        # Initialize encryption/decryption key
        self.key = load_key()
        # Initialize UDP socket for receiving messages
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('127.0.0.1', 1200))

        # Start a new thread to handle UDP messages
        self.udp_thread = threading.Thread(target=self.receive_udp_messages)
        self.udp_thread.start()

        # Call function receive connections
        self.receive_connections()

    def receive_udp_messages(self):
        while True:
            try:
                data, addr = self.udp_socket.recvfrom(1024)
                message = decrypt_message(data, self.key)
                print(f'Received UDP message from {addr}: {message}')
                # Process the UDP message as needed
            except Exception as e:
                print(f'Error receiving UDP message: {e}')

    def receive_connections(self):
        ##########################################################################

        # Continuous loop that accepts connections from incoming clients and passes
        # to validate_client function or connect_client

        ##########################################################################

        print(Fore.BLUE + 'Server is running and listening')

        while True:

            # Returns a socket obj and address of anything that connects to us
            client, address = self.listening_port.accept()
            print(Fore.BLUE + f'{str(address)} is trying to connect')

            # If client is already logged in, run function connected
            if client in self.clients:
                # If client is already connected show him menu 2 (Logout, Chat, Show list of connected clients)
                thread = threading.Thread(target=self.connected_client)
                thread.start()
            else:
                # If client is not logged in, validate client
                thread = threading.Thread(target=self.validate_client, args=[client]).start()


    def validate_client(self, client):
        ##########################################################################

        # Accepts/Rejects clients based on the authentication info
        # In case of Accepting:
        #   client is added to list of clients.
        #   alias is added to list of aliases.
        #   broadcast a message saying [alias] has connected.
        # In case of rejection:
        #   send the client that he is rejected.
        #   close connection and thread.

        ##########################################################################
        # Request option

        client.send(encrypt_message("\n ***Choose an option: \n 1. Register \n 2. Login \n", self.key))

        # Receive answer from client
        action = decrypt_message(client.recv(2048), self.key)
        while action not in ['1', '2']:
            client.send(encrypt_message("Invalid option, please try again \n", self.key))
            action = decrypt_message(client.recv(2048), self.key)

        # Request Username
        client.send(encrypt_message('Username: ', self.key))

        # Receive Username
        username = decrypt_message(client.recv(2048), self.key).replace(" ", "")

        # Request Password
        client.send(encrypt_message('Password: ', self.key))
        # Receive Password
        password = decrypt_message(client.recv(2048), self.key).replace(" ", "")

        # Validate
        try:
            print(f'Received username from user: {username}')

            if action == '1':
                print(f'{username} chose to register.')

                if not self.db.is_account_exist(username):
                    encrypted_password = encrypt_message(password, self.key)
                    self.db.register(username, encrypted_password)
                    client.send(encrypt_message('Registration successful!', self.key))

                else:
                    client.send(
                        encrypt_message('Username already exists.',
                                        self.key))
                    self.disconnect_client(client)
                    return


            elif action == '2':
                print(f'{username} chose to login.')

                if self.db.is_account_exist(username) and (decrypt_message(self.db.get_password(username), self.key) == password):
                    client.send(encrypt_message('Login successful!', self.key))
                else:
                    client.send(encrypt_message('Invalid username or password.', self.key))
                    self.disconnect_client(client)
                    return

            self.aliases.append(username)
            self.addresses.append(client.getsockname())
            self.clients.append(client)

            # broadcast(f'{username} ''has joined the chatroom!')
            client.send(encrypt_message('You are now connected!', self.key))

            # Run connected_client
            self.connected_client(client)
        except:
            client.send(encrypt_message('There was an error.', self.key))
            self.disconnect_client(client)


    def connected_client(self, client):
        ##########################################################################

        # Present client with list of options when he is connected

        ##########################################################################
        time.sleep(0.2)

        while True:
            try:
                # Request option
                client.send(encrypt_message(
                    "\n ***Choose an option: \n 1. Logout \n 2. List of online clients \n 3. Create Chat room \n 4. List of Chat rooms \n 5. Join Chat room \n 6. Private Chat",
                    self.key))

                # Recieve answer from client
                action = decrypt_message(client.recv(2048), self.key)
                if action[0] not in ['1', '2', '3', '4', '5', '6']:
                    client.send(encrypt_message("Invalid option, please try again \n", self.key))
                    client.send(encrypt_message(
                        "\n ***Choose an option: \n 1. Logout \n 2. List of online clients \n 3. Create Chat room \n 4. List of Chat rooms \n 5. Join Chat room \n 6. Chat",
                        self.key))
                    action = decrypt_message(client.recv(2048), self.key)

                if action == '1':
                    index_of_client = self.index(client)
                    alias_of_client = self.aliases[index_of_client]
                    print(f'{alias_of_client} chose to logout.')
                    # clients.remove(client)
                    # aliases.remove(alias_of_client)
                    client.send(encrypt_message('Logout successful!', self.key))
                    self.disconnect_client(client)
                    return

                elif action == '2':
                    client.send(encrypt_message(self.get_online_peers(), self.key))

                elif action == '3':
                    self.create_chat_room(client, self.aliases[self.clients.index(client)])

                elif action == '4':
                    self.list_chat_rooms(client)

                elif action == '5':
                    # Request chat room name from the client if room name is not provided
                    client.send(encrypt_message("Enter the chat room name to join: ", self.key))
                    room_name = decrypt_message(client.recv(2048), self.key)
                    while room_name not in list(self.chatroom_dict.keys()):
                        message = f"There is no chatroom with this name \n " \
                                  f"the available chatrooms \n " \
                                  f"{self.list_chat_rooms()}"
                        client.send(encrypt_message(message, self.key))
                        client.send(encrypt_message("Enter the chat room name to join: ", self.key))
                        room_name = decrypt_message(client.recv(2048), self.key)
                    self.join_chat_room(client, room_name)

                elif action == '6':
                    self.handle_p2p_client_chat(client)
            except:
                return



    def handle_p2p_client_chat(self, client1):

        # Ask client1 for client2 username
        client1.send(encrypt_message('Specify the username of the user you want to chat with', self.key))
        client2_name = decrypt_message(client1.recv(2048), self.key)

        # Get client2 socket
        try:
            client2 = self.clients[self.aliases.index(client2_name)]
        except:
            client1.send(encrypt_message('No client with matching username', self.key))
            return

        try:
            # Request from client1 it's listening port address
            client1.send(encrypt_message(f"COMMAND GET", self.key))

            client1_addr = decrypt_message(client1.recv(2048), self.key)
            client1_ip   = client1_addr.split()[0]
            client1_port = client1_addr.split()[1]
            #print(f"Client1 address is '{client1_addr}'")


            # Provide client2 with client1 listening port address
            msg = f"COMMAND  POST {client1_ip} {client1_port} {self.aliases[self.clients.index(client1)]}"
            #print(f"We are sending the following message to client 2: {msg}")
            client2.send(encrypt_message(msg, self.key))

            # If client2 sends a message then he rejected client1 connection
            # If client2 connection closes then he accepted connection
            try:
                client2_response = decrypt_message(client2.recv(2048), self.key)
                client1.send(encrypt_message(f"{client2_name} rejected your connection request.", self.key))
            except:

                # Close connections with both clients
                self.disconnect_client(client1)
                self.disconnect_client(client2)
                return

        except:
            client1.send(encrypt_message(f"{client2_name} was found but there was an error connecting with him.", self.key))
            return


    def get_online_peers(self):
        ##########################################################################

        # Return a message containing all online clients

        ##########################################################################
        msg = ''
        for alias in self.aliases:
            msg += alias
            msg += '\n'

        return 'online users: \n' + msg if msg != '' else 'No online clients'


    def broadcast(self, room_name, message):
        ##########################################################################

        # Broadcast a message to all connected clients

        ##########################################################################
        print('Broadcasting')
        for client in self.chatroom_dict[room_name]:
            try:
                encrypted_message = encrypt_message(message, self.key)
                client.send(encrypted_message)
            except socket.error:
                print(f'Could not send message to {self.aliases[self.clients.index(client)]}')



    def listen_to_client(self, room_name, client):
        ##########################################################################

        # Continuous loop that listens to messages from a specific client and
        # echoes back the message to the client.

        ##########################################################################
        # client_socket.sendall(encrypt_message("\n Let's start chattin ! ", key))
        print('Listening')
        while True:
            try:
                # Receive the message from the client
                message = decrypt_message(client.recv(2048), self.key)
                alias = self.aliases[self.clients.index(client)]
                if message:
                    self.broadcast(room_name, f'{alias} : {message}')
                    # If the message is empty, the client has disconnected

                # print(f"Received message from {client_socket.getpeername()}: {message}")

                # Broadcast message to all clients in the chatroom

            except Exception as e:
                print(f"Error: {e}")
                break  # If an error occurs, break out of the loop

        # Remove from chatroom dictionary
        self.chatroom_dict[room_name].remove(client)

        # Broadcast "User has left the chat"
        self.broadcast(room_name, f'User "{self.aliases[self.clients.index(client)]}" has left the chat')

        # Disconnect client
        self.disconnect_client(client)

        return


    def disconnect_client(self, client):

        # Remove client from clients, aliases, addresses
        if client in self.clients:
            index_of_bad_client = self.clients.index(client)
            self.clients.remove(client)
            self.aliases.remove(self.aliases[index_of_bad_client])
            self.addresses.remove(self.addresses[index_of_bad_client])

        # Remove from database

        # Close the connection
        #client.send(encrypt_message('You are being disconnected',self.key))
        print(Fore.BLUE + f'{str(client.getsockname)} is being disconnected')
        client.close()


    def create_chat_room(self, client, alias):

        try:
            # Request chat room name from the client
            client.send(encrypt_message("Enter the chat room name: ", self.key))
            room_name = decrypt_message(client.recv(2048), self.key)

            # Create the chat room in the database
            self.db.create_chat_room(room_name, alias)

            # Create the chat room in the dictionary
            self.chatroom_dict[room_name] = []

            # Inform the creator about the new chat room
            client.send(encrypt_message(f"Chat room '{room_name}' created successfully!", self.key))

            # Join the client to the newly created chatroom
            self.join_chat_room(client, room_name)

        except:
            print('Error creating chat room')


    def join_chat_room(self, client, room_name):

        # Check if the chat room exists
        if not self.db.is_chat_room_exist(room_name):
            client.send(encrypt_message(f'Could not find "{room_name}" in database.', self.key))
            return

        # Add the client to the chat room in the dictionary
        self.chatroom_dict[room_name].append(client)

        # Add the client's alias to the chat room in the database
        self.db.add_alias_to_chat_room(room_name, self.aliases[self.clients.index(client)])

        # Notify client that he has joined the chatroom, notify other users that
        # client has joined
        client.send(encrypt_message(f'You have joined chat room "{room_name}" successfully!', self.key))
        self.broadcast(room_name, f'{self.aliases[self.clients.index(client)]} has joined chat room "{room_name}".')

        # Call function listen to start chatting
        self.listen_to_client(room_name, client)


    def list_chat_rooms(self, client):
        # Get the list of available chat rooms from the database
        chat_rooms = self.db.get_chat_rooms()

        # Send the list of chat rooms to the client
        client.send(encrypt_message("\nList of available chat rooms:\n" + "\n".join(chat_rooms), self.key))


# Initialize a PeerServer instance
main = PeerServer()