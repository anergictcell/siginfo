import sys
import signal
import os
import stat
import atexit
import subprocess

from siginfo.localclass import LocalClass


class SiginfoBasic:
    """
    Base class for the SigInfo module

    Args
    ----
    info : bool
        Listen for SIGINFO
        Default: True
        (works only on Mac and BSD)
    usr1 : bool
        Listen for SIGUSR1
        Default: True
    usr2 : bool)
        Listen for SIGUSR2
        Default: True
    output : _io.TextIOWrapper
        IO interface for writing output and log.
        Default: sys.stdout


    Attributes
    ----------
    COLUMNS: int
        Width of Terminal (number of columns)
        Default: Auto (Fallback to 80)
    MAX_LEVELS: int
        Number of parent stack frames to display
        Default: 0 (only current frame)

    Returns
    -------
    SigInfoBasic: An instance of the class

    Example
    -------
        ::

            foo = SiginfoBasic()

            # Write up to 120 characters per line
            foo.COLUMNS = 120

            # Write three parent stack frame
            foo.MAX_LEVELS = 3

            # create executeable to send signal to Python script
            foo.create_info_script('/usr/local/bin')

            # Code of your regular Python script
            def read_lines():
                a = 12
                b = 15
                i = 0
                print('Loading a very long file')
                with open('many_rows.txt') as fh:
                    for line in fh:
                        i += 1
                        # print(line)
                        time.sleep(1)
                print('Done loading')

            # Some useless function so we have more stacks
            def main2():
                read_lines()

            def main():
                main2()

            if __name__ == '__main__':
                main()

        In another terminal window:

        .. code-block:: bash

            # send signal via custom script
            /usr/local/bin/siginfo-USR1

            # Output:
            ========================================================================================================================
            LEVEL       0
            METHOD      read_lines
            LINE NUMBER:    33
            ------------------------------------------------------------------------------------------------------------------------
            LOCALS
            VARIABLE | TYPE            | VALUE
            i        | int             | 1
            fh       | TextIOWrapper   | <_io.TextIOWrapper name='many_rows.txt' mode='r' encoding='UTF-8'>
            b        | int             | 15
            a        | int             | 12
            line     | str             | Row 1

            ------------------------------------------------------------------------------------------------------------------------
            SCOPE   <code object read_lines at 0x108c30c90, file "long_script.py", line 24>
            CALLER  <code object main2 at 0x108c309c0, file "long_script.py", line 21>
            ========================================================================================================================

            ========================================================================================================================
            LEVEL       1
            METHOD      main2
            LINE NUMBER:    22
            ------------------------------------------------------------------------------------------------------------------------
            LOCALS
            VARIABLE                                               | TYPE                       | VALUE
            ------------------------------------------------------------------------------------------------------------------------
            SCOPE   <code object main2 at 0x108c309c0, file "long_script.py", line 21>
            CALLER  <code object main at 0x108c30ed0, file "long_script.py", line 18>
            ========================================================================================================================

            ...


    """
    def __init__(self, info=True, usr1=True, usr2=False, output=None):
        self.COLUMNS = 80
        self.MAX_LEVELS = 0  # How many parent stack frames to display
        self.OUTPUT = output or sys.stdout  # where to print the output to
        self.pid = os.getpid()
        self.signals = []

        # Bind SIGINFO if available and requested
        if info:
            if hasattr(signal, 'SIGINFO'):
                signal.signal(signal.SIGINFO, self)
                self.OUTPUT.write('Listening for >>SIGINFO<<\n')
                self.OUTPUT.write('==> kill -s INFO {}\n'.format(self.pid))
                self.signals.append('INFO')
            else:
                self.OUTPUT.write('No SIGINFO availale\n')

        # Bind SIGUSR1 if available and requested
        if usr1:
            if hasattr(signal, 'SIGUSR1'):
                signal.signal(signal.SIGUSR1, self)
                self.OUTPUT.write('Listening for >>SIGUSR1<<\n')
                self.OUTPUT.write('==> kill -s USR1 {}\n'.format(self.pid))
                self.signals.append('USR1')
            else:
                self.OUTPUT.write('No SIGUSR1 availale\n')

        # Bind SIGUSR2 if available and requested
        if usr2:
            if hasattr(signal, 'SIGUSR2'):
                signal.signal(signal.SIGUSR2, self)
                self.OUTPUT.write('Listening for >>SIGUSR2<<\n')
                self.OUTPUT.write('==> kill -s USR2 {}\n'.format(self.pid))
                self.signals.append('USR2')
            else:
                self.OUTPUT.write('No SIGUSR2 availale\n')

        if not info and not usr1 and not usr2:
            self.OUTPUT.write('No signal specified\n')
        self.OUTPUT.flush()

        # Attempts to use all columns of the current tty window size
        # Falls back to 80 columns by default
        try:
            rows, columns = subprocess.check_output(['stty', 'size']).split()
            self.COLUMNS = max([self.COLUMNS, int(columns)-20])
        except Exception:
            self.COLUMNS = 80

    def create_info_script(self, path=None, prefix='', overwrite=False):
        """
        Create an executable on the file system to send the appropiate signal.

        For user convenience, create executable filess in the specified path
        that can be used to send corresponding signals to the parent's script.

        Args
        ----
        path : str
            path to executable files (default $HOME)
        prefix : str
            Prefix of the executable file name (default '')
        overwrite : bool
            Overwrite existing executables (default False)

        Returns
        ------
        None

        """
        if path is None:
            path = os.path.expanduser('~')
        for sig in self.signals:
            filename = os.path.abspath(
                os.path.join(
                    path,
                    '{}siginfo-{}'.format(prefix, sig)
                )
            )
            if not os.path.isfile(filename) or overwrite:
                with open(filename, 'w') as fh:
                    fh.write('#!/bin/sh\n')
                    fh.write('kill -s {} {}'.format(sig, self.pid))
                os.chmod(filename, os.stat(filename).st_mode | stat.S_IEXEC)

                atexit.register(self._delete_file, filename)

    def _print_frame(self, frame):
        """
        Formats and prints the frame output
        in a somewhat tabbular format
        """
        local_vars = LocalClass(frame.f_locals, self.COLUMNS)
        self.OUTPUT.write('METHOD\t\t{}\n'.format(frame.f_code.co_name))
        self.OUTPUT.write('LINE NUMBER:\t{}\n'.format(frame.f_lineno))
        self.OUTPUT.write('-'*self.COLUMNS)
        self.OUTPUT.write('\n')
        self.OUTPUT.write('LOCALS\n')
        self.OUTPUT.write(str(local_vars))
        self.OUTPUT.write('\n')
        self.OUTPUT.write('-'*self.COLUMNS)
        self.OUTPUT.write('\n')
        self.OUTPUT.write('SCOPE\t')
        self.OUTPUT.write(str(frame.f_code))
        self.OUTPUT.write('\n')
        self.OUTPUT.write('CALLER\t')
        if frame.f_back:
            self.OUTPUT.write(str(frame.f_back.f_code))
        else:
            self.OUTPUT.write('NONE')
        self.OUTPUT.write('\n')

    # Print all stack frames
    # callback for signal.signal
    def _call(self, signum, frame):
        depth = self.MAX_LEVELS or 1000
        self.OUTPUT.write('\n')
        self.OUTPUT.write(type(self).__name__)
        self.OUTPUT.write('\n')

        for i in range(depth):
            if frame:
                self.OUTPUT.write('\n')
                self.OUTPUT.write('='*self.COLUMNS)
                self.OUTPUT.write('\n')
                self.OUTPUT.write('LEVEL    \t{}\n'.format(i))
                self._print_frame(frame)
                self.OUTPUT.write('='*self.COLUMNS)
                self.OUTPUT.write('\n')
                self.OUTPUT.flush()
                frame = frame.f_back
            else:
                self.OUTPUT.flush()
                break

    __call__ = _call

    @staticmethod
    def _delete_file(filename):
        """
        used for atexit cleanup
        """
        if os.path.isfile(filename):
            os.remove(filename)


