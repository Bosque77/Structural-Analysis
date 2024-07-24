import re
import unittest
from scale_loadcases import scale_loadcases

# Tests
class TestScaleLoadcases(unittest.TestCase):
    def test_basic_scaling(self):
        loadcases = [
            "1 LoadCase_A 1.5 (101) + 2.0 (102) - 3.0 (103)",
            "2 LoadCase_B 0.5 (104) + 1.0 (105)"
        ]
        expected = [
            "1 LoadCase_A 3.00 (101) + 2.00 (102) - 6.00 (103)",
            "2 LoadCase_B 1.00 (104) + 1.00 (105)"
        ]
        result = scale_loadcases(loadcases, 2, [102, 105])
        self.assertEqual(result, expected)

    def test_negative_scaling(self):
        loadcases = [
            "1 LoadCase_A 1.5 (101) + 2.0 (102) - 3.0 (103)",
            "2 LoadCase_B 0.5 (104) + 1.0 (105)"
        ]
        expected = [
            "1 LoadCase_A 0.75 (101) + 2.00 (102) - 1.50 (103)",
            "2 LoadCase_B 0.25 (104) + 1.00 (105)"
        ]
        result = scale_loadcases(loadcases, -0.5, [102, 105])
        self.assertEqual(result, expected)

    def test_all_lcid_not_to_change(self):
        loadcases = [
            "1 LoadCase_A 1.5 (101) + 2.0 (102) - 3.0 (103)",
            "2 LoadCase_B 0.5 (104) + 1.0 (105)"
        ]
        expected = [
            "1 LoadCase_A 1.50 (101) + 2.00 (102) - 3.00 (103)",
            "2 LoadCase_B 0.50 (104) + 1.00 (105)"
        ]
        result = scale_loadcases(loadcases, 2, [101, 102, 103, 104, 105])
        self.assertEqual(result, expected)

    def test_no_lcid_not_to_change(self):
        loadcases = [
            "1 LoadCase_A 1.5 (101) + 2.0 (102) - 3.0 (103)",
            "2 LoadCase_B 0.5 (104) + 1.0 (105)"
        ]
        expected = [
            "1 LoadCase_A 3.00 (101) + 4.00 (102) - 6.00 (103)",
            "2 LoadCase_B 1.00 (104) + 2.00 (105)"
        ]
        result = scale_loadcases(loadcases, 2, [])
        self.assertEqual(result, expected)

    def test_mixed_sign_scaling(self):
        loadcases = [
            "1 LoadCase_A 1.5 (101) - 2.00 (102) - 3.0 (103)",
            "2 LoadCase_B -0.5 (104) + 1.0 (105)"
        ]
        expected = [
            "1 LoadCase_A -0.75 (101) - 2.00 (102) - 1.50 (103)",
            "2 LoadCase_B -0.25 (104) + 1.00 (105)"
        ]
        result = scale_loadcases(loadcases, -0.5, [102, 105])
        self.assertEqual(result, expected)

    def test_varied_loadcase_format(self):
        loadcases = [
            "1 LoadCase_A 1.5 (101)",
            "2 LoadCase_B 0.5 (104) + 1.0 (105) - 2.0 (106)",
            "3 LoadCase_C 2.5 (107) - 1.5 (108) + 4.0 (109)"
        ]
        expected = [
            "1 LoadCase_A 0.75 (101)",
            "2 LoadCase_B 0.25 (104) + 1.00 (105) - 1.00 (106)",
            "3 LoadCase_C 1.25 (107) - 0.75 (108) + 2.00 (109)"
        ]
        result = scale_loadcases(loadcases, -0.5, [105])
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)