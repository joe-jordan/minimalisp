#! /usr/bin/env python
# If you get an import error here, please use python >= 2.6 .
from __future__ import print_function

from parse import parse_program

from vm import run

if __name__ == "__main__":
    import pycatch
    pycatch.enable(ipython=True)

    import sys
    parse_only = sys.argv[1:] and sys.argv[1] == '-p'

    possible_fn = 1
    if parse_only:
        possible_fn = 2

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

    if parse_only:
        print("parsed %s successfully. resulting program:" % fn if fn else "stdin")
        cursor = program
        while type(cursor) is not NIL:
            print(repr(cursor.left))
            cursor = cursor.right
        exit(0)

    run(program)

