(bind 'five 5)
(bind 'list '(one two three))

(bind 'myfunc (with '(arg)
                    '(puts arg)))

(myfunc "hello world!")
