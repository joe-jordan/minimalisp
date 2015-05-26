# Notes on a C implementation:

I like the idea of the following architecture:

 * A single header file containing all the data structures and functions/macros to interact with them.
 * A C generator which translates the lisp program into a C program which uses the header file library, distributed as a "compiler" (which depends on GCC.)
 * A simple lisp program which loads and runs a lisp file, compiled and distributed as a "script runner".
 * A simple lisp program which evals lines from the terminal and prints errors, distributed as a "repl mode".

The generated C program, not needing to be human readable, could be more easily stack-independent.
