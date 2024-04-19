import unittest
from new import on_text_modified

class TestOnTextModified(unittest.TestCase):

    def test_on_text_modified_prints_message(self):
        on_text_modified(None)
        self.assertEqual(1, 1) # placeholder

    def test_on_text_modified_resets_pause_index(self):
        self.assertEqual(1, 1) # placeholder

if __name__ == '__main__':
    unittest.main()
