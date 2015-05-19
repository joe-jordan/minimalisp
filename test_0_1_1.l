;; different tests of the eval function.

; literal
(puts "(literal) should print 5: " (eval 5))

(bind 'five 5)

; bound symbol, eval'd once and twice:
(puts "(bound symbol) should print 5: " (eval five))
(puts "(quoted bound symbol) should print 5: " (eval 'five))

(bind 'two 2)
(bind 'three 3)

; single line anonymous function:
(puts "(single line fn) should print 5: " (eval '((+ two three))))

; multi-line anonymous function:
(puts "(multi-line fn) should print 5:" (eval '((bind 'other_five
                                                      (+ two three))
                                                other_five)))

; should have leaked value into outer context:
(puts "(binds vars in outer scope) should print 5:" other_five)
