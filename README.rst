*******
siginfo
*******

``siginfo`` is a small Python module to conveniently get status or debug info from running Python processes.


``siginfo`` listens for ``SIGUSR1`` or ``SIGUSR2`` [#f1]_ signals and prints info about the current callstack, local variables etc.


Use cases
=========
You have long running Python processes and want to check in on progress, but don't want to print the progress all the time.
This is especially useful for I/O heavy operations.

Imagine you're reading in a large file and work on it line by line. Instead of printing the line-number in regular intervals, you can simply send a SIGUSR command from another shell session and see the current callstack or start an interactive debugger. 


How to
======

Simply add the following two lines:

.. code:: python

    from siginfo import SiginfoBasic
    SiginfoBasic()

to your python script. Once your application is running, you can always check the current callstack from another shell session by sending a SIGUSR signal.

.. code:: bash

    kill -SIGUSR1 ${pid}


It will now print the current callstack with basic information about all local variables to stdout (or a predefined file).

.. code-block:: bash

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
    VARIABLE    | TYPE    | VALUE
    ------------------------------------------------------------------------------------------------------------------------
    SCOPE   <code object main2 at 0x108c309c0, file "long_script.py", line 21>
    CALLER  <code object main at 0x108c30ed0, file "long_script.py", line 18>
    ========================================================================================================================

    ...


Installation
============
I want to add this to pypy, but not yet done. Clone the git repo and create a symlink from your python script folder to the ``signint`` folder.

.. code:: bash

    ln -s ./siginfo <PATH_TO_SIGINFO_REPO>/siginfo


Usage
=====

Include ``siginfo`` in your python script

.. code:: python

    import siginfo


Initialize SignInfo Class
-------------------------

.. code:: python

    siginfo.SiginfoBasic()



Basic overview
==============

``siginfo`` contains the following classes:

- ``SiginfoBasic`` Print info about the current stack (and caller stacks). Regular execution continues automatically.
- ``SigInfoPDB`` Open the ``PDB`` debugger. Pauses script execution until debugger is exited.
- ``SigInfoSingle`` Print the value of a single variable of the current scope. Continues regular execution automatically.


Initiating the class
--------------------

All class allow the following arguments:

- ``info`` Listen for ``SIGNFO`` (Default: ``True``) (only on Mac and BSD)
- ``usr1`` Listen for ``SIGUSR1`` (Default: ``True``)
- ``usr2`` Listen for ``SIGUSR2`` (Default: ``False``)
- ``output`` Where to write the output to (Default: ``sys.stdout``). Can be anything that offers a ``write`` function.


.. code:: python

    from siginfo import SiginfoBasic
    SiginfoBasic(info=True, usr1=False)  # listen only for SIGINFO
    SiginfoBasic(info=False, usr=True)  # listen only for SIGUSR1
    SiginfoBasic(output=open('mylog.log', 'a'))  # Write call stack output to a log file



``signinfo`` class instance attributes
--------------------------------------

- ``COLUMNS``: Maximum width of the Terminal (or max number of rows per line in an output file) (Default: current tty columns - 20; Fallback to 80 if determination isn't possible)
- ``MAX_LEVELS``: Number of stack frames to print (Default: 1 [only the current one])
- ``OUTPUT``: Same as ``output`` argument to the constructor function. Defines where to write the output to (Default: ``sys.stdout``)

.. code:: python

    from siginfo import SiginfoBasic
    info_handler = SiginfoBasic()

    info_handler.COLUMNS = 200  # Format output to match 200 columns
    info_handler.MAX_LEVELS = 4  # Print the current frame + 3 parent frames
    info_handler.OUTPUT = open('mylog.log', 'a')  # write the output to mylog.log


API docs
========
For a more detailed API description, check out `the full documentation`_ 

.. _the full documentation: https://esbme.com/siginfo/docs/


.. rubric:: Footnotes

.. [#f1] In addition, on MacOS or BSD system, the ``SIGINFO`` signal can be used as well.