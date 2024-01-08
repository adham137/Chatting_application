from pymongo import MongoClient


# Includes database operations
class DB:

    # db initializations
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['p2p-chat']

    # checks if an account with the username exists
    def is_account_exist(self, username):
        if len(list(self.db.accounts.find({'username': username}))) > 0:
            return True
        else:
            return False

    # registers a user
    def register(self, username, password):
        account = {
            "username": username,
            "password": password
        }
        self.db.accounts.insert_one(account)

    # retrieves the password for a given username
    def get_password(self, username):
        return self.db.accounts.find_one({"username": username})["password"]

    # checks if an account with the username online
    def is_account_online(self, username):
        return self.db.online_peers.count_documents({'username': username}) > 0

    # logs in the user
    def user_login(self, username, ip, port):
        online_peer = {
            "username": username,
            "ip": ip,
            "port": port
        }
        self.db.online_peers.insert_one(online_peer)

    # logs out the user
    def user_logout(self, username):
        self.db.online_peers.delete_one({"username": username})

    # retrieves the ip address and the port number of the username
    def get_peer_ip_port(self, username):
        res = self.db.online_peers.find_one({"username": username})
        return res["ip"], res["port"]

    def create_chat_room(self, room_name, creator_alias):
        chat_room = {
            "room_name": room_name,
            "creator_alias": creator_alias,
            "aliases": [creator_alias]  # Include the creator in the list of aliases
        }
        self.db.chat_rooms.insert_one(chat_room)

    def get_chat_rooms(self):
        # Retrieve the list of available chat rooms from the database
        chat_rooms = self.db.chat_rooms.distinct("room_name")
        return chat_rooms

    def is_chat_room_exist(self, room_name):
        # Check if a chat room with the given name exists in the database
        return self.db.chat_rooms.count_documents({"room_name": room_name}) > 0

    def add_alias_to_chat_room(self, room_name, alias):
        # Add an alias to the specified chat room in the database
        self.db.chat_rooms.update_one({"room_name": room_name}, {"$push": {"aliases": alias}})

