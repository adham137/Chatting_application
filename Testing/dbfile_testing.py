import unittest
from unittest.mock import patch
from dbfile import DB

class TestDB(unittest.TestCase):

    def setUp(self):
        # Add a test user to the database
        self.db = DB()
        self.test_username = "test_user"
        self.test_password = "test_password"
        self.db.register(self.test_username, self.test_password)

    def tearDown(self):
        # Remove the test user and close the database connection
        self.db.db.accounts.delete_one({"username": self.test_username})
        self.db.client.close()

    def test_is_account_exist(self):
        # Assert that the test account exists in the database
        result = self.db.is_account_exist(self.test_username)
        self.assertTrue(result)

    def test_register(self):
        # Test the registration process
        self.db.register(self.test_username, self.test_password)
        result = self.db.is_account_exist(self.test_username)
        self.assertTrue(result)

    def test_get_password(self):
        # Test retrieving the password for a given username
        self.db.register(self.test_username, self.test_password)
        retrieved_password = self.db.get_password(self.test_username)
        self.assertEqual(retrieved_password, self.test_password)


if __name__ == '__main__':
    unittest.main()
