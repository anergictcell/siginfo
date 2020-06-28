import unittest

from siginfo.localclass import LocalClass


class LocalTest(unittest.TestCase):
    def test_init(self):
        my_locals = {
            'a': 12,
            'b': 'a string',
            'c': {'foo': 'bar'}
        }
        res = LocalClass(my_locals)
        assert isinstance(res, LocalClass), (res, type(res))
        assert len(res.types) == 4
        assert len(res.values) == 4
        assert len(res.var_names) == 4
        for key in my_locals:
            assert type(my_locals[key]).__name__ in res.types
        for idx, key in enumerate(res.var_names):
            if idx == 0:
                # skip the header
                continue
            # Check that the values are identical
            assert str(res.values[idx]) == str(my_locals[key])
            # Check that types are corretly printed
            # We can't use isinstance, we have to compare the strings
            assert res.types[idx] == type(my_locals[key]).__name__  # noqa: E721

    def test_max_width(self):
        loc = LocalClass({'xyz:': 123})
        assert (loc.MAX_KEY+loc.MAX_TYPE+loc.MAX_VALUES+6) <= 80

        loc = LocalClass({'xyz:': 123}, 100)
        assert (loc.MAX_KEY+loc.MAX_TYPE+loc.MAX_VALUES+6) <= 100

        loc = LocalClass({'xyz:': 123}, 20)
        assert (loc.MAX_KEY+loc.MAX_TYPE+loc.MAX_VALUES+6) <= 20

    def test_private_scaling(self):
        loc = LocalClass({'xyz:': 123})
        assert loc.MAX_KEY == 35
        assert loc.MAX_TYPE == 16
        assert loc.MAX_VALUES == 21

        loc._scale_columns(100)
        assert loc.MAX_KEY == 45
        assert loc.MAX_TYPE == 21
        assert loc.MAX_VALUES == 27

        loc._scale_columns(20)
        assert loc.MAX_KEY == 7
        assert loc.MAX_TYPE == 2
        assert loc.MAX_VALUES == 3

    def test_private_add_header(self):
        loc = LocalClass({'xyz:': 123})
        assert loc.var_names[0] == 'VARIABLE'
        assert loc.var_names[1] == 'xyz:'
        assert loc.types[0] == 'TYPE'
        assert loc.types[1] == 'int'
        assert loc.values[0] == 'VALUE'
        assert loc.values[1] == '123'

        loc._add_headers()
        assert loc.var_names[0] == 'VARIABLE'
        assert loc.var_names[1] == 'VARIABLE'
        assert loc.var_names[2] == 'xyz:'
        assert loc.types[0] == 'TYPE'
        assert loc.types[1] == 'TYPE'
        assert loc.types[2] == 'int'
        assert loc.values[0] == 'VALUE'
        assert loc.values[1] == 'VALUE'
        assert loc.values[2] == '123'

    def test_private_make_row(self):
        loc = LocalClass({'xyz:': 123})
        res = loc._make_row('foo', 'bar', 'foobar')
        assert res == 'foo{sp1}| bar{sp2}| foobar{sp3}'.format(
            sp1=' '*33,
            sp2=' '*14,
            sp3=' '*15
        )

    def test_stringify(self):
        loc = LocalClass({'xyz:': 123})
        res = str(loc)
        rows = res.split('\n')
        assert 'VARIABLE' in rows[0]
        assert 'TYPE' in rows[0]
        assert 'VALUE' in rows[0]

        assert 'xyz:' in rows[1]
        assert '| int' in rows[1]
        assert '| 123' in rows[1]


if __name__ == '__main__':
    unittest.main()
