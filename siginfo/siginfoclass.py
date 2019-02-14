import sys
import signal
import os
import stat
import atexit

from siginfo.localclass import LocalClass

class SiginfoBasic:
    """
    Base class for the SigInfo module
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
            self.OUTPUT.write('No signal specified')
        self.OUTPUT.flush()           

        # Attempts to use all columns of the current tty window size
        # Falls back to 80 columns by default
        try:
            rows, columns = os.popen('stty size', 'r').read().split()
            self.COLUMNS = max([self.COLUMNS, int(columns)-20])
        except:
            self.COLUMNS = 80

    def create_info_script(self, path=None, prefix='',overwrite=False):
        """
        User convenience function
        Creates an executable file that can be used to trigger the
        registered signals
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

                atexit.register(self.delete_file, filename)


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

    def _call(self, signum, frame):
        """
        Iterates through the stack frames and prints
        all requested frames.
        """
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
    def delete_file(filename):
        """
        used for atexit cleanup
        """
        if os.path.isfile(filename):
            os.remove(filename)



class SigInfoPDB(SiginfoBasic):
    """
    SigInfo class that starts the 
    Python PDB Debugger
    """
    def __call__(self, signum, frame):
        self._call(signum, frame)
        locals = frame.f_locals
        print('Waiting for your command')
        import pdb; pdb.Pdb(nosigint=True).set_trace()

class SigInfoSingle(SiginfoBasic):
    """
    SigInfo class that only returns a single value
    """
    def set_var(self, varname, default=None):
        """
        Defines the variable that should be printed
        """
        self._varname = varname
        self._default = default

    def __call__(self, signum, frame):
        self.OUTPUT.write('{}\n'.format(
            frame.f_locals.get(self._varname, self._default)
        ))
