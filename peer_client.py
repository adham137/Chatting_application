import socket
import threading
import colorama
from encryption import encrypt_message, decrypt_message, load_key
import pyfiglet
from colorama import Back, Fore, Style

colorama.init(autoreset =True )

class PeerClient:


    def __init__(self):

        # Connect to default server at the beginning
        self.default_server = ('127.0.0.1', 59990)
        self.connected_host = self.default_server

        # Initialize messaging port
        self.messaging_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to default server
        self.messaging_port.connect(self.connected_host)      ### TAKE A LOOK ###

        # initializes udp socket which is used to send hello messages
        # Initialize UDP socket for sending messages
        self.udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_server_address = ('127.0.0.1', 1200)  # Replace with the server's UDP address

        # Initialize listening port
        self.listening_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind listening port to a random free port and start listening to connections
        self.listening_port.bind(('127.0.0.1', 0))
        self.listening_port.listen()

        # Flag client as available
        self.is_available = True

        # Exit flag
        self.exit_flag = False

        # Get encryption/decryption key
        self.key = load_key()

        # Print welcome screen
        welcome_word = pyfiglet.figlet_format("WELCOME  TO")
        app_name = pyfiglet.figlet_format("\nTALK-ROOM APP")
        print(Fore.GREEN + welcome_word + Fore.RED + app_name)

        # Start sending/recieving functions on new threads
        self.receive_thread = threading.Thread(target=self.client_receive, args=[self.exit_flag])
        self.receive_thread.start()
        self.send_thread = threading.Thread(target=self.client_send, args=[self.exit_flag])
        self.send_thread.start()
        # Start the function that accepts connections from other peers
        self.accept_connections()

    def client_send_udp(self, message):
        try:
            self.udp_client_socket.sendto(encrypt_message(message, self.key), self.udp_server_address)
        except Exception as e:
            print(f'Error sending UDP message: {e}')

    def client_receive_udp(self):
        while not self.exit_flag:
            try:
                data, _ = self.udp_client_socket.recvfrom(1024)
                decrypted_message = decrypt_message(data, self.key)
                print(Fore.CYAN + f'Received UDP message: {decrypted_message}')
            except Exception as e:
                if self.is_available:
                    self.connect_to_default_server()
                print(f'Error receiving UDP message: {e}')



    # def client_send(self):
    #     # old = ''
    #     # new = ''
    #     while not self.exit_flag:
    #         try:
    #             # new = Fore.YELLOW + f"The port is: {self.messaging_port.getsockname()}"
    #             # if not old == new:
    #             #     print(new)
    #             #     old = new
    #             message = f'{input("")}'
    #             self.messaging_port.send(encrypt_message(message, self.key))
    #         except:
    #             if self.is_available:
    #                 self.connect_to_defualt_server()
    #             continue
    def client_send(self, exit):
        while True:
            try:
                if exit :
                    break

                message = input("")
                self.messaging_port.send(encrypt_message(message, self.key))
                # Send the same message through UDP
                if self.connected_host == self.default_server:
                    self.client_send_udp(message)
            except Exception as e:
                if self.is_available:
                    print(e)
                    self.connect_to_default_server()



    # def client_receive(self):
    #     while True:
    #         try:
    #             message = decrypt_message(self.messaging_port.recv(2048), self.key)
    #
    #             if message.split()[0] == 'COMMAND':
    #                 #print(Fore.RED + 'We are handling a command')
    #                 self.handle_command(message)
    #                 #print(Fore.WHITE + f"OUR MESSAGING PORT NOW IS {self.messaging_port.getsockname()}")
    #                 continue
    #                 # Send listening port to server
    #
    #             # Display message if not empty
    #             if message:
    #                 print(Fore.CYAN + message)
    #         except Exception as e:
    #             if self.is_available:
    #                 self.connect_to_defualt_server()
    #             continue
    def client_receive(self, exit):

        while True:
            try:
                if exit :
                    break
                message = decrypt_message(self.messaging_port.recv(2048), self.key)
                if message.split()[0] == 'COMMAND':
                    self.handle_command(message)
                    continue
                if message:
                    print(Fore.CYAN + message)
            except Exception as e:
                if self.is_available:
                    print(e)
                    self.connect_to_default_server()
                continue



    # def handle_command(self, message):
    #     message = message.split()
    #
    #     # The server is requesting your listening port
    #     if message[1] == 'GET':
    #         ### SHOULD PUT A CONDITION, IF YOU DONT WANT TO SEND YOUR LISTENING ADDRESS ###
    #         my_ip   = self.listening_port.getsockname()[0]
    #         my_port = str(self.listening_port.getsockname()[1])  ### IS GETSOCKNAME() RIGHT ? ###
    #         message = f"{my_ip} {my_port}"
    #         #print(Fore.RED + f"The message that will be sent to the server: {message}")
    #         self.messaging_port.send(encrypt_message(message, self.key))
    #
    #     # Connect to port given by the server
    #     elif message[1] == 'POST':
    #         #print(f'The message is : {message}')
    #         receiver_addr = (message[2], int(message[3]))
    #         #print(Fore.GREEN + f"Connecting to '{receiver_addr}' instead of default server")
    #         # Close the old connection and open a new one with the peer
    #         self.messaging_port.close()         ### IS CLOSING THE CONNECTION LIKE THIS RIGHT? ###
    #         self.messaging_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         self.messaging_port.connect(receiver_addr)
    #
    #         # # Re-run sending thread
    #         # self.exit_flag = True
    #         # self.send_thread.join()
    #         # self.exit_flag = False
    #         # self.send_thread.start()
    #
    #         self.connected_host = receiver_addr
    #         message = f"You are now connected to '{receiver_addr}', This is a private chat"
    #         print(Fore.GREEN + message)
    #         self.is_available = False


    def handle_command(self, message):
        message = message.split()

        # The server is requesting your listening port
        if message[1] == 'GET':

            # construct and send the message
            my_ip   = self.listening_port.getsockname()[0]
            my_port = str(self.listening_port.getsockname()[1])
            message = f"{my_ip} {my_port}"
            #print(Fore.RED + f"The message that will be sent to the server: {message}")
            self.messaging_port.send(encrypt_message(message, self.key))
            self.is_available = False



        # Connect to port given by the server
        elif message[1] == 'POST':

            # # Stop sending and receiving threads to take user input
            # self.exit_flag = True
            # self.send_thread.join()
            # self.receive_thread.join()

            # Ask for the user if he wants to accept the conenction
            msg = Fore.YELLOW + f"user '{message[4]}' with address '{message[2]} {message[3]}' is requesting to connect\n" \
                                f" to you and start a private P2P chat, type 'YES' to accept connection\n , any other " \
                                f"input will be considered as a rejection."
            print(msg)
            action = input()

            # Ask for the user if he wants to accept the conenction
            if action == 'YES':
                # Close the old connection and open a new one with the peer
                receiver_addr = (message[2], int(message[3]))
                # print(Fore.GREEN + f"Connecting to '{receiver_addr}' instead of default server")
                self.messaging_port.close()  ### IS CLOSING THE CONNECTION LIKE THIS RIGHT? ###
                self.messaging_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.messaging_port.connect(receiver_addr)

                self.connected_host = receiver_addr
                message = f"You are now connected to '{receiver_addr}', This is a private chat"
                print(Fore.GREEN + message)
                self.is_available = False
            else:
                # Send REJECT message
                self.messaging_port.send(encrypt_message("REJECT", self.key))

            # # Restart sending and receiving threads
            # self.exit_flag = False
            # self.send_thread.start()
            # self.receive_thread.start()




    def accept_connections(self):
        while self.is_available:
        #while True:
            # Accept incoming connections
            client_socket, client_address = self.listening_port.accept()
            message = f"You are now connected to '{client_address}', This is a private chat"
            print(Fore.GREEN + message)

            # Mark as un avalible while trying to connect to other clients
            self.is_available = False

            # # Close the existing connection to messaging port
            # self.messaging_port.close()

            # Connect to the new client socket on listening port
            self.messaging_port = client_socket
            self.connected_host = client_address

            # Mark as not available
            #self.is_available = True
            ### What happens to listening port ? ###

            # Re-run receiving and listening threads
            # self.exit_flag = True
            # self.receive_thread.join()
            # self.send_thread.join()
            # self.exit_flag = False
            # self.receive_thread.start()
            # self.send_thread.start()



    # def connect_to_default_server(self):
    #
    #     # Close sending and receiving threads
    #     self.exit_flag = True
    #     self.receive_thread.join()
    #     self.send_thread.join()
    #
    #     option = ''
    #     while option not in ['1', '0']:
    #         message = Fore.BLUE + 'It appears that an error has occurred, ' \
    #                               'do you want to reconnect to the default server? (1 for Yes, 0 for no)'
    #         print(message)
    #         option = f'{input("")}'
    #
    #     if option == '0':
    #         exit()
    #
    #     # Close the messaging port
    #     self.messaging_port.close()
    #
    #     # Reconnect messaging port
    #     self.messaging_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     self.messaging_port.connect(self.default_server)                     ### Does closing the connection destroy the port? ###
    #     self.connected_host = self.default_server
    #
    #     # Restart sending and receiving threads
    #     self.exit_flag = False
    #     self.receive_thread.start()
    #     self.send_thread.start()
    #
    #     # Mark as available
    #     self.is_available = True
    #
    #     # Clear listening port
    #     # self.listening_port.listen()

    def connect_to_default_server(self):

        message = Fore.BLUE + 'It appears that an error has occurred, ' \
                              'You are being reconnected with the default server'
        print(message)

        # Close the messaging port
        self.messaging_port.close()

        # Reconnect messaging port
        self.messaging_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messaging_port.connect(self.default_server)                     ### Does closing the connection destroy the port? ###
        self.connected_host = self.default_server

        self.is_available = True


# Initialize a PeerClient instance
main = PeerClient()