import unittest
import sys
sys.path.append("../dist")
from cgbenigma import cgblib

class TestBasicEncryption(unittest.TestCase):
    def test_encrypt(self):
        # Test basic encryption functionality
        cipher = cgblib.encrypt("HELLO", "AAA", "AAA")
        # cipher = [{'Key': 'AAA', 'Ring': 'AAA', 'Message': 'HELLO', 'Cipher': 'NFOOV'}]
        self.assertEqual(cipher[0]['Cipher'], "NFOOV")

    def test_decrypt(self):
        # Test basic decryption functionality
        plain_text = cgblib.decrypt("NFOOV", "AAA", "AAA")
        # plain_text = 'HELLO'
        self.assertEqual(plain_text, "HELLO")

if __name__ == '__main__':
    unittest.main()

