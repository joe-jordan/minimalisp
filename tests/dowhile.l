(bind '++ (with '(i) '(+ i 1)))

(bind 'i 0)

(puts "before dowhile, i = " i)

(dowhile '(bind 'i (++ i))
         '(< i 5))

(puts "after dowhile, i = " i)
