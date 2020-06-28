import unittest
from siginfo import siginfoclass as si
import sys

OLD_OUT = sys.stdout


class MockOutput(object):
    def __init__(self):
        self.lines = []

    def write(self, line):
        self.lines.append(line)

    def flush(self):
        pass


class MockSignal(object):
    def __init__(self, info=True, usr1=True, usr2=True):
        if info:
            self.SIGINFO = 1
        if usr1:
            self.SIGUSR1 = 2
        if usr2:
            self.SIGUSR2 = 3
        self.signals = []

    def signal(self, sigtype, func):
        self.signals.append((sigtype, func))


class MockClass(object):
    def __init__(self, attrs):
        for key in attrs:
            self.__setattr__(key, attrs[key])
        self._keys = attrs.keys()

    def __str__(self):
        return 'MockClass: {}'.format(', '.join(
            ['{}={}'.format(key, self.__getattribute__(key)) for key in self._keys]
        ))


class MockFrame(object):
    def __init__(self, local_vars={}, line_number=0, back=None):
        self.f_locals = local_vars
        self.f_code = MockClass(
            {'co_name': 'my_test_function_line_{}'.format(line_number)}
        )
        self.f_lineno = line_number
        self.f_back = back


class MockFunction(object):
    def __init__(self):
        self.called = 0
        self.called_with = []

    def __call__(self, *args, **kwargs):
        self.called += 1
        self.called_with.append((args, kwargs))


class SigInfoInitTests(unittest.TestCase):
    def setUp(self):
        si.sys.stdout = MockOutput()
        si.signal = MockSignal()

    def tearDown(self):
        si.sys.stdout = OLD_OUT

    def test_init(self):
        res = si.SiginfoBasic()
        assert isinstance(res, si.SiginfoBasic)
        assert isinstance(res.pid, int)
        assert isinstance(res.MAX_LEVELS, int)
        assert isinstance(res.COLUMNS, int)
        assert isinstance(res.OUTPUT, MockOutput)

    def test_output(self):
        si.sys.stdout.lines = []
        si.SiginfoBasic(info=True, usr1=True, usr2=True)
        assert len(si.sys.stdout.lines) == 6


class SigInfoInputTests(unittest.TestCase):
    def setUp(self):
        si.sys.stdout = MockOutput()

    def tearDown(self):
        si.sys.stdout = OLD_OUT

    def test_inputs(self):
        si.signal = MockSignal()
        res = si.SiginfoBasic(info=True, usr1=True, usr2=True)
        assert res.signals == ['INFO', 'USR1', 'USR2']

        res = si.SiginfoBasic(info=True, usr1=True, usr2=False)
        assert res.signals == ['INFO', 'USR1']

        res = si.SiginfoBasic(info=True, usr1=False, usr2=False)
        assert res.signals == ['INFO']

        res = si.SiginfoBasic(info=True, usr1=False, usr2=True)
        assert res.signals == ['INFO', 'USR2']

        res = si.SiginfoBasic(info=False, usr1=True, usr2=True)
        assert res.signals == ['USR1', 'USR2']

        si.sys.stdout.lines = []
        res = si.SiginfoBasic(info=False, usr1=False, usr2=False)
        assert res.signals == []
        assert si.sys.stdout.lines[0] == 'No signal specified\n'

    def test_inexistent_inputs(self):
        si.sys.stdout.lines = []
        si.signal = MockSignal(info=False)
        res = si.SiginfoBasic(info=True, usr1=True, usr2=True)
        assert res.signals == ['USR1', 'USR2']
        assert 'No SIGINFO availale\n' == si.sys.stdout.lines[0]

    def test_all_missing_inputs(self):
        si.sys.stdout.lines = []
        si.signal = MockSignal(info=False, usr1=False, usr2=False)
        res = si.SiginfoBasic(info=True, usr1=True, usr2=True)
        assert res.signals == []
        assert 'No SIGINFO availale\n' == si.sys.stdout.lines[0]
        assert 'No SIGUSR1 availale\n' == si.sys.stdout.lines[1]
        assert 'No SIGUSR2 availale\n' == si.sys.stdout.lines[2]


class SigInfoSigFormattingTests(unittest.TestCase):
    def test_column_specification(self):
        si.subprocess.check_output = lambda x: '5 140'
        res = si.SiginfoBasic(
            info=False,
            usr1=False,
            usr2=False,
            output=MockOutput())
        assert res.COLUMNS == 120

        # Defaulting to minimum of 80 colunns
        si.subprocess.check_output = lambda x: '5 79'
        res = si.SiginfoBasic(
            info=False,
            usr1=False,
            usr2=False,
            output=MockOutput())
        assert res.COLUMNS == 80

        # Defaulting to minimum of 80 colunns
        si.subprocess.check_output = lambda x: '5 81'
        res = si.SiginfoBasic(
            info=False,
            usr1=False,
            usr2=False,
            output=MockOutput())
        assert res.COLUMNS == 80

        # Defaulting to minimum of 80 colunns
        si.subprocess.check_output = lambda x: '5 101'
        res = si.SiginfoBasic(
            info=False,
            usr1=False,
            usr2=False,
            output=MockOutput())
        assert res.COLUMNS == 81

        # this will cause the check_output to fail
        si.subprocess.check_output = lambda x: 1
        res = si.SiginfoBasic(
            info=False,
            usr1=False,
            usr2=False,
            output=MockOutput())
        assert res.COLUMNS == 80


