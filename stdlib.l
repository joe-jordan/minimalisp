;; TODO implement these two as tail-recursive functions.

; position of a value in an S-expression
(bind 'pos (with '(v l i) '((if 'i NIL '(bind 'i 0)) ; if i was not passed, start it at index 0.
                            (if (= v (car l))
                                i
                                '(pos v (cdr l) (+ i 1))))))

; length of an S expression.
(bind 'len (with '(l i) '((if 'i NIL '(bind 'i 0)) ; if i is missing, start it at length 0.
                          (if l
                              '(len (cdr l) (+ i 1))
                              i))))

; logical reversal.
(bind 'not (with '(t) '(if t
                           NIL
                           1)))

; logical and.
(bind 'and (with 'args '(if (car args)
                            '(if (cdr args)
                                 '(apply and (cdr args))
                                 1))
                            NIL))

; logical or.
(bind 'or (with 'args '(if (car args)
                           1
                           '(if (cdr args)
                                '(apply or (cdr args))
                                NIL))))
