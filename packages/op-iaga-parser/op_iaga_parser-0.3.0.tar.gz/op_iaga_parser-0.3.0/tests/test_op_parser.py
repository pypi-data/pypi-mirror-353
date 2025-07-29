import unittest
from src.op_parser.op_parser import OpFileParser

class TestParser(unittest.TestCase):
    def test_parse_lines_basic(self):
        data = [
            "DATE TIME TEMP",
            "20250101 0000 32",
            "20250101 0100 50"
        ]
        parser = OpFileParser()
        records = parser.parse_lines(data)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]['TEMP'], '32')

    def test_parse_with_conversion(self):
        field_converters = {
            'TEMP': [float]
        }
        parser = OpFileParser(field_converters=field_converters, apply_conversion=True)
        data = [
            "DATE TIME TEMP",
            "20250101 0000 32.5",
            "20250101 0100 50.1"
        ]
        records = parser.parse_lines(data)
        self.assertIsInstance(records[0]['TEMP'], float)
        self.assertAlmostEqual(records[0]['TEMP'], 32.5)

    def test_parse_skip_conversion(self):
        field_converters = {
            'TEMP': [float]
        }
        parser = OpFileParser(field_converters=field_converters, apply_conversion=False)
        data = [
            "DATE TIME TEMP",
            "20250101 0000 32.5",
            "20250101 0100 50.1"
        ]
        records = parser.parse_lines(data)
        self.assertIsInstance(records[0]['TEMP'], str)
        self.assertEqual(records[0]['TEMP'], '32.5')
