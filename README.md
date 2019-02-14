# siginfo

A module to conveniently get status or debug info from running Python scripts.

<code>siginfo</code> listens for <code>SIGUSR1</code> or <code>SIGUSR2</code>[1] signals and prints info about the current callstack, local variables etc.

## Use cases
Imagine you work line by line on a very large file (Something that happens quite frequenly in Bioinformatics) and you want to see the progress of your program without printing status of each line to <code>STDOUT</code>.<br>
Simply add the following two lines:

```python
from siginfo import SiginfoBasic
SiginfoBasic()
```

Now, run your script and send a <code>SIGUSR1</code> signal to the running process.
```bash
kill -SIGUSR1 ${pid}
```

![image](https://user-images.githubusercontent.com/875703/52584898-a18b9500-2e33-11e9-9d9c-ba2539f3dfb2.png)

*[1]: In addition, on MacOS or BSD system, the <code>SIGINFO</code> signal can be used as well.*

## Installation
Not yet done. Clone the git repo and create a symlink from your python script folder to the <code>signint</code> folder.
```bash
ln -s ./siginfo <PATH_TO_SIGINFO_REPO>/siginfo
```

## Usage
Include <code>siginfo</code> in your python script
```python
import siginfo
```

### General <code>signinfo</code> classes
<code>siginfo</code> contains the following classes:
- <code>SiginfoBasic</code> Print info about the current stack (and caller stacks). Regular execution continues automatically.
- <code>SigInfoPDB</code> Open the <code>PDB</code> debugger. Pauses script execution until debugger is exited.
- <code>SigInfoSingle</code> Print the value of a single variable of the current scope. Continues regular execution automatically.

#### Initiating the class
All class allow the following arguments:
- <code>info</code> Listen for <code>SIGNFO</code> (Default: <code>True</code>) (only on Mac and BSD)
- <code>usr1</code> Listen for <code>SIGUSR1</code> (Default: <code>True</code>)
- <code>usr2</code> Listen for <code>SIGUSR2</code> (Default: <code>False</code>)
- <code>output</code> Where to write the output to (Default: <code>sys.stdout</code>). Can be anything that offers a <code>write</code> function.

```python
from siginfo import SiginfoBasic
SiginfoBasic(info=True, usr1=False)  # listen only for SIGINFO
SiginfoBasic(info=False, usr=True)  # listen only for SIGUSR1
SiginfoBasic(output=open('mylog.log', 'a'))  # Write call stack output to a log file
```

#### <code>signinfo</code> class instance attributes
- <code>COLUMNS</code>: Maximum width of the Terminal (or max number of rows per line in an output file) (Default: current tty columns - 20; Fallback to 80 if determination isn't possible)
- <code>MAX_LEVELS</code>: Number of stack frames to print (Default: 1 [only the current one])
- <code>OUTPUT</code>: Same as <code>output</code> argument to the constructor function. Defines where to write the output to (Default: <code>sys.stdout</code>)

```python
from siginfo import SiginfoBasic
info_handler = SiginfoBasic()

info_handler.COLUMNS = 200  # Format output to match 200 columns
info_handler.MAX_LEVELS = 4  # Print the current frame + 3 parent frames
info_handler.OUTPUT = open('mylog.log', 'a')  # write the output to mylog.log
```

#### <code>SiginfoBasic</code>

This class prints out the current stack and let's the program continue automatically. You can also print out the caller and the caller's caller etc.
