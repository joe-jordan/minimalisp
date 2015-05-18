;; TODO implement these two as tail-recursive functions.

; position of a value in an S-expression
(bind 'pos (with '(l) '(()
                        ()
                        ())))

; length of an S expression.
(bind 'len (with '(l) '(()
                        ()
                        ())))

; logical reversal.
(bind 'not (with '(t) '((if t
                            '()
                            1))))