class SigInfoPDB(SiginfoBasic):
    """
    SigInfo class that starts the Python PDB Debugger

    Instead of printing out the call stack, it allows to
    interactively inspect the current frame via PDB Debugger.

    Local variables from current frame are avaialable via the  ``_locals`` dict.

    Example
    -------
        ::

            foo = SigInfoPDB()
            do_long_task()

            # create executeable to send signal to Python script
            foo.create_info_script('/usr/local/bin')

        Now get access to PDB debugger in another terminal window:

        .. code-block:: bash

            # send signal via custom script
            /usr/local/bin/siginfo-USR1

    """

    # Start the PDB Debugger
    def __call__(self, signum, frame):
        self._call(signum, frame)
        _locals = frame.f_locals
        print('Waiting for your command')
        import pdb; pdb.Pdb(nosigint=True).set_trace()


class SigInfoSingle(SiginfoBasic):
    """
    SigInfo class that only returns a single value

    Example
    -------
        ::

            # create signal listener
            foo = SigInfoSingle(usr1=True)

            # define which variable to print
            foo.set_var('i')

            # create executeable to send signal to Python script
            foo.create_info_script('/usr/local/bin')

            # run your regular code
            for n in seq(1, 100):
                do_long_task(i=n)

        In another terminal window:

        .. code-block:: bash

            # send signal via custom script
            /usr/local/bin/siginfo-USR1

            # Output:
            4


    """
    def set_var(self, varname, default=None):
        """
        Defines the variable that should be printed

        Args
        ----
        varname : str
            Name of variable from stack frame that should be printed
        default
            Backup value to print if ``varname`` is not present in local
            stack frame.
            Default: None

        Returns
        -------
        None
        """
        self._varname = varname
        self._default = default

    # Print value of set variable
    def __call__(self, signum, frame):
        if self._varname:
            self.OUTPUT.write('{}\n'.format(
                frame.f_locals.get(self._varname, self._default)
            ))
