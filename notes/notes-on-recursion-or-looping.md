# Recursion

The traditional lisp way of performing loops (particularly of looping over each item in a list) is to use recusion. Some examples of recursive functions which do this can be found in the minimalisp standard library in `stdlib.l`.

However, at present the implementation is stack-bound and in Python. As such, without tail-recusion optimisation (where the stack is re-used for each iteration which doesn't require more operations), recursion is probably unhelpful if it is the only means of looping.

Obviously the Python implementation is little more than a toy in terms of performance (I assume, benchmarks are pending), but a C implementation (especialy one which compiles lisp programs to C) would be a much stronger candidate for stack elimination in general, and tail-recursion optimisation in particular.

# Looping

In the meantime, I intend to deliver an extremely simple iterating mechanism which enables the running of code a straight number of times:

 * `DOWHILE` will be a function which works like `EVAL`, except that it will run the body until it returns something which fails an `IF`, i.e. `0`, `NIL` or `'()`. It will thus always return `NIL`, but because (like `EVAL`) it runs in the outer scope it will leak new variable bindings.
 * There will be no `BREAK` function, as this is too side-effect-ridden even for me. Containing code within `IF` functions clauses will have to be sufficient.

This method will be a simple way to deliver stack-friendly iteration, and should be simple enough to implement and keep even in future releases.

# Ugly

Kept for posterity is a lisp-based `DOWHILE` I implemented while thinking about this problem. Please don't think this is good code (it may not even work.)


    ; This is an awful definition, and may illustrate the need for an outer-implementation (in python,
    ; or C.) In particular, notice what happens if code carefully initialises all its own variables,
    ; rather than inheriting them from the outer scope: they will be the same on each iteration, and the
    ; loop will never exit. Similarly, no variables from the loop will leave the outer scope apart from
    ; the return value. Finally, if the poor consumer tries to use the symbol TEST, CODE, or OUT they
    ; will encounter unexpected bugs.
    (bind 'dowhile (with '(test code)
                         '(bind 'out (eval code))
                         '(if (eval test)
                              out
                              '(dowhile test code))))
