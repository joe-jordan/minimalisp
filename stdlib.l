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

; logical and.
(bind 'and (with 'args '(if (car args)
                            '(if (cdr args)
                                 '(apply and (cdr args))
                                 1))
                            'NIL))
