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

Note that minimalisp standard library functions *can* have side effects - in particular, `bind`, `puts` and `gets` (since `gets` allows binding directly to variables like `bind`.)

### Current Status

`minimalisp.py` is a working implementation with a subset of the final standard library implemented. The implementation is in `parse.py` for the parser, `values.py` contains the types, and `vm.py` for the function implementations.

You can run the tutorial program, `tests/tutorial.l`, by using the standard library flag:

    ./minimalisp.py -l tests/tutorial.l

Without the `-l` you will get an error for using the `APPLY` symbol unbound.

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

The program `tests/tutorial.l` will run, with `./minimalisp.py tests/tutorial.l`, and provides a demonstration / test of most of the standard library functions. (note, this is currently bugged until stdlib.l can be included in programs.)

TODO:

(The original goal of a Lisp stack that is independent of the Python stack may be resurrected in a future version, or perhaps in the optimised (probably C) version.)

*this list is now frozen, and is the target for an alpha release.*

**Finish the standard library**

 * mathematical functions.

**Make runtime errors optional/configurable.**  The default should be with errors on (and nicely shown in the eventual REPL), but the purpose of turning them off is to allow a "permissive" state for random programs (genetic programs) to be run in. This obviously excludes "compile" errors (in the parser).

Example permissive rules:

* Unbound variables are `NIL`
* Trying to call a non-function is a no-op.
* Standard library function don't throw errors for wrong number of arguments.
* Binding to a non-symbol simply returns the value.

...

It should perhaps be possible to switch/force this (permissive) mode programmatically - whether this would be useful depends on whether people would use some other language to generate the random programs, in which case not, or whether they would use minimalisp as the evaluation engine as well, where it would be very useful (strict mode for hand-written programs, permissive for other programs.)

**Define random and jump concepts.** Add to the standard library draft: the idea for one or more random functions, so that random structures can be generated; some mechanism to run loops, other than recursion; and a mechanism for reading and writing text files, and for loading and dumping S-expression structures to them (access to the parser.)

For examples of random functions, `random` to return a random float between 0. and 1., and `randint` to return an integer below its first argument (default 256). This would allow use of two types of random numbers, and weighted conditional execution (useful for code generation.)

Similarly, for examples of a jump concept, we could provide a `while`, which `eval`s the same code repeatedly until a condition is met. This is subtly different to a recursive function (where the scope of the code is within an inner context), and is much neater than needing to define a recursive function and then call it. Alternatively, a `loop` or `repeat` function could be defined, which took either an exit condition or a number of iterations.

**Installable.** Add a `setup.py` which can install an executable script and libraries such that this program works from any directory. Future releases may also build into `.deb`, `.rpm` and friends, especially when we try a C implementation.
