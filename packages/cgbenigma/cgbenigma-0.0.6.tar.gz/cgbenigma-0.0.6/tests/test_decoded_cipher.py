import unittest
from cgbenigma import cgblib

class TestDecodedCipher(unittest.TestCase):
    def test_cipher(self):
        # Test if the decrypted cipher returns the expected result
        decrypted = cgblib.getDecryptedCiphers("A")
        decoded = decrypted[0]['decoded']
        text = decoded[1]['message']
        message = cgblib.decrypt(decoded[1]['cipher'], decoded[1]['key'], decoded[1]['ring'])
        # text = USOGDWHEN
        self.assertEqual(text, "USOGDWHEN")
        self.assertEqual(text, message)

if __name__ == '__main__':
    unittest.main()

