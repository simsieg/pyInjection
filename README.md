# pyInjection

pyInjection uses various heuristics to look for SQL injection vulnerabilities in python source code.

Based on https://github.com/uber/py-find-injection.


# Usage
```
$ python bin/pyInjection.py --help
usage: pyInjection.py [-h] [-v] [-i INPUT] [-j] [-s] [-q] [files [files ...]]

Look for patterns in python source files that might indicate SQL injection or
other vulnerabilities

positional arguments:
  files                 files to check or '-' for standard in

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -i INPUT, --input INPUT
                        path to a file containing a list of files to check,
                        each file in a line
  -j, --json            print output in JSON
  -s, --stdin           read from standard in, passed files are ignored
  -q, --quiet           do not print error statistics

Exit status is 0 if all files are okay, 1 if any files have an error. Found
vulnerabilities are printed to standard out
```
