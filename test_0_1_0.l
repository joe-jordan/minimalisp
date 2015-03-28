; bind a variable
(bind five 5)

; print things to stdout
(puts five) ; => 5\n
(puts five 6 7) ; => 567\n

; define a new scope, including input data bindings, using with
((with '(input values)
       '((puts input)
         (puts values)
         (puts five)) ; works, because five is inherited from outer scope
 ) 5 15)

; input and values are now out of scope, and cannot be accessed:
; (puts input) ; throws an error, halts execution.


; define a named function using bind and with
(bind myfunc (with '(arg1 arg2 arg3) 
                   '((bind sum (+ arg1 arg2))
                     (bind product (* sum arg3))
                     (puts product)
                     product)))

; read values from stdin
(gets a)
(gets b c)

; run our named function, and save its returned value in a new variable
(bind retval (myfunc a b c))

; define an anonymous function, which reuses the outer context, and store it in a variable
(bind anon '((puts myfunc)
             (puts retval)
             (* retval 2)))

; run the anonymous function and print the return value
(puts (eval anon))

(bind ++ (with '(i) '(+ i 1)))

; bind a symbol *to a symbol*, rather than the current value of the symbol.
(bind myreference 'five)

(puts (eval myreference)) ; 5

(bind five (++ five))

(puts (eval myreference)) ; 6

