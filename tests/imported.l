; define some file-scoped variables:
(bind 'public_binding 7)

; and import the extended standard library, where NOT is defined for us.
(import "lib/ext.l")

;; expose two functions:

(bind 'implementation_detail (with '(s)
                                   '(join "I print: " s)))

(bind 'exported (with '(s)
                      '(bind 's2 (implementation_detail s))
                      '(if (not (= public_binding 7))
                           '(puts "can't see public_binding")
                           NIL)
                      '(puts s2)))

