import unittest

from siginfo.localclass import LocalClass


class LocalTest(unittest.TestCase):
    def test_init(self):
        my_locals = {
            'a': '12',
            'b': 'a string',
            'c': {'foo': 'bar'}
        }
        res = LocalClass(my_locals)
        assert type(res) is LocalClass
        assert len(res.types) == 4
        assert len(res.values) == 4
        assert len(res.var_names) == 4
        for key in my_locals:
            assert type(my_locals[key]).__name__ in res.types
        for idx, key in enumerate(res.var_names):
            if idx == 0:
                continue
            assert str(res.values[idx]) == str(my_locals[key])

    def test_max_width(self):
        pass


if __name__ == '__main__':
    unittest.main()
