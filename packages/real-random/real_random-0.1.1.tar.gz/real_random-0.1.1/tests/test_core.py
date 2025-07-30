import unittest
from unittest.mock import patch
from real_random import (
    real_random_int,
    real_random_float,
    real_random_choice,
    real_random_string,
)

class TestRealRandomFunctions(unittest.TestCase):

    @patch("real_random.core.real_random", return_value=0.5)
    def test_real_random_int_midpoint(self, mock_rand):
        self.assertEqual(real_random_int(10, 20), 15)

    @patch("real_random.core.real_random", return_value=0.0)
    def test_real_random_int_lower_bound(self, mock_rand):
        self.assertEqual(real_random_int(5, 5), 5)

    @patch("real_random.core.real_random", return_value=1.0)
    def test_real_random_int_upper_bound(self, mock_rand):
        self.assertEqual(real_random_int(0, 1), 1)

    @patch("real_random.core.real_random", return_value=0.25)
    def test_real_random_float_range(self, mock_rand):
        result = real_random_float(2.0, 6.0)
        self.assertAlmostEqual(result, 3.0)

    @patch("real_random.core.real_random", return_value=0.75)
    def test_real_random_choice(self, mock_rand):
        self.assertEqual(real_random_choice(['a', 'b', 'c', 'd']), 'd')

    @patch("real_random.core.real_random", side_effect=[0.1, 0.5, 0.9])
    def test_real_random_string(self, mock_rand):
        charset = "ABC"
        result = real_random_string(3, charset)
        self.assertEqual(len(result), 3)
        self.assertTrue(all(c in charset for c in result))

    def test_real_random_choice_empty(self):
        with self.assertRaises(ValueError):
            real_random_choice([])


if __name__ == "__main__":
    unittest.main()
