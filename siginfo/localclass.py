import math

from siginfo.utils import left_string


class LocalClass:
    """
    Formats the ``locale`` object for display in the tty.

    Can handle any kind  of object to format it in a

    +-----+------+-------+
    | KEY | TYPE | VALUE |
    +-----+------+-------+

    like table

    Args
    ----
    local_vars : object
        Object to display in table. key will be one row
    columns : int
        Width (in columns) of the output stream. Default: 80

    """
    def __init__(self, local_vars, columns=80):
        self.var_names = list(local_vars.keys())
        self.types = [type(local_vars[key]).__name__ for key in self.var_names]
        self.values = [str(local_vars[key]) for key in self.var_names]

        self._add_headers()

        self._scale_columns(columns)

    def _scale_columns(self, columns):
        """
        Adjusts the total width of all three columns
        to match the max column width available
        """
        cur_max_key = max(len(val) for val in self.var_names)
        cur_max_type = max(len(val) for val in self.types)
        cur_max_value = max(len(val) for val in self.values)

        cur = cur_max_key + cur_max_type + cur_max_value
        factor = float(columns) / float(cur)
        self.MAX_KEY = math.floor(factor * cur_max_key) - 2
        self.MAX_TYPE = math.floor(factor * cur_max_type) - 2
        self.MAX_VALUES = math.floor(factor * cur_max_value) - 2

    def _add_headers(self):
        self.var_names.insert(0, 'VARIABLE')
        self.types.insert(0, 'TYPE')
        self.values.insert(0, 'VALUE')

    def _make_row(self, key, tp, val):
        return '{key} | {tp} | {val}'.format(
            key=left_string(key, self.MAX_KEY),
            tp=left_string(tp, self.MAX_TYPE),
            val=left_string(val, self.MAX_VALUES)
            )

    def __str__(self):
        res = []
        for idx, key in enumerate(self.var_names):
            res.append(
                self._make_row(key, self.types[idx], self.values[idx])
            )
        return '\n'.join(res)
