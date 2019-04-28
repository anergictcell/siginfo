import unittest

from siginfo.utils import left_string


class LeftString(unittest.TestCase):
    def test_trimming(self):
        str_in = '12345'
        str_out = left_string(str_in, 4)
        assert str_out[-3:] == '...'
        assert len(str_out) == 4

    def test_padding(self):
        str_in = '12345'
        str_out = left_string(str_in, 7)
        assert str_out[-3:] == '5  '
        assert len(str_out) == 7

    def test_equal_length(self):
        str_in = '12345'
        str_out = left_string(str_in, 5)
        assert str_out == str_in
        assert len(str_out) == 5


if __name__ == '__main__':
    unittest.main()
