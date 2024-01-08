import unittest
import os
from encryption import generate_key, load_key, encrypt_message, decrypt_message

class TestEncryption(unittest.TestCase):

    def setUp(self):
        # Load the secrete key
        self.key = load_key()
    #
    # def tearDown(self):
    #     # Close the secrete key file
    #     if os.path.exists("secrete.key"):
    #         os.close(self.file)


    def test_generate_key(self):
        # The key is generated
        self.assertTrue(os.path.exists("secrete.key"))

    def test_load_key(self):
        # The key is loaded
        self.assertTrue(isinstance(self.key, str))

    def test_encrypt_decrypt_message(self):
        # Encryption and Decryption
        original_message = "Test message"
        encrypted_message = encrypt_message(original_message, self.key)
        decrypted_message = decrypt_message(encrypted_message, self.key)
        self.assertEqual(original_message, decrypted_message)

if __name__ == '__main__':
    unittest.main()
