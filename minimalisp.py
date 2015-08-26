#! /usr/bin/env python
# If you get an import error here, please use python >= 2.6 .
from __future__ import print_function

import os.path, fileinput

from parse import parse_program
from values import NIL
import vm
from vm import run, LispRuntimeError

STDLIB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "stdlib.l")

if __name__ == "__main__":
    import pycatch
    pycatch.enable(ipython=True)

    import sys
    permissive_mode = '-p' in sys.argv
    use_stdlib = '-l' in sys.argv
    with_math = '-m' in sys.argv

    possible_fn = 1
    if permissive_mode:
        vm.PERMISSIVE = True
        possible_fn += 1

    if use_stdlib:
        possible_fn += 1

    if with_math:
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
        source = '\n'.join([line for line in fileinput.input('-')])

    program = parse_program(source)

    if use_stdlib:
        use_stdlib = parse_program(open(STDLIB_PATH, 'r').read())

    try:
        run(program, use_stdlib=use_stdlib, with_math=with_math)
    except LispRuntimeError as e:
        print("  \033[1;31mERROR:\033[0m  %s" % e.message)
