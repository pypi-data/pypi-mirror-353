import unittest
from cgbenigma import cgblib

class TestGetCipher(unittest.TestCase):
    def test_cipher(self):
        # Test if a known cipher can be retrieved
        cipher = cgblib.getKnownCiphers()
        # cipher[15] = 'ZUQUPNZN'
        self.assertEqual(cipher[15], "ZUQUPNZN")

if __name__ == '__main__':
    unittest.main()

