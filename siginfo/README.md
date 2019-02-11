# SigINFO

A module to conveniently get status or debug info from running Python scripts.

<code>SigINFO</code> listens for <code>SIGUSR1</code> or <code>SIGUSR2</code>[1] signals and prints info about the current callstack, local variables etc.

## Use cases
Imagine you work line by line on a very large file (Something that happens quite frequenly in Bioinformatics) and you want to see the progress of your program without printing status of each line to <code>STDOUT</code>.<br>
Simply add the following two lines:


## Usage
```python
from siginfo import SiginfoBasic
SiginfoBasic()
```

Now, run your script and send a <code>SIGUSR1</code> signal to the running process.
```bash
kill -SIGUSR1 ${pid}
```


*[1]: In addition, on MacOS or BSD system, the <code>SIGINFO</code> signal can be used as well.*
