import unittest
from src.op_parser.iaga_parser import IAGA2002Parser

class TestIAGA2002Parser(unittest.TestCase):
    def setUp(self):
        # Пример строк, имитирующих содержимое файла IAGA-2002
        self.sample_lines = [
            "# This is a comment line",
            "# Another comment",
            "DATE TIME X Y Z",
            "2025-06-05 00:00:00 12345 23456 34567",
            "2025-06-05 00:01:00 12350 23460 34570"
        ]
        self.parser = IAGA2002Parser()

    def test_parse_lines(self):
        records, headers = self.parser.parse_lines(self.sample_lines)
        self.assertEqual(headers, ['DATE', 'TIME', 'X', 'Y', 'Z'])
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]['DATE'], '2025-06-05')
        self.assertEqual(records[1]['TIME'], '00:01:00')


if __name__ == '__main__':
    unittest.main()
