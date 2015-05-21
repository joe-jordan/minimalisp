; by adding print() to + and -, you can use this file to check that the arguments of a function are
; evaluated before the function itself is called, by looking at the call order (- first, then +.)
(puts (+ 1 3 5 (- 7 2)))
