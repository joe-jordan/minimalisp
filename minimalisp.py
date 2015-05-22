#! /usr/bin/env python
# If you get an import error here, please use python >= 2.6 .
from __future__ import print_function

import os.path

from parse import parse_program
from values import NIL
from vm import run, LispRuntimeError

STDLIB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "stdlib.l")

if __name__ == "__main__":
    import pycatch
    pycatch.enable(ipython=True)

    import sys
    parse_only = '-p' in sys.argv
    use_stdlib = '-l' in sys.argv

    possible_fn = 1
    if parse_only:
        possible_fn += 1

    if use_stdlib:
        possible_fn += 1

    source = None
    fn = False

    try:
        if sys.argv[1:]:
            fn = sys.argv[possible_fn]
            source = open(fn, 'r').read()
    except IndexError:
        pass

    if source is None:
        source = '\n'.join([line for line in fileinput.input()])

    program = parse_program(source)

    if use_stdlib:
        use_stdlib = parse_program(open(STDLIB_PATH, 'r').read())

    if parse_only:
        print("parsed %s successfully. resulting program:" % fn if fn else "stdin")
        for line in program:
            print(repr(line))
        exit(0)

    try:
        run(program, use_stdlib=use_stdlib)
    except LispRuntimeError as e:
        print("  \033[1;31mERROR:\033[0m  %s" % e.message)
