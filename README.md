minimalisp
==========

Minimalist Lisp Implementation (initially in Python, will be ported to C).

The goal of minimalisp is to create a very very lightweight Lisp implementation with (opinion)*proper*(/opinion) code deferral syntax. It is minimal in that it should have almost no standard library beyond that necessary to use function definition and value types.

The reason for choosing to implement such a small subset of lisp functionality is to allow a very very efficient parser and runtime, and to make code generation simple &mdash; the ideal use case for this language would be [Genetic Programming](http://en.wikipedia.org/wiki/Genetic_programming).

The only other important detail, is that the implementation will use nonstandard notation for deferred code specification, by taking full advantage of Lisp's [Homoiconicity](http://en.wikipedia.org/wiki/Homoiconicity). To explain, let me give an example: in most Lisp implementations, literal S expressions are escaped with quotes:

    ; "normal" lisp implementation:
    (bar must be a defined function)
    '(foo need not be a defined function)

i.e. you defer evaluation of only quoted S-expressions, **except** where you're using a "magic" function like `if`:

    ; "normal" lisp implementation:
    (if (test with data)
        (run this if true)
        (run this if false))

Part of the point of the simpler syntax of minimalisp is that *there are no magic functions* &mdash; it uses the more formal:

    ; minimalisp:
    (if (test with data)
        '(run this if true)
        '(run this if false))

Since we only want to actually evaluate one of the two clauses, we must pass them in deferred/quoted, and `eval` them.

The author hypothesises that this should make the runtime faster, since we will not need to climb up the expression tree looking for magic functions before internal calls to `eval` - the information about whether execution is deferred or not is stored directly on the code data from the start.

The idea is to provide all functions that *cannot* be implemented in the language itself easily as standard library, particularly `bind` and `with` (for binding values to symbols and creating contexts, which function as a stack) and `puts`, `gets`, `cons`, `car`, `cdr`, plus the arithmetic and comparisons `+`, `-` and so on, and `if`. There may later be a math library which allows use of `sin` and `ln` and the like, for convenience.

### Current Status

`minimalisp.py` is a working implementation with a subset of the final standard library implemented. The implementation is in `parse.py` for the parser, `values.py` contains the types, and `vm.py` for the function implementations.

The code is currently implemented in Python, the program can parse input and run code, but the standard library is incomplete. It can parse:

* integers and floats -> stored as python primitives, so bignum support for free!
* all base-10 number formats accepted (i.e. `1` == `+1`, `-1` == `(- 0 1)`, `-13.762e+037` == exactly what it says on the tin.)
* hex numbers starting with `#` (converted to integers, hexness not remembered.)
* comments are correctly escaped
* strings, including most special characters, including `;`, escaped correctly (printing this only works assuming python returns us a sensible repr)
* S-expressions parsed into linked lists correctly
* quoted S-expressions store this status correctly
* literal (dotted) pairs are parsed and stored correctly
* nil or NIL correctly interpreted as a NIL object.
* symbols are correctly detected in tricky cases, e.g. `+five` is a symbol, where `+5` is an integer.
* symbols can be quoted `'five` is "the quoted symbol `FIVE`", which is not a symbol with a quote at the start, `'FIVE`, which is disallowed.
* however, symbols MAY contain some special characters - `'` is allowed anywhere but the start, and `.` is not excluded. In order to define a pair literal, one must put spaces before and after a `.`.

The program test_0_1_0.l will run, with `./minimalisp.py test_0_1_0.l`, and provides a demonstration / test of most of the standard library functions.

TODO:

Finish the standard library (especially `if`) and mathematical function implementations. The original goal of a Lisp stack that is independent of the Python stack may be resurrected in a future version, or perhaps in the optimised (probably C) version.
