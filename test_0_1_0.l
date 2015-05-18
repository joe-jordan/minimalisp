; bind a variable (must quote it so that bind sees the symbol, not what it currently points to.)
(bind 'five 5)

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
(bind 'myfunc (with '(arg1 arg2 arg3)
                   '((bind 'sum (+ arg1 arg2))
                     (bind 'product (* sum arg3))
                     (puts product)
                     product)))

; read values from stdin
(gets 'a)
(gets 'b 'c)

; run our named function, and save its returned value in a new variable
(bind 'retval (myfunc a b c))

; define an anonymous function, which reuses the outer context, and store it in a variable
(bind 'anon '((puts myfunc)
             (puts retval)
             (* retval 2)))

; run the anonymous function and print the return value
(puts (eval anon))

; EVAL supports lists of S-expressions, or single S expressions.
(puts (eval '(+ 303 5)))

; as does WITH
(bind '++ (with '(i) '(+ i 1)))

; bind a symbol *to a symbol*, rather than the current value of the symbol.
(bind 'myreference 'five)

; this is eval'd twice: once before being passed to eval (symbol five), and again in eval.
(puts (eval myreference)) ; 5

(bind 'five (++ five))

(puts (eval myreference)) ; 6

; using cons, car and cdr:
(bind 'pair (cons #deadb33f "unkempt"))

(puts 'pair)
(puts (car pair))
(puts (cdr pair))

; or using pair literals:
(bind 'pair '(#deadb33f . "unkempt"))

(puts 'pair)
(puts (car pair))
(puts (cdr pair))

;; False: NIL '() (which are the same),
;;        0,
;;        unbound symbols.
;; True:  everything else.
(if 15 '(bind 'eight 8) '(bind 'seven 7))

(if 'eight '(puts "eight is bound to " eight) '(puts "eight is unbound."))

(if 'seven '(puts "seven is bound to " seven) '(puts "seven is unbound"))

; apply lets you pass arguments to a function if you have them saved in a list.

(bind 'the_arguments '(eight pair five))

(bind 'the_function (with '(a b c) '(puts a b c)))

(apply the_function the_arguments)

; and with also lets you define functions which accept variable numbers of arguments in one list:
(bind 'foo (with 'args '(puts args)))

(foo the_arguments)       ; prints the list of symbols.
(foo eight pair five)     ; prints the values the symbols point to.
(apply foo the_arguments) ; ditto.
