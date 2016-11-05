(bind 'i 5)
; LEN uses a local variable called i: the `i` in this scope should be invisible
; to it.
(import "lib/ext.l")
(puts (len '()))
