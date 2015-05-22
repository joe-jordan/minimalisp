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

`minimalisp.py` is a working implementation with a standard library implemented. The implementation is in `parse.py` for the parser, `values.py` contains the types, and `vm.py` for the function implementations.

`minimalisp.py` accepts three arguments: `-p` for "parse-only" mode, `-l` for the extended standard library (the parts that can be implemented in the language itself,) and `-m` for the mathematical functions.

The program `tests/tutorial.l` will run, with `./minimalisp.py -l tests/tutorial.l`, and provides a demonstration / test of most of the standard library functions.

## Function Reference:

Built-in:

  * `WITH` returns a function object which can be called.
  * `BIND` binds a symbol (name) to a value in the current scope.
  * `EVAL` executes the expression on the right.
  * `CONS`, `CAR` and `CDR` behave as expected for a lisp; for Pair construction and value extraction.
  * `PUTS` and `GETS` allow reading and writing values from stdin and stdout.
  * `+`, `-`, `*`, `/` all do what they say on the tin. Additionally, `i/` and `%` are provided for integer division and remainder (modulo) respectively.
  * `ROUND` coerces floating point values to integers.
  * `RAND` returns a pseudo-random number between 0.0 and 1.0.
  * `IF` will test its first argument, and if it is not `NIL`, an unbound symbol or 0 it will `EVAL` its second argument, otherwise its third (if provided.)
  * `=` tests for equivalence and `==` for exact (object) equality. They return 1 or `NIL`.
  * `>` and `<` test for greater than or less than, and can compare numbers or strings (if compared, numbers are always lower than strings, regardless of the contents.)

`stdlib.l` (`-l`)

(ever expanding.)

  * `APPLY` invokes its first argument (a function) with its second as a list of arguments.
  * `POS` finds an object (`=`) in a list and returns its index.
  * `LEN` returns the length of a list.
  * `NOT` inverts logical expressions.
  * `AND` tests each argument like `IF`, and returns 1 if all are 1, otherwise `NIL`.
  * `OR` ditto, but 1 if any are 1, otherwise `NIL`.
  * `RANDINT` generates a random integer between 0 and its argument, default 256.

(there is also a broken `DOWHILE` there, pending work on a looping syntax of some kind.)

`math.py` (`-m`)

  * `SIN`, `COS`, `TAN` trigonomic functions (arguments in radians.)
  * `ASIN`, `ACOS`, `ATAN`, `ATAN2` inverse trigonomic functions (returning radians.)
  * `LOG` logarithm, second argument is the base, default 10.
  * `PI` the value of *pi* as a double precision float.
  * `EXP` raise *e* to the power of the first argument.


## TODO:

(The original goal of a Lisp stack that is independent of the Python stack may be resurrected in a future version, or perhaps in the optimised (probably C) version.)

*this list is now frozen, and is the target for an alpha release.*

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
