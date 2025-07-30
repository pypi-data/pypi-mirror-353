import unittest
from cgbenigma import cgblib

class TestFindCipher(unittest.TestCase):
    def test_cipher(self):
        # Test if the decryption returns the expected result
        decoded = cgblib.find(["FEWGDRHDDEEUMFFTEEMJXZR"], ["BANK"])
        # decoded[1] = {'Key': 'GPV', 'Ring': 'XZR', 'Message': 'OUSTGOVPBANKIZMUBMHUVOG', 'Cipher': 'FEWGDRHDDEEUMFFTEEMJXZR'}
        self.assertEqual(decoded[1]['Key'], "GPV")
        self.assertEqual(decoded[1]['Message'], "OUSTGOVPBANKIZMUBMHUVOG")

if __name__ == '__main__':
    unittest.main()

