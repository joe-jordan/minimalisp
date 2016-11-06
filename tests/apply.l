; apply lets you pass arguments to a function if you have them saved in a list.
; we import the extensions library to get the apply function.
(import "lib/ext.l")

; create some bindings in the file scope:

(bind 'eight 8)
(bind 'str "upon the moon henceforth")
(bind 'stellar 'H)


(bind 'the_arguments '('eight 'str 'stellar))

(bind 'the_function (with '(a b c) '(puts (eval a) (eval b) (eval c))))

(apply the_function the_arguments)

; and with also lets you define functions which accept variable numbers of arguments in one list:
;(bind 'foo (with 'args '(puts args)))

;(foo the_arguments)       ; prints the list of symbols.
;(foo eight pair five)     ; prints the values the symbols point to.
;(apply foo the_arguments) ; ditto.
