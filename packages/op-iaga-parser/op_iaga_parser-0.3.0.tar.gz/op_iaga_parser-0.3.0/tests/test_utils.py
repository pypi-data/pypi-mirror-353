import unittest
from src.op_parser.utils import safe_float, f_to_c, convert_value

class TestUtils(unittest.TestCase):
    def test_safe_float_valid(self):
        self.assertEqual(safe_float('10.5'), 10.5)

    def test_safe_float_invalid(self):
        self.assertIsNone(safe_float('abc'))

    def test_f_to_c_conversion(self):
        self.assertAlmostEqual(f_to_c(32), 0)
        self.assertEqual(f_to_c(''), '')

    def test_convert_value_apply(self):
        val = '100'
        res = convert_value(val, converters=[safe_float, f_to_c], apply_conversion=True)
        self.assertAlmostEqual(res, 37.78)

    def test_convert_value_skip(self):
        val = '100'
        res = convert_value(val, converters=[safe_float, f_to_c], apply_conversion=False)
        self.assertEqual(res, '100')
