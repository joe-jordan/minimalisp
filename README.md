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

The idea is to provide all functions that *cannot* be implemented in the language itself easily as standard library, particularly `bind` and `with` (for binding values to symbols and creating contexts, which function as a stack) and `puts`, `gets`, `cons`, `car`, `cdr`, plus the arithmetic and comparisons `+`, `-` and so on, and `if`. There is also math library which allows use of `sin` and `log` and the like, for convenience.

Note that minimalisp standard library functions *can* have side effects - in particular, `bind`, `puts` and `gets` (since `gets` allows binding directly to variables like `bind`.)

### Current Status

`minimalisp.py` is a working implementation with a standard library implemented. It is installable with `setup.py`. The implementation is in `parse.py` for the parser, `values.py` contains the types, and `vm.py` for the function implementations.

`minimalisp.py` accepts three arguments: `-p` for "parse-only" mode, `-l` for the extended standard library (the parts that can be implemented in the language itself,) and `-m` for the mathematical functions.

The program `tests/tutorial.l` will run, with `scripts/minimalisp -l tests/tutorial.l`, and provides a demonstration / test of most of the standard library functions.

## Documentation:

I have started using the [github wiki](https://github.com/joe-jordan/minimalisp/wiki) for the function reference.

