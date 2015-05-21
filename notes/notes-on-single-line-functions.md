Single Line Functions
=====================

**What should `eval`?**

I am not sure that

    (eval 5)              ; 1
    (eval five)           ; 2
    (eval '(+ 6 7 8))     ; 3
    (eval '((bind 'a 4)   ; 4
            (bind 'b (+ a 7))
            (puts "a = " a " and b = " b ".")))

should all evaluate simply like this. In particular, writing a fast and simple implementation that
can accurately distinguish between examples 3 and 4 is quite difficult, especially when you consider
that

    (eval '(NIL           ; 5
            7
            (+ 2 3)
            (puts "done!")))

is a valid (albiet pointless) function. Sadly, if one implements support for example 4 naively, it
renders example 3 useless, since it will return 8 instead of 21 (having `eval`d the symbol `+`, then
6, then 7, and finally 8.) If one adds a peek at the first item in the argument list to see if it is
a symbol, then example 5 raises an error ("`NIL` is not a function").

There are several places where this is pertinent. At the time of writing, arguments two and three of
`if` are assumed to be single line, where `eval` accepts only multi-line function bodies.

One proposal occurs: allow `eval` to take more than one argument. Thus:

    ; new 3:
    (eval '(+ 6 7 8))

    ; new 4:
    (eval '(bind 'a 4)
          '(bind 'b (+ a 7)
          '(puts "a = " a " and b = " b ".")))

    ; new 5:
    (eval NIL
          7
          '(+ 2 3)
          '(puts "done!"))

We can then use `eval` to simply extend `if`, since it allows one to run multiple lines where only
one "fits".

This is slightly uglier, since one must quote each line of the function individually. But,
minimalisp was supposed to have monolithic syntactic definition(s), without special cases. I think
this proposal works nicely.
