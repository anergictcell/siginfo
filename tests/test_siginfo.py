import unittest
from siginfo import siginfoclass as si
import sys

OLD_OUT = sys.stdout


class MockOutput:
    def __init__(self):
        self.lines = []

    def write(self, line):
        self.lines.append(line)

    def flush(self):
        pass


class MockSignal:
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


class MockClass:
    def __init__(self, attrs):
        for key in attrs:
            self.__setattr__(key, attrs[key])
        self._keys = attrs.keys()

    def __str__(self):
        return 'MockClass: {}'.format(', '.join(
            ['{}={}'.format(key, self.__getattribute__(key)) for key in self._keys]
        ))


class MockFrame:
    def __init__(self, local_vars={}, line_number=0, back=None):
        self.f_locals = local_vars
        self.f_code = MockClass(
            {'co_name': 'my_test_function_line_{}'.format(line_number)}
        )
        self.f_lineno = line_number
        self.f_back = back


class SigInfoInitTests(unittest.TestCase):
    def setUp(self):
        si.sys.stdout = MockOutput()
        si.signal = MockSignal()

    def tearDown(self):
        si.sys.stdout = OLD_OUT

    def test_init(self):
        res = si.SiginfoBasic()
        assert type(res) is si.SiginfoBasic
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


@unittest.skip('Not yet testing calling')
class SiginfoCalling(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
