; all the following are valid lines of minimalisp.

; a value
NIL

; a data structure
'(foo bar baz "mystring")

; function definition and variable binding.
(bind 'factorial (with '(n acc)
                       '((if 'acc NIL '(bind 'acc 1))
                         (if n
                             '(factorial (- n 1) (* n acc)) ; recursion.
                             'acc))))

; call a user defined function
(bind 'n 5)
(puts n "! = " (factorial n))