@unittest.skip('Not yet testing script generation')
class SigInfoSigScriptTests(unittest.TestCase):

    def test_create_info_script(self):
        pass

    def test_make_scripts_excecutable(self):
        pass

    def test_script_pids(self):
        pass


class SiginfoFramePrinting(unittest.TestCase):
    def test_print_without_parent(self):
        si.subprocess.check_output = lambda x: '5 80'
        mock_out = MockOutput()
        mock_frame = MockFrame()
        res = si.SiginfoBasic(
            info=False,
            usr1=False,
            usr2=False,
            output=mock_out)

        res._print_frame(mock_frame)
        assert len(mock_out.lines) == 16, mock_out.lines
        assert mock_out.lines[1] == 'METHOD\t\tmy_test_function_line_0\n'
        assert mock_out.lines[2] == 'LINE NUMBER:\t0\n'
        assert mock_out.lines[3] == '-'*80
        assert mock_out.lines[5] == 'LOCALS\n'
        assert mock_out.lines[10] == 'SCOPE\t'
        assert mock_out.lines[11] == 'MockClass: co_name=my_test_function_line_0'
        assert mock_out.lines[13] == 'CALLER\t'
        assert mock_out.lines[14] == 'NONE'

    def test_print_with_parent(self):
        si.subprocess.check_output = lambda x: '5 80'
        mock_out = MockOutput()
        mock_frame = MockFrame(back=MockFrame(line_number=2))
        res = si.SiginfoBasic(
            info=False,
            usr1=False,
            usr2=False,
            output=mock_out)

        res._print_frame(mock_frame)
        assert len(mock_out.lines) == 16, mock_out.lines
        assert mock_out.lines[1] == 'METHOD\t\tmy_test_function_line_0\n'
        assert mock_out.lines[2] == 'LINE NUMBER:\t0\n'
        assert mock_out.lines[3] == '-'*80
        assert mock_out.lines[5] == 'LOCALS\n'
        assert mock_out.lines[10] == 'SCOPE\t'
        assert mock_out.lines[11] == 'MockClass: co_name=my_test_function_line_0'
        assert mock_out.lines[13] == 'CALLER\t'
        assert mock_out.lines[14] == 'MockClass: co_name=my_test_function_line_2'


class SiginfoCalling(unittest.TestCase):
    def test_signal_calling(self):
        si.subprocess.check_output = lambda x: '5 80'
        mock_out = MockOutput()
        mock_frame = MockFrame()
        res = si.SiginfoBasic(
            info=False,
            usr1=False,
            usr2=False,
            output=mock_out)

        res._print_frame = MockFunction()

        res(1, mock_frame)

        assert len(mock_out.lines) == 10
        assert res._print_frame.called == 1
        assert res._print_frame.called_with[0][0][0] == mock_frame

    def test_signal_calling_multiple_level(self):
        si.subprocess.check_output = lambda x: '5 80'
        mock_out = MockOutput()
        mock_frame_back = MockFrame(line_number=2)
        mock_frame = MockFrame(back=mock_frame_back)
        res = si.SiginfoBasic(
            info=False,
            usr1=False,
            usr2=False,
            output=mock_out)

        res._print_frame = MockFunction()

        res(1, mock_frame)

        assert len(mock_out.lines) == 16
        assert res._print_frame.called == 2
        assert res._print_frame.called_with[0][0][0] == mock_frame
        assert res._print_frame.called_with[1][0][0] == mock_frame_back

    def test_signal_calling_limit_levels(self):
        """
        2 levels of stack frames are present
        but MAX_LEVELS is set to 1
        """
        si.subprocess.check_output = lambda x: '5 80'
        mock_out = MockOutput()
        mock_frame_back = MockFrame(line_number=2)
        mock_frame = MockFrame(back=mock_frame_back)
        res = si.SiginfoBasic(
            info=False,
            usr1=False,
            usr2=False,
            output=mock_out)
        res.MAX_LEVELS = 1

        res._print_frame = MockFunction()

        res(1, mock_frame)

        assert len(mock_out.lines) == 10
        assert res._print_frame.called == 1
        assert res._print_frame.called_with[0][0][0] == mock_frame


class SiginfoSingleCalling(unittest.TestCase):
    def test_setting_variables(self):
        mock_out = MockOutput()
        res = si.SigInfoSingle(
            info=False,
            usr1=False,
            usr2=False,
            output=mock_out)
        res.set_var('foo')

        assert res._varname == 'foo'
        assert res._default is None

    def test_getting_existing_variables(self):
        mock_out = MockOutput()
        mock_frame = MockFrame({'foo': '12', 'bar': 'abc'})
        res = si.SigInfoSingle(
            info=False,
            usr1=False,
            usr2=False,
            output=mock_out)
        res.set_var('foo')

        mock_out.lines = []
        res(1, mock_frame)

        assert len(mock_out.lines) == 1
        assert mock_out.lines[0] == '12\n'

    def test_getting_nonexisting_variables(self):
        mock_out = MockOutput()
        mock_frame = MockFrame({'foo': '12', 'bar': 'abc'})
        res = si.SigInfoSingle(
            info=False,
            usr1=False,
            usr2=False,
            output=mock_out)
        res.set_var('xyz', 'foobar')

        mock_out.lines = []
        res(1, mock_frame)

        assert len(mock_out.lines) == 1
        assert mock_out.lines[0] == 'foobar\n'


if __name__ == '__main__':
    unittest.main()
